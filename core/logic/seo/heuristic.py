#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Heuristic SEO Processor
职责：基础出版模式的「结构化启发提取」策略。
🚀 [V53.0] 无 AI，纯物理规则，离线友好。

处理逻辑：
1. 从 H1 标题提取 title（Frontmatter 优先）
2. 从正文首段提取 description（上限 160 字）
3. 通过词频统计提取 keywords
4. 从文件名推导 slug
"""

import re
import os
from .base import BaseSeoProcessor
from core.utils.tracing import tlog


class HeuristicSeoProcessor(BaseSeoProcessor):
    """📜 结构化启发提取：基础出版模式的默认 SEO 策略。
    
    纯物理规则，零 AI 依赖，零网络调用。
    适用于离线创作、私密备份、对 API 额度敏感的用户。
    """

    def process(self, ctx) -> dict:
        tlog.info(f"📜 [启发式 SEO] 正在为 '{ctx.title}' 执行结构化提取...")
        
        seo_result = {}
        body = getattr(ctx, 'ai_pure_body', '') or getattr(ctx, 'raw_body', '')

        # --- 1. Title 提取 ---
        # 优先级：Frontmatter > H1 > 文件名
        if not ctx.fm_dict.get('title'):
            h1_title = self._extract_h1_title(body)
            if h1_title:
                seo_result['og_title'] = h1_title
                tlog.debug(f"  └── 📝 从 H1 提取标题: {h1_title[:40]}...")
            else:
                # 从文件名推导
                filename = os.path.splitext(os.path.basename(
                    getattr(ctx, 'src_path', 'untitled.md')
                ))[0]
                seo_result['og_title'] = filename.replace('-', ' ').replace('_', ' ').title()
                tlog.debug(f"  └── 📝 从文件名推导标题: {seo_result['og_title']}")

        # --- 2. Description 提取 ---
        if not ctx.fm_dict.get('description'):
            description = self._extract_first_paragraph(body, self.MAX_DESCRIPTION_LENGTH)
            if description:
                seo_result['description'] = description
                tlog.debug(f"  └── 📄 从首段提取描述: {description[:50]}...")
            else:
                # 兜底：截取正文前 160 字
                clean_body = re.sub(r'[#*`\[\]()>!\n]+', ' ', body)
                clean_body = re.sub(r'\s+', ' ', clean_body).strip()
                seo_result['description'] = clean_body[:self.MAX_DESCRIPTION_LENGTH]

        # --- 3. Keywords 提取 ---
        if not ctx.fm_dict.get('keywords'):
            keywords = self._extract_keywords_from_content(body, self.MAX_KEYWORDS_COUNT)
            if keywords:
                seo_result['keywords'] = keywords
                tlog.debug(f"  └── 🏷️ 提取关键词 ({len(keywords)}): {', '.join(keywords[:5])}...")

        # --- 4. 应用元数据优先原则 ---
        seo_result = self._respect_frontmatter(ctx.fm_dict, seo_result)

        tlog.info(f"✅ [启发式 SEO] 提取完成，填充字段: {list(seo_result.keys())}")
        return seo_result
