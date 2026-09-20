# -*- coding: utf-8 -*-
"""
Illacme-plenipes Governance - License Crypto (准入防伪加密中枢)
职责：负责物理硬件指纹提取、RSA-2048 非对称防伪签名核验及许可证信封完整性解析。
"""

import os
import uuid
import platform
import hashlib
import json
import base64
import time
import binascii
from typing import Dict, Tuple, Optional
from core.utils.tracing import tlog

# 官方内置公钥 (用于非对称防伪签名验证)
RSA_PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1xyrlTwrQ2cpKs1eG5Ab
v+huOyL0HyoM0XpS1+OU0TNxVGSS/csvpJH9WV7KV47q3DL8rg/Hz7o5HTCBJHZz
zR42oPHMsiyF1UHg754GQ14IRMkCk3STNk3xPd6gaDOi+Fu95KyAZW3aVewtu+14
FjDYN4iytGS9N1BZ8DNCajHvkCHJg2oFOO8RXW+oL6aJHsjgAmes8+f3pIg7oQ3U
JKP+qc+t0mWfqjcYlCwzkr9vbNbprsXq5bErV7oEaSng3adFmLUyWHqn/B5/54FS
EVkmlninS/CLWzvjz3Nj2zfOHF3xpfJbOAAEHOEU7ZLv6x1tENj4scRM36r4ZvWX
RQIDAQAB
-----END PUBLIC KEY-----"""


def get_machine_fingerprint() -> str:
    """🚀 [V35.1] 获取物理机器指纹：硬件级唯一标识"""
    node = uuid.getnode()
    system = platform.system()
    release = platform.release()
    machine = platform.machine()
    
    # 混合特征生成 SHA-256 指纹
    raw_id = f"{node}-{system}-{release}-{machine}"
    return hashlib.sha256(raw_id.encode()).hexdigest()[:16].upper()


def verify_rsa_signature(payload: Dict, sig_str: str) -> bool:
    """使用内置官方公钥核验 RSA-SHA256 签名"""
    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives.serialization import load_pem_public_key

        pub_key = load_pem_public_key(RSA_PUBLIC_KEY_PEM)
        sig_bytes = base64.b64decode(sig_str.encode('utf-8'))
        data_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        
        pub_key.verify(
            sig_bytes,
            data_bytes,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception as rsa_err:
        tlog.debug(f"🛡️ [RSA验签拦截] {rsa_err}")
        return False


def verify_license_data(license_text: str, current_fingerprint: Optional[str] = None) -> Tuple[bool, str, Dict]:
    """
    核验许可证字符串的合法性与防伪签名（纯 RSA-2048 非对称防伪签名）。
    
    :param license_text: 许可证 Base64 编码文本
    :param current_fingerprint: 可选当前物理硬件指纹，若未提供则自动采集
    :return: (is_valid, reason, payload)
    """
    if not license_text or not isinstance(license_text, str):
        return False, "许可证数据为空", {}
        
    license_text = license_text.strip()
    try:
        raw_bytes = base64.b64decode(license_text.encode('utf-8'))
        raw_json = raw_bytes.decode('utf-8')
        envelope = json.loads(raw_json)
    except (ValueError, binascii.Error, UnicodeDecodeError):
        return False, "许可证格式不正确 (包含非法字符或损坏的 Base64 编码)，请确认粘贴的文本或 .lic 文件是否完整", {}
    except json.JSONDecodeError:
        return False, "许可证数据结构损坏，无法解析 JSON 证书信封", {}
    except Exception as parse_err:
        return False, f"许可证解密失败: {parse_err}", {}

    if not isinstance(envelope, dict) or "payload" not in envelope or "signature" not in envelope:
        return False, "许可证结构非法，缺少 payload 或 signature", {}

    payload = envelope["payload"]
    sig = envelope["signature"]
    alg = str(envelope.get("alg", "")).upper()

    # 1. 签名算法与防伪签名核验 (强制 RSA-2048 非对称签名)
    if alg not in ("RSA-SHA256", "RSA"):
        return False, f"不支持或非法的签名算法 [{alg}]，商业版强制要求 RSA-2048 非对称防伪签名", {}

    if not verify_rsa_signature(payload, sig):
        return False, "RSA 官方防伪签名核验失败，许可证可能已被非法篡改或并非由官方签发", {}

    # 2. 硬件指纹核验
    target_fp = payload.get("fingerprint", "")
    current_fp = current_fingerprint or get_machine_fingerprint()
    if target_fp != "*" and target_fp.upper() != current_fp.upper():
        return False, f"设备标识不匹配 (授权编号: {target_fp}, 当前编号: {current_fp})", {}

    # 3. 有效期核验
    exp = payload.get("exp", 0)
    if exp > 0 and time.time() > exp:
        exp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp))
        return False, f"许可证已于 {exp_str} 过期", {}

    return True, "验证通过", payload
