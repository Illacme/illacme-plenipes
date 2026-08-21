# -*- coding: utf-8 -*-
"""
🔒 [I5] Translation Human Review Ops
职责：翻译人工校对回流的业务原子逻辑实现。
遵循职责分离 SOP：路由层仅注册端点，业务逻辑全量下沉至此文件。
"""

import re
from core.utils.tracing import tlog


def _split_paragraphs(body: str) -> list:
    """将 Markdown 正文切割为段落块列表，用于前端段落级校对（Q1=C）。"""
    if not body:
        return []

    # 剥离系统内部追踪注释（Sovereign-Tag），不在校对 UI 中对用户展示
    body = re.sub(r'\s*<!--\s*Sovereign-Tag:.*?-->', '', body, flags=re.DOTALL).strip()

    # 🚀 [V115.0] 物理级 Markdown Block 对齐规范化：物理擦除 Çeviri ### 杂质、空 ### 标题及补齐标题前后空行断点
    body = re.sub(r'^(?:Çeviri|Translation|Translate|Çevirisi|翻译)\s*(?:###|:|：)?\s*', '', body, flags=re.IGNORECASE)
    body = re.sub(r'(?:Çeviri|Translation|Translate|Çevirisi|翻译)\s*###', '', body, flags=re.IGNORECASE)
    lines_clean = [l for l in body.split("\n") if not re.match(r'^#{1,6}\s*(?:Translation|Content|Inhalt|Übersetzung|Traduction|Contenido|Context|Tərcümə|Çeviri|原文|内容|译文|説明|概要)?\s*#{0,6}$', l.strip(), re.IGNORECASE)]
    body = "\n".join(lines_clean)
    body = re.sub(r'([^\n#])\s*(#{1,6}\s+)', r'\1\n\n\2', body)
    body = re.sub(r'^(#{1,6}\s+.*?)\n([^\n#])', r'\1\n\n\2', body, flags=re.MULTILINE)

    blocks = []
    idx = 0
    lines = body.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # 🚀 [V114.2] Alert 块自动归一化：若 > [!TAG] 标签与引文正文被 LLM 粘连在同一行，自动切割为独立的 Alert 头 Block
        if line.strip().startswith(">") and "[!" in line and "]" in line:
            match = re.match(r'^(\s*>\s*\[![^\]]+\])(.+)$', line.strip())
            if match and match.group(2).strip():
                tag_line = match.group(1).strip()
                rest_text = match.group(2).strip()
                rest_line = f"> {rest_text}" if not rest_text.startswith(">") else rest_text
                lines[i] = tag_line
                lines.insert(i + 1, rest_line)
                line = tag_line

        # 代码块：只读整体
        if line.strip().startswith("```"):
            end_j = i + 1
            while end_j < len(lines) and not lines[end_j].strip().startswith("```"):
                end_j += 1
            if end_j < len(lines):
                end_j += 1
            blocks.append({
                "index": idx,
                "type": "code",
                "text": "\n".join(lines[i:end_j])
            })
            idx += 1
            i = end_j
            continue

        # Callout 块（::: 语法）
        if line.strip().startswith(":::"):
            end_j = i + 1
            while end_j < len(lines) and not lines[end_j].strip().startswith(":::"):
                end_j += 1
            if end_j < len(lines):
                end_j += 1
            blocks.append({
                "index": idx,
                "type": "callout",
                "text": "\n".join(lines[i:end_j])
            })
            idx += 1
            i = end_j
            continue

        # 普通段落 / Callout (>)：智能拆分与连贯性识别
        if line.strip():
            para_lines = []
            is_quote_block = line.strip().startswith(">")
            while i < len(lines) and lines[i].strip():
                curr_l = lines[i].strip()
                if para_lines:
                    if curr_l.startswith('#'):
                        break
                    if not is_quote_block and curr_l.startswith('>'):
                        break
                    if is_quote_block and not curr_l.startswith('>'):
                        break
                para_lines.append(lines[i])
                i += 1
            text = "\n".join(para_lines).strip()
            # 🛡️ 分割线与 HTML 注释：设为 spacer 块（index=-1），在 UI 中展示但不计入正文段落编号
            if text.startswith("---") or text.startswith("***") or text.startswith("___") or text.startswith("<!--"):
                blocks.append({
                    "index": -1,
                    "type": "spacer",
                    "text": text
                })
                continue
            b_type = "callout" if is_quote_block else "paragraph"
            blocks.append({
                "index": idx,
                "type": b_type,
                "text": text
            })
            idx += 1
        else:
            i += 1

    return blocks


