import pytest
from core.adapters.ai.tool_runner import parse_xml_tool_calls

@pytest.fixture
def anyio_backend():
    return 'asyncio'

def test_parse_xml_tool_calls_basic():
    """
    验证标准的 XML-like 工具调用能被 parse_xml_tool_calls 正确捕获并解析。
    """
    text = """
    些许文字描述
    <tool_call>
    <function=read_document>
    <parameter=relative_path>
    Private/Plenipes/README.md
    </parameter>
    </function>
    </tool_call>
    后面的一些文字
    """
    events = parse_xml_tool_calls(text)
    assert len(events) == 1
    assert events[0].name == "read_document"
    assert events[0].arguments == {"relative_path": "Private/Plenipes/README.md"}
    assert events[0].id.startswith("xml_")

def test_parse_xml_tool_calls_multiple():
    """
    验证单次输出中包含多个 XML-like 工具调用的情况。
    """
    text = """
    <tool_call>
    <function=read_document>
    <parameter=relative_path>
    Index.md
    </parameter>
    </function>
    </tool_call>
    
    <tool_call>
    <function=write_document>
    <parameter=relative_path>
    Docs/test.md
    </parameter>
    <parameter=content>
    # Hello
    This is test.
    </parameter>
    </function>
    </tool_call>
    """
    events = parse_xml_tool_calls(text)
    assert len(events) == 2
    assert events[0].name == "read_document"
    assert events[0].arguments == {"relative_path": "Index.md"}
    
    assert events[1].name == "write_document"
    assert events[1].arguments == {
        "relative_path": "Docs/test.md",
        "content": "# Hello\n    This is test."
    }

def test_parse_xml_tool_calls_no_param_name():
    """
    验证对于只有一个参数但无参数名标签的极简情况（猜测自愈机制）。
    """
    text = """
    <tool_call>
    <function=read_document>
    <parameter>
    Docs/about.md
    </parameter>
    </function>
    </tool_call>
    """
    events = parse_xml_tool_calls(text)
    assert len(events) == 1
    assert events[0].name == "read_document"
    assert events[0].arguments == {"relative_path": "Docs/about.md"}

@pytest.mark.anyio
async def test_call_llm_stream_heals_xml():
    """
    验证 call_llm_stream 在面对流式 reasoning_content 吐出 XML 工具调用时，
    能够完美自愈并 yield 正确的 tool_calls 事件。
    """
    from core.adapters.ai.tool_runner import call_llm_stream
    from unittest.mock import MagicMock

    # 1. 构造一个符合 OpenAICompatibleTranslator MRO 要求的 Mock Adapter
    class MockTranslator:
        pass
    class OpenAICompatibleTranslator(MockTranslator):
        pass
    class ActiveAdapter(OpenAICompatibleTranslator):
        def __init__(self):
            self.config = MagicMock()
            self.config.model = "qwen/qwen3.5-9b"
            self.timeout = 10
            self._session = MagicMock()
            
        def safe_get_url(self):
            return "http://localhost:1234/v1"
            
        def safe_get_config(self, key):
            return "test-key"

    adapter = ActiveAdapter()

    # 2. 模拟响应流中的 chunks
    chunks = [
        b'data: {"choices": [{"delta": {"role": "assistant", "reasoning_content": "<tool_call>"}}]}\n',
        b'data: {"choices": [{"delta": {"reasoning_content": "\\n<function=read_document>"}}]}\n',
        b'data: {"choices": [{"delta": {"reasoning_content": "\\n<parameter=relative_path>"}}]}\n',
        b'data: {"choices": [{"delta": {"reasoning_content": "\\nPrivate/Plenipes/README.md"}}]}\n',
        b'data: {"choices": [{"delta": {"reasoning_content": "\\n</parameter>"}}]}\n',
        b'data: {"choices": [{"delta": {"reasoning_content": "\\n</function>"}}]}\n',
        b'data: {"choices": [{"delta": {"reasoning_content": "\\n</tool_call>"}}]}\n',
        b'data: [DONE]\n'
    ]

    mock_resp = MagicMock()
    mock_resp.iter_lines.return_value = chunks
    adapter._session.post.return_value = mock_resp

    # 3. 执行流调用并收集结果
    events = []
    async for chunk in call_llm_stream(adapter, messages=[], tools=[], reasoning_enabled=True, reasoning_effort="medium"):
        events.append(chunk)

    # 4. 验证 yields
    # 验证中间有 thinking_chunk
    thinking_chunks = [e for e in events if e["type"] == "thinking_chunk"]
    assert len(thinking_chunks) > 0
    
    # 验证最后自愈成功，产生 tool_calls 类型的事件，并且包含 read_document
    tool_call_events = [e for e in events if e["type"] == "tool_calls"]
    assert len(tool_call_events) == 1
    
    events_list = tool_call_events[0]["events"]
    assert len(events_list) == 1
    assert events_list[0].name == "read_document"
    assert events_list[0].arguments == {"relative_path": "Private/Plenipes/README.md"}


def test_openai_healer_refuses_reasoning_content_for_translation():
    """
    验证 OpenAI 兼容适配器在 content 为空但 reasoning_content 不为空时，
    若 payload 包含 is_translation=True，则拒绝降级使用 reasoning_content，
    而当 is_translation=False 时允许降级，is_json=True 时同样拒绝降级。
    """
    from adapters.compute.openai import OpenAICompatibleTranslator
    from unittest.mock import MagicMock
    import requests

    # 1. 实例化一个 Mock 风格 of OpenAI 适配器
    trans_cfg = MagicMock()
    trans_cfg.api_key = "test-key"
    trans_cfg.base_url = "http://localhost:1234/v1"
    trans_cfg.model = "qwen3.5"
    trans_cfg.temperature = 0.2
    trans_cfg.max_tokens = 2048
    trans_cfg.params = {}
    
    mock_config = MagicMock()
    mock_config.limits.max_concurrency = 2
    mock_config.limits.timeout = 60.0
    trans_cfg.compute_nodes.get.return_value = mock_config

    translator = OpenAICompatibleTranslator("test_node", trans_cfg)
    translator.timeout = 10

    # 2. 模拟 requests.Session.post 返回空的 content 却有 reasoning_content
    mock_resp = MagicMock(spec=requests.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "",
                    "reasoning_content": "Analyze the Request: 1. Translate Chinese to English..."
                }
            }
        ]
    }
    translator._session.post = MagicMock(return_value=mock_resp)

    # 3.1 测试正常文本（is_translation=False），应自愈降级
    payload_normal = {
        "model": "qwen3.5",
        "messages": [{"role": "user", "content": "hello"}],
        "is_json": False,
        "is_translation": False
    }
    res_normal = translator._ask_ai(payload_normal)
    assert res_normal == "Analyze the Request: 1. Translate Chinese to English..."

    # 3.2 测试翻译请求（is_translation=True），应拒绝降级
    payload_trans = {
        "model": "qwen3.5",
        "messages": [{"role": "user", "content": "hello"}],
        "is_json": False,
        "is_translation": True
    }
    res_trans = translator._ask_ai(payload_trans)
    assert res_trans == ""

    # 3.3 测试 JSON 请求（is_json=True），应拒绝降级
    payload_json = {
        "model": "qwen3.5",
        "messages": [{"role": "user", "content": "hello"}],
        "is_json": True,
        "is_translation": False
    }
    res_json = translator._ask_ai(payload_json)
    assert res_json == ""


