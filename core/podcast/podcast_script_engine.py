# -*- coding: utf-8 -*-
"""
🎙️ Podcast Script Engine - Dual-Host Conversational Script Extractor
职责：将 Markdown 原稿提炼为双人对话式技术播客剧本（Host A 架构讲师 & Host B 敏锐提问）。
特性：
1. 双人角色分工：沉稳专业讲解 vs 敏锐好奇追问；
2. 多风格剧本模式：tech_deep (深度剖析), casual_brief (通俗快讯), debate (观点交锋)；
3. 多语言原生支持：中文 (zh), 英文 (en), 日文 (ja) 自然口语化模板；
4. 离线启发式规则兜底：零大模型也能 100% 秒级产出高质对话。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import re
from typing import List, Dict, Any, Optional

from .podcast_models import DialogueTurn, PodcastScript, PodcastChapter
from .podcast_style_templates import (
    TOPIC_MAP,
    build_intro_turns,
    build_discussion_turns,
    build_outro_turns
)

# 对外导出，保持向后兼容
__all__ = ["PodcastScriptEngine", "DialogueTurn", "PodcastScript"]


def _clean_text(text: str) -> str:
    """清洗 Markdown 符号，保留适宜朗读的纯文本"""
    if not text:
        return ""
    t = str(text).strip()
    t = re.sub(r'!\[.*?\]\(.*?\)', '', t)
    t = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', t)
    t = re.sub(r'`([^`]+)`', r'\1', t)
    t = re.sub(r'[*_]{1,3}([^*_]+)[*_]{1,3}', r'\1', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'^[\s\-\*\d\.\>]+', '', t, flags=re.MULTILINE)
    return " ".join(t.split())


class PodcastScriptEngine:
    """双人对谈剧本提炼中枢"""

    DEFAULT_NAMES = {
        "zh": {"host_a": "晓晓", "host_b": "云希"},
        "en": {"host_a": "Jenny", "host_b": "Guy"},
        "ja": {"host_a": "七海", "host_b": "圭太"}
    }

    @classmethod
    def extract_script(
        cls,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        lang: str = "zh",
        style: str = "tech_deep",
        max_turns: int = 12,
        use_ai: bool = False,
        engine: Any = None
    ) -> PodcastScript:
        """主入口：从 Markdown 提取双人对话剧本（支持极速规则或大模型深度编剧）"""
        meta = metadata or {}
        lang_code = lang.lower() if lang else "zh"
        if not lang_code.startswith(("zh", "en", "ja")):
            lang_code = "zh" if any('\u4e00' <= c <= '\u9fff' for c in content[:500]) else "en"

        if use_ai and engine:
            from .podcast_ai_writer import PodcastAIWriter
            return PodcastAIWriter.generate_script(
                engine=engine,
                content=content,
                metadata=meta,
                lang=lang_code,
                style=style,
                max_turns=max_turns
            )

        names = cls.DEFAULT_NAMES.get(lang_code, cls.DEFAULT_NAMES["en"])
        title = meta.get("title") or cls._extract_title(content) or ("技术前沿探索" if lang_code == "zh" else "Tech Insights")
        summary = meta.get("description") or meta.get("summary") or ""

        # 解析正文结构（自动剔除表格与代码块）
        sections = cls._parse_markdown_sections(content, lang=lang_code)
        turns: List[DialogueTurn] = []

        # 1. 开场白 (Intro)
        turns.extend(cls._build_intro(title, summary, lang_code, style, names))

        # 2. 章节交替深度探讨 (Discussion turns)
        turns.extend(cls._build_discussion(sections, lang_code, style, names, max_turns - 4))

        # 3. 总结收尾 (Outro)
        turns.extend(cls._build_outro(title, lang_code, style, names))

        # 估算朗读时长 (中文 ~3.5 字/秒，英文 ~2.5 词/秒)
        total_len = sum(len(t.text) for t in turns)
        est_sec = max(30, int(total_len / (3.5 if lang_code == "zh" else 2.5)))
        default_topic = TOPIC_MAP.get(style, TOPIC_MAP["tech_deep"]).get(lang_code, "Engineering")

        chapters = cls.build_chapters(turns, sections, lang=lang_code)

        return PodcastScript(
            title=title,
            topic=meta.get("category") or default_topic,
            lang=lang_code,
            style=style,
            turns=turns,
            summary=summary,
            estimated_duration_sec=est_sec,
            chapters=chapters,
            sections=sections
        )

    @classmethod
    def build_chapters(
        cls,
        turns: List[DialogueTurn],
        sections: List[Dict[str, Any]],
        lang: str = "zh",
        turn_durations_ms: Optional[List[int]] = None
    ) -> List[PodcastChapter]:
        """构建结构化章节时间轴（支持估算或真实毫秒级校准）"""
        if not turns:
            return []
        intro_lbl = "话题引入与背景" if lang == "zh" else ("イントロダクション" if lang == "ja" else "Introduction & Context")
        chapters = [PodcastChapter(title=intro_lbl, start_seconds=0, start_time="00:00")]

        turn_start_sec = [0] * len(turns)
        cur_ms = 0
        speed = 3.5 if lang == "zh" else 2.5
        for i, t in enumerate(turns):
            turn_start_sec[i] = int(cur_ms / 1000)
            if turn_durations_ms and i < len(turn_durations_ms):
                cur_ms += turn_durations_ms[i] + 400
            else:
                dur_sec = max(2.0, len(t.text) / speed)
                cur_ms += int(dur_sec * 1000) + 400

        sec_idx, last_sec = 0, -1
        for i, t in enumerate(turns):
            if t.intent == "intro":
                continue
            if t.intent in ("outro", "summary"):
                if not any(c.title.startswith(("总结", "まとめ", "Summary")) for c in chapters):
                    outro_lbl = "总结与行动指南" if lang == "zh" else ("まとめとアクション" if lang == "ja" else "Summary & Takeaways")
                    chapters.append(PodcastChapter(
                        title=outro_lbl, start_seconds=turn_start_sec[i],
                        start_time=PodcastChapter.format_timestamp(turn_start_sec[i])
                    ))
            elif sec_idx < len(sections) and sec_idx != last_sec:
                head = sections[sec_idx].get("heading")
                if head:
                    chapters.append(PodcastChapter(
                        title=head, start_seconds=turn_start_sec[i],
                        start_time=PodcastChapter.format_timestamp(turn_start_sec[i])
                    ))
                    last_sec = sec_idx
                sec_idx += 1

        if len(chapters) <= 1 and len(turns) >= 4:
            total_sec = turn_start_sec[-1]
            step_sec = max(60, total_sec // 3)
            for s in range(step_sec, total_sec, step_sec):
                idx = len(chapters) + 1
                chapters.append(PodcastChapter(
                    title=f"核心议题 {idx}" if lang == "zh" else f"Key Topic {idx}",
                    start_seconds=s, start_time=PodcastChapter.format_timestamp(s)
                ))
        return chapters

    @classmethod
    def _extract_title(cls, content: str) -> str:
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("# "):
                return _clean_text(line[2:])
        return ""

    @classmethod
    def _parse_markdown_sections(cls, content: str, lang: str = "zh") -> List[Dict[str, Any]]:
        """按标题拆解章节，自动剔除表格、代码块及纯符号行"""
        lines = content.splitlines()
        sections = []
        cur_heading = ""
        cur_paras: List[str] = []
        in_code_block = False

        for line in lines:
            line_s = line.strip()
            if line_s.startswith("```") or line_s.startswith("~~~"):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            if line_s.startswith("|") or line_s.endswith("|") or line_s.count("|") >= 2 or "|---" in line_s or line_s in ("---", "***", "___"):
                continue
            if line_s.startswith("<!--") or line_s.startswith("</") or (line_s.startswith("<") and line_s.endswith(">")):
                continue

            if line_s.startswith("## ") or line_s.startswith("### "):
                if cur_heading and cur_paras:
                    sections.append({"heading": cur_heading, "body": cur_paras})
                cur_heading = _clean_text(line_s.lstrip("#").strip())
                cur_paras = []
            elif line_s:
                clean = _clean_text(line_s)
                clean_no_sym = re.sub(r'[\W_]+', '', clean)
                if len(clean) >= 15 and len(clean_no_sym) >= 4:
                    cur_paras.append(clean)

        if cur_heading and cur_paras:
            sections.append({"heading": cur_heading, "body": cur_paras})

        # 保底：若无标题，则按段落群归类
        if not sections and cur_paras:
            chunk_size = max(1, len(cur_paras) // 3)
            for i in range(0, len(cur_paras), chunk_size):
                idx = i // chunk_size + 1
                h_name = f"核心要点 {idx}" if lang == "zh" else (f"重要ポイント {idx}" if lang == "ja" else f"Key Takeaway {idx}")
                sections.append({
                    "heading": h_name,
                    "body": cur_paras[i:i + chunk_size]
                })
        return sections

    @classmethod
    def _build_intro(
        cls, title: str, summary: str, lang: str, style: str, names: Dict[str, str]
    ) -> List[DialogueTurn]:
        """构建开场台词"""
        return build_intro_turns(title, summary, lang, style, names)

    @classmethod
    def _build_discussion(
        cls, sections: List[Dict[str, Any]], lang: str, style: str, names: Dict[str, str], max_turns: int
    ) -> List[DialogueTurn]:
        """构建多轮交替探讨"""
        return build_discussion_turns(sections, lang, style, names, max_turns)

    @classmethod
    def _build_outro(
        cls, title: str, lang: str, style: str, names: Dict[str, str]
    ) -> List[DialogueTurn]:
        """构建收束台词"""
        return build_outro_turns(title, lang, style, names)
