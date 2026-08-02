#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - License Issuer (官方准入许可证签发器)
职责：官方运维与商业发行人员使用的私钥/暗号签名工具，生成二进制/Base64 .lic 准入文件。

用法示例:
    python3 scripts/generate_license.py --customer "Acme Press" --fingerprint "8F3A99B1CD0477E2" --days 365 --output license.lic
    python3 scripts/generate_license.py --customer "Global Publishing Ltd" --fingerprint "*" --days 0 --output pro_unlimited.lic
"""

import os
import sys
import time
import json
import base64
import hmac
import hashlib
import argparse

SECRET_MASTER_SALT = b"ILLACME-PLENIPES-SOVEREIGN-MASTER-KEY-V100"

def generate_license(customer: str, fingerprint: str, days: int, features: list = None) -> str:
    """生成经过 HMAC 签名的 Base64 格式许可证文本"""
    if features is None:
        features = ["multi_imprint", "subfolder_ingress", "multi_language", "multi_dialect", "cloud_harvesting"]

    exp_timestamp = 0
    if days != 0:
        exp_timestamp = int(time.time() + days * 86400)

    payload = {
        "customer": customer.strip(),
        "fingerprint": fingerprint.strip().upper(),
        "tier": "PRO",
        "features": features,
        "issued_at": int(time.time()),
        "exp": exp_timestamp
    }

    sig = hmac.new(SECRET_MASTER_SALT, json.dumps(payload, sort_keys=True).encode('utf-8'), hashlib.sha256).hexdigest()
    envelope = {
        "payload": payload,
        "signature": sig
    }

    b64_str = base64.b64encode(json.dumps(envelope, ensure_ascii=False).encode('utf-8')).decode('utf-8')
    return b64_str

def main():
    parser = argparse.ArgumentParser(description="Illacme Plenipes 许可证签发工具")
    parser.add_argument("--customer", "-c", required=True, help="被授权机构或客户名称 (例: Acme Press)")
    parser.add_argument("--fingerprint", "-f", required=True, help="目标设备的物理工场编号/机器指纹 (支持 * 通配)")
    parser.add_argument("--days", "-d", type=int, default=365, help="授权有效天数 (0 表示永久授权，默认 365 天)")
    parser.add_argument("--output", "-o", default="license.lic", help="输出许可证文件名 (默认: license.lic)")

    args = parser.parse_args()

    lic_text = generate_license(args.customer, args.fingerprint, args.days)
    
    out_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(lic_text)

    print(f"✅ 许可证签发成功！")
    print(f"   机构名称: {args.customer}")
    print(f"   硬件指纹: {args.fingerprint}")
    print(f"   有效期限: {'永久授权' if args.days == 0 else f'{args.days} 天'}")
    print(f"   保存路径: {out_path}")
    print(f"\n预览内容:\n{lic_text}\n")

if __name__ == "__main__":
    main()
