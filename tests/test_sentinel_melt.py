#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from core.adapters.ai.agent_loop import AutonomousAgent
from core.adapters.ai.tool_protocol import ToolCallEvent
from core.adapters.ai.base import BaseTranslator

class DummyTranslator(BaseTranslator):
    """用于测试的模拟翻译器"""
    def __init__(self):
        # 绕过父类复杂的配置对正逻辑，仅赋予最基础的属性
        self.trans_cfg = type('MockTransCfg', (), {'primary_model': 'qwen3.5-9b'})()
        self.config = type('MockConfig', (), {'model': 'qwen3.5-9b'})()
        self.timeout = 5

    def safe_get_url(self, path=""):
        return "http://localhost:0"

    def safe_get_config(self, key):
        return "none"

    def _ask_ai(self, payload) -> str:
        return "Mock Response"

@pytest.mark.anyio
async def test_sentinel_infinite_loop_melt():
    """
    🛡️ [自检熔断测试]：
    模拟大模型连续 3 次返回完全相同的 Tool 调用（且工具执行也返回完全相同报错的情况），
    验证 Repetitive Action Loop Sentinel 是否能精准在第 3 次时发生自动熔断保护。
    """
    translator = DummyTranslator()
    agent = AutonomousAgent(ai_adapter=translator, max_iterations=5)

    # 1. 模拟 _call_llm_stream 逻辑，让它在前几轮不断返回相同的工具调用
    # 模拟工具：check_health，参数为空
    tool_event = ToolCallEvent(tool_name="check_health", arguments={}, raw_call_id="call_1")

    call_count = 0
    async def mock_call_llm_stream(messages, tools, reasoning_enabled, reasoning_effort):
        nonlocal call_count
        call_count += 1
        # 返回工具调用事件
        yield {"type": "tool_calls", "events": [tool_event]}

    agent._call_llm_stream = mock_call_llm_stream

    # 2. 执行核心 Agent 循环并收集流式事件
    events = []
    async for event in agent.execute_task_stream("system prompt", "user prompt"):
        events.append(event)

    # 3. 结果断言
    # 检查返回事件列表
    event_types = [e["type"] for e in events]
    print(f"Captured events: {event_types}")

    # 验证是否包含了 Sentinel 熔断警告和最终熔断消息
    has_warning = any("[Sentinel] 熔断警告" in e.get("message", "") for e in events if e["type"] == "step")
    has_final_melt = any("[Sentinel] 已成功熔断" in e.get("message", "") for e in events if e["type"] == "final")

    assert has_warning, "应该触发 Sentinel 熔断警告"
    assert has_final_melt, "应该以 Sentinel 熔断消息优雅结束当前循环"
    
    # 因为在第 3 轮重复工具并返回相同结果时熔断，且循环是在执行完工具后进行判断，
    # 故 1 次正常执行，加上 3 次完全相同的重复（共 4 轮），第 4 次检测到第 3 次重复，触发 return 退出，
    # 所以 call_llm_stream 应该被调用了 4 次。
    assert call_count == 4, f"大模型应该只被调用了 4 次，实际调用了 {call_count} 次"
    assert agent._repetition_count == 3, f"重复计数器应该达到 3 轮，实际为 {agent._repetition_count}"
