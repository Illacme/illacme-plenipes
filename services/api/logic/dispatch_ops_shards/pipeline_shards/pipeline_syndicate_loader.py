#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 [V113.2] Illacme Plenipes - Pipeline Syndication Loader Shard
职责：社交广播多语种译文智能装载、磁盘候选产物探测与段落级 Block Cache 组装还原。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
"""

import os
from typing import Tuple, List
from core.utils import extract_frontmatter
from core.utils.tracing import tlog

def get_enabled_syndication_channels(syndication_cfg: dict, target_channel: str = None) -> List[Tuple[str, dict]]:
    """找出已启用全局总开关或单篇手动指定的社交同步渠道"""
    enabled_syndication_channels = []
    for chan_id, chan_cfg in syndication_cfg.items():
        if isinstance(chan_cfg, dict):
            # 手动单篇定向广播时，只要该渠道在配置中有 api_key / token 凭据，直接放行支持定向广播
            has_cred = bool(chan_cfg.get("api_key") or chan_cfg.get("token") or chan_cfg.get("webhook_url"))
            is_match = not target_channel or chan_id == target_channel or chan_id.replace('_', '') == str(target_channel).replace('_', '')
            if is_match and (chan_cfg.get("enabled") or has_cred):
                enabled_syndication_channels.append((chan_id, chan_cfg))
    return enabled_syndication_channels

def load_syndication_content_and_metadata(
    engine,
    doc_id: str,
    doc_info: dict,
    target_slot: str
) -> Tuple[str, str, dict]:
    """
    智能装载用于社交广播的文章标题、正文 Markdown、Frontmatter。
    返回: (broadcast_title, body, fm)
    """
    # 读取源文件内容
    source_path = os.path.join(engine.vault_root, doc_id)
    if not os.path.exists(source_path):
        return "", "", {}

    with open(source_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
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
                    if not blk.is_translatable:
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

    return broadcast_title, body, fm
