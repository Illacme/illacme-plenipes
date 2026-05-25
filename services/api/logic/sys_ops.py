# -*- coding: utf-8 -*-
"""
⚙️ Illacme API Logic - System Operations (系统运维异步逻辑)
职责：承载主题安装、升级、回滚及版图向导生命周期管理。
🛡️ [V65.0]：实现物理管线同步，确保 subprocess 日志实时穿透至总线。
"""

import os
import shutil
import subprocess
from typing import Any, List
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
            restored.append(f)
    return restored
