#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Tests - Block Cache Migration
"""

import os
import shutil
import tempfile
from core.archives.block_cache import BlockCache

def test_block_cache_migration_and_clearing():
    # 1. 初始化临时测试缓存根目录
    temp_dir = tempfile.mkdtemp(prefix="test_plenipes_cache_")
    try:
        # 创建一个 0 级 (不分级) 的缓存对象
        cache_l0 = BlockCache(
            shadow_root=temp_dir,
            custom_cache_dir=temp_dir,
            shard_levels=0
        )
        
        # 写入几个测试段落缓存数据
        lang = "en"
        style = "technical"
        block_hash_1 = "abcdef1234567890"
        block_hash_2 = "987654fedcba0000"
        content_1 = "Hello, high-concurrency local LLM!"
        content_2 = "Zero latency engineering!"
        
        cache_l0.store_block(lang, block_hash_1, content_1, style)
        cache_l0.store_block(lang, block_hash_2, content_2, style)
        
        # 验证 0 级缓存路径是否符合预期：root/en/technical/hash.txt
        expected_path_1 = os.path.join(temp_dir, lang, style, f"{block_hash_1}.txt")
        expected_path_2 = os.path.join(temp_dir, lang, style, f"{block_hash_2}.txt")
        
        assert os.path.exists(expected_path_1)
        assert os.path.exists(expected_path_2)
        assert open(expected_path_1, "r", encoding="utf-8").read() == content_1
        assert open(expected_path_2, "r", encoding="utf-8").read() == content_2
        
        # 2. 物理迁移：从 0 级迁移至 2 级 (取前 4 位分流，如 ab/cd/)
        cache_l0.migrate_cache(
            old_dir=temp_dir,
            new_dir=temp_dir,
            old_levels=0,
            new_levels=2
        )
        
        # 验证 2 级缓存新物理路径是否符合预期：root/en/technical/ab/cd/hash.txt
        # block_hash_1 前 4 位是 ab/cd/ -> ab, cd
        # block_hash_2 前 4 位是 98/76/ -> 98, 76
        migrated_path_1 = os.path.join(temp_dir, lang, style, "ab", "cd", f"{block_hash_1}.txt")
        migrated_path_2 = os.path.join(temp_dir, lang, style, "98", "76", f"{block_hash_2}.txt")
        
        assert os.path.exists(migrated_path_1)
        assert os.path.exists(migrated_path_2)
        assert open(migrated_path_1, "r", encoding="utf-8").read() == content_1
        assert open(migrated_path_2, "r", encoding="utf-8").read() == content_2
        
        # 验证旧的路径已经不存在文件
        assert not os.path.exists(expected_path_1)
        assert not os.path.exists(expected_path_2)
        
        # 3. 验证 2 级缓存的正常读取
        cache_l2 = BlockCache(
            shadow_root=temp_dir,
            custom_cache_dir=temp_dir,
            shard_levels=2
        )
        assert cache_l2.get_block(lang, block_hash_1, style) == content_1
        assert cache_l2.get_block(lang, block_hash_2, style) == content_2
        
        # 4. 验证一键清空全量缓存
        success = cache_l2.clear_all_cache()
        assert success
        
        # 检查物理目录已空
        assert len(os.listdir(temp_dir)) == 0

    finally:
        # 清理临时文件系统空间
        shutil.rmtree(temp_dir, ignore_errors=True)
