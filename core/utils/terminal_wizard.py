#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Terminal Wizard
负责首次启动时的交互式主权引导。
"""

import os
import yaml
from core.utils.tracing import tlog

def run_onboarding_wizard(config_path: str):
    """🚀 [V19.0] 交互式主权引导程序"""
    print("🏛️  欢迎来到 Illacme Plenipes：全球私人出版社")
    print("     ── 您的主权化全球出版发行中心")
    print("="*60 + "\n")
    print("检测到这是你首次点火。请跟随引导完成基础导航配置：\n")

    try:
        # 1. 基础信息
        vault_path = input("📂 请输入你的内容库 (Vault) 物理路径 [默认: ./content-vault]: ").strip() or "./content-vault"
        if not os.path.exists(vault_path):
            os.makedirs(vault_path, exist_ok=True)
            print(f"   └── ✨ 已为你创建内容库目录: {vault_path}")

        # 2. 算力引擎
        print("\n🤖 选择你的算力引擎 (LLM Provider):")
        print("   1) Mistral AI (推荐，平衡性极佳)")
        print("   2) OpenAI (性能巅峰)")
        choice = input("请输入编号 [默认: 1]: ").strip() or "1"
        
        provider = "mistral" if choice == "1" else "openai"
        api_key = input(f"🔑 请输入你的 {provider.upper()} API KEY: ").strip()
        
        # 3. 构造基础配置
        config_data = {
            "version": "18.0",
            "active_theme": "dark-theme",
            "metadata_db": "storage/ledger/main_ledger.db",
            "paths": {
                "vault": vault_path,
                "shadow": "storage/shadow",
                "storage": "storage"
            },
            "ai": {
                "provider": provider,
                "api_key": api_key,
                "model": "mistral-large-latest" if provider == "mistral" else "gpt-4-turbo"
            },
            "system": {
                "api_token": "omni-secret-token",
                "api_port": 43211,
                "serve_port": 43212
            }
        }

        # 确保存储目录存在
        os.makedirs("storage/ledger", exist_ok=True)
        os.makedirs("storage/index", exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)

        print("\n" + "-"*60)
        print("✨ 点火成功！配置文件已固化至: " + config_path)
        print("🚀 正在加载算力矩阵，准备进入全真同步流程...")
        print("-"*60 + "\n")
        
        return config_data

    except KeyboardInterrupt:
        print("\n\n🛑 点火已中断。你可以随时重新运行 plenipes.py 开启引导。")
        return None
    except Exception as e:
        print(f"\n❌ 引导程序发生意外错误: {e}")
        return None
