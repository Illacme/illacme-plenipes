# -*- coding: utf-8 -*-
"""
⚙️ Illacme Diagnostics - Vault Detector (文库智感探测器)
职责：跨平台解析 Obsidian、Logseq、Typora、MarkText、Zettlr 物理配置与磁盘挂载卷，定位文稿库。
"""

import os
import platform
import json
import string
from typing import Dict, Any, List


def detect_vault_suggestions() -> List[Dict[str, Any]]:
    """
    🚀 [V88.5] 全域智感路径引擎：跨平台解析 Obsidian、Logseq、Typora、MarkText、Zettlr 物理配置与磁盘挂载卷，
    极速定位用户的真实文稿库，最大限度屏蔽手动输入成本。
    
    Returns:
        List[Dict]: 建议的物理路径列表，包含 name, path, icon, dialect, is_detected 属性。
    """
    suggestions = []
    seen_paths = set()
    home = os.path.expanduser("~")
    system = platform.system()  # Darwin / Windows / Linux
    appdata = os.environ.get("APPDATA", "")

    def add_suggestion(name: str, path: str, icon: str, dialect: str = "standard", priority: int = 50, is_detected: bool = True):
        if not path or not os.path.exists(path):
            return
        abs_p = os.path.abspath(path)
        if abs_p in seen_paths:
            return
        seen_paths.add(abs_p)
        suggestions.append({
            "name": name,
            "path": abs_p,
            "icon": icon,
            "dialect": dialect,
            "is_detected": is_detected,
            "priority": priority
        })

    # 1. 💎 Obsidian 动态配置感应 (支持 macOS / Linux / Windows)
    obsidian_cfgs = [
        os.path.join(home, "Library", "Application Support", "obsidian", "obsidian.json"),
        os.path.join(home, ".config", "obsidian", "obsidian.json"),
        os.path.join(appdata, "obsidian", "obsidian.json")
    ]
    for cfg in obsidian_cfgs:
        if cfg and os.path.exists(cfg):
            try:
                with open(cfg, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    vaults = data.get("vaults", {})
                    for v_info in vaults.values():
                        p = v_info.get("path")
                        if p and os.path.exists(p):
                            basename = os.path.basename(p) or p
                            prio = 100 if v_info.get("open") else 80
                            add_suggestion(f"Obsidian ({basename})", p, "💎", dialect="obsidian", priority=prio)
            except Exception:
                pass

    # 2. 🌿 Logseq 动态配置感应
    logseq_cfgs = [
        os.path.join(home, ".logseq", "preferences.json"),
        os.path.join(home, "Library", "Application Support", "Logseq", "preferences.json"),
        os.path.join(home, ".config", "Logseq", "preferences.json"),
        os.path.join(appdata, "Logseq", "preferences.json")
    ]
    for cfg in logseq_cfgs:
        if cfg and os.path.exists(cfg):
            try:
                with open(cfg, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    graphs = data.get("graphs", [])
                    if isinstance(graphs, list):
                        for g in graphs:
                            if isinstance(g, str) and os.path.exists(g):
                                add_suggestion(f"Logseq ({os.path.basename(g)})", g, "🌿", dialect="logseq", priority=75)
            except Exception:
                pass

    # 3. 📝 MarkText 动态配置感应
    marktext_cfgs = [
        os.path.join(home, "Library", "Application Support", "marktext", "config.json"),
        os.path.join(home, ".config", "marktext", "config.json"),
        os.path.join(appdata, "marktext", "config.json")
    ]
    for cfg in marktext_cfgs:
        if cfg and os.path.exists(cfg):
            try:
                with open(cfg, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    folders = data.get("openedFolders", []) or data.get("history", {}).get("folders", [])
                    for f_path in folders:
                        if os.path.exists(f_path):
                            add_suggestion(f"MarkText ({os.path.basename(f_path)})", f_path, "📝", dialect="standard", priority=70)
            except Exception:
                pass

    # 4. 🔬 Zettlr 动态配置感应
    zettlr_cfgs = [
        os.path.join(home, "Library", "Application Support", "Zettlr", "config.json"),
        os.path.join(home, ".config", "Zettlr", "config.json"),
        os.path.join(appdata, "Zettlr", "config.json")
    ]
    for cfg in zettlr_cfgs:
        if cfg and os.path.exists(cfg):
            try:
                with open(cfg, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    workspaces = data.get("openWorkspaces", [])
                    for w in workspaces:
                        if os.path.exists(w):
                            add_suggestion(f"Zettlr ({os.path.basename(w)})", w, "🔬", dialect="standard", priority=70)
            except Exception:
                pass

    # 5. ✍️ Typora 动态配置感应
    typora_cfgs = [
        os.path.join(home, "Library", "Application Support", "abnerworks.Typora", "typora-pref.json"),
        os.path.join(home, ".config", "Typora", "typora-pref.json"),
        os.path.join(appdata, "Typora", "history.json")
    ]
    for cfg in typora_cfgs:
        if cfg and os.path.exists(cfg):
            try:
                with open(cfg, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    recents = data.get("recentFolders", [])
                    for r in recents:
                        if os.path.exists(r):
                            add_suggestion(f"Typora ({os.path.basename(r)})", r, "✍️", dialect="typora", priority=65)
            except Exception:
                pass

    # 6. 🛰️ 挂载卷与磁盘根目录智能特征扫描
    mount_roots = []
    if system == "Darwin" and os.path.exists("/Volumes"):
        try:
            for vol in os.listdir("/Volumes"):
                v_path = os.path.join("/Volumes", vol)
                if os.path.isdir(v_path):
                    mount_roots.append(v_path)
        except Exception:
            pass
    elif system == "Windows":
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                mount_roots.append(drive)

    for m_root in mount_roots:
        try:
            for sub in os.listdir(m_root):
                candidate = os.path.join(m_root, sub)
                if os.path.isdir(candidate):
                    if os.path.exists(os.path.join(candidate, ".obsidian")):
                        add_suggestion(f"Obsidian ({sub})", candidate, "💎", dialect="obsidian", priority=90)
                    elif os.path.exists(os.path.join(candidate, ".logseq")):
                        add_suggestion(f"Logseq ({sub})", candidate, "🌿", dialect="logseq", priority=85)
        except Exception:
            pass

    # 7. 静态常用默认路径补全扫描
    search_targets = [
        (["Documents", "Obsidian Vault"], "Obsidian Vault", "💎", "obsidian", 60),
        (["Documents", "Obsidian"], "Obsidian", "💎", "obsidian", 60),
        (["Documents", "Logseq"], "Logseq", "🌿", "logseq", 55),
        (["Documents", "Zettlr"], "Zettlr", "🔬", "zettlr", 50),
        (["Documents", "VNote"], "VNote", "📓", "vnote", 50),
        (["Documents", "Typora"], "Typora", "✍️", "typora", 50),
        (["Documents", "Manuscripts"], "原稿库", "📚", "standard", 40),
        (["Desktop", "Manuscripts"], "桌面原稿", "📚", "standard", 40)
    ]

    for parts, name, icon, dialect, prio in search_targets:
        full_path = os.path.join(home, *parts)
        add_suggestion(name, full_path, icon, dialect=dialect, priority=prio, is_detected=False)

    # 8. 物理工作区相对路径扫描
    cwd = os.getcwd()
    candidates = [
        {"name": "默认原稿库", "rel": "manuscripts", "icon": "📦"},
        {"name": "知识文库", "rel": "vault", "icon": "🏛️"},
        {"name": "内容目录", "rel": "content", "icon": "📑"},
        {"name": "技术文档", "rel": "docs", "icon": "📚"}
    ]
    for cand in candidates:
        abs_path = os.path.join(cwd, cand["rel"])
        if os.path.isdir(abs_path):
            add_suggestion(cand["name"], abs_path, cand["icon"], priority=30, is_detected=False)

    # 9. 绝对兜底
    if not suggestions:
        add_suggestion("默认原稿库", os.path.join(cwd, "manuscripts"), "📦", priority=1, is_detected=False)

    # 按优先级降序整理并移除内部计算用的 priority 键
    suggestions.sort(key=lambda x: x.get("priority", 0), reverse=True)
    for s in suggestions:
        s.pop("priority", None)

    return suggestions
