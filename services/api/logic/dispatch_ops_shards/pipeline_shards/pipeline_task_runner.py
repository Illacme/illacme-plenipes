#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
♻️ [V112.0] Illacme Plenipes - Pipeline Task Runner Shard
职责：异步重分发任务执行逻辑、算力熔断门禁与待同步渠道扫描。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
"""

import os
from core.logic.orchestration.task_orchestrator import global_executor, TaskPriority
from core.utils.tracing import tlog
from .pipeline_hosting_pusher import push_to_hosting_channel
from .pipeline_syndicate_loader import get_enabled_syndication_channels, load_syndication_content_and_metadata

def _async_redispatch_task(engine, task_path, prefix, src_rel, target_slot, clear_cache, doc_id, target_channel=None, skip_syndication=False):
    enabled_syndication_channels = []
    try:
        # 🚀 [V112.0] 物理性能与算力保护解耦：若指定了 target_channel (单篇社交广播)，跳过全站 SSG/AI 翻译管线
        syndication_cfg = getattr(engine.config, "syndication", {}) or {}
        direct_upload = getattr(engine.config.publish_control, "direct_upload", {}) or {}
        
        is_targeted_syndication = False
        if target_channel and target_channel in syndication_cfg:
            is_targeted_syndication = True
            
        if not is_targeted_syndication:
            # 仅在非定向社交广播时，才编译生成本地网页与触发 AI 跨语种同步
            engine.sync_document(
                task_path, prefix, src_rel,
                False,  # is_dry_run
                True,   # force_sync (强制重新发布)
                is_sandbox=False,
                target_slot=target_slot,
                clear_cache=clear_cache
            )
        else:
            tlog.info(f"⚡ [单篇社交广播] 定向广播至 {target_channel}，免除全站 SSG 与 LLM AI 翻译管线重编。")
        
        # 2. 获取编译后的文档最新元数据
        doc_info = engine.meta.get_doc_info(doc_id) or {}
        if not doc_info and os.path.exists(os.path.join(engine.vault_root, doc_id)):
            # 物理 Fallback 保障：若账本尚未收录，从物理 Frontmatter 直接解包
            with open(os.path.join(engine.vault_root, doc_id), 'r', encoding='utf-8') as f:
                raw_c = f.read()
            from core.utils import extract_frontmatter
            fm, _ = extract_frontmatter(raw_c)
            doc_info = {"title": fm.get("title", os.path.basename(doc_id)), "slug": fm.get("slug", "")}

        # 检测 target_channel 是否属于 Hosting 全站托管渠道
        is_target_hosting = False
        if isinstance(direct_upload, dict):
            is_target_hosting = (target_channel in direct_upload)
        elif hasattr(direct_upload, "__dict__"):
            is_target_hosting = hasattr(direct_upload, target_channel)

        if target_channel and is_target_hosting:
            push_to_hosting_channel(engine, doc_id, doc_info, target_channel, direct_upload)
            return

        # 🚀 [V110.1] 强制重译/重编译跳过分发渠道：若显示请求 skip_syndication，完成本地网页重编译后即可退出
        if skip_syndication:
            tlog.info(f"💡 [分发中枢] {doc_id} 属于本地重译/编译任务，已跳过外部分发渠道同步。")
            return

        # 3. 🚀 [物理分发全渠道/单通道联动]
        enabled_syndication_channels = get_enabled_syndication_channels(syndication_cfg, target_channel)
        if not enabled_syndication_channels:
            return

        broadcast_title, body, fm = load_syndication_content_and_metadata(
            engine, doc_id, doc_info, target_slot
        )

        site_url = getattr(engine.config, "site_url", "")
        sys_tuning = {"vault_root": getattr(engine, "vault_root", os.getcwd())}
        
        from core.syndication.hub import ContentSyndicator
        syndicator = ContentSyndicator(
            syndication_cfg=syndication_cfg,
            site_url=site_url,
            sys_tuning_cfg=sys_tuning,
            meta=engine.meta
        )
        
        source_lang = (doc_info.get("source_lang") or "zh").lower()
        target_slot_str = str(target_slot).lower() if target_slot else source_lang
        
        # 记录正在分发状态 (显式把上一轮的 url 设为空，防止继承 404 草稿旧地址)
        for chan_id, _ in enabled_syndication_channels:
            engine.meta.update_egress_status(doc_id, chan_id, "syncing", url="")
        engine.meta.save()
            
        tlog.info(f"📡 [分发中枢] 正在将 {doc_id} ({target_slot_str}) 联动分发至 {len(enabled_syndication_channels)} 个分发渠道...")
        
        # 临时过滤分发插件数组，使其仅保留我们定向需要的分发渠道
        target_channel_ids = [c[0] for c in enabled_syndication_channels]
        syndicator.plugins = [p for p in syndicator.plugins if getattr(p, 'PLUGIN_ID', p.__class__.__name__) in target_channel_ids]

        # 执行分发 (强注入 force_push=True 以绕过 Hash 重复抑制，并显式传入目标语种 lang_code)
        syndicator.syndicate(
            title=broadcast_title,
            slug=doc_info.get("slug") or "",
            content=body,
            metadata=fm,
            rel_path=doc_id,
            lang_code=target_slot_str,
            trigger_global_retry=False,
            force_push=True
        )
    except Exception as e:
        tlog.error(f"❌ [手动重调度联动异常] 物理分发 {doc_id} 失败: {e}")
        if enabled_syndication_channels:
            for chan_id, _ in enabled_syndication_channels:
                engine.meta.update_egress_status(doc_id, chan_id, "FAILED", error=str(e))
            engine.meta.save()

def trigger_re_dispatch_logic(engine, doc_id: str, req: dict) -> dict:
    """
    ♻️ 主权调度中心：强制推入出版管线
    """
    try:
        # 🚀 物理对正与调度准备：通过扫描模块自动感应本文件的物理信道属性与槽位
        from core.runtime.orchestration.scanner import build_task_queue
        task_queue, _ = build_task_queue(engine, [doc_id])
        if not task_queue:
            return {"success": False, "message": f"未能在当前品牌的频道矩阵中匹配到该稿件: {doc_id}"}
            
        task_path, prefix, src_rel, default_slot = task_queue[0]
        clear_cache = bool(req.get("clear_cache", False))
        target_channel = req.get("target_channel")
        # 🚀 [V113.5] 优先使用前端显式选择的目标语种 target_slot，严防被扫描器的默认母语槽位覆盖吞掉
        target_slot = req.get("target_slot") or req.get("target_lang") or req.get("slot") or default_slot
        skip_syndication = bool(req.get("skip_syndication", clear_cache if not target_channel else False))

        # 🛡️ [V76.8] 翻译矩阵与算力可用性强关联校验熔断门禁 (同步拦截)
        # 🚀 [V113.0] 单篇社交广播定向分发时，完全跳过 AI 算力校验 (无需 LLM 翻译)
        syndication_cfg = getattr(engine.config, "syndication", {}) or {}
        if hasattr(syndication_cfg, "model_dump"):
            syndication_cfg = syndication_cfg.model_dump()
        elif not isinstance(syndication_cfg, dict):
            syndication_cfg = getattr(syndication_cfg, "__dict__", {})
        is_targeted_syndication = bool(target_channel and target_channel in syndication_cfg)
        if not is_targeted_syndication:
            try:
                from core.governance.checks.ai import check_ai_availability_or_raise
                check_ai_availability_or_raise(engine)
            except RuntimeError as e:
                return {"success": False, "message": str(e)}
        
        # 提交至主权线程池以进行异步物理编译，彻底避免对 FastAPI 事件循环的阻塞
        global_executor.submit(
            _async_redispatch_task,
            engine, task_path, prefix, src_rel, target_slot, clear_cache, doc_id, target_channel, skip_syndication,
            priority=TaskPriority.INGRESS,
            task_name=f"Manual-Redispatch-{os.path.basename(task_path)}"
        )
        return {"success": True, "message": f"资产 {doc_id} 的重编译/分发任务已受理。"}
    except Exception as e:
        import traceback
        tlog.error(f"❌ [手动重调度异常]: {e}\n{traceback.format_exc()}")
        return {"success": False, "message": f"调度失败: {str(e)}"}

def get_pending_syndication_logic(engine) -> dict:
    """
    渠道系统扫描：扫描全账本，找出已启用的分发渠道中，状态不为 SUCCESS 的待同步文档列表
    """
    if not hasattr(engine, "meta"):
        return {"count": 0, "pending_docs": []}
        
    config = engine.config
    
    # 提取已启用的分发同步渠道
    syndication_cfg = getattr(config, "syndication", {}) or {}
    if hasattr(syndication_cfg, "model_dump"):
        syndication_cfg = syndication_cfg.model_dump()
    elif not isinstance(syndication_cfg, dict):
        syndication_cfg = getattr(syndication_cfg, "__dict__", {})
        
    enabled_syndication_channels = []
    for chan_id, chan_cfg in syndication_cfg.items():
        if isinstance(chan_cfg, dict) and chan_cfg.get("enabled"):
            enabled_syndication_channels.append(chan_id)
            
    if not enabled_syndication_channels:
        return {"count": 0, "pending_docs": []}
        
    # 读取账本中所有的文档
    raw_docs = engine.meta.sqlite.get_all_documents() or []
    if isinstance(raw_docs, dict):
        all_docs = list(raw_docs.values())
    elif isinstance(raw_docs, list):
        all_docs = raw_docs
    else:
        all_docs = []
        
    pending_docs = []
    
    for doc in all_docs:
        if not isinstance(doc, dict):
            continue
        rel_path = doc.get("rel_path")
        if not rel_path:
            continue
            
        publish_status = doc.get("publish_status", {})
        # 检测是否每个启用的分发渠道都成功同步了
        has_pending = False
        for chan in enabled_syndication_channels:
            status_info = publish_status.get(chan, {})
            status = str(status_info.get("status", "")).lower()
            if status not in ("success", "published", "done"):
                has_pending = True
                break
                
        if has_pending:
            pending_docs.append({
                "title": doc.get("title", "Untitled"),
                "rel_path": rel_path
            })
            
    return {
        "count": len(pending_docs),
        "pending_docs": pending_docs
    }
