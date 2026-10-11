#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V127.0] Illacme Plenipes - Dispatch Pipeline Rate Limiter & Anti-Ban Guard
职责：提供面向社交媒体分发渠道的平台级频控、请求防抖与账号防封安全护栏。
物理红线：严格控制文件行数 ≤ 300 行（SOP-01），纯内存轻量级节流，不产生磁盘锁竞争。
"""

import time
from typing import Dict, Tuple, Any, Optional

# 平台安全冷却基准周期 (秒)
CHANNEL_COOLDOWN_MAP: Dict[str, int] = {
    "wechat": 30,       # 微信公众号：单篇草稿更新建议间隔 ≥ 30 秒，防 45009 频控
    "weixin": 30,
    "mp": 30,
    "zhihu": 20,        # 知乎：单篇专栏草稿建议间隔 ≥ 20 秒
    "xiaohongshu": 30,  # 小红书：建议间隔 ≥ 30 秒
    "medium": 15,       # Medium: 建议间隔 ≥ 15 秒
    "devto": 15,        # Dev.to: 建议间隔 ≥ 15 秒
    "hashnode": 15,     # Hashnode: 建议间隔 ≥ 15 秒
    "default": 10       # 默认通用渠道防抖间隔：10 秒
}

# 渠道级并发短时节流保护 (秒)
CHANNEL_GLOBAL_THROTTLE_MAP: Dict[str, int] = {
    "wechat": 5,
    "weixin": 5,
    "mp": 5,
    "zhihu": 5,
    "xiaohongshu": 5,
    "default": 3
}

# 内存账本：记录 (doc_id::target_channel) 的最近下发时间戳
_doc_channel_push_history: Dict[str, float] = {}

# 内存账本：记录 (target_channel) 全局通道的最近下发时间戳
_channel_global_push_history: Dict[str, float] = {}


def _resolve_channel_key(target_channel: str) -> str:
    """标准化渠道标识"""
    raw = (target_channel or "default").strip().lower()
    for k in CHANNEL_COOLDOWN_MAP:
        if k in raw:
            return k
    return "default"


def get_channel_cooldown_seconds(target_channel: str) -> int:
    """获取指定渠道的安全冷却时间 (秒)"""
    key = _resolve_channel_key(target_channel)
    return CHANNEL_COOLDOWN_MAP.get(key, CHANNEL_COOLDOWN_MAP["default"])


def check_and_acquire_rate_limit(doc_id: str, target_channel: str) -> Tuple[bool, str, int, int]:
    """
    🛡️ 核心门禁：检查并锁定单篇推流频率
    返回：(是否允许推流, 提示说明, 需等待秒数, 冷却总周期秒数)
    """
    if not target_channel:
        return True, "", 0, 0

    now = time.time()
    chan_key = _resolve_channel_key(target_channel)
    task_key = f"{doc_id}::{chan_key}"

    cooldown_total = get_channel_cooldown_seconds(target_channel)
    global_throttle = CHANNEL_GLOBAL_THROTTLE_MAP.get(chan_key, CHANNEL_GLOBAL_THROTTLE_MAP["default"])

    # 1. 检查同一篇文章在同一渠道的冷却期
    last_doc_time = _doc_channel_push_history.get(task_key, 0.0)
    elapsed_doc = now - last_doc_time
    if elapsed_doc < cooldown_total:
        remaining = int(cooldown_total - elapsed_doc) + 1
        return (
            False,
            f"🛡️ 平台安全频控护栏生效中：【{target_channel.upper()}】建议更新间隔 ≥ {cooldown_total} 秒，请等待 {remaining} 秒后再试以避免平台限频拦截。",
            remaining,
            cooldown_total
        )

    # 2. 检查全局渠道防抖（避免同一渠道短时间高频并发）
    last_chan_time = _channel_global_push_history.get(chan_key, 0.0)
    elapsed_chan = now - last_chan_time
    if elapsed_chan < global_throttle:
        remaining = int(global_throttle - elapsed_chan) + 1
        return (
            False,
            f"🛡️ 通道防抖拦截：该渠道刚刚下发过推流任务，请等待 {remaining} 秒再发起下一篇以防接口突发熔断。",
            remaining,
            global_throttle
        )

    # 3. 校验通过，登记当前推流时间戳
    _doc_channel_push_history[task_key] = now
    _channel_global_push_history[chan_key] = now
    return True, "", 0, cooldown_total


def get_channel_rate_limit_status(doc_id: str, target_channel: str) -> Dict[str, Any]:
    """
    🔍 查询指定文章在目标渠道的冷却状态
    """
    now = time.time()
    chan_key = _resolve_channel_key(target_channel)
    task_key = f"{doc_id}::{chan_key}"
    cooldown_total = get_channel_cooldown_seconds(target_channel)

    last_doc_time = _doc_channel_push_history.get(task_key, 0.0)
    elapsed = now - last_doc_time
    is_cooling = elapsed < cooldown_total
    remaining = int(cooldown_total - elapsed) if is_cooling else 0

    return {
        "doc_id": doc_id,
        "target_channel": target_channel,
        "is_cooling": is_cooling,
        "remaining_seconds": max(0, remaining),
        "cooldown_seconds": cooldown_total
    }


def reset_rate_limit_history(doc_id: Optional[str] = None, target_channel: Optional[str] = None) -> None:
    """自愈或测试辅助：重置频控记录"""
    global _doc_channel_push_history, _channel_global_push_history
    if not doc_id and not target_channel:
        _doc_channel_push_history.clear()
        _channel_global_push_history.clear()
        return

    if doc_id and target_channel:
        chan_key = _resolve_channel_key(target_channel)
        task_key = f"{doc_id}::{chan_key}"
        _doc_channel_push_history.pop(task_key, None)
