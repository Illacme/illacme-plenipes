import os
import re
import threading
import logging
from typing import Dict, Any, Optional
from core.markup.base import IContentTransformer
from core.utils.common import extract_frontmatter
from core.utils.tracing import tlog

class ObsidianTransclusionTransformer(IContentTransformer):
    """🚀 [V16.0] Obsidian 嵌套展开转换器 (全功能插件版)"""
    
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth
        self._cache = {}
        self._cache_lock = threading.Lock()
        self._pattern = re.compile(r'^[ \t]*\!\[\[([^\]]+)\]\]', re.MULTILINE)

    def _extract_sub_content(self, body: str, sub_target: str, is_block: bool = False) -> str:
        """从文档正文中精准切割出指定的块或标题区域"""
        if not sub_target:
            return body

        if is_block:
            pattern = re.compile(r'(?:^|\n\n)(.*?\^' + re.escape(sub_target) + r')(?:$|\n\n)', re.DOTALL)
            match = pattern.search(body)
            if match:
                return re.sub(r'\s*\^' + re.escape(sub_target) + r'$', '', match.group(1)).strip()
        else:
            header_pattern = re.compile(r'^(#+)\s+' + re.escape(sub_target) + r'\s*$', re.MULTILINE)
            hmatch = header_pattern.search(body)
            if hmatch:
                level = len(hmatch.group(1))
                start_idx = hmatch.end()
                next_header_pattern = re.compile(r'^#{1,' + str(level) + r'}\s+', re.MULTILINE)
                next_match = next_header_pattern.search(body, start_idx)
                return body[start_idx:next_match.start()].strip() if next_match else body[start_idx:].strip()

        return body

    def expand(self, content: str, context: Dict[str, Any], current_depth: int = 0) -> str:
        """递归展开嵌套引用"""
        if current_depth > self.max_depth:
            tlog.warning(f"⚠️ 嵌套递归受限: 深度上限 ({self.max_depth})。")
            return content

        md_index = context.get('md_index', {})
        asset_index = context.get('asset_index', {})

        def repl(m):
            raw_target = m.group(1).split('|')[0].strip()
            is_block = '^' in raw_target
            is_heading = '#' in raw_target and not is_block

            if is_block:
                file_part, sub_target = raw_target.split('^', 1)
            elif is_heading:
                file_part, sub_target = raw_target.split('#', 1)
            else:
                file_part, sub_target = raw_target, None

            link_target = file_part.strip()
            if not link_target or link_target in asset_index:
                return m.group(0)

            target_abs_path = md_index.get(link_target)
            if target_abs_path and os.path.exists(target_abs_path):
                current_mtime = os.path.getmtime(target_abs_path)
                with self._cache_lock:
                    cached_node = self._cache.get(target_abs_path)
                    cached_body = cached_node['content'] if cached_node and cached_node['mtime'] >= current_mtime else None

                if cached_body is None:
                    try:
                        with open(target_abs_path, 'r', encoding='utf-8') as f:
                            _, t_body = extract_frontmatter(f.read())
                        with self._cache_lock:
                            self._cache[target_abs_path] = {'mtime': current_mtime, 'content': t_body}
                            cached_body = t_body
                    except Exception:
                        return m.group(0)

                scoped_body = self._extract_sub_content(cached_body, sub_target.strip() if sub_target else None, is_block)
                expanded = self.expand(scoped_body, context, current_depth + 1)
                return f"\n\n{expanded}\n\n"

            return m.group(0)

        return self._pattern.sub(repl, content)

    def transform(self, content: str, context: Dict[str, Any]) -> str:
        return self.expand(content, context)