import os
from core.utils.text import parse_frontmatter
from services.api.logic.content_ops_shards.safe_ops import resolve_safe_path

def get_translation_snapshot_impl(engine, doc_id: str) -> dict:
    """获取文档所有已翻译语种的快照（含锁定状态、段落分割），源自账本及缓存（Q6=B）。"""
    if not engine or not engine.meta:
        return {"error": "Engine not initialized", "langs": {}}

    doc_info = engine.meta.get_doc_info(doc_id) or {}

    # 1. 查询该文档有哪些已翻译的语种
    t_rows = engine.meta.sqlite._get_conn().execute(
        "SELECT lang_code, status FROM translations WHERE rel_path = ?", (doc_id,)
    ).fetchall()
    t_map = {}
    for t in t_rows:
        td = dict(t) if hasattr(t, "keys") else ({"lang_code": t[0], "status": t[1]} if isinstance(t, (list, tuple)) and len(t) >= 2 else None)
        if td: t_map[td["lang_code"]] = td
    
    # 2. 查询人工校对表
    r_rows = engine.meta.sqlite._get_conn().execute(
        "SELECT lang_code, reviewed_body, reviewed_title, reviewed_desc, is_stale, reviewed_at, reviewed_by FROM translation_reviews WHERE doc_id = ?", (doc_id,)
    ).fetchall()
    r_map = {}
    for r in r_rows:
        rd = dict(r) if hasattr(r, "keys") else ({"lang_code": r[0], "reviewed_body": r[1], "reviewed_title": r[2], "reviewed_desc": r[3], "is_stale": r[4], "reviewed_at": r[5], "reviewed_by": r[6]} if isinstance(r, (list, tuple)) and len(r) >= 7 else None)
        if rd: r_map[rd["lang_code"]] = rd

    # 3. 获取原文用于对比
    src_abs = resolve_safe_path(engine, doc_id)
    source_body = ""
    source_title = ""
    source_desc = ""
    if src_abs and os.path.exists(src_abs):
        try:
            with open(src_abs, "r", encoding="utf-8") as f:
                fm_dict, source_body, _ = parse_frontmatter(f.read())
                source_title = fm_dict.get("title", "")
                source_desc = fm_dict.get("description", "")
        except Exception:
            pass

    real_rel_path = os.path.relpath(src_abs, os.path.abspath(engine.vault_root)).replace('\\', '/') if src_abs else doc_id
    if not doc_info and real_rel_path: doc_info = engine.meta.get_doc_info(real_rel_path) or {}

    # 🛡️ 3 级钢铁标题提取 (Frontmatter -> 正文 H1 标题 -> 账本/物理文件名)
    if not source_title and source_body:
        import re; m = re.search(r'^\s*#\s+(.+)$', source_body, re.MULTILINE)
        if m: source_title = m.group(1).strip()
    if not source_title:
        source_title = doc_info.get("title") or os.path.splitext(os.path.basename(real_rel_path))[0]

    source_paras = _split_paragraphs(source_body)

    langs = {}
    
    # 准备路径解析依赖
    route_prefix = doc_info.get("route_prefix")
    sub_dir = doc_info.get("sub_dir")
    slug = doc_info.get("slug")
    target_slot = doc_info.get("target_slot", "docs")
    cache_dir = engine.paths.get("cache") if hasattr(engine, "paths") else None
    target_ext = os.path.splitext(doc_id)[1].lower() or ".md"

    # 获取全量目标语种配置（仅使用当前版图配置中激活的语种）
    # 🛡️ [UI 防污染] 不将 translations 表中的历史過期语种（如旧版本的 PT）并入展示，
    # 只展示当前 i18n_settings.targets 配置的语种，避免用户看到不应展示的 Tab。
    target_codes = []
    if hasattr(engine, "config") and hasattr(engine.config, "i18n_settings"):
        target_codes = [t.lang_code for t in engine.config.i18n_settings.targets]

    for lang_code in target_codes:
        td = t_map.get(lang_code, {})
        st = td.get("status", "MISSING")
        r_data = r_map.get(lang_code, {})
        has_review = bool(r_data)
        body = r_data.get("reviewed_body")
        title = r_data.get("reviewed_title")
        desc = r_data.get("reviewed_desc")
        total_blocks, translated_blocks = 0, 0
        try:
            translation_cfg = getattr(engine.config, "translation", None)
            resolved_style = getattr(translation_cfg, "active_style", "default") if translation_cfg else "default"
            p_style = getattr(translation_cfg, "prompts", None) if translation_cfg else None
            if resolved_style and p_style:
                from core.logic.ai.ai_factory import TranslatorFactory
                p_style = TranslatorFactory.get_prompts_for_style(resolved_style, getattr(engine, "imprint_id", "default"), p_style)
            t_sys = getattr(p_style, "translate_system", "") if p_style else ""
            t_user = getattr(p_style, "translate_user", "") if p_style else ""
            if type(t_sys).__name__ in ('MagicMock', 'Mock'): t_sys = ""
            if type(t_user).__name__ in ('MagicMock', 'Mock'): t_user = ""
            import hashlib
            style_content = str(t_sys or "") + "\n" + str(t_user or "")
            style_hash = hashlib.md5(style_content.encode('utf-8')).hexdigest()

            if hasattr(engine, 'active_translation_progress') and (real_rel_path, lang_code) in engine.active_translation_progress:
                progress_data = engine.active_translation_progress[(real_rel_path, lang_code)]
            else:
                from core.logic.block_parser import MarkdownBlockParser
                parser = MarkdownBlockParser()
                for block in parser.parse(source_body):
                    c_str = block.content.strip()
                    if block.type == "spacer" or not c_str or c_str.startswith("---") or c_str.startswith("<!--"): continue
                    total_blocks += 1
                    import re
                    stripped = re.sub(r'__B_MASK_\d+__', '', c_str)
                    stripped = re.sub(r'\[\[STB_MASK_\d+\]\]', '', stripped)
                    stripped = re.sub(r'\[\[GLOS_MASK_\d+\]\]', '', stripped)
                    if not re.search(r'\w', stripped) or engine.block_cache.get_block(lang_code, block.fingerprint, style_hash):
                        translated_blocks += 1
                progress_data = {"translated_paras": translated_blocks, "total_paras": max(1, total_blocks)}
        except Exception:
            progress_data = {"translated_paras": 0, "total_paras": 1}

        # 🛡️ [V106.0] 竞态防护：如果后台翻译管线正在 running，即使旧缓存/旧 body 仍存在于磁盘上，
        # 也必须强制返回 is_missing=True + 实时进度，防止前端轮询被旧数据骗到而提前宣布翻译完成。
        is_actively_running = (
            hasattr(engine, 'active_translation_progress')
            and (real_rel_path, lang_code) in engine.active_translation_progress
            and engine.active_translation_progress[(real_rel_path, lang_code)].get('running', False)
        )
        if is_actively_running:
            langs[lang_code] = {
                "is_missing": True,
                "title": "", "desc": "", "paragraphs": [],
                "human_approved": False, "review_is_stale": False,
                "progress": progress_data
            }
            continue

        # 🚀 [BlockCache 增强] 优先尝试从 BlockCache 聚合已翻译的段落 (按 source_paras 对齐)
        block_cached_paras = []
        has_block_cache_content = False
        try:
            from core.markup.base import MarkupBlock
            cached_texts = []
            hit_count = 0
            valid_src_count = 0
            for sp in source_paras:
                if sp.get("index", -1) < 0 or sp.get("type") == "spacer":
                    cached_texts.append(dict(sp))
                    continue
                valid_src_count += 1
                fp = MarkupBlock(sp.get("text", ""), block_type=sp.get("type", "paragraph")).fingerprint
                c_text = engine.block_cache.get_block(lang_code, fp, style_hash)
                if c_text:
                    hit_count += 1
                    cached_texts.append({"index": sp.get("index", 0), "type": sp.get("type", "paragraph"), "text": c_text})
                else:
                    cached_texts.append(dict(sp))
            
            if valid_src_count > 0 and hit_count > 0:
                block_cached_paras = cached_texts
                has_block_cache_content = (hit_count >= valid_src_count / 2)
        except Exception as e:
            tlog.warning(f"BlockCache reading error for snapshot: {e}")

        if not body and hasattr(engine, "route_manager"):
            try:
                candidate_paths = []
                if hasattr(engine, "config") and engine.config:
                    theme_name = getattr(engine, 'active_theme', 'default') or 'default'
                    theme_cache_dir = engine.config.get_theme_source_cache_dir(theme_name)
                    if theme_cache_dir:
                        candidate_paths.append(engine.route_manager.resolve_physical_path(theme_cache_dir, lang_code, route_prefix, sub_dir, slug, target_ext, source_type=target_slot))
                if cache_dir:
                    candidate_paths.append(engine.route_manager.resolve_physical_path(cache_dir, lang_code, route_prefix, sub_dir, slug, target_ext, source_type=target_slot))

                for c_path in candidate_paths:
                    if c_path and os.path.exists(c_path):
                        with open(c_path, "r", encoding="utf-8") as f:
                            fm_dict, pure_content, _ = parse_frontmatter(f.read())
                            if pure_content and pure_content.strip():
                                body = pure_content
                                title = title or fm_dict.get("title", "")
                                d_val = fm_dict.get("description", "")
                                if d_val and isinstance(d_val, str) and lang_code != "ja":
                                    import re
                                    if re.search(r'[\u3040-\u30ff]', d_val):
                                        d_val = ""
                                desc = desc or d_val
                                break
            except Exception as e:
                from core.utils.tracing import tlog
                tlog.warning(f"Failed to read AI snapshot for {doc_id} / {lang_code}: {e}")

        import re
        is_disk_body_chinese = bool(body and lang_code != 'zh' and re.search(r'[\u4e00-\u9fa5]', body) and re.search(r'[\u4e00-\u9fa5]', source_body))
        if (not body or is_disk_body_chinese) and has_block_cache_content:
            body = "\n\n".join([p["text"] for p in block_cached_paras if p.get("index", -1) >= 0])

        if not body:
            err_title = title or "⚠️ 翻译失败 / Translation Failed" if st == "ERROR" else ""
            err_desc = desc or "AI 引擎处理该语种时发生严重错误，请检查后台日志或节点连通性。" if st == "ERROR" else ""
            err_paras = [{"index": 0, "type": "paragraph", "text": "*(该语种生成失败，请稍后重试或检查 LLM 配置)*"}] if st == "ERROR" else []
            langs[lang_code] = {
                "is_missing": (st != "ERROR"),
                "title": err_title, "desc": err_desc, "paragraphs": err_paras,
                "human_approved": False, "review_is_stale": False, "progress": progress_data
            }
            continue

        target_paras = block_cached_paras if (has_block_cache_content and is_disk_body_chinese) else _split_paragraphs(body)
        valid_src_p_count = len([p for p in source_paras if p.get("index", -1) >= 0])
        valid_tgt_p_count = len([p for p in target_paras if p.get("index", -1) >= 0])
        count_mismatch = bool(valid_src_p_count > 0 and valid_tgt_p_count > 0 and valid_tgt_p_count != valid_src_p_count)

        if not desc or desc.strip() == "无描述":
            for tp in target_paras:
                t_text = (tp.get("text") or "").strip()
                if t_text and not t_text.startswith("#") and not t_text.startswith("```"):
                    desc = t_text[:150]
                    break
        if desc:
            from core.logic.ai.ai_logic_hub import AILogicHub
            desc = AILogicHub.clean_metadata_value(desc)

        langs[lang_code] = {
            "is_missing": False, "title": title or "", "desc": desc or "",
            "paragraphs": target_paras, "human_approved": bool(has_review),
            "review_is_stale": bool(r_data.get("is_stale", False)),
            "reviewed_at": r_data.get("reviewed_at"), "reviewed_by": r_data.get("reviewed_by"),
            "progress": progress_data, "paragraph_count_mismatch": count_mismatch
        }

    # 4. 获取出版模式并下发
    from core.config.models.governance import PublishingMode
    gov = getattr(engine.config, 'governance', None)
    publishing_mode = getattr(gov, 'publishing_mode', PublishingMode.BASIC) if gov else PublishingMode.BASIC
    mode_str = publishing_mode.value if hasattr(publishing_mode, 'value') else str(publishing_mode)

    real_rel_path = os.path.relpath(src_abs, os.path.abspath(engine.vault_root)).replace('\\', '/') if src_abs else doc_id

    return {
        "doc_id": real_rel_path,
        "doc_title": doc_info.get("title", ""),
        "source_title": source_title,
        "source_desc": source_desc,
        "source_hash": doc_info.get("source_hash", ""),
        "source_paragraphs": source_paras,
        "publishing_mode": mode_str,
        "langs": langs
    }


