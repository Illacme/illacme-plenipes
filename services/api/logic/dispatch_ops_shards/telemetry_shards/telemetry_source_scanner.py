# -*- coding: utf-8 -*-
"""
📡 Telemetry Shard - Source Document Scanner
职责：读取源 Markdown 文件，提取 Frontmatter、计算基准 Token 数、解析 AST 语义块与指纹。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
"""

import os
from core.utils.common import TokenCounter
from core.utils.language_hub import LanguageHub
from core.utils import extract_frontmatter, normalize_keywords
from core.logic.block_parser import MarkdownBlockParser

def scan_source_document(engine, doc_id: str, doc_info: dict) -> dict:
    """
    扫描源 Markdown 文档，解析 Token、Frontmatter、AST 语义块与源语言识别
    """
    src_tokens = 0
    total_blocks = 0
    blocks_fingerprints = []
    content = ""
    body = ""
    source_path = os.path.join(engine.vault_root, doc_id)

    if os.path.exists(source_path):
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
                src_tokens = TokenCounter.count(content)
                raw_fm_dict, raw_body = extract_frontmatter(content)
                
                # 🚀 [V75.5] 物理归一化与全局隐私屏蔽，以彻底对齐分发管线，消除指纹分裂
                if hasattr(engine, 'input_adapter') and engine.input_adapter:
                    raw_body, raw_fm_dict = engine.input_adapter.normalize(raw_body, raw_fm_dict)
                
                body = engine.ast_resolver.resolve(raw_body, source_path, engine.paths.get('target_base'))
                
                # 🚀 [V75.5] 对齐 MetadataAndHashStep 的 current_hash 计算
                defaults = getattr(engine, 'fm_defaults', None) or {}
                base_fm = {k: v for k, v in defaults.items() if v is not None and str(v).strip() != ""}
                base_fm.update(raw_fm_dict)
                for fld in ['keywords', 'tags', 'categories']:
                    if fld in base_fm:
                        base_fm[fld] = normalize_keywords(base_fm.get(fld))
                if 'slug' in base_fm:
                    base_fm.pop('slug', None)

                parser = MarkdownBlockParser()
                for block in parser.parse(body):
                    if not block.is_translatable:
                        continue
                    blocks_fingerprints.append(block.fingerprint)
                total_blocks = len(blocks_fingerprints)
        except Exception:
            pass

    # 🚀 [V75.5] 自动探测或从数据库中还原已识别的原稿源语种
    resolved_src_lang = doc_info.get("source_lang")
    if not resolved_src_lang and os.path.exists(source_path):
        try:
            detect_sample = content[:1000] if content else ""
            resolved_src_lang = LanguageHub.detect_source_lang(detect_sample, getattr(engine, 'translator', None))
        except Exception:
            pass
    resolved_src_lang = resolved_src_lang or "zh-Hans" # 兜底至 zh-Hans
    src_display_name = LanguageHub.resolve_to_name(resolved_src_lang)

    return {
        "src_tokens": src_tokens,
        "total_blocks": total_blocks,
        "blocks_fingerprints": blocks_fingerprints,
        "source_path": source_path,
        "resolved_src_lang": resolved_src_lang,
        "src_display_name": src_display_name,
        "content": content,
        "body": body
    }
