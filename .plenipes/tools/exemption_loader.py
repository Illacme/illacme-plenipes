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
        import yaml
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        entries = data.get("redline_exempt_files", []) if data else []
        return set(entries)
    except Exception as e:
        print(f"  ⚠️  [豁免加载器] YAML 解析失败: {e}，豁免白名单降级为空集合。")
        return set()
