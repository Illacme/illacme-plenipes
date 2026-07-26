#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes (v50.3) - 全球私人出版社总入口
🛡️ [V50.3] 架构升级：实装主权 Imprint 路由、准入校验与自动化引导。
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
from core.runtime.cli_bootstrap import parse_args_and_lock, set_global_engine, set_global_args, set_global_observer
from core.runtime.orchestrator import prepare_sync_tasks, execute_full_sync
from core.runtime.daemon import start_watchdog
from core.governance.imprint_manager import im

from core.governance.license_guard import LicenseGuard
from core.ui.handlers.status_handlers import StatusHandlers

# 全局句柄
logger = None
global_engine = None
global_observer = None
should_exit = False

def graceful_shutdown(signum, frame):
    """拦截信号并防死锁优雅退出"""
    global should_exit
    if should_exit or not getattr(sys, '_plenipes_in_loop', False):
        os._exit(0)
    should_exit = True

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

def probe_local_compute():
    """探测本机算力环境"""
    print("🔍 [环境探测] 正在扫描本机算力节点...")
    from core.logic.diagnostics import DiagnosticsService
    nodes = DiagnosticsService.probe_local_compute()
    if nodes:
        print(f"  └── ✅ 发现活跃算力节点: {', '.join([n['name'] for n in nodes])}")
    else:
        print("  └── ℹ️ 未发现本机活跃算力节点，建议配合云端 API 使用。")

