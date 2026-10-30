#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 自动化守卫测试：产品语义化版本唯一真理源铁律 (Rule 18)
验证：
1. core.__version__ 与 UpdateChecker.APP_VERSION 100% 物理对齐；
2. DisplayDelegate.get_system_version 格式化输出对齐语义化版本；
3. Configuration 默认版本与 core.__version__ 物理对齐；
4. 官方主题母本与模板中 0 硬编码历史死版本 (V50.3)。
"""

from pathlib import Path
from core import __version__
from core.runtime.update_checker import UpdateChecker
from core.ui.delegate import DisplayDelegate
from core.config.config_models import Configuration


def test_core_version_is_semver_truth():
    """验证 core.__version__ 满足语义化版本格式且与发版中枢完全对齐"""
    assert __version__ == "1.8.2"
    assert UpdateChecker.APP_VERSION == __version__
    assert UpdateChecker.get_current_version() == __version__


def test_display_delegate_version_formatting():
    """验证 DisplayDelegate 统一输出 v1.8.0 格式"""
    formatted = DisplayDelegate.get_system_version()
    assert formatted == f"v{__version__}"

    cfg = Configuration()
    assert cfg.version == __version__
    assert DisplayDelegate.get_system_version(cfg) == f"v{__version__}"


def test_templates_free_of_hardcoded_v50_version():
    """验证官方主题母本与核心模板中 0 残留 V50.3 硬编码版本"""
    root = Path(__file__).parent.parent
    check_files = [
        root / "themes" / "sovereign" / "templates" / "layout.html",
        root / "themes" / "sovereign" / "templates" / "404.html",
        root / "themes" / "docusaurus" / "src" / "pages" / "index.js",
    ]
    for p in check_files:
        assert p.exists(), f"Template file missing: {p}"
        content = p.read_text(encoding="utf-8")
        assert "V50.3" not in content, f"Hardcoded V50.3 found in {p}"
