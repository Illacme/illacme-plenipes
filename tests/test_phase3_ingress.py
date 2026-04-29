#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Phase 3 Ingress Verification
职责：验证子目录映射规则、免费版拦截逻辑与语种自动探测。
"""

import os
import shutil
import pytest
from core.pipeline.vault_indexer import VaultIndexer
from core.ingress.source.local import LocalFileSource
from core.governance.license_guard import LicenseGuard

class MockConfig:
    def __init__(self, ingress_rules=None, lang="zh"):
        self.system = type('obj', (object,), {'allowed_extensions': ['.md']})
        self.ingress_settings = type('obj', (object,), {'ingress_rules': ingress_rules or []})
        self.i18n_settings = type('obj', (object,), {
            'source': type('obj', (object,), {'lang_code': lang})
        })

from unittest.mock import patch

@patch('core.governance.license_guard.LicenseGuard.is_licensed', return_value=True)
def test_pro_ingress_mapping(mock_is_licensed):
    """验证授权版下的子目录映射"""
    test_root = "test_ingress_pro"
    if os.path.exists(test_root): shutil.rmtree(test_root)
    os.makedirs(os.path.join(test_root, "docs/api"))
    
    with open(os.path.join(test_root, "docs/api/test.md"), 'w') as f:
        f.write("---\ntitle: API Test\nlang: en\n---\nContent")
        
    source = LocalFileSource(test_root)
    config = MockConfig(ingress_rules=[{"source": "docs/api", "target": "reference"}])
    
    try:
        md_index, _, _ = VaultIndexer.build_indexes(source, config)
        assert "docs/api/test.md" in md_index
        assert md_index["docs/api/test.md"]["target_prefix"] == "reference"
        assert md_index["docs/api/test.md"]["detected_lang"] == "en"
    finally:
        shutil.rmtree(test_root)

@patch('core.governance.license_guard.LicenseGuard.is_licensed', return_value=False)
def test_free_ingress_blocking(mock_is_licensed):
    """验证免费版拦截子目录"""
    test_root = "test_ingress_free"
    if os.path.exists(test_root): shutil.rmtree(test_root)
    os.makedirs(os.path.join(test_root, "docs"))
    
    with open(os.path.join(test_root, "root.md"), 'w') as f: f.write("Root")
    with open(os.path.join(test_root, "docs/sub.md"), 'w') as f: f.write("Sub")
    
    source = LocalFileSource(test_root)
    config = MockConfig()
    
    try:
        md_index, _, _ = VaultIndexer.build_indexes(source, config)
        assert "root.md" in md_index
        assert "docs/sub.md" not in md_index # 免费版应拦截子目录
    finally:
        shutil.rmtree(test_root)

def test_language_detection():
    """验证语种自动探测逻辑"""
    test_root = "test_lang_detect"
    if os.path.exists(test_root): shutil.rmtree(test_root)
    os.makedirs(test_root)
    
    # 中文内容
    with open(os.path.join(test_root, "cn.md"), 'w') as f: 
        f.write("这是一段中文内容，索引器应该能识别出来。")
    
    source = LocalFileSource(test_root)
    config = MockConfig(lang="en") # 目标语种设为 en
    
    try:
        # 免费版下，如果探测到 zh 但目标是 en，且没有授权，则应允许（因为是源语种）
        # 但如果 LanguageSentinel.is_language_allowed 拦截了，则会跳过
        md_index, _, _ = VaultIndexer.build_indexes(source, config)
        # 我们的逻辑是：如果 lang == target_lang，在免费版下会被拦截（防止自循环或冲突）
        assert "cn.md" in md_index
        assert md_index["cn.md"]["detected_lang"] == "zh"
    finally:
        shutil.rmtree(test_root)

if __name__ == "__main__":
    pytest.main([__file__])
