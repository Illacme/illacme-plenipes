#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sync Orchestrator
模块职责：单次全量/增量同步的并发调度总管。
负责初始化的队列扫描、高并发 `ThreadPoolExecutor` 任务派发，以及极尽严苛的资产交叉审计雷达。
"""

import os
import time
from datetime import datetime
import traceback
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from .cli_bootstrap import send_notification

logger = logging.getLogger("Illacme.plenipes")

def prepare_sync_tasks(engine):
    """根据路由矩阵，扫描物理目录，建立同步初始化队列"""
    current_source_files = set()
    task_queue = []
    
    for route_cfg in engine.route_matrix:
        src_rel = route_cfg.get('source', '')
        prefix = route_cfg.get('prefix', '')
        abs_src = os.path.join(engine.vault_root, src_rel)
        
        if not os.path.exists(abs_src):
            logger.warning(f"路由源矩阵缺失: 无法找到映射物理目录 {abs_src}")
            continue
            
        for root, _, files in os.walk(abs_src):
            for f in files:
                if f.endswith((".md", ".mdx")):
                    rel_path = os.path.relpath(os.path.join(root, f), engine.vault_root).replace('\\', '/')
                    
                    if engine._is_excluded(rel_path): 
                        continue
                        
                    task_queue.append((os.path.join(root, f), prefix, src_rel))
                    current_source_files.add(rel_path)
                    engine.meta.register_document(rel_path, os.path.splitext(f)[0], route_prefix=prefix, route_source=src_rel)
                    
    return task_queue, current_source_files

def execute_full_sync(engine, args, task_queue, current_source_files):
    """
    核心任务并发调度派发区 (单次 Sync 逻辑)
    🚀 [架构升级 V14.3]：全面引入 Rich 工业级全息仪表盘。
    废弃传统的逐行 Print 滚屏机制，改为底部吸顶的动态进度条，完美解决 1000+ 极高并发下的“日志致盲”问题。
    """
    if not task_queue:
        logger.warning("⚠️ 没有找到任何 Markdown 笔记！💡 请检查 config.yaml 中的 `route_matrix` 目录配置是否正确。")
        return

    start_perf = time.perf_counter()
    start_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"🚀 [系统点火] 核心引擎启动 | 启动时间: {start_time_str}")

    mode_str = 'Dry-Run 安全模拟' if args.dry_run else f'物理火力: {engine.max_workers} 核同步'
    logger.info(f"🚀 [全速点火] 引擎就绪 | {mode_str} | 待处理文章: {len(task_queue)} 篇")
    
    # ---------------------------------------------------------
    # 📊 仪表盘装载层 (UI Loading)
    # ---------------------------------------------------------
    try:
        from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    except ImportError:
        logger.error("❌ 缺失工业级 UI 渲染依赖！请立即在终端执行: pip install rich")
        import sys
        sys.exit(1)

    total_tasks = len(task_queue)

    # 挂载 Rich 动态上下文，定义进度条的 5 个视觉列：动画转子、任务名、能量条、百分比、已消耗时间
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=40, complete_style="green", finished_style="bold green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("({task.completed}/{task.total})"),
        TimeElapsedColumn(),
        transient=False  # 设置为 False，进度条走满后保留在屏幕上，作为执行留档
    ) as progress:
        
        # 注册主控任务槽
        task_id = progress.add_task("🚀 V8 核心并发调度中...", total=total_tasks)
        
        # ---------------------------------------------------------
        # ⚡️ 并发射击层 (Thread Pool Dispatch)
        # ---------------------------------------------------------
        with ThreadPoolExecutor(max_workers=engine.max_workers) as executor:
            future_to_task = {
                executor.submit(engine.sync_document, task_path, prefix, src_rel, args.dry_run, args.force): task_path 
                for task_path, prefix, src_rel in task_queue
            }
            
            for future in as_completed(future_to_task):
                task_path = future_to_task[future]
                try: 
                    # 侦听线程内部异常
                    future.result()
                except Exception as e: 
                    # 🛡️ 架构防线：遇到报错时，不使用传统 logger 破坏进度条，而是通过 progress.console 输出
                    # 这会让报错信息平滑地从进度条上方飘出，彻底免疫屏幕撕裂
                    progress.console.print(f"[bold red]❌ 文章处理遇到意外故障 ({os.path.basename(task_path)}): {e}[/bold red]")
                    logger.error(f"❌ 文章处理遇到意外故障 ({os.path.basename(task_path)}): {traceback.format_exc()}")
                finally:
                    # 每当任意一个子线程安全着陆，将主进度条推进一步
                    progress.advance(task_id)
    
    # === 进度条走满结束，重新接管后续串行清理逻辑 ===
    if not args.dry_run: 
        engine.meta.force_save() 
    
    elapsed_seconds = time.perf_counter() - start_perf
    time_display = f"{elapsed_seconds:.2f} 秒" if elapsed_seconds < 60 else f"{int(elapsed_seconds // 60)} 分 {elapsed_seconds % 60:.2f} 秒"
    logger.info(f"🎉 全部文章同步动作执行完毕 | ⏱️ 阵列总耗时: {time_display}")

    enable_audit = engine.sys_cfg.get('enable_asset_audit', True)

    if enable_audit:
        logger.info("🧹 [资产审计] 启动全量交叉验证基线管控 (双轨模式)...")
        asset_docs_count = 0
        missing_local_assets = []
        remote_assets_to_check = set()
        
        for rel_path in current_source_files:
            doc_info = engine.meta.get_doc_info(rel_path)
            has_local = doc_info and doc_info.get('assets')
            has_remote = doc_info and doc_info.get('ext_assets')
            
            if has_local or has_remote:
                asset_docs_count += 1
                
            if has_local:
                for asset_path in doc_info['assets']:
                    if str(asset_path).startswith(('http://', 'https://', '//')):
                        continue
                    abs_asset_path = os.path.join(engine.paths['assets'], asset_path)
                    if not os.path.exists(abs_asset_path):
                        missing_local_assets.append((rel_path, asset_path))
                        
            if has_remote:
                for ext_url in doc_info['ext_assets']:
                    remote_assets_to_check.add((rel_path, ext_url))

        logger.info(f"📊 [审计简报] 本轮参与对齐文档: {len(current_source_files)} 篇 | 确诊含资产文档: {asset_docs_count} 篇")

        if missing_local_assets:
            logger.warning(f"⚠️ [本地资产断链] 警报：发现 {len(missing_local_assets)} 处物理资产已丢失！")
            for doc, missing_asset in missing_local_assets[:5]:
                logger.warning(f"   └── 缺链点：文档 [{doc}] 指向了不存在的 [{missing_asset}]")
            if len(missing_local_assets) > 5:
                logger.warning(f"   └── ... 等共 {len(missing_local_assets)} 处断链。")
        else:
            logger.info("✨ [本地审计] 正向引用检查完美通过，物理资产已 100% 严丝合缝。")

        if remote_assets_to_check:
            logger.info(f"📡 [外链雷达] 正在嗅探 {len(remote_assets_to_check)} 个远程图床链接的存活性...")
            dead_remote_links = []
            
            def ping_remote_asset(doc_path, url):
                network_cfg = engine.sys_cfg.get('network_settings', {})
                default_ignored = [
                    'img.shields.io', 'badgen.net', 'badge.fury.io', 'skillicons.dev',
                    'github-readme-stats.vercel.app', 'github-readme-streak-stats.herokuapp.com',
                    'komarev.com', 'wakatime.com',
                    'visitor-badge.laobi.icu', 'visitor-badge.glitch.me', 
                    'api.visitorbadge.io', 'hits.seeyoufarm.com', 'count.getloli.com'
                ]
                ignored_domains = network_cfg.get('ignored_domains') or default_ignored
                if any(domain in url for domain in ignored_domains):
                    return None
                    
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                    resp = requests.head(url, headers=headers, timeout=3, allow_redirects=True)
                    if resp.status_code in [404, 410, 500, 502, 503]:
                        return (doc_path, url, f"HTTP {resp.status_code}")
                    return None
                except requests.RequestException:
                    return (doc_path, url, "连接超时或被目标服务器强制掐断")

            with ThreadPoolExecutor(max_workers=10) as prober:
                futures = [prober.submit(ping_remote_asset, doc, url) for doc, url in remote_assets_to_check]
                for f in as_completed(futures):
                    result = f.result()
                    if result:
                        dead_remote_links.append(result)
                        
            if dead_remote_links:
                logger.warning(f"🔴 [外链失效警报] 探测到 {len(dead_remote_links)} 个远程图床链接已死亡 (404或无响应)！")
                for doc, url, reason in dead_remote_links[:5]:
                    logger.warning(f"   └── 🚨 碎链: [{doc}] -> {url} ({reason})")
                if len(dead_remote_links) > 5:
                    logger.warning(f"   └── ... 剩余 {len(dead_remote_links) - 5} 个死链已折叠。")
            else:
                logger.info("🟢 [外链雷达] 所有远程图床链接均返回 HTTP 200，健康度 100%！")

        engine.janitor.gc_orphans(current_source_files, is_dry_run=args.dry_run)
        engine.janitor.gc_ghost_nodes(is_dry_run=args.dry_run)
        if not args.dry_run:
            engine.meta.save()
    else:
        logger.info("🧹 [资产审计] 已根据配置文件 (enable_asset_audit: false) 主动跳过基线交叉验证与物理清理操作。")
    
    if not args.dry_run:
        send_notification("Illacme 同步完成", f"已成功同步 {len(task_queue)} 篇文章，总耗时 {time_display}")

    degraded_files = []
    for task_path, prefix, src_rel in task_queue:
        rel_path = os.path.relpath(task_path, engine.vault_root).replace('\\', '/')
        doc_info = engine.meta.get_doc_info(rel_path)
        if doc_info and doc_info.get("hash") == "":
            degraded_files.append(rel_path)
            
    if degraded_files:
        logger.warning(f"⚠️ [诊断简报] 发现 {len(degraded_files)} 篇文章在同步时触发了安全降级 (可能是 AI 幻觉或超时，已保留原文)。")
        logger.warning("   └── 💡 建议抽查以下文件 (下次重新启动引擎时，会自动尝试重试补全):")
        for i, df in enumerate(degraded_files[:5]):
            logger.warning(f"       {i+1}. {df}")
        if len(degraded_files) > 5:
            logger.warning(f"       ... 等共 {len(degraded_files)} 篇")
        
        if args.watch:
            logger.info("👀 同步阶段结束，正在转入后台实时守护...")
        else:
            logger.info("🛑 单次同步任务已执行完毕，引擎即将安全下线。")
    else:
        if args.watch:
            logger.info("✨ 完美收官: 所有文章均以最高质量通过管线！正在转入后台实时守护。")
        else:
            logger.info("✨ 完美收官: 所有文章均以最高质量通过管线！单次同步任务已执行完毕，引擎即将安全下线。")