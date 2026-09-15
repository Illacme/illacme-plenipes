#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Syndication Diagnostic Hub (全渠道分发智能故障诊断中枢)
模块职责：对各社交分发平台的底层报错进行精准秒级归因，输出人类可读的友好诊断与自愈指南。
遵循 SOP-01 物理行数规范 (< 300 行)。
"""

import re
from typing import Dict, Any, Optional

def diagnose_syndication_error(target_id: str, error_msg: Optional[str]) -> Dict[str, Any]:
    """
    智能解析分发错误信息，输出结构化诊断报告
    :param target_id: 渠道标识 (如 'wechat', 'juejin', 'zhihu', 'devto', 'medium')
    :param error_msg: 原始错误日志字符串
    :return: 包含 category, badge, badge_color, friendly_message, suggestion, quick_drawer_id 的字典
    """
    clean_err = str(error_msg or "").strip()
    target_lower = str(target_id or "").lower()

    if not clean_err:
        return {
            "category": "UNKNOWN",
            "badge": "⚠️ 未知异常",
            "badge_color": "#64748b",
            "friendly_message": "分发管线未返回具体错误详情。",
            "suggestion": "请点击‘重试’重新触发，或检查网络连接状态。",
            "quick_drawer_id": target_lower
        }

    err_lower = clean_err.lower()

    # ── 1. ⚙️ 平台特定规范与字段拦截诊断 (优先匹配) ─────────────
    if target_lower == "wechat":
        if "40007" in err_lower or "invalid media_id" in err_lower:
            return {
                "category": "PAYLOAD",
                "code": "WECHAT_INVALID_MEDIA_ID",
                "badge": "🖼️ 封面素材失效",
                "badge_color": "#8b5cf6",
                "friendly_message": "微信公众号草稿箱接口拒绝接收此封面素材 (40007)。",
                "suggestion": "文章缺少合规封面，系统已自动启用 900x383 科技封面自愈生成，请点击重试。",
                "quick_drawer_id": "wechat"
            }
        if "45004" in err_lower or "description size" in err_lower:
            return {
                "category": "PAYLOAD",
                "code": "WECHAT_DIGEST_LIMIT",
                "badge": "✂️ 摘要超长拦截",
                "badge_color": "#8b5cf6",
                "friendly_message": "微信公众号草稿摘要 (digest) 超过官方限制 (45004)。",
                "suggestion": "系统已启用智能截断自愈，请点击重试即可成功发布。",
                "quick_drawer_id": "wechat"
            }
        if "45110" in err_lower or "author size" in err_lower:
            return {
                "category": "PAYLOAD",
                "code": "WECHAT_AUTHOR_LIMIT",
                "badge": "✂️ 作者名称超限",
                "badge_color": "#8b5cf6",
                "friendly_message": "微信公众号作者字段超过 8 个字符限制 (45110)。",
                "suggestion": "系统已启用 8 字符智能安全清洗，请点击重试。",
                "quick_drawer_id": "wechat"
            }
        if "41039" in err_lower or "invalid content_source_url" in err_lower:
            return {
                "category": "PAYLOAD",
                "code": "WECHAT_LOCAL_SOURCE_URL",
                "badge": "🌐 原文链接受限",
                "badge_color": "#8b5cf6",
                "friendly_message": "微信禁止本地地址 (localhost/私有IP) 作为阅读原文外链 (41039)。",
                "suggestion": "系统已将私有开发环境链接自动安全置空，请使用公网可访问域名，或直接重试。",
                "quick_drawer_id": "wechat"
            }

    if target_lower == "juejin" and ("category_id" in err_lower or "edit_type" in err_lower):
        return {
            "category": "PAYLOAD",
            "code": "JUEJIN_PAYLOAD_FORMAT",
            "badge": "⚙️ 掘金格式异常",
            "badge_color": "#8b5cf6",
            "friendly_message": "稀土掘金拒绝接收此 Markdown 草稿载荷。",
            "suggestion": "系统已注入 Markdown 原生 edit_type=10 标识，请点击重试。",
            "quick_drawer_id": "juejin"
        }

    # ── 2. 🔑 认证与凭据失效类诊断 ────────────────────────────
    auth_patterns = [
        r"401", r"403", r"40001", r"40013", r"unauthorized", r"forbidden",
        r"invalid credential", r"invalid token", r"invalid api key", r"bad credentials",
        r"缺少\s*(api_key|token|cookie|secret|integration_token|app_id)",
        r"凭据", r"未配置", r"认证失败", r"授权失败", r"登录过期", r"not authenticated"
    ]
    if any(re.search(pat, err_lower) for pat in auth_patterns):
        platform_tips = {
            "wechat": "微信 AppID 或 AppSecret 配置错误或已在公众平台重置。",
            "juejin": "稀土掘金 Cookie 已过期失效，请使用嗅探功能重新捕获。",
            "zhihu": "知乎 Cookie 或 z_c0 凭据已失效，请重新复制或嗅探。",
            "bilibili": "哔哩哔哩 SESSDATA / bili_jct 凭据已过期，请重新获取。",
            "devto": "Dev.to API Key 无效或未开放权限。",
            "medium": "Medium Integration Token 无效或账号已被冻结。",
            "ghost": "Ghost Admin API Key 格式错误或未被管理员授权。"
        }
        tip = platform_tips.get(target_lower, f"{target_id.upper()} 渠道认证凭据无效或已过期。")
        return {
            "category": "AUTH",
            "code": "AUTH_INVALID_TOKEN",
            "badge": "⚠️ 凭据失效/未授权",
            "badge_color": "#ef4444",
            "friendly_message": tip,
            "suggestion": "点击右侧‘⚙️ 快速配置’，重新填入有效凭据或唤醒一键自动嗅探重新授权。",
            "quick_drawer_id": target_lower
        }

    # ── 3. ⏳ 平台频控与限流类诊断 ────────────────────────────
    rate_patterns = [
        r"429", r"45009", r"rate limit", r"too many requests", r"freq out of limit",
        r"频控", r"频率限制", r"调用过于频繁", r"throttled"
    ]
    if any(re.search(pat, err_lower) for pat in rate_patterns):
        return {
            "category": "RATE_LIMIT",
            "code": "RATE_LIMIT_EXCEEDED",
            "badge": "🛑 频率受限超限",
            "badge_color": "#f59e0b",
            "friendly_message": f"{target_id.upper()} 官方 API 触发防刷风控拦截 (429/45009)。",
            "suggestion": "系统已启用平滑退避机制，请稍候重试。",
            "quick_drawer_id": target_lower
        }

    # ── 4. 🌐 外部网络连接与代理超时类诊断 ──────────────────────
    network_patterns = [
        r"timeout", r"connecttimeout", r"readtimeout", r"proxyerror",
        r"max retries exceeded", r"connection reset", r"connection refused",
        r"ssl", r"eof occurred", r"network is unreachable", r"failed to establish"
    ]
    if any(re.search(pat, err_lower) for pat in network_patterns):
        return {
            "category": "NETWORK",
            "code": "NETWORK_ERROR",
            "badge": "⚡ 网络连接超时",
            "badge_color": "#3b82f6",
            "friendly_message": f"连接 {target_id.upper()} 官方服务器失败或超时。",
            "suggestion": "请检查本机互联网连通性，或在插件配置中指定有效的 HTTP/SOCKS5 代理。",
            "quick_drawer_id": target_lower
        }

    # ── 5. 🧩 默认兜底诊断 ────────────────────────────────────
    return {
        "category": "UNKNOWN",
        "code": "UNKNOWN",
        "badge": "⚠️ 分发推流异常",
        "badge_color": "#64748b",
        "friendly_message": clean_err[:120] + ("..." if len(clean_err) > 120 else ""),
        "suggestion": "请查阅底层堆栈，或点击‘🔄 重试’尝试重新分发推流。",
        "quick_drawer_id": target_lower
    }
