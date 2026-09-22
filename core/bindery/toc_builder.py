# -*- coding: utf-8 -*-
"""
Illacme Plenipes - TOC Builder (典籍层级目录与大纲构建器)
模块职责：
1. 规整提取文档内部多级标题树 (H2/H3 Heading Tree)
2. 支持 python-markdown toc_tokens 与原生 HTML 兜底提取
3. 渲染 EPUB 3 原生嵌套 <ol> 目录与 EPUB 2 嵌套 <navPoint> NCX 大纲
4. 渲染 WebBook 树形侧栏大纲结构
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import re
from html import escape
from typing import Dict, Any, List, Tuple, Optional


class TocBuilder:
    """📑 典籍细粒度层级目录构建器"""

    @staticmethod
    def extract_heading_tree(toc_tokens: List[Dict[str, Any]], chapter_title: str = "") -> List[Dict[str, Any]]:
        """
        将 python-markdown 的 toc_tokens 规整化为章节内部的层级目录列表。
        规则：
        1. 若根节点仅有一个 level == 1 (H1)，则认为其是章节主标题，提取其 children 作为内部目录；
        2. 若根节点有多个 level == 1 或直接以 level >= 2 起始，则直接规整根节点；
        3. 提取 level 2 与 level 3 的节点，生成统一数据格式：
           {"id": str, "title": str, "level": int, "children": [...]}
        """
        if not toc_tokens:
            return []

        def _clean_title(raw_name: str) -> str:
            t = re.sub(r'<[^>]+>', '', raw_name or '').strip()
            return t

        def _normalize_node(token: Dict[str, Any], target_level: int = 2) -> Optional[Dict[str, Any]]:
            node_id = token.get("id") or ""
            name = _clean_title(token.get("name") or token.get("html") or "")
            if not node_id or not name:
                return None
            level = token.get("level", target_level)
            children = []
            for child in token.get("children", []):
                norm_c = _normalize_node(child, target_level=level + 1)
                if norm_c:
                    children.append(norm_c)
            return {
                "id": node_id,
                "title": name,
                "level": level,
                "children": children
            }

        # 检查是否只有一个顶层 H1 且其子节点存在
        if len(toc_tokens) == 1 and toc_tokens[0].get("level") == 1:
            raw_children = toc_tokens[0].get("children", [])
        else:
            raw_children = toc_tokens

        result = []
        for token in raw_children:
            norm = _normalize_node(token)
            if norm:
                result.append(norm)
        return result

    @staticmethod
    def extract_headings_from_html(html: str) -> List[Dict[str, Any]]:
        """
        从原生 HTML 字符串中正则提取 <h2> 与 <h3> 标题树（防御性兜底）
        """
        if not html:
            return []
        pattern = r'<h([23])\s+[^>]*id=["\']([^"\']+)["\'][^>]*>(.*?)</h\1>'
        matches = re.findall(pattern, html, flags=re.IGNORECASE | re.DOTALL)

        result: List[Dict[str, Any]] = []
        current_h2: Optional[Dict[str, Any]] = None

        for lvl_str, node_id, raw_title in matches:
            lvl = int(lvl_str)
            title = re.sub(r'<[^>]+>', '', raw_title).strip()
            if not title or not node_id:
                continue

            node = {"id": node_id, "title": title, "level": lvl, "children": []}
            if lvl == 2:
                result.append(node)
                current_h2 = node
            elif lvl == 3:
                if current_h2 is not None:
                    current_h2["children"].append(node)
                else:
                    result.append(node)
        return result

    @staticmethod
    def get_or_extract_headings(chapter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """安全获取章节标题树（优先 chapter['headings']，无则从 html_body 解析兜底）"""
        if chapter.get("headings"):
            return chapter["headings"]
        return TocBuilder.extract_headings_from_html(chapter.get("html_body", ""))

    @staticmethod
    def render_epub_nav_ol(headings: List[Dict[str, Any]], ch_filename: str) -> str:
        """
        渲染 EPUB 3 nav.xhtml 内部的嵌套 <ol> 列表
        """
        if not headings:
            return ""

        def _render_level(nodes: List[Dict[str, Any]]) -> str:
            if not nodes:
                return ""
            items = []
            for n in nodes:
                nid = n.get("id", "")
                ntitle = escape(n.get("title", ""))
                href = f"{ch_filename}#{nid}" if nid else ch_filename
                sub_html = _render_level(n.get("children", []))
                items.append(f'<li><a href="{href}">{ntitle}</a>{sub_html}</li>')
            return f"<ol>{''.join(items)}</ol>"

        return _render_level(headings)

    @staticmethod
    def render_epub_ncx_navpoints(
        headings: List[Dict[str, Any]],
        ch_filename: str,
        start_play_order: int
    ) -> Tuple[str, int]:
        """
        递归渲染 EPUB 2 toc.ncx 的子 <navPoint> 节点，并返回 (xml_str, last_play_order)
        """
        if not headings:
            return "", start_play_order

        nav_points = []
        curr_order = start_play_order

        for n in headings:
            curr_order += 1
            h_order = curr_order
            nid = n.get("id", "")
            ntitle = escape(n.get("title", ""))
            src = f"{ch_filename}#{nid}" if nid else ch_filename
            point_id = f"navPoint-{h_order}"

            child_nodes = n.get("children", [])
            child_pts = []
            for c in child_nodes:
                curr_order += 1
                c_order = curr_order
                c_id = c.get("id", "")
                c_title = escape(c.get("title", ""))
                c_src = f"{ch_filename}#{c_id}" if c_id else ch_filename
                child_pts.append(f"""        <navPoint id="navPoint-{c_order}" playOrder="{c_order}">
          <navLabel><text>{c_title}</text></navLabel>
          <content src="{c_src}"/>
        </navPoint>""")
            child_xml = ("\n" + "\n".join(child_pts)) if child_pts else ""

            nav_points.append(f"""    <navPoint id="{point_id}" playOrder="{h_order}">
      <navLabel><text>{ntitle}</text></navLabel>
      <content src="{src}"/>{child_xml}
    </navPoint>""")

        return "\n".join(nav_points), curr_order

    @staticmethod
    def render_webbook_toc_group(
        idx: int,
        ch_id: str,
        ch_title: str,
        headings: List[Dict[str, Any]]
    ) -> str:
        """
        渲染 WebBook 侧边栏的章节层级条目组（含展开/折叠控件与多级小节链接）
        """
        escaped_title = escape(ch_title)
        has_sub = bool(headings)
        toggle_btn = '<button class="wb-toc-toggle" aria-label="展开/折叠章节目录" title="展开/折叠">▾</button>' if has_sub else ''

        sub_items = []
        if has_sub:
            for h in headings:
                h_id = h.get("id", "")
                h_title = escape(h.get("title", ""))
                sub_items.append(
                    f'<a href="#{h_id}" class="wb-toc-subitem wb-toc-h2" data-id="{h_id}">'
                    f'<span class="wb-toc-bullet">▪</span> {h_title}</a>'
                )
                for sub in h.get("children", []):
                    s_id = sub.get("id", "")
                    s_title = escape(sub.get("title", ""))
                    sub_items.append(
                        f'<a href="#{s_id}" class="wb-toc-subitem wb-toc-h3" data-id="{s_id}">'
                        f'<span class="wb-toc-bullet">▫</span> {s_title}</a>'
                    )

        sub_container = f'<div class="wb-toc-sub">{"".join(sub_items)}</div>' if sub_items else ''

        return f"""<div class="wb-toc-group{" has-sub" if has_sub else ""}" data-ch-id="{ch_id}">
  <div class="wb-toc-row">
    <a href="#{ch_id}" class="wb-toc-item wb-toc-chapter" data-id="{ch_id}">
      <span class="wb-toc-num">{idx + 1}.</span> {escaped_title}
    </a>
    {toggle_btn}
  </div>
  {sub_container}
</div>"""
