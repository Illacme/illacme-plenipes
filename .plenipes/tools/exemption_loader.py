#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - 治理豁免白名单加载器 🚀 [V5.4]
职责：从 .plenipes/governance/exemptions.yaml 加载红线豁免白名单。
消费方：pre-commit / sentinel_matrix / sovereign_audit

设计原则 - 安全一侧失败 (Fail-Safe)：
  当 YAML 文件缺失或损坏时，返回空集合。
  效果：所有超标文件都将被拦截（安全方向），而非全部放行。
"""
import os
import re


def _locate_project_root():
    """从当前文件位置向上查找项目根目录 (包含 .plenipes/ 的目录)"""
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(10):  # 最多向上遍历 10 层
        if os.path.isdir(os.path.join(current, ".plenipes")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


def load_redline_exemptions():
    """加载 300 行红线豁免文件列表

    Returns:
        set[str]: 豁免文件路径集合（相对于项目根目录）。
                  加载失败时返回空集合 (安全一侧失败)。
    """
    root = _locate_project_root()
    if not root:
        print("  ⚠️  [豁免加载器] 无法定位项目根目录，豁免白名单降级为空集合。")
        return set()

    yaml_path = os.path.join(root, ".plenipes", "governance", "exemptions.yaml")
    if not os.path.exists(yaml_path):
        print(f"  ⚠️  [豁免加载器] 未找到 {yaml_path}，豁免白名单降级为空集合。")
        return set()

    try:
        import yaml  # 首选：精确解析
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        entries = data.get("redline_exempt_files", []) if data else []
        return set(entries)
    except Exception as e:
        # PyYAML 在钩子运行环境可能缺失或 YAML 解析异常：
        # 降级为内置极简解析器，确保红线豁免白名单仍可被加载（不降级为空集）。
        print(f"  ⚠️  [豁免加载器] PyYAML 不可用/解析失败 ({e})，启用内置降级解析器。")
        return _fallback_load_redline_exemptions(yaml_path)


def _fallback_load_redline_exemptions(yaml_path):
    """极简 YAML 降级解析：仅支持本项目豁免文件结构

    支持的语法：
      - 顶层块列表键   key:
      - 列表项         - value
      - # 注释与空行忽略
    当 PyYAML 不可用时（如 pre-commit 钩子的 python 环境）保证豁免白名单仍生效，
    而非安全一侧失败成空集导致所有超标文件被误拦截。
    """
    result = {}
    current_key = None
    with open(yaml_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.split("#", 1)[0].rstrip()  # 去除行内注释
            if not line.strip():
                continue
            key_m = re.match(r"^([A-Za-z0-9_-]+):\s*$", line)
            if key_m:
                current_key = key_m.group(1)
                result.setdefault(current_key, [])
                continue
            item_m = re.match(r"^\s*-\s+(.+?)\s*$", line)
            if item_m and current_key is not None:
                result[current_key].append(item_m.group(1))
    return set(result.get("redline_exempt_files", []))
