# -*- coding: utf-8 -*-
"""
Tests for 50-language I18N View Matrix and UI Localization Decoupling.
确保全球 50 种语言的前台核心视图与交互标签 100% 具备地道母语翻译，零硬编码分支。
"""

import pytest
from core.adapters.egress.ssg.base_shards.ssg_slot_matrix import (
    VIEW_I18N_MATRIX,
    get_i18n_view_label
)
from core.utils.language_data import SUPPORTED_MATRIX
from themes.sovereign.adapters.sovereign_i18n import get_ui_i18n


def test_view_i18n_matrix_covers_all_supported_languages():
    """验证 VIEW_I18N_MATRIX 对 SUPPORTED_MATRIX 中所有 50 种语言的覆盖率"""
    required_keys = ["timeline", "cards", "list", "all", "read_more"]
    
    for item in SUPPORTED_MATRIX:
        code = item["code"]
        for key in required_keys:
            label = get_i18n_view_label(key, code)
            assert label, f"Missing label for key='{key}' in lang='{code}'"
            assert isinstance(label, str) and len(label.strip()) > 0


def test_get_ui_i18n_dynamic_cascade():
    """验证 get_ui_i18n 能够动态吸收并为任意语种提供标准视图词条"""
    # 1. 验证常规主流语言
    zh_ui = get_ui_i18n("zh")
    assert zh_ui["view_cards"] == "卡片"
    assert zh_ui["view_list"] == "列表"
    assert zh_ui["view_timeline"] == "时间轴"

    en_ui = get_ui_i18n("en")
    assert en_ui["view_cards"] == "Cards"
    assert en_ui["view_list"] == "List"
    assert en_ui["view_timeline"] == "Timeline"

    ja_ui = get_ui_i18n("ja")
    assert ja_ui["view_cards"] == "カード"
    assert ja_ui["view_list"] == "リスト"
    assert ja_ui["view_timeline"] == "タイムライン"

    # 2. 验证小语种无缝自适应 (西班牙语, 法语, 德语, 越南语, 俄语, 阿拉伯语)
    es_ui = get_ui_i18n("es")
    assert es_ui["view_cards"] == "Tarjetas"
    assert es_ui["view_list"] == "Lista"

    fr_ui = get_ui_i18n("fr")
    assert fr_ui["view_cards"] == "Cartes"
    assert fr_ui["view_list"] == "Liste"

    de_ui = get_ui_i18n("de")
    assert de_ui["view_cards"] == "Karten"
    assert de_ui["view_list"] == "Liste"

    vi_ui = get_ui_i18n("vi")
    assert vi_ui["view_cards"] == "Thẻ"
    assert vi_ui["view_list"] == "Danh sách"

    ru_ui = get_ui_i18n("ru")
    assert ru_ui["view_cards"] == "Карточки"
    assert ru_ui["view_list"] == "Список"

    ar_ui = get_ui_i18n("ar")
    assert ar_ui["view_cards"] == "بطاقات"
    assert ar_ui["view_list"] == "قائمة"
