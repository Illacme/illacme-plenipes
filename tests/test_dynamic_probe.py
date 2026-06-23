#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import pytest
from unittest.mock import MagicMock
from core.adapters.ai.prober import DynamicCapabilityProber
from adapters.compute.openai import OpenAICompatibleTranslator

class DummyTranslator(OpenAICompatibleTranslator):
    def __init__(self):
        self.node_name = "test_node"
        self.config = MagicMock()
        self.config.limits = type('MockLimits', (), {'max_concurrency': 5, 'timeout': 30.0})()

class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        return self._json_data

@pytest.fixture(autouse=True)
def clean_cache():
    """每次测试前清理临时缓存文件"""
    DynamicCapabilityProber._cache = {}
    DynamicCapabilityProber._probing_models = set()
    if os.path.exists(".plenipes/capabilities_cache.json"):
        try:
            os.remove(".plenipes/capabilities_cache.json")
        except OSError:
            pass
    yield
    if os.path.exists(".plenipes/capabilities_cache.json"):
        try:
            os.remove(".plenipes/capabilities_cache.json")
        except OSError:
            pass

def test_heuristic_fallback_and_cache_mechanism():
    """验证当无缓存时，首次访问立即返回启发式默认值，并防重复触发"""
    adapter = DummyTranslator()
    adapter.safe_get_url = MagicMock(return_value="http://localhost:1234/v1")
    adapter.safe_get_config = MagicMock(return_value="not-needed")
    
    # 首次调用，应立即返回启发式推断值，且不阻塞
    caps = DynamicCapabilityProber.get_capabilities(adapter, "qwen3.5-coder")
    assert caps["cot"] is True
    assert caps["tools"] is True
    
    # 验证该模型被标记为正在探测中，避免重复触发探测任务
    cache_key = "http://localhost:1234/v1:qwen3.5-coder"
    assert cache_key in DynamicCapabilityProber._probing_models

@pytest.mark.anyio
async def test_async_probe_tools_and_cot_success():
    """验证异步探测成功流程：Tools 接口响应 200，CoT 返回带 reasoning_content，结果成功写入缓存"""
    adapter = DummyTranslator()
    adapter.safe_get_url = MagicMock(return_value="http://localhost:1234/v1")
    adapter.safe_get_config = MagicMock(return_value="not-needed")
    
    mock_session = MagicMock()
    # 模拟第一次 post 探测 Tools 返回 200，第二次 post 探测 CoT 返回 200 带 reasoning_content
    resp_tools = MockResponse(200, {"choices": [{"message": {"content": "OK"}}]})
    resp_cot = MockResponse(200, {"choices": [{"message": {"content": "9.9", "reasoning_content": "Thinking process..."}}]})
    
    mock_session.post.side_effect = [resp_tools, resp_cot]
    adapter._session = mock_session
    
    cache_key = "http://localhost:1234/v1:test-model"
    default_caps = {"cot": False, "tools": False, "stream": True, "vision": False}
    
    # 触发探测
    await DynamicCapabilityProber._async_probe(adapter, "test-model", cache_key, default_caps)
    
    # 验证最终缓存的数据
    cached_caps = DynamicCapabilityProber._cache.get(cache_key)
    assert cached_caps is not None
    assert cached_caps["tools"] is True
    assert cached_caps["cot"] is True
    
    # 验证落盘文件是否存在
    assert os.path.exists(".plenipes/capabilities_cache.json")
    with open(".plenipes/capabilities_cache.json", 'r', encoding='utf-8') as f:
        disk_cache = json.load(f)
        assert cache_key in disk_cache
        assert disk_cache[cache_key]["tools"] is True
        assert disk_cache[cache_key]["cot"] is True

@pytest.mark.anyio
async def test_async_probe_tools_rejection():
    """验证当 Tools 探针返回 400 Bad Request 时，工具自治被判定为 False"""
    adapter = DummyTranslator()
    adapter.safe_get_url = MagicMock(return_value="http://localhost:1234/v1")
    adapter.safe_get_config = MagicMock(return_value="not-needed")
    
    mock_session = MagicMock()
    # Tools 探针返回 400，CoT 返回 200 但没有思考字段
    resp_tools = MockResponse(400, {"error": "Unsupported parameter: tools"})
    resp_cot = MockResponse(200, {"choices": [{"message": {"content": "9.9"}}]})
    
    mock_session.post.side_effect = [resp_tools, resp_cot]
    adapter._session = mock_session
    
    cache_key = "http://localhost:1234/v1:test-dumb-model"
    default_caps = {"cot": True, "tools": True, "stream": True, "vision": False}
    
    await DynamicCapabilityProber._async_probe(adapter, "test-dumb-model", cache_key, default_caps)
    
    cached_caps = DynamicCapabilityProber._cache.get(cache_key)
    assert cached_caps is not None
    assert cached_caps["tools"] is False
    assert cached_caps["cot"] is False

@pytest.mark.anyio
async def test_async_probe_vision_success():
    """验证视觉探针成功流程：当视觉探测返回 200 时，vision 被点亮"""
    adapter = DummyTranslator()
    adapter.safe_get_url = MagicMock(return_value="http://localhost:1234/v1")
    adapter.safe_get_config = MagicMock(return_value="not-needed")
    
    mock_session = MagicMock()
    # 模拟三个 post 探测，分别是 Tools(400)，CoT(400)，Vision(200)
    resp_tools = MockResponse(400, {"error": "no tools"})
    resp_cot = MockResponse(400, {"error": "no cot"})
    resp_vision = MockResponse(200, {"choices": [{"message": {"content": "OK"}}]})
    
    mock_session.post.side_effect = [resp_tools, resp_cot, resp_vision]
    adapter._session = mock_session
    
    cache_key = "http://localhost:1234/v1:test-vision-model"
    default_caps = {"cot": False, "tools": False, "stream": True, "vision": False}
    
    await DynamicCapabilityProber._async_probe(adapter, "test-vision-model", cache_key, default_caps)
    
    cached_caps = DynamicCapabilityProber._cache.get(cache_key)
    assert cached_caps is not None
    assert cached_caps["tools"] is False
    assert cached_caps["cot"] is False
    assert cached_caps["vision"] is True

@pytest.mark.anyio
async def test_async_probe_vision_rejection():
    """验证视觉探针失败流程：当视觉探测返回 400 时，vision 被安全熄灭"""
    adapter = DummyTranslator()
    adapter.safe_get_url = MagicMock(return_value="http://localhost:1234/v1")
    adapter.safe_get_config = MagicMock(return_value="not-needed")
    
    mock_session = MagicMock()
    # 模拟三个 post 探测都返回 400
    resp_tools = MockResponse(400, {"error": "no tools"})
    resp_cot = MockResponse(400, {"error": "no cot"})
    resp_vision = MockResponse(400, {"error": "unsupported format"})
    
    mock_session.post.side_effect = [resp_tools, resp_cot, resp_vision]
    adapter._session = mock_session
    
    cache_key = "http://localhost:1234/v1:test-no-vision-model"
    default_caps = {"cot": False, "tools": False, "stream": True, "vision": True}
    
    await DynamicCapabilityProber._async_probe(adapter, "test-no-vision-model", cache_key, default_caps)
    
    cached_caps = DynamicCapabilityProber._cache.get(cache_key)
    assert cached_caps is not None
    assert cached_caps["vision"] is False
