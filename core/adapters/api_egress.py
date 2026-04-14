#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - API Egress Adapter (生态破壁层)
模块职责：全域 Webhook 异步广播引擎。
负责在文章成功通过 AI 翻译与 SSG 编译管线后，向外部生态（飞书、钉钉、TG、CMS）发射通知。
架构原则：绝对非阻塞。网络 I/O 必须在游离线程中执行，严禁拖慢主引擎的毫秒级写盘速度。
🚀 [V14.3 架构升级]：剥离游离态 Thread 构建池化调度器，平滑削峰填谷。
"""

import json
import logging
import requests
import threading
from concurrent.futures import ThreadPoolExecutor # 🚀 新增：导入工业级线程池调度器

logger = logging.getLogger("Illacme.plenipes")

class WebhookBroadcaster:
    """
    🚀 漏斗式安全异步广播矩阵
    """
    def __init__(self, publish_cfg, sys_tuning_cfg=None):
        self.enabled = publish_cfg.get('webhook_enabled', False)
        self.endpoints = publish_cfg.get('webhook_urls', [])
        self.timeout = publish_cfg.get('webhook_timeout', 3.0) 
        
        # 🚀 抽取硬编码：动态接管线程池并发上限
        sys_tuning = sys_tuning_cfg or {}
        max_workers = sys_tuning.get('max_concurrent_workers', 5)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def _fire(self, url, payload):
        try:
            headers = {'Content-Type': 'application/json'}
            # 物理级隔离网络请求
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            logger.debug(f"📡 [生态破壁] Webhook 投递成功 -> {url[:30]}...")
        except Exception as e:
            logger.debug(f"⚠️ [生态破壁] 投递失败 (不影响主站运行): {url[:30]}... | 拦截原因: {e}")

    def broadcast(self, title, rel_path, lang_code, mapped_sub_dir, slug):
        """组装标准 JSON 卡片并异步发射 (多态路由版)"""
        if not self.enabled or not self.endpoints:
            return

        url_path = f"/{lang_code}/{mapped_sub_dir}/{slug}".replace('//', '/')
        
        # 定义一个内部工厂，根据 URL 域名生成不同平台的专属卡片格式
        def build_payload(target_url):
            if 'feishu.cn' in target_url:
                # 🚀 飞书富文本卡片格式
                return {
                    "msg_type": "post",
                    "content": {
                        "post": {
                            "zh_cn": {
                                "title": "✨ Illacme 引擎：新文章编译就绪",
                                "content": [
                                    [{"tag": "text", "text": f"📚 标题: {title}"}],
                                    [{"tag": "text", "text": f"🌐 语种: {lang_code.upper()}"}],
                                    [{"tag": "text", "text": f"🔗 预测路由: {url_path}"}]
                                ]
                            }
                        }
                    }
                }
            elif 'dingtalk.com' in target_url:
                # 🚀 钉钉 Markdown 卡片格式
                return {
                    "msgtype": "markdown",
                    "markdown": {
                        "title": f"Illacme 同步就绪: {title}",
                        "text": f"### ✨ Illacme 引擎编译就绪\n- **标题**: {title}\n- **语种**: {lang_code.upper()}\n- **路由**: {url_path}\n> ⚡️ 状态: SSG 增量更新已触发。"
                    }
                }
            elif 'qyapi.weixin.qq.com' in target_url:
                # 🟢 企业微信 (WeCom) Markdown 机器人
                return {
                    "msgtype": "markdown",
                    "markdown": {
                        "content": f"### ✨ Illacme 引擎编译就绪\n> **标题**: {title}\n> **语种**: {lang_code.upper()}\n> **路由**: {url_path}\n> ⚡️ 状态: SSG 增量更新已触发。"
                    }
                }
            elif 'api.telegram.org' in target_url:
                # ✈️ Telegram Bot API
                return {
                    "text": f"✨ <b>Illacme 同步就绪</b>\n\n📚 <b>标题</b>: {title}\n🌐 <b>语种</b>: {lang_code.upper()}\n🔗 <b>路由</b>: {url_path}",
                    "parse_mode": "HTML"  # 使用 HTML 模式最稳定，避免 Markdown 转义导致发送失败
                }
            else:
                # 🌐 通用系统格式兜底
                return {
                    "event": "document_published",
                    "data": {
                        "title": title, "lang": lang_code, "relative_path": rel_path, "url_path": url_path
                    }
                }

        # 🚀 [调度层重构] 遍历目标，推入线程池排队执行，取代原有的无限裸线程起爆
        for url in self.endpoints:
            payload = build_payload(url)
            self.executor.submit(self._fire, url, payload)