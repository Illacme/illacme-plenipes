import os
import re
import threading
from typing import Dict, Any, Optional
from core.markup.base import IContentTransformer
from core.utils.common import extract_frontmatter
from core.utils.tracing import tlog

class ObsidianTransclusionTransformer(IContentTransformer):
    """🚀 [V35.0] Obsidian 嵌套展开转换器 (主权适配版)
    职责：基于抽象 Source 接口与元数据索引执行文档嵌套。
    """
    
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth
        self._cache = {}
        self._cache_lock = threading.Lock()
        self._pattern = re.compile(r'^[ \t]*\!\[\[([^\]]+)\]\]', re.MULTILINE)

    def _extract_sub_content(self, body: str, sub_target: str, is_block: bool = False) -> str:
        """从文档正文中精准切割出指定的块或标题区域"""
        if not sub_target: return body
        if is_block:
            pattern = re.compile(r'(?:^|\n\n)(.*?\^' + re.escape(sub_target) + r')(?:$|\n\n)', re.DOTALL)
            match = pattern.search(body)
            if match: return re.sub(r'\s*\^' + re.escape(sub_target) + r'$', '', match.group(1)).strip()
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
            tlog.warning(f"⚠️ [嵌套拦截] 递归深度上限 ({self.max_depth})。")
            return content

        md_index = context.get('md_index', {})
        asset_index = context.get('asset_index', {})
        source = context.get('source')

        def repl(m):
            raw_target = m.group(1).split('|')[0].strip()
            is_block = '^' in raw_target
            is_heading = '#' in raw_target and not is_block

            if is_block: file_part, sub_target = raw_target.split('^', 1)
            elif is_heading: file_part, sub_target = raw_target.split('#', 1)
            else: file_part, sub_target = raw_target, None

            link_target = file_part.strip()
            if not link_target or link_target in asset_index:
                return m.group(0)

            # 🚀 [V35.0] 适配字典结构的 md_index
            target_info = md_index.get(link_target)
            if not target_info: return m.group(0)
            
            rel_path = target_info.get('rel_path') if isinstance(target_info, dict) else target_info
            
            if rel_path and source:
                # 🚀 [V35.0] 影子库缓存逻辑：使用 rel_path 作为 Key
                with self._cache_lock:
                    cached_body = self._cache.get(rel_path)

                if cached_body is None:
                    try:
                        t_content = source.read_content(rel_path)
                        _, t_body = extract_frontmatter(t_content)
                        with self._cache_lock:
                            self._cache[rel_path] = t_body
                            cached_body = t_body
                    except Exception as e:
                        tlog.error(f"❌ [嵌套失败] 无法读取 {rel_path}: {e}")
                        return m.group(0)

                scoped_body = self._extract_sub_content(cached_body, sub_target.strip() if sub_target else None, is_block)
                expanded = self.expand(scoped_body, context, current_depth + 1)
                return f"\n\n{expanded}\n\n"

            return m.group(0)

        return self._pattern.sub(repl, content)

    def transform(self, content: str, context: Dict[str, Any]) -> str:
        return self.expand(content, context)
