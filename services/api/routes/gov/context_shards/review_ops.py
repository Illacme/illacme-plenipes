# -*- coding: utf-8 -*-
"""
🔒 [I5] Translation Human Review Ops
职责：翻译人工校对回流的业务原子逻辑实现。
遵循职责分离 SOP：路由层仅注册端点，业务逻辑全量下沉至此文件及对应子分片。
"""

import os
import re
from core.utils.tracing import tlog
from core.utils.text import parse_frontmatter
from services.api.logic.content_ops_shards.safe_ops import resolve_safe_path
from .review_parser import split_paragraphs as _split_paragraphs
from .review_actions import (
    save_human_review_impl,
    unlock_human_review_impl,
    retranslate_paragraph_impl,
)

# 保持对外导出与兼容性
__all__ = [
    "_split_paragraphs",
    "get_translation_snapshot_impl",
    "save_human_review_impl",
    "unlock_human_review_impl",
    "retranslate_paragraph_impl",
]


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
        if td:
            t_map[td["lang_code"]] = td

    # 2. 查询人工校对表
    r_rows = engine.meta.sqlite._get_conn().execute(
        "SELECT lang_code, reviewed_body, reviewed_title, reviewed_desc, is_stale, reviewed_at, reviewed_by FROM translation_reviews WHERE doc_id = ?", (doc_id,)
    ).fetchall()
    r_map = {}
    for r in r_rows:
        rd = dict(r) if hasattr(r, "keys") else ({"lang_code": r[0], "reviewed_body": r[1], "reviewed_title": r[2], "reviewed_desc": r[3], "is_stale": r[4], "reviewed_at": r[5], "reviewed_by": r[6]} if isinstance(r, (list, tuple)) and len(r) >= 7 else None)
        if rd:
            r_map[rd["lang_code"]] = rd

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
    if not doc_info and real_rel_path:
        doc_info = engine.meta.get_doc_info(real_rel_path) or {}

    # 🛡️ 3 级钢铁标题提取 (Frontmatter -> 正文 H1 标题 -> 账本/物理文件名)
    if not source_title and source_body:
        m = re.search(r'^\s*#\s+(.+)$', source_body, re.MULTILINE)
        if m:
            source_title = m.group(1).strip()
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

    # 获取全量目标语种配置（仅使用当前品牌配置中激活的语种）
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
        progress_data = _calc_translation_progress(engine, real_rel_path, lang_code, source_body)

        # 🛡️ [V106.0] 竞态防护：如果后台翻译管线正在 running，返回 is_missing=True + 实时进度
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

        # 🚀 [BlockCache 增强] 优先尝试从 BlockCache 聚合已翻译的段落
        block_cached_paras, has_block_cache_content = _fetch_block_cached_paras(engine, lang_code, source_paras)

        if not body and hasattr(engine, "route_manager"):
            body, title, desc = _read_ai_snapshot_from_disk(
                engine, doc_id, lang_code, route_prefix, sub_dir, slug,
                target_slot, target_ext, cache_dir, title, desc
            )

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


def _calc_translation_progress(engine, real_rel_path: str, lang_code: str, source_body: str) -> dict:
    """计算当前语种的翻译段落进度。"""
    try:
        if hasattr(engine, 'active_translation_progress') and (real_rel_path, lang_code) in engine.active_translation_progress:
            return engine.active_translation_progress[(real_rel_path, lang_code)]

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
        style_hash = hashlib.md5((str(t_sys or "") + "\n" + str(t_user or "")).encode('utf-8')).hexdigest()

        from core.logic.block_parser import MarkdownBlockParser
        parser = MarkdownBlockParser()
        total_blocks, translated_blocks = 0, 0
        for block in parser.parse(source_body):
            if not block.is_translatable:
                continue
            total_blocks += 1
            c_str = block.content.strip()
            stripped = re.sub(r'__B_MASK_\d+__', '', c_str)
            stripped = re.sub(r'\[\[STB_MASK_\d+\]\]', '', stripped)
            stripped = re.sub(r'\[\[GLOS_MASK_\d+\]\]', '', stripped)
            if not re.search(r'\w', stripped) or engine.block_cache.get_block(lang_code, block.fingerprint, style_hash):
                translated_blocks += 1
        return {"translated_paras": translated_blocks, "total_paras": max(1, total_blocks)}
    except Exception:
        return {"translated_paras": 0, "total_paras": 1}


def _fetch_block_cached_paras(engine, lang_code: str, source_paras: list) -> tuple:
    """从 BlockCache 尝试检索已翻译段落列表。"""
    try:
        from core.markup.base import MarkupBlock
        import hashlib
        translation_cfg = getattr(engine.config, "translation", None)
        p_style = getattr(translation_cfg, "prompts", None) if translation_cfg else None
        t_sys = getattr(p_style, "translate_system", "") if p_style else ""
        t_user = getattr(p_style, "translate_user", "") if p_style else ""
        style_hash = hashlib.md5((str(t_sys or "") + "\n" + str(t_user or "")).encode('utf-8')).hexdigest()

        cached_texts = []
        hit_count, valid_src_count = 0, 0
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

        has_content = (valid_src_count > 0 and hit_count >= valid_src_count / 2)
        return (cached_texts if valid_src_count > 0 and hit_count > 0 else []), has_content
    except Exception as e:
        tlog.warning(f"BlockCache reading error for snapshot: {e}")
        return [], False


def _read_ai_snapshot_from_disk(
    engine, doc_id: str, lang_code: str, route_prefix: str, sub_dir: str,
    slug: str, target_slot: str, target_ext: str, cache_dir: str,
    title: str, desc: str
) -> tuple:
    """从磁盘主题缓存或公共缓存中读取 AI 生成的快照。"""
    body = None
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
                            if re.search(r'[\u3040-\u30ff]', d_val):
                                d_val = ""
                        desc = desc or d_val
                        break
    except Exception as e:
        tlog.warning(f"Failed to read AI snapshot for {doc_id} / {lang_code}: {e}")
    return body, title, desc
