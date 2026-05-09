#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SEO Processor Base Class
职责：定义所有 SEO 处理器的抽象接口与通用工具方法。
🚀 [V53.0] 出版模式矩阵基座。

所有 SEO 处理器必须遵守"元数据优先 (Frontmatter Priority)" 底线：
如果 Markdown 原稿 Frontmatter 中已定义 title/description/slug 等字段，
处理器不得覆盖，仅可在缺失时补充。
"""

import re
from abc import ABC, abstractmethod
from core.utils.tracing import tlog


class BaseSeoProcessor(ABC):
    """SEO 处理器抽象基类
    
    所有策略（Heuristic / Protocol / AI Alignment 等）均需继承此类，
    实现 `process` 方法。
    """

    # 🛡️ SEO 物理常量
    MAX_TITLE_LENGTH = 60       # Google 推荐的标题长度上限
    MAX_DESCRIPTION_LENGTH = 160  # Google 推荐的描述长度上限
    MAX_KEYWORDS_COUNT = 10     # 关键词数量上限

    @abstractmethod
    def process(self, ctx) -> dict:
        """执行 SEO 处理并返回增强后的元数据字典。
        
        Args:
            ctx: 编辑管线上下文 (EditorialContext)，包含：
                - ctx.title: 文档标题
                - ctx.raw_body: 原始正文（Markdown 格式）
                - ctx.ai_pure_body: 去噪后的纯文本
                - ctx.fm_dict: Frontmatter 字典
                - ctx.seo_data: 现有 SEO 数据（可能含 word_count 等物理指标）
                - ctx.slug: 当前 Slug
                - ctx.engine: 引擎实例引用
        
        Returns:
            dict: SEO 增强数据，可能包含：
                - description: str
                - keywords: list[str]
                - og_title: str
                - og_description: str
                - og_image: str
                - json_ld: dict
                - canonical_url: str
        """
        raise NotImplementedError

    def _respect_frontmatter(self, fm_dict: dict, seo_result: dict) -> dict:
        """🛡️ 元数据优先原则：Frontmatter 中已定义的字段不被覆盖。
        
        Args:
            fm_dict: 用户在 Markdown Frontmatter 中手写的元数据
            seo_result: 处理器自动生成的 SEO 数据
        
        Returns:
            dict: 合并后的最终 SEO 数据（用户手写优先）
        """
        protected_fields = ['title', 'description', 'keywords', 'slug', 'canonical']
        
        for field in protected_fields:
            if fm_dict.get(field):
                # 用户手动定义的优先级最高，覆盖自动生成的
                seo_result[field] = fm_dict[field]
                tlog.debug(f"  └── 🛡️ [元数据优先] '{field}' 保留用户手动定义值")
        
        return seo_result

    @staticmethod
    def _extract_first_paragraph(body: str, max_length: int = 160) -> str:
        """从正文中提取第一个有效段落作为描述。
        
        跳过标题行 (#)、空行和代码块，抓取第一个纯文本段落。
        """
        lines = body.split('\n')
        in_code_block = False
        paragraph_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            # 跳过代码块
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            
            # 跳过标题行
            if stripped.startswith('#'):
                continue
            
            # 跳过空行（但如果已经积累了段落内容则结束）
            if not stripped:
                if paragraph_lines:
                    break
                continue
            
            # 跳过图片、链接等纯 Markdown 结构
            if stripped.startswith('![') or stripped.startswith('> '):
                continue
            
            paragraph_lines.append(stripped)
        
        if not paragraph_lines:
            return ""
        
        # 合并段落并剥离 Markdown 格式
        raw_text = ' '.join(paragraph_lines)
        # 移除内联 Markdown 格式（粗体、斜体、行内代码、链接等）
        clean = re.sub(r'\*\*(.+?)\*\*', r'\1', raw_text)  # 粗体
        clean = re.sub(r'\*(.+?)\*', r'\1', clean)          # 斜体
        clean = re.sub(r'`(.+?)`', r'\1', clean)            # 行内代码
        clean = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', clean)   # 链接
        clean = re.sub(r'\s+', ' ', clean).strip()           # 多余空白
        
        # 截断至最大长度，保持语义完整（在句号或逗号处断开）
        if len(clean) <= max_length:
            return clean
        
        truncated = clean[:max_length]
        # 尝试在最后一个句号、问号、逗号处截断
        for sep in ['。', '？', '！', '. ', '? ', '! ', '，', ', ']:
            last_pos = truncated.rfind(sep)
            if last_pos > max_length * 0.5:  # 至少保留 50% 的内容
                return truncated[:last_pos + len(sep)].strip()
        
        return truncated.strip() + '...'

    @staticmethod
    def _extract_h1_title(body: str) -> str:
        """从正文中提取第一个 H1 标题"""
        match = re.search(r'^#\s+(.+?)$', body, re.MULTILINE)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _extract_keywords_from_content(body: str, max_count: int = 10) -> list:
        """通过词频统计从正文中提取高频关键词（无 AI 版本）。
        
        策略：
        1. 剥离所有 Markdown 格式
        2. 按中英文分词统计词频
        3. 过滤停用词后返回 Top N
        """
        # 剥离 Markdown 格式
        clean = re.sub(r'[#*`\[\]()>!]', ' ', body)
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        # 英文单词提取
        en_words = re.findall(r'[a-zA-Z]{3,}', clean.lower())
        # 中文词组提取（简单的 2-4 字切分）
        zh_phrases = re.findall(r'[\u4e00-\u9fa5]{2,4}', clean)
        
        # 英文停用词过滤
        en_stopwords = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'can', 'had', 'her', 'was', 'one', 'our', 'out', 'has',
            'have', 'been', 'from', 'this', 'that', 'with', 'they',
            'will', 'each', 'make', 'like', 'been', 'long', 'very',
            'when', 'what', 'your', 'how', 'about', 'which', 'their',
            'some', 'would', 'them', 'than', 'its', 'into', 'more',
            'other', 'also', 'use', 'using', 'used',
        }
        
        filtered_en = [w for w in en_words if w not in en_stopwords]
        
        # 统计词频
        freq = {}
        for w in filtered_en + zh_phrases:
            freq[w] = freq.get(w, 0) + 1
        
        # 按频率排序，取 Top N
        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_words[:max_count]]
