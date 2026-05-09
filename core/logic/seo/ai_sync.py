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
                payload["params"]["max_tokens"] = 256

                raw = translator.ask_ai_with_retry(payload)
                repaired = AILogicHub.repair_json(raw)
                data = json.loads(repaired)

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

        tlog.info(f"✅ [AI 翻译同步] 完成: 母语 + {len(translated_seo)} 语种同步")
        base_seo = self._respect_frontmatter(ctx.fm_dict, base_seo)
        return base_seo
