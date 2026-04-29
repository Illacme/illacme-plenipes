#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Governance - Secret Manager
模块职责：敏感信息加密。负责对配置文件中的 API Key 等核心资产进行加密存储与运行时解密。
🛡️ [AEL-Iter-v1.0]：主权安全加固。
"""

import os
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

# 全局管理器
secrets = SecretManager
