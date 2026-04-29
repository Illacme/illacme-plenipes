#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes V12.0 - Sovereignty & MDX Full-Flow Validator
全流程验证脚本：覆盖从“入站扫描”到“AI 屏蔽”再到“物理落盘”的全主权链路。
"""
import os
import sys
import shutil
import subprocess

# 🚀 路径自愈
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

TEST_VAULT = os.path.join(BASE_DIR, "content-vault/V12_Test")
OUTPUT_BASE = os.path.join(BASE_DIR, "themes/default/src/content/docs")

def setup_test_files():
    print("🛠️  [1/4] 正在构造全后缀测试矩阵...")
    if os.path.exists(TEST_VAULT): shutil.rmtree(TEST_VAULT)
    os.makedirs(TEST_VAULT, exist_ok=True)

    # 1. 标准 MD
    with open(os.path.join(TEST_VAULT, "std.md"), "w") as f:
        f.write("---\ntitle: Std MD\n---\nNormal content.")
    
    # 2. 传统后缀
    with open(os.path.join(TEST_VAULT, "legacy.markdown"), "w") as f:
        f.write("---\ntitle: Legacy MD\n---\nLegacy content.")

    # 3. 严谨 MDX (包含 JSX)
    with open(os.path.join(TEST_VAULT, "advanced.mdx"), "w") as f:
        f.write("""---
title: Advanced MDX
---
import { Comp } from './Comp';

<Hero title="Welcome">
  AI should translate this text inside JSX.
</Hero>

<SelfClosingTag variant="dark" />

<UnrecognizedTag>
  Nested content should be safe.
</UnrecognizedTag>
""")

def run_sync():
    print("🚀 [2/4] 启动物理火力执行同步...")
    # 我们通过命令行运行以确保全量加载配置
    cmd = [sys.executable, "plenipes.py", "--sync", "--path", "V12_Test", "--force"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 同步失败: {result.stderr}")
        return False
    return True

def verify_results():
    print("🔍 [3/4] 执行物理资产全息审计...")
    
    # 检查后缀基因是否保全
    expected_files = [
        "std-md.md",
        "legacy-md.markdown",
        "advanced-mdx.mdx"
    ]
    
    # 默认语言 (zh) 根目录检查
    v12_out_dir = os.path.join(OUTPUT_BASE, "v12-test")
    
    for f_name in expected_files:
        path = os.path.join(v12_out_dir, f_name)
        if os.path.exists(path):
            print(f"  ✅ 后缀保全成功: {f_name}")
        else:
            print(f"  ❌ 缺失资产: {f_name} (期待路径: {path})")
            return False

    # 检查 MDX 内容主权
    mdx_path = os.path.join(v12_out_dir, "advanced-mdx.mdx")
    with open(mdx_path, "r") as f:
        content = f.read()
        
    checks = {
        "JSX 开标签保护": '<Hero title="Welcome">',
        "JSX 闭标签保护": '</Hero>',
        "自闭合标签保护": '<SelfClosingTag variant="dark" />',
        "语义内容保留": 'AI should translate this text inside JSX.'
    }
    
    for label, snippet in checks.items():
        if snippet in content:
            print(f"  ✅ {label}: 通过")
        else:
            print(f"  ❌ {label}: 失败！内容被破坏。")
            return False

    return True

def main():
    print("==========================================")
    print("Illacme-plenipes V12.0 全流程主权验证引擎")
    print("==========================================")
    
    try:
        setup_test_files()
        if run_sync():
            if verify_results():
                print("\n✨ [4/4] 验证通过！V12.0 全流程链路已严丝合缝。")
            else:
                print("\n🚨 验证未通过：物理审计发现缺陷。")
        else:
            print("\n🚨 验证未通过：引擎同步过程崩溃。")
    finally:
        # 清理测试目录 (可选)
        # shutil.rmtree(TEST_VAULT)
        pass

if __name__ == "__main__":
    main()
