from unittest.mock import MagicMock
from types import SimpleNamespace
from adapters.compute.google_base import GoogleCompatibleTranslator
from adapters.compute.anthropic_base import AnthropicCompatibleTranslator
from core.adapters.ai.tool_runner import call_llm_stream

def test_google_compatible_translator_messages_payload():
    """测试 GoogleCompatibleTranslator 正确将 OpenAI 格式的 messages 转换为 Gemini contents 和 systemInstruction"""
    node_cfg = SimpleNamespace(
        api_key="test-api-key",
        model="gemini-3.8-flash",
        type="gemini",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        enabled=True,
        limits=None
    )
    trans_cfg = SimpleNamespace(
        compute_nodes={"gemini": node_cfg},
        api_timeout=30,
        max_retries=1
    )
    
    translator = GoogleCompatibleTranslator("gemini", trans_cfg)
    translator.config = node_cfg

    captured_payload = {}

    def mock_post(url, json=None, **kwargs):
        nonlocal captured_payload
        captured_payload = json
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "你好！我是出版助理。"}]
                    }
                }
            ]
        }
        return mock_resp

    translator._session.post = mock_post

    # 1. 模拟 Copilot 发送 messages
    payload = {
        "model": "gemini-3.8-flash",
        "messages": [
            {"role": "system", "content": "You are a professional assistant."},
            {"role": "user", "content": "你好"}
        ],
        "params": {"temperature": 0.2}
    }

    result = translator._ask_ai(payload)
    assert result == "你好！我是出版助理。"
    assert "systemInstruction" in captured_payload
    assert captured_payload["systemInstruction"]["parts"][0]["text"] == "You are a professional assistant."
    assert len(captured_payload["contents"]) == 1
    assert captured_payload["contents"][0]["role"] == "user"
    assert captured_payload["contents"][0]["parts"][0]["text"] == "你好"

    # 2. 模拟标准翻译任务发送顶层 system + user
    captured_payload.clear()
    payload_trans = {
        "model": "gemini-3.8-flash",
        "system": "Translate to English.",
        "user": "创作者指南",
        "params": {"temperature": 0.3}
    }
    result_trans = translator._ask_ai(payload_trans)
    assert result_trans == "你好！我是出版助理。"
    assert "systemInstruction" in captured_payload
    assert captured_payload["systemInstruction"]["parts"][0]["text"] == "Translate to English."
    assert captured_payload["contents"][0]["role"] == "user"
    assert captured_payload["contents"][0]["parts"][0]["text"] == "创作者指南"

def test_anthropic_compatible_translator_messages_payload():
    """测试 AnthropicCompatibleTranslator 正确处理 messages 列表"""
    node_cfg = SimpleNamespace(
        api_key="test-api-key",
        model="claude-3-5-sonnet",
        type="anthropic",
        base_url="https://api.anthropic.com/v1",
        enabled=True,
        limits=None
    )
    trans_cfg = SimpleNamespace(
        compute_nodes={"anthropic": node_cfg},
        api_timeout=30,
        max_retries=1
    )
    translator = AnthropicCompatibleTranslator("anthropic", trans_cfg)
    translator.config = node_cfg

    anthropic_payload = translator.build_anthropic_payload(
        system_prompt="",
        user_content="",
        params={"temperature": 0.5},
        messages=[
            {"role": "system", "content": "System directive"},
            {"role": "user", "content": "Hello Claude"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]
    )

    assert anthropic_payload["system"] == "System directive"
    assert len(anthropic_payload["messages"]) == 3
    assert anthropic_payload["messages"][0] == {"role": "user", "content": "Hello Claude"}
    assert anthropic_payload["messages"][1] == {"role": "assistant", "content": "Hi there!"}
    assert anthropic_payload["messages"][2] == {"role": "user", "content": "How are you?"}

def test_tool_runner_sync_fallback_non_openai():
    """测试 call_llm_stream 对非 OpenAI 适配器降级为同步调用时，正确封装 messages、system 和 user 字段"""
    import asyncio
    class DummyNonOpenAIAdapter:
        def __init__(self):
            self.trans_cfg = SimpleNamespace(primary_model="gemini-3.8-flash")
            self.config = SimpleNamespace(model="gemini-3.8-flash")
            self.ask_ai_with_retry = MagicMock(return_value="同步调用成功响应")

    mock_adapter = DummyNonOpenAIAdapter()

    messages = [
        {"role": "system", "content": "System prompt text"},
        {"role": "user", "content": "你好"}
    ]

    async def _run():
        events = []
        async for event in call_llm_stream(mock_adapter, messages, tools=None, reasoning_enabled=False, reasoning_effort="medium", stream_enabled=True):
            events.append(event)
        return events

    events = asyncio.run(_run())

    assert len(events) == 1
    assert events[0] == {"type": "final_text", "text": "同步调用成功响应"}
    
    mock_adapter.ask_ai_with_retry.assert_called_once()
    called_payload = mock_adapter.ask_ai_with_retry.call_args[0][0]
    assert called_payload["model"] == "gemini-3.8-flash"
    assert called_payload["messages"] == messages
    assert called_payload["system"] == "System prompt text"
    assert called_payload["user"] == "你好"

def test_translator_factory_model_precedence_over_physical_node():
    """测试 TranslatorFactory 在调度策略设置 primary_model 时，其模型严格优先于物理节点中的默认模型，并在未设置时优雅回退"""
    from core.logic.ai.ai_factory import TranslatorFactory
    
    physical_node = SimpleNamespace(
        api_key="test-key",
        model="gemini-3.8-flash",  # 算力单元物理底座默认模型
        type="gemini",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        enabled=True,
        limits=None
    )
    
    trans_cfg = SimpleNamespace(
        compute_nodes={"gemini": physical_node},
        primary_node="gemini",
        primary_model="gemini-3.5-flash",  # 调度策略主力模型
        fallback_node="gemini",
        fallback_model="gemini-2.5-flash", # 调度策略容灾模型
        api_timeout=30,
        max_retries=1
    )
    
    # 1. 验证主力节点优先使用调度策略中的 primary_model
    primary_inst = TranslatorFactory._build_node("gemini", trans_cfg, role='primary')
    assert primary_inst.config.model == "gemini-3.5-flash"
    assert trans_cfg._synced_providers["gemini"].model == "gemini-3.5-flash"
    
    # 2. 验证容灾节点优先使用调度策略中的 fallback_model
    fallback_inst = TranslatorFactory._build_node("gemini", trans_cfg, role='fallback')
    assert fallback_inst.config.model == "gemini-2.5-flash"
    assert trans_cfg._synced_providers["gemini"].model == "gemini-2.5-flash"
    
    # 3. 验证当调度策略未设置品牌模型时，优雅回退至物理底座默认模型 gemini-3.8-flash
    trans_cfg.primary_model = None
    fallback_to_node_inst = TranslatorFactory._build_node("gemini", trans_cfg, role='primary')
    assert fallback_to_node_inst.config.model == "gemini-3.8-flash"



