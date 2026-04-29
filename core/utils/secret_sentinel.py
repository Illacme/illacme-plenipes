#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - SecretSentinel
职责：主权凭据加密盾牌。基于物理机器指纹对敏感配置进行加密存储。
🛡️ [V35.2]：工业级合规加固。
"""

import base64
import os
import hashlib
from cryptography.fernet import Fernet
from core.utils.tracing import tlog

class SecretSentinel:
    """🚀 [V35.2] 凭据哨兵：确保主权空间内的敏感信息不以明文存储"""
    
    _key = None

    @classmethod
    def _get_machine_key(cls) -> bytes:
        """基于物理机器指纹生成唯一的 32 字节 Fernet 密钥"""
        if cls._key:
            return cls._key
            
        try:
            # 🚀 获取物理指纹 (MacOS/Linux 兼容)
            import uuid
            machine_id = str(uuid.getnode())
            # 结合用户名进一步锁定主权
            owner = os.getlogin()
            
            seed = f"illacme-sovereign-{machine_id}-{owner}".encode()
            hash_key = hashlib.sha256(seed).digest()
            cls._key = base64.urlsafe_b64encode(hash_key)
            return cls._key
        except Exception as e:
            tlog.error(f"🚨 [SecretSentinel] 密钥生成失败: {e}")
            raise RuntimeError("无法确立物理加密主权")

    @classmethod
    def encrypt(cls, plain_text: str) -> str:
        """加密明文，返回带 ENC: 前缀的密文"""
        if not plain_text or plain_text.startswith("ENC:"):
            return plain_text
            
        f = Fernet(cls._get_machine_key())
        token = f.encrypt(plain_text.encode())
        return f"ENC:{token.decode()}"

    @classmethod
    def decrypt(cls, encrypted_text: str) -> str:
        """解密带 ENC: 前缀的密文，非 ENC 开头则原样返回"""
        if not encrypted_text or not encrypted_text.startswith("ENC:"):
            return encrypted_text
            
        try:
            f = Fernet(cls._get_machine_key())
            token = encrypted_text.replace("ENC:", "").encode()
            return f.decrypt(token).decode()
        except Exception as e:
            tlog.error(f"🛑 [SecretSentinel] 解密失败 (可能由于物理迁移或密钥损坏): {e}")
            return "DEC_FAILED"

# 全局哨兵单例
sentinel = SecretSentinel()
