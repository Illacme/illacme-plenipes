#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes (v14.7) - 工业级架构双向解耦版 (CLI Entry)
模块职责：本地运行的命令行入口客户端。
🚀 [V14.5] 核心功能：智能环境重定向 (Smart Bootstrapping) 与 算力拓扑自动化。
"""

import time
import signal
import os
import sys
import shutil
import subprocess
from core.utils.tracing import tlog

def ensure_venv():
    """🚀 [V14.5] 智能环境重定向 (Smart Bootstrapping)"""
    if os.environ.get('PLENIPES_SKIP_VENV') or '--no-venv' in sys.argv:
        return
    in_venv = (sys.prefix != sys.base_prefix) or hasattr(sys, 'real_prefix')
    if not in_venv:
        venv_path = os.path.join(os.getcwd(), '.venv')
        if os.name == 'nt':
            python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
        else:
            python_exe = os.path.join(venv_path, 'bin', 'python')
            
        if os.path.exists(python_exe):
            os.environ['PLENIPES_SKIP_VENV'] = '1'
            if os.name == 'nt':
                sys.exit(subprocess.call([python_exe] + sys.argv))
            else:
                os.execv(python_exe, [python_exe] + sys.argv)

# 优先执行环境自愈
ensure_venv()

from core.utils import setup_logger
from core.runtime.cli_bootstrap import parse_args_and_lock, set_global_engine
from core.runtime.orchestrator import prepare_sync_tasks, execute_full_sync
from core.runtime.daemon import start_watchdog

# 全局句柄
logger = None
global_engine = None
global_observer = None
global_watch_pool = None
global_dev_server = None

def graceful_shutdown(signum, frame):
    """拦截操作系统级的中断信号，执行防内存撕裂的终极快照固化"""
    if logger:
        logger.warning("\n⚠️ 收到停止指令！正在尝试安全保存数据并关闭工场...")
    
    if global_observer:
        global_observer.stop()
        if logger: logger.info("  └── [1/4] 原稿自动监控已关闭。")
        
    if global_watch_pool:
        global_watch_pool.shutdown(wait=False)
        if logger: logger.info("  └── [2/4] 正在中断尚未开始的出版排队任务。")

    if global_dev_server:
        if logger: logger.info("  └── [3/4] 正在切断全球书店预览连接。")
        
    if global_engine and hasattr(global_engine, 'meta'):
        try:
            global_engine.meta.force_save()
            if logger: logger.info("  └── [4/4] 出版进度已 100% 安全存档至注册簿。")
        except Exception as e:
            if logger: logger.error(f"  └── ⚠️ 注册簿存档发生异常: {e}")
            
    if logger: logger.info("🛑 物理主进程已切断，工场下线！")
    os._exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

if __name__ == "__main__":
    # 🚀 [V34.9] 视觉主权：Banner 绝对置顶
    from core.ui.terminal import TerminalUI
    TerminalUI.register_listeners()
    
    # 🛡️ [V25.0] 出版准入校验
    from core.governance.license_guard import LicenseGuard
    LicenseGuard.verify_authority()

    tlog.info("🚀 [总编室] 正在唤醒出版流水线并点火编辑部算力...")

    logger = setup_logger()
    try:
        # 1. 解析参数并锁定单例端口
        args, config = parse_args_and_lock()
        
        # 🚀 [V19.0] 零门槛点火：首次运行引导程序
        if not os.path.exists(args.config):
            from core.utils.terminal_wizard import run_onboarding_wizard
            config_data = run_onboarding_wizard(args.config)
            if not config_data:
                sys.exit(0)
            from core.config.config import load_config
            config = load_config(args.config)
        
        # 🚀 [V31.2] 档案库重置
        if args.clean:
            logger.info("🧹 [工场维护] 正在响应 --clean 指令，发起全量档案重置...")
            from core.config.config import load_config
            tmp_cfg = load_config(args.config)
            theme = tmp_cfg.active_theme
            db_root = tmp_cfg.metadata_db
            theme_db_path = db_root.replace("{theme}", theme)
            db_path = os.path.abspath(os.path.expanduser(theme_db_path))
            
            if not os.path.splitext(db_path)[1]:
                potential_db = os.path.join(db_path, f"ledger_{theme}.db")
                if os.path.exists(potential_db):
                    os.remove(potential_db)
                    logger.info(f"   └── ✨ 已清除当前主题注册簿: {os.path.basename(potential_db)}")
                main_db = os.path.join(db_path, "metadata.db")
                if os.path.exists(main_db):
                    os.remove(main_db)
                    logger.info(f"   └── ✨ 已清除默认全局注册簿: {os.path.basename(main_db)}")
            else:
                target_db = db_path.replace(".json", ".db")
                if not target_db.endswith(".db"): target_db += ".db"
                if os.path.exists(target_db):
                    os.remove(target_db)
                    logger.info(f"   └── ✨ 已清除主题关联注册簿: {os.path.basename(target_db)}")

            cache_dir = os.path.join(tmp_cfg.system.data_root, "cache")
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
                logger.info(f"   └── ✨ 已粉碎 AI 影子库目录: {cache_dir}")

            dist_dir = f"themes/{theme}/dist"
            if os.path.exists(dist_dir):
                shutil.rmtree(dist_dir)
                logger.info(f"   └── ✨ 已清除『全球书店』分发目录: {dist_dir}")

            logger.info("✨ 工场已成功回归初始态！所有指纹与记忆已抹除。")

        # 3. 实例化主引擎
        from core.runtime.engine_factory import EngineFactory
        engine = EngineFactory.create_engine(config or args.config, no_ai=args.no_ai, args=args, workspace_id=args.workspace)
        set_global_engine(engine)
        global_engine = engine

        # 📊 [V7.0] 商业审计报告
        if args.audit_report:
            tlog.info(f"📊 [审计] 正在生成侧翼馆室 '{args.workspace}' 的合规审计报告...")
            report = engine.ledger.export_report(workspace_id=args.workspace)
            if not report:
                tlog.warning("⚠️ [审计] 未发现任何审计记录。")
            else:
                import json
                print(json.dumps(report, indent=2, ensure_ascii=False))
            sys.exit(0)

        # 🩺 [V34.8] 全域诊断模式
        if args.doctor:
            logger.info("🩺 [诊断中心] 正在执行全量出版体检...")
            report = engine.doctor.run_full_check()
            if args.heal:
                logger.info("💊 [自愈手术] 正在根据诊断报告执行物理修复...")
                engine.doctor.heal()
            sys.exit(0 if report["status"] != "FAIL" else 1)

        # 🛡️ [V24.6] 哨兵主动审计
        if args.sentinel:
            engine.sentinel.run_health_check()
            sys.exit(0)

        # 🚀 [V11.0] 差异审计
        if args.audit:
            engine.auditor.run_diff_audit()
            sys.exit(0)

        # 🚀 [V11.0] 样稿转正
        if args.promote:
            engine.auditor.promote_to_production()
            sys.exit(0)

        # 🚀 [V11.0] 进化报告 (Brain)
        if args.brain:
            summary = engine.brain.get_summary()
            tlog.info("🧠 [编辑部进化简报]")
            print(f"  └── 故障拦截总数: {summary.get('total_lessons', 0)}")
            print(f"  └── 涉及治理维度: {', '.join(summary.get('categories', []))}")
            print(f"  └── 最近拦截记录: {summary.get('recent_failures', [])[-3:]}")
            sys.exit(0)

        # 🚀 [V13.0] 流水线清单
        if args.list_plugins:
            tlog.info("📡 [流水线中心] 当前已装配的出版工序:")
            for i, step in enumerate(engine.pipeline.steps):
                print(f"  {i+1}. {step.__class__.__name__}")
            sys.exit(0)

        # 🔌 [V14.1] API 总编室服务
        if args.api:
            from core.api.server import start_api_server
            api_host = engine.config.system.api_host
            api_blocking = not (args.watch or args.sync or args.path or args.serve)
            if not api_blocking:
                logger.info(f"🔌 [总编室] 正在后台启动 API 服务: http://{api_host}:{args.api_port}")
            else:
                logger.info(f"🔌 [总编室] 正在启动 API 服务 (阻塞模式): http://{api_host}:{args.api_port}")
            start_api_server(host=api_host, port=args.api_port, blocking=api_blocking)
            if api_blocking: sys.exit(0)

        # 🌐 [V11.7] 本地样张预览服务器
        if args.serve:
            from core.utils.dev_server import DevServer
            dist_dir = os.path.join(os.getcwd(), "themes", engine.config.active_theme, "dist")
            serve_host = engine.config.system.serve_host
            dev_server = DevServer(directory=dist_dir, host=serve_host, port=args.serve_port)
            global_dev_server = dev_server
            serve_blocking = not (args.watch or args.sync or args.path)
            if not serve_blocking:
                logger.info(f"🌐 [样张预览] 正在后台启动全球书店容器: http://{serve_host}:{args.serve_port}")
            else:
                logger.info(f"🌐 [样张预览] 正在启动全球书店容器 (阻塞模式): http://{serve_host}:{args.serve_port}")
            dev_server.start(blocking=serve_blocking)
            if serve_blocking: sys.exit(0)

        # 4. 构建出版任务队列
        task_queue, current_source_files = prepare_sync_tasks(engine, requested_paths=args.path)
        any_mode_active = any([args.api, args.serve, args.watch, args.doctor, args.clean, args.sentinel, args.list_plugins])
        is_vault_empty = not engine.meta.get_documents_snapshot()
        should_default_sync = (not any_mode_active) or is_vault_empty
        
        if args.sync or should_default_sync:
            execute_full_sync(engine, args, task_queue, current_source_files)
            
        # 5. 启动看门狗守护
        if args.watch:
            logger.info("🐕 [监控] 首席校对已进入守护模式，正在监听原稿变动...")
            engine.meta.is_watch_mode = True
            global_observer, global_watch_pool = start_watchdog(engine, args, current_source_files)
            while True:
                time.sleep(1)
        
        if not args.watch:
            tlog.info("🏁 出版任务已全部完成，工场安全熄火...")
            from core.logic.orchestration.task_orchestrator import harvest_all_executors
            harvest_all_executors()
            sys.exit(0)

    except Exception as e:
        if logger:
            logger.error(f"🚨 [紧急停机] 捕捉到致命异常: {e}")
        else:
            print(f"PUBLISHING ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