if __name__ == "__main__":
    args, config = parse_args_and_lock()
    set_global_args(args)

    from core.ui.handlers.status_handlers import StatusHandlers
    StatusHandlers.quick_banner()

    from core.ui.mediator import UIMediator
    UIMediator.register_listeners()
    LicenseGuard.verify_authority()
    probe_local_compute()

    if config and not config.active_imprint:
        chosen = im.get_most_recent_imprint()
        if chosen:
            config.active_imprint = chosen
            tlog.info(f"✨ [主权自愈] 自动探测并对正最新活动物理品牌: '{chosen}'")
            try:
                import yaml
                local_p = "config.local.yaml"
                l_data = {}
                if os.path.exists(local_p):
                    with open(local_p, 'r', encoding='utf-8') as f:
                        l_data = yaml.safe_load(f) or {}
                l_data["active_imprint"] = chosen
                with open(local_p, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(l_data, f, allow_unicode=True)
            except Exception as e:
                tlog.warning(f"⚠️ [配置持久化失败] 无法锁存 active_imprint: {e}")

    if config and config.active_imprint:
        from core.config.config import CONFIG_IMPRINT_NAME, IMPRINT_DIR, CONFIG_DIR
        imprint_config = os.path.join(IMPRINT_DIR, config.active_imprint, CONFIG_DIR, CONFIG_IMPRINT_NAME)
        if os.path.exists(imprint_config):
            if args.imprint == "default":
                args.imprint = config.active_imprint
                tlog.info(f"🔄 [品牌激活] (切换出版社) 出版品牌已切换至: {args.imprint}")
        else:
            tlog.warning(f"⚠️ [配置缺失] 品牌 '{config.active_imprint}' 的核心配置文件已丢失，进入初始化修复模式。")
            config.active_imprint = None
    
    # 3. 决定是否开启引导
    # 逻辑：如果没找到 active_imprint，且不是在执行管理指令，则开启引导
    is_admin_cmd = any([args.imprint_list, args.imprint_delete, args.imprint_create])
    should_wizard = args.wizard or (not is_admin_cmd and (not config or not config.active_imprint))
    
    if should_wizard:
        # 1. 授权红线预检 (略过列表，直接进入引导逻辑)
        # 2. 启动 Web 引导向导
        from core.ui.wizard import run_onboarding_wizard
        tlog.info("🧙 [环境初始化] 正在启动初始化引导向导 (端口: 43211)...")
        if not run_onboarding_wizard():
            tlog.error("🛑 [引导中断] 品牌建立失败，程序退出。")
            sys.exit(0)
        
        # 🚀 [V52.10] 引导完成后，重新加载配置以获取最新的 active_imprint
        from core.config.config import load_config
        config = load_config(args.config)
        args.imprint = config.active_imprint
        args.api = True
        setattr(sys, '_plenipes_fresh_install', True)
        tlog.info(f"🛰️ [自举成功] 品牌 '{args.imprint}' 已激活，正在接力启动...")
    
    try:

        if getattr(sys, '_plenipes_fresh_install', False):
            args.api = True

        # 6. 实例化主引擎 (内部会自动划定品牌疆域)
        from core.runtime.engine_factory import EngineFactory
        engine = EngineFactory.create_engine(config or args.config, no_ai=args.no_ai, args=args, imprint_id=args.imprint)
        from core.config.config import ConfigManager
        engine.config_manager = ConfigManager(args.config, imprint_id=args.imprint)

        
        # 🧪 [V50.3] 日志主权对正：在引擎划定品牌后，重定向日志管线
        logger = setup_logger(engine.paths["logs"])

        # 7. 激活当前活跃主权 Imprint
        im.switch(args.imprint)
        
        set_global_engine(engine)
        global_engine = engine


        # --- 后续任务执行逻辑 (Sync / Watch / Serve / Purge / Credentials) ---
        
        # 🧪 [V35.2] 资产净化特权指令
        if args.purge:
            engine.janitor.purge_dist()
            tlog.info("🏁 [净化完成] 出版品牌已恢复纯净状态。")
            if not any([args.sync, args.watch, args.serve]): sys.exit(0)

        # 📦 [增量装帧] 增量静态装帧编译指令
        if args.build:
            from core.syndication.incremental_builder import IncrementalBuildManager
            manager = IncrementalBuildManager(engine)
            if not manager.build():
                sys.exit(1)
            if not any([args.sync, args.watch, args.serve]):
                sys.exit(0)


        # 🧪 [V50.3] 凭据审计特权指令
        if args.credentials:
            tlog.info("🔍 [凭据审计] 正在启动交互式脱敏与加密向导...")
            from core.governance.credential_wizard import run_credentials_wizard
            run_credentials_wizard(args.config)
            if hasattr(engine, 'config_manager') and engine.config_manager:
                engine.config_manager.reload()
                from core.governance.contract_guard import ContractGuard
                violations = ContractGuard.verify_config(engine.config_manager.config)
                if any("安全红线" in v for v in violations):
                    tlog.error("🛑 [安全审计未通过] 依然存在未加密的明文密钥，请核对配置文件！")
                else:
                    tlog.success("🎉 [安全审计通过] 所有敏感凭据均已加密，安全红线状态已解除。")
        # 🧪 [V50.3] 主权体检特权指令
        if args.doctor:
            tlog.info("🩺 [主权体检] 正在启动全链路深度诊断中心...")
            report = engine.doctor.run_full_check()
            from core.ui.mediator import UIMediator
            UIMediator.show_doctor_report(report)
            try:
                from core.config.auditor import audit_config_layers, print_cli_audit_report
                audit_data = audit_config_layers(engine.config_manager, imprint_id=args.imprint)
                print_cli_audit_report(audit_data)
            except Exception as ae:
                tlog.warning(f"⚠️ [配置审计失败]: {ae}")
            if args.heal:
                tlog.info("💊 [物理自愈] 正在根据诊断报告执行自动修复手术...")
                repairs = engine.doctor.heal()
                for r in repairs:
                    tlog.success("✅ [品牌落成] (出版社已就绪) 出版品牌环境边界已确立。")
                tlog.info("🏁 [修复完成] 系统已尝试恢复至健康基准线。")
            if not any([args.sync, args.watch, args.serve]):
                sys.exit(0 if report["status"] != "FAIL" else 1)

        # 🚀 [V51.0] 商业级缺省逻辑：如果没有指定任何操作，默认进入“全量主权模式” (API + Watch)
        if not any([args.sync, args.watch, args.api, args.serve, args.doctor, args.purge, args.credentials]):
            tlog.info("🛰️ [自动对齐] 未指定操作指令，系统将自动进入 [全功能出版模式] (API + 全时守护)...")
            args.api = True
            args.watch = True

        # 🚀 [V51.0] 商业级启动时序优化：优先启动 API，确保同步过程可被 Dashboard 实时观测
        if args.api:
            from services.api.server import start_api_server
            active_cfg = config
            api_port = args.api_port or (active_cfg.system.api_port if active_cfg else 43212)
            tlog.info(f"🔌 [API 模式] 正在抢先启动出版 API 服务 (端口: {api_port})...")
            
            engine.services["api"].update({
                "status": "running",
                "port": api_port,
                "start_time": time.time()
            })
            # 🚀 [V51.0] 强制使用非阻塞模式启动，以便后续执行同步任务
            start_api_server(port=api_port, blocking=False)

        task_queue, current_source_files = prepare_sync_tasks(engine, requested_paths=args.path)

        if args.sync or (not any([args.api, args.serve, args.watch])):
            execute_full_sync(engine, args, task_queue, current_source_files)
            
        if args.watch:
            tlog.info("🐕 [后台守护] (环境监控) 系统监听已进入全时工作模式...")
            global_observer, _ = start_watchdog(engine, args, current_source_files)
        set_global_observer(global_observer)

        if args.serve:
            from core.utils.dev_server import DevServer
            # 自动探测预览目录
            preview_dir = engine.paths.get('site_dir') or engine.paths.get('target_base')
            if preview_dir:
                active_cfg = config
                port = args.serve_port or (active_cfg.system.serve_port if active_cfg else 43213)
                dev_server = DevServer(directory=preview_dir, port=port)
                engine.preview_server = dev_server
                
                # 🧪 [V50.3] 联动 Watch 模式实现热重载
                if args.watch:
                    from core.utils.event_bus import bus
                    bus.subscribe("SYNC_COMPLETED", lambda **kwargs: dev_server.notify_reload())
                
                # 🚀 [V50.3] 注册服务状态
                engine.services["preview"].update({
                    "status": "running",
                    "port": port,
                    "start_time": time.time(),
                    "root": preview_dir
                })
                
                tlog.info(f"🌐 [内嵌预览] 正在启动预览容器 (端口: {port})...")
                dev_server.start(blocking=not args.watch)
                # 🚀 [V80.0] 端口自愈后回填，确保系统注册的端口与实际运行端口一致
                engine.services["preview"].update({
                    "port": dev_server.port
                })
            else:
                tlog.warning("⚠️ [预览失败] 无法在配置中定位输出目录，请检查 output_paths。")

        # 🚀 [V51.0] 修正：如果是持续运行模式，保持主线程存活
        if args.watch or args.api or args.serve:
            setattr(sys, '_plenipes_in_loop', True)
            try:
                while not should_exit:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                setattr(sys, '_plenipes_in_loop', False)
            
            # 脱离信号上下文的安全退出流程，物理级避免 Lock 锁死
            if (logger): logger.warning("\n⚠️ 收到停止指令！正在尝试安全导出系统快照并关闭数字出版中心...")
            if global_observer: global_observer.stop()
            if global_engine and hasattr(global_engine, 'meta'):
                try:
                    global_engine.meta.force_save()
                    if logger: logger.info("  └── 🏁 出版进度已 100% 安全存档。")
                except: pass
            os._exit(0)
        else:
            tlog.info("🏁 [出版完成] (单次任务模式) 出版任务已全量闭环，出版品牌归位。")
            sys.exit(0)

    except Exception as e:
        if logger: logger.error(f"🚨 [紧急停机] 致命异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
