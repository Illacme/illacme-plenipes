#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 [V112.1] Illacme Plenipes - Pipeline Hosting Pusher Shard
职责：定向全站托管渠道的物理部署与 Egress 状态回填。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
"""

import os
from core.utils.tracing import tlog

def push_to_hosting_channel(engine, doc_id: str, doc_info: dict, target_channel: str, direct_upload: dict) -> None:
    """🚀 [定向全站托管单篇物理推送]"""
    matching_pub = None
    if hasattr(engine, "publisher") and engine.publisher:
        matching_pub = next((p for p in engine.publisher.active_publishers if getattr(p, 'PLUGIN_ID', None) == target_channel or getattr(p, 'name', p.__class__.__name__) == target_channel), None)
    
    # 动态按需实例化按需托管通道 (On-Demand Dynamic Instantiation)
    if not matching_pub:
        from core.adapters.egress.publishers import PublisherRegistry
        pub_cls = PublisherRegistry.get_publisher(target_channel)
        if pub_cls:
            chan_cfg = direct_upload.get(target_channel, {}) if isinstance(direct_upload, dict) else (getattr(direct_upload, target_channel, {}) or {})
            if hasattr(chan_cfg, "__dict__"):
                chan_cfg = chan_cfg.__dict__
            elif hasattr(chan_cfg, "dict"):
                chan_cfg = chan_cfg.dict()
            elif not isinstance(chan_cfg, dict):
                chan_cfg = {}
            sys_tuning = getattr(engine.publisher, "sys_tuning", {}) if (hasattr(engine, "publisher") and engine.publisher) else {"vault_root": getattr(engine, "vault_root", os.getcwd())}
            try:
                matching_pub = pub_cls(chan_cfg, sys_tuning)
                tlog.info(f"✨ [分发中枢] 已动态按需激活托管通道: {target_channel}")
            except Exception as ie:
                tlog.warning(f"⚠️ [分发中枢] 实例化托管通道 {target_channel} 异常: {ie}")

    if matching_pub:
        tlog.info(f"🚀 [分发中枢] 正在将 {doc_id} 独立物理推送至托管渠道: {target_channel}...")
        engine.meta.update_egress_status(doc_id, target_channel, "syncing")
        
        # 🚀 [V112.1] 遵照治理中心装帧主题设定与路径契约 (Engine Path Resolver & SSG Adapter Contract) 锚定静态产物发布包
        bundle_path = None
        if hasattr(engine, "paths") and isinstance(engine.paths, dict):
            bundle_path = engine.paths.get("site_dir") or engine.paths.get("target_base")

        if not bundle_path or not os.path.exists(bundle_path):
            imprint_id = getattr(engine.config, "active_imprint", "default") or "default"
            theme = getattr(engine.config, "active_theme", "default") or "default"
            
            # 优先从当前装帧主题的 SSG 插件适配器接口直接查询原生输出目录 (如 Starlight/Astro -> dist, Docusaurus -> build)
            ssg_site_dir = "dist"
            if hasattr(engine, "ssg_adapter") and engine.ssg_adapter and hasattr(engine.ssg_adapter, "get_site_dir"):
                ssg_site_dir = engine.ssg_adapter.get_site_dir()
                
            paths_cfg = getattr(engine.config, "output_paths", {}) or {}
            site_dir_cfg = (paths_cfg.get("site_dir") if isinstance(paths_cfg, dict) else getattr(paths_cfg, "site_dir", ssg_site_dir)) or ssg_site_dir
            resolved_site_dir = site_dir_cfg.replace("{theme}", theme)

            # 规范契约寻址：品牌专属主题 > 治理中心装帧主题 > 全局静态输出
            candidates = [
                os.path.abspath(os.path.join("imprints", imprint_id, "themes", theme, resolved_site_dir)),
                os.path.abspath(os.path.join("themes", theme, resolved_site_dir)),
                os.path.abspath(os.path.join("imprints", imprint_id, resolved_site_dir)),
                os.path.abspath(resolved_site_dir)
            ]
            bundle_path = next((p for p in candidates if os.path.exists(p)), candidates[1] if os.path.exists(candidates[1]) else candidates[0])
        
        try:
            metadata = {
                "rel_path": doc_id,
                "title": doc_info.get("title", "Untitled"),
                "slug": doc_info.get("slug") or ""
            }
            res = matching_pub.push(bundle_path, metadata)
            
            # 🛡️ [V89.9] 严格核验发布状态，杜绝静默假成功隐患
            if isinstance(res, dict) and res.get("status") != "success":
                raise RuntimeError(res.get("message") or "对端托管服务器部署失败")
                
            # 物理提取具体的发布 URL 传入 update_egress_status
            deploy_url = res.get("url") if isinstance(res, dict) else None
            engine.meta.update_egress_status(doc_id, target_channel, "SUCCESS", url=deploy_url)
            engine.meta.save()
        except Exception as pe:
            tlog.error(f"❌ [分发中枢] 定向托管物理部署失败: {pe}")
            engine.meta.update_egress_status(doc_id, target_channel, "FAILED", error=str(pe))
            engine.meta.save()
    else:
        tlog.warning(f"⚠️ [分发中枢] 未能找到已激活的托管通道: {target_channel}")
