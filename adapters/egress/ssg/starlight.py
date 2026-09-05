#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Starlight SSG Adapter
模块职责：负责 Astro Starlight 语法的标准化转换。
🛡️ [AEL-Iter-v5.3]：物理隔离的渲染插件实现。
"""

from typing import Dict, Any, Tuple
from core.adapters.egress.ssg.base import BaseSSGAdapter

class StarlightAdapter(BaseSSGAdapter):
    """🚀 Starlight 专属渲染引擎"""
    PLUGIN_ID = "starlight"
    DISPLAY_NAME = "Starlight Engine"
    VERSION = "V2.0"
    DESCRIPTION = "驱动 Astro Starlight 架构的文档渲染，完美支持 Asides 容器语法与物理路径投影。"
    
    @classmethod
    def get_default_path_mappings(cls) -> Dict[str, str]:
        """🚀 [V76.0] Starlight 推荐的原生默认物理寻址映射"""
        return {
            'source_dir': "src/content/docs",
            'site_dir': "dist",
            'assets_dir': "public/assets",
            'graph_json_dir': "public"
        }
    
    _GENERIC_MAP = {
        'info': 'note', 'abstract': 'note', 'note': 'note', 'question': 'note',
        'warning': 'caution', 'attention': 'caution',
        'error': 'danger', 'bug': 'danger', 'danger': 'danger',
        'success': 'tip', 'check': 'tip', 'tip': 'tip'
    }
    def get_feature_slots(self) -> dict:
        """🚀 [V56.0] Starlight 标准布局声明：需对齐主题 sidebar 自动生成规则"""
        return {
            "docs": {
                "label": "文档中心",
                "single": "docs",
                "multi": "{lang}/docs"
            },
            "blog": {
                "label": "博客文章",
                "single": "blog",
                "multi": "{lang}/blog"
            },
            "showcase": {
                "label": "展示橱窗",
                "single": "showcase",
                "multi": "{lang}/showcase"
            },
            "pages": {
                "label": "展示页面",
                "single": "",
                "multi": "{lang}"
            },
            "static": {
                "label": "静态资产",
                "single": "../../public",
                "multi": "../../public"
            }
        }
    
    IS_CLEAN_URL = True

    def render(self, body: str, fm: Dict[str, Any], seo_data: Dict[str, Any] = None, target_lang: str = "en", sub_path: str = "") -> Tuple[str, Dict[str, Any]]:
        """🚀 [V10.3] Starlight 深度渲染：SEO 注入与元数据对齐"""
        new_fm = fm.copy()
        
        # 1. 注入 AI 生成的 SEO 元数据
        if seo_data:
            # Starlight 允许直接在 Frontmatter 中使用 description
            if seo_data.get('description'):
                new_fm['description'] = seo_data.get('description')
            
        # 2. 智能规范化文档排序属性
        if 'order' in new_fm:
            order_val = new_fm.pop('order')
            try:
                order_val = int(order_val)
            except (ValueError, TypeError):
                pass
            new_fm['sidebar'] = {"order": order_val}

        # 3. 🛡️ 在 Starlight 架构下，frontmatter 中的 slug 会覆盖目录物理路径并破坏多语言隔离
        # 移除 frontmatter 中的 slug，让 Starlight 完全基于真实的物理文件拓扑计算多语言路由
        new_fm.pop('slug', None)

        # 4. 智能剥离正文首行冗余的 H1 标题，防止与 Starlight 页面框架自带的 <h1>{fm.title}</h1> 冲突产生双标题
        lines = body.split('\n')
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith('# '):
                h1_text = stripped[2:].strip()
                # 若正文首行标题带 emoji 且更加生动完整，赋给 new_fm['title']
                if h1_text and len(h1_text) >= len(new_fm.get('title', '')):
                    new_fm['title'] = h1_text
                # 从正文移除该首行 H1
                lines.pop(idx)
            break

        # 🛡️ 正文排版层级韧性自愈 (Heading & Paragraph Resilience Guard)
        # 扫描剥离首行后剩余的正文内容：
        # 1) 若存在误加 '# ' 的长文本段落（如译文简介、长度 > 35 或包含句子标点），强制剥离 '# ' 还原为普通正文段落，杜绝巨大字体排版断崖；
        # 2) 若存在残留的 '# ' 短小章节标题，自动降级为 '## ' (H2)，避免在现代 SSG 框架下破坏大纲树与字体层级
        healed_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('# '):
                header_body = stripped[2:].strip()
                is_paragraph_sentence = (len(header_body) > 35 or any(p in header_body for p in ['。', '！', '!', '？', '?', '...', '…']))
                if is_paragraph_sentence:
                    healed_lines.append(header_body)
                else:
                    healed_lines.append('## ' + header_body)
            else:
                healed_lines.append(line)
        cleaned_body = '\n'.join(healed_lines)

        # 5. 链接与双链自愈标准化 (Universal Link & Wikilink Healing，Starlight 使用 Clean URL 规范)
        healed_body = self.normalize_markdown_content(cleaned_body, sub_path=sub_path, target_lang=target_lang, clean_url=True)

        return healed_body, new_fm

    def render_callout(self, g_type: str, title: str, body: str) -> str:
        target_type = self._GENERIC_MAP.get(g_type.lower(), 'note')
        # Starlight 使用 ::: 容器语法
        res = f"\n:::{target_type}"
        if title: res += f" [{title}]"
        res += f"\n{body}\n:::\n\n"
        return res

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        # Starlight 默认元数据映射
        new_fm = fm.copy()
        if hasattr(date_obj, 'strftime'):
            new_fm['lastUpdated'] = date_obj
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
            
        return LanguageHub.get_physical_path(
            iso_code,
            theme="starlight",
            source_lang=source_lang,
            force_prefix=force_prefix
        )

    def get_i18n_path_template(self, source_type: str = "docs") -> str:
        """
        [Sovereignty] Starlight 特有的多语言路径规范 (通常是根目录下的语言前缀)
        """
        return "{lang}/{sub_dir}"
