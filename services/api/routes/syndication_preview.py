# -*- coding: utf-8 -*-
"""
Illacme-plenipes API - Syndication Live Preview Route
模块职责：全渠道高保真排版即时预览后端服务（微信/知乎/掘金/Dev.to 等）。
支持外链转脚注、内联 CSS 注入、多语种文稿水合与合规审计指标。
🛡️ [SOP-01 纯净架构 / 单文件 ≤ 300 行]
"""

import os
import re
import math
from typing import Dict, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from core.runtime.engine_singleton import get_global_engine
from core.utils.text import parse_frontmatter
from services.api.routes.system import verify_token
from services.api.logic.content_ops_shards.safe_ops import resolve_safe_path

router = APIRouter(prefix="/api/syndication", tags=["Syndication Preview"])


class SyndicationPreviewRequest(BaseModel):
    rel_path: str
    target_platform: str = "wechat"
    lang: str = "zh"
    convert_footnotes: bool = True
    theme: str = "default"


def _estimate_reading_metrics(text: str) -> Dict[str, int]:
    """估算字数与预计阅读时间（CJK 汉字 + 西文单词）"""
    clean_text = re.sub(r'<[^>]+>', '', text)
    clean_text = re.sub(r'```.*?```', '', clean_text, flags=re.DOTALL)
    
    # 统计汉字数
    cjk_chars = len(re.findall(r'[\u4e00-\u9fff]', clean_text))
    # 统计非 CJK 单词数
    non_cjk_words = len(re.findall(r'[a-zA-Z0-9_-]+', clean_text))
    total_words = cjk_chars + non_cjk_words

    # 按照每分钟 350 字估算
    reading_time = max(1, math.ceil(total_words / 350)) if total_words > 0 else 1
    image_count = len(re.findall(r'!\[.*?\]\(.*?\)', text)) + len(re.findall(r'<img\s+', text, re.I))

    return {
        "word_count": total_words,
        "reading_time_min": reading_time,
        "image_count": image_count
    }


def _extract_title_and_digest(fm: dict, body: str, filename: str) -> tuple:
    """提取高置信度标题与摘要"""
    title = fm.get("title") or ""
    if not title and body:
        m = re.search(r'^\s*#\s+(.+)$', body, re.MULTILINE)
        if m:
            title = m.group(1).strip()
    if not title:
        title = os.path.splitext(os.path.basename(filename))[0]

    raw_desc = fm.get("description") or fm.get("digest") or ""
    if not raw_desc and body:
        clean_lines = [l.strip() for l in body.splitlines() if l.strip() and not l.strip().startswith('#')]
        raw_desc = clean_lines[0] if clean_lines else ""
    
    digest = " ".join(str(raw_desc).split())[:120]
    return str(title).strip(), digest


