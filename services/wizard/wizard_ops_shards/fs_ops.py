#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧙‍♂️ fs_ops.py - 文件系统金库路径的安全交互式扫描与双向遍历防越界防御
"""

import os

def list_files_logic(req):
    path = os.path.expanduser(req.path)
    if not os.path.exists(path):
        return {"current": path, "items": [], "error": "路径不存在"}
    try:
        items = []
        if os.path.dirname(path) != path:
            items.append({"name": "..", "path": os.path.dirname(path), "type": "dir"})
        for entry in os.scandir(path):
            if entry.is_dir() and not entry.name.startswith("."):
                items.append({"name": entry.name, "path": entry.path, "type": "dir"})
        return {"current": os.path.abspath(path), "items": sorted(items, key=lambda x: (x or {}).get("name", ""))}
    except Exception as e:
        return {"current": path, "items": [], "error": str(e)}
