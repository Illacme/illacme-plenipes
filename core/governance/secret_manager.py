#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Governance - Secret Manager
模块职责：敏感信息加密。负责对配置文件中的 API Key 等核心资产进行加密存储与运行时解密。
🛡️ [AEL-Iter-v1.0]：主权安全加固。
"""

import os
from typing import Any
from cryptography.fernet import Fernet
from core.utils.tracing import tlog


class SecretManager:
    """🚀 [V1.0] 密钥管理器：保护商业核心资产"""
    
    _master_key = None
    _fernet = None

    @classmethod
    def initialize(cls, key_path: str = "core/storage/.master.key"):
        """初始化主密钥"""
        if cls._fernet: return
        
        try:
            if not os.path.exists(key_path):
                # 首次运行，生成新主密钥
                tlog.warning("🛡️ [SecretManager] 未发现主密钥，正在生成新的物理安全底座...")
                os.makedirs(os.path.dirname(key_path), exist_ok=True)
                key = Fernet.generate_key()
                with open(key_path, "wb") as f:
                    f.write(key)
                os.chmod(key_path, 0o600) # 物理层权限收紧
            
            with open(key_path, "rb") as f:
                cls._master_key = f.read()
                cls._fernet = Fernet(cls._master_key)
            tlog.info("🔐 [SecretManager] 物理安全底座已激活，敏感字段解密网关就绪。")
        except Exception as e:
            tlog.error(f"❌ [SecretManager] 初始化失败: {e}")
            raise RuntimeError(f"SECURITY_INITIALIZATION_FAILED: {e}")

    @classmethod
    def encrypt(cls, plain_text: str) -> str:
        """加密文本"""
        if not cls._fernet: cls.initialize()
        if not plain_text: return ""
        token = cls._fernet.encrypt(plain_text.encode())
        return f"enc:{token.decode()}"

    @classmethod
    def decrypt(cls, cipher_text: str) -> str:
        """解密文本 (仅处理带有 enc: 前缀的字段)"""
        if not cls._fernet: cls.initialize()
        if not cipher_text or not cipher_text.startswith("enc:"):
            return cipher_text
        
        try:
            token = cipher_text[4:].encode()
            return cls._fernet.decrypt(token).decode()
        except Exception as e:
            tlog.error(f"❌ [SecretManager] 解密失败，资产可能已损坏或密钥不匹配: {e}")
            return "DEC_ERROR"

    @classmethod
    def mask_display(cls, val: str) -> str:
        """对敏感文本进行视觉脱敏展示，防止截屏或录屏物理泄露"""
        if not val or not isinstance(val, str):
            return ""
        val = val.strip()
        if val.startswith("enc:") or val.startswith("ENC:"):
            return "enc:********"
        if len(val) <= 8:
            if len(val) <= 4:
                return "****"
            return f"{val[:2]}****{val[-2:]}"
        return f"{val[:4]}****{val[-4:]}"

    @classmethod
    def encrypt_tree(cls, data: Any, key_name: str = "") -> Any:
        """🚀 [V102.0] 递归对配置树进行敏感字段扫描并自动执行加密"""
        sensitive_keys = {
            'api_key', 'access_key', 'secret_key', 'token', 'password', 'key',
            'api_token', 'app_password', 'admin_api_key', 'auth_token'
        }
        if isinstance(data, dict):
            return {k: cls.encrypt_tree(v, str(k)) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.encrypt_tree(elem, key_name) for elem in data]
        elif isinstance(data, str):
            val_clean = data.strip()
            if not val_clean or val_clean.startswith("enc:") or val_clean.startswith("ENC:"):
                return data
            # 判定键名是否敏感
            k_lower = key_name.lower()
            is_sensitive = any(sk in k_lower for sk in sensitive_keys)
            # 判定值是否包含典型 API 密钥指纹 (sk-..., AIza..., ghp_...)
            import re
            key_fingerprints = [r'sk-[a-zA-Z0-9_\-]{12,}', r'AIza[a-zA-Z0-9_\-]{12,}', r'ghp_[a-zA-Z0-9_\-]{12,}']
            if any(re.search(fp, val_clean) for fp in key_fingerprints):
                is_sensitive = True
            
            # 排除常见非敏感占位符
            if val_clean.lower() in ("null", "none", "true", "false", "", "your_key", "placeholder"):
                is_sensitive = False

            if is_sensitive:
                encrypted = cls.encrypt(data)
                tlog.info(f"🛡️ [SecretManager] 发现敏感凭据 [{key_name}]，已自动完成主权加密落盘。")
                return encrypted
        return data

    @classmethod
    def decrypt_tree(cls, data: Any) -> Any:
        """🚀 [V102.0] 递归对配置树中的所有 enc: 密文执行透明解密"""
        if isinstance(data, dict):
            return {k: cls.decrypt_tree(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.decrypt_tree(elem) for elem in data]
        elif isinstance(data, str) and (data.startswith("enc:") or data.startswith("ENC:")):
            return cls.decrypt(data)
        return data

    @classmethod
    def mask_dict(cls, data: dict) -> dict:
        """保持历史兼容性，委托至 encrypt_tree"""
        if isinstance(data, dict):
            encrypted = cls.encrypt_tree(data)
            data.clear()
            data.update(encrypted)
        return data


# 全局管理器
secrets = SecretManager

