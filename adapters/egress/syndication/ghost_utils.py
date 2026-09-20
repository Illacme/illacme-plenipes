#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes — Ghost Syndicator Utilities
模块职责：Ghost JWT 鉴权 Token 构造与 Mobiledoc 数据格式转换。
🛡️ [SOP-01 & SOP-02]：从 ghost.py 物理拆解出的独立工具分片。
"""

import base64
import hashlib
import hmac
import json
import time


def b64url_encode(data: bytes) -> str:
    """URL-safe Base64 编码，无填充符"""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def build_ghost_jwt(key_id: str, hex_secret: str) -> str:
    """
    生成符合 Ghost Admin API 规范的 JWT Token。

    :param key_id: Admin API Key 的 ID 部分（冒号前）
    :param hex_secret: Admin API Key 的 Secret 部分（冒号后，十六进制字符串）
    :return: JWT Token 字符串
    """
    now = int(time.time())
    header = {"alg": "HS256", "kid": key_id, "typ": "JWT"}
    payload = {"iat": now, "exp": now + 300, "aud": "/admin/"}

    header_b64 = b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = b64url_encode(json.dumps(payload, separators=(",", ":")).encode())

    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    signing_key = bytes.fromhex(hex_secret)

    signature = hmac.new(signing_key, signing_input, hashlib.sha256).digest()
    signature_b64 = b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


def markdown_to_mobiledoc(markdown: str) -> str:
    """
    将 Markdown 内容包装为 Ghost Mobiledoc 格式（Markdown Card）。
    Ghost Admin API 接受 Mobiledoc JSON 字符串作为内容载体。
    """
    mobiledoc = {
        "version": "0.3.1",
        "markups": [],
        "atoms": [],
        "cards": [["markdown", {"markdown": markdown}]],
        "sections": [[10, 0]],
    }
    return json.dumps(mobiledoc, ensure_ascii=False)
