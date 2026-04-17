#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - CLI Bootstrap & OS Shield
模块职责：系统级初始化前置屏障。
负责命令行解析、零配置 onboarding 自举、以及通过底层 Socket 劫持实现免疫 Kill -9 的单例进程锁。
"""

import os
import sys
import argparse
import socket
import shutil
import platform
import subprocess
import logging


logger = logging.getLogger("Illacme.plenipes")
_SINGLETON_SOCKET = None

def send_notification(title, message):
    """
    🚀 跨平台系统通知调度器
    支持：macOS (osascript), Linux (notify-send), Windows (PowerShell)
    """
    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            cmd = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", cmd], check=False)
        elif system == "Linux": # Linux
            subprocess.run(["notify-send", title, message], check=False)
        elif system == "Windows": # Windows
            cmd = f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('{message}', '{title}')"
            subprocess.run(["powershell", "-Command", cmd], check=False)
    except Exception as e:
        logger.debug(f"系统通知发送失败: {e}")

def acquire_singleton_lock(port=43210):
    """
    进程级单例防线 (OS-Level Singleton Mutex)
    基于配置文件动态分配防撞端口。
    """
    global _SINGLETON_SOCKET
    _SINGLETON_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        _SINGLETON_SOCKET.bind(('127.0.0.1', port))
    except socket.error:
        logger.error(f"\n🛑 [运行冲突] 启动失败：端口 {port} 已被占用，检测到系统已经在后台运行！")
        logger.error("   └── 💡 为了保护您的文章数据和电脑内存，本次重复启动已自动拦截。")
        logger.error("   └── 请检查是否开了多个终端窗口，或者在 config.yaml 中修改 singleton_port。")
        sys.exit(1)

def parse_args_and_lock():
    """解析命令行参数，执行配置文件自检，并激活防抖锁"""
    parser = argparse.ArgumentParser(description="Illacme-plenipes: 工业级 Markdown 到全量泛用型 SSG 映射同步中枢")
    parser.add_argument('--config', default='config.yaml', help="指定 YAML 配置文件路径 (默认: config.yaml)")
    parser.add_argument('--sync', action='store_true', help="发起单次全库阵列增量同步测绘")
    parser.add_argument('--watch', action='store_true', help="进入 Daemon 模式：启动系统看门狗守护进程，毫秒级监听源库变动")
    parser.add_argument('--dry-run', action='store_true', help="[安全演练模式] 阻断实际 API 扣费请求和物理写盘")
    parser.add_argument('--force', action='store_true', help="[强制重构模式] 强行撕碎 MD5 本地状态防抖指纹，强拉所有引擎模块执行覆盖重编")
    
    # 🚀 [V31.3 增强参数]
    parser.add_argument('--path', '-p', nargs='+', help="[选择性同步] 指定同步的源文件或目录路径 (相对于库根目录，支持多个)")
    parser.add_argument('--no-ai', action='store_true', help="[离线/节流模式] 禁用所有 AI 任务 (翻译/SEO/Slug)，仅执行本地排版加工")
    parser.add_argument('--port', type=int, help="[多开模式] 物理覆盖 singleton_port，允许同一份配置运行多个实例")
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help="[诊断模式] 手动覆盖配置文件的终端日志级别")
    parser.add_argument('--clean', action='store_true', help="[一键重置] 物理删除所有同步指纹与 AI 影子缓存，重置引擎到初始态")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.config):
        # 🚀 盲区一修复：零配置自启 (Zero-Config Onboarding)
        example_config = 'config.example.yaml'
        if os.path.exists(example_config):
            try:
                shutil.copy2(example_config, args.config)
                logger.info(f"✨ 欢迎使用！已为您自动生成默认配置文件 '{args.config}'。")
                logger.info(f"   └── 💡 请打开该文件，填入您的 API Key 或调整文件夹路径后，再次运行本程序。")
                sys.exit(0)
            except Exception as e:
                logger.error(f"🛑 自动生成配置文件失败: {e}")
                sys.exit(1)
        else:
            logger.error(f"🛑 启动终止: 未发现配置文件 '{args.config}'，且未找到范例文件 '{example_config}'。")
            sys.exit(1)

    # 在初始化主引擎和模型加载前，单独解析系统级参数以抢占端口锁
    try:
        from .config import load_config
        cfg = load_config(args.config)
        lock_port = args.port or cfg.system.singleton_port
        
        # 🚀 同步覆盖日志级别
        if args.log_level:
            logger.setLevel(getattr(logging, args.log_level))
            logger.info(f"⚙️ [内核诊断] 日志级别已由命令行覆盖为: {args.log_level}")
    except Exception as e:
        logger.debug(f"前置配置加载异常 (可能正在自举): {e}")
        lock_port = args.port or 43210
        
    acquire_singleton_lock(lock_port)
    return args