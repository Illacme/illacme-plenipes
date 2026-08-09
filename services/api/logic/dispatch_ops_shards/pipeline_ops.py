#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 [V68.0] Illacme Plenipes - Dispatch Pipeline Shard
职责：管线异步重分发编译分发与物理销毁自愈。
"""

import os
from core.logic.orchestration.task_orchestrator import global_executor, TaskPriority
from core.utils.tracing import tlog

def _async_redispatch_task(engine, task_path, prefix, src_rel, target_slot, clear_cache, doc_id, target_channel=None, skip_syndication=False):
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
            # 🚀 [定向全站托管单篇物理推送]
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
            return

        # 🚀 [V110.1] 强制重译/重编译跳过分发渠道：若显示请求 skip_syndication，完成本地网页重编译后即可退出
        if skip_syndication:
            tlog.info(f"💡 [分发中枢] {doc_id} 属于本地重译/编译任务，已跳过外部分发渠道同步。")
            return

        # 3. 🚀 [物理分发全渠道/单通道联动]
        site_url = getattr(engine.config, "site_url", "")
        sys_tuning = {"vault_root": getattr(engine, "vault_root", os.getcwd())}
        
        # 找出已启用全局总开关或单篇手动指定的社交同步渠道
        enabled_syndication_channels = []
        for chan_id, chan_cfg in syndication_cfg.items():
            if isinstance(chan_cfg, dict):
                # 手动单篇定向广播时，只要该渠道在配置中有 api_key / token 凭据，直接放行支持定向广播
                has_cred = bool(chan_cfg.get("api_key") or chan_cfg.get("token") or chan_cfg.get("webhook_url"))
                is_match = not target_channel or chan_id == target_channel or chan_id.replace('_', '') == str(target_channel).replace('_', '')
                if is_match and (chan_cfg.get("enabled") or has_cred):
                    enabled_syndication_channels.append((chan_id, chan_cfg))
                
        if enabled_syndication_channels:
            from core.syndication.hub import ContentSyndicator
            syndicator = ContentSyndicator(
                syndication_cfg=syndication_cfg,
                site_url=site_url,
                sys_tuning_cfg=sys_tuning,
                meta=engine.meta
            )
            
            # 读取源文件内容
            source_path = os.path.join(engine.vault_root, doc_id)
            if os.path.exists(source_path):
                with open(source_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 剥离 frontmatter
                from core.utils import extract_frontmatter
                fm, body = extract_frontmatter(content)
                # 🚀 [V113.2] 标题优先级链：frontmatter.title > 账本.title > Untitled
                broadcast_title = fm.get("title") or doc_info.get("title") or "Untitled"

                # 🚀 [多语种译文广播适配] 若目标语种不等于母语，智能装载已就绪译文
                source_lang = (doc_info.get("source_lang") or "zh").lower()
                target_slot_str = str(target_slot).lower() if target_slot else source_lang
                
                if target_slot_str != source_lang:
                    translations = doc_info.get("translations", {}) if isinstance(doc_info.get("translations"), dict) else {}
                    target_trans = None
                    for k, v in translations.items():
                        if str(k).lower() == target_slot_str or str(k).lower().replace('-', '_') == target_slot_str.replace('-', '_'):
                            target_trans = v
                            break
                    if not target_trans and target_slot in translations:
                        target_trans = translations[target_slot]
                    
                    translated_body = None
                    translated_title = None
                    if isinstance(target_trans, dict):
                        translated_body = (
                            target_trans.get("translated_body") or
                            target_trans.get("content") or
                            target_trans.get("raw_markdown") or
                            target_trans.get("translated_markdown") or
                            target_trans.get("markdown") or
                            target_trans.get("body")
                        )
                        translated_title = (
                            target_trans.get("translated_title") or
                            target_trans.get("title") or
                            target_trans.get("og_title")
                        )
                        target_fm_dict = target_trans.get("frontmatter") or target_trans.get("metadata")
                        if isinstance(target_fm_dict, dict):
                            fm.update(target_fm_dict)

                    # 🚀 [途径 2: 磁盘产物候选路径探测 (Content Dir / Runtime Cache / Sources Cache)]
                    if not translated_body:
                        imprint_id = getattr(engine.config, "active_imprint", "default") or "default"
                        theme = getattr(engine.config, "active_theme", "default") or "default"
                        slug = doc_info.get("slug") or os.path.splitext(os.path.basename(doc_id))[0]
                        route_prefix = doc_info.get("route_prefix") or ""
                        sub_dir = doc_info.get("sub_dir") or ""

                        content_roots = []
                        if hasattr(engine, "paths") and isinstance(engine.paths, dict) and engine.paths.get("content_dir"):
                            content_roots.append(engine.paths.get("content_dir"))
                        
                        from core.config.config import IMPRINT_DIR
                        if IMPRINT_DIR:
                            content_roots.append(os.path.join(IMPRINT_DIR, imprint_id, "themes", theme, "src", "content"))
                        content_roots.append(os.path.join("imprints", imprint_id, "themes", theme, "src", "content"))
                        content_roots.append(os.path.join("themes", theme, "src", "content"))

                        target_md_candidates = []
                        for cr in content_roots:
                            if cr:
                                target_md_candidates.extend([
                                    os.path.join(cr, target_slot_str, route_prefix, sub_dir, f"{slug}.md"),
                                    os.path.join(cr, target_slot_str, "docs", target_slot_str, f"{slug}.md"),
                                    os.path.join(cr, target_slot_str, f"{slug}.md"),
                                    os.path.join(cr, target_slot_str, f"{os.path.splitext(os.path.basename(doc_id))[0]}.md")
                                ])
                        target_md_candidates.extend([
                            os.path.join(engine.vault_root, ".plenipes", "cache", "runtime", target_slot_str, route_prefix, sub_dir, f"{slug}.md"),
                            os.path.join(engine.vault_root, ".plenipes", "cache", "runtime", target_slot_str, "docs", target_slot_str, f"{slug}.md"),
                            os.path.join(engine.vault_root, ".plenipes", "cache", "runtime", target_slot_str, f"{slug}.md"),
                            os.path.join(engine.vault_root, ".plenipes", "cache", "sources", imprint_id, target_slot_str, route_prefix, sub_dir, f"{slug}.md"),
                            os.path.join(engine.vault_root, ".plenipes", "cache", "sources", imprint_id, target_slot_str, "docs", target_slot_str, f"{slug}.md"),
                            os.path.join(engine.vault_root, ".plenipes", "cache", "sources", imprint_id, target_slot_str, f"{slug}.md"),
                        ])
                        for cand_path in target_md_candidates:
                            if os.path.exists(cand_path):
                                try:
                                    with open(cand_path, 'r', encoding='utf-8') as cf:
                                        cand_content = cf.read()
                                    cand_fm, cand_body = extract_frontmatter(cand_content)
                                    if cand_body and cand_body.strip():
                                        translated_body = cand_body
                                        if cand_fm:
                                            fm.update(cand_fm)
                                            if cand_fm.get("title"):
                                                translated_title = cand_fm["title"]
                                        break
                                except Exception:
                                    pass

                    # 🚀 [途径 3: 段落级 Block Cache 自动组装还原]
                    if not translated_body and hasattr(engine, "block_cache") and engine.block_cache:
                        try:
                            from core.logic.block_parser import MarkdownBlockParser
                            parser = MarkdownBlockParser()
                            parsed_blocks = parser.parse(body)
                            assembled_blocks = []
                            all_cached = True
                            for blk in parsed_blocks:
                                c_str = blk.content.strip()
                                if blk.type == "spacer" or not c_str or c_str.startswith("---") or c_str.startswith("<!--"):
                                    assembled_blocks.append(blk.content)
                                    continue
                                cached = engine.block_cache.get_block(target_slot_str, blk.fingerprint, "")
                                if not cached:
                                    style_hash = getattr(engine, 'active_style_hash', '') or ""
                                    cached = engine.block_cache.get_block(target_slot_str, blk.fingerprint, style_hash)
                                if cached:
                                    assembled_blocks.append(cached)
                                else:
                                    all_cached = False
                                    break
                            if all_cached and assembled_blocks:
                                translated_body = "\n".join(assembled_blocks)
                        except Exception as bce:
                            tlog.warning(f"⚠️ [Block Cache 还原异常]: {bce}")

                    if not translated_body:
                        raise RuntimeError(
                            f"目标语种 [{target_slot_str.upper()}] "
                            f"的译文尚未生成或就绪。请先在‘语言翻译与内容治理’中生成该语种的 AI 译文后再重新广播！"
                        )
                    
                    body = translated_body
                    if translated_title:
                        broadcast_title = translated_title
                    fm["title"] = broadcast_title
                
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
        if 'enabled_syndication_channels' in locals() and enabled_syndication_channels:
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

def destroy_artifact_logic(engine, doc_id: str) -> dict:
    """
    🗑️ 物理销毁逻辑：抹除磁盘资产及其所有出版产物，并在账本中彻底注销
    """
    deleted_paths = []
    
    try:
        # 1. 物理撤销 Vault 源文件
        source_path = os.path.abspath(os.path.join(engine.vault_root, doc_id))
        if os.path.exists(source_path):
            os.remove(source_path)
            deleted_paths.append(source_path)
            
            # 清理 Vault 中因删除产生的空父文件夹
            parent = os.path.dirname(source_path)
            vault_root_abs = os.path.abspath(engine.vault_root)
            while parent != vault_root_abs and parent.startswith(vault_root_abs):
                try:
                    if os.path.exists(parent) and not os.listdir(parent):
                        os.rmdir(parent)
                        parent = os.path.dirname(parent)
                    else:
                        break
                except Exception:
                    break

        # 2. 物理抹除 dist 目录中的多语言出版快照
        config = engine.config
        imprint_id = config.active_imprint or "default"
        theme = config.active_theme or "default"
        dist_root = os.path.abspath(os.path.join("imprints", imprint_id, "themes", theme, "dist"))
        
        rel_path, _ = os.path.splitext(doc_id)
        html_name = f"{rel_path}.html"
        
        # 2.1 默认语种 HTML
        zh_path = os.path.join(dist_root, html_name)
        if os.path.exists(zh_path):
            os.remove(zh_path)
            deleted_paths.append(zh_path)
            
        # 2.2 目标语种 HTMLs
        i18n = config.i18n_settings
        for target in i18n.targets:
            lang_code = target.lang_code
            target_path = os.path.join(dist_root, lang_code, html_name)
            if os.path.exists(target_path):
                os.remove(target_path)
                deleted_paths.append(target_path)

        # 2.3 清理 dist 下因删除产生的空文件夹
        for root_dir in [dist_root] + [os.path.join(dist_root, t.lang_code) for t in i18n.targets]:
            html_abs_dir = os.path.dirname(os.path.join(root_dir, html_name))
            while html_abs_dir != root_dir and html_abs_dir.startswith(root_dir):
                try:
                    if os.path.exists(html_abs_dir) and not os.listdir(html_abs_dir):
                        os.rmdir(html_abs_dir)
                        html_abs_dir = os.path.dirname(html_abs_dir)
                    else:
                        break
                except Exception:
                    break

        # 3. 从 SQLite 主权账本与内存索引中注销元数据
        if hasattr(engine, "meta"):
            engine.meta.remove_document(doc_id)

        return {
            "success": True,
            "message": f"资产 {doc_id} 及其所有多语言出版产物已在全网物理销毁。",
            "deleted_items_count": len(deleted_paths)
        }
    except Exception as e:
        return {"success": False, "message": f"物理销毁失败: {str(e)}"}

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
