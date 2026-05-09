#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Alignment SEO Processor
职责：智能增强模式的「AI 算法对齐」策略。
🚀 [V53.0] 利用 AI 优化 CTR 和关键词埋点，精准投喂搜索引擎。

处理逻辑：
1. AI 分析全文语义，生成高点击率的 SEO 标题
2. AI 提取高热搜索词并自然埋入描述
3. AI 生成精准的 keywords 标签
4. 所有结果遵守"元数据优先"底线
"""

import json
from .base import BaseSeoProcessor
from core.logic.ai.ai_logic_hub import AILogicHub
from core.utils.tracing import tlog

# 🚀 [V53.0] AI 算法对齐专用提示词
ALIGNMENT_SYSTEM_PROMPT = """You are an expert SEO strategist specializing in search engine algorithm optimization.
Analyze the provided content and generate SEO metadata optimized for maximum Click-Through Rate (CTR).

Your output MUST be a valid JSON object with these fields:
- "seo_title": A compelling, click-worthy title (max 60 chars) optimized for search engines
- "description": A persuasive meta description (max 160 chars) with high-value search terms naturally embedded
- "keywords": An array of 5-8 high-relevance keywords/phrases that match current search trends
- "og_title": An Open Graph title optimized for social sharing (can differ from seo_title)

Rules:
- Prioritize clarity and relevance over clickbait
- Include the primary topic keyword in the first 30 chars of the title
- Use natural language that matches search intent
- The description should answer the searcher's likely question
- Output language: {lang_name}
"""

ALIGNMENT_USER_PROMPT = """### Content to Optimize ###
Title: {title}
Body (excerpt):
{text}

### Generate SEO JSON ###"""


class AIAlignmentProcessor(BaseSeoProcessor):
    """🛰️ AI 算法对齐：智能增强模式的默认 SEO 策略。

    利用 AI 深度分析内容语义，生成高 CTR 的标题和描述，
    并将高热搜索词自然埋入元数据，实现对搜索引擎的"精准投喂"。
    """

    def process(self, ctx) -> dict:
        tlog.info(f"🛰️ [AI 算法对齐] 正在为 '{ctx.title}' 执行智能 SEO 投喂...")

        translator = getattr(ctx.engine, 'translator', None)
        if not translator:
            tlog.warning("⚠️ [AI 算法对齐] AI 引擎未就绪，回退至启发式处理")
            from .heuristic import HeuristicSeoProcessor
            return HeuristicSeoProcessor().process(ctx)

        body = getattr(ctx, 'ai_pure_body', '') or getattr(ctx, 'raw_body', '')
        # 截取前 2000 字避免超出 Token 限制
        body_excerpt = body[:2000] if len(body) > 2000 else body
        
        source_lang = getattr(ctx, 'source_lang', 'zh')
        from core.utils.language_hub import LanguageHub
        lang_name = LanguageHub.resolve_to_name(source_lang)

        seo_result = {}

        try:
            # 构建 AI 请求
            from core.adapters.ai.payload_manager import PayloadManager
            system_prompt = ALIGNMENT_SYSTEM_PROMPT.format(lang_name=lang_name)
            user_content = ALIGNMENT_USER_PROMPT.format(
                title=ctx.title,
                text=body_excerpt
            )
            payload = PayloadManager.prepare_payload(
                translator, system_prompt, user_content, is_json=True
            )
            if "params" not in payload:
                payload["params"] = {}
            payload["params"]["max_tokens"] = 512

            # 调用 AI
            raw_response = translator.ask_ai_with_retry(payload)
            repaired = AILogicHub.repair_json(raw_response)
            data = json.loads(repaired)

            # 提取结果
            if data.get('seo_title'):
                seo_result['og_title'] = data['seo_title'][:self.MAX_TITLE_LENGTH]
            if data.get('description'):
                seo_result['description'] = data['description'][:self.MAX_DESCRIPTION_LENGTH]
            if data.get('keywords'):
                kw = data['keywords']
                if isinstance(kw, str):
                    kw = [k.strip() for k in kw.split(',') if k.strip()]
                seo_result['keywords'] = kw[:self.MAX_KEYWORDS_COUNT]
            if data.get('og_title'):
                seo_result['og_title'] = data['og_title'][:self.MAX_TITLE_LENGTH]

            tlog.info(f"✅ [AI 算法对齐] 投喂完成，生成字段: {list(seo_result.keys())}")

        except Exception as e:
            tlog.warning(f"⚠️ [AI 算法对齐] AI 处理异常: {e}，回退至启发式")
            from .heuristic import HeuristicSeoProcessor
            return HeuristicSeoProcessor().process(ctx)

        # 应用元数据优先原则
        seo_result = self._respect_frontmatter(ctx.fm_dict, seo_result)
        return seo_result
