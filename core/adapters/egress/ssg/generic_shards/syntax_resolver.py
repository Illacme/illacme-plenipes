# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Generic SSG Adapter Syntax Resolver Shard
模块职责：提供 Universal 主题与通用 SSG 的 Markdown 语法扩展解析器。
包含双链 Wikilinks、Callouts 提示块与 Mermaid 图表预处理。
"""

import os
import re
from typing import Dict, Any, Tuple

from .navigation_builder import get_doc_slug_map


def resolve_wikilinks(body: str, root_path: str, sub_path: str = "", engine: Any = None) -> str:
    """将 Obsidian 双链 [[target|alias]] 智能解析为真实目标文件的相对超链接 (防 404)"""
    slug_map = get_doc_slug_map(engine)

    def _repl(match):
        target = match.group(1).strip()
        alias = (match.group(2) or target).strip()
        clean_target = target.replace('\\', '/').strip('/')
        if not clean_target:
            return alias

        anchor = ""
        if '#' in clean_target:
            parts = clean_target.split('#', 1)
            clean_target = parts[0]
            anchor = f"#{parts[1]}"

        if clean_target.startswith(('http://', 'https://', 'mailto:', '/')):
            return f'<a href="{clean_target}{anchor}" class="universal-link external">{alias}</a>'

        target_stem = os.path.splitext(os.path.basename(clean_target))[0].lower()

        # 命中元数据精确 Slug 查找
        if target_stem in slug_map:
            mapped_entry = slug_map[target_stem]
            final_slug = mapped_entry["slug"]
            channel = mapped_entry["channel"] or "docs"
            if "docs" in sub_path and channel == "docs":
                href = f"./{final_slug}.html{anchor}"
            else:
                href = f"{root_path}{channel}/{final_slug}.html{anchor}"
        else:
            if not clean_target.endswith('.html'):
                clean_target = f"{clean_target}.html"
            if "docs" in sub_path and "/" not in clean_target:
                href = f"./{clean_target}{anchor}"
            elif "docs" not in sub_path and "/" not in clean_target:
                href = f"{root_path}docs/{clean_target}{anchor}"
            else:
                href = f"{root_path}{clean_target}{anchor}"

        return f'<a href="{href}" class="universal-link wikilink">{alias}</a>'

    wiki_pattern = re.compile(r'(?<!\!)\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
    return wiki_pattern.sub(_repl, body)


def resolve_callouts(body: str) -> Tuple[str, list]:
    """提取并预解析 Markdown Callouts 提示块"""
    import markdown
    callouts = []
    callout_pattern = re.compile(r'^>\s*\[!(\w+)\]\s*(.*)?\n((?:^>.*\n?)*)', re.MULTILINE)

    icon_map = {
        "note": "ℹ️", "tip": "💡", "important": "📌", "warning": "⚠️",
        "caution": "🛑", "danger": "🔥", "info": "📘", "success": "✅"
    }

    def _collect(match):
        c_type = match.group(1).lower()
        raw_title = (match.group(2) or "").strip().lstrip('> ').strip()
        content_lines = match.group(3).split('\n')
        clean_content = "\n".join([line.lstrip('> ').strip() for line in content_lines if line.strip()])

        icon = icon_map.get(c_type, "💡")
        title = raw_title if raw_title else c_type.capitalize()
        rendered_body = markdown.markdown(clean_content, extensions=['extra', 'nl2br'])

        callout_html = f"""<div class="universal-callout callout-{c_type}">
    <div class="callout-header"><span class="callout-icon">{icon}</span> <strong class="callout-title">{title}</strong></div>
    <div class="callout-body">{rendered_body}</div>
</div>"""
        idx = len(callouts)
        callouts.append(callout_html)
        return f"\n@@CALLOUT:{idx}@@\n"

    processed = callout_pattern.sub(_collect, body)
    return processed, callouts


def resolve_mermaids(body: str) -> Tuple[str, list]:
    """提取并保护 Mermaid 图表代码块"""
    import html as _html
    mermaids = []
    mermaid_pattern = re.compile(r'```(?:mermaid|flowchart)\s*\n(.*?)\n```', re.DOTALL)

    def _collect(match):
        raw_code = match.group(1).strip()
        idx = len(mermaids)
        html_code = _html.escape(raw_code)
        h = f'<div class="universal-mermaid"><pre class="mermaid">{html_code}</pre></div>'
        mermaids.append(h)
        return f"\n@@MERMAID:{idx}@@\n"

    processed = mermaid_pattern.sub(_collect, body)
    return processed, mermaids
