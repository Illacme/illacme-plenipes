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

# 🚀 [V1.0] 内置插件定义
import os
import json
from datetime import datetime
from core.pipeline.vault_indexer import VaultIndexer

class GraphExportPlugin(PostSyncTask):
    """关系图谱导出插件"""
    def run(self, engine, stats: Dict[str, Any], snapshot: Dict[str, Any], args: Any):
        # 🚀 [V22.6] 路径主权：直接使用引擎解析器
        output = engine._resolve_path("data/index/{id}/link_graph.json".replace("{id}", engine.territory_id))
        VaultIndexer.export_graph(engine.link_graph, output)

class SearchIndexPlugin(PostSyncTask):
    """全域搜索索引导出插件"""
    def run(self, engine, stats: Dict[str, Any], snapshot: Dict[str, Any], args: Any):
        # 🚀 [V22.6] 路径主权：直接使用引擎解析器
        output = engine._resolve_path("data/index/{id}/search_index.json".replace("{id}", engine.territory_id))
        VaultIndexer.export_search_index_v2(snapshot, output)

class SyncStatsPlugin(PostSyncTask):
    """同步统计数据保存插件"""
    def run(self, engine, stats: Dict[str, Any], snapshot: Dict[str, Any], args: Any):
        # 🚀 [V22.6] 路径主权：直接使用引擎解析器
        output = engine._resolve_path("data/index/{id}/sync_stats.json".replace("{id}", engine.territory_id))
        
        # 🚀 [V7.0] 从审计账本获取权威财务数据
        historical_cost = engine.ledger.get_total_cost(territory_id=engine.territory_id)
        
        sync_data = {
            "total_vault_files": len(snapshot),
            "processed_timestamp": datetime.now().isoformat(),
            "engine_version": "V16.0",
            "territory": engine.territory_id,
            "usage": {
                "session_cost": round(engine.meter.stats["session"]["cost"], 4),
                "total_historical_cost": round(historical_cost, 2)
            }
        }

        os.makedirs(os.path.dirname(output), exist_ok=True)
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(sync_data, f, indent=2)

class AssetAuditPlugin(PostSyncTask):
    """物理资产交叉审计插件"""
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
                if any(d in url for d in ignored): return None
                
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
    """清道夫：资产清洗插件"""
    def run(self, engine, stats, snapshot, args):
        no_changes = (stats.get("UPDATED", 0) == 0 and stats.get("ERROR", 0) == 0 and not args.force)
        if not no_changes:
            tlog.info("🧹 [Lifecycle] 检测到变更，正在启动 Janitor 清洗...")
            engine.janitor.gc_orphans(set(snapshot.keys()), is_dry_run=args.dry_run)
            engine.janitor.gc_ghost_nodes(is_dry_run=args.dry_run)
            
            # 🚀 [V35.2] 物理自愈清理：确保分发前 dist 目录绝对纯净
            engine.janitor.purge_dist(is_dry_run=args.dry_run)


class DigitalGardenPlugin(PostSyncTask):
    """数字花园图谱导出插件 (全量语种支持)"""
    def run(self, engine, stats, snapshot, args):
        # 🚀 [V34.9] 只有在有变更或非强制模式下才执行昂贵的导出
        has_changes = not (stats.get("UPDATED", 0) == 0 and stats.get("ERROR", 0) == 0 and not args.force)
        if not has_changes:
            tlog.info("✨ [Plugin] 数字花园数据无变更，跳过导出。")
            return

        from core.dispatch.garden_exporter import export_digital_garden
        export_digital_garden(engine, all_docs_snapshot=snapshot)

class SovereignDeploymentPlugin(PostSyncTask):
    """🚀 [V35.2] 全渠道主权分发插件：执行最终的出版资产投递"""
    def run(self, engine, stats: Dict[str, Any], snapshot: Dict[str, Any], args: Any):
        # 1. 只有在非 dry_run 且有实际产出（或强制模式）时执行
        has_output = stats.get("UPDATED", 0) > 0 or args.force
        if args.dry_run or not has_output:
            tlog.info("ℹ️ [Deployment] 无新增产出或处于演练模式，跳过渠道投递。")
            return

        if not hasattr(engine, 'deployment_manager') or not engine.deployment_manager:
            tlog.debug("ℹ️ [Deployment] 引擎未挂载分发调度员。")
            return

        # 2. 获取分发根目录 (通常是 static_dir)
        bundle_path = engine.paths.get('static_dir') or engine.paths.get('target_base')
        
        # 3. 准备全局分发元数据
        deployment_meta = {
            "timestamp": datetime.now().isoformat(),
            "territory_id": engine.territory_id,
            "stats": stats,
            "total_files": len(snapshot)
        }

        # 4. 执行全渠道事务分发
        results = engine.deployment_manager.deploy_all(bundle_path, deployment_meta)
        
        # 5. 记录分发凭证至审计账本 (将结果存入 metadata 避免 details 参数冲突)
        engine.ledger.log("GLOBAL_DEPLOY", f"全渠道分发完成，状态: {results.get('status')}",
                          territory_id=engine.territory_id, metadata=results)


# 🚀 自动注册内置插件 (注意顺序：Janitor 清理在前，分发在后)
LifecycleManager.register(GraphExportPlugin())
LifecycleManager.register(SearchIndexPlugin())
LifecycleManager.register(SyncStatsPlugin())
LifecycleManager.register(AssetAuditPlugin())
LifecycleManager.register(JanitorPlugin())
LifecycleManager.register(DigitalGardenPlugin())
LifecycleManager.register(SovereignDeploymentPlugin())


import time
