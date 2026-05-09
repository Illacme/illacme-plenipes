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
import yaml
import platform
import time
import subprocess
import logging
from core.utils.tracing import tlog
from core.config.config import CONFIG_NAME, CONFIG_LOCAL_NAME, CONFIG_IMPRINT_NAME, IMPRINT_DIR, CONFIG_DIR
_SINGLETON_SOCKET = None
_GLOBAL_ENGINE = None
_GLOBAL_OBSERVER = None
_GLOBAL_ARGS = None

def set_global_args(args):
    global _GLOBAL_ARGS
    _GLOBAL_ARGS = args

def get_global_args():
    return _GLOBAL_ARGS

def get_global_engine():
    """🚀 获取引擎全局单例 (供 SSG 适配器或管线深度组件调用)"""
    return _GLOBAL_ENGINE

def set_global_engine(engine):
    """🛡️ 注册引擎全局单例 (支持热重载清理)"""
    global _GLOBAL_ENGINE
    if _GLOBAL_ENGINE and hasattr(_GLOBAL_ENGINE, 'sentinel'):
        try:
            tlog.debug("🔄 [热重载清理] 正在释放旧引擎的哨兵资源...")
            _GLOBAL_ENGINE.sentinel.stop()
        except: pass
    _GLOBAL_ENGINE = engine

def get_global_observer():
    return _GLOBAL_OBSERVER

def set_global_observer(observer):
    global _GLOBAL_OBSERVER
    if _GLOBAL_OBSERVER:
        try:
            tlog.debug("🔄 [热重载清理] 正在安全切断旧金库的实时监听...")
            _GLOBAL_OBSERVER.stop()
            _GLOBAL_OBSERVER.join(timeout=2.0)
        except: pass
    _GLOBAL_OBSERVER = observer

