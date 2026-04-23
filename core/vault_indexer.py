#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Vault Indexer
模块职责：物理笔记库扫描与索引构建。
"""

import os

class VaultIndexer:
    """🚀 [TDR-Iter-021] 索引器：负责建立文档与资产的物理映射矩阵"""
    
    @staticmethod
    def build_indexes(vault_path):
        """
        深度扫描笔记库，建立：
        1. md_index: { rel_path: abs_path }
        2. asset_index: { filename: [abs_path1, abs_path2] }
        """
        md_index = {}
        asset_index = {}
        
        if not vault_path or not os.path.exists(vault_path):
            return md_index, asset_index
            
        for root, dirs, files in os.walk(vault_path):
            # 屏蔽系统级隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'dist', 'build']]
            
            for f in files:
                if f.startswith('.'): continue
                
                abs_path = os.path.join(root, f)
                rel_path = os.path.relpath(abs_path, vault_path).replace('\\', '/')
                
                if f.lower().endswith(('.md', '.mdx')):
                    md_index[rel_path] = abs_path
                else:
                    # 资产索引支持同名文件碰撞（通过路径深度消歧）
                    if f not in asset_index:
                        asset_index[f] = []
                    asset_index[f].append(abs_path)
                    
        return md_index, asset_index
