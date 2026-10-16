#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Unit Test: Dispatch Pipeline Rate Limiter & Anti-Ban Safety Guard
验证社交媒体单篇推流平台级频控限流、通道级防抖拦截与倒计时计算
"""

import pytest
from services.api.logic.dispatch_ops_shards.pipeline_shards.pipeline_rate_limiter import (
    check_and_acquire_rate_limit,
    get_channel_rate_limit_status,
    reset_rate_limit_history,
    get_channel_cooldown_seconds
)


@pytest.fixture(autouse=True)
def clean_rate_limit_env():
    """每次测试前后自动清空频控记录"""
    reset_rate_limit_history()
    yield
    reset_rate_limit_history()


def test_channel_cooldown_duration():
    """验证各主流渠道的预设冷却时长"""
    assert get_channel_cooldown_seconds("wechat") == 30
    assert get_channel_cooldown_seconds("weixin") == 30
    assert get_channel_cooldown_seconds("mp") == 30
    assert get_channel_cooldown_seconds("zhihu") == 20
    assert get_channel_cooldown_seconds("medium") == 15
    assert get_channel_cooldown_seconds("devto") == 15
    assert get_channel_cooldown_seconds("unknown_channel") == 10


def test_single_doc_rate_limit_interception():
    """验证同一篇稿件在冷却期内的二次推流拦截"""
    doc = "docs/test-guide.md"
    channel = "wechat"

    # 第一次下发推流：应当允许
    allowed, msg, retry_after, cd_total = check_and_acquire_rate_limit(doc, channel)
    assert allowed is True
    assert retry_after == 0
    assert cd_total == 30

    # 立即发起第二次推流：应当被拦截，返回剩余秒数
    allowed_2, msg_2, retry_after_2, cd_total_2 = check_and_acquire_rate_limit(doc, channel)
    assert allowed_2 is False
    assert retry_after_2 > 0
    assert "平台安全频控护栏生效中" in msg_2

    # 查询状态
    status = get_channel_rate_limit_status(doc, channel)
    assert status["is_cooling"] is True
    assert status["remaining_seconds"] > 0
    assert status["cooldown_seconds"] == 30


def test_different_docs_independent_rate_limit():
    """验证不同稿件在同一渠道下的独立频控，杜绝全局粗暴拦截导致首点被误阻"""
    doc_1 = "docs/first.md"
    doc_2 = "docs/second.md"
    channel = "wechat"

    # 第一篇推流成功
    allowed, _, _, _ = check_and_acquire_rate_limit(doc_1, channel)
    assert allowed is True

    # 紧接着推流第二篇不同文档，不应受到第一篇的粗暴干扰阻断（独立频控）
    allowed_second, _, _, _ = check_and_acquire_rate_limit(doc_2, channel)
    assert allowed_second is True

def test_clear_rate_limit_instant_unfreeze():
    """验证推流失败或自愈时的频控即时解冻契约"""
    from services.api.logic.dispatch_ops_shards.pipeline_shards.pipeline_rate_limiter import clear_rate_limit
    doc = "docs/failed_article.md"
    channel = "wechat"

    # 首次触发
    allowed, _, _, _ = check_and_acquire_rate_limit(doc, channel)
    assert allowed is True

    # 重复触发被拦截
    allowed_blocked, _, _, _ = check_and_acquire_rate_limit(doc, channel)
    assert allowed_blocked is False

    # 模拟管线失败即时解冻
    clear_rate_limit(doc, channel)

    # 解冻后应可立即重新触发
    allowed_retry, _, _, _ = check_and_acquire_rate_limit(doc, channel)
    assert allowed_retry is True
