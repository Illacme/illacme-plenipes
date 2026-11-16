# -*- coding: utf-8 -*-
"""
🎙️ Podcast RSS Feed Generator - Standard RSS 2.0 & Apple / Xiaoyuzhou Feed
职责：将出版发行的各期播客单轨音频汇聚生成标准且合规的 RSS 2.0 / iTunes 播客订阅源 (podcast.xml)。
特性：
1. 工业级播客规范兼容：兼容 Apple Podcasts, Spotify, 小宇宙 (Xiaoyuzhou), Google Podcasts;
2. 多语种隔离：支持独立按母语及多语种生成对应频道的播客 Feed;
3. 动态媒体载荷：包含 <enclosure> 字节长度、MIME 类型及 itunes:duration 时长;
4. 容错回退机制：缺省字段自动由品牌母本信息兜底补齐。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import xml.etree.ElementTree as ET


@dataclass
class PodcastEpisode:
    """单期播客节目载荷"""
    title: str
    audio_url: str
    audio_size_bytes: int
    duration_sec: int
    pub_date: datetime
    description: str = ""
    guid: str = ""
    link: str = ""
    cover_image_url: str = ""
    episode_num: Optional[int] = None
    chapters: List[Dict[str, Any]] = field(default_factory=list)
    shownotes: str = ""


class PodcastRSSGenerator:
    """标准播客 RSS 订阅源生成中枢"""

    @classmethod
    def format_duration(cls, seconds: int) -> str:
        """格式化时长为 HH:MM:SS 或 MM:SS"""
        m, s = divmod(max(0, int(seconds)), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    @classmethod
    def format_rfc822(cls, dt: datetime) -> str:
        """格式化日期为 RFC 822 规范"""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.strftime("%a, %d %b %Y %H:%M:%S %z")

    @classmethod
    def generate_feed_xml(
        cls,
        channel_title: str,
        channel_link: str,
        channel_desc: str,
        episodes: List[PodcastEpisode],
        author: str = "创作者",
        lang: str = "zh-cn",
        cover_image_url: str = "",
        category: str = "Technology",
        sub_category: str = "Tech News",
        owner_email: str = ""
    ) -> str:
        """构建合规的 RSS 2.0 + iTunes Podcast XML 字符串"""
        rss = ET.Element("rss", {
            "version": "2.0",
            "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
            "xmlns:content": "http://purl.org/rss/1.0/modules/content/"
        })
        channel = ET.SubElement(rss, "channel")

        # 核心频道元数据
        ET.SubElement(channel, "title").text = channel_title
        ET.SubElement(channel, "link").text = channel_link
        ET.SubElement(channel, "description").text = channel_desc
        ET.SubElement(channel, "language").text = lang.lower()
        ET.SubElement(channel, "generator").text = "Illacme Plenipes Sovereign Podcast Engine"

        # iTunes 扩展标签
        ET.SubElement(channel, "itunes:author").text = author
        ET.SubElement(channel, "itunes:summary").text = channel_desc
        ET.SubElement(channel, "itunes:explicit").text = "no"
        if owner_email:
            owner_node = ET.SubElement(channel, "itunes:owner")
            ET.SubElement(owner_node, "itunes:name").text = author
            ET.SubElement(owner_node, "itunes:email").text = owner_email

        # 播客封面图
        if cover_image_url:
            ET.SubElement(channel, "itunes:image", {"href": cover_image_url})
            img_node = ET.SubElement(channel, "image")
            ET.SubElement(img_node, "url").text = cover_image_url
            ET.SubElement(img_node, "title").text = channel_title
            ET.SubElement(img_node, "link").text = channel_link

        # 分类标签
        cat_elem = ET.SubElement(channel, "itunes:category", {"text": category})
        if sub_category:
            ET.SubElement(cat_elem, "itunes:category", {"text": sub_category})

        # 单集节目列表
        for ep in episodes:
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = ep.title
            desc_text = ep.description or ep.title
            if ep.shownotes:
                desc_text = f"{desc_text}\n\n{ep.shownotes}"
            elif ep.chapters:
                from .podcast_models import PodcastChapter
                ch_objs = [PodcastChapter(**c) if isinstance(c, dict) else c for c in ep.chapters]
                timeline = PodcastChapter.format_shownotes_timeline(ch_objs)
                if timeline:
                    desc_text = f"{desc_text}\n\n{timeline}"
            ET.SubElement(item, "description").text = desc_text
            if ep.link:
                ET.SubElement(item, "link").text = ep.link

            guid_text = ep.guid or ep.audio_url
            ET.SubElement(item, "guid", {"isPermaLink": "false"}).text = guid_text
            ET.SubElement(item, "pubDate").text = cls.format_rfc822(ep.pub_date)

            # 音频外链附件
            ET.SubElement(item, "enclosure", {
                "url": ep.audio_url,
                "length": str(ep.audio_size_bytes),
                "type": "audio/mpeg"
            })

            ET.SubElement(item, "itunes:duration").text = cls.format_duration(ep.duration_sec)
            ET.SubElement(item, "itunes:explicit").text = "no"
            ET.SubElement(item, "itunes:author").text = author

            if ep.cover_image_url:
                ET.SubElement(item, "itunes:image", {"href": ep.cover_image_url})
            if ep.episode_num is not None:
                ET.SubElement(item, "itunes:episode").text = str(ep.episode_num)

        # 美化缩进输出
        ET.indent(rss, space="  ", level=0)
        xml_str = ET.tostring(rss, encoding="utf-8", xml_declaration=True).decode("utf-8")
        return xml_str

    @classmethod
    def save_feed(
        cls,
        output_file_path: str,
        **kwargs
    ) -> str:
        """生成并保存 XML 文件"""
        xml_content = cls.generate_feed_xml(**kwargs)
        os.makedirs(os.path.dirname(os.path.abspath(output_file_path)), exist_ok=True)
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        return output_file_path


def generate_podcast_rss(
    imprint_id: str = "default",
    base_url: str = "http://localhost:43213",
    lang: str = "zh",
    podcast_dir: Optional[str] = None,
    engine: Any = None,
    use_api_audio_route: bool = False
) -> str:
    """生成并提供指定 Imprint 的标准 Podcast RSS 2.0 XML 订阅源（联动原稿元数据与播客主控台配置）"""
    if not lang or lang == "auto":
        lang = "zh"

    if not podcast_dir:
        base_cache = getattr(engine, "cache_dir", None) or os.path.join(os.getcwd(), ".plenipes", "cache") if engine else os.path.join(os.getcwd(), ".plenipes", "cache")
        podcast_dir = os.path.join(base_cache, "podcasts", imprint_id)

    # 构建文库原稿 Slug -> 元数据映射表
    slug_doc_map: Dict[str, Dict[str, Any]] = {}
    if engine and hasattr(engine, "meta") and hasattr(engine.meta, "get_documents_snapshot"):
        try:
            snap = engine.meta.get_documents_snapshot()
            if isinstance(snap, dict):
                for rel_p, d in snap.items():
                    if isinstance(d, dict):
                        clean_rel = rel_p.replace("\\", "/").strip("/")
                        stem = os.path.splitext(os.path.basename(clean_rel))[0]
                        rel_no_ext = os.path.splitext(clean_rel)[0]
                        rel_slug = rel_no_ext.replace("/", "__") if "/" in rel_no_ext else ""
                        doc_slug = str(d.get("slug") or stem)
                        info = {
                            "title": str(d.get("title") or stem),
                            "desc": str(d.get("description") or d.get("summary") or ""),
                            "url": f"{base_url.rstrip('/')}/{str(d.get('url') or d.get('route') or f'blog/{doc_slug}.html').lstrip('/')}"
                        }
                        if rel_slug:
                            slug_doc_map[rel_slug] = info
                        if stem.lower() not in ("index", "readme") or not rel_slug:
                            slug_doc_map[stem] = info
                            slug_doc_map[doc_slug] = info
                        else:
                            slug_doc_map.setdefault(stem, info)
        except Exception:
            pass

    episodes: List[PodcastEpisode] = []
    if os.path.isdir(podcast_dir):
        from .podcast_storage_engine import PodcastStorageEngine
        files = [
            f for f in sorted(os.listdir(podcast_dir))
            if f.endswith(".mp3") and (f.endswith(f"_{lang}.mp3") or f"_{lang}_" in f or lang == "all")
        ]
        for idx, f in enumerate(files):
            f_path = os.path.join(podcast_dir, f)
            size, mtime = os.path.getsize(f_path), os.path.getmtime(f_path)
            pub_dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
            stem_raw = f[:-4]
            for suf in ("_tech_deep", "_casual_brief", "_debate", "_solo_read"):
                if stem_raw.endswith(suf):
                    stem_raw = stem_raw[:-len(suf)]
                    break
            for lg_suf in (f"_{lang}", "_zh", "_en", "_ja"):
                if stem_raw.endswith(lg_suf):
                    stem_raw = stem_raw[:-len(lg_suf)]
                    break

            doc_meta = slug_doc_map.get(stem_raw) or {}
            ep_title = doc_meta.get("title") or stem_raw.replace("-", " ").replace("_", " ").title()
            ep_desc = doc_meta.get("desc") or f"《{ep_title}》双人技术深度对谈与伴读播客"
            ep_link = doc_meta.get("url") or base_url
            local_url = f"{base_url.rstrip('/')}/api/podcast/audio/{imprint_id}/{f}" if use_api_audio_route else f"{base_url.rstrip('/')}/podcasts/{f}"
            audio_url = PodcastStorageEngine.get_audio_public_url(f, local_url, engine)

            chapters, shownotes = [], ""
            sc_f = os.path.splitext(f_path)[0] + ".chapters.json"
            if os.path.isfile(sc_f):
                try:
                    with open(sc_f, "r", encoding="utf-8") as sf:
                        sc_d = json.load(sf)
                        chapters = sc_d.get("chapters", [])
                        shownotes = sc_d.get("shownotes", "")
                except Exception:
                    pass

            episodes.append(PodcastEpisode(
                title=f"【伴读】{ep_title}",
                audio_url=audio_url,
                audio_size_bytes=size,
                duration_sec=max(30, int(size / 16000)),
                pub_date=pub_dt,
                description=ep_desc,
                link=ep_link,
                episode_num=idx + 1,
                chapters=chapters,
                shownotes=shownotes
            ))

    site_name = ""
    hub_cfg: Dict[str, Any] = {}
    if engine and hasattr(engine, "config") and engine.config:
        raw_sn = getattr(engine.config, "site_name", None) or getattr(getattr(engine.config, "imprint", None), "site_name", None)
        if isinstance(raw_sn, str):
            site_name = raw_sn
        p_cfg = getattr(engine.config, "podcast", None)
        if isinstance(p_cfg, dict) and isinstance(p_cfg.get("podcast_hub"), dict):
            hub_cfg = p_cfg["podcast_hub"]
    if not site_name:
        site_name = imprint_id.title()

    ch_title = str(hub_cfg.get("title") or "").strip() or f"{site_name} 伴读播客"
    ch_author = str(hub_cfg.get("author") or "").strip() or site_name or "创作者指南"
    ch_email = str(hub_cfg.get("email") or "").strip()
    ch_cover = str(hub_cfg.get("cover_url") or "").strip()
    ch_cat = str(hub_cfg.get("category") or "").strip() or "Technology"
    ch_desc = str(hub_cfg.get("description") or "").strip() or f"{site_name} 旗下由出版发行工作台自动衍生的多语种双人技术对谈与伴读播客。"

    return PodcastRSSGenerator.generate_feed_xml(
        channel_title=ch_title,
        channel_link=base_url,
        channel_desc=ch_desc,
        episodes=episodes,
        author=ch_author,
        lang=f"{lang}-cn" if lang == "zh" else lang,
        cover_image_url=ch_cover,
        category=ch_cat,
        owner_email=ch_email
    )


