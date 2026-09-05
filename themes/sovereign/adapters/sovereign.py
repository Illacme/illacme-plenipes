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
    PLUGIN_ID = 'sovereign'
    DISPLAY_NAME = 'Sovereign HTML'
    DESCRIPTION = '主权原生渲染引擎：零外部技术栈依赖，直出具有极致霓虹玻璃拟态美学的高级静态 HTML 知识库。'
    VERSION = 'V11.6'
    
    @classmethod
    def get_default_path_mappings(cls) -> Dict[str, str]:
        """🚀 [V76.0] 声明 Sovereign 适配器推荐的原生默认物理寻址映射"""
        return {
            'source_dir': "src/content",
            'site_dir': "dist",
            'assets_dir': "public/assets",
            'graph_json_dir': "public"
        }
    
    @classmethod
    def get_build_command(cls) -> str:
        """🚀 [V78.0] Sovereign 零依赖直出，无需 npm 构建，使用 echo 绕过"""
        return 'echo "Sovereign build completed"'
    
    def __init__(self, theme_settings: Any = None, engine=None):
        super().__init__(theme_settings, engine=engine)
        theme_name = getattr(theme_settings, 'name', 'sovereign')
        if theme_name == 'default': theme_name = 'sovereign'
        self.template_path = f"themes/{theme_name}/templates/layout.html"

    def has_autonomous_blog_engine(self) -> bool:
        """🚀 Sovereign 主题具备独立全息博客与展示流合成器"""
        return True

    def get_feature_slots(self) -> dict:
        """🚀 [V56.0] Sovereign 标准布局声明"""
        return {
            "docs": {
                "label": "📚 文档中心 (docs)",
                "single": "docs",
                "multi": "{lang}/docs"
            },
            "blog": {
                "label": "📰 博客文章 (blog)",
                "single": "blog",
                "multi": "{lang}/blog"
            },
            "showcase": {
                "label": "🎨 展示中心 (show)",
                "single": "showcase",
                "multi": "{lang}/showcase"
            },
            "pages": {
                "label": "📄 独立页面 (page)",
                "single": "",
                "multi": "{lang}"
            },
            "static": {
                "label": "📦 静态资源 (static)",
                "single": "static",
                "multi": "static"
            }
        }

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
        # sub_path 已包含完整的路由路径 (含语种段如 zh/docs)，深度直接由路径段数决定
        sub_dir = sub_path.strip('/')
        is_default = (target_lang == getattr(self, 'default_lang', 'zh'))
        depth = len(sub_dir.split('/')) if sub_dir else 0
        root_path = "../" * depth if depth > 0 else "./"

        # 4. Markdown 核心方言与扩展编译
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
            return f"\n@@CALLOUT:{idx}@@\n"
        body = callout_pattern.sub(_callout_collect, body)

        # 5.5 🚀 方言预处理：隔离 Mermaid 图表代码块 (防止被 codehilite/pygments 破坏转义)
        import html as _html
        mermaids = []
        mermaid_pattern = re.compile(r'```(?:mermaid|flowchart)\s*\n(.*?)\n```', re.DOTALL)
        
        def _mermaid_collect(match):
            raw_code = match.group(1).strip()
            idx = len(mermaids)
            html_code = _html.escape(raw_code)
            h = f'<div class="sovereign-mermaid-diagram"><pre class="mermaid">{html_code}</pre></div>'
            mermaids.append(h)
            return f"\n@@MERMAID:{idx}@@\n"
        # 4.5 🚀 [WikiLink & Relative Link Dynamic Resolver] 将双向链接与相对链接动态解析为真实落盘路径
        from core.adapters.egress.ssg.generic_shards.navigation_builder import get_doc_slug_map
        slug_map = get_doc_slug_map(self.engine)

        trans_cfg = getattr(getattr(self.engine, 'config', None), 'translation', None)
        dir_mode = getattr(trans_cfg, 'slug_dir_mode', 'nested') if trans_cfg else 'nested'

        # 推导当前页面相对于根目录的相对路径
        sub_clean = sub_path.replace('\\', '/').strip('/')
        parts = [p for p in sub_clean.split('/') if p and not p.endswith('.html')]
        depth = len(parts)
        root_path = "../" * depth if depth > 0 else "./"

        def _resolve_relative_url(clean_target: str, anchor: str = "") -> str:
            """统一将相对原稿或旧相对路径转换为匹配当前 slug_dir_mode 的物理落地路径"""
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

            # 🎯 2. 文档与页面映射识别 (防止非首页的 index 误回退到根目录首页)
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
                    # 极简根目录：单篇与专区首页都在根目录
                    target_dir = ""
                elif dir_mode == 'prefix':
                    target_dir = ""
                    if channel and channel not in ('', 'pages') and not actual_slug.startswith(f"{channel}-"):
                        actual_slug = f"{channel}-{actual_slug}"
                else:
                    # nested 目录树复刻
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
                parts = clean_target.split('#', 1)
                clean_target = parts[0]
                anchor = f"#{parts[1]}"
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
                parts = clean_target.split('#', 1)
                clean_target = parts[0]
                anchor = f"#{parts[1]}"
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
                parts = clean_href.split('#', 1)
                clean_href = parts[0]
                anchor = f"#{parts[1]}"
            if clean_href.endswith(('.html', '.md')):
                resolved_url = _resolve_relative_url(clean_href, anchor)
                return f'<a {prefix_attr}href="{resolved_url}"{suffix_attr}>'
            return match.group(0)

        wiki_pattern = re.compile(r'(?<!\!)\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
        body = wiki_pattern.sub(_wikilink_repl, body)
        body = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', _mdlink_repl, body)
        # 🔗 对 HTML <a href="..."> 相对链接同样做动态路由重写，使内嵌 HTML 完全契合 slug_dir_mode
        html_a_pattern = re.compile(r'<a\s+([^>]*?)href=["\']([^"\']+)["\']([^>]*)>', re.IGNORECASE)
        body = html_a_pattern.sub(_html_a_repl, body)

        html_fragment = markdown.markdown(body, extensions=['extra', 'codehilite', 'toc', 'nl2br'])
        
        # 7. 还原 Callout 与 Mermaid HTML 容器
        for i, callout_h in enumerate(callouts):
            html_fragment = re.sub(rf'<p>@@CALLOUT:{i}@@(?:<br\s*/?>)?\s*</p>|@@CALLOUT:{i}@@', callout_h, html_fragment)
        for i, mermaid_h in enumerate(mermaids):
            html_fragment = re.sub(rf'<p>@@MERMAID:{i}@@(?:<br\s*/?>)?\s*</p>|@@MERMAID:{i}@@', mermaid_h, html_fragment)

        # 8. 加载物理模版 (layout.html)
        full_html = self._apply_template(html_fragment, fm, target_lang, sub_path, is_default=is_default)

        # 9. 🚀 [V11.8] 资产原子搬运 (Singleton Copy) - 严禁污染 themes/ 母本目录
        if not SovereignSSGAdapter._assets_copied:
            with SovereignSSGAdapter._assets_lock:
                if not SovereignSSGAdapter._assets_copied:
                    import shutil
                    theme_root = os.path.dirname(os.path.dirname(self.template_path))
                    static_src = os.path.join(theme_root, "static")
                    
                    dist_root = None
                    if self.engine and hasattr(self.engine, "paths"):
                        dist_root = self.engine.paths.get("site_dir")
                    
                    # 🛡️ [Rule 13] 若未配置输出路径（如纯内存单测），严禁回退至母本目录创建 dist/
                    if dist_root:
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
        from .sovereign_helpers import apply_template
        return apply_template(self, content_html, fm, lang, sub_path, is_default)

    def _get_layout_type(self, prefix: str, sub_path: str, fm: Dict[str, Any] = None) -> str:
        """识别页面形态意图"""
        from .sovereign_helpers import get_layout_type
        return get_layout_type(self, prefix, sub_path, fm)

    def _build_sidebar(self, lang: str, prefix: str, current_sub: str, root_path: str) -> str:
        """🚀 [V15.0] 树状侧边栏自动测绘引擎"""
        from .sovereign_helpers import build_sidebar
        return build_sidebar(self, lang, prefix, current_sub, root_path)

    def render_callout(self, c_type: str, title: str, body: str) -> str:
        """[Sovereign] 呼号语法渲染：将 Obsidian 风格 Callouts 转化为美观的 HTML 容器"""
        from .sovereign_helpers import render_callout
        return render_callout(c_type, title, body)

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        """[Sovereignty] 元数据清洗"""
        fm['author'] = author_name
        if date_obj:
            fm['date_formatted'] = date_obj.strftime("%Y-%m-%d")
        return fm

    def get_i18n_path_template(self, source_type: str = "docs") -> str:
        """主权路径模版：直接将语种作为根目录"""
        return "{lang}/{sub_dir}"
