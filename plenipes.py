#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes (v35.2) - 全球私人出版社总入口
🛡️ [V35.2] 架构升级：实装主权空间路由、准入校验与自动化引导。
"""

import time
import signal
import os
import sys
import subprocess
from core.utils.tracing import tlog

def ensure_venv():
    """🚀 [V14.5] 智能环境重定向"""
    if os.environ.get('PLENIPES_SKIP_VENV') or '--no-venv' in sys.argv:
        return
    in_venv = (sys.prefix != sys.base_prefix) or hasattr(sys, 'real_prefix')
    if not in_venv:
        venv_path = os.path.join(os.getcwd(), '.venv')
        python_exe = os.path.join(venv_path, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(venv_path, 'bin', 'python')
        if os.path.exists(python_exe):
            os.environ['PLENIPES_SKIP_VENV'] = '1'
            if os.name == 'nt':
                sys.exit(subprocess.call([python_exe] + sys.argv))
            else:
                os.execv(python_exe, [python_exe] + sys.argv)

ensure_venv()

from core.utils import setup_logger
from core.runtime.cli_bootstrap import parse_args_and_lock, set_global_engine
from core.runtime.orchestrator import prepare_sync_tasks, execute_full_sync
from core.runtime.daemon import start_watchdog
from core.governance.territory_manager import wm

from core.governance.license_guard import LicenseGuard
from core.ui.handlers.status_handlers import StatusHandlers

# 全局句柄
logger = None
global_engine = None
global_observer = None

def graceful_shutdown(signum, frame):
    """拦截操作系统级的中断信号，执行防内存撕裂的终极快照固化"""
    if logger: logger.warning("\n⚠️ 收到停止指令！正在尝试安全保存数据并关闭工场...")
    if global_observer: global_observer.stop()
    if global_engine and hasattr(global_engine, 'meta'):
        try:
            global_engine.meta.force_save()
            if logger: logger.info("  └── 🏁 出版进度已 100% 安全存档。")
        except: pass
    os._exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

def probe_local_compute():
    """探测本机算力环境"""
    tlog.info("🔍 [环境探测] 正在扫描本机算力节点...")
    # 模拟探测逻辑 (后续实装端口扫描)
    nodes = []
    import socket
    def is_port_open(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex(('127.0.0.1', port)) == 0
            
    if is_port_open(11434): nodes.append("Ollama")
    if is_port_open(1234): nodes.append("LM Studio")
    
    if nodes:
        tlog.success(f"  └── ✅ 发现活跃算力节点: {', '.join(nodes)}")
    else:
        tlog.info("  └── ℹ️ 未发现本机活跃算力节点，建议配合云端 API 使用。")

if __name__ == "__main__":
    # 1. 视觉主权：Banner 置顶
    StatusHandlers.handle_banner("v35.2", "Sovereign-Hardening (主权加固版)", "Production-Ready Private Press (生产级私人出版社)")


    
    # 2. 准入审计
    LicenseGuard.verify_authority()
    
    # 3. 主权疆域初始化检查
    territories = wm.list_territories()
    if not territories:
        tlog.info("🛡️ [主权点火] (系统启动) 欢迎进入您的私人出版疆域！检测到尚未建立任何主权出版社。")

        from core.ui.wizard import run_onboarding_wizard
        # 如果技术可行，后续将在此处启动 Web Wizard
        if not run_onboarding_wizard():
            tlog.error("🛑 [引导中断] (配置失败) 出版社建立失败。")
            sys.exit(0)
        territories = wm.list_territories()

    # 4. 环境探测
    probe_local_compute()

    # logger = setup_logger()  # [V35.2] 推迟至引擎划定疆域后再初始化
    try:
        # 5. 解析参数
        args, config = parse_args_and_lock()
        
        # 🧪 [V35.2] 主权智能路由：如果缺省请求 default 且已存在唯一疆域，则自动对正
        if args.territory == "default":
            territories = wm.list_territories()
            if len(territories) == 1 and territories[0]['id'] != "default":
                tlog.info(f"🛰️ [智能路由] 检测到唯一疆域，已自动对正至: {territories[0]['id']}")
                args.territory = territories[0]['id']

        
        # 6. 实例化主引擎 (内部会自动划定疆域)
        from core.runtime.engine_factory import EngineFactory
        engine = EngineFactory.create_engine(config or args.config, args=args, territory_id=args.territory)
        
        # 🧪 [V35.2] 日志主权对正：在引擎划定疆域后，重定向日志管线
        logger = setup_logger(engine.paths["logs"])

        
        # 7. 激活当前活跃主权疆域
        wm.switch(args.territory)

        
        set_global_engine(engine)
        global_engine = engine


        # --- 后续任务执行逻辑 (Sync / Watch / Serve / Purge / Credentials) ---
        
        # 🧪 [V35.2] 资产净化特权指令
        if args.purge:
            engine.janitor.purge_dist()
            tlog.info("🏁 [净化完成] 疆域已恢复纯净状态。")
            if not any([args.sync, args.watch, args.serve]): sys.exit(0)


        # 🧪 [V35.2] 凭据审计特权指令
        if args.credentials:
            from core.governance.secret_manager import secrets
            tlog.info("🔍 [凭据审计] 正在执行全域脱敏扫描...")
            # 逻辑：触发一次配置重载并保存，自动执行 mask_dict
            engine.meta.force_save()
            tlog.info("🏁 [审计完成] 所有敏感凭据已受主权 Sentinel 保护。")
            if not any([args.sync, args.watch, args.serve]): sys.exit(0)

        task_queue, current_source_files = prepare_sync_tasks(engine, requested_paths=args.path)

        
        if args.sync or (not any([args.api, args.serve, args.watch])):
            execute_full_sync(engine, args, task_queue, current_source_files)
            
        if args.watch:
            tlog.info("🐕 [主权守护] (后台监控) 首席指挥官已进入全时监听模式...")
            global_observer, _ = start_watchdog(engine, args, current_source_files)


            while True: time.sleep(1)
        
        if not args.watch:
            tlog.info("🏁 [演习胜利] (出版完成) 出版任务已全量闭环，主权疆域归位。")
            sys.exit(0)



    except Exception as e:
        if logger: logger.error(f"🚨 [紧急停机] 致命异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
