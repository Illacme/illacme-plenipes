#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Auto Secret Encryption
测试目标：
1. 验证 SecretManager.encrypt_tree 正确识别敏感字段（键名包含 key/token/secret 或值匹配 sk-/AIza 指纹）并自动加密为 enc:...；
2. 验证 SecretManager.decrypt_tree 能够正确递归还原密文；
3. 验证 mask_display 视觉脱敏保护；
4. 验证在通过 Configuration.dump_to_disk 落盘时，磁盘 YAML 物理文件中的敏感字段被自动转换为 enc:...，而明文被彻底消除。
"""

import os
import yaml
import tempfile
from core.governance.secret_manager import SecretManager

def test_encrypt_and_decrypt_tree():
    """测试配置树敏感数据识别与自动对称加密/解密"""
    raw_config = {
        "theme": "sovereign",
        "api_key": "sk-1234567890abcdef123456",
        "compute_nodes": {
            "gemini": {
                "model": "gemini-3.5-flash",
                "api_key": "AIzaSyADP4I6TxgfPlE7MFI1BD13uxAOSmtqhxY",
                "enabled": True
            }
        },
        "channels": [
            {"name": "github", "token": "ghp_1234567890abcdefghijklmnopqrstuv"}
        ],
        "non_sensitive": "normal_value"
    }

    # 执行树形加密
    encrypted_tree = SecretManager.encrypt_tree(raw_config)

    # 验证非敏感字段未被改变
    assert encrypted_tree["theme"] == "sovereign"
    assert encrypted_tree["non_sensitive"] == "normal_value"
    assert encrypted_tree["compute_nodes"]["gemini"]["model"] == "gemini-3.5-flash"
    assert encrypted_tree["compute_nodes"]["gemini"]["enabled"] is True

    # 验证敏感字段被转换为 enc: 密文
    assert encrypted_tree["api_key"].startswith("enc:")
    assert encrypted_tree["compute_nodes"]["gemini"]["api_key"].startswith("enc:")
    assert encrypted_tree["channels"][0]["token"].startswith("enc:")

    # 验证解密树能够完整还原原始值
    decrypted_tree = SecretManager.decrypt_tree(encrypted_tree)
    assert decrypted_tree["api_key"] == "sk-1234567890abcdef123456"
    assert decrypted_tree["compute_nodes"]["gemini"]["api_key"] == "AIzaSyADP4I6TxgfPlE7MFI1BD13uxAOSmtqhxY"
    assert decrypted_tree["channels"][0]["token"] == "ghp_1234567890abcdefghijklmnopqrstuv"

def test_mask_display():
    """测试视觉脱敏展示函数"""
    assert SecretManager.mask_display("enc:gAAAAAB...") == "enc:********"
    assert SecretManager.mask_display("sk-12345678") == "sk-1****5678"
    assert SecretManager.mask_display("abcd") == "****"
    assert SecretManager.mask_display("") == ""

def test_dump_to_disk_auto_encrypts():
    """测试 Configuration.dump_to_disk 落盘时物理 YAML 自动加密敏感凭据"""
    from core.config.config_models import Configuration
    from core.config.models.ai import ComputeNode

    node = ComputeNode(
        api_key="sk-test-key-1234567890abcdef",
        model="gemini-3.5-flash",
        type="gemini"
    )
    cfg = Configuration(
        translation={"compute_nodes": {"gemini_custom": node}}
    )

    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as tf:
        temp_path = tf.name

    try:
        cfg.dump_to_disk(temp_path)
        with open(temp_path, 'r', encoding='utf-8') as f:
            disk_content = f.read()
            disk_data = yaml.safe_load(disk_content)

        # 物理文件中不得出现明文
        assert "sk-test-key-1234567890abcdef" not in disk_content
        # 物理文件中应包含密文前缀
        saved_api_key = disk_data.get("translation", {}).get("compute_nodes", {}).get("gemini_custom", {}).get("api_key", "")
        assert saved_api_key.startswith("enc:")

        # 运行时解密可完整还原
        decrypted_val = SecretManager.decrypt(saved_api_key)
        assert decrypted_val == "sk-test-key-1234567890abcdef"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

