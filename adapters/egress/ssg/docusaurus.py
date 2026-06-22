#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Docusaurus SSG Adapter
模块职责：负责 Docusaurus v2/v3 语法的标准化转换。
🛡️ [AEL-Iter-v5.3]：物理隔离的渲染插件实现。
"""

from typing import Tuple, Dict, Any
from core.adapters.egress.ssg.base import BaseSSGAdapter

class DocusaurusAdapter(BaseSSGAdapter):
    """🚀 Docusaurus 专属渲染引擎"""
    PLUGIN_ID = "docusaurus"
    DISPLAY_NAME = "Docusaurus Engine"
    VERSION = "V1.8"
    DESCRIPTION = "驱动 Facebook Docusaurus 架构的排版渲染，支持 MDX、Admonitions 与多语言深度对齐。"
    
    @classmethod
    def get_default_path_mappings(cls) -> Dict[str, str]:
        """🚀 [V76.0] Docusaurus 推荐的原生默认物理寻址映射"""
        return {
            'source_dir': ".",
            'site_dir': "build",
            'assets_dir': "static/assets",
            'graph_json_dir': "static"
        }
    
    _GENERIC_MAP = {
        'info': 'info', 'note': 'info', 'warning': 'warning',
        'danger': 'danger', 'error': 'danger', 'success': 'success', 'tip': 'tip'
    }

    def get_feature_slots(self) -> Dict[str, Dict[str, str]]:
        """🚀 [V56.0] Docusaurus 标准布局声明"""
        return {
            "docs": {
                "label": "文档中心",
                "single": "docs",
                "multi": "i18n/{lang}/docusaurus-plugin-content-docs/current"
            },
            "blog": {
                "label": "博客文章",
                "single": "blog",
                "multi": "i18n/{lang}/docusaurus-plugin-content-blog"
            },
            "pages": {
                "label": "独立页面",
                "single": "src/pages",
                "multi": "i18n/{lang}/docusaurus-plugin-content-pages"
            },
            "static": {
                "label": "静态资产",
                "single": "static",
                "multi": "static"
            }
        }

    def render(self, body: str, fm: Dict[str, Any], seo_data: Dict[str, Any] = None, target_lang: str = "en", sub_path: str = "") -> Tuple[str, Dict[str, Any]]:
        """🚀 [V10.3] Docusaurus 深度渲染：SEO 注入与链接自愈"""
        new_fm = fm.copy()
        
        # 1. 注入 AI 生成的 SEO 元数据
        if seo_data:
            new_fm = self.inject_seo(new_fm, seo_data.get('description'), seo_data.get('keywords'))
            
        # 2. 链接自愈 (Link Healing)
        import re
        def heal_link(match):
            text, path = match.groups()
            if path.endswith('.md') and not path.startswith('http'):
                return f"[{text}]({path})"
            return match.group(0)
            
        healed_body = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', heal_link, body)
        
        # 3. 智能兼容落地页模板
        if new_fm.get('template') == 'splash':
            new_fm['hide_table_of_contents'] = True
            new_fm['hide_title'] = True
            new_fm.pop('template', None)

        # 4. 智能规范化文档排序属性 (Docusaurus 使用 sidebar_position)
        if 'order' in new_fm:
            order_val = new_fm.pop('order')
            try:
                order_val = int(order_val)
            except (ValueError, TypeError):
                pass
            new_fm['sidebar_position'] = order_val

        return healed_body, new_fm

    def render_callout(self, g_type: str, title: str, body: str) -> str:
        target_type = self._GENERIC_MAP.get(g_type.lower(), 'info')
        # Docusaurus 使用 ::: 容器语法
        res = f"\n:::{target_type}"
        if title: res += f" {title}"
        res += f"\n{body}\n:::\n\n"
        return res

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        new_fm = fm.copy()
        if hasattr(date_obj, 'strftime'):
            new_fm['last_update'] = {'date': date_obj.strftime('%Y-%m-%d')}
        return new_fm

    def get_language_code(self, logic_code: str) -> str:
        from core.utils.language_hub import LanguageHub
        iso_code = LanguageHub.resolve_to_iso(logic_code)
        
        # 🚀 [V57.0] 注入主权配置参数
        source_lang = "zh"
        force_prefix = False
        if self.engine and hasattr(self.engine, "config"):
            source_lang = self.engine.config.i18n_settings.source.lang_code
            force_prefix = self.engine.config.i18n_settings.force_source_prefix
            
        # 🚀 [Docusaurus 规范化自愈]
        # Docusaurus 要求其默认语言一律不加 i18n 物理路径前缀（即直接落盘于主 docs/ 目录）
        source_iso = LanguageHub.resolve_to_iso(source_lang)
        if source_iso == "auto":
            source_iso = "zh"
            
        current_iso = iso_code
        if current_iso == "auto":
            current_iso = "zh"
            
        if current_iso == source_iso:
            return ""
            
        return LanguageHub.get_physical_path(
            iso_code,
            theme="docusaurus",
            source_lang=source_lang,
            force_prefix=force_prefix
        )

    def get_i18n_path_template(self, source_type: str = "docs") -> str:
        # 🚀 [V55.24] 动态路由：针对 Docusaurus 的非线性 i18n 物理结构进行适配
        plugin_map = {
            "docs": "docusaurus-plugin-content-docs/current",
            "blog": "docusaurus-plugin-content-blog",
            "pages": "docusaurus-plugin-content-pages"
        }
        plugin_path = plugin_map.get(source_type.lower(), plugin_map["docs"])
        
        # 🛡️ 核心对正：如果 {lang} 为空，RouteManager 会解析为默认语言，此时应使用 docs 根目录
        # 我们返回一个特殊的复合模板，RouteManager 将在运行时根据 physical_lang 决定分支
        # 这里的策略是：如果存在 lang，则走 i18n 分流；如果不存在，则走 docs 默认
        if source_type == "docs":
            return "i18n/{lang}/docusaurus-plugin-content-docs/current/{sub_dir}"
        return f"i18n/{{lang}}/{plugin_path}/{{sub_dir}}"
