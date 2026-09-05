#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试：向导中“自动注入中英双语演示手稿与资产目录结构”功能验证
验证当用户勾选该选项时，自动为 6 种模板类型生成演示手稿，未勾选时保持纯净。
"""

import os
import shutil
import pytest
from core.governance.imprint_manager import ImprintManager
from core.editorial.vault_indexer import VaultIndexer

@pytest.fixture
def temp_workspace(tmp_path):
    root = str(tmp_path / "workspace")
    os.makedirs(root, exist_ok=True)
    yield root
    if os.path.exists(root):
        shutil.rmtree(root)

def test_bootstrap_vault_false_remains_clean(temp_workspace):
    """验证 bootstrap_vault=False 时，文库保持纯净，不注入演示文档"""
    manager = ImprintManager(root_dir=temp_workspace)
    vault_path = os.path.join(temp_workspace, "my_custom_vault")
    os.makedirs(vault_path, exist_ok=True)
    
    success = manager.init_sovereign_imprint(
        name="test_clean_press",
        manuscripts_path=vault_path,
        imprint_name="纯净测试品牌",
        bootstrap_vault=False
    )
    assert success is True
    assert len(os.listdir(vault_path)) == 0  # 依然保持为空

def test_bootstrap_vault_true_injects_all_templates_and_galaxy(temp_workspace):
    """验证 bootstrap_vault=True 时，为6种装帧模板生成中英双语演示手稿与资产目录结构"""
    manager = ImprintManager(root_dir=temp_workspace)
    vault_path = os.path.join(temp_workspace, "my_showcase_vault")
    os.makedirs(vault_path, exist_ok=True)
    
    success = manager.init_sovereign_imprint(
        name="test_showcase_press",
        manuscripts_path=vault_path,
        imprint_name="星系演示品牌",
        bootstrap_vault=True
    )
    assert success is True

    # 1. 验证资产目录结构
    assert os.path.isdir(os.path.join(vault_path, "Blog"))
    assert os.path.isdir(os.path.join(vault_path, "Docs"))
    assert os.path.isdir(os.path.join(vault_path, "Pages"))
    assert os.path.isdir(os.path.join(vault_path, "assets", "images"))
    assert os.path.isfile(os.path.join(vault_path, "assets", "images", ".gitkeep"))

    # 2. 验证根目录与 Blog 频道的中心创世手稿
    root_welcome = os.path.join(vault_path, "welcome-to-illacme.md")
    assert os.path.isfile(root_welcome)
    with open(root_welcome, "r", encoding="utf-8") as f:
        welcome_text = f.read()

    # 验证中心手稿包含 6 大模板的 WikiLinks 双向链接
    expected_links = [
        "demo-sovereign",
        "demo-universal",
        "demo-docusaurus",
        "demo-starlight",
        "demo-nextra",
        "demo-vitepress"
    ]
    extracted = VaultIndexer.extract_links(welcome_text)
    for link in expected_links:
        assert link in extracted, f"Link {link} should be present in welcome-to-illacme.md"

    # 3. 验证 6 大装帧模板特性演示手稿
    templates_features = {
        "demo-sovereign.md": ["Sovereign", "毛玻璃", "免编译直出", "Glassmorphism"],
        "demo-universal.md": ["Universal", "通用自适应", "响应式", "Responsive"],
        "demo-docusaurus.md": ["Docusaurus", ":::note", ":::tip", ":::warning", ":::danger"],
        "demo-starlight.md": ["Starlight", "Astro", "0-JS", "Card Grid"],
        "demo-nextra.md": ["Nextra", "Next.js", "MDX", "FlexSearch"],
        "demo-vitepress.md": ["VitePress", "Vite", "Vue 3", "defineConfig"]
    }

    docs_dir = os.path.join(vault_path, "Docs")
    for doc_name, keywords in templates_features.items():
        doc_path = os.path.join(docs_dir, doc_name)
        assert os.path.isfile(doc_path), f"File {doc_name} should exist in Docs/"
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()
        for kw in keywords:
            assert kw in content, f"Keyword '{kw}' should be in {doc_name}"
        # 验证每个手稿都包含反向引力回链
        doc_links = VaultIndexer.extract_links(content)
        assert "welcome-to-illacme" in doc_links, f"{doc_name} should link back to welcome-to-illacme"