def deep_reload_imprint(imprint_id: str):
    """🚀 [V52.6] 深度主权迁移：全量重载引擎、配置与监控管线"""
    global _GLOBAL_ENGINE, _GLOBAL_ARGS
    
    if not _GLOBAL_ARGS:
        tlog.error("🛑 [重载失败] 无法定位原始启动参数，主权迁移中止。")
        return False
        
    tlog.info(f"🛰️ [主权迁移] 正在启动深度重载流水线 (Target Imprint: {imprint_id})...")
    
    try:
        # 🚀 [V52.15] 抢先主权对正 (物理消杀)：在加载配置前，直接清空 config.local.yaml
        # 仅保留 active_imprint 指针。这是因为 dashboard 会把全量配置同时写入 local 和 brand 层，
        # 导致 local 层变成上一个品牌的僵尸缓存，在切换时覆盖新品牌的配置。
        try:
            import yaml
            local_path = CONFIG_LOCAL_NAME
            existing_local = {}
            if os.path.exists(local_path):
                with open(local_path, "r", encoding="utf-8") as f:
                    existing_local = yaml.safe_load(f) or {}
            
            # 🚀 [V55.10] 主权迁移保障：确保在消杀前将关键路径固化到版图层
            if imprint_id != "default":
                target_imprint_yaml = os.path.join(IMPRINT_DIR, imprint_id, CONFIG_DIR, CONFIG_IMPRINT_NAME)
                if os.path.exists(target_imprint_yaml):
                    with open(target_imprint_yaml, "r", encoding="utf-8") as f:
                        target_cfg = yaml.safe_load(f) or {}
                    
                    # 如果版图内缺失 vault_root，则从当前 local 补全
                    if not target_cfg.get("vault_root") and existing_local.get("vault_root"):
                        target_cfg["vault_root"] = existing_local["vault_root"]
                        with open(target_imprint_yaml, "w", encoding="utf-8") as f:
                            yaml.safe_dump(target_cfg, f, allow_unicode=True)
                        tlog.debug(f"🏗️ [主权固化] 已将金库路径迁移至版图配置: {imprint_id}")

            l_cfg = {"active_imprint": imprint_id}
            # 💡 [V55.11] 物理保留：如果是默认品牌，保留其本地金库路径，避免 onboarding 循环
            if imprint_id == "default" and existing_local.get("vault_root"):
                l_cfg["vault_root"] = existing_local["vault_root"]

            with open(local_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(l_cfg, f, allow_unicode=True)
            tlog.debug(f"🛡️ [物理消杀] 已清空陈旧的 Local 缓存并预设活跃版图 '{imprint_id}'。")
        except Exception as ex:
            tlog.warning(f"⚠️ [物理消杀失败] {ex}")

        # 1. 加载基础配置 (显式传递目标品牌 ID，防止被陈旧的 local 层劫持)
        from core.config.config import load_config
        config_path = _GLOBAL_ARGS.config
        config = load_config(config_path, imprint_id=imprint_id)
        
        # 2. 调用工厂重新组装引擎 (内部会自动处理 Preflight)
        from core.runtime.engine_factory import EngineFactory
        new_engine = EngineFactory.create_engine(config, args=_GLOBAL_ARGS, imprint_id=imprint_id)
        
        if not new_engine:
            tlog.error("🛑 [重载失败] 引擎工厂组装失败。")
            return False
            
        # 3. 注册新引擎 (自动清理旧哨兵)
        set_global_engine(new_engine)
        
        # 🚀 [V52.12] 物理主权持久化：同步最终确定的活跃状态至 config.local.yaml
        try:
            import yaml
            local_path = CONFIG_LOCAL_NAME
            if os.path.exists(local_path):
                with open(local_path, "r", encoding="utf-8") as f:
                    local_cfg = yaml.safe_load(f) or {}
                
                local_cfg["active_imprint"] = imprint_id
                local_cfg["imprint_name"] = new_engine.config.imprint_name
                local_cfg["vault_root"] = new_engine.config.vault_root
                local_cfg["active_theme"] = new_engine.active_theme
                
                # 同步路径锚点
                if imprint_id != "default":
                    local_cfg.setdefault("system", {})["data_root"] = os.path.join(IMPRINT_DIR, imprint_id)
                else:
                    if "system" in local_cfg and "data_root" in local_cfg["system"]:
                        local_cfg["system"]["data_root"] = ".plenipes"
                    # 归位逻辑：强制恢复默认品牌名
                    local_cfg["imprint_name"] = "Illacme Press"
                    local_cfg["vault_root"] = "./content-vault"
                    local_cfg["active_theme"] = "default"
                
                with open(local_path, "w", encoding="utf-8") as f:
                    yaml.safe_dump(local_cfg, f, allow_unicode=True)
                tlog.debug(f"🛡️ [主权锁定] 活跃版图状态已同步至 {local_path}")
        except Exception: pass

        # 5. 🚀 [V52.6] 日志管线对正：重定向文件日志至新品牌领土
        from core.utils import setup_logger
        setup_logger(new_engine.paths["logs"])
        
        # 4. 如果开启了 Watch 模式，重新激活看门狗
        if _GLOBAL_ARGS.watch:
            from core.runtime.daemon import start_watchdog
            from core.runtime.orchestrator import prepare_sync_tasks
            
            # 准备新品牌的任务队列
            _, current_files = prepare_sync_tasks(new_engine, requested_paths=_GLOBAL_ARGS.path)
            
            # 🚀 [V52.10] 物理避让：在启动新监听器前，必须先彻底注销并停止旧监听器
            set_global_observer(None)
            
            # 启动新监听器
            new_observer, _ = start_watchdog(new_engine, _GLOBAL_ARGS, current_files)
            set_global_observer(new_observer)
            
        tlog.success(f"✅ [迁移完成] 出版品牌已成功切换至 '{imprint_id}'，物理主权已全面对正。")
        return True
        
    except Exception as e:
        tlog.error(f"🛑 [迁移异常] 致命错误: {e}")
        import traceback
        traceback.print_exc()
        return False

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
        tlog.debug(f"系统通知发送失败: {e}")

def acquire_singleton_lock(port=43210): # 默认值仅作签名参考，实际由 parse_args_and_lock 传入
    """
    进程级单例防线 (OS-Level Singleton Mutex)
    基于配置文件动态分配防撞端口。
    🚀 [V50.5] 增强：增加 5 秒宽容期，支持主权接力时的平滑过渡。
    """
    global _SINGLETON_SOCKET
    import time
    
    attempts = 0
    max_attempts = 5
    while attempts < max_attempts:
        _SINGLETON_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            _SINGLETON_SOCKET.bind(('127.0.0.1', port))
            return # 成功夺取主权锁
        except socket.error:
            if attempts == 0:
                tlog.debug(f"⏳ [端口竞争] 正在等待端口 {port} 释放主权 (尝试 {attempts+1}/{max_attempts})...")
            
            attempts += 1
            if attempts < max_attempts:
                time.sleep(1)
            else:
                tlog.error(f"\n🛑 [运行冲突] 启动失败：端口 {port} 已被占用，检测到系统已经在后台运行！")
                tlog.error("   └── 💡 为了保护您的文章数据和电脑内存，本次重复启动已自动拦截。")
                tlog.error("   └── 请检查是否开了多个终端窗口，或者在 config.yaml 中修改 singleton_port。")
                sys.exit(1)

def parse_args_and_lock():
    """解析命令行参数，执行配置文件自检，并激活防抖锁"""
    parser = argparse.ArgumentParser(description="🛡️ Illacme-plenipes [V50.3]: 全球私人出版社主权操作系统 - 负责从原稿摄取到全量分发的全生命周期治理")

    parser.add_argument('--config', '-c', default='config.yaml', help="指定 YAML 配置文件路径 (默认: config.yaml)")
    parser.add_argument('--sync', '-s', action='store_true', help="🚀 [分发演习] 发起单次全库阵列资产分发演习")
    parser.add_argument('--watch', '-w', action='store_true', help="🐕 [全时守护] 启动系统看门狗，实时监控原稿变更并触发即时分发")
    parser.add_argument('--dry-run', action='store_true', help="🛡️ [安全仿真模式] 模拟全流程逻辑，阻断一切物理写盘与 API 费用支出")
    parser.add_argument('--force', '-f', action='store_true', help="🔥 [强制重构] 强行撕碎指纹防抖，强拉所有引擎模块执行覆盖重编")
    parser.add_argument('--re-slug', action='store_true', help="🧠 [路径重塑] 强制 AI 重新生成文档路径锚点 (警告：会导致现有 URL 失效)")



    # 🚀 [V31.3 增强参数]
    parser.add_argument('--path', '-p', nargs='+', help="[选择性同步] 指定同步的源文件或目录路径 (相对于库根目录，支持多个)")
    parser.add_argument('--no-ai', action='store_true', help="[离线/节流模式] 禁用所有 AI 任务 (翻译/SEO/Slug)，仅执行本地排版加工")
    parser.add_argument('--port', type=int, help="[多开模式] 物理覆盖 singleton_port，允许同一份配置运行多个实例")
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help="[诊断模式] 手动覆盖配置文件的终端日志级别")
    parser.add_argument('--clean', action='store_true', help="🧹 [主权重置] 物理删除所有同步指纹与 AI 影子缓存")
    parser.add_argument('--purge', action='store_true', help="🪠 [资产净化] 立即唤醒清道夫 (Janitor)，抹除出版品牌内的所有非法或过期资产")
    parser.add_argument('--sentinel', action='store_true', help="🛡️ [哨兵审计] 立即唤醒项目哨兵，执行健康审计与算力成本上报")
    parser.add_argument('--doctor', '-d', action='store_true', help="🩺 [主权体检] 启动诊断中心，执行账本一致性审计与路径映射校验")
    parser.add_argument('--heal', action='store_true', help="💊 [物理自愈] 配合 --doctor 使用，自动修复路径缺失与指纹冲突")


    # 🚀 [V11.0 全息主权治理]
    parser.add_argument('--sandbox', action='store_true', help="📦 [仿真沙盒模式] 同步任务仅分发至演习场，不触动生产环境")
    parser.add_argument('--audit', action='store_true', help="📊 [差异审计] 自动比对沙盒预览与生产环境的差异，生成全息质量简报")
    parser.add_argument('--promote', action='store_true', help="🚀 [一键转正] 将已审计的沙盒内容物理推向 SSG 生产目录")
    parser.add_argument('--brain', action='store_true', help="🧠 [知识中心] 展示 V11.0 自动化教训累积简报，透视系统进化轨迹")

    # 🚀 [V11.7 原生预览支持]
    parser.add_argument('--serve', action='store_true', help="🌐 [内嵌预览] 同步完成后自动启动极简 Web 容器，预览当前主题的 HTML 产物")
    parser.add_argument('--serve-port', type=int, help="[预览端口] 自定义内嵌预览服务器的监听端口")

    # 🚀 [V14.1 API 化]
    parser.add_argument('--api', action='store_true', help="🔌 [API 模式] 启动 FastAPI 后端服务，暴露监控接口与实时事件流")
    parser.add_argument('--api-port', type=int, help="[API 端口] 自定义 API 服务器端口")

    # 🚀 [V10.1 Headless Engine]
    parser.add_argument('--headless', action='store_true', help="[无头模式] 彻底剥离 Rich 视觉组件与进度条，仅保留基础日志")
    parser.add_argument('--json-log', action='store_true', help="[结构化日志] 强制以 JSON 格式输出日志，便于外部系统采集审计")

    # 🚀 [V12.2 时光机]
    parser.add_argument('--rollback', action='store_true', help="⏪ [时光机回滚] 将账本恢复至上一个紧急检查点 (pre_sync)")
    parser.add_argument('--rollback-to', help="⏪ [高级回滚] 指定回滚的快照名称")

    # 🚀 [V13.0 插件中心]
    parser.add_argument('--list-plugins', action='store_true', help="📡 [插件中心] 枚举当前系统中所有已注册的分发插件及其运行时状态")

    # 🚀 [V34.6] 进程自杀协议
    parser.add_argument('--shutdown', action='store_true', help="🛑 [远程下线] 向正在运行的实例发送关机指令并安全存档 (需要 API 模式已启动)")
    # 🚀 [V50.3 主权定型参数]
    parser.add_argument('--imprint', '-i', dest='imprint', default='default', help="🌐 [出版品牌选择] 指定当前操作的 Imprint ID (默认: default)")


    parser.add_argument('--credentials', action='store_true', help="🔑 [凭据审计] 扫描并脱敏当前品牌内的所有敏感凭据")
    parser.add_argument('--audit-report', action='store_true', help="📊 [账本报告] 导出当前出版品牌的商业审计流水账本")

    # 🚀 [V50.3] 工业级 Imprint 治理体系 (Imprint Governance)
    parser.add_argument('--imprint-list', action='store_true', help="📜 [品牌清单] 枚举当前系统内所有已划定的出版品牌 (Imprints)")
    parser.add_argument('--imprint-create', metavar='NAME', help="🏗️ [品牌划定] 快速创建一个新的出版品牌 (需配合 --vault-path)")
    parser.add_argument('--imprint-delete', metavar='NAME', help="🪓 [品牌撤销] 物理抹除一个已有的出版品牌及其所有资产")
    parser.add_argument('--vault-path', metavar='PATH', help="📂 [物理锚定] 指定原稿金库的物理路径 (用于创建新品牌)")
    from core import __version__, __edition__
    parser.add_argument('--wizard', '-W', action='store_true', help="🧙 [引导向导] 启动 Web 端可视化安装与配置向导")
    parser.add_argument('--version', '-v', action='version', version=f'Illacme-plenipes v{__version__} ({__edition__})')


    args = parser.parse_args()
    cfg = None

    if not os.path.exists(args.config) or args.wizard or args.imprint_create:
        # 🚀 零配置自启 (Magic Onboarding) 或 手动管理品牌
        from core.ui.mediator import UIMediator
        example_config = 'config.example.yaml'
        if os.path.exists(example_config):
            # 如果提供了完整的命令行参数，执行非交互式初始化数据准备
            if args.imprint_create and args.vault_path:
                tlog.info(f"🏗️ [自动化初始化] 正在准备出版品牌配置: {args.imprint_create}")
                config_data = {
                    "press_name": args.imprint_create,
                    "vault_root": args.vault_path,
                    "active_theme": "starlight",
                    "system": {"singleton_port": 43210}
                }
            # 读取范例配置作为底座
            with open(example_config, 'r', encoding='utf-8') as f:
                import yaml
                base_cfg = yaml.safe_load(f) or {}

            # 🚀 [V50.5] 简化自举逻辑：底层不再负责交互式向导
            # 所有的向导触发与品牌建立逻辑已统一收口至 plenipes.py
            final_cfg = base_cfg

            try:
                # 仅在文件缺失时初始化基础配置
                if not os.path.exists(args.config):
                    with open(args.config, 'w', encoding='utf-8') as f:
                        yaml.dump(final_cfg, f, allow_unicode=True, sort_keys=False)
                    tlog.info(f"✨ 基础配置文件 '{args.config}' 已生成。")
            except Exception as e:
                tlog.error(f"🛑 自动生成配置文件失败: {e}")
                sys.exit(1)
        else:
            if not os.path.exists(args.config):
                tlog.error(f"🛑 启动终止: 未发现配置文件 '{args.config}'，且未找到范例文件 '{example_config}'。")
                sys.exit(1)

    # 在初始化主引擎和模型加载前，单独解析系统级参数以抢占端口锁
    try:
        from core.config.config import load_config
        cfg = load_config(args.config)
        lock_port = args.port or cfg.system.singleton_port

        # 🚀 [V34.8] 动态回填配置文件的端口设置
        if args.api_port is None:
            args.api_port = cfg.system.api_port
        if args.serve_port is None:
            args.serve_port = cfg.system.serve_port

        # 🚀 [V34.9] 日志持久化已由 plenipes.py 接管，以实现主权对正
        log_level = getattr(logging, args.log_level) if args.log_level else getattr(logging, cfg.system.log_level.upper(), logging.INFO)
        # setup_file_logging(cfg.system.logs_dir, level=log_level) # [V35.2] 移除过早初始化，防止日志逃逸

        # 🚀 同步覆盖日志级别
        if args.log_level:
            tlog.setLevel(getattr(logging, args.log_level))
            tlog.info(f"⚙️ [内核诊断] 日志级别已由命令行覆盖为: {args.log_level}")
    except Exception as e:
        tlog.debug(f"前置配置加载异常 (可能正在自举): {e}")
        # 🚀 [V15.8] 回退值也应尽量从模型默认值中获取
        from core.config.models.system import SystemSettings
        default_sys = SystemSettings()
        lock_port = args.port or default_sys.singleton_port

    # 🚀 处理无头化标记
    if args.headless or args.json_log:
        from core.ui.mediator import UIMediator
        UIMediator.set_web_mode(True) # 借用 Web 模式来静默 Rich
        if args.json_log:
            os.environ['PLENIPES_JSON_LOG'] = '1'

    if args.shutdown:
        # 🚀 [V34.6] 物理关机逻辑：尝试通过 API 端口发送自杀指令
        from core.config.models.system import SystemSettings
        default_sys = SystemSettings()
        
        target_host = cfg.system.serve_host if 'cfg' in locals() else "127.0.0.1"
        api_port = args.api_port or (cfg.system.api_port if 'cfg' in locals() else default_sys.api_port)
        net_timeout = cfg.system.resilience.network_timeout if 'cfg' in locals() else default_sys.resilience.network_timeout

        # 🚀 [V34.9] 精准打击：如果同时带了 --serve 参数，则只关闭预览服务，不关闭主引擎
        if args.serve:
            tlog.info(f"📡 [远程指令] 正在请求关闭预览服务 (地址: {target_host}:{api_port})...")
            target_url = f"http://{target_host}:{api_port}/serve/control?action=stop"
            success_msg = "✅ [指令完成] 预览服务器已安全下线，主引擎继续保持监听。"
        else:
            tlog.info(f"📡 [远程指令] 正在请求全局关机 (端口: {api_port})...")
            target_url = f"http://{target_host}:{api_port}/shutdown"
            success_msg = "✅ [指令完成] 全局下线指令已送达，系统正在存档并退出。"

        import urllib.request
        try:
            # 💡 [V34.9] 安全补丁：注入 API 令牌
            headers = {}
            api_token = cfg.system.api_token if 'cfg' in locals() else ""
            if api_token:
                headers["X-Token"] = api_token

            req = urllib.request.Request(target_url, data=b"", headers=headers)
            with urllib.request.urlopen(req, timeout=net_timeout) as response:
                if response.status == 200:
                    tlog.info(success_msg)
                else:
                    tlog.error(f"❌ [指令失败] 服务器返回异常状态码: {response.status}")
        except Exception as e:
            tlog.error(f"🛑 [远程指令] 发送失败: {e}")
            tlog.error("   └── 💡 请确认该实例是否开启了 --api 模式，或端口是否正确。")
            sys.exit(1)
        sys.exit(0)

    # 🚀 [V11.0] 启动前置主权治理自检
    try:
        from tests.sovereignty_guard import TestSovereigntyGuard
        import unittest
        import io
        suite = unittest.TestLoader().loadTestsFromTestCase(TestSovereigntyGuard)
        # 🚀 [V34.9] 警告收集器：不再直接打印，交由 UI 在 Banner 后统一渲染
        engine_warnings = []
        if cfg and cfg.output_paths.get('markdown_dir', '').startswith('.'):
            engine_warnings.append("⚠️ [配置弱项] 输出目录使用相对路径，建议迁移至绝对路径以增强主权隔离性。")
            
        # 记录到 hub 供后续回填
        from core.logic.ai.model_intelligence import ModelIntelligenceHub
        for w in engine_warnings:
            ModelIntelligenceHub.record_failure("system", reason=w)

        tlog.info("🛡️ [主权治理自检] 核心红线验证通过。")
    except Exception as e:
        tlog.warning(f"⚠️ [主权治理自检] 检查异常: {e}")

    acquire_singleton_lock(lock_port)
    return args, cfg
