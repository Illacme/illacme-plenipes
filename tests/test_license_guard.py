#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - License Guard Unit Tests
测试核心准入卫士 LicenseGuard 的机器指纹匹配、HMAC防伪签名、过期校验、物理落盘与功能栅栏。
"""

import os
from core.governance.license_guard import LicenseGuard
from scripts.generate_license import generate_license

def test_machine_fingerprint():
    fp = LicenseGuard.get_machine_fingerprint()
    assert isinstance(fp, str)
    assert len(fp) == 16
    assert fp == fp.upper()

def test_license_issuer_and_verification():
    fp = LicenseGuard.get_machine_fingerprint()
    lic_text = generate_license(customer="Test Press", fingerprint=fp, days=30)
    
    is_valid, reason, payload = LicenseGuard.verify_license_data(lic_text)
    assert is_valid is True
    assert reason == "验证通过"
    assert payload["customer"] == "Test Press"
    assert payload["fingerprint"] == fp
    assert payload["tier"] == "PRO"

def test_license_wildcard_fingerprint():
    lic_text = generate_license(customer="Wildcard Customer", fingerprint="*", days=10)
    is_valid, reason, payload = LicenseGuard.verify_license_data(lic_text)
    assert is_valid is True
    assert payload["fingerprint"] == "*"

def test_license_mismatched_fingerprint():
    lic_text = generate_license(customer="Mismatch Test", fingerprint="WRONGFINGERPRINT", days=10)
    is_valid, reason, payload = LicenseGuard.verify_license_data(lic_text)
    assert is_valid is False
    assert "设备标识不匹配" in reason

def test_license_expired():
    # 生成已过期的许可证 (-1 天)
    lic_text = generate_license(customer="Expired Test", fingerprint="*", days=-1)
    is_valid, reason, payload = LicenseGuard.verify_license_data(lic_text)
    assert is_valid is False
    assert "已于" in reason and "过期" in reason

def test_invalid_unicode_license_input():
    # 测试包含中文字符或非 Base64 ASCII 字符的异常输入
    invalid_text = "这是测试用的非 ASCII 乱码证书文件内容！"
    is_valid, reason, payload = LicenseGuard.verify_license_data(invalid_text)
    assert is_valid is False
    assert "许可证格式不正确" in reason
    assert "包含非法字符或损坏的 Base64 编码" in reason

def test_license_activation_and_revocation(tmp_path, monkeypatch):
    # 使用临时文件测试激活落盘与注销
    test_lic_file = os.path.join(tmp_path, ".plenipes", "license.lic")
    monkeypatch.setattr(LicenseGuard, "get_license_file_path", lambda: test_lic_file)
    monkeypatch.delenv("ILLACME_DEV_LICENSE", raising=False)
    LicenseGuard.clear_cache()

    from core.governance.imprint_manager import im
    old_imp = im.active_imprint
    try:
        im.active_imprint = "custom_press"
        fp = LicenseGuard.get_machine_fingerprint()
        lic_text = generate_license(customer="Activation Test", fingerprint=fp, days=365)

        # 1. 初始自定义品牌为 LITE 状态
        assert LicenseGuard.is_licensed() is False
        info = LicenseGuard.get_license_info()
        assert info["tier"] == "LITE"

        # 2. 点火激活
        success, msg = LicenseGuard.activate_license(lic_text)
        assert success is True
        assert os.path.exists(test_lic_file)

        # 3. 验证激活为 PRO 状态
        assert LicenseGuard.is_licensed() is True
        info = LicenseGuard.get_license_info()
        assert info["tier"] == "PRO"
        assert info["customer"] == "Activation Test"

        # 4. 验证功能栅栏拦截解禁
        assert LicenseGuard.is_pro_feature_allowed("multi_imprint") is True
        assert LicenseGuard.is_pro_feature_allowed("multi_language") is True

        # 5. 注销许可证
        rev_success, rev_msg = LicenseGuard.revoke_license()
        assert rev_success is True
        assert not os.path.exists(test_lic_file)
        assert LicenseGuard.is_licensed() is False
        assert LicenseGuard.get_license_info()["tier"] == "LITE"
    finally:
        im.active_imprint = old_imp
