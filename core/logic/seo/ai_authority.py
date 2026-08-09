#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Authority SEO Processor
职责：智能增强模式的「AI 实体增强」策略。
🚀 [V53.0] 利用 AI 提取知识实体，生成权威结构化数据。

处理逻辑：
1. AI 识别内容中的核心实体（人物、组织、技术、概念）
2. 生成精确的 Schema.org JSON-LD（Article + 实体标注）
3. 建议站内内链策略（基于实体关联）
4. 生成 FAQ 结构化数据（如果内容包含问答）
"""

import json
from datetime import datetime
from .base import BaseSeoProcessor
from core.logic.ai.ai_logic_hub import AILogicHub
from core.utils.tracing import tlog

# 🚀 [V53.0] AI 实体增强专用提示词
AUTHORITY_SYSTEM_PROMPT = """You are an expert in Schema.org structured data and Google E-E-A-T optimization.
Extract knowledge entities from the provided content to build authoritative SEO metadata.

Your output MUST be a valid JSON object with these fields:
- "description": A factual, authority-building meta description (max 160 chars)
- "keywords": An array of 5-8 precise entity-focused keywords
- "entities": An object with arrays for each entity type found:
  - "people": Names of people mentioned
  - "organizations": Organizations, companies, imprints
  - "technologies": Technical terms, frameworks, languages
  - "concepts": Abstract concepts, theories, methodologies
- "faq": An array of FAQ items (if Q&A patterns detected), each with "question" and "answer" fields
- "suggested_links": An array of 2-3 related topic suggestions for internal linking

Rules:
- Focus on factual accuracy and domain expertise signals
- Entities must be specific, not generic
- FAQ answers should be concise (1-2 sentences)
- Output language: {lang_name}
"""

AUTHORITY_USER_PROMPT = """### Content to Analyze ###
Title: {title}
Body (excerpt):
{text}

### Extract Entities and Generate Schema ###"""


class AIAuthorityProcessor(BaseSeoProcessor):
    """🏛️ AI 实体增强：智能增强模式的进阶 SEO 策略。

    利用 AI 提取内容中的知识实体，生成权威的 Schema.org 结构化数据，
    并建议内链策略，提升站点在 Google E-E-A-T 评估中的权重。
    """

    def process(self, ctx) -> dict:
        tlog.info(f"🏛️ [AI 实体增强] 正在为 '{ctx.title}' 构建权威数据...")

        translator = getattr(ctx.engine, 'translator', None)
        if not translator:
            tlog.warning("⚠️ [AI 实体增强] AI 引擎未就绪，回退至协议工程")
            from .protocol import ProtocolSeoProcessor
            return ProtocolSeoProcessor().process(ctx)

        body = getattr(ctx, 'ai_pure_body', '') or getattr(ctx, 'raw_body', '')
        body_excerpt = body[:2500] if len(body) > 2500 else body

        source_lang = getattr(ctx, 'source_lang', 'zh')
        from core.utils.language_hub import LanguageHub
        lang_name = LanguageHub.resolve_to_name(source_lang)

        seo_result = {}

        try:
            from core.adapters.ai.payload_manager import PayloadManager
            system_prompt = AUTHORITY_SYSTEM_PROMPT.format(lang_name=lang_name)
            user_content = AUTHORITY_USER_PROMPT.format(
                title=ctx.title,
                text=body_excerpt
            )
            payload = PayloadManager.prepare_payload(
                translator, system_prompt, user_content, is_json=True
            )
            if "params" not in payload:
                payload["params"] = {}
            payload["params"]["max_tokens"] = 1024

            raw_response = translator.ask_ai_with_retry(payload)
            repaired = AILogicHub.repair_json(raw_response)
            data = json.loads(repaired)

            # --- 基础 SEO 字段 ---
            if data.get('description'):
                seo_result['description'] = data['description'][:self.MAX_DESCRIPTION_LENGTH]
            if data.get('keywords'):
                kw = data['keywords']
                if isinstance(kw, str):
                    kw = [k.strip() for k in kw.split(',') if k.strip()]
                seo_result['keywords'] = kw[:self.MAX_KEYWORDS_COUNT]

            # --- JSON-LD: Article + 实体标注 ---
            og_title = ctx.fm_dict.get('title') or ctx.title or ''
            json_ld = {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": og_title[:110],
                "description": seo_result.get('description', ''),
                "author": {
                    "@type": "Person",
                    "name": ctx.fm_dict.get('author', '')
                            or getattr(ctx.engine.config, 'imprint_name', 'Unknown')
                },
                "publisher": {
                    "@type": "Organization",
                    "name": getattr(ctx.engine.config, 'imprint_name', 'Illacme Press')
                },
                "dateModified": datetime.now().strftime('%Y-%m-%d')
            }

            # 注入实体作为 about / mentions
            entities = data.get('entities', {})
            about_items = []
            for etype, items in entities.items():
                if not isinstance(items, list):
                    continue
                for item in items[:5]:
                    schema_type = {
                        'people': 'Person',
                        'organizations': 'Organization',
                        'technologies': 'SoftwareApplication',
                        'concepts': 'DefinedTerm'
                    }.get(etype, 'Thing')
                    about_items.append({
                        "@type": schema_type,
                        "name": str(item)
                    })

            if about_items:
                json_ld['about'] = about_items
            
            seo_result['json_ld'] = json_ld

            # --- FAQ 结构化数据 ---
            faq_items = data.get('faq', [])
            if faq_items and isinstance(faq_items, list):
                faq_ld = {
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "mainEntity": []
                }
                for faq in faq_items[:5]:
                    if faq.get('question') and faq.get('answer'):
                        faq_ld["mainEntity"].append({
                            "@type": "Question",
                            "name": faq['question'],
                            "acceptedAnswer": {
                                "@type": "Answer",
                                "text": faq['answer']
                            }
                        })
                if faq_ld["mainEntity"]:
                    seo_result['faq_ld'] = faq_ld

            # --- 内链建议 ---
            suggestions = data.get('suggested_links', [])
            if suggestions:
                seo_result['internal_link_suggestions'] = suggestions[:5]

            tlog.info(
                f"✅ [AI 实体增强] 完成: "
                f"{len(about_items)} 实体, "
                f"{len(faq_items)} FAQ, "
                f"{len(suggestions)} 内链建议"
            )

        except Exception as e:
            tlog.warning(f"⚠️ [AI 实体增强] AI 处理异常: {e}，回退至协议工程")
            from .protocol import ProtocolSeoProcessor
            return ProtocolSeoProcessor().process(ctx)

        seo_result = self._respect_frontmatter(ctx.fm_dict, seo_result)
        return seo_result
