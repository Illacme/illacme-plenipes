#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Governance - Credentials Wizard
模块职责：敏感凭据交互式加密向导。
辅助用户交互式地对配置文件（config.yaml 和本地覆盖配置）中的明文敏感密钥进行就地对称加密。
🛡️ [V66.8] 全自治安全增强版：支持格式与注释的 100% 物理保留。
"""

import os
import re
from core.governance.secret_manager import secrets
from core.utils.tracing import tlog

# 敏感字段关键字列表
SENSITIVE_KEYS = {
    'api_key', 'access_key', 'secret_key', 'token', 'password', 'key',
    'api_token', 'app_password', 'admin_api_key', 'auth_token'
}

# 排除加密的占位符模式（不区分大小写）
PLACEHOLDER_PATTERNS = [
    r'^$',
    r'^your_.*',
    r'^placeholder.*',
    r'^not-needed$',
    r'^put_your_key_here$',
    r'^none$',
    r'^null$'
]

# 明文密钥指纹模式 (sk-..., AIza..., ghp_...)
KEY_FINGERPRINTS = [
    r'sk-[a-zA-Z0-9_\-]{12,}',
    r'AIza[a-zA-Z0-9_\-]{12,}',
    r'ghp_[a-zA-Z0-9_\-]{12,}'
]


def is_placeholder(val: str) -> bool:
    """判定是否为无意义的占位符"""
    v = val.strip().lower()
    for pattern in PLACEHOLDER_PATTERNS:
        if re.match(pattern, v):
            return True
    return False


def is_sensitive_value(key: str, val: str) -> bool:
    """综合判定是否为需要加密的明文敏感数据"""
    val_clean = val.strip()
    if not val_clean:
        return False
    # 已经是密文的直接放行
    if val_clean.startswith("enc:") or val_clean.startswith("ENC:"):
        return False
    if is_placeholder(val_clean):
        return False

    # 1. 若值部分直接包含典型的明文密钥指纹，则强制判定为敏感
    for fp in KEY_FINGERPRINTS:
        if re.search(fp, val_clean):
            return True

    # 2. 若字段键名包含敏感字眼，则判定为敏感
    if key:
        k_lower = key.lower()
        if any(sk in k_lower for sk in SENSITIVE_KEYS):
            return True

    return False


def mask_plain_value(val: str) -> str:
    """对敏感明文进行脱敏展示，防止屏幕物理泄露"""
    val = val.strip()
    if len(val) <= 8:
        if len(val) <= 4:
            return "****"
        return f"{val[:2]}****{val[-2:]}"
    return f"{val[:4]}****{val[-4:]}"


def analyze_line(line: str) -> dict:
    """对 YAML 单行进行精确的词法结构剖析，用于无损回写"""
    # 1. 尝试匹配常规的键值对结构 (Indent, Key, RawValue)
    kv_match = re.match(r'^(\s*)([a-zA-Z0-9_\-]+)\s*:\s*(.*)$', line)
    if kv_match:
        indent, key, raw_val = kv_match.groups()
        # 对值部分进一步切分出 (Quote, ValueContent, CommentPart)
        val_match = re.match(r'^([\'"]?)(.*?)\1(\s*(?:#.*)?)$', raw_val)
        if val_match:
            quote, val_content, comment = val_match.groups()
            return {
                "type": "kv",
                "indent": indent,
                "key": key,
                "quote": quote,
                "val_content": val_content,
                "comment": comment
            }

    # 2. 尝试匹配 YAML 列表项结构 (Indent, RawValue)
    list_match = re.match(r'^(\s*)-\s*(.*)$', line)
    if list_match:
        indent, raw_val = list_match.groups()
        val_match = re.match(r'^([\'"]?)(.*?)\1(\s*(?:#.*)?)$', raw_val)
        if val_match:
            quote, val_content, comment = val_match.groups()
            return {
                "type": "list",
                "indent": indent,
                "quote": quote,
                "val_content": val_content,
                "comment": comment
            }

    return None


def run_credentials_wizard(config_path: str):
    """启动交互式凭据自动加密与就地无损更新"""
    files_to_scan = []
    if os.path.exists(config_path):
        files_to_scan.append(config_path)

    # 自动检索主配置文件关联的 local.yaml 文件
    base, _ = os.path.splitext(config_path)
    local_path = f"{base}.local.yaml"
    if os.path.exists(local_path):
        files_to_scan.append(local_path)

    for file_p in files_to_scan:
        tlog.info(f"📂 [安全哨兵] 正在扫描配置文件: {file_p} ...")
        try:
            with open(file_p, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            tlog.error(f"❌ 读取配置文件失败 '{file_p}': {e}")
            continue

        changes_made = False
        new_lines = []

        for idx, line in enumerate(lines):
            line_num = idx + 1
            parsed = analyze_line(line)

            if parsed:
                key = parsed.get("key")
                val = parsed["val_content"]
                if is_sensitive_value(key, val):
                    masked = mask_plain_value(val)
                    label = f"键 '{key}'" if key else "列表项"
                    print(f"\n⚠️  [安全警告] 文件 '{file_p}' 行 {line_num} 中发现明文敏感凭据:")
                    print(f"  └── {label}: {parsed['quote']}{masked}{parsed['quote']}")

                    # 提示用户交互选择
                    try:
                        user_input = input("  └── 是否对此凭据进行本地对称加密并就地回写？(y/N): ").strip().lower()
                    except (KeyboardInterrupt, EOFError):
                        print("\n🛑 用户取消操作。")
                        new_lines.append(line)
                        continue

                    if user_input in ('y', 'yes', '是'):
                        encrypted_val = secrets.encrypt(val)
                        # 组装替换后的行，确保 100% 保留缩进、引号和注释
                        if parsed["type"] == "kv":
                            new_line = f"{parsed['indent']}{key}: {parsed['quote']}{encrypted_val}{parsed['quote']}{parsed['comment']}\n"
                        else:
                            new_line = f"{parsed['indent']}-{parsed['quote']}{encrypted_val}{parsed['quote']}{parsed['comment']}\n"
                        new_lines.append(new_line)
                        changes_made = True
                        tlog.success(f"  └── 🔒 凭据已成功加密: {parsed['quote']}{encrypted_val[:12]}...{parsed['quote']}")
                    else:
                        print("  └── ℹ️  跳过此凭据，保留明文。")
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # 仅在有实际变动时回写，防止不必要的磁盘物理写操作
        if changes_made:
            try:
                with open(file_p, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                tlog.info(f"💾 [安全哨兵] 配置文件已安全就地回写: {file_p}")
            except Exception as e:
                tlog.error(f"❌ 写入配置文件失败 '{file_p}': {e}")

    tlog.info("🏁 [凭据审计] 全域脱敏扫描与加密交互向导执行完毕。")
