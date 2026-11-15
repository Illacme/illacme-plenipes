# -*- coding: utf-8 -*-
"""
🎙️ Podcast Data Models
职责：定义双人对话播客台词 (DialogueTurn)、剧本结构 (PodcastScript) 与章节时间戳 (PodcastChapter)。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel


@dataclass
class DialogueTurn:
    """单条播客台词载荷"""
    speaker: str               # "host_a" | "host_b"
    speaker_name: str          # 角色名，如 "晓晓" / "云希" 或 "Jenny" / "Guy"
    text: str                  # 播客台词内容
    intent: str = "dialogue"   # "intro" | "question" | "explanation" | "contrast" | "summary" | "outro"


@dataclass
class PodcastChapter:
    """播客章节时间戳标记 (Podcasting 2.0 & Show Notes 标准)"""
    title: str
    start_seconds: int = 0
    start_time: str = "00:00"
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "start_seconds": self.start_seconds,
            "start_time": self.start_time,
            "description": self.description
        }

    @staticmethod
    def format_timestamp(seconds: int) -> str:
        """秒数转标准 mm:ss 格式"""
        sec = max(0, int(seconds))
        m = sec // 60
        s = sec % 60
        return f"{m:02d}:{s:02d}"

    @classmethod
    def format_shownotes_timeline(cls, chapters: List["PodcastChapter"]) -> str:
        """生成小宇宙、Apple、Spotify 标准识别的 Show Notes 时间轴文本"""
        if not chapters:
            return ""
        lines = ["⏱️ 节目时间轴 (Chapters):"]
        for c in chapters:
            t = c.start_time or cls.format_timestamp(c.start_seconds)
            lines.append(f"{t} {c.title}")
        return "\n".join(lines)


@dataclass
class PodcastScript:
    """完整播客对谈剧本"""
    title: str
    topic: str
    lang: str = "zh"
    style: str = "tech_deep"
    turns: List[DialogueTurn] = field(default_factory=list)
    summary: str = ""
    estimated_duration_sec: int = 0
    chapters: List[PodcastChapter] = field(default_factory=list)
    sections: List[Dict[str, Any]] = field(default_factory=list)


class ScriptExtractRequest(BaseModel):
    rel_path: Optional[str] = None
    content: Optional[str] = None
    lang: Optional[str] = "zh"
    style: Optional[str] = "tech_deep"
    max_turns: Optional[int] = 10
    use_ai: Optional[bool] = False


class TurnPayload(BaseModel):
    speaker: str
    speaker_name: str
    text: str
    intent: Optional[str] = "dialogue"


class PodcastSynthesizeRequest(BaseModel):
    rel_path: str
    title: str
    turns: List[TurnPayload]
    lang: Optional[str] = "zh"
    style: Optional[str] = "tech_deep"
    voice_a: Optional[str] = None
    voice_b: Optional[str] = None
    pause_ms: Optional[int] = 400
    rate: Optional[str] = "+0%"
    pitch: Optional[str] = "+0Hz"
    bgm_style: Optional[str] = "cyber_ambient"
