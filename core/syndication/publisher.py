#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Publisher Service
模块职责：全域发布生命周期调度。
🛡️ [AEL-Iter-v11.0]：将资产推送至外部生态的中央指挥部。
"""

import logging
from typing import Dict, Any, List
from ..adapters.egress.publishers import PublisherRegistry

from core.utils.tracing import tlog

class PublisherService:
    """
    🏗️ 全域发布调度中心
    负责接收同步完成信号，并协调各注册渠道执行物理发布。
    """
    def __init__(self, config: Dict[str, Any], sys_tuning: Dict[str, Any] = None):
        self.config = config
        self.sys_tuning = sys_tuning or {}
        self.active_publishers = []

        # 🚀 自动化发现并初始化已配置的发布器
        self._initialize_publishers()

    def _initialize_publishers(self):
        """扫描配置并激活对应的发布插件"""
        publish_cfg = self.config.get("publish_control", {})
        # 支持多种发布模式：direct_upload, git_sync 等
        # 目前优先处理 direct_upload 下的子项
        direct_cfg = publish_cfg.get("direct_upload", {})

        for name, cfg in direct_cfg.items():
            if cfg.get("enabled", False):
                pub_cls = PublisherRegistry.get_publisher(name)
                if pub_cls:
                    self.active_publishers.append(pub_cls(cfg, self.sys_tuning))
                    tlog.debug(f"📡 [发布中心] 已激活直传通道: {name}")
                else:
                    tlog.warning(f"⚠️ [发布中心] 无法找到发布器插件: {name}")

    def run_syndication(self, bundle_path: str, metadata: Dict[str, Any], ledger=None):
        """
        🚀 触发广播发布
        :param bundle_path: 待发布的物理路径
        :param metadata: 同步上下文元数据
        :param ledger: 主权账本实例 (用于状态记录)
        """
        if not self.active_publishers:
            return

        tlog.info(f"🚀 [发布中心] 正在向 {len(self.active_publishers)} 个渠道分发资产...")

        results = []
        rel_path = metadata.get("rel_path") # 如果是单文档发布，提取相对路径
        
        for pub in self.active_publishers:
            pub_name = getattr(pub, 'name', pub.__class__.__name__)
            try:
                res = pub.push(bundle_path, metadata)
                results.append(res)
                
                # 🛡️ [V35.2] 事务反馈：记录成功状态
                if ledger and rel_path:
                    ledger.update_egress_status(rel_path, pub_name, "SUCCESS")
            except Exception as e:
                tlog.error(f"❌ [发布中心] 渠道 {pub_name} 分发异常: {e}")
                results.append({"status": "error", "message": str(e)})
                
                # 🛡️ [V35.2] 事务反馈：记录失败状态
                if ledger and rel_path:
                    ledger.update_egress_status(rel_path, pub_name, "FAILED", error=str(e))

        return results


    def bind_to_bus(self, bus):
        """将发布逻辑绑定至系统事件总线"""
        @bus.on("SYNC_COMPLETED")
        def handle_sync_completed(stats=None, **kwargs):
            # 只有非 dry-run 模式下才执行真实发布
            if kwargs.get("is_dry_run"):
                tlog.info("🧪 [发布中心] 侦测到模拟模式，拦截物理分发。")
                return

            # [Sovereignty] 默认发布逻辑：根据配置分发至 SSG 目录或影子库
            output_path = self.config.get("output_paths", {}).get("markdown_dir", "")
            # 处理路径占位符
            active_theme = self.config.get("active_theme", "docusaurus")
            output_path = output_path.replace("{theme}", active_theme)

            if os.path.exists(output_path):
                # 🚀 [V10.5] 导出全域站点地图 (Sitemap Sovereignty)
                try:
                    from core.logic.sitemap_engine import SitemapGenerator
                    # 此处需要获取 engine 实例。由于 handle_sync_completed 在闭包中，
                    # 我们可以通过 kwargs 传递，或者在这里直接利用全局单例。
                    # 考虑到组件装配，我们在 assemble_components 时已绑定。
                    engine = kwargs.get("engine")
                    if engine:
                        # 🚀 [V16.8] 性能优化：只有在物理更新（UPDATED > 0）时才重新生成站点地图
                        if stats and stats.get('UPDATED', 0) > 0:
                            generator = SitemapGenerator(engine)
                            # 使用事件总线传回来的快照，防止重新扫描 DB
                            generator.generate(all_docs_snapshot=kwargs.get("all_docs_snapshot"))
                        else:
                            tlog.debug("✨ [发布服务] 侦测到内容指纹无变化，跳过站点地图生成。")
                except Exception as e:
                    tlog.error(f"🛑 [发布服务] 站点地图生成失败: {e}")

                self.run_syndication(output_path, {"ael_iter_id": "v11.0"}, ledger=engine.ledger if engine else None)
            else:
                tlog.warning(f"⚠️ [发布中心] 无法找到待发布目录: {output_path}")

        @bus.on("DOCUMENT_PUBLISHED")
        def handle_document_published(doc_path=None, engine=None, **kwargs):
            """🛡️ [V35.2] 支持单文档即时分发事务"""
            if doc_path and engine:
                tlog.debug(f"📡 [发布中心] 侦测到单文档发布信号: {doc_path}")
                # 此处可根据配置决定是否开启“即时分发”
                # self.run_syndication(doc_path, {"rel_path": doc_path}, ledger=engine.ledger)


import os # 为了处理路径
