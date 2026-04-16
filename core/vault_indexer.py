#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Vault Indexer
模块职责：全域扫描雷达。
负责遍历本地 Markdown 知识库，提取所有文档与附件的绝对物理路径，构建倒排索引字典。
🚀 [V16.4 架构重构]：将底层文件系统 I/O 从主引擎中剥离。
"""

import os
import logging

logger = logging.getLogger("Illacme.plenipes")

class VaultIndexer:
    @staticmethod
    def build_indexes(vault_path):
        """
        🚀 静态扫描器：无状态执行全库遍历，返回装载完毕的双重索引
        """
        md_index = {}
        asset_index = {}
        
        for root, dirs, files in os.walk(vault_path):
            # 过滤掉以 . 开头的隐藏文件夹（如 .git, .obsidian, .illacme-shadow）
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in files:
                if f.startswith("."): 
                    continue 
                
                abs_path = os.path.join(root, f)
                
                if f.endswith((".md", ".mdx")):
                    md_index[f] = abs_path
                    # 额外挂载无后缀名的寻址键，方便短链映射
                    md_index[os.path.splitext(f)[0]] = abs_path
                else:
                    if f not in asset_index: 
                        asset_index[f] = []
                    asset_index[f].append(abs_path)
                    
        return md_index, asset_index