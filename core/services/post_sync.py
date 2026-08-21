#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Service - Post-Sync Registry & Lifecycle Manager
模块职责：负责管理同步任务完成后的所有自动化下游插件。
🛡️ [AEL-Iter-v1.0]：生命周期主权隔离引擎。
"""

import abc
import traceback
from typing import List, Any, Dict
from core.utils.tracing import tlog
from core.utils.event_bus import bus

class PostSyncTask(metaclass=abc.ABCMeta):
    """🚀 [V1.0] 下游插件抽象基类"""
    @abc.abstractmethod
    def run(self, engine, stats: Dict[str, Any], snapshot: Dict[str, Any], args: Any):
        pass

    @property
    def name(self):
        return self.__class__.__name__

class LifecycleManager:
    _tasks: List[PostSyncTask] = []

    @classmethod
    def register(cls, task: PostSyncTask):
        """注册一个新的生命周期插件"""
        cls._tasks.append(task)
        tlog.debug(f"📡 [Lifecycle] 已挂载下游任务插件: {task.name}")

    @classmethod
    def execute_all(cls, engine, stats, snapshot, args):
        """⚡ 按顺序执行所有已注册的插件 (具备异常隔离能力)"""
        tlog.info(f"⚡ [Lifecycle] 正在点火 {len(cls._tasks)} 个下游插件...")
        
        for task in cls._tasks:
            try:
                start_time = time.perf_counter()
                task.run(engine, stats, snapshot, args)
                elapsed = time.perf_counter() - start_time
                tlog.info(f"✅ [Plugin] {task.name} 执行完毕 | 耗时: {elapsed:.3f}s")
            except Exception as e:
                tlog.error(f"🚨 [Plugin Error] {task.name} 发生故障: {e}")
                tlog.debug(traceback.format_exc())

# 🚀 [V1.0] 内置付印插件定义
# ============================================================
# 以下插件构成了 Illacme-Plenipes 的核心自动化交付管线。
# 每个插件均独立运行，具备异常隔离能力，确保单一环节失败不影响全链路付印。
# ============================================================

import os
import json
from datetime import datetime
from core.editorial.vault_indexer import VaultIndexer

class GraphExportPlugin(PostSyncTask):
    """
    关系图谱导出插件
    职责：基于 Manuscripts (原稿库) 的双链引用，生成全局关系图谱 JSON。
    该资产是 Digital Garden 可视化的核心数据源。
    """
    def run(self, engine, stats: Dict[str, Any], snapshot: Dict[str, Any], args: Any):
        # 🚀 [V55.26] 路径主权对正：使用配置助手解析物理路径
        output = engine._resolve_path(engine.config.get_link_graph_path())
        VaultIndexer.export_graph(engine.link_graph, output)

class SearchIndexPlugin(PostSyncTask):
    """
    全域搜索索引导出插件
    职责：构建基于正文与元数据的扁平化检索索引，支持全局快速搜索。
    """
    def run(self, engine, stats: Dict[str, Any], snapshot: Dict[str, Any], args: Any):
        # 🚀 [V55.26] 路径主权对正：使用配置助手解析物理路径
        output = engine._resolve_path(engine.config.get_search_index_path())
        VaultIndexer.export_search_index_v2(snapshot, output, engine=engine)

class SyncStatsPlugin(PostSyncTask):
    """
    同步统计数据保存插件
    职责：记录本次付印周期的元数据统计，包括算力消耗、文件总数及时间戳。
    """
    def run(self, engine, stats: Dict[str, Any], snapshot: Dict[str, Any], args: Any):
        # 🚀 [V55.26] 路径主权对正：使用配置助手解析物理路径
        output = engine._resolve_path(engine.config.get_sync_stats_path())
        
        # 🚀 [V7.0] 从注册簿 (The Registry) 获取权威财务数据，确保每一分算力都有据可查
        historical_cost = engine.ledger.get_total_cost(imprint_id=engine.imprint_id)
        
        sync_data = {
            "total_vault_files": len(snapshot),
            "processed_timestamp": datetime.now().isoformat(),
            "engine_version": "V50.3",
            "imprint": engine.imprint_id,
            "usage": {
                "session_cost": round((engine.meter.stats.get("session", {}).get("cost", 0.0)), 4),
                "total_historical_cost": round(historical_cost, 2)
            }
        }

        os.makedirs(os.path.dirname(output), exist_ok=True)
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(sync_data, f, indent=2)

class AssetAuditPlugin(PostSyncTask):
    """
    物理资产交叉审计插件
    职责：执行“首席校对员”职能，核实原稿库中引用的所有本地及远程资产的可用性。
    """
    def run(self, engine, stats, snapshot, args):
        if not engine.config.system.enable_asset_audit:
            return

        missing_local = []
        remote_to_check = []
        
        for rel_path in snapshot.keys():
            doc_info = engine.meta.get_doc_info(rel_path)
            if not doc_info: continue
            
            # 本地源资产审计：核实文件是否存在于 Vault 的 assets 目录中
            assets = doc_info.get('assets', [])
            vault_assets_root = os.path.join(engine.vault_root, "assets")
            for asset in assets:
                if str(asset).startswith(('http://', 'https://', '//')): continue
                # 归一化路径以支持跨平台识别
                normalized_asset = os.path.normpath(asset)
                abs_asset = os.path.join(vault_assets_root, normalized_asset)
                if not os.path.exists(abs_asset):
                    missing_local.append((rel_path, asset))
            
            # 远程资产探测准备
            ext_assets = doc_info.get('ext_assets', [])
            for url in ext_assets:
                remote_to_check.append((rel_path, url))

        # 远程资产并发探测
        dead_remote = []
        if remote_to_check:
            from concurrent.futures import ThreadPoolExecutor, as_completed
            import requests
            from urllib.parse import urlparse
            import threading
            
            def ping(doc_path, url):
                ignored = engine.config.system.network_settings.ignored_domains
                if any(d in url for d in (ignored or [])): return None
                
                domain = urlparse(url).netloc
                if not hasattr(engine, '_audit_locks'): engine._audit_locks = {}
                if domain not in engine._audit_locks: engine._audit_locks[domain] = threading.Lock()
                
                with engine._audit_locks[domain]:
                    time.sleep(engine.config.system.network_settings.prober_cooling_delay)
                    try:
                        headers = {'User-Agent': engine.config.system.network_settings.asset_prober_ua}
                        timeout = engine.config.system.resilience.asset_ping_timeout
                        resp = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
                        if resp.status_code in [404, 410, 500, 502, 503]:
                            return (doc_path, url, f"HTTP {resp.status_code}")
                    except Exception: return (doc_path, url, "超时/连接失败")
                return None

            workers = engine.config.system.concurrency.audit_workers
            with ThreadPoolExecutor(max_workers=workers) as p:
                futures = [p.submit(ping, d, u) for d, u in remote_to_check]
                for f in as_completed(futures):
                    res = f.result()
                    if res: dead_remote.append(res)

        bus.emit("UI_AUDIT_RESULTS", missing_local=missing_local, dead_remote=dead_remote, total_files=len(snapshot))

class JanitorPlugin(PostSyncTask):
    """
    清道夫：资产清洗插件
    职责：物理级别的垃圾回收。清理无效的索引节点、孤立资产以及过期的分发快照。
    """
    def run(self, engine, stats, snapshot, args):
        no_changes = (stats.get("UPDATED", 0) == 0 and stats.get("ERROR", 0) == 0 and not args.force)
        if not no_changes:
            tlog.info("🧹 [Lifecycle] 检测到变更，正在启动 Janitor 清洗...")
            engine.janitor.gc_orphans(set(snapshot.keys()), is_dry_run=args.dry_run)
            engine.janitor.gc_ghost_nodes(is_dry_run=args.dry_run)
            
            # 🚀 [V35.2] 物理自愈清理：确保在最终付印前 dist 目录绝对纯净
            engine.janitor.purge_dist(is_dry_run=args.dry_run)


class DigitalGardenPlugin(PostSyncTask):
    """
    数字花园图谱导出插件 (全量语种支持)
    职责：为全语种矩阵生成多维关联索引。
    """
    def run(self, engine, stats, snapshot, args):
        # 🚀 [V34.9] 只有在有变更或非强制模式下才执行昂贵的导出
        has_changes = not (stats.get("UPDATED", 0) == 0 and stats.get("ERROR", 0) == 0 and not (args and args.force))
        if not has_changes:
            tlog.info("✨ [Plugin] 数字花园数据无变更，跳过导出。")
            return

        from core.bindery.garden_exporter import export_digital_garden
        export_digital_garden(engine, all_docs_snapshot=snapshot)

class SovereignDeploymentPlugin(PostSyncTask):
    """
    🚀 [V35.2] 全渠道主权分发插件
    职责：执行最终的出版资产投递，将印刷好的印张上架至全球书店 (The Bookstore)。
    """
    def run(self, engine, stats: Dict[str, Any], snapshot: Dict[str, Any], args: Any):
        # 1. 只有在非 dry_run、非 local_only 且有实际产出（或强制模式）时执行
        if getattr(args, 'local_only', False):
            tlog.info("ℹ️ [Deployment] 当前处于发布预览模式 (local_only)，已完成本地静态装帧，跳过全网外部渠道推流。")
            bus.emit("UI_TERMINAL_DATA", type="LOG", data="⚡ [发布预览] 本地装帧与静态编译已就绪，跳过全网外部渠道推流。")
            return

        has_output = stats.get("UPDATED", 0) > 0 or (args and args.force)
        if (args and args.dry_run) or not has_output:
            tlog.info("ℹ️ [Deployment] 无新增产出或处于演练模式，跳过渠道投递。")
            return

        if not hasattr(engine, 'deployment_manager') or not engine.deployment_manager:
            tlog.debug("ℹ️ [Deployment] 引擎未挂载分发调度员。")
            return

        # 2. 获取分发根目录 (通常是 site_dir)
        bundle_path = (engine.paths or {}).get('site_dir') or (engine.paths or {}).get('target_base')
        
        # 🛡️ [物理自愈纠偏] 确保 bundle_path 指向真实的静态网页编译成品目录，而非 Markdown 原文目录
        if bundle_path:
            import os
            has_index = os.path.exists(os.path.join(bundle_path, "index.html"))
            is_source_dir = "src/content" in bundle_path.replace("\\", "/") or (
                os.path.exists(os.path.join(bundle_path, "configs")) and os.path.exists(os.path.join(bundle_path, "themes"))
            )
            if not has_index or is_source_dir:
                # 尝试寻找 themes/{theme}/dist 真实的静态成品根目录
                themes_root = (engine.paths or {}).get('themes') or os.path.join(os.getcwd(), "themes")
                theme_dist = os.path.join(themes_root, engine.active_theme or "default", "dist")
                if os.path.exists(theme_dist) and os.path.exists(os.path.join(theme_dist, "index.html")):
                    tlog.warning(f"⚠️ [物理纠偏] 侦测到发布源路径 {bundle_path} 异常（缺少网页入口或指向源码目录），系统已智能自动将其重定向至主题静态成品目录: {theme_dist}")
                    bundle_path = theme_dist

        # 3. 准备全局分发元数据
        deployment_meta = {
            "timestamp": datetime.now().isoformat(),
            "imprint_id": engine.imprint_id,
            "stats": stats,
            "total_files": len(snapshot)
        }

        # 4. 执行全渠道事务分发
        results = engine.deployment_manager.deploy_all(bundle_path, deployment_meta)
        
        # 5. 记录分发凭证至注册簿 (Registry)
        engine.ledger.log("GLOBAL_DEPLOY", f"全渠道分发完成，状态: {(results or {}).get('status')}",
                          imprint_id=engine.imprint_id, metadata=results)


class BlogIndexGeneratorPlugin(PostSyncTask):
    """
    🚀 [V1.0] 博客归档动态聚合生成插件 (零文库污染)
    职责：自动扫描文库中的所有博文，为 Universal 及各主题动态聚合生成现代化博客首页。
    """
    def run(self, engine, stats: Dict[str, Any], snapshot: Dict[str, Any], args: Any):
        try:
            from core.adapters.egress.ssg.generic_templates import generate_dynamic_blog_archive
            generate_dynamic_blog_archive(engine, snapshot=snapshot)
        except Exception as e:
            tlog.warning(f"⚠️ [BlogIndexGeneratorPlugin] 博客归档聚合跳过: {e}")


# 🚀 自动注册内置插件 (注意顺序：Janitor 清理在前，分发在后)
LifecycleManager.register(GraphExportPlugin())
LifecycleManager.register(SearchIndexPlugin())
LifecycleManager.register(SyncStatsPlugin())
LifecycleManager.register(AssetAuditPlugin())
LifecycleManager.register(BlogIndexGeneratorPlugin())
LifecycleManager.register(JanitorPlugin())
LifecycleManager.register(DigitalGardenPlugin())
LifecycleManager.register(SovereignDeploymentPlugin())


import time

