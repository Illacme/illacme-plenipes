#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - 混沌压测库生成器 (Config-Aware Chaos Generator)
核心升级：动态读取 config.yaml，确保物理产物与引擎配置路径 100% 对齐。
"""

import os
import sys
import random
import yaml

def generate_chaos_vault(num_files=1000):
    # 1. 自动定位项目根目录 (相对于 tests 文件夹向上跳一级)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    sys.path.append(project_root)
    
    # 2. 尝试引入并复用引擎自带的配置装载器，以保持路径推导的一致性
    try:
        from core.utils import load_unified_config
        config = load_unified_config(os.path.join(project_root, "config.yaml"))
        vault_root_raw = config.get('vault_root', './content-vault')
    except Exception:
        # 兜底逻辑：手动解析
        with open(os.path.join(project_root, "config.yaml"), 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            vault_root_raw = config.get('vault_root', './content-vault')

    # 3. 物理路径解析：处理相对路径（如 ../vault）并转换为绝对路径
    # 确保相对于项目根目录进行锚定
    if not os.path.isabs(vault_root_raw):
        abs_vault_root = os.path.abspath(os.path.join(project_root, vault_root_raw))
    else:
        abs_vault_root = vault_root_raw

    vault_dir = os.path.join(abs_vault_root, "ChaosTest")
    
    print(f"🌪️ 正在物理路径 '{vault_dir}' 构建混沌压测矩阵...")
    os.makedirs(vault_dir, exist_ok=True)
    
    # 建立深度目录树
    directories = [vault_dir]
    for i in range(10):
        sub_dir = os.path.join(vault_dir, f"Domain_{i}", f"SubDomain_{random.randint(1,5)}")
        os.makedirs(sub_dir, exist_ok=True)
        directories.append(sub_dir)

    file_names = [f"Chaos_Node_{i:04d}" for i in range(num_files)]
    
    # 模拟资产
    dummy_img_dir = os.path.join(vault_dir, "assets")
    os.makedirs(dummy_img_dir, exist_ok=True)
    # 写入一张真实的 1x1 像素有效 PNG 图片，真正激活 WebP 压缩引擎
    import base64
    b64_png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    with open(os.path.join(dummy_img_dir, "dummy_test_image.png"), "wb") as f:
        f.write(base64.b64decode(b64_png))
        
    for i, name in enumerate(file_names):
        target_dir = random.choice(directories)
        filepath = os.path.join(target_dir, f"{name}.md")
        links = random.sample(file_names, random.randint(5, 10))
        link_str = "\n".join([f"- [[{l}]]" for l in links])
        
        content = f"""---
title: {name}
ai_sync: true
draft: false
tags: [chaos, stress-test]
---
# {name}
这是一篇由混沌发生器自动生成的压测节点。
## 🕸️ 高频双链矩阵
{link_str}
## 🖼️ 并发资产争夺
![并发测试图](../assets/dummy_test_image.png)
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        if i % 200 == 0:
            print(f"   └── 已部署 {i} 个节点...")
            
    print(f"✨ 部署完毕！1000 篇笔记已送达：{vault_dir}")

# 启动终极压力测试命令：python tests/generate_chaos_vault.py
if __name__ == "__main__":
    generate_chaos_vault()