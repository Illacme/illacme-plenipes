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
            'source_dir': "src/content",
            'site_dir': "dist",
            'assets_dir': "public/assets",
            'graph_json_dir': "public"
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
        # 🚀 [V80.0] 自动物理探测并加载主题自描述 JSON Schema 协议
        import os
        import json
        self.theme_schema = {}
        if self.theme_settings:
            theme_name = getattr(self.theme_settings, 'name', 'default')
            schema_path = os.path.join("themes", theme_name, "theme.schema.json")
            if os.path.exists(schema_path):
                try:
                    with open(schema_path, 'r', encoding='utf-8') as f:
                        self.theme_schema = json.load(f)
                except Exception:
                    pass

    def get_custom_options(self) -> Dict[str, Any]:
        """
        🚀 [V80.0] 获取并合并强校验的主题自定义选项映射。
        自动将用户填写的 theme_settings.options 与主题 schema 默认值进行深层合并，实现自愈降级。
        """
        options = {}
        properties = self.theme_schema.get("properties", {})
        for key, prop in properties.items():
            if "default" in prop:
                options[key] = prop["default"]
                
        # 🚀 [Unified Promotion Architecture] 引入全局基础信息继承层 (I&O Engine)
        # 如果全局配置中定义了通用合规与视觉基础，将其作为基底加载（实现跨主题单一数据源）
        if hasattr(self, 'engine') and self.engine and hasattr(self.engine, 'config'):
            cfg = self.engine.config
            
            # 自愈逻辑：site_name Fallback 为 imprint_name/press_name; site_description Fallback 为 imprint_description
            g_site_name = getattr(cfg, "site_name", None) or getattr(cfg, "imprint_name", None)
            g_site_desc = getattr(cfg, "site_description", None) or getattr(cfg, "imprint_description", None)
            
            # 版权声明自愈逻辑：彻底合并为单数据源，直接继承自全域默认版权设置 frontmatter_defaults.copyright
            fm_defaults = getattr(cfg, "frontmatter_defaults", {}) or {}
            g_copyright = fm_defaults.get("copyright", None)
            
            global_promotions = {
                "site_name": g_site_name,
                "site_description": g_site_desc,
                "favicon_path": getattr(cfg, "favicon_path", None),
                "logo_path": getattr(cfg, "logo_path", None),
                "footer_copyright": g_copyright
            }
            
            for g_key, g_val in global_promotions.items():
                if g_val is not None and str(g_val).strip() != "":
                    options[g_key] = g_val
                    
        if self.theme_settings and hasattr(self.theme_settings, 'options') and self.theme_settings.options:
            for key, val in self.theme_settings.options.items():
                if val is not None and str(val).strip() != "":
                    options[key] = val
        return options

    @abc.abstractmethod
    def render(self, body: str, fm: Dict[str, Any], seo_data: Dict[str, Any] = None, target_lang: str = "en", sub_path: str = "") -> Tuple[str, Dict[str, Any]]:
        """[Contract] 执行特定 SSG 的语法转换与元数据增强。"""
        pass

    def supports_frontmatter(self, ext: str) -> bool:
        """🚀 [V15.6] 判定特定扩展名是否支持元数据头"""
        if not ext: return False
        return ext.lower() in self.frontmatter_extensions

    def get_output_schema(self) -> List[str]:
        """🚀 [V11.2] 获取该适配器支持的输出出口列表。"""
        schema = ["source"]
        if hasattr(self, 'active_renderer') and self.active_renderer:
            schema.append("static")
        return schema

    def get_feature_slots(self) -> Dict[str, Dict[str, str]]:
        """🚀 [V56.0] 意图感知协议：声明该适配器支持的功能槽及其物理路径映射。"""
        return {
            "docs": {"label": "文档中心", "single": "docs", "multi": "i18n/{lang}/docs"},
            "blog": {"label": "博客文章", "single": "blog", "multi": "i18n/{lang}/blog"},
            "pages": {"label": "独立页面", "single": "pages", "multi": "i18n/{lang}/pages"},
            "static": {"label": "静态资产", "single": "static", "multi": "static"}
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
        """[Sovereignty] 物理路径语种对齐。"""
        from core.utils.language_hub import LanguageHub
        iso_code = LanguageHub.resolve_to_iso(logic_code)
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
          path: {site_dir}
          
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
"""

    def compile_theme_options(self) -> bool:
        """
        🎯 [SSG 热对齐] 将用户最新的自定义主题选项编译并输出为物理层样式，
        使 SSG 引擎或前台预览能免刷新、瞬时热感知。
        """
        options = self.get_custom_options()
        theme_name = getattr(self.theme_settings, 'name', 'default')
        
        import os
        assets_dir = os.path.join("themes", theme_name, "static", "assets")
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir, exist_ok=True)
            
        style_path = os.path.join(assets_dir, "theme.options.css")
        
        # 🚀 [V88.8] 原厂样式防卫拦截网：在未显式勾选自定义开关时，完全不编译输出任何 CSS 视觉变量，以 100% 保持主题出厂的最佳质感与稳健度！
        if not options.get('enable_custom_style', False):
            try:
                if os.path.exists(style_path):
                    os.remove(style_path)
            except Exception:
                pass
                
            # 虽清除/不输出高危 CSS 视觉变量，但保留导出基础 JS/JSON 桥接文件，确保 site_name, logo 等非破坏性工程参数安全生效
            json_path = os.path.join("themes", theme_name, "theme.options.json")
            js_path = os.path.join("themes", theme_name, "theme.options.js")
            try:
                import json
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(options, f, indent=2, ensure_ascii=False)
                js_content = "// 🚀 [V88.0 Live Hot-Reload] 自动生成的主题选项常量，请勿手动编辑\n"
                js_content += f"export const themeOptions = {json.dumps(options, indent=2, ensure_ascii=False)};\n"
                js_content += "export default themeOptions;\n"
                with open(js_path, 'w', encoding='utf-8') as f:
                    f.write(js_content)
            except Exception:
                pass
            return True
            
        css_vars = []
        for k, v in options.items():
            if isinstance(v, (str, int, float)) and not str(v).startswith("http"):
                css_key = k.replace("_", "-")
                css_vars.append(f"  --{css_key}: {v};")
                
        css_content = "/* 🚀 [V74.96 Live Hot-Reload] 自动生成的主题运行时变量对齐，请勿手动编辑 */\n"
        css_content += ":root {\n" + "\n".join(css_vars) + "\n}\n"
        
        try:
            with open(style_path, 'w', encoding='utf-8') as f:
                f.write(css_content)
        except Exception:
            pass
            
        # 🚀 [V88.0] 物理 JSON 桥接：将自愈合并后的自定义选项导出至主题根目录，供异构 SSG 编译热加载
        json_path = os.path.join("themes", theme_name, "theme.options.json")
        try:
            import json
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(options, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
            
        # 🚀 [V88.0] 纯前端 JS 桥接：生成无 Node.js 模块依赖的纯前端 JS 常量文件，彻底绕过 Webpack/Vite 客户端打包时的 fs 模块丢失限制
        js_path = os.path.join("themes", theme_name, "theme.options.js")
        try:
            import json
            js_content = "// 🚀 [V88.0 Live Hot-Reload] 自动生成的主题选项常量，请勿手动编辑\n"
            js_content += f"export const themeOptions = {json.dumps(options, indent=2, ensure_ascii=False)};\n"
            js_content += "export default themeOptions;\n"
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(js_content)
        except Exception:
            pass
            
        return True
