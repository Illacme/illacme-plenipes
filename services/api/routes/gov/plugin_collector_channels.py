#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Plugin Matrix Channels Collector Shard
模块职责：收集全站托管 (Hosting)、通知告警 (Notifications)、分发渠道 (Syndication) 与图床存储 (Image Hosting) 插件。
🛡️ [SOP-01 & SOP-02]：从 plugin_mapper.py 物理拆解出的渠道层装配器。
"""

from typing import List, Dict, Any


def collect_hosting_plugins(engine, disabled: set, system_track: str) -> List[Dict[str, Any]]:
    """收集全站托管能力 (Hosting)"""
    from core.adapters.egress.publishers.base import PublisherRegistry

    hosting_root = engine.config.publish_control.direct_upload
    non_hosting_publishers = {"webhook_dispatch", "aliyun_oss", "tencent_cos", "s3", "upyun_uss"}
    pub_ctrl = getattr(engine.config, "publish_control", None)
    primary_hosting_id = (
        getattr(pub_ctrl, "primary_hosting_id", "") or
        (hosting_root.get("primary_hosting_id", "") if isinstance(hosting_root, dict) else "")
    )
    plugins = []
    for p_id, cls in PublisherRegistry.get_all_publishers().items():
        if p_id in non_hosting_publishers:
            continue  # 🚀 [V18.0] 物理剥离：非纯网页托管归位至专属大类
        current_cfg = {}
        if isinstance(hosting_root, dict):
            current_cfg = hosting_root.get(p_id, {})
        elif hasattr(hosting_root, "get"):
            current_cfg = hosting_root.get(p_id, {})
            
        is_active = (
            current_cfg.get("enabled", False) if isinstance(current_cfg, dict) else (
                getattr(current_cfg, "enabled", False) if hasattr(current_cfg, "enabled") else False
            )
        )
        name = getattr(cls, "DISPLAY_NAME", p_id.upper())
        plugins.append({
            "id": p_id, "name": name, "category": "hosting", "category_name": "🌐 全站托管",
            "status": "In-Use" if is_active else "Ready", "is_in_use": is_active, "is_enabled": (p_id not in disabled),
            "is_primary": bool(is_active and p_id == primary_hosting_id),
            "origin": "core", "version": getattr(cls, "VERSION", system_track),
            "description": getattr(cls, "DESCRIPTION", f"托管适配器插件：负责将出版物物理同步至 {name}。"),
            "cfg": hosting_root.get(p_id, {}) if isinstance(hosting_root, dict) else {}, "is_manageable": True
        })
    return plugins


def collect_notification_plugins(engine, disabled: set) -> List[Dict[str, Any]]:
    """收集消息通知矩阵 (Notifications & Event Dispatchers)"""
    notification_plugins_meta = [
        {"id": "feishu", "name": "飞书 Notice 适配器", "desc": "自动构造飞书 Post 富文本卡片，支持编译就绪与分发失败状态推送。"},
        {"id": "dingtalk", "name": "钉钉 Notice 适配器", "desc": "自动构造钉钉 Markdown 消息卡片，实时同步系统出版生命周期。"},
        {"id": "wecom", "name": "企业微信 Notice 适配器", "desc": "对接企业微信群机器人，提供高颜值出版告警与状态提醒。"},
        {"id": "telegram", "name": "Telegram 运维事件通知", "desc": "面向站长/运维：利用 Telegram Bot API 实时接收全站编译就绪与系统故障告警推送。"},
        {"id": "discord", "name": "Discord 运维事件通知", "desc": "面向站长/运维：通过 Discord Webhook 接收全站编译日志、算力熔断与系统状态告警推送。"},
        {"id": "generic_webhook", "name": "通用 HTTP Webhook 适配器", "desc": "向任意自定义 HTTP API 发送 JSON 事件报文，兼容标准 Webhook。"},
        {"id": "webhook_dispatch", "name": "Webhook Dispatcher 信号触发器", "desc": "同步完成后向目标端点推送带 HMAC 签名的分发信号，触发下游 CI/CD 或自动化工具。"},
        {"id": "email", "name": "SMTP 邮件通知适配器", "desc": "支持标准 SMTP / SSL / STARTTLS 发送高质感 HTML 出版通知与故障运维告警。"},
        {"id": "sms", "name": "短信告警通知适配器", "desc": "对接阿里云/腾讯云/Twilio/通用短信网关，在全站出版故障或算力熔断时下发短信通知。"},
        {"id": "app_push", "name": "移动与桌面推送中枢", "desc": "支持 Bark (iOS)、Gotify (私有化)、Server酱 (微信通知) 与 Pushover 极速推送。"}
    ]
    pub_ctrl = getattr(engine.config, "publish_control", None)
    endpoints = getattr(pub_ctrl, "webhook_endpoints", {}) if pub_ctrl else {}
    if hasattr(endpoints, "dict"):
        endpoints = endpoints.dict()
    if not isinstance(endpoints, dict):
        endpoints = {}

    plugins = []
    for notif in notification_plugins_meta:
        n_id = notif["id"]
        n_cfg = endpoints.get(n_id, {}) if isinstance(endpoints, dict) else {}
        if not n_cfg and n_id == "generic_webhook" and isinstance(endpoints, dict):
            n_cfg = endpoints.get("generic", {})
        if hasattr(n_cfg, "dict"):
            n_cfg = n_cfg.dict()
        if not isinstance(n_cfg, dict):
            n_cfg = {}
        
        is_in_use = bool(n_cfg.get("enabled", False))
        plugins.append({
            "id": n_id,
            "name": notif["name"],
            "category": "notification",
            "category_name": "📢 消息通知",
            "status": "Active" if is_in_use else "Ready",
            "is_in_use": is_in_use,
            "is_enabled": (n_id not in disabled),
            "origin": "core",
            "version": "V1.0",
            "description": notif["desc"],
            "cfg": n_cfg,
            "is_manageable": True
        })
    return plugins


def collect_syndication_plugins(engine, disabled: set, system_track: str) -> List[Dict[str, Any]]:
    """收集分发渠道 (Syndication)"""
    from core.adapters.syndication.targets import TARGET_REGISTRY

    synd_cfg = engine.config.syndication
    plugins = []
    for t_id in TARGET_REGISTRY.keys():
        targets = getattr(synd_cfg, "targets", synd_cfg) if synd_cfg else {}
        curr_cfg = targets.get(t_id, {}) if isinstance(targets, dict) else getattr(targets, t_id, {})
        is_in_use = curr_cfg.get("enabled", False) if isinstance(curr_cfg, dict) else getattr(curr_cfg, "enabled", False)
        if hasattr(curr_cfg, 'dict'):
            curr_cfg = curr_cfg.dict()
        t_cls = TARGET_REGISTRY.get(t_id)
        name = getattr(t_cls, "DISPLAY_NAME", None) or t_id.upper()
        icon = getattr(t_cls, "ICON", None) or "📡"
        sla_tier = getattr(t_cls, "SLA_TIER", "tier1")
        sla_label = getattr(t_cls, "SLA_LABEL", "官方直连" if sla_tier == "tier1" else "Cookie辅助")
        sla_desc = getattr(t_cls, "SLA_DESC", "通过官方开放 API 直连分发，具备企业级稳定性。" if sla_tier == "tier1" else "依赖 Web 登录凭据，建议定期校验有效性。")
        plugins.append({
            "id": t_id, "name": name, "icon": icon, "category": "publisher", "category_name": "🚀 分发渠道",
            "status": "Active" if is_in_use else "Ready", "is_in_use": is_in_use, "is_enabled": (t_id not in disabled),
            "origin": "core", "version": getattr(t_cls, "VERSION", system_track),
            "description": f"全自动分发插件：支持将出版成品推向 {name} 矩阵。", "cfg": curr_cfg, "is_manageable": True,
            "sla_tier": sla_tier, "sla_label": sla_label, "sla_desc": sla_desc
        })
    return plugins


def collect_image_hosting_plugins(engine, disabled: set, system_track: str) -> List[Dict[str, Any]]:
    """收集图床服务 (Image Hosting)"""
    from core.adapters.image_hosting.targets import IMAGE_HOST_REGISTRY

    image_hosting_cfg = getattr(engine.config, "image_hosting", {}) or {}
    if hasattr(image_hosting_cfg, "dict"):
        image_hosting_cfg = image_hosting_cfg.dict()
    elif not isinstance(image_hosting_cfg, dict):
        image_hosting_cfg = {}

    plugins = []
    for host_id, host_cls in IMAGE_HOST_REGISTRY.items():
        is_in_use = False
        current_cfg = {}
        if host_id in image_hosting_cfg and isinstance(image_hosting_cfg[host_id], dict):
            current_cfg = image_hosting_cfg[host_id]
            is_in_use = current_cfg.get("enabled", False)
        elif image_hosting_cfg.get("provider") == host_id:
            current_cfg = image_hosting_cfg
            is_in_use = True
            
        if host_id in ["s3", "aliyun_oss", "tencent_cos", "upyun_uss"] and not is_in_use:
            direct_hosting = getattr(engine.config.publish_control, "direct_upload", {})
            if isinstance(direct_hosting, dict) and host_id in direct_hosting:
                h_cfg = direct_hosting[host_id]
                if isinstance(h_cfg, dict) and h_cfg.get("enabled"):
                    is_in_use = True
                    current_cfg = h_cfg

        fallback_names = {
            "telegraph": "Telegraph 自建图床", "cloudflare_r2": "Cloudflare R2",
            "imgbb": "ImgBB", "catbox": "Catbox", "github": "GitHub 图床"
        }
        display_name = getattr(host_cls, "DISPLAY_NAME", fallback_names.get(host_id, host_id.upper()))
        description = getattr(host_cls, "DESCRIPTION", f"图床自发现适配器：支持将原稿相对图片上传至 {display_name} 并自动替换 CDN 链接。")
        plugins.append({
            "id": host_id, "name": display_name, "category": "image_hosting", "category_name": "📷 图床存储",
            "status": "Active" if is_in_use else "Ready",
            "is_in_use": is_in_use,
            "is_enabled": (host_id not in disabled),
            "origin": "core" if host_id == "s3" else "extension",
            "version": getattr(host_cls, "VERSION", system_track),
            "description": description,
            "cfg": current_cfg,
            "is_manageable": True
        })
    return plugins


def collect_tunnel_plugins(engine, disabled: set, system_track: str) -> List[Dict[str, Any]]:
    """🚀 [V126.0] 收集网络穿透能力 (Tunnel & Public Remote Access)"""
    from core.adapters.tunnel import TunnelRegistry

    tunnel_root = getattr(engine.config, "tunnel", {}) if engine and hasattr(engine, "config") else {}
    if hasattr(tunnel_root, "__dict__"):
        tunnel_dict = tunnel_root.__dict__
    elif isinstance(tunnel_root, dict):
        tunnel_dict = tunnel_root
    else:
        tunnel_dict = {}

    active_driver = tunnel_dict.get("active_driver", "") if isinstance(tunnel_dict, dict) else ""
    default_driver = TunnelRegistry.get_default_driver_id()
    plugins = []
    for p_id, cls in TunnelRegistry.list_all().items():
        current_cfg = tunnel_dict.get(p_id, {}) if isinstance(tunnel_dict, dict) else {}
        if isinstance(current_cfg, dict) and "enabled" in current_cfg:
            is_active = bool(current_cfg.get("enabled", False))
        elif active_driver:
            is_active = (p_id == active_driver)
        else:
            is_active = (p_id == default_driver)
        name = getattr(cls, "DISPLAY_NAME", p_id.upper())
        has_cfg = getattr(cls, "HAS_CONFIG", False)
        desc = getattr(cls, "DESCRIPTION", "网络穿透驱动：建立指向本地服务的高可用远程隧道通道。")
        ver = getattr(cls, "VERSION", system_track)

        plugins.append({
            "id": p_id,
            "name": name,
            "category": "tunnel",
            "category_name": "🛰️ 网络穿透",
            "status": "In-Use" if is_active else "Ready",
            "is_in_use": is_active,
            "is_enabled": (p_id not in disabled),
            "origin": "core",
            "version": ver,
            "description": desc,
            "has_config": has_cfg,
            "is_configurable": has_cfg,
            "cfg": current_cfg,
            "is_manageable": True
        })
    return plugins