def save_human_review_impl(engine, doc_id: str, lang_code: str, paragraphs: list, title: str = None, desc: str = None) -> dict:
    """保存人工校对结果并上锁（语种级，Q2=A）。"""
    if not engine or not engine.meta: return {"ok": False, "error": "Engine not initialized"}
    doc_info = engine.meta.get_doc_info(doc_id) or {}
    src_abs = resolve_safe_path(engine, doc_id)
    if not doc_info and src_abs:
        real_rel_path = os.path.relpath(src_abs, os.path.abspath(engine.vault_root)).replace('\\', '/')
        doc_info = engine.meta.get_doc_info(real_rel_path) or {}
    reviewed_body = "\n\n".join([p.get("text", "") for p in (paragraphs or [])])
    source_hash = doc_info.get("source_hash", "")
    engine.meta.set_human_lock(doc_id=doc_id, lang_code=lang_code, reviewed_body=reviewed_body, reviewed_title=title or None, reviewed_desc=desc or None, source_hash=source_hash, reviewed_by="commander")
    tlog.info(f"🔒 [I5] 校对结果已保存并上锁: {doc_id} / {lang_code}")
    return {"ok": True, "doc_id": doc_id, "lang_code": lang_code}

def unlock_human_review_impl(engine, doc_id: str, lang_code: str) -> dict:
    """解除人工校对锁（用户主动操作，重置为 AI 重译）。"""
    if not engine or not engine.meta: return {"ok": False, "error": "Engine not initialized"}
    engine.meta.clear_human_lock(doc_id=doc_id, lang_code=lang_code)
    tlog.info(f"🗑️ [I5] 校对锁已解除: {doc_id} / {lang_code}")
    return {"ok": True, "doc_id": doc_id, "lang_code": lang_code}

