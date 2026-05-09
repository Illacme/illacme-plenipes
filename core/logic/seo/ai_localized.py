#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Localized SEO Processor
职责：全球矩阵模式的「AI 本地化策略」策略。
🚀 [V53.0] 针对不同语种的搜索习性，差异化生成非对称 SEO 数据。

处理逻辑：
1. AI 分析原稿内容
2. 针对每个目标语种，独立生成符合该语言搜索习惯的 SEO
3. 不是简单翻译，而是根据搜索文化差异重新构思标题和描述
"""

import json
from .base import BaseSeoProcessor
from .ai_alignment import AIAlignmentProcessor
from core.logic.ai.ai_logic_hub import AILogicHub
from core.utils.tracing import tlog

LOCALIZED_SYSTEM_PROMPT = """You are a multilingual SEO expert who deeply understands search behavior differences across cultures.
Generate SEO metadata for {target_lang} searchers based on the provided content.

IMPORTANT: Do NOT simply translate the original metadata. Instead, RETHINK the SEO strategy
specifically for {target_lang} search patterns and user intent.

Your output MUST be a valid JSON object with:
- "seo_title": A title optimized for {target_lang} search patterns (max 60 chars)
- "description": A description tailored to {target_lang} searcher expectations (max 160 chars)
- "keywords": An array of 5-8 keywords that {target_lang} users would actually search for
- "search_intent": A brief note on how {target_lang} search intent differs from the source

Rules:
- Consider local search engine preferences (e.g., Baidu for Chinese, Google for English, Yahoo for Japanese)
- Adapt keyword length and style to the target language's search patterns
- Use culturally appropriate phrasing and tone
- Prioritize local relevance over literal accuracy
"""

LOCALIZED_USER_PROMPT = """### Original Content (in {source_lang}) ###
Title: {title}
Summary: {summary}

Body excerpt:
{text}

### Generate {target_lang}-Optimized SEO ###"""


class AILocalizedProcessor(BaseSeoProcessor):
    """🌐 AI 本地化策略：全球矩阵模式的进阶 SEO 策略。

    不是简单的翻译，而是根据不同语种用户的搜索习惯、
    文化偏好和搜索引擎特性，重新构思每个语种的 SEO 策略。
    """

    def process(self, ctx) -> dict:
        tlog.info(f"🌐 [AI 本地化] 正在为 '{ctx.title}' 执行差异化本地 SEO...")

        # 阶段 1: 先生成母语 SEO
        alignment = AIAlignmentProcessor()
        base_seo = alignment.process(ctx)

        translator = getattr(ctx.engine, 'translator', None)
        if not translator:
            tlog.warning("⚠️ [AI 本地化] AI 引擎未就绪，仅返回母语 SEO")
            return base_seo

        i18n = getattr(ctx.engine, 'i18n', None)
        if not i18n or not hasattr(i18n, 'targets'):
            return base_seo

        body = getattr(ctx, 'ai_pure_body', '') or getattr(ctx, 'raw_body', '')
        body_excerpt = body[:1500] if len(body) > 1500 else body

        source_lang = getattr(ctx, 'source_lang', 'zh')
        from core.utils.language_hub import LanguageHub
        source_name = LanguageHub.resolve_to_name(source_lang)

        localized_seo = {}
        for target in i18n.targets:
            lang_code = target.lang_code if hasattr(target, 'lang_code') else target.get('lang_code', '')
            if not lang_code:
                continue

            target_name = LanguageHub.resolve_to_name(lang_code)

            try:
                from core.adapters.ai.payload_manager import PayloadManager
                system_prompt = LOCALIZED_SYSTEM_PROMPT.format(target_lang=target_name)
                user_content = LOCALIZED_USER_PROMPT.format(
                    source_lang=source_name,
                    target_lang=target_name,
                    title=ctx.title,
                    summary=base_seo.get('description', ''),
                    text=body_excerpt
                )
                payload = PayloadManager.prepare_payload(
                    translator, system_prompt, user_content, is_json=True
                )
                if "params" not in payload:
                    payload["params"] = {}
                payload["params"]["max_tokens"] = 512

                raw = translator.ask_ai_with_retry(payload)
                repaired = AILogicHub.repair_json(raw)
                data = json.loads(repaired)

                entry = {
                    'seo_title': data.get('seo_title', '')[:self.MAX_TITLE_LENGTH],
                    'description': data.get('description', '')[:self.MAX_DESCRIPTION_LENGTH],
                    'keywords': data.get('keywords', [])[:self.MAX_KEYWORDS_COUNT]
                }

                # 记录搜索意图差异（用于调试和分析）
                if data.get('search_intent'):
                    entry['search_intent_note'] = data['search_intent']

                localized_seo[lang_code] = entry
                tlog.debug(f"  └── ✅ {lang_code}: 本地化 SEO 生成完成")

            except Exception as e:
                tlog.warning(f"  └── ⚠️ {lang_code}: 本地化 SEO 失败: {e}")

        if localized_seo:
            base_seo['i18n_seo'] = localized_seo

        tlog.info(f"✅ [AI 本地化] 完成: 母语 + {len(localized_seo)} 语种差异化 SEO")
        base_seo = self._respect_frontmatter(ctx.fm_dict, base_seo)
        return base_seo
