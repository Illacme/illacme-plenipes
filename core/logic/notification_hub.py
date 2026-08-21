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
from typing import Any, List, Dict, Optional
from core.utils.tracing import tlog
import requests
from concurrent.futures import ThreadPoolExecutor
from core.adapters.egress.webhook.base import BaseWebhookDriver, WebhookRegistry
from core.utils.plugin_loader import discover_and_register

from core.utils.tracing import Tracer

# 🚀 [Zero-Touch] 初始化全协议驱动矩阵
def _init_drivers():
    base_notif_dir = os.path.abspath("adapters/notifications")
    if os.path.exists(base_notif_dir):
        if os.path.abspath("adapters") not in sys.path:
            sys.path.append(os.path.abspath("adapters"))
        sub_dirs = ["webhook", "email", "sms", "app_push"]
        for sub in sub_dirs:
            p = os.path.join(base_notif_dir, sub)
            if os.path.exists(p):
                rel_pkg = f"adapters.notifications.{sub}"
                discover_and_register([p], rel_pkg, BaseWebhookDriver, WebhookRegistry.register)

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


# ==============================================================================
# 🚀 [V107.0] 全域生命周期与业务通知事件标准矩阵
# ==============================================================================

EVENT_ALIASES = {
    # 📚 文章出版与构建
    "SYNC_SUCCESS": ["SYNC_SUCCESS", "SUCCESS", "PUBLISH_SUCCESS", "DOCS_SYNC_SUCCESS"],
    "SYNC_FAIL": ["SYNC_FAIL", "FAIL", "PUBLISH_FAIL", "SYNC_ERROR", "ERROR"],
    "SYNC_START": ["SYNC_START", "START", "PUBLISH_START"],
    # 🌐 跨平台社交分发
    "SYNDICATION_COMPLETED": ["SYNDICATION_COMPLETED", "SYNDICATION_SUCCESS", "EGRESS_SUCCESS", "ALL_CHANNELS_SYNCED"],
    "SYNDICATION_FAILED": ["SYNDICATION_FAILED", "SYNDICATION_FAIL", "EGRESS_FAIL", "CHANNEL_ERROR"],
    # 🛡️ 安全合规与算力告警
    "AI_MELT": ["AI_MELT", "AI_RATE_LIMIT_MELT", "AI_FAIL", "RATE_LIMIT_BREAKER"],
    "COMPLIANCE_BLOCKED": ["COMPLIANCE_BLOCKED", "BLOCKED", "SECURITY_BLOCKED", "AUDIT_FAIL"],
    # 🚀 云端托管与上线
    "DEPLOY_SUCCESS": ["DEPLOY_SUCCESS", "HOSTING_DEPLOY_SUCCESS", "DEPLOY_DONE"],
    "DEPLOY_FAILED": ["DEPLOY_FAILED", "HOSTING_DEPLOY_FAIL", "DEPLOY_ERROR"]
}

# 默认推荐预设
RECOMMENDED_EVENTS = ["SYNC_SUCCESS", "SYNC_FAIL", "SYNDICATION_COMPLETED", "SYNDICATION_FAILED", "AI_MELT", "COMPLIANCE_BLOCKED", "DEPLOY_SUCCESS"]
ALERTS_ONLY_EVENTS = ["SYNC_FAIL", "SYNDICATION_FAILED", "AI_MELT", "COMPLIANCE_BLOCKED", "DEPLOY_FAILED"]
ALL_EVENTS = list(EVENT_ALIASES.keys())

def normalize_event(event_type: str) -> str:
    """将任意变体/别名事件统一映射为标准事件键名"""
    ev_upper = (event_type or "").strip().upper()
    for standard_key, aliases in EVENT_ALIASES.items():
        if ev_upper == standard_key or ev_upper in aliases:
            return standard_key
    return ev_upper

