#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - YAML Frontmatter Healer (物理级 YAML 语法自愈修复器)
职责：针对语法严重损坏、未闭合引号、错位缩进与非转义冒号的 Frontmatter 进行三阶物理自愈拯救。
"""

import re
import yaml
from typing import Dict, Any
from core.utils.tracing import tlog

class FrontmatterHealer:
    """🛠️ 物理级 Frontmatter 自愈修复器"""

    @staticmethod
    def heal_and_parse_yaml(yaml_str: str) -> Dict[str, Any]:
        """
        三阶物理自愈解析 YAML Frontmatter
        """
        if not yaml_str or not yaml_str.strip():
            return {}

        # --- 阶段一：原生尝试 ---
        try:
            parsed = yaml.safe_load(yaml_str)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass

        # --- 阶段二：物理语法自愈修复 ---
        healed_str = FrontmatterHealer._repair_yaml_syntax(yaml_str)
        try:
            parsed = yaml.safe_load(healed_str)
            if isinstance(parsed, dict):
                tlog.info("✨ [Frontmatter 自愈] 成功修正语法不规范的 Frontmatter YAML")
                return parsed
        except Exception:
            pass

        # --- 阶段三：行级正则降级提取 (Key-Value Key Extractor Fallback) ---
        fallback_data = FrontmatterHealer._line_by_line_extractor(yaml_str)
        if fallback_data:
            tlog.warning("⚠️ [Frontmatter 降级自愈] 无法完全修复 YAML 语法，已通过行级正则拯救有效 Key-Value 属性")
        return fallback_data

    @staticmethod
    def _repair_yaml_syntax(yaml_str: str) -> str:
        lines = yaml_str.splitlines()
        repaired_lines = []

        for line in lines:
            # 1. 替换硬 Tab 为 2 个空格
            line_str = line.replace('\t', '  ')
            
            # 忽略空行或纯注释
            if not line_str.strip() or line_str.strip().startswith('#'):
                repaired_lines.append(line_str)
                continue

            # 2. 对 KV 结构中的未闭合引号与冒号做自愈
            kv_match = re.match(r'^(\s*[\w\.\-]+:\s*)(.*)$', line_str)
            if kv_match:
                key_part = kv_match.group(1)
                val_part = kv_match.group(2).strip()

                if val_part:
                    # 如果值已有方括号、大括号或已是用引号包裹的，保持原样
                    if (val_part.startswith('[') and val_part.endswith(']')) or \
                       (val_part.startswith('{') and val_part.endswith('}')):
                        pass
                    elif (val_part.startswith('"') and val_part.endswith('"')) or \
                         (val_part.startswith("'") and val_part.endswith("'")):
                        # 检查内部是否有未转义的单双引号匹配问题
                        pass
                    else:
                        # 检查引号奇偶性，自愈闭合
                        double_quotes = val_part.count('"')
                        single_quotes = val_part.count("'")

                        if double_quotes % 2 != 0:
                            val_part += '"'
                        elif single_quotes % 2 != 0:
                            val_part += "'"
                        elif ':' in val_part:
                            # 含有未经包裹的冒号，物理强制加双引号
                            # 转义内部双引号
                            safe_val = val_part.replace('"', '\\"')
                            val_part = f'"{safe_val}"'

                line_str = f"{key_part}{val_part}"

            repaired_lines.append(line_str)

        return '\n'.join(repaired_lines)

    @staticmethod
    def _line_by_line_extractor(yaml_str: str) -> Dict[str, Any]:
        """降级拯救器：逐行抽取 valid Key: Value"""
        result = {}
        for line in yaml_str.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith('#'):
                continue

            m = re.match(r'^([\w\.\-]+):\s*(.*)$', line_str)
            if m:
                k = m.group(1).strip()
                v = m.group(2).strip()

                # 清理首尾多余引号与垃圾符号
                v = re.sub(r'^["\']|["\']$', '', v).strip()

                # 列表基础解析
                if v.startswith('[') and v.endswith(']'):
                    raw_items = v[1:-1].split(',')
                    v = [re.sub(r'^["\']|["\']$', '', item.strip()) for item in raw_items if item.strip()]

                result[k] = v

        return result
