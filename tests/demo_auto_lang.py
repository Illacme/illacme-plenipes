#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import logging

# 将项目根目录加入路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config.config import load_config
from core.utils.language_hub import LanguageHub
from core.editorial.vault_indexer import VaultIndexer

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Illacme.plenipes")

def demo_auto_detection():
    print("🚀 [Demo] 启动源语种自动探测演示...")
    
    # 1. 加载配置
    config = load_config("config.yaml")
    vault_path = os.path.abspath(os.path.expanduser(config.vault_root))
    
    print(f"📂 正在扫描 Vault: {vault_path}")
    
    # 2. 构建索引
    md_index, _, _ = VaultIndexer.build_indexes(vault_path)
    
    # 3. 模拟探测逻辑
    first_doc = next(iter(md_index.keys()), None)
    if not first_doc:
        print("❌ Vault 中没有 Markdown 文件。")
        return

    print(f"📄 选取首个样本文件: {first_doc}")
    
    abs_path = os.path.join(vault_path, first_doc)
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            text = f.read(2000)
            detected = LanguageHub.detect_source_lang(text)
            print(f"✨ [识别结果]：{detected}")
            
            # 展示 LanguageHub 对该代码的物理路径映射
            physical = LanguageHub.get_physical_path(detected, "docusaurus")
            print(f"🎨 [Docusaurus 物理路径]：{physical}")
    except Exception as e:
        print(f"❌ 探测失败: {e}")

if __name__ == "__main__":
    demo_auto_detection()
