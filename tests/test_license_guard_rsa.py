#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for RSA Asymmetric License Guard
测试目标：
1. 验证 RSA-2048 签名的商业许可证能否正确通过 LicenseGuard.verify_license_data 验签；
2. 验证许可证防伪（内容篡改、伪造签名、设备指纹不匹配、过期）能否被 100% 拦截；
3. 验证旧版 HMAC 许可证能够平滑向后兼容通过。
"""

import time
import json
import base64
from core.governance.license_guard import LicenseGuard
from scripts.generate_license import generate_commercial_license


def test_rsa_license_verification_valid():
    """测试合法的 RSA 许可证验签"""
    current_fp = LicenseGuard.get_machine_fingerprint()
    lic_str = generate_commercial_license(
        fingerprint=current_fp,
        tier="PRO",
        customer="测试商业机构",
        days=30
    )
    
    is_valid, reason, payload = LicenseGuard.verify_license_data(lic_str)
    assert is_valid is True
    assert reason == "验证通过"
    assert payload["tier"] == "PRO"
    assert payload["fingerprint"] == current_fp
    assert payload["customer"] == "测试商业机构"

def test_rsa_license_wildcard_fingerprint():
    """测试通配设备指纹 (*) 的商业许可证"""
    lic_str = generate_commercial_license(
        fingerprint="*",
        tier="STANDARD",
        customer="多机部署客户",
        days=0  # 永久
    )
    is_valid, reason, payload = LicenseGuard.verify_license_data(lic_str)
    assert is_valid is True
    assert payload["tier"] == "STANDARD"
    assert payload["exp"] == 0

def test_rsa_license_fingerprint_mismatch():
    """测试指纹不匹配的许可证被拦截"""
    lic_str = generate_commercial_license(
        fingerprint="OTHER-DEVICE-1234",
        tier="PRO",
        customer="指纹不符测试",
        days=30
    )
    is_valid, reason, payload = LicenseGuard.verify_license_data(lic_str)
    assert is_valid is False
    assert "设备标识不匹配" in reason

def test_rsa_license_expired():
    """测试已过期的许可证被拦截"""
    current_fp = LicenseGuard.get_machine_fingerprint()
    lic_str = generate_commercial_license(
        fingerprint=current_fp,
        tier="PRO",
        customer="过期测试",
        days=-1  # 已经过期
    )
    is_valid, reason, payload = LicenseGuard.verify_license_data(lic_str)
    assert is_valid is False
    assert "已于" in reason and "过期" in reason

def test_rsa_license_tampered_payload():
    """测试篡改 payload 后签名验证失败"""
    current_fp = LicenseGuard.get_machine_fingerprint()
    lic_str = generate_commercial_license(
        fingerprint=current_fp,
        tier="STANDARD",
        customer="篡改测试",
        days=30
    )
    
    # 解码并篡改 payload 将 STANDARD 变为 PRO
    envelope = json.loads(base64.b64decode(lic_str.encode('utf-8')).decode('utf-8'))
    envelope["payload"]["tier"] = "PRO"
    tampered_lic = base64.b64encode(json.dumps(envelope).encode('utf-8')).decode('utf-8')
    
    is_valid, reason, payload = LicenseGuard.verify_license_data(tampered_lic)
    assert is_valid is False
    assert "防伪签名核验失败" in reason or "签名不匹配" in reason

def test_reject_non_rsa_signature():
    """测试系统拒绝非 RSA-2048 签名的证书（如旧版 HMAC 或任意对称签名），不再兼容旧格式"""
    current_fp = LicenseGuard.get_machine_fingerprint()
    payload = {
        "fingerprint": current_fp,
        "tier": "PRO",
        "customer": "未授权伪造客户",
        "features": ["multi_imprint"],
        "exp": int(time.time()) + 86400 * 10
    }
    
    # 模拟旧版系统生成的非 RSA 签名信封
    envelope = {
        "alg": "HMAC-SHA256",
        "payload": payload,
        "signature": "fake_hmac_signature_hex"
    }
    non_rsa_lic = base64.b64encode(json.dumps(envelope).encode('utf-8')).decode('utf-8')
    
    is_valid, reason, res_payload = LicenseGuard.verify_license_data(non_rsa_lic)
    assert is_valid is False
    assert "强制要求 RSA-2048 非对称防伪签名" in reason

