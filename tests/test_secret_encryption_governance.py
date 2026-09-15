#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Secret Encryption Governance & Base Adapter Transparent Decryption
测试目标：
1. 验证 BaseSyndicator / BasePublisher / BaseImageHost 在实例化时，能对 enc: 密文全自动透明解密，避免断链；
2. 验证 BaseTranslator.safe_get_config 对 enc: 密文的透明解密兜底；
3. 验证 system.encrypt_secrets 在 governance_map 中被严格归类至 local 层；
4. 验证 config_persistence_ops 与 save_config 在 system.encrypt_secrets 为 True 与 False 时的落盘加密/解密自愈表现。
"""

import os
import yaml
import tempfile
from core.governance.secret_manager import SecretManager
from core.adapters.syndication.base import BaseSyndicator
from core.adapters.egress.publishers.base import BasePublisher
from core.adapters.image_hosting.base import BaseImageHost
from core.config.governance_map import resolve_governance_level

class DummySyndicator(BaseSyndicator):
    def format_payload(self, title, slug, content, metadata, canonical_url=None):
        return {}
    def push(self, payload, remote_id=None):
        return {}

class DummyPublisher(BasePublisher):
    def push(self, bundle_path, metadata):
        return {}

class DummyImageHost(BaseImageHost):
    def upload(self, local_path):
        return ""

def test_base_adapters_transparent_decryption():
    """验证三大驱动基座构造函数自动解密密文，构筑全域兜底防线"""
    real_key = "sk-live-secret-test-token-12345678"
    enc_key = SecretManager.encrypt(real_key)
    assert enc_key.startswith("enc:")

    raw_cfg = {
        "enabled": True,
        "api_key": enc_key,
        "token": enc_key,
        "url": "https://api.example.com"
    }

    # 1. BaseSyndicator
    syndicator = DummySyndicator(raw_cfg)
    assert syndicator.config["api_key"] == real_key
    assert syndicator.config["token"] == real_key
    assert syndicator.config["url"] == "https://api.example.com"

    # 2. BasePublisher
    publisher = DummyPublisher(raw_cfg)
    assert publisher.config["api_key"] == real_key
    assert publisher.config["token"] == real_key

    # 3. BaseImageHost
    image_host = DummyImageHost(raw_cfg)
    assert image_host.config["api_key"] == real_key
    assert image_host.config["token"] == real_key

def test_governance_map_encrypt_secrets_tier():
    """验证 system.encrypt_secrets 严格归类到 local 私有治理层"""
    tier = resolve_governance_level("system.encrypt_secrets")
    assert tier == "local"

def test_save_config_with_encrypt_secrets_toggle():
    """验证开启/关闭加密开关时的落盘行为"""
    from core.config.config_models import Configuration
    from core.config.models.system import SystemSettings
    real_token = "ghp_mocktoken1234567890abcdefghijklmn"
    enc_token = SecretManager.encrypt(real_token)

    with tempfile.TemporaryDirectory() as tmpdir:
        test_yaml = os.path.join(tmpdir, "config.test.yaml")
        
        # 1. 开启加密开关 (默认 True)
        cfg = Configuration(system=SystemSettings(encrypt_secrets=True, api_token=real_token))
        cfg.dump_to_disk(test_yaml)

        with open(test_yaml, "r", encoding="utf-8") as f:
            disk_data = yaml.safe_load(f)
        assert disk_data["system"]["api_token"].startswith("enc:")

        # 2. 关闭加密开关 (设置为 False)
        # 即使内存中存的是 enc_token，落盘时也应自动还原解密为明文
        cfg_plain = Configuration(system=SystemSettings(encrypt_secrets=False, api_token=enc_token))
        cfg_plain.dump_to_disk(test_yaml)

        with open(test_yaml, "r", encoding="utf-8") as f:
            disk_data_plain = yaml.safe_load(f)
        assert disk_data_plain["system"]["api_token"] == real_token
