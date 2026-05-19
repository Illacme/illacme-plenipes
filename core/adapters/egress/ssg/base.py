#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SSG Rendering Base
模块职责：定义 SSG 输出端渲染器的基类协议。
🛡️ [AEL-Iter-v5.3]：全链路解耦的渲染基座。
"""
import abc
from typing import Tuple, Dict, Any, List

class BaseSSGAdapter(abc.ABC):
    PLUGIN_ID = "generic"
    """所有 SSG 渲染插件的抽象基类"""
    
    @classmethod
    def get_default_path_mappings(cls) -> Dict[str, str]:
        """🚀 [V76.0] 声明该适配器推荐的原生默认物理寻址映射"""
        return {
            'source_dir': "content",
            'static_dir': "public",
            'assets_dir': "static/assets",
            'graph_json_dir': "static"
        }

    def __init__(self, theme_settings: Any = None, engine=None):
        self.theme_settings = theme_settings
        self.engine = engine
        self.default_lang = "zh"

        # 🚀 [V11.2] 双相出口扩展名定义
        self.output_extensions = {
            "source": None,  # 🚀 [V12.0] None 表示跟随原文件后缀
            "static": ".html"
        }
        # 🚀 [V11.2] 默认语言路径契约：是否强制在物理路径中包含语言前缀
        self.force_default_lang_prefix = False
        # 🚀 [V15.6] 元数据主权：定义哪些输出后缀支持 Frontmatter
        self.frontmatter_extensions = [".md", ".mdx", ".markdown"]

    @abc.abstractmethod
    def render(self, body: str, fm: Dict[str, Any], seo_data: Dict[str, Any] = None, target_lang: str = "en", sub_path: str = "") -> Tuple[str, Dict[str, Any]]:
        """
        [Contract] 执行特定 SSG 的语法转换与元数据增强。
        """
        pass

    def supports_frontmatter(self, ext: str) -> bool:
        """🚀 [V15.6] 判定特定扩展名是否支持元数据头"""
        if not ext: return False
        return ext.lower() in self.frontmatter_extensions

    def get_output_schema(self) -> List[str]:
        """
        🚀 [V11.2] 获取该适配器支持的输出出口列表。
        默认为 ['source']，如果支持静态渲染则返回 ['source', 'static']。
        """
        schema = ["source"]
        if hasattr(self, 'active_renderer') and self.active_renderer:
            schema.append("static")
        return schema

    def get_feature_slots(self) -> Dict[str, Dict[str, str]]:
        """
        🚀 [V56.0] 意图感知协议：声明该适配器支持的功能槽及其物理路径映射。
        返回格式: {
            "slot_id": {
                "label": "人类可读名称",
                "single": "单语言相对路径",
                "multi": "多语言相对路径(含{lang}占位符)"
            }
        }
        """
        return {
            "docs": {
                "label": "文档中心",
                "single": "docs",
                "multi": "i18n/{lang}/docs"
            },
            "blog": {
                "label": "博客文章",
                "single": "blog",
                "multi": "i18n/{lang}/blog"
            },
            "pages": {
                "label": "独立页面",
                "single": "pages",
                "multi": "i18n/{lang}/pages"
            },
            "static": {
                "label": "静态资产",
                "single": "static",
                "multi": "static"
            }
        }

    def adapt_metadata(self, fm: dict, date_obj, author_name) -> dict:
        """[Sovereignty] 物理元数据方言适配"""
        return fm

    def inject_seo(self, fm: dict, description: str, keywords: list) -> dict:
        """[SEO] 框架感知的 SEO 字段映射协议"""
        if description: fm['description'] = description
        if keywords: fm['keywords'] = keywords
        return fm

    def get_language_code(self, logic_code: str) -> str:
        """
        [Sovereignty] 物理路径语种对齐。
        """
        from core.utils.language_hub import LanguageHub
        iso_code = LanguageHub.resolve_to_iso(logic_code)
        # 🛡️ 如果不强制前缀且为默认语言，返回空字符串以匹配根路径
        if not self.force_default_lang_prefix and iso_code == LanguageHub.resolve_to_iso(self.default_lang):
            return ""
        return LanguageHub.get_physical_path(iso_code, "generic")

    def get_i18n_path_template(self, source_type: str = "docs") -> str:
        """
        [Sovereignty] 获取当前 SSG 的多语言路径模版。
        """
        return "{lang}/{sub_dir}"

    @classmethod
    def get_build_command(cls) -> str:
        """🚀 [V78.0] 返回该 SSG 引擎的标准构建命令"""
        return "npm run build"

    @classmethod
    def get_deploy_script_template(cls) -> str:
        """🚀 [V78.0] 返回本地一键部署的通用 shell 脚本模板"""
        return """#!/bin/bash
# 🚀 Illacme Plenipes Sovereign Local Deployment Script
# SSG Type: {ssg_type}
# Generated at: {datetime}

set -e

echo "🟢 1. 正在执行 {ssg_type} 的依赖核验与安装..."
if [ -f "package.json" ]; then
    npm install
fi

echo "📦 2. 开始构建生产环境静态站点..."
{build_cmd}

echo "🚀 3. 部署资产对正完毕，就绪发布！"
"""

    @classmethod
    def get_github_actions_template(cls) -> str:
        """🚀 [V78.0] 返回 GitHub Actions CI/CD 流水线模板"""
        return """name: Deploy Sovereign Website

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
        
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          
      - name: Install Dependencies
        run: npm ci || npm install
        
      - name: Build Site
        run: {build_cmd}
        
      - name: Upload Artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: {static_dir}
          
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
"""
