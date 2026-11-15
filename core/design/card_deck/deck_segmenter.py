# -*- coding: utf-8 -*-
"""
📑 CardDeck Core - Markdown Document Segmenter
职责：将 Markdown 原稿根据结构（标题、列表、金句、段落）智能切分为小红书/社交卡片幻灯数据。
特性：
1. 提取封面元数据（标题、摘要、作者、品牌名、总张数）；
2. 依据二级标题(##)与要点列表拆分为独立知识卡片；
3. 智能保底自愈：针对短文或无标题文稿自动聚类分页；
4. 结尾生成互动与核心速览收束卡；
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class DeckCardData:
    """单张知识幻灯卡片的数据载荷"""
    index: int                          # 当前卡片序号 (从 1 开始)
    total: int                          # 总卡片数量
    card_type: str                      # "cover" | "content" | "closing"
    title: str                          # 卡片主标题
    subtitle: str = ""                  # 副标题 / 引言
    points: List[str] = field(default_factory=list)  # 核心要点列表
    quote: str = ""                     # 金句 / 引用
    body_text: str = ""                 # 辅助解释段落
    category: str = "笔记精选"           # 分类徽标
    author: str = "创作者"               # 作者标识
    brand_name: str = "SOVEREIGN PRESS" # 出版品牌标识


def _clean_markdown_syntax(text: str) -> str:
    """清理 Markdown 行内语法标记（链接、粗体、代码块等），保留纯文本"""
    if not text:
        return ""
    t = str(text).strip()
    # 移除图片语法 ![alt](url)
    t = re.sub(r'!\[.*?\]\(.*?\)', '', t)
    # 移除超链接保留文字 [text](url) -> text
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)
    # 移除行内代码 `code` -> code
    t = re.sub(r'`([^`]+)`', r'\1', t)
    # 移除粗体和斜体 **bold** / *italic*
    t = re.sub(r'[*_]{1,3}([^*_]+)[*_]{1,3}', r'\1', t)
    # 移除行内 HTML 标签
    t = re.sub(r'<[^>]+>', '', t)
    return " ".join(t.split())


class DeckSegmenter:
    """Markdown 原稿智能切片分析中枢"""

    @classmethod
    def segment_document(
        cls,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        max_cards: int = 6
    ) -> List[DeckCardData]:
        """将 Markdown 正文切分为一组 DeckCardData (卡片张数控制在 3 ~ max_cards 之间)"""
        meta = metadata or {}
        clean_max = max(3, min(9, int(max_cards or 6)))

        # 1. 提取标题、作者、分类、摘要
        title = meta.get("title") or ""
        if not title:
            h1_m = re.search(r'^\s*#\s+(.+)$', content, re.MULTILINE)
            if h1_m:
                title = h1_m.group(1).strip()
            else:
                title = "知识卡片精选"
        title = _clean_markdown_syntax(title)

        author = meta.get("author") or "创作者"
        category = meta.get("category") or "深度干货"
        brand_name = meta.get("brand_name") or "ILLACME SOVEREIGN"

        digest = meta.get("description") or meta.get("digest") or ""
        if not digest:
            # 尝试抓取正文第一段有意义文字
            paras = [p.strip() for p in content.split("\n\n") if p.strip() and not p.strip().startswith("#")]
            digest = paras[0] if paras else "一文提炼核心精髓，深度干货整理速览。"
        digest = _clean_markdown_syntax(digest)[:120]

        # 2. 提取中间内容卡片 (根据 ## 分段，或根据段落聚合)
        content_sections = cls._extract_sections(content)

        # 控制中间内容卡片数量上限 (max_cards - 2 为内容卡预留容量)
        max_content_cards = max(1, clean_max - 2)
        if len(content_sections) > max_content_cards:
            content_sections = content_sections[:max_content_cards]
        elif not content_sections:
            # 自愈保底：如果没有任何小节，把正文聚合成 1~2 张卡
            content_sections = cls._fallback_sections(content)

        total_cards = len(content_sections) + 2  # 1 cover + N content + 1 closing

        cards: List[DeckCardData] = []

        # ── 第 1 张：封面卡片 ──────────────────────────────────────────
        cards.append(DeckCardData(
            index=1,
            total=total_cards,
            card_type="cover",
            title=title,
            subtitle=digest,
            category=category,
            author=author,
            brand_name=brand_name
        ))

        # ── 第 2 ~ N 张：知识内容卡片 ───────────────────────────────────
        for idx, sec in enumerate(content_sections, start=2):
            cards.append(DeckCardData(
                index=idx,
                total=total_cards,
                card_type="content",
                title=sec.get("title", f"核心要点 0{idx-1}"),
                subtitle=sec.get("subtitle", ""),
                points=sec.get("points", []),
                quote=sec.get("quote", ""),
                body_text=sec.get("body", ""),
                category=category,
                author=author,
                brand_name=brand_name
            ))

        # ── 最后 1 张：总结与收尾卡片 ───────────────────────────────────
        cards.append(DeckCardData(
            index=total_cards,
            total=total_cards,
            card_type="closing",
            title="核心总结 · 记忆速记",
            subtitle="精要提炼，融会贯通",
            points=[
                f"全文共提炼了 {len(content_sections)} 个核心认知要点",
                "关注出版主权工作台，获取全模态深度知识衍生",
                "收藏本篇卡片，随时回顾与实战落地"
            ],
            quote="“把知识沉淀为带不走的私有资产，在创作中见证生长。”",
            category=category,
            author=author,
            brand_name=brand_name
        ))

        return cards

    @classmethod
    def _extract_sections(cls, content: str) -> List[Dict[str, Any]]:
        """从 Markdown 中提取基于二级标题 (##) 的知识分段"""
        sections: List[Dict[str, Any]] = []
        raw_sections = re.split(r'\n(?=##\s+)', content)

        for chunk in raw_sections:
            chunk = chunk.strip()
            if not chunk or not chunk.startswith("## "):
                continue

            lines = chunk.splitlines()
            header_line = lines[0]
            sec_title = _clean_markdown_syntax(header_line.replace("##", "").strip())
            body_lines = lines[1:]

            points: List[str] = []
            quotes: List[str] = []
            para_lines: List[str] = []

            for l in body_lines:
                sl = l.strip()
                if not sl:
                    continue
                if sl.startswith(("- ", "* ", "+ ")) or re.match(r'^\d+\.\s+', sl):
                    cleaned_p = _clean_markdown_syntax(re.sub(r'^([-*+]|\d+\.)\s+', '', sl))
                    if cleaned_p and len(points) < 4:
                        points.append(cleaned_p[:60])
                elif sl.startswith(">"):
                    cleaned_q = _clean_markdown_syntax(sl.lstrip(">").strip())
                    if cleaned_q and len(quotes) < 2:
                        quotes.append(cleaned_q[:80])
                elif not sl.startswith("#") and not sl.startswith("```"):
                    if len(para_lines) < 3:
                        para_lines.append(_clean_markdown_syntax(sl))

            quote_text = " ".join(quotes) if quotes else ""
            body_text = " ".join(para_lines)[:140] if para_lines else ""

            # 如果既没有列表也没有引用，就把正文前两句作为 points
            if not points and body_text:
                sentences = [s.strip() for s in re.split(r'[。！？.!?]', body_text) if s.strip()]
                points = sentences[:3]

            sections.append({
                "title": sec_title[:32],
                "points": points[:4],
                "quote": quote_text,
                "body": body_text
            })

        return sections

    @classmethod
    def _fallback_sections(cls, content: str) -> List[Dict[str, Any]]:
        """当文稿没有清晰标题时，依据自然段落进行自愈聚合"""
        paragraphs = [
            _clean_markdown_syntax(p)
            for p in content.split("\n\n")
            if p.strip() and not p.strip().startswith("#") and not p.strip().startswith("```")
        ]
        paragraphs = [p for p in paragraphs if len(p) > 20]

        if not paragraphs:
            return [{
                "title": "精要洞察",
                "points": ["提炼核心思维模型", "建立端到端闭环实践", "持续迭代与资产复用"],
                "quote": "“博观而约取，厚积而薄发。”",
                "body": "文章内容已由出版引擎提炼为便携卡片形态。"
            }]

        sections = []
        for i, p in enumerate(paragraphs[:3], start=1):
            sentences = [s.strip() for s in re.split(r'[。！？.!?]', p) if s.strip()]
            sections.append({
                "title": f"关键洞察 0{i}",
                "points": sentences[:3] if len(sentences) >= 2 else [p[:60]],
                "quote": "",
                "body": p[:120]
            })
        return sections

