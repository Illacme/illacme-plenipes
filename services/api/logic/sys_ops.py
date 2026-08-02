# -*- coding: utf-8 -*-
"""
⚙️ Illacme API Logic - System Operations (系统运维异步逻辑)
职责：承载主题安装、升级、回滚及版图向导生命周期管理。
🛡️ [V65.0]：实现物理管线同步，确保 subprocess 日志实时穿透至总线。
"""

import os
import shutil
import subprocess
import time
import re
from typing import Any, List, Dict
from core.utils.tracing import tlog
from core.utils.event_bus import bus

def run_theme_install(engine: Any, theme_dir: str):
    """🚀 [V52.11] 物理安装：执行 npm install 并通过总线同步日志"""
    tlog.info(f"🏗️ [安装启动] 正在为主题 '{engine.active_theme}' 安装依赖...")
    bus.emit("UI_TERMINAL_DATA", type="INSTALL_START", message=f"开始安装主题 {engine.active_theme} 的依赖...")
    
    try:
        cmd = ["npm", "install"]
        if os.path.exists(os.path.join(theme_dir, "pnpm-lock.yaml")):
            cmd = ["pnpm", "install"]
        elif os.path.exists(os.path.join(theme_dir, "yarn.lock")):
            cmd = ["yarn", "install"]
            
        process = subprocess.Popen(
            cmd,
            cwd=theme_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            line = process.stdout.readline()
            if not line: break
            clean_line = line.strip()
            if clean_line:
                bus.emit("UI_TERMINAL_DATA", type="LOG", data=clean_line)
        
        process.wait()
        if process.returncode == 0:
            tlog.success(f"✅ [安装成功] 主题 '{engine.active_theme}' 依赖已就绪。")
            bus.emit("UI_TERMINAL_DATA", type="INSTALL_SUCCESS", message="依赖安装完成！")
        else:
            tlog.error(f"❌ [安装失败] npm install 退出码: {process.returncode}")
            bus.emit("UI_TERMINAL_DATA", type="INSTALL_ERROR", message=f"安装失败，退出码: {process.returncode}")
            
    except Exception as e:
        tlog.error(f"🚨 [安装异常] {str(e)}")
        bus.emit("UI_TERMINAL_DATA", type="INSTALL_ERROR", message=f"系统异常: {str(e)}")

def run_theme_upgrade(engine: Any, theme_dir: str):
    """🚀 [V65.0] 物理升级：执行 npx @astrojs/upgrade 并管理物理快照"""
    tlog.info(f"🔄 [升级启动] 正在为主题 '{engine.active_theme}' 执行版本更新...")
    
    # 🛡️ [V65.3] 物理快照备份
    try:
        for f in ["package.json", "package-lock.json", "astro.config.mjs", "docusaurus.config.js"]:
            fpath = os.path.join(theme_dir, f)
            if os.path.exists(fpath):
                shutil.copy2(fpath, fpath + ".bak")
        bus.emit("UI_TERMINAL_DATA", type="LOG", data="🛡️ [物理保护] 已完成核心配置文件快照备份 (.bak)。")
    except Exception as e:
        bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"⚠️ [系统提示] 快照备份失败，但仍将尝试继续升级: {str(e)}")

    # 框架感知
    is_astro = os.path.exists(os.path.join(theme_dir, "astro.config.mjs")) or os.path.exists(os.path.join(theme_dir, "astro.config.js"))
    is_docusaurus = os.path.exists(os.path.join(theme_dir, "docusaurus.config.js"))
    
    cmd = ["npm", "update"]
    msg = "检测到通用 Node.js 环境，正在下达全局依赖更新指令..."
    
    if is_astro:
        cmd = ["npx", "-y", "@astrojs/upgrade", "-y"]
        msg = "正在向 Astro 引擎下达物理升级指令 (@astrojs/upgrade)..."
    elif is_docusaurus:
        msg = "正在向 Docusaurus 引擎下达物理升级指令 (npm update)..."

    bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"🚀 [系统感知] {msg}")
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=theme_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        while True:
            line = process.stdout.readline()
            if not line: break
            clean_line = line.strip()
            if clean_line:
                bus.emit("UI_TERMINAL_DATA", type="LOG", data=clean_line)
        
        process.wait()
        if process.returncode == 0:
            tlog.success(f"✅ [升级成功] 主题 '{engine.active_theme}' 已完成版本对正。")
            bus.emit("UI_TERMINAL_DATA", type="LOG", data="✅ [指令闭环] 主题版本升级完成！建议重启预览服务。")
        else:
            bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"❌ [升级失败] 退出码: {process.returncode}")
            
    except Exception as e:
        tlog.error(f"🚨 [升级异常] {str(e)}")
        bus.emit("UI_TERMINAL_DATA", type="LOG", data=f"🚨 [物理冲突] 升级异常: {str(e)}")