def retranslate_paragraph_impl(engine, doc_id: str, lang_code: str, para_index: int, source_text: str) -> dict:
    """🪄 物理单段落 AI 微粒度重译与 Block Cache 装配。"""
    if not engine: return {"ok": False, "error": "Engine not initialized"}
    if not source_text or not source_text.strip(): return {"ok": True, "translated_text": source_text}
    try:
        from core.logic.ai.ai_factory import TranslatorFactory
        from core.logic.ai.ai_logic_hub import AILogicHub
        node = TranslatorFactory.create(engine.config.translation) if hasattr(engine, "config") and engine.config else None
        if not node: return {"ok": False, "error": "无可用算力节点"}

        if para_index == -2:
            rem = "Polish into an elegant 1-2 sentence SEO abstract in target language. Remove raw Wikilinks or placeholders. No prompt delimiters."
            res = AILogicHub.clean_metadata_value(node.translate(source_text, source_lang="auto", target_lang=lang_code, remedy_instruction=rem) or "")
        elif para_index == -1:
            rem = "Polish into a concise title in target language. No prompt delimiters."
            res = AILogicHub.clean_metadata_value(node.translate(source_text, source_lang="auto", target_lang=lang_code, remedy_instruction=rem) or "")
        else:
            res = AILogicHub.clean_translation_response(node.translate(source_text, source_lang="zh-cn", target_lang=lang_code) or "")
            if res and hasattr(engine, 'block_cache'):
                import hashlib
                from core.logic.block_parser import MarkdownBlock
                fp = MarkdownBlock(source_text, type='paragraph', index=para_index).fingerprint
                translation_cfg = getattr(engine.config, "translation", None)
                resolved_style = getattr(translation_cfg, "active_style", "default") if translation_cfg else "default"
                p_style = getattr(translation_cfg, "prompts", None) if translation_cfg else None
                t_sys = getattr(p_style, "translate_system", "") if p_style else ""
                t_user = getattr(p_style, "translate_user", "") if p_style else ""
                style_content = str(t_sys or "") + "\n" + str(t_user or "")
                style_hash = hashlib.md5(style_content.encode('utf-8')).hexdigest()
                engine.block_cache.store_block(lang_code, fp, res, style_hash=style_hash)
        return {"ok": True, "translated_text": res or source_text}
    except Exception as e: return {"ok": False, "error": str(e)}