def should_deliver_event(channel_cfg: Any, event_type: str, default_events=None) -> bool:
    """
    🚀 [V107.0] 智能判定当前渠道是否订阅了该事件 (支持别名自动归一化与集合匹配)
    """
    target_event = normalize_event(event_type)
    if default_events is None:
        default_events = RECOMMENDED_EVENTS

    if not channel_cfg:
        norm_defaults = [normalize_event(x) for x in default_events]
        return target_event in norm_defaults

    if hasattr(channel_cfg, "dict"):
        channel_cfg = channel_cfg.dict()

    if isinstance(channel_cfg, dict):
        subscribed = channel_cfg.get("events")
        if subscribed:
            if isinstance(subscribed, list):
                norm_sub = [normalize_event(str(x)) for x in subscribed]
                return target_event in norm_sub
            if isinstance(subscribed, str):
                norm_sub = [normalize_event(x.strip()) for x in subscribed.split(',') if x.strip()]
                return target_event in norm_sub

    norm_defaults = [normalize_event(x) for x in default_events]
    return target_event in norm_defaults


def broadcast_system_event(engine, event_type: str, title: str, message: str, detail: str = "", extra_data: Optional[Dict[str, Any]] = None):
    """
    🚀 [V107.0] 全域统一消息通知广播总线
    向桌面通知、活跃 Webhook 机器人、SMTP 邮件、云短信、Bark/移动推送进行全渠道智能分流与自适应排版。
    """
    from core.runtime.engine_singleton import send_notification

    standard_event = normalize_event(event_type)
    
    # 1. 桌面原生轻量通知
    msg_body = f"{message}。{detail}" if detail else message
    threading.Thread(target=send_notification, args=(title, msg_body), daemon=True).start()

    # 2. 依据配置的安全矩阵提取端点
    pub_ctrl = getattr(engine.config, "publish_control", None) if engine else None
    if not pub_ctrl or not getattr(pub_ctrl, "webhook_enabled", False):
        return

    endpoints = getattr(pub_ctrl, "webhook_endpoints", {})
    if hasattr(endpoints, "dict"):
        endpoints = endpoints.dict()
    if not isinstance(endpoints, dict):
        endpoints = {}
    active_ids = getattr(pub_ctrl, "active_webhook_ids", [])
    full_text = f"【Plenipes 出版中枢】\n事件: {title}\n摘要: {message}\n详情: {detail or '无'}"

    def _dispatch_all():
        # 3a. 传统与自定义 Webhook 机器人 (飞书/钉钉/企微/TG/Discord)
        urls = []
        if hasattr(pub_ctrl, "webhook_urls") and pub_ctrl.webhook_urls:
            urls.extend(pub_ctrl.webhook_urls)

        for wid in active_ids:
            if wid in endpoints:
                ep = endpoints[wid]
                if should_deliver_event(ep, standard_event, default_events=RECOMMENDED_EVENTS):
                    u = getattr(ep, "url", None) or (ep.get("url") if isinstance(ep, dict) else None)
                    if u and u not in urls:
                        urls.append(u)

        for u in urls:
            try:
                payload = build_universal_text_payload(u, full_text)
                requests.post(u, json=payload, timeout=10.0)
                tlog.debug(f"📡 [通知中心] Webhook 投递成功 -> {u[:30]}...")
            except Exception as e:
                tlog.debug(f"⚠️ [通知中心] Webhook 投递失败 {u[:30]}... | 原因: {e}")

        # 3b. 📧 Email 邮件通知 (HTML 富文本自适应排版)
        email_cfg = endpoints.get("email")
        is_email_active = bool(email_cfg.get("enabled") if isinstance(email_cfg, dict) else getattr(email_cfg, "enabled", False))
        if email_cfg and (is_email_active or "email" in active_ids):
            if should_deliver_event(email_cfg, standard_event, default_events=RECOMMENDED_EVENTS):
                try:
                    from adapters.notifications.email.smtp import SmtpEmailDriver
                    cfg = email_cfg if isinstance(email_cfg, dict) else email_cfg.dict()
                    email_driver = SmtpEmailDriver(config=cfg)
                    email_driver.send_email(
                        f"📢 [{standard_event}] {title}: {message}",
                        f"""<div style="font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif; max-width:620px; margin:0 auto; padding:24px; background:#0b0f17; color:#e2e8f0; border-radius:12px; border:1px solid #1e293b;">
                            <div style="display:flex; align-items:center; margin-bottom:16px;">
                                <span style="background:rgba(0,242,254,0.15); color:#00f2fe; padding:4px 10px; border-radius:6px; font-size:0.8rem; font-weight:bold; border:1px solid rgba(0,242,254,0.3);">{standard_event}</span>
                            </div>
                            <h2 style="color:#ffffff; margin:0 0 12px 0; font-size:1.3rem;">{title}</h2>
                            <p style="font-size:1.05rem; line-height:1.5; color:#cbd5e1; margin:0 0 16px 0;">{message}</p>
                            <div style="background:rgba(255,255,255,0.04); padding:14px; border-radius:8px; border:1px solid rgba(255,255,255,0.06); font-size:0.88rem; color:#94a3b8;">
                                <b>详情描述</b>: {detail or '无'}
                            </div>
                            <hr style="border:none; border-top:1px solid #1e293b; margin:20px 0 12px 0;">
                            <p style="font-size:0.75rem; color:#64748b; margin:0;">来自 Illacme Plenipes 极速数字出版自动化中枢</p>
                        </div>"""
                    )
                    tlog.debug("📧 [通知中心] 邮件通知投递成功。")
                except Exception as e:
                    tlog.debug(f"⚠️ [通知中心] 邮件投递失败: {e}")

        # 3c. 📱 SMS 短信告警 (默认仅紧急告警 ALERTS_ONLY_EVENTS)
        sms_cfg = endpoints.get("sms")
        is_sms_active = bool(sms_cfg.get("enabled") if isinstance(sms_cfg, dict) else getattr(sms_cfg, "enabled", False))
        if sms_cfg and (is_sms_active or "sms" in active_ids):
            if should_deliver_event(sms_cfg, standard_event, default_events=ALERTS_ONLY_EVENTS):
                try:
                    from adapters.notifications.sms.generic_sms import GenericSmsDriver
                    cfg = sms_cfg if isinstance(sms_cfg, dict) else sms_cfg.dict()
                    sms_driver = GenericSmsDriver(config=cfg)
                    sms_driver.send_sms({"event": standard_event, "status": standard_event, "message": message, "detail": detail})
                    tlog.debug("📱 [通知中心] 短信告警投递成功。")
                except Exception as e:
                    tlog.debug(f"⚠️ [通知中心] 短信投递失败: {e}")

        # 3d. 📲 App Push 移动与桌面推送 (Bark / Gotify / Server酱)
        push_cfg = endpoints.get("app_push")
        is_push_active = bool(push_cfg.get("enabled") if isinstance(push_cfg, dict) else getattr(push_cfg, "enabled", False))
        if push_cfg and (is_push_active or "app_push" in active_ids):
            if should_deliver_event(push_cfg, standard_event, default_events=RECOMMENDED_EVENTS):
                try:
                    from adapters.notifications.app_push.push_hub import AppPushDriver
                    cfg = push_cfg if isinstance(push_cfg, dict) else push_cfg.dict()
                    push_driver = AppPushDriver(config=cfg)
                    push_driver.push(title, f"{message}\n{detail}")
                    tlog.debug("📲 [通知中心] 移动推送投递成功。")
                except Exception as e:
                    tlog.debug(f"⚠️ [通知中心] 移动推送投递失败: {e}")

    threading.Thread(target=_dispatch_all, daemon=True).start()


def send_sync_lifecycle_notification(engine, status: str, message: str, detail: str = ""):
    """
    🚀 向前兼容的生命周期通知转发器
    """
    title_map = {
        "START": "🚀 Plenipes 发布启动",
        "SUCCESS": "✅ Plenipes 发布成功",
        "FAIL": "❌ Plenipes 发布失败",
        "BLOCKED": "🔒 Plenipes 发布被拦截",
        "WARN": "⚠️ Plenipes 发布警告"
    }
    title = title_map.get(status.upper(), f"📢 Plenipes 通知 ({status})")
    broadcast_system_event(engine, status, title, message, detail)




