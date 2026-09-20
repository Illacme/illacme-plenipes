# -*- coding: utf-8 -*-
"""
🔒 [I5] Translation Human Review Actions Shard
职责：提供人工校对工作台的保存上锁、解除校对锁及微粒度单段落 AI 重译逻辑。
"""

import os
from core.utils.tracing import tlog
from services.api.logic.content_ops_shards.safe_ops import resolve_safe_path


def save_human_review_impl(engine, doc_id: str, lang_code: str, paragraphs: list, title: str = None, desc: str = None) -> dict:
    """保存人工校对结果并上锁（语种级，Q2=A）。"""
    if not engine or not engine.meta:
        return {"ok": False, "error": "Engine not initialized"}
    doc_info = engine.meta.get_doc_info(doc_id) or {}
    src_abs = resolve_safe_path(engine, doc_id)
    if not doc_info and src_abs:
        real_rel_path = os.path.relpath(src_abs, os.path.abspath(engine.vault_root)).replace('\\', '/')
        doc_info = engine.meta.get_doc_info(real_rel_path) or {}
    reviewed_body = "\n\n".join([p.get("text", "") for p in (paragraphs or [])])
    source_hash = doc_info.get("source_hash", "")
    engine.meta.set_human_lock(
        doc_id=doc_id,
        lang_code=lang_code,
        reviewed_body=reviewed_body,
        reviewed_title=title or None,
        reviewed_desc=desc or None,
        source_hash=source_hash,
        reviewed_by="commander"
    )
    tlog.info(f"🔒 [I5] 校对结果已保存并上锁: {doc_id} / {lang_code}")
    return {"ok": True, "doc_id": doc_id, "lang_code": lang_code}


def unlock_human_review_impl(engine, doc_id: str, lang_code: str) -> dict:
    """解除人工校对锁（用户主动操作，重置为 AI 重译）。"""
    if not engine or not engine.meta:
        return {"ok": False, "error": "Engine not initialized"}
    engine.meta.clear_human_lock(doc_id=doc_id, lang_code=lang_code)
    tlog.info(f"🗑️ [I5] 校对锁已解除: {doc_id} / {lang_code}")
    return {"ok": True, "doc_id": doc_id, "lang_code": lang_code}


def retranslate_paragraph_impl(engine, doc_id: str, lang_code: str, para_index: int, source_text: str) -> dict:
    """🪄 物理单段落 AI 微粒度重译与 Block Cache 装配。"""
    if not engine:
        return {"ok": False, "error": "Engine not initialized"}
    if not source_text or not source_text.strip():
        return {"ok": True, "translated_text": source_text}
    try:
        from core.logic.ai.ai_factory import TranslatorFactory
        from core.logic.ai.ai_logic_hub import AILogicHub
        node = TranslatorFactory.create(engine.config.translation) if hasattr(engine, "config") and engine.config else None
        if not node:
            return {"ok": False, "error": "无可用算力节点"}

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
                from core.markup.base import MarkupBlock
                fp = MarkupBlock(source_text, block_type='paragraph').fingerprint
                translation_cfg = getattr(engine.config, "translation", None)
                p_style = getattr(translation_cfg, "prompts", None) if translation_cfg else None
                t_sys = getattr(p_style, "translate_system", "") if p_style else ""
                t_user = getattr(p_style, "translate_user", "") if p_style else ""
                style_content = str(t_sys or "") + "\n" + str(t_user or "")
                style_hash = hashlib.md5(style_content.encode('utf-8')).hexdigest()
                engine.block_cache.store_block(lang_code, fp, res, style_hash=style_hash)
        return {"ok": True, "translated_text": res or source_text}
    except Exception as e:
        return {"ok": False, "error": str(e)}
