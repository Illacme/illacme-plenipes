#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# 将项目根目录加入路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.utils.language_hub import LanguageHub

def test_language_hub():
    print("🧪 [Test] LanguageHub 识别测试...")
    
    test_cases = [
        ("简体中文", "zh-Hans"),
        ("Traditional Chinese", "zh-Hant"),
        ("English", "en"),
        ("Japanese", "ja"),
        ("日语", "ja"),
        ("法语", "fr"),
        ("zh-cn", "zh-Hans"),
    ]
    
    for name, expected in test_cases:
        actual = LanguageHub.resolve_to_iso(name)
        status = "✅" if actual == expected else "❌"
        print(f"  {status} {name:20} -> {actual} (Expected: {expected})")

def test_theme_awareness():
    print("\n🧪 [Test] 主题感知路径对齐测试...")
    
    iso_code = "zh-Hans"
    
    # Docusaurus 偏好
    path_doc = LanguageHub.get_physical_path(iso_code, "docusaurus")
    print(f"  Docusaurus: {iso_code} -> {path_doc} (Expected: zh-Hans)")
    
    # Starlight 偏好
    path_star = LanguageHub.get_physical_path(iso_code, "starlight")
    print(f"  Starlight:  {iso_code} -> {path_star} (Expected: zh-cn)")

if __name__ == "__main__":
    test_language_hub()
    test_theme_awareness()
