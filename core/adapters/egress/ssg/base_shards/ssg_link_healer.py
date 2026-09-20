#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SSG Link Healer Shard
职责：通用 Markdown/MDX 链接清洗与语法规范化：
1. 将 Obsidian 双链 [[target|alias]]、[[target]] 标准化为符合通用 Markdown 规范的相对链接 [alias](./target.md)。
2. 自愈相对超链接中的 .html 后缀为 .md (契合第三方 SSG 框架内部 SPA 路由器要求) 或 Clean URL。
3. 消除 CommonMark 陷阱，确保第三方框架 MDX 编译器 0 语法报错。
"""

import os
import re
from typing import Any


class SSGLinkHealer:
    """SSG 链接自愈与 Markdown 规范化处理器"""

    @staticmethod
    def normalize_markdown_content(adapter: Any, body: str, sub_path: str = "", target_lang: str = "zh", clean_url: bool = None) -> str:
        if clean_url is None:
            clean_url = getattr(adapter, 'IS_CLEAN_URL', False)

        try:
            from core.adapters.egress.ssg.generic_shards.navigation_builder import get_doc_slug_map
            slug_map = get_doc_slug_map(adapter.engine) if getattr(adapter, "engine", None) else {}
        except Exception:
            slug_map = {}

        raw_current_dir = os.path.dirname(sub_path.replace('\\', '/')).strip('/')
        lang_code = adapter.get_language_code(target_lang) if hasattr(adapter, 'get_language_code') else ""
        lang_prefix = f"/{lang_code}" if lang_code else ""

        # 🛡️ 剥离当前目录中的物理语言前缀 (如 ja/docs -> docs, ja -> "")，杜绝 /ja/ja/ 双重语种叠加
        current_dir_parts = [p for p in raw_current_dir.split('/') if p]
        if current_dir_parts and lang_code and current_dir_parts[0] == lang_code:
            current_dir_parts = current_dir_parts[1:]
        current_dir = '/'.join(current_dir_parts)

        def _resolve_target_md(target_str: str, anchor: str = "") -> str:
            raw_t = target_str.replace('\\', '/').strip()
            while raw_t.startswith('./'):
                raw_t = raw_t[2:]
            clean_t = raw_t.strip('/')
            if not clean_t:
                return f"./{anchor}" if anchor else ""
            clean_lookup = clean_t.lower().removesuffix('.md').removesuffix('.html')
            stem = os.path.splitext(os.path.basename(clean_t))[0].lower()

            matched = slug_map.get(clean_lookup)
            if not matched and stem != 'index':
                matched = slug_map.get(stem)
            elif not matched and clean_lookup == 'index':
                matched = slug_map.get('index')

            if clean_url:
                if matched:
                    actual_slug = matched.get('slug', stem)
                    channel = matched.get('channel', '')
                    target_dir = channel if (channel and channel not in ('', 'pages')) else ""

                    if actual_slug == 'index':
                        if target_dir:
                            res_url = f"{lang_prefix}/{target_dir}/{anchor}"
                        else:
                            res_url = f"{lang_prefix}/{anchor}" if lang_prefix else f"/{anchor}"
                    else:
                        if target_dir:
                            res_url = f"{lang_prefix}/{target_dir}/{actual_slug}/{anchor}"
                        else:
                            res_url = f"{lang_prefix}/{actual_slug}/{anchor}"
                else:
                    clean_name = clean_lookup
                    is_index_target = clean_name.endswith('/index') or clean_name == 'index'
                    if clean_name.endswith('/index'):
                        clean_name = clean_name.removesuffix('/index')

                    clean_parts = [p for p in clean_name.split('/') if p]
                    if clean_parts and lang_code and clean_parts[0] == lang_code:
                        clean_parts = clean_parts[1:]
                        clean_name = '/'.join(clean_parts)

                    if clean_name.startswith('../'):
                        resolved_parts = [p for p in (current_dir.split('/') if current_dir else []) if p]
                        sub_parts = clean_name.split('/')
                        for p in sub_parts:
                            if p == '..':
                                if resolved_parts:
                                    resolved_parts.pop()
                            elif p and p != '.':
                                resolved_parts.append(p)
                        abs_path = '/'.join(resolved_parts)
                        if abs_path:
                            res_url = f"{lang_prefix}/{abs_path}/{anchor}"
                        else:
                            res_url = f"{lang_prefix}/{anchor}" if lang_prefix else f"/{anchor}"
                    elif '/' in clean_name:
                        res_url = f"{lang_prefix}/{clean_name}/{anchor}"
                    else:
                        if current_dir and not is_index_target and clean_name != 'index':
                            res_url = f"{lang_prefix}/{current_dir}/{clean_name}/{anchor}"
                        elif clean_name and clean_name != 'index':
                            res_url = f"{lang_prefix}/{clean_name}/{anchor}"
                        else:
                            res_url = f"{lang_prefix}/{anchor}" if lang_prefix else f"/{anchor}"

                if lang_code and clean_url:
                    double_pfx = f"/{lang_code}/{lang_code}/"
                    single_pfx = f"/{lang_code}/"
                    while double_pfx in res_url:
                        res_url = res_url.replace(double_pfx, single_pfx)
                return res_url
            else:
                suffix = ".md"
                if matched:
                    actual_slug = matched.get('slug', stem)
                    channel = matched.get('channel', '')
                    slots = adapter.get_feature_slots() if hasattr(adapter, 'get_feature_slots') else {}
                    slot_single = slots.get(channel, {}).get("single", channel) if isinstance(slots.get(channel), dict) else channel
                    if slot_single == "":
                        target_dir = ""
                    else:
                        target_dir = channel if (channel and channel not in ('', 'pages')) else ""

                    if current_dir == target_dir:
                        return f"./{actual_slug}{suffix}{anchor}"
                    elif not current_dir and target_dir:
                        return f"./{target_dir}/{actual_slug}{suffix}{anchor}"
                    elif current_dir and not target_dir:
                        return f"../{actual_slug}{suffix}{anchor}"
                    else:
                        return f"../{target_dir}/{actual_slug}{suffix}{anchor}"
                else:
                    return f"./{clean_lookup}{suffix}{anchor}"

        # 1. 转换 Obsidian 双链 [[target|alias]] 或 [[target]]
        def _wikilink_repl(match):
            target = match.group(1).strip()
            alias = (match.group(2) or target).strip()
            if target.startswith(('AEL-Iter-ID:', 'AEL:')) or 'Iter-ID' in target:
                return match.group(0)
            clean_target = target.replace('\\', '/').strip('/')
            if not clean_target:
                return alias
            anchor = ""
            if '#' in clean_target:
                parts = clean_target.split('#', 1)
                clean_target = parts[0]
                anchor = f"#{parts[1]}"
            if clean_target.startswith(('http://', 'https://', 'mailto:', '/')):
                return f"[{alias}]({clean_target}{anchor})"

            resolved_md = _resolve_target_md(clean_target, anchor)
            return f"[{alias}]({resolved_md})"

        wiki_pattern = re.compile(r'(?<!\!)\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
        processed = wiki_pattern.sub(_wikilink_repl, body)

        # 2. 规范化标准 Markdown 相对链接中的 .html / .md
        def _mdlink_repl(match):
            alias = match.group(1)
            target = match.group(2).strip()
            if target.startswith(('http://', 'https://', 'mailto:', '/', '#')):
                return match.group(0)
            anchor = ""
            clean_target = target
            if '#' in clean_target:
                parts = clean_target.split('#', 1)
                clean_target = parts[0]
                anchor = f"#{parts[1]}"
            if clean_url:
                resolved = _resolve_target_md(clean_target, anchor)
                if resolved:
                    return f"[{alias}]({resolved})"
                if clean_target.endswith(('.html', '.md')):
                    clean_stem = clean_target.removesuffix('.html').removesuffix('.md')
                    if clean_stem.endswith('/index'):
                        clean_stem = clean_stem.removesuffix('/index')
                    if not clean_stem.endswith('/'):
                        clean_stem += '/'
                    return f"[{alias}]({clean_stem}{anchor})"
            else:
                if clean_target.endswith('.html'):
                    clean_stem = clean_target.removesuffix('.html')
                    return f"[{alias}]({clean_stem}.md{anchor})"
            return match.group(0)

        processed = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', _mdlink_repl, processed)

        # 3. 规范化原生 HTML 中的 <a href="..."> 相对链接
        def _html_a_repl(match):
            prefix_attr = match.group(1)
            href_val = match.group(2).strip()
            suffix_attr = match.group(3)
            if href_val.startswith(('http://', 'https://', 'mailto:', '/', '#')):
                return match.group(0)
            anchor = ""
            clean_href = href_val
            if '#' in clean_href:
                parts = clean_href.split('#', 1)
                clean_href = parts[0]
                anchor = f"#{parts[1]}"
            if clean_url:
                resolved = _resolve_target_md(clean_href, anchor)
                if resolved:
                    return f'<a {prefix_attr}href="{resolved}"{suffix_attr}>'
                if clean_href.endswith(('.html', '.md')):
                    clean_stem = clean_href.removesuffix('.html').removesuffix('.md')
                    if clean_stem.endswith('/index'):
                        clean_stem = clean_stem.removesuffix('/index')
                    if not clean_stem.endswith('/'):
                        clean_stem += '/'
                    return f'<a {prefix_attr}href="{clean_stem}{anchor}"{suffix_attr}>'
            else:
                resolved = _resolve_target_md(clean_href, anchor)
                if resolved:
                    return f'<a {prefix_attr}href="{resolved}"{suffix_attr}>'
                if clean_href.endswith('.html'):
                    clean_stem = clean_href.removesuffix('.html')
                    return f'<a {prefix_attr}href="{clean_stem}.md{anchor}"{suffix_attr}>'
            return match.group(0)

        html_a_pattern = re.compile(r'<a\s+([^>]*?)href=["\']([^"\']+)["\']([^>]*)>', re.IGNORECASE)
        processed = html_a_pattern.sub(_html_a_repl, processed)

        # 4. 🛡️ 消除 CommonMark 陷阱：将带有 4+ 空格缩进的 HTML 标签行自动顶格
        lines = processed.split('\n')
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('<', '</', '<!--')) or stripped.endswith('>') or ('</' in stripped):
                new_lines.append(stripped)
            elif '<' in line and '>' in line and not line.strip().startswith(('`', '-', '*', '1.', '2.', '3.')):
                new_lines.append(stripped)
            else:
                new_lines.append(line)
        processed = '\n'.join(new_lines)

        return processed
