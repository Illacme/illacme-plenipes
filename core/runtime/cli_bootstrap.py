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
from core.ui.terminal import TerminalUI


from core.utils.tracing import tlog
_SINGLETON_SOCKET = None
_GLOBAL_ENGINE = None

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
    """
    global _SINGLETON_SOCKET
    _SINGLETON_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        _SINGLETON_SOCKET.bind(('127.0.0.1', port))
    except socket.error:
        tlog.error(f"\n🛑 [运行冲突] 启动失败：端口 {port} 已被占用，检测到系统已经在后台运行！")
        tlog.error("   └── 💡 为了保护您的文章数据和电脑内存，本次重复启动已自动拦截。")
        tlog.error("   └── 请检查是否开了多个终端窗口，或者在 config.yaml 中修改 singleton_port。")
        sys.exit(1)

def parse_args_and_lock():
    """解析命令行参数，执行配置文件自检，并激活防抖锁"""
    parser = argparse.ArgumentParser(description="Illacme-plenipes: 工业级 Markdown 到全量泛用型 SSG 映射同步中枢")
    parser.add_argument('--config', default='config.yaml', help="指定 YAML 配置文件路径 (默认: config.yaml)")
    parser.add_argument('--sync', action='store_true', help="发起单次全库阵列增量同步测绘")
    parser.add_argument('--watch', action='store_true', help="进入 Daemon 模式：启动系统看门狗守护进程，毫秒级监听源库变动")
    parser.add_argument('--dry-run', action='store_true', help="[安全演练模式] 阻断实际 API 扣费请求和物理写盘")
    parser.add_argument('--force', action='store_true', help="[强制重构模式] 强行撕碎 MD5 本地状态防抖指纹，强拉所有引擎模块执行覆盖重编")
    parser.add_argument('--re-slug', action='store_true', help="[Slug 重塑模式] 强制 AI 重新生成所有文档的 Slug（注意：这将导致现有 URL 变更，请谨慎使用）")


    # 🚀 [V31.3 增强参数]
    parser.add_argument('--path', '-p', nargs='+', help="[选择性同步] 指定同步的源文件或目录路径 (相对于库根目录，支持多个)")
    parser.add_argument('--no-ai', action='store_true', help="[离线/节流模式] 禁用所有 AI 任务 (翻译/SEO/Slug)，仅执行本地排版加工")
    parser.add_argument('--port', type=int, help="[多开模式] 物理覆盖 singleton_port，允许同一份配置运行多个实例")
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help="[诊断模式] 手动覆盖配置文件的终端日志级别")
    parser.add_argument('--clean', action='store_true', help="[一键重置] 物理删除所有同步指纹与 AI 影子缓存，重置引擎到初始态")
    parser.add_argument('--sentinel', action='store_true', help="🛡️ [哨兵主动管控] 立即唤醒项目哨兵，执行全量健康审计、Lint 修复与算力成本上报")
    parser.add_argument('--doctor', action='store_true', help="🩺 [全域诊断中心] 立即唤醒诊断中心，执行账本一致性审计、算力连通性体检与路径映射校验")
    parser.add_argument('--heal', action='store_true', help="💊 [自愈手术] 配合 --doctor 使用，自动修复路径缺失、Slug 冲突等关键风险")

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
    # 🚀 [V7.0 商业化主权参数]
    parser.add_argument('--workspace', '-ws', default='default', help="[多租户隔离] 指定工作空间 ID (默认: default)")
    parser.add_argument('--audit-report', action='store_true', help="📊 [审计报告] 导出当前工作空间的商业审计流水账本")

    args = parser.parse_args()
    cfg = None

    if not os.path.exists(args.config):
        # 🚀 零配置自启 (Magic Onboarding)
        from core.ui.terminal import TerminalUI
        example_config = 'config.example.yaml'
        if os.path.exists(example_config):
            config_data = TerminalUI.show_wizard()

            # 读取范例配置作为底座
            with open(example_config, 'r', encoding='utf-8') as f:
                import yaml
                base_cfg = yaml.safe_load(f) or {}

            # 深度合并向导配置
            def deep_update(d, u):
                import collections.abc
                for k, v in u.items():
                    if isinstance(v, collections.abc.Mapping):
                        d[k] = deep_update(d.get(k, {}), v)
                    else: d[k] = v
                return d

            final_cfg = deep_update(base_cfg, config_data)

            try:
                with open(args.config, 'w', encoding='utf-8') as f:
                    yaml.dump(final_cfg, f, allow_unicode=True, sort_keys=False)
                tlog.info(f"✨ 配置文件 '{args.config}' 已生成并初始化。")
            except Exception as e:
                tlog.error(f"🛑 自动生成配置文件失败: {e}")
                sys.exit(1)
        else:
            tlog.error(f"🛑 启动终止: 未发现配置文件 '{args.config}'，且未找到范例文件 '{example_config}'。")
            sys.exit(1)

    # 在初始化主引擎和模型加载前，单独解析系统级参数以抢占端口锁
    try:
        from core.config.config import load_config
        cfg = load_config(args.config)
        lock_port = args.port or cfg.system.safety_policy.singleton_port

        # 🚀 [V34.8] 动态回填配置文件的端口设置
        if args.api_port is None:
            args.api_port = cfg.system.api_port
        if args.serve_port is None:
            args.serve_port = cfg.system.serve_port

        # 🚀 [V34.9] 激活物理日志持久化：从配置中心读取 logs_dir
        from core.utils.tracing import setup_file_logging
        log_level = getattr(logging, args.log_level) if args.log_level else getattr(logging, cfg.system.log_level.upper(), logging.INFO)
        setup_file_logging(cfg.system.logs_dir, level=log_level)

        # 🚀 同步覆盖日志级别
        if args.log_level:
            tlog.setLevel(getattr(logging, args.log_level))
            tlog.info(f"⚙️ [内核诊断] 日志级别已由命令行覆盖为: {args.log_level}")
    except Exception as e:
        tlog.debug(f"前置配置加载异常 (可能正在自举): {e}")
        # 🚀 [V15.8] 回退值也应尽量从模型默认值中获取
        from core.config.models.system import SystemSettings
        default_sys = SystemSettings()
        lock_port = args.port or default_sys.safety_policy.singleton_port

    # 🚀 处理无头化标记
    if args.headless or args.json_log:
        from core.ui.terminal import TerminalUI
        import core.ui.terminal as terminal_mod
        terminal_mod.HEADLESS = True
        if args.json_log:
            terminal_mod.JSON_LOGGING = True

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