def rollback_config(engine: Any, theme_dir: str) -> List[str]:
    """物理快照回滚逻辑"""
    restored = []
    for f in ["package.json", "package-lock.json", "astro.config.mjs", "docusaurus.config.js"]:
        bak_path = os.path.join(theme_dir, f + ".bak")
        target_path = os.path.join(theme_dir, f)
        if os.path.exists(bak_path):
            shutil.copy2(bak_path, target_path)
    return restored

def run_precheck_logic(engine: Any) -> Dict[str, Any]:
    """🚀 [V78.5] 毫秒级双段式预检逻辑：执行快速静态审计以供 UI 拦截"""
    from core.config.models.governance import PublishingMode
    gov = getattr(engine.config, 'governance', None)
    publishing_mode = getattr(gov, 'publishing_mode', PublishingMode.BASIC) if gov else PublishingMode.BASIC
    mode_str = publishing_mode.value if hasattr(publishing_mode, 'value') else str(publishing_mode)

    has_synced = False
    if engine and hasattr(engine, 'meta'):
        try:
            ledger = engine.meta.get_active_ledger() if hasattr(engine.meta, 'get_active_ledger') else None
            has_synced = bool(ledger)
        except Exception:
            has_synced = False

    result = {
        "critical_errors": [],
        "warnings": [],
        "publishing_mode": mode_str,
        "has_synced": has_synced
    }
    
    if not engine:
        result["critical_errors"].append("物理底层 Engine 实例未就绪。")
        return result

    # 1. 强阻断维度 (Critical): 主题包环境验证
    from core.config.config import THEMES_DIR
    theme_dir = os.path.join(engine.paths.get(THEMES_DIR, THEMES_DIR), engine.active_theme)
    vault_assets_root = os.path.join(engine.vault_root, "assets") if engine.vault_root else ""
    
    if not os.path.exists(theme_dir):
        result["critical_errors"].append(f"主题环境丢失：未找到激活的主题 '{engine.active_theme}' 对应的物理目录。")
    elif engine.active_theme not in ['default'] and not os.path.exists(os.path.join(theme_dir, "package.json")):
        result["critical_errors"].append(f"核心清单丢失：在主题 '{engine.active_theme}' 下未找到 package.json 文件。")

    # 2. 从本地 SQLite 数据库中提取所有已解析资产并执行存在性审计 (Physical Existence)
    try:
        # 宽容模式：如果 SQLite 尚未建表或不存在，安全退化
        if hasattr(engine, 'meta') and hasattr(engine.meta, 'sqlite'):
            docs_res = engine.meta.sqlite.list_documents_paginated(1, 10000)
            docs = docs_res.get("data", []) if isinstance(docs_res, dict) else docs_res
            
            for doc in docs:
                assets = doc.get("assets", [])
                rel_path = doc.get("rel_path") or doc.get("id") or "Unknown"
                for asset in assets:
                    # 跳过外部链接
                    if str(asset).startswith(('http://', 'https://', '//')): continue
                    
                    normalized_asset = os.path.normpath(asset)
                    abs_asset = os.path.join(vault_assets_root, normalized_asset)
                    
                    if not os.path.exists(abs_asset):
                        result["warnings"].append({
                            "doc_id": rel_path,
                            "asset": asset,
                            "reason": "物理资产文件已丢失"
                        })
    except Exception as e:
        tlog.error(f"🚨 [预检异常] 提取物理资产清单时发生抖动: {e}")
        # 宽容模式：资产审计崩溃时不阻断流程
        
    # 3. 深度补偿维度: 扫描近期变动但尚未入库的脏文件 (Dirty Files)
    try:
        vault_root = engine.vault_root
        if vault_root and os.path.exists(vault_root):
            asset_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
            img_pattern = re.compile(r'<img[^>]+src="([^">]+)"')
            
            tlog.info(f"🔎 [预检嗅探] 正在启动脏文件深度扫描... (vault_root: {vault_root})")
            scanned_files = 0
            found_missing_count = 0
            
            for root, dirs, files in os.walk(vault_root):
                # 剪枝：过滤隐藏目录和常见无关目录，防止将缓存文件判定为脏文件
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ["node_modules", "dist", "build", "themes", ".venv"]]
                for f in files:
                    if f.endswith(('.md', '.mdx')):
                        file_path = os.path.join(root, f)
                        # 为了性能，仅深度扫描最近 2 小时内被修改过的文件
                        if os.path.getmtime(file_path) > time.time() - 7200:
                            scanned_files += 1
                            rel_path = os.path.relpath(file_path, vault_root)
                            with open(file_path, 'r', encoding='utf-8') as mf:
                                content = mf.read()
                                # 提取图片链接
                                found_assets = asset_pattern.findall(content) + img_pattern.findall(content)
                                if found_assets:
                                    tlog.info(f"🔎 [预检嗅探] 在 '{rel_path}' 提取到潜在资产: {found_assets}")
                                for asset in found_assets:
                                    if asset.startswith(('http://', 'https://', '//', 'data:', '#', '{')): continue
                                    # 剥离可能存在的 title 属性，例如: path/to/img.png "title"
                                    clean_asset = asset.split(' ')[0].strip().strip('\'"')
                                    if not clean_asset: continue
                                    
                                    normalized_asset = os.path.normpath(clean_asset)
                                    
                                    # 尝试 3 种可能的物理路径解析方式：
                                    # 1. 如果路径中自带了 assets/ (比如相对于库根目录)
                                    path_from_vault = os.path.join(engine.vault_root, normalized_asset.lstrip('/\\'))
                                    # 2. 如果是纯文件名或相对 assets 根的路径
                                    path_from_assets = os.path.join(vault_assets_root, normalized_asset)
                                    # 3. 如果是相对于当前 Markdown 文件的路径
                                    path_from_doc = os.path.join(os.path.dirname(file_path), normalized_asset)
                                    
                                    if not (os.path.exists(path_from_vault) or os.path.exists(path_from_assets) or os.path.exists(path_from_doc)):
                                        found_missing_count += 1
                                        tlog.warning(f"🚨 [预检拦截] 命中丢失资产: {clean_asset} (Abs: {path_from_vault} / {path_from_assets} / {path_from_doc})")
                                        # 避免与 SQLite 查出的历史记录重复警告
                                        is_duplicate = any(w.get("asset") == clean_asset and (w.get("doc_id") == rel_path or w.get("doc_id").endswith(rel_path)) for w in result["warnings"])
                                        if not is_duplicate:
                                            result["warnings"].append({
                                                "doc_id": f"*{rel_path}",
                                                "asset": clean_asset,
                                                "reason": "物理资产文件已丢失 (未同步的本地改动)"
                                            })
                                            
            tlog.info(f"🔎 [预检嗅探] 脏文件扫描完成！受检变动文件数: {scanned_files}, 新增拦截项: {found_missing_count}")
    except Exception as e:
        tlog.error(f"🚨 [预检异常] 深度扫描脏文件时发生抖动: {e}")
    
    return result
