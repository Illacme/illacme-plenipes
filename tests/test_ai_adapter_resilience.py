#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for AI Adapter Resilience & Full Transparent Decryption
测试目标：
1. 验证 BaseTranslator 在实例化时，能对 node 配置中的 enc: 密文全自动透明解密；
2. 验证 OpenAI、Google Gemini、Anthropic 等主流协议适配器拿到的一定是真实明文 Key；
3. 验证 Session 自动绑定全局网络代理；
4. 验证网络超时动态感应 system.network_timeout。
"""

from unittest.mock import MagicMock, patch
from core.governance.secret_manager import SecretManager
from adapters.compute.openai import OpenAICompatibleTranslator
from adapters.compute.google_base import GoogleCompatibleTranslator
from adapters.compute.anthropic import AnthropicTranslator

def test_ai_adapter_secret_transparent_decryption():
    """验证算力适配器基座对 enc: 密文的全自动透明解密"""
    real_api_key = "sk-test-ai-key-9876543210abcdef"
    enc_api_key = SecretManager.encrypt(real_api_key)
    assert enc_api_key.startswith("enc:")

    # 构造 mock 的翻译总配置
    mock_node_cfg = MagicMock()
    mock_node_cfg.api_key = enc_api_key
    mock_node_cfg.model = "gpt-4o"
    mock_node_cfg.base_url = "https://api.openai.com/v1"
    mock_node_cfg.limits = MagicMock(max_concurrency=2, timeout=30.0)

    mock_trans_cfg = MagicMock()
    mock_trans_cfg.compute_nodes = {"test_openai": mock_node_cfg}
    mock_trans_cfg.llm_concurrency = 2
    mock_trans_cfg.max_retries = 3

    # 1. OpenAI 兼容适配器
    adapter = OpenAICompatibleTranslator("test_openai", mock_trans_cfg)
    assert adapter.config.api_key == real_api_key
    assert adapter.safe_get_config("api_key") == real_api_key

    # 2. Google 适配器
    google_node = MagicMock()
    google_node.api_key = enc_api_key
    google_node.model = "gemini-1.5-pro"
    google_node.base_url = "https://generativelanguage.googleapis.com/v1beta"
    google_node.limits = MagicMock(max_concurrency=2, timeout=30.0)
    mock_trans_cfg.compute_nodes["test_google"] = google_node

    google_adapter = GoogleCompatibleTranslator("test_google", mock_trans_cfg)
    assert google_adapter.config.api_key == real_api_key
    assert google_adapter.safe_get_config("api_key") == real_api_key

    # 3. Anthropic 适配器
    anthropic_node = MagicMock()
    anthropic_node.api_key = enc_api_key
    anthropic_node.model = "claude-3-5-sonnet-20241022"
    anthropic_node.base_url = "https://api.anthropic.com/v1"
    anthropic_node.limits = MagicMock(max_concurrency=2, timeout=30.0)
    mock_trans_cfg.compute_nodes["test_anthropic"] = anthropic_node

    anthropic_adapter = AnthropicTranslator("test_anthropic", mock_trans_cfg)
    assert anthropic_adapter.config.api_key == real_api_key
    assert anthropic_adapter.safe_get_config("api_key") == real_api_key

def test_ai_adapter_proxy_and_timeout_alignment():
    """验证算力适配器 Session 自动注入全局代理与治理中心网络超时"""
    mock_node_cfg = MagicMock()
    mock_node_cfg.api_key = "sk-plain-key"
    mock_node_cfg.model = "gpt-4o"
    mock_node_cfg.base_url = "https://api.openai.com/v1"
    mock_node_cfg.limits = MagicMock(max_concurrency=2, timeout=None)
    mock_node_cfg.proxy = None
    mock_node_cfg.timeout = None

    mock_trans_cfg = MagicMock()
    mock_trans_cfg.compute_nodes = {"test_node": mock_node_cfg}
    mock_trans_cfg.global_proxy = "http://127.0.0.1:7890"
    mock_trans_cfg.api_timeout = None

    with patch("core.runtime.engine_singleton.get_global_engine", return_value=None), \
         patch("core.config.config.load_config") as mock_load:
        mock_sys = MagicMock()
        mock_sys.system.global_proxy = "http://127.0.0.1:7890"
        mock_sys.system.network_timeout = 25
        mock_load.return_value = mock_sys

        adapter = OpenAICompatibleTranslator("test_node", mock_trans_cfg)
        
        # 验证代理自动注入 Session
        assert adapter.get_proxy() == "http://127.0.0.1:7890"
        assert adapter.get_proxy_dict() == {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
        assert adapter._session.proxies.get("http") == "http://127.0.0.1:7890"
        assert adapter._session.proxies.get("https") == "http://127.0.0.1:7890"

        # 验证治理中心超时对齐
        assert adapter.get_network_timeout() == 25.0
