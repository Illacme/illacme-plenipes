#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Persistence Engine (Disk I/O)
模块职责：处理底层物理落盘、orjson 二进制序列化与时光机自愈灾备。
不关心任何业务逻辑，只负责极速、安全的字典存取。
"""
import os
import time
import shutil
import glob
import logging
import threading
import orjson

logger = logging.getLogger("Illacme.plenipes")

class PersistenceEngine:
    def __init__(self, cache_path, backup_slots=5):
        self.cache_path = os.path.abspath(os.path.expanduser(cache_path))
        self.backup_slots = backup_slots
        self._io_lock = threading.Lock()

    def load_with_recovery(self):
        """底层的二进制读取动作，搭载时光机自愈降级引擎"""
        def _try_load_json(file_path):
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0: 
                return None
            try:
                with open(file_path, 'rb') as f:
                    data = orjson.loads(f.read())
                    if "documents" in data:
                        if "dir_index" not in data: 
                            data["dir_index"] = {}
                        return data
            except orjson.JSONDecodeError: 
                return None
            return None

        data = _try_load_json(self.cache_path)
        if data: 
            return data

        logger.warning("🚨 检测到主状态机账本损坏或为空！正在强行激活时光机灾备引擎...")
        backup_dir = os.path.join(os.path.dirname(self.cache_path), ".plenipes_backup")
        if os.path.exists(backup_dir):
            backups = sorted(glob.glob(os.path.join(backup_dir, "metadata_snapshot_*.json")), key=os.path.getmtime, reverse=True)
            for backup_file in backups:
                logger.info(f"   └── ⏳ 正在尝试挂载历史快照: {os.path.basename(backup_file)}")
                recovered_data = _try_load_json(backup_file)
                if recovered_data:
                    logger.info("   └── ✨ 已成功从历史快照中恢复全量元数据！")
                    try: 
                        shutil.copy2(backup_file, self.cache_path)
                    except Exception as e: 
                        logger.error(f"   └── ⚠️ 无法回写恢复主账本: {e}")
                    return recovered_data

        logger.error("🛑 未发现有效的历史灾备记录。引擎将开启全量重新测绘。")
        return {"documents": {}, "link_index": {}, "dir_index": {}}

    def atomic_flush(self, data_dict):
        """事务级落盘与环形快照备份"""
        json_bytes = orjson.dumps(data_dict, option=orjson.OPT_INDENT_2)
        with self._io_lock:
            try:
                base_dir = os.path.dirname(self.cache_path)
                os.makedirs(base_dir, exist_ok=True)
                
                # 时光机环形灾备写入
                if os.path.exists(self.cache_path) and os.path.getsize(self.cache_path) > 0:
                    backup_dir = os.path.join(base_dir, ".plenipes_backup")
                    os.makedirs(backup_dir, exist_ok=True)
                    slot = int(time.time()) % self.backup_slots 
                    shutil.copy2(self.cache_path, os.path.join(backup_dir, f"metadata_snapshot_{slot}.json"))

                # 原子级写盘
                tmp_file = self.cache_path + ".tmp"
                with open(tmp_file, 'wb') as f: 
                    f.write(json_bytes)
                os.replace(tmp_file, self.cache_path)
                return True
            except Exception as e:
                logger.error(f"🛑 存档失败: 引擎无法更新后台增量指纹库。报错: {e}")
                return False