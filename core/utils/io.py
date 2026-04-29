"""
📂 I/O 工具集 — 文件读写与路径操作的原子化工具函数。
提供安全的文件读写、目录遍历、临时文件管理与路径规范化。
"""
# -*- coding: utf-8 -*-
import os
import tempfile
import shutil

def atomic_write(path: str, content: str, mode: str = 'w', encoding: str = 'utf-8'):
    """🚀 [V5.0] 原子化物理写盘：通过临时文件交换确保数据完整性。"""
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(fd, mode, encoding=encoding) as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception as e:
        if os.path.exists(tmp_path): os.remove(tmp_path)
        raise e

def safe_makedirs(path: str):
    """安全创建目录层级"""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
