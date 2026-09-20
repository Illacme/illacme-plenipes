#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sovereign Markdown Compiler & Link Healer Shard
模块职责：Callouts / Mermaid 隔离预处理、双向链接 (WikiLink) 与相对链接动态重写，以及渲染后容器还原。
🛡️ [SOP-01 & SOP-02]：从 sovereign.py 物理拆解出的编译前置/后置治理分片。
"""

import os
import re
import html as _html
import markdown
from typing import Tuple, List
from core.adapters.egress.ssg.generic_shards.navigation_builder import get_doc_slug_map


def preprocess_markdown(body: str, adapter) -> Tuple[str, List[str], List[str]]:
    """方言预处理：隔离 Callouts 与 Mermaid 图表代码块 (防止被 codehilite/pygments 破坏转义)"""
    callouts = []
    callout_pattern = re.compile(r'^>\s*\[!(\w+)\]\s*(.*)?\n((?:^>.*\n?)*)', re.MULTILINE)
    
    def _callout_collect(match):
        c_type = match.group(1)
        raw_title = match.group(2).strip().lstrip('> ').strip()
        content_lines = match.group(3).split('\n')
        clean_content = "\n".join([line.lstrip('> ').strip() for line in content_lines])
        
        rendered_title = markdown.markdown(raw_title) if raw_title else c_type.capitalize()
        rendered_title = re.sub(r'^<p>(.*)</p>$', r'\1', rendered_title)
        rendered_body = markdown.markdown(clean_content, extensions=['extra', 'nl2br'])
        
        html_card = adapter.render_callout(c_type, rendered_title, rendered_body)
        idx = len(callouts)
        callouts.append(html_card)
        return f"\n@@CALLOUT:{idx}@@\n"

    body = callout_pattern.sub(_callout_collect, body)

    mermaids = []
    mermaid_pattern = re.compile(r'```(?:mermaid|flowchart)\s*\n(.*?)\n```', re.DOTALL)
    
    def _mermaid_collect(match):
        raw_code = match.group(1).strip()
        idx = len(mermaids)
        html_code = _html.escape(raw_code)
        h = f'<div class="sovereign-mermaid-diagram"><pre class="mermaid">{html_code}</pre></div>'
        mermaids.append(h)
        return f"\n@@MERMAID:{idx}@@\n"

    body = mermaid_pattern.sub(_mermaid_collect, body)
    return body, callouts, mermaids


def rewrite_markdown_links(body: str, engine, sub_path: str) -> str:
    """将双向链接 (WikiLink)、Markdown 相对链接及 HTML a 标签动态重写为符合 slug_dir_mode 的路径"""
    slug_map = get_doc_slug_map(engine)

    trans_cfg = getattr(getattr(engine, 'config', None), 'translation', None)
    dir_mode = getattr(trans_cfg, 'slug_dir_mode', 'nested') if trans_cfg else 'nested'

    sub_clean = sub_path.replace('\\', '/').strip('/')
    parts = [p for p in sub_clean.split('/') if p and not p.endswith('.html')]
    depth = len(parts)
    root_path = "../" * depth if depth > 0 else "./"

    def _resolve_relative_url(clean_target: str, anchor: str = "") -> str:
        clean_norm = clean_target.replace('\\', '/').strip('/')
        clean_lookup = clean_norm.lower().removesuffix('.md').removesuffix('.html')
        stem = os.path.splitext(os.path.basename(clean_norm))[0].lower()

        # 🎯 1. 频道中心入口识别 (docs, blog, showcase)
        first_segment = clean_lookup.split('/')[0] if '/' in clean_lookup else clean_lookup
        if first_segment in ('docs', 'blog', 'showcase'):
            if clean_lookup in (first_segment, f"{first_segment}/index"):
                sub_parts = [p for p in sub_clean.split('/') if p and not p.endswith('.html')]
                lang_prefix = ""
                if sub_parts and len(sub_parts[0]) <= 4 and sub_parts[0].isalpha() and sub_parts[0] not in ('docs', 'blog', 'showcase'):
                    lang_prefix = f"{sub_parts[0]}/"

                if dir_mode == 'flat':
                    return f"{root_path}{lang_prefix}{first_segment}.html{anchor}".replace('//', '/')
                else:
                    return f"{root_path}{lang_prefix}{first_segment}/index.html{anchor}".replace('//', '/')

        # 🎯 2. 文档与页面映射识别
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
            if dir_mode == 'flat' and '/' in clean_slug:
                p_parts = clean_slug.split('/')
                if p_parts[0] in ('docs', 'blog', 'showcase', 'about'):
                    clean_slug = "/".join(p_parts[1:])
            return f"{root_path}{clean_slug}.html{anchor}".replace('//', '/')

    def _wikilink_repl(match):
        target = match.group(1).strip()
        alias = (match.group(2) or target).strip()
        clean_target = target.replace('\\', '/').strip('/')
        if not clean_target:
            return alias
        anchor = ""
        if '#' in clean_target:
            parts_hash = clean_target.split('#', 1)
            clean_target = parts_hash[0]
            anchor = f"#{parts_hash[1]}"
        if not clean_target.startswith(('http://', 'https://', 'mailto:', '/')):
            final_link = _resolve_relative_url(clean_target, anchor)
        else:
            final_link = f"{clean_target}{anchor}"
        return f"[{alias}]({final_link})"

    def _mdlink_repl(match):
        alias = match.group(1)
        target = match.group(2)
        if target.startswith(('http://', 'https://', 'mailto:', '/', '#')):
            return match.group(0)
        anchor = ""
        clean_target = target
        if '#' in clean_target:
            parts_hash = clean_target.split('#', 1)
            clean_target = parts_hash[0]
            anchor = f"#{parts_hash[1]}"
        if clean_target.endswith(('.html', '.md')):
            resolved_url = _resolve_relative_url(clean_target, anchor)
            return f"[{alias}]({resolved_url})"
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
            parts_hash = clean_href.split('#', 1)
            clean_href = parts_hash[0]
            anchor = f"#{parts_hash[1]}"
        if clean_href.endswith(('.html', '.md')):
            resolved_url = _resolve_relative_url(clean_href, anchor)
            return f'<a {prefix_attr}href="{resolved_url}"{suffix_attr}>'
        return match.group(0)

    wiki_pattern = re.compile(r'(?<!\!)\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
    body = wiki_pattern.sub(_wikilink_repl, body)
    body = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', _mdlink_repl, body)

    html_a_pattern = re.compile(r'<a\s+([^>]*?)href=["\']([^"\']+)["\']([^>]*)>', re.IGNORECASE)
    body = html_a_pattern.sub(_html_a_repl, body)
    return body


def restore_containers(html_fragment: str, callouts: list, mermaids: list) -> str:
    """还原 Callout 与 Mermaid HTML 容器"""
    for i, callout_h in enumerate(callouts):
        html_fragment = re.sub(rf'<p>@@CALLOUT:{i}@@(?:<br\s*/?>)?\s*</p>|@@CALLOUT:{i}@@', callout_h, html_fragment)
    for i, mermaid_h in enumerate(mermaids):
        html_fragment = re.sub(rf'<p>@@MERMAID:{i}@@(?:<br\s*/?>)?\s*</p>|@@MERMAID:{i}@@', mermaid_h, html_fragment)
    return html_fragment
