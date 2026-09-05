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
    """将 Obsidian 双链 [[target|alias]]、Markdown 链接与 HTML 相对超链接智能解析为真实目标文件的相对超链接 (防 404，自适应 slug_dir_mode)"""
    slug_map = get_doc_slug_map(engine)

    trans_cfg = getattr(getattr(engine, 'config', None), 'translation', None) if engine else None
    dir_mode = getattr(trans_cfg, 'slug_dir_mode', 'nested') if trans_cfg else 'nested'

    def _resolve_relative_url(clean_target: str, anchor: str = "") -> str:
        clean_norm = clean_target.replace('\\', '/').strip('/')
        clean_lookup = clean_norm.lower().removesuffix('.md').removesuffix('.html')
        stem = os.path.splitext(os.path.basename(clean_norm))[0].lower()

        # 🎯 1. 频道中心入口识别 (docs, blog, showcase)
        first_segment = clean_lookup.split('/')[0] if '/' in clean_lookup else clean_lookup
        if first_segment in ('docs', 'blog', 'showcase'):
            if clean_lookup in (first_segment, f"{first_segment}/index"):
                # 提取当前所在页面的语言子目录前缀 (如 "en/", "ja/", "")
                sub_parts = [p for p in sub_path.replace('\\', '/').strip('/').split('/') if p and not p.endswith('.html')]
                lang_prefix = ""
                if sub_parts and len(sub_parts[0]) <= 4 and sub_parts[0].isalpha() and sub_parts[0] not in ('docs', 'blog', 'showcase'):
                    lang_prefix = f"{sub_parts[0]}/"

                if dir_mode == 'flat':
                    return f"{root_path}{lang_prefix}{first_segment}.html{anchor}".replace('//', '/')
                else:
                    return f"{root_path}{lang_prefix}{first_segment}/index.html{anchor}".replace('//', '/')

        # 🎯 2. 文档与页面映射识别
        # 注意：如果 stem == 'index' 且 clean_lookup != 'index'，绝不能回退到全站首页 index！
        matched_entry = slug_map.get(clean_lookup)
        if not matched_entry and stem != 'index':
            matched_entry = slug_map.get(stem)
        elif not matched_entry and clean_lookup == 'index':
            matched_entry = slug_map.get('index')

        if matched_entry:
            actual_slug = matched_entry['slug']
            channel = matched_entry.get('channel', '')
            current_dir = os.path.dirname(sub_path.replace('\\', '/')).strip('/')

            if dir_mode == 'flat':
                target_dir = ""
            elif dir_mode == 'prefix':
                target_dir = ""
                if channel and channel not in ('', 'pages') and not actual_slug.startswith(f"{channel}-"):
                    actual_slug = f"{channel}-{actual_slug}"
            else:
                target_dir = channel if (channel not in ('', 'pages')) else ""

            if current_dir == target_dir:
                return f"./{actual_slug}.html{anchor}"
            elif not current_dir and target_dir:
                return f"./{target_dir}/{actual_slug}.html{anchor}"
            elif current_dir and not target_dir:
                return f"../{actual_slug}.html{anchor}"
            else:
                return f"../{target_dir}/{actual_slug}.html{anchor}"
        else:
            clean_slug = clean_lookup
            current_dir = os.path.dirname(sub_path.replace('\\', '/')).strip('/')
            if dir_mode == 'flat' and '/' in clean_slug:
                parts = clean_slug.split('/')
                if parts[0] in ('docs', 'blog', 'showcase'):
                    clean_slug = "/".join(parts[1:])
            # 🎯 容错回退：若目标为独立单页常见名，直接回退至根路径
            if clean_slug in ('about', 'terms', 'privacy', 'disclaimer', 'contact'):
                return f"{root_path}{clean_slug}.html{anchor}".replace('//', '/')
            if current_dir and '/' not in clean_slug:
                return f"./{clean_slug}.html{anchor}"
            return f"{root_path}{clean_slug}.html{anchor}".replace('//', '/')

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

        href = _resolve_relative_url(clean_target, anchor)
        return f'<a href="{href}" class="universal-link wikilink">{alias}</a>'

    def _mdlink_repl(match):
        alias = match.group(1)
        target = match.group(2)
        if target.startswith(('http://', 'https://', 'mailto:', '/', '#')):
            return match.group(0)
        anchor = ""
        clean_target = target
        if '#' in clean_target:
            parts = clean_target.split('#', 1)
            clean_target = parts[0]
            anchor = f"#{parts[1]}"
        if clean_target.endswith(('.html', '.md')):
            resolved_url = _resolve_relative_url(clean_target, anchor)
            return f'<a href="{resolved_url}" class="universal-link mdlink">{alias}</a>'
        return match.group(0)

    def _html_a_repl(match):
        prefix_attr = match.group(1)
        href_val = match.group(2)
        suffix_attr = match.group(3)
        if href_val.startswith(('http://', 'https://', 'mailto:', '/', '#')):
            return match.group(0)
        anchor = ""
        clean_href = href_val.lstrip('./')
        if '#' in clean_href:
            parts = clean_href.split('#', 1)
            clean_href = parts[0]
            anchor = f"#{parts[1]}"
        if clean_href.endswith(('.html', '.md')):
            resolved_url = _resolve_relative_url(clean_href, anchor)
            return f'<a {prefix_attr}href="{resolved_url}"{suffix_attr}>'
        return match.group(0)

    wiki_pattern = re.compile(r'(?<!\!)\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
    body = wiki_pattern.sub(_repl, body)
    body = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', _mdlink_repl, body)
    html_a_pattern = re.compile(r'<a\s+([^>]*?)href=["\']([^"\']+)["\']([^>]*)>', re.IGNORECASE)
    body = html_a_pattern.sub(_html_a_repl, body)
    return body


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
