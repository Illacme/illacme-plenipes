#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Protocol SEO Processor
职责：基础出版模式的「全维协议工程」策略。
🚀 [V53.0] 无 AI，生成标准化的 SEO 协议数据。

处理逻辑：
1. 生成 JSON-LD 结构化数据 (Article / BlogPosting)
2. 生成 Open Graph 社交分享标签
3. 生成 Twitter Card 标签
4. 生成 Canonical URL
5. 与 sitemap_engine.py 协同完成全站 SEO 矩阵
"""

import re
import os
from datetime import datetime
from .base import BaseSeoProcessor
from core.utils.tracing import tlog


class ProtocolSeoProcessor(BaseSeoProcessor):
    """🏗️ 全维协议工程：基础出版模式的进阶 SEO 策略。

    在 Heuristic 的基础上，额外生成符合 W3C 和搜索引擎标准的
    结构化数据协议，提升内容在 SERP 中的"富媒体展现"能力。
    """

    def process(self, ctx) -> dict:
        tlog.info(f"🏗️ [协议工程 SEO] 正在为 '{ctx.title}' 构建全维协议矩阵...")
        
        seo_result = {}
        body = getattr(ctx, 'ai_pure_body', '') or getattr(ctx, 'raw_body', '')
        site_url = getattr(ctx.engine.config, 'site_url', '') or ''

        # --- 1. 基础元数据提取（复用 Heuristic 逻辑） ---
        if not ctx.fm_dict.get('description'):
            seo_result['description'] = self._extract_first_paragraph(
                body, self.MAX_DESCRIPTION_LENGTH
            )
        
        if not ctx.fm_dict.get('keywords'):
            seo_result['keywords'] = self._extract_keywords_from_content(
                body, self.MAX_KEYWORDS_COUNT
            )

        # --- 2. Open Graph 标签生成 ---
        og_title = ctx.fm_dict.get('title') or ctx.title or ''
        og_desc = (
            ctx.fm_dict.get('description')
            or seo_result.get('description', '')
        )
        
        seo_result['og_title'] = og_title
        seo_result['og_description'] = og_desc[:200] if og_desc else ''
        seo_result['og_type'] = 'article'
        seo_result['og_locale'] = getattr(ctx, 'source_lang', 'zh-CN')

        # --- 3. Twitter Card 标签生成 ---
        seo_result['twitter_card'] = 'summary_large_image'
        seo_result['twitter_title'] = og_title
        seo_result['twitter_description'] = og_desc[:200] if og_desc else ''

        # --- 4. Canonical URL 生成 ---
        if site_url and hasattr(ctx, 'slug'):
            route_prefix = getattr(ctx, 'route_prefix', '') or ''
            mapped_sub = getattr(ctx, 'mapped_sub_dir', '') or ''
            parts = [p for p in [site_url.rstrip('/'), route_prefix, mapped_sub, ctx.slug] if p]
            canonical = '/'.join(parts)
            # 清理重复斜杠（保留 https://）
            canonical = re.sub(r'(?<!:)//+', '/', canonical)
            seo_result['canonical_url'] = canonical

        # --- 5. JSON-LD 结构化数据 (Article Schema) ---
        json_ld = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": og_title[:110],  # Schema.org 推荐 110 字符内
            "description": og_desc[:200] if og_desc else '',
            "author": {
                "@type": "Person",
                "name": ctx.fm_dict.get('author', '')
                        or getattr(ctx.engine.config, 'imprint_name', 'Unknown')
            },
            "publisher": {
                "@type": "Organization",
                "name": getattr(ctx.engine.config, 'imprint_name', 'Illacme Press')
            }
        }

        # 日期信息
        date_published = ctx.fm_dict.get('date') or ctx.fm_dict.get('created')
        if date_published:
            json_ld['datePublished'] = str(date_published)
        
        date_modified = ctx.fm_dict.get('updated') or ctx.fm_dict.get('lastmod')
        if date_modified:
            json_ld['dateModified'] = str(date_modified)
        else:
            json_ld['dateModified'] = datetime.now().strftime('%Y-%m-%d')

        # 关键词
        kw = ctx.fm_dict.get('keywords') or seo_result.get('keywords', [])
        if kw:
            json_ld['keywords'] = kw if isinstance(kw, list) else [kw]

        # 字数信息
        word_count = ctx.seo_data.get('word_count', 0)
        if word_count:
            json_ld['wordCount'] = word_count

        seo_result['json_ld'] = json_ld

        # --- 6. Breadcrumb 结构化数据 ---
        if hasattr(ctx, 'mapped_sub_dir') and ctx.mapped_sub_dir:
            breadcrumb_items = []
            parts = ctx.mapped_sub_dir.split('/')
            for i, part in enumerate(parts):
                breadcrumb_items.append({
                    "@type": "ListItem",
                    "position": i + 1,
                    "name": part.replace('-', ' ').title()
                })
            # 最后一项是当前文档
            breadcrumb_items.append({
                "@type": "ListItem",
                "position": len(parts) + 1,
                "name": og_title
            })
            
            seo_result['breadcrumb_ld'] = {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": breadcrumb_items
            }

        # --- 7. 应用元数据优先原则 ---
        seo_result = self._respect_frontmatter(ctx.fm_dict, seo_result)

        tlog.info(
            "✅ [协议工程 SEO] 构建完成: JSON-LD + OG + Twitter Card + Canonical"
        )
        return seo_result
