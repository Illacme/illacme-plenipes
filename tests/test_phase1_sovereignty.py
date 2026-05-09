#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Phase 1 Sovereignty Verification
职责：验证物理空间隔离、方言镜像分发与准入栅栏。
🛡️ [V50.3]：基于“出版品牌 (Imprint)”的主权校验。
"""

import os
import shutil
import pytest
from core.governance.imprint_manager import ImprintManager
from core.governance.license_guard import LicenseGuard

def test_imprint_isolation():
    """验证物理空间隔离与目录 tree 生成"""
    test_root = "test_imprint_root"
    if os.path.exists(test_root):
        shutil.rmtree(test_root)
        
    im = ImprintManager(root_dir=test_root)
    press_name = "TestPress"
    vault_path = os.path.join(test_root, "test_vault")
    os.makedirs(vault_path)
    
    # 模拟母本资源 (Mother Templates)
    os.makedirs(os.path.join(test_root, "configs"), exist_ok=True)
    with open(os.path.join(test_root, "configs/prompts.yaml"), 'w') as f:
        f.write("test_prompts: true")
    
    # 初始化空间
    success = im.init_sovereign_imprint(press_name, vault_path)
    assert success is True
    
    # 检查物理目录
    space_path = os.path.join(test_root, "imprints", press_name)
    assert os.path.exists(os.path.join(space_path, "configs/config.imprint.yaml"))
    assert os.path.exists(os.path.join(space_path, "configs/dialects/default.yaml"))
    assert os.path.exists(os.path.join(space_path, "cache"))
    
    # 验证元数据一致性
    import yaml
    with open(os.path.join(space_path, "configs", "config.imprint.yaml"), 'r') as f:
        cfg = yaml.safe_load(f)
        # 🛡️ [V50.3]：对齐主权命名 (imprint_name / vault_root)
        assert cfg.get("imprint_name") == press_name
        assert cfg.get("vault_root") == vault_path

    # 清理
    shutil.rmtree(test_root)

def test_license_fingerprint():
    """验证机器指纹稳定性"""
    fp1 = LicenseGuard.get_machine_fingerprint()
    fp2 = LicenseGuard.get_machine_fingerprint()
    assert len(fp1) == 16
    assert fp1 == fp2  # 物理指纹必须在同一机器上保持恒定

from unittest.mock import patch

@patch('core.governance.license_guard.LicenseGuard.is_licensed', return_value=False)
def test_license_gating(mock_is_licensed):
    """验证功能栅栏拦截逻辑"""
    try:
        # 在 Imprint 架构下，多品牌支持对应的 key 已更迭为 multi_imprint
        assert LicenseGuard.is_pro_feature_allowed("multi_imprint") is False
        assert LicenseGuard.is_pro_feature_allowed("multi_language") is False
        # 非管控功能应允许
        assert LicenseGuard.is_pro_feature_allowed("basic_markdown") is True
    finally:
        pass

if __name__ == "__main__":
    pytest.main([__file__])