@router.post("/preview", dependencies=[Depends(verify_token)])
async def generate_syndication_preview(req: SyndicationPreviewRequest) -> Dict[str, Any]:
    """生成指定社媒渠道的高保真排版预览数据"""
    engine = get_global_engine()
    if not engine:
        return {"status": "error", "error": "引擎未完成初始化"}

    # 🛡️ 路径安全解析（防御目录穿越）
    safe_abs_path = resolve_safe_path(engine, req.rel_path)
    if not safe_abs_path or not os.path.exists(safe_abs_path):
        return {"status": "error", "error": f"文库中未找到稿件: {req.rel_path}"}

    try:
        with open(safe_abs_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
    except Exception as e:
        return {"status": "error", "error": f"读取稿件失败: {e}"}

    fm_dict, body, _ = parse_frontmatter(raw_content)

    # 🌐 多语言文稿支持：若指定了非主语种，尝试提取该语种的校对或已译文本
    target_lang = (req.lang or "zh").lower()
    if target_lang != "zh" and hasattr(engine, "meta") and hasattr(engine.meta, "sqlite"):
        try:
            cur = engine.meta.sqlite.get_cursor()
            row = cur.execute(
                "SELECT reviewed_body, reviewed_title, reviewed_desc FROM reviewed_translations WHERE rel_path = ? AND lang_code = ?",
                (req.rel_path, target_lang)
            ).fetchone()
            if row and row[0]:
                body = row[0]
                if row[1]: fm_dict["title"] = row[1]
                if row[2]: fm_dict["description"] = row[2]
        except Exception:
            pass

    title, digest = _extract_title_and_digest(fm_dict, body, req.rel_path)
    cover_url = fm_dict.get("cover") or fm_dict.get("banner") or fm_dict.get("image") or ""
    metrics = _estimate_reading_metrics(body)

    platform = (req.target_platform or "wechat").lower()
    rendered_html = ""
    rendered_markdown = body
    footnotes_count = 0
    compliance = {"is_valid": True, "warnings": [], "platform_rules": ""}

    # 🎨 针对全渠道矩阵编译排版
    if platform == "wechat":
        from adapters.egress.syndication.wechat_shards.wechat_formatter import render_wechat_html, transmute_footnotes
        clean_title = title[:32]
        if len(title) > 32: compliance["warnings"].append(f"微信标题已截断至 32 字 (原长: {len(title)})")
        wechat_body = re.sub(r'^\s*#\s+.*$', '', body, count=1, flags=re.MULTILINE).strip()
        _, f_list = transmute_footnotes(wechat_body)
        footnotes_count = len(f_list)
        rendered_html = render_wechat_html(wechat_body, {"convert_footnotes": req.convert_footnotes})
        compliance["platform_rules"] = "微信要求全局内联 CSS，非白名单外链已转换为文末脚注上标"

    elif platform in ("zhihu", "bilibili", "toutiao"):
        clean_title = title[:40]
        import markdown
        zh_body = re.sub(r'^\s*#\s+.*$', '', body, count=1, flags=re.MULTILINE)
        rendered_html = markdown.markdown(zh_body, extensions=['extra', 'codehilite', 'tables', 'toc'])
        rendered_markdown = zh_body.strip()
        compliance["platform_rules"] = f"{platform.upper()} 专栏排版：大标题自适应外置收拢，支持代码块高亮"

    elif platform in ("juejin", "csdn", "cnblogs", "segmentfault", "oschina"):
        clean_title = title[:50]
        import markdown
        notice = "\n\n---\n> 🛡️ *本文首发于创作者文库，知识产权受自主保护。*"
        rendered_markdown = f"> 💡 **导读**：{digest}\n\n{body}{notice}" if digest else f"{body}{notice}"
        rendered_html = markdown.markdown(rendered_markdown, extensions=['extra', 'codehilite', 'tables', 'toc'])
        compliance["platform_rules"] = f"{platform.upper()} 技术博客流：已注入技术导读卡片与文末原创版权声明"

    elif platform in ("devto", "medium", "hashnode", "substack", "ghost", "wordpress"):
        clean_title = title[:60]
        site_url = getattr(engine.config.compliance, "site_url", "https://your-domain.com") if hasattr(engine.config, "compliance") else "https://your-domain.com"
        slug = os.path.splitext(req.rel_path)[0].replace('\\', '/')
        canonical_url = f"{site_url.rstrip('/')}/{slug}"
        tags = fm_dict.get("tags") or ["tech", "programming", "webdev"]
        if isinstance(tags, str): tags = [t.strip() for t in tags.split(',')]
        tags_str = ", ".join(tags[:4])
        rendered_markdown = f"---\ntitle: \"{clean_title}\"\npublished: true\ndescription: \"{digest}\"\ntags: {tags_str}\ncanonical_url: {canonical_url}\n---\n\n{body}"
        import markdown
        rendered_html = markdown.markdown(body, extensions=['extra', 'codehilite', 'tables', 'toc'])
        compliance["platform_rules"] = f"已注入 Canonical URL ({canonical_url}) 保护跨站 SEO 权重"

    elif platform == "xiaohongshu":
        clean_title = title[:20]
        # 小红书短图文合规：上限 1000 字符，文末自动提取话题标签
        if len(body) > 1000:
            compliance["warnings"].append(f"正文字数 ({len(body)}) 超过小红书 1000 字符限制，建议分图发布")
        tags = fm_dict.get("tags") or ["生活随笔", "知识分享", "科技数码"]
        if isinstance(tags, str): tags = [t.strip() for t in tags.split(',')]
        tag_pills = "".join([f"<span style='display:inline-block;padding:2px 8px;margin:2px 4px 2px 0;background:#ffeef0;color:#ff2442;border-radius:12px;font-size:12px;'>#{t}</span>" for t in tags[:6]])
        clean_body = re.sub(r'^\s*#\s+.*$', '', body, count=1, flags=re.MULTILINE).strip()
        xhs_md = f"{digest}\n\n{clean_body[:850]}" if digest else clean_body[:900]
        rendered_markdown = f"{xhs_md}\n\n" + " ".join([f"#{t}" for t in tags[:6]])
        import markdown
        body_html = markdown.markdown(xhs_md)
        rendered_html = f"<div style='font-size:15px;line-height:1.7;'>{body_html}<div style='margin-top:16px;border-top:1px dashed #f0f0f0;padding-top:10px;'>{tag_pills}</div></div>"
        compliance["platform_rules"] = "小红书 3:4 竖屏短图文：自动提取文末话题标签，单篇限制 1000 字符"

    else:
        clean_title = title
        import markdown
        rendered_html = markdown.markdown(body, extensions=['extra', 'codehilite'])
        compliance["platform_rules"] = f"{platform.upper()} 通用排版：采用标准 CommonMark 与代码高亮渲染"

    return {
        "status": "success",
        "platform": platform,
        "title": title,
        "clean_title": clean_title,
        "digest": digest,
        "cover_url": cover_url,
        "rendered_html": rendered_html,
        "rendered_markdown": rendered_markdown,
        "stats": {
            "word_count": metrics["word_count"],
            "reading_time_min": metrics["reading_time_min"],
            "image_count": metrics["image_count"],
            "footnotes_count": footnotes_count,
            "title_length": len(clean_title)
        },
        "compliance": compliance
    }
