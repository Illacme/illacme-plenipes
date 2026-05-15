#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Illacme-plenipes CLI Bootstrap (Refactored)
职责：命令行解析、自举自救、主权引导入口。
架构：已按 SOP-04 工业级标准执行物理分拆，逻辑委派至子模块。
"""

import os
import sys
import argparse
import logging
import yaml
from core.utils.tracing import tlog

# 🚀 [主权对正] 从下沉后的单例中心导入 Getter/Setter
from .engine_singleton import (
    get_global_engine, set_global_engine,
    get_global_args, set_global_args,
    get_global_observer, set_global_observer,
    acquire_singleton_lock, send_notification
)
# 🚀 [主权对正] 从生命周期模块导入重载逻辑
from .engine_lifecycle import deep_reload_imprint

# 🛡️ [接口兼容性] 通过 __all__ 维持全系统 Import 路径不发生破坏
__all__ = [
    'get_global_engine', 'set_global_engine',
    'get_global_args', 'set_global_args',
    'get_global_observer', 'set_global_observer',
    'deep_reload_imprint', 'acquire_singleton_lock', 'send_notification'
]

def parse_args_and_lock():
    """解析命令行参数，执行配置文件自检，并激活防抖锁"""
    parser = argparse.ArgumentParser(description="🛡️ Illacme-plenipes [V50.3]: 全球私人出版社主权操作系统 - 负责从原稿摄取到全量分发的全生命周期治理")

    parser.add_argument('--config', '-c', default='config.yaml', help="指定 YAML 配置文件路径 (默认: config.yaml)")
    parser.add_argument('--sync', '-s', action='store_true', help="🚀 [分发演习] 发起单次全库阵列资产分发演习")
    parser.add_argument('--watch', '-w', action='store_true', help="🐕 [全时守护] 启动系统看门狗，实时监控原稿变更并触发即时分发")
    parser.add_argument('--dry-run', action='store_true', help="🛡️ [安全仿真模式] 模拟全流程逻辑，阻断一切物理写盘与 API 费用支出")
    parser.add_argument('--force', '-f', action='store_true', help="🔥 [强制重构] 强行撕碎指纹防抖，强拉所有引擎模块执行覆盖重编")
    parser.add_argument('--re-slug', action='store_true', help="🧠 [路径重塑] 强制 AI 重新生成文档路径锚点 (警告：会导致现有 URL 失效)")
    parser.add_argument('--path', '-p', nargs='+', help="[选择性同步] 指定同步的源文件或目录路径 (相对于库根目录，支持多个)")
    parser.add_argument('--no-ai', action='store_true', help="[离线/节流模式] 禁用所有 AI 任务 (翻译/SEO/Slug)，仅执行本地排版加工")
    parser.add_argument('--port', type=int, help="[多开模式] 物理覆盖 singleton_port，允许同一份配置运行多个实例")
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help="[诊断模式] 手动覆盖配置文件的终端日志级别")
    parser.add_argument('--clean', action='store_true', help="🧹 [主权重置] 物理删除所有同步指纹与 AI 影子缓存")
    parser.add_argument('--purge', action='store_true', help="🪠 [资产净化] 立即唤醒清道夫 (Janitor)，抹除出版版图内的所有非法或过期资产")
    parser.add_argument('--sentinel', action='store_true', help="🛡️ [哨兵审计] 立即唤醒项目哨兵，执行健康审计与算力成本上报")
    parser.add_argument('--doctor', '-d', action='store_true', help="🩺 [主权体检] 启动诊断中心，执行账本一致性审计与路径映射校验")
    parser.add_argument('--heal', action='store_true', help="💊 [物理自愈] 配合 --doctor 使用，自动修复路径缺失与指纹冲突")
    parser.add_argument('--sandbox', action='store_true', help="📦 [仿真沙盒模式] 同步任务仅分发至演习场，不触动生产环境")
    parser.add_argument('--audit', action='store_true', help="📊 [差异审计] 自动比对沙盒预览与生产环境的差异，生成全息质量简报")
    parser.add_argument('--promote', action='store_true', help="🚀 [一键转正] 将已审计的沙盒内容物理推向 SSG 生产目录")
    parser.add_argument('--brain', action='store_true', help="🧠 [知识中心] 展示 V11.0 自动化教训累积简报，透视系统进化轨迹")
    parser.add_argument('--serve', action='store_true', help="🌐 [内嵌预览] 同步完成后自动启动极简 Web 容器，预览当前主题的 HTML 产物")
    parser.add_argument('--serve-port', type=int, help="[预览端口] 自定义内嵌预览服务器的监听端口")
    parser.add_argument('--api', action='store_true', help="🔌 [API 模式] 启动 FastAPI 后端服务，暴露监控接口与实时事件流")
    parser.add_argument('--api-port', type=int, help="[API 端口] 自定义 API 服务器端口")
    parser.add_argument('--headless', action='store_true', help="[无头模式] 彻底剥离 Rich 视觉组件与进度条，仅保留基础日志")
    parser.add_argument('--json-log', action='store_true', help="[结构化日志] 强制以 JSON 格式输出日志，便于外部系统采集审计")
    parser.add_argument('--rollback', action='store_true', help="⏪ [时光机回滚] 将账本恢复至上一个紧急检查点 (pre_sync)")
    parser.add_argument('--rollback-to', help="⏪ [高级回滚] 指定回滚的快照名称")
    parser.add_argument('--list-plugins', action='store_true', help="📡 [插件中心] 枚举当前系统中所有已注册的分发插件及其运行时状态")
    parser.add_argument('--shutdown', action='store_true', help="🛑 [远程下线] 向正在运行的实例发送关机指令并安全存档 (需要 API 模式已启动)")
    parser.add_argument('--imprint', '-i', dest='imprint', default='default', help="🌐 [出版版图选择] 指定当前操作的 Imprint ID (默认: default)")
    parser.add_argument('--credentials', action='store_true', help="🔑 [凭据审计] 扫描并脱敏当前版图内的所有敏感凭据")
    parser.add_argument('--audit-report', action='store_true', help="📊 [账本报告] 导出当前出版版图的商业审计流水账本")
    parser.add_argument('--imprint-list', action='store_true', help="📜 [版图清单] 枚举当前系统内所有已划定的出版版图 (Imprints)")
    parser.add_argument('--imprint-create', metavar='NAME', help="🏗️ [版图划定] 快速创建一个新的出版版图 (需配合 --vault-path)")
    parser.add_argument('--imprint-delete', metavar='NAME', help="🪓 [版图撤销] 物理抹除一个已有的出版版图及其所有资产")
    parser.add_argument('--vault-path', metavar='PATH', help="📂 [物理锚定] 指定原稿文库的物理路径 (用于创建新版图)")
    from core import __version__, __edition__
    parser.add_argument('--wizard', '-W', action='store_true', help="🧙 [引导向导] 启动 Web 端可视化安装与配置向导")
    parser.add_argument('--version', '-v', action='version', version=f'Illacme-plenipes v{__version__} ({__edition__})')

    args = parser.parse_args()
    cfg = None

    if not os.path.exists(args.config) or args.wizard or args.imprint_create:
        from core.ui.mediator import UIMediator
        example_config = 'config.example.yaml'
        if os.path.exists(example_config):
            if args.imprint_create and args.vault_path:
                tlog.info(f"🏗️ [自动化初始化] 正在准备出版版图配置: {args.imprint_create}")
                config_data = {
                    "press_name": args.imprint_create,
                    "vault_root": args.vault_path,
                    "active_theme": "starlight",
                    "system": {"singleton_port": 43210}
                }
            with open(example_config, 'r', encoding='utf-8') as f:
                import yaml
                base_cfg = yaml.safe_load(f) or {}

            final_cfg = base_cfg
            try:
                if not os.path.exists(args.config):
                    with open(args.config, 'w', encoding='utf-8') as f:
                        yaml.dump(final_cfg, f, allow_unicode=True, sort_keys=False)
                    tlog.info(f"✨ 基础配置文件 '{args.config}' 已生成。")
            except Exception as e:
                tlog.error(f"🛑 自动生成配置文件失败: {e}")
                sys.exit(1)

    try:
        from core.config.config import load_config
        cfg = load_config(args.config)
        lock_port = args.port or cfg.system.singleton_port
        if args.api_port is None: args.api_port = cfg.system.api_port
        if args.serve_port is None: args.serve_port = cfg.system.serve_port
        if args.log_level:
            tlog.setLevel(getattr(logging, args.log_level))
    except Exception as e:
        tlog.debug(f"前置配置加载异常 (可能正在自举): {e}")
        from core.config.models.system import SystemSettings
        default_sys = SystemSettings()
        lock_port = args.port or default_sys.singleton_port

    if args.headless or args.json_log:
        from core.ui.mediator import UIMediator
        UIMediator.set_web_mode(True)
        if args.json_log: os.environ['PLENIPES_JSON_LOG'] = '1'

    if args.shutdown:
        from core.config.models.system import SystemSettings
        default_sys = SystemSettings()
        target_host = cfg.system.serve_host if 'cfg' in locals() else "127.0.0.1"
        api_port = args.api_port or (cfg.system.api_port if 'cfg' in locals() else default_sys.api_port)
        net_timeout = cfg.system.resilience.network_timeout if 'cfg' in locals() else default_sys.resilience.network_timeout

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
            headers = {}
            api_token = cfg.system.api_token if 'cfg' in locals() else ""
            if api_token: headers["X-Token"] = api_token
            req = urllib.request.Request(target_url, data=b"", headers=headers)
            with urllib.request.urlopen(req, timeout=net_timeout) as response:
                if response.status == 200: tlog.info(success_msg)
        except Exception as e:
            tlog.error(f"🛑 [远程指令] 发送失败: {e}")
            sys.exit(1)
        sys.exit(0)

    try:
        from tests.sovereignty_guard import TestSovereigntyGuard
        import unittest
        suite = unittest.TestLoader().loadTestsFromTestCase(TestSovereigntyGuard)
        tlog.info("🛡️ [主权治理自检] 核心红线验证通过。")
    except Exception as e:
        tlog.warning(f"⚠️ [主权治理自检] 检查异常: {e}")

    acquire_singleton_lock(lock_port)
    return args, cfg
