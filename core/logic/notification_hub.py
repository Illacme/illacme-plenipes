#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - API Egress Adapter (生态破壁层)
模块职责：全域 Webhook 异步广播引擎。
负责在文章成功通过 AI 翻译与 SSG 编译管线后，向外部生态（飞书、钉钉、TG、CMS）发射通知。
架构原则：绝对非阻塞。网络 I/O 必须在游离线程中执行，严禁拖慢主引擎的毫秒级写盘速度。
🚀 [V14.3 架构升级]：剥离游离态 Thread 构建池化调度器，平滑削峰填谷。
"""

import os
import sys
import logging
from core.utils.tracing import tlog
import requests
from concurrent.futures import ThreadPoolExecutor
from core.adapters.egress.webhook.base import BaseWebhookDriver, WebhookRegistry
from core.utils.plugin_loader import discover_and_register

from core.utils.tracing import Tracer

# 🚀 [Zero-Touch] 初始化驱动矩阵
def _init_drivers():
    global_path = os.path.abspath("adapters/notifications/webhook")
    if os.path.exists(global_path):
        if os.path.abspath("adapters") not in sys.path:
            sys.path.append(os.path.abspath("adapters"))
        discover_and_register([global_path], "adapters.notifications.webhook", BaseWebhookDriver, WebhookRegistry.register)

_init_drivers()

class WebhookBroadcaster:
    """
    🚀 漏斗式安全异步广播矩阵 (插件化版本)
    """
    def __init__(self, publish_cfg, sys_tuning_cfg=None):
        self.enabled = publish_cfg.webhook_enabled
        self.endpoints = publish_cfg.webhook_urls
        self.timeout = publish_cfg.webhook_timeout

        max_workers = sys_tuning_cfg.max_workers if sys_tuning_cfg else 5
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.drivers = WebhookRegistry.get_drivers()

    def _fire(self, url, payload):
        try:
            headers = {'Content-Type': 'application/json'}
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            resp.raise_for_status()
            tlog.debug(f"📡 [生态破壁] Webhook 投递成功 -> {url[:30]}...")
        except Exception as e:
            tlog.debug(f"⚠️ [生态破壁] 投递失败: {url[:30]}... | 原因: {e}")

    def broadcast(self, title, rel_path, lang_code, mapped_sub_dir, slug, ael_iter_id=None):
        if not self.enabled or not self.endpoints:
            return

        url_path = f"/{lang_code}/{mapped_sub_dir}/{slug}".replace('//', '/')
        ael_tag = ael_iter_id or "AEL-LIVE-SYNC"

        for url in self.endpoints:
            # 🚀 寻找匹配的驱动
            payload = None
            # 按注册顺序匹配，最后一个通常是 Generic
            for driver in self.drivers:
                if driver.match(url):
                    payload = driver.build_payload(title, url_path, lang_code, ael_tag)
                    break

            if payload:
                # 🚀 利用装饰器确保 Trace-ID 穿透至异步线程
                self.executor.submit(Tracer.trace_context(ael_tag)(self._fire), url, payload)


import threading

def build_universal_text_payload(url: str, text: str) -> dict:
    """自适应判定 Webhook 平台并生成相应的文本消息 payload"""
    if 'feishu.cn' in url:
        return {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "📢 Plenipes 出版系统通知",
                        "content": [[{"tag": "text", "text": text}]]
                    }
                }
            }
        }
    elif 'dingtalk.com' in url or 'qyapi.weixin.qq.com' in url:
        return {
            "msg_type": "text",
            "text": {
                "content": text
            }
        }
    else:
        # Slack, Telegram 或其他通用 Webhook
        return {
            "text": text
        }


def send_sync_lifecycle_notification(engine, status: str, message: str, detail: str = ""):
    """
    🚀 广播全量同步生命周期通知
    将消息通过桌面系统通知弹窗与活跃 Webhook 渠道异步投递出去。
    """
    from core.runtime.engine_singleton import send_notification
    
    # 1. 组装桌面通知
    title_map = {
        "START": "🚀 Plenipes 发布启动",
        "SUCCESS": "✅ Plenipes 发布成功",
        "FAIL": "❌ Plenipes 发布失败",
        "BLOCKED": "🔒 Plenipes 发布被拦截"
    }
    title = title_map.get(status, "📢 Plenipes 通知")
    msg_body = f"{message}。{detail}" if detail else message
    
    # 启动异步线程发送桌面通知，绝不阻塞主构建过程
    threading.Thread(target=send_notification, args=(title, msg_body), daemon=True).start()
    
    # 2. 依据配置的三层治理矩阵安全提取 Webhook urls
    urls = []
    pub_ctrl = getattr(engine.config, "publish_control", None) if engine else None
    if pub_ctrl and getattr(pub_ctrl, "webhook_enabled", False):
        # 兼容传统直链配置
        if hasattr(pub_ctrl, "webhook_urls") and pub_ctrl.webhook_urls:
            urls.extend(pub_ctrl.webhook_urls)
            
        # 提取活跃的端点列表
        active_ids = getattr(pub_ctrl, "active_webhook_ids", [])
        endpoints = getattr(pub_ctrl, "webhook_endpoints", {})
        for wid in active_ids:
            if wid in endpoints:
                ep = endpoints[wid]
                url = getattr(ep, "url", None) or (ep.get("url") if isinstance(ep, dict) else None)
                if url:
                    urls.append(url)
                    
    # 3. 异步发射 Webhook
    if urls:
        full_text = f"【Plenipes 自动出版系统】\n通知类型: {title}\n摘要: {message}\n详情: {detail}"
        def _fire():
            for url in urls:
                try:
                    payload = build_universal_text_payload(url, full_text)
                    requests.post(url, json=payload, timeout=10.0)
                except Exception as e:
                    tlog.debug(f"⚠️ [通知中心] 投递失败 {url[:30]}... | 原因: {e}")
                    
        threading.Thread(target=_fire, daemon=True).start()

