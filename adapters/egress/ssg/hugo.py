#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Hugo SSG Adapter
模块职责：负责 Hugo 语法的物理转换与默认路径映射。
🛡️ [V76.0]：高自治适配器，支持 Go Hugo 专属 Shortcode。
"""

from typing import Dict, Any, Tuple
from core.adapters.egress.ssg.base import BaseSSGAdapter

class HugoAdapter(BaseSSGAdapter):
    """🚀 Hugo 专属渲染引擎"""
    PLUGIN_ID = "hugo"
    DISPLAY_NAME = "Hugo Engine"
    VERSION = "V1.0"
    DESCRIPTION = "驱动 Go 编写的 Hugo 极速排版渲染，支持 Go HTML 模板、Shortcode 与物理本地化对齐。"

    _GENERIC_MAP = {
        'info': 'note', 'abstract': 'note', 'note': 'note', 'question': 'note',
        'warning': 'warning', 'attention': 'warning', 'caution': 'warning',
        'error': 'danger', 'bug': 'danger', 'danger': 'danger',
        'success': 'tip', 'check': 'tip', 'tip': 'tip'
    }

    @classmethod
    def get_default_path_mappings(cls) -> Dict[str, str]:
        """🚀 [V76.0] Hugo 推荐的原生默认物理寻址映射"""
        return {
            'source_dir': "content",
            'site_dir': "public",
            'assets_dir': "static/assets",
            'graph_json_dir': "static"
        }

    def get_feature_slots(self) -> dict:
        """🚀 [V56.0] Hugo 标准布局声明 (对齐 Hugo content)"""
        return {
            "docs": {
                "label": "文档中心",
                "single": "content",
                "multi": "content/{lang}"
            },
            "blog": {
                "label": "博客文章",
                "single": "content/blog",
                "multi": "content/{lang}/blog"
            },
            "pages": {
                "label": "展示页面",
                "single": "content/custom",
                "multi": "content/{lang}/custom"
            },
            "static": {
                "label": "静态资产",
                "single": "static",
                "multi": "static"
            }
        }

    def render(self, body: str, fm: Dict[str, Any], seo_data: Dict[str, Any] = None, target_lang: str = "en", sub_path: str = "") -> Tuple[str, Dict[str, Any]]:
        """Hugo 渲染逻辑：支持标准 Frontmatter 与 SEO 字段注入"""
        new_fm = fm.copy()
        if seo_data:
            new_fm = self.inject_seo(new_fm, seo_data.get('description'), seo_data.get('keywords'))
        
        # 智能兼容落地页模板 (Hugo 使用 layout: landing)
        if new_fm.get('template') == 'splash':
            new_fm['layout'] = 'landing'
            new_fm.pop('template', None)
            
        return body, new_fm

    def render_callout(self, g_type: str, title: str, body: str) -> str:
        """Hugo 专属 Shortcode `{{% notice type %}}` 标签块语法渲染"""
        target_type = self._GENERIC_MAP.get(g_type.lower(), 'note')
        res = f"\n{{{{% notice {target_type} %}}}}"
        if title:
            res += f"\n**{title}**\n"
        res += f"\n{body}\n{{{{% /notice %}}}}\n\n"
        return res

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        return fm

    def get_language_code(self, logic_code: str) -> str:
        from core.utils.language_hub import LanguageHub
        iso_code = LanguageHub.resolve_to_iso(logic_code)
        
        source_lang = "zh"
        force_prefix = False
        if self.engine and hasattr(self.engine, "config"):
            source_lang = self.engine.config.i18n_settings.source.lang_code
            force_prefix = self.engine.config.i18n_settings.force_source_prefix
            
        return LanguageHub.get_physical_path(
            iso_code,
            theme="generic",
            source_lang=source_lang,
            force_prefix=force_prefix
        )

    def get_i18n_path_template(self, source_type: str = "docs") -> str:
        return "{lang}/{sub_dir}"

    @classmethod
    def get_build_command(cls) -> str:
        """🚀 [V78.0] 返回 Hugo 的标准构建命令"""
        return "hugo --minify"

    @classmethod
    def get_deploy_script_template(cls) -> str:
        """🚀 [V78.0] 返回 Hugo 本地部署脚本"""
        return """#!/bin/bash
# 🚀 Illacme Plenipes Sovereign Local Hugo Deployment Script
# SSG Type: {ssg_type}
# Generated at: {datetime}

set -e

echo "🟢 1. 正在执行 Hugo 环境校验..."
if ! command -v hugo &> /dev/null; then
    echo "❌ 错误: 本地未安装 Hugo CLI！请通过 'brew install hugo' 安装。"
    exit 1
fi

echo "📦 2. 开始构建生产环境静态站点..."
{build_cmd}

echo "🚀 3. 部署资产对正完毕，就绪发布！"
"""

    @classmethod
    def get_github_actions_template(cls) -> str:
        """🚀 [V78.0] 返回 Hugo 专用的 GitHub Actions 模板"""
        return """name: Deploy Sovereign Website (Hugo)

on:
  push:
    branches:
      - main
      - master

permissions:
  contents: write
  pages: write
  id-token: write

concurrency:
  group: 'pages'
  cancel-in-progress: true

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          submodules: recursive
          fetch-depth: 0
          
      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: 'latest'
          extended: true
          
      - name: Build Hugo Site
        run: {build_cmd}
        
      - name: Upload Artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: {site_dir}
          
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
"""
