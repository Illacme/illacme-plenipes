#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Sync SEO Processor
职责：全球矩阵模式的「AI 翻译同步」策略。
🚀 [V53.0] 将原稿 SEO 元信息 1:1 精准翻译并同步至目标语言版本。

处理逻辑：
1. 先对原稿执行 AI 算法对齐，生成母语 SEO 元数据
2. 将生成的 title/description/keywords 逐一翻译为各目标语种
3. 确保多语言页面的 SEO 元数据与原稿语义一致
"""

import json
from .base import BaseSeoProcessor
from .ai_alignment import AIAlignmentProcessor
from core.logic.ai.ai_logic_hub import AILogicHub
from core.utils.tracing import tlog

SYNC_SYSTEM_PROMPT = """You are a professional SEO translator. Translate the following SEO metadata
from {source_lang} to {target_lang}. Keep the same semantic meaning, emotional tone, and SEO effectiveness.

Your output MUST be a valid JSON object with:
- "seo_title": Translated title (max 60 chars)
- "description": Translated description (max 160 chars)
- "keywords": Translated keyword array (5-8 items)

Rules:
- Maintain the original SEO intent and keyword density
- Adapt cultural references where appropriate
- Preserve technical terms that should not be translated
"""

SYNC_USER_PROMPT = """### Original SEO Metadata ({source_lang}) ###
Title: {title}
Description: {description}
Keywords: {keywords}

### Translate to {target_lang} ###"""


class AISyncProcessor(BaseSeoProcessor):
    """🔄 AI 翻译同步：全球矩阵模式的默认 SEO 策略。

    先用 AI 对原稿生成高质量 SEO 元数据，再将这些元数据
    1:1 翻译同步到每个目标语种的页面，确保跨语言 SEO 一致性。
    """

    def process(self, ctx) -> dict:
        import hashlib
        body = getattr(ctx, 'ai_pure_body', '') or getattr(ctx, 'raw_body', '')
        body_excerpt = body[:2000] if len(body) > 2000 else body
        rel_path = getattr(ctx, 'rel_path', '') or getattr(ctx, 'title', '')
        current_hash = getattr(ctx, 'current_hash', None) or hashlib.md5(body_excerpt.encode('utf-8')).hexdigest()
        engine_meta = getattr(getattr(ctx, 'engine', None), 'meta', None)

        # 🚀 [V101.0] 增量缓存：基于原稿内容 Hash 检查多语 AI 翻译同步 SEO 缓存
        if engine_meta and rel_path and current_hash and not getattr(ctx, 'clear_cache', False):
            doc_info = engine_meta.get_doc_info(rel_path) or {}
            cached_sync_seo = doc_info.get("ai_seo_sync")
            if isinstance(cached_sync_seo, dict) and cached_sync_seo.get("hash") == current_hash and cached_sync_seo.get("data"):
                tlog.info(f"✨ [AI 翻译同步] 命中本地多语 SEO 缓存，跳过大模型翻译 ({ctx.title})")
                return self._respect_frontmatter(ctx.fm_dict, cached_sync_seo.get("data", {}))
            existing_seo = doc_info.get("seo_data")
            if (isinstance(existing_seo, dict) and existing_seo.get("i18n_seo")
                    and doc_info.get("source_hash") == current_hash):
                tlog.info(f"✨ [AI 翻译同步] 命中账本已有多语 SEO 资产，跳过大模型翻译 ({ctx.title})")
                return self._respect_frontmatter(ctx.fm_dict, existing_seo)

        tlog.info(f"🔄 [AI 翻译同步] 正在为 '{ctx.title}' 执行跨语种 SEO 同步...")

        # 阶段 1: 先用 AI Alignment 生成母语 SEO
        alignment = AIAlignmentProcessor()
        base_seo = alignment.process(ctx)

        translator = getattr(ctx.engine, 'translator', None)
        if not translator:
            tlog.warning("⚠️ [AI 翻译同步] AI 引擎未就绪，仅返回母语 SEO")
            return base_seo

        # 阶段 2: 将 SEO 元数据翻译到目标语种
        i18n = getattr(ctx.engine, 'i18n', None)
        if not i18n or not hasattr(i18n, 'targets'):
            return base_seo

        source_lang = getattr(ctx, 'source_lang', 'zh')
        from core.utils.language_hub import LanguageHub
        source_name = LanguageHub.resolve_to_name(source_lang)

        translated_seo = {}
        for target in i18n.targets:
            lang_code = target.lang_code if hasattr(target, 'lang_code') else target.get('lang_code', '')
            if not lang_code:
                continue

            target_name = LanguageHub.resolve_to_name(lang_code)

            try:
                from core.adapters.ai.payload_manager import PayloadManager
                system_prompt = SYNC_SYSTEM_PROMPT.format(
                    source_lang=source_name, target_lang=target_name
                )
                user_content = SYNC_USER_PROMPT.format(
                    source_lang=source_name,
                    target_lang=target_name,
                    title=base_seo.get('og_title', ctx.title),
                    description=base_seo.get('description', ''),
                    keywords=', '.join(base_seo.get('keywords', []))
                )
                payload = PayloadManager.prepare_payload(
                    translator, system_prompt, user_content, is_json=True
                )
                if "params" not in payload:
                    payload["params"] = {}
                payload["params"]["max_tokens"] = 1024

                raw = translator.ask_ai_with_retry(payload)
                if hasattr(raw, 'text'): raw = getattr(raw, 'text')
                elif hasattr(raw, 'content'): raw = getattr(raw, 'content')
                if not isinstance(raw, (str, bytes, bytearray)):
                    raw = '{"seo_title": "", "description": "", "keywords": []}'

                repaired = AILogicHub.repair_json(raw)
                data = json.loads(repaired) if isinstance(repaired, str) else {}

                translated_seo[lang_code] = {
                    'seo_title': data.get('seo_title', '')[:self.MAX_TITLE_LENGTH],
                    'description': data.get('description', '')[:self.MAX_DESCRIPTION_LENGTH],
                    'keywords': data.get('keywords', [])[:self.MAX_KEYWORDS_COUNT]
                }
                tlog.debug(f"  └── ✅ {lang_code}: 翻译同步完成")

            except Exception as e:
                tlog.warning(f"  └── ⚠️ {lang_code}: 翻译同步失败: {e}")

        if translated_seo:
            base_seo['i18n_seo'] = translated_seo

        # 🚀 [V101.0] 持久化缓存：将跨语种 SEO 翻译数据写入账本
        if engine_meta and rel_path and current_hash and translated_seo:
            try:
                doc_info = engine_meta.get_doc_info(rel_path) or {}
                engine_meta.sqlite.upsert_document(rel_path, {**doc_info, "ai_seo_sync": {"hash": current_hash, "data": base_seo}})
            except Exception as e:
                tlog.debug(f"⚠️ [AI 翻译同步] 写入多语 SEO 缓存失败: {e}")

        tlog.info(f"✅ [AI 翻译同步] 完成: 母语 + {len(translated_seo)} 语种同步")
        base_seo = self._respect_frontmatter(ctx.fm_dict, base_seo)
        return base_seo
