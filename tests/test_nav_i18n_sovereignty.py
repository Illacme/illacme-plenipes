#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [SOP-15] Nav I18N & Route Matrix Sovereignty Lock Tests
物理锁定：
1. 官方模板 showcase 英文标准名称物理锁定为 'Show'（严禁篡改）。
2. 自定义导航名称（如'核心特性'）在执行多语言翻译时，严禁被底层技术 slot 劫持，必须判定为未命中字典并交由大模型。
3. 前端 route.i18n.js 与 route.i18n.dict.js 静态语法与语义断言。
"""
import os
import re
import pytest


def test_showcase_english_name_lock_in_frontend_dict():
    """断言前端 route.i18n.dict.js 中 showcase 的英文名称必须严格锁定为 'Show'"""
    dict_js_path = os.path.join(os.path.dirname(__file__), "..", "web", "dashboard", "js", "route", "route_shards", "route.i18n.dict.js")
    assert os.path.exists(dict_js_path), "route.i18n.dict.js 文件必须物理存在"
    
    with open(dict_js_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取 showcase 字典块
    match = re.search(r'"showcase"\s*:\s*\{([^}]+)\}', content)
    assert match is not None, "route.i18n.dict.js 必须包含 'showcase' 字典定义"
    
    showcase_block = match.group(1)
    en_match = re.search(r'"en"\s*:\s*"([^"]+)"', showcase_block)
    assert en_match is not None, "showcase 块中必须包含 'en' 属性"
    assert en_match.group(1) == "Show", f"网页模板 showcase 官方英文名必须锁定为 'Show'，当前被异常篡改为: {en_match.group(1)}"


def test_nav_i18n_js_no_blind_slot_fallback():
    """断言前端 route.i18n.js 严禁将 matchedDictKey 盲目预设为 slot"""
    route_i18n_path = os.path.join(os.path.dirname(__file__), "..", "web", "dashboard", "js", "route", "route_shards", "route.i18n.js")
    assert os.path.exists(route_i18n_path), "route.i18n.js 文件必须物理存在"

    with open(route_i18n_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 严禁出现 let matchedDictKey = slot;
    assert "let matchedDictKey = slot;" not in content, "route.i18n.js 严禁盲目默认 'let matchedDictKey = slot;'，必须为 null 并根据 label 严格匹配"


@pytest.mark.anyio
async def test_backend_translate_nav_labels_custom_label_never_hijacked(anyio_backend):
    """断言后端 translate_nav_labels_impl 对自定义名称（如'核心特性'）绝不回落到 slot 字典"""
    from services.api.routes.gov.actions_shards.theme_and_publish_ops import translate_nav_labels_impl, TranslateNavLabelsRequest
    from unittest.mock import patch, MagicMock

    # 构造请求：slot 是 showcase，但 label 是用户自定义的“核心特性”
    req = TranslateNavLabelsRequest(
        label="核心特性",
        target_languages=["en", "ja"],
        slot="showcase",
        source_language="zh"
    )

    # Mock 大模型 node，确保验证进入了 AI 分支而不是被字典拦截
    mock_node = MagicMock()
    mock_node.translate_title.side_effect = lambda text, target_lang: "Core Features" if target_lang == "en" else "コア機能"

    with patch("services.api.routes.gov.actions_shards.theme_and_publish_ops.get_global_engine") as mock_get_engine, \
         patch("core.logic.ai.ai_factory.TranslatorFactory.create", return_value=mock_node):
        
        mock_engine = MagicMock()
        mock_engine.config.translation = MagicMock()
        mock_get_engine.return_value = mock_engine

        res = await translate_nav_labels_impl(req)
        assert res.get("ok") is True
        translations = res.get("translations", {})
        
        # 绝不能是 showcase 字典里的值，必须是大模型返回的“核心特性”翻译
        assert translations.get("en") == "Core Features", f"期望 'Core Features'，实际却被字典劫持为: {translations.get('en')}"
        assert translations.get("ja") == "コア機能", f"期望 'コア機能'，实际却被字典劫持为: {translations.get('ja')}"
