#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sovereign Theme Adapter
模块职责：主权原生主题渲染适配器。
🛡️ [AEL-Iter-v11.6]：实现零依赖、直出型的 Markdown to HTML 渲染逻辑。
"""

import os
import logging
# import markdown  <-- 移至方法内部延迟导入，防止扫描时报错
import threading
from typing import Tuple, Dict, Any
from core.adapters.egress.ssg.base import BaseSSGAdapter

from core.utils.tracing import tlog
logger = logging.getLogger("Illacme.plenipes")

class SovereignSSGAdapter(BaseSSGAdapter):
    """
    🚀 默认原生适配器：将 Markdown 直接渲染为具有高级感视觉系统的静态 HTML。
    """
    PLUGIN_ID = 'default'
    
    def __init__(self, theme_settings: Any = None):
        super().__init__(theme_settings)
        self.template_path = "themes/default/templates/layout.html"

    def get_output_schema(self) -> list:
        """🚀 [V11.2] 主权适配器强制开启双相分发 (源码 + 静态渲染)"""
        return ["source", "static"]

    @property
    def output_extension(self) -> str:
        return ".html" # 强制 HTML 输出

    _assets_copied = False # 🚀 类级标志位，防止并发搬运冲突
    _assets_lock = threading.Lock() # 🛡️ [V16.5] 资产搬运专属物理锁
    _sidebar_cache = {} # 🚀 [V16.5] 侧边栏缓存，避免 O(N^2) 重复扫描

    def render(self, body: str, fm: Dict[str, Any], seo_data: Dict[str, Any] = None, target_lang: str = "en", sub_path: str = "") -> Tuple[str, Dict[str, Any]]:
        """
        [Sovereign] 执行 Markdown 到 HTML 的全量渲染与模版注入。
        """
        import re
        # 1. 物理剥离 Frontmatter
        body = re.sub(r'^\s*---.*?---\s*', '', body, flags=re.DOTALL)

        # 2. 基础 SEO 处理
        if seo_data:
            fm = self.inject_seo(fm, seo_data.get('description', ''), seo_data.get('keywords', []))
        
        # 3. 🚀 [V15.7] 物理主权对齐：深度探测自适应
        # 如果是默认语种，物理路径不包含语言前缀，深度减 1
        sub_dir = sub_path.strip('/')
        is_default = (target_lang == getattr(self, 'default_lang', 'zh'))
        depth = 0 if is_default else 1 
        
        if sub_dir:
            depth += len(sub_dir.split('/'))
        root_path = "../" * depth if depth > 0 else "./"

        # 4. 核心 Markdown 转换 (带 GFM 扩展)
        import markdown
        # 5. 🚀 方言预处理：隔离 Callouts
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
            
            html = self.render_callout(c_type, rendered_title, rendered_body)
            idx = len(callouts)
            callouts.append(html)
            return f"@@CALLOUT:{idx}@@\n"
        
        body = callout_pattern.sub(_callout_collect, body)
        html_fragment = markdown.markdown(body, extensions=['extra', 'codehilite', 'toc', 'nl2br'])
        
        # 7. 还原 Callout HTML 容器
        for i, html in enumerate(callouts):
            html_fragment = html_fragment.replace(f"<p>@@CALLOUT:{i}@@</p>", html)
            html_fragment = html_fragment.replace(f"@@CALLOUT:{i}@@", html)

        # 8. 加载物理模版 (layout.html)
        full_html = self._apply_template(html_fragment, fm, target_lang, sub_path, is_default=is_default)

        # 9. 🚀 [V11.8] 资产原子搬运 (Singleton Copy)
        if not SovereignSSGAdapter._assets_copied:
            with SovereignSSGAdapter._assets_lock:
                # 双重检查锁定 (DCL)
                if not SovereignSSGAdapter._assets_copied:
                    import shutil
                    theme_root = os.path.dirname(os.path.dirname(self.template_path))
                    static_src = os.path.join(theme_root, "static")
                    dist_root = os.path.join(theme_root, "dist")
                    static_dest = os.path.join(dist_root, "static")
                    
                    if os.path.exists(static_src):
                        try:
                            shutil.copytree(static_src, static_dest, dirs_exist_ok=True)
                            favicon_src = os.path.join(theme_root, "favicon.png")
                            if os.path.exists(favicon_src):
                                shutil.copy2(favicon_src, dist_root)
                            SovereignSSGAdapter._assets_copied = True
                            tlog.info(f"✨ [Sovereign] 全局资产单次同步完成: {static_dest}")
                        except Exception as e:
                            tlog.error(f"🛑 [Sovereign] 资产同步失败: {e}")

        return full_html, fm

    def _apply_template(self, content_html: str, fm: Dict[str, Any], lang: str, sub_path: str, is_default: bool = False) -> str:
        """物理模版注入系统 - [V15.0] 支持 Docusaurus 风格形态分发"""
        # 🚀 [V15.0] 布局形态探测
        prefix = fm.get('route_prefix', 'docs')
        # 🚀 [V15.8] 布局控制权回传：用户显式指定优先，引擎自动推断兜底
        layout_type = fm.get('layout', self._get_layout_type(prefix, sub_path, fm))
        
        # 尝试寻找专用模版，如 docs.html, blog.html
        theme_dir = os.path.dirname(os.path.dirname(self.template_path))
        specific_tpl = os.path.join(theme_dir, "templates", f"{layout_type}.html")
        tpl_to_use = specific_tpl if os.path.exists(specific_tpl) else self.template_path
        
        if not os.path.exists(tpl_to_use):
            logger.warning(f"⚠️ [Sovereign] 模版不存在: {tpl_to_use}，回退至原始片段。")
            return content_html

        try:
            with open(tpl_to_use, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # 🚀 [V15.9] 物理主权对齐：精准深度探测
            # depth 应该等于 sub_path 中目录的层级数
            parts = [p for p in sub_path.split('/') if p and not p.endswith('.html')]
            depth = len(parts)
            root_path = "../" * depth if depth > 0 else "./"
            
            # 🚀 [V15.7] 布局形态感知注入：仅在文档页显示侧边栏
            sidebar_container = ""
            if layout_type == "docs":
                sidebar_html = self._build_sidebar(lang, prefix, sub_path, root_path)
                sidebar_container = f"""
        <!-- 📂 侧边栏导航 -->
        <aside class="sidebar-pioneer">
            <div class="sidebar-content">
                <div class="nav-tree">
                    {sidebar_html}
                </div>
            </div>
        </aside>
                """

            # 🚀 [V11.7] 动态语种路由对齐
            lang_names = {"zh": "🇨🇳 简体中文", "en": "🇺🇸 English", "ja": "🇯🇵 日本語", "fr": "🇫🇷 Français", "de": "🇩🇪 Deutsch", "es": "🇪🇸 Español"}
            switcher_items = []
            hreflangs = fm.get('hreflangs', [])
            
            if not hreflangs:
                for l_code, l_name in lang_names.items():
                    is_active = "selected" if l_code == lang else ""
                    switcher_items.append(f'<option value="{root_path}{l_code}/index.html" {is_active}>{l_name}</option>')
            else:
                for item in hreflangs:
                    l_code = item.get('lang')
                    l_url = item.get('url', '').lstrip('/')
                    if l_url and not l_url.endswith('.html'):
                        l_url += '.html'
                    l_name = lang_names.get(l_code, l_code.upper())
                    is_active = "selected" if l_code == lang else ""
                    switcher_items.append(f'<option value="{root_path}{l_url}" {is_active}>{l_name}</option>')

            lang_switcher_html = "\n".join(switcher_items)
            
            # 🌐 [V15.9] 全息 UI 国际化矩阵
            ui_i18n = {
                "zh-Hans": {
                    "nav_home": "门户", "nav_docs": "文档", "nav_blog": "博客", "nav_showcase": "案例", "nav_about": "关于",
                    "search_placeholder": "搜索主权资产...", "footer_motto": "物理主权数字花园", "footer_slogan": "物理主权，自洽生长。", "toc_title": "目录导航"
                },
                "en": {
                    "nav_home": "Home", "nav_docs": "Docs", "nav_blog": "Blog", "nav_showcase": "Showcase", "nav_about": "About",
                    "search_placeholder": "Search Assets...", "footer_motto": "Physical Sovereignty Digital Garden", "footer_slogan": "Physical Sovereignty, Self-Consistent Growth.", "toc_title": "Table of Contents"
                },
                "ja": {
                    "nav_home": "ホーム", "nav_docs": "ドキュメント", "nav_blog": "ブログ", "nav_showcase": "ショーケース", "nav_about": "アバウト",
                    "search_placeholder": "資産を検索...", "footer_motto": "物理的主権デジタルガーデン", "footer_slogan": "物理的主権、自己完結型の成長。", "toc_title": "目次"
                }
            }
            t = ui_i18n.get(lang, ui_i18n["en"])

            replacements = {
                "{{ title }}": fm.get('title', 'Untitled'),
                "{{ site_name }}": "Illacme Sovereign",
                "{{ description }}": fm.get('description', ''),
                "{{ keywords }}": ", ".join(fm.get('keywords', [])) if isinstance(fm.get('keywords'), list) else fm.get('keywords', ''),
                "{{ content }}": content_html,
                "{{ sidebar_container }}": sidebar_container,
                "{{ language_switcher }}": lang_switcher_html,
                "{{ root_path }}": root_path,
                "{{ lang_code | default('zh') }}": lang,
                "{{ layout_class }}": f"layout-{layout_type}",
                "{{ canonical_url }}": f"/{lang if not is_default else ''}/{prefix}/{fm.get('slug', '')}.html".replace('//', '/'),
                # 🚀 UI I18n 注入
                "{{ t_nav_home }}": t["nav_home"],
                "{{ t_nav_docs }}": t["nav_docs"],
                "{{ t_nav_blog }}": t["nav_blog"],
                "{{ t_nav_showcase }}": t["nav_showcase"],
                "{{ t_nav_about }}": t["nav_about"],
                "{{ t_search_placeholder }}": t["search_placeholder"],
                "{{ t_footer_motto }}": t["footer_motto"],
                "{{ t_footer_slogan }}": t["footer_slogan"],
                "{{ t_toc_title }}": t["toc_title"]
            }

            for key, val in replacements.items():
                template = template.replace(key, str(val))
            
            return template
        except Exception as e:
            logger.error(f"🛑 [Sovereign] 渲染模版失败: {e}")
            return content_html

    def _get_layout_type(self, prefix: str, sub_path: str, fm: Dict[str, Any] = None) -> str:
        """识别页面形态意图"""
        # 🚀 [V15.9] 路由主权对齐：强制大小写不敏感
        p_low = prefix.lower()
        slug_raw = fm.get('slug', '')
        slug = slug_raw.lower() if slug_raw else ""
        
        if p_low == "blog" or "blog" in slug: return "blog"
        if p_low == "showcase" or "showcase" in slug or (sub_path and "Showcase" in sub_path): return "showcase"
        if not sub_path or sub_path == "Index": return "page"
        return "docs"

    def _build_sidebar(self, lang: str, prefix: str, current_sub: str, root_path: str) -> str:
        """🚀 [V15.0] 树状侧边栏自动测绘引擎"""
        # 🚀 [V16.5] 命中缓存，直接返回预渲染片段
        cache_key = f"{lang}_{prefix}"
        if cache_key in SovereignSSGAdapter._sidebar_cache:
            return SovereignSSGAdapter._sidebar_cache[cache_key]

        from core.runtime.cli_bootstrap import get_global_engine
        engine = get_global_engine()
        if not engine: return ""
        
        db = engine.meta.data.get("documents", {})
        tree = {"_dirs": {}, "_files": []}
        
        # 1. 过滤并建立树结构
        for rel, info in db.items():
            # 🚀 [V15.9] 语种主权对齐：源语种文档可能没有 lang 字段，需兼容处理
            doc_lang = info.get('language') or info.get('lang')
            if doc_lang and doc_lang != lang:
                continue
            
            # 仅显示相同前缀下的文档，或 Index 下的非首页文档
            doc_prefix = info.get('route_prefix')
            if doc_prefix != prefix and prefix != "docs": 
                continue
            
            slug = info.get('slug')
            if not slug: continue
            
            # 分解物理子路径
            sub = info.get('sub_dir', '').strip('/')
            path_parts = sub.split('/') if sub else []
            
            curr = tree
            for part in path_parts:
                if part not in curr["_dirs"]: 
                    curr["_dirs"][part] = {"_dirs": {}, "_files": []}
                curr = curr["_dirs"][part]
            
            curr["_files"].append({
                "title": info.get('title', slug),
                "url": f"{root_path}{prefix}/{sub}/{slug}.html".replace('//', '/')
            })

        # 2. 递归生成 HTML
        def _render_tree(node, level=0):
            html = '<ul class="nav-list">'
            # 先渲染子目录 (支持折叠)
            for dirname, contents in node.get("_dirs", {}).items():
                html += f'<li class="nav-group"><div class="group-title"><span>{dirname}</span><span class="group-toggle">▼</span></div>'
                html += _render_tree(contents, level + 1)
                html += '</li>'
            # 后渲染文件
            for f_info in node.get("_files", []):
                title = f_info['title']
                url = f_info['url']
                html += f'<li class="nav-item"><a href="{url}" class="nav-link">{title}</a></li>'
            html += '</ul>'
            return html

        result = _render_tree(tree)
        SovereignSSGAdapter._sidebar_cache[cache_key] = result
        return result

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        """[Sovereignty] 元数据清洗"""
        fm['author'] = author_name
        if date_obj:
            fm['date_formatted'] = date_obj.strftime("%Y-%m-%d")
        return fm

    def render_callout(self, c_type: str, title: str, body: str) -> str:
        """[Sovereign] 呼号语法渲染：将 Obsidian 风格 Callouts 转化为美观的 HTML 容器"""
        icon_map = {"info": "ℹ️", "warning": "⚠️", "error": "🚫", "tip": "💡", "note": "📝"}
        icon = icon_map.get(c_type.lower(), "📝")
        return f"""
        <div class="callout callout-{c_type.lower()}">
            <div class="callout-header">
                <span class="callout-icon">{icon}</span>
                <span class="callout-title">{title or c_type.capitalize()}</span>
            </div>
            <div class="callout-body">{body}</div>
        </div>
        """

    def get_i18n_path_template(self, source_type: str = "docs") -> str:
        """主权路径模版：直接将语种作为根目录"""
        return "{lang}/{sub_dir}"
