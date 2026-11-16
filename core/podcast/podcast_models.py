# -*- coding: utf-8 -*-
"""
🎙️ Podcast Data Models
职责：定义双人对话播客台词 (DialogueTurn)、剧本结构 (PodcastScript) 与章节时间戳 (PodcastChapter)。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import os
from pydantic import BaseModel


def resolve_podcast_slug(
    rel_path: str,
    explicit_slug: str = "",
    engine: Any = None,
    snapshot: Optional[Dict[str, Any]] = None,
) -> str:
    """生成无冲突的播客物理文件名前缀：子目录 index/readme 或跨目录同名原稿采用 docs__index 消歧"""
    clean_rel = (rel_path or "").replace("\\", "/").strip("/")
    base = os.path.splitext(os.path.basename(clean_rel))[0]
    rel_no_ext = os.path.splitext(clean_rel)[0]
    if "/" in rel_no_ext:
        if base.lower() in ("index", "readme"):
            return rel_no_ext.replace("/", "__")
        snap = snapshot
        if not isinstance(snap, dict) and engine and hasattr(engine, "meta") and hasattr(engine.meta, "get_documents_snapshot"):
            try:
                snap = engine.meta.get_documents_snapshot()
            except Exception:
                snap = {}
        if isinstance(snap, dict):
            same_stem = [
                rp for rp in snap.keys()
                if os.path.splitext(os.path.basename(rp))[0].lower() == base.lower()
            ]
            if len(same_stem) > 1:
                return rel_no_ext.replace("/", "__")
    return explicit_slug or base or "episode"


def get_podcast_candidate_slugs(
    rel_path: str = "",
    explicit_slug: str = "",
    file_slug: str = "",
    vault_dir: str = "",
) -> List[str]:
    """构建播客音频匹配候选前缀列表：对子目录 index/readme 优先匹配路径限定名 (如 docs__index)"""
    clean_rel = (rel_path or "").replace("\\", "/")
    if os.path.isabs(clean_rel) and vault_dir:
        try:
            clean_rel = os.path.relpath(clean_rel, os.path.abspath(vault_dir)).replace("\\", "/")
        except Exception:
            pass
    clean_rel = clean_rel.strip("/")
    base = os.path.splitext(os.path.basename(clean_rel))[0] if clean_rel else file_slug
    rel_no_ext = os.path.splitext(clean_rel)[0] if clean_rel else ""
    rel_slug = rel_no_ext.replace("/", "__") if "/" in rel_no_ext else ""
    if base and base.lower() in ("index", "readme") and rel_slug:
        raw_list = [rel_slug, explicit_slug]
    else:
        raw_list = [rel_slug, explicit_slug, file_slug, base]
    cands: List[str] = []
    for s in raw_list:
        if s and s not in cands:
            cands.append(s)
    return cands


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
