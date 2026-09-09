#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Cross-Theme Link Doctor (跨主题多语言内链巡检中枢)
模块职责：模拟全系 SSG 适配器在不同多语言拓扑下的链接转译结果，深度排查 404 与格式陷阱。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
from typing import Dict, Any, List, Tuple
from core.adapters.egress.ssg.registry import SSGRegistry
from core.adapters.egress.ssg.generic_shards.navigation_builder import get_doc_slug_map

class CrossThemeLinkDoctor:
    """🛰️ 全系 SSG 跨语言内链健康诊断器"""

    THEMES = ["sovereign", "universal", "nextra", "docusaurus", "starlight", "vitepress"]
    LOCALES = ["zh", "en", "ja"]

    @classmethod
    def extract_links_from_markdown(cls, md_text: str) -> List[Dict[str, str]]:
        """从 Markdown 文本中提取所有原稿内链（双链、标准相对链接）"""
        links = []
        
        # 1. 提取双向链接 [[target|alias]] 或 [[target]]
        wiki_pat = re.compile(r'(?<!\!)\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
        for m in wiki_pat.finditer(md_text):
            raw_target = m.group(1).strip()
            alias = (m.group(2) or raw_target).strip()
            if not raw_target.startswith(('http://', 'https://', 'mailto:')):
                links.append({"type": "wikilink", "raw": m.group(0), "target": raw_target, "alias": alias})

        # 2. 提取标准 Markdown 链接 [alias](target)
        md_pat = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        for m in md_pat.finditer(md_text):
            alias = m.group(1).strip()
            target = m.group(2).strip()
            if not target.startswith(('http://', 'https://', 'mailto:', '#')):
                links.append({"type": "mdlink", "raw": m.group(0), "target": target, "alias": alias})

        # 3. 提取 HTML 原生链接 <a href="...">
        html_pat = re.compile(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)
        for m in html_pat.finditer(md_text):
            target = m.group(1).strip()
            alias = re.sub(r'<[^>]+>', '', m.group(2)).strip() or target
            if not target.startswith(('http://', 'https://', 'mailto:', '#')):
                links.append({"type": "htmllink", "raw": m.group(0), "target": target, "alias": alias})

        return links

    @classmethod
    def diagnose_content_links(
        cls,
        body: str,
        theme_name: str,
        lang: str = "zh",
        sub_path: str = "docs/test.md",
        engine: Any = None
    ) -> List[Dict[str, Any]]:
        """
        针对指定主题与语种执行链接渲染仿真，并断言其合法性与有效性。
        """
        issues = []
        renderer_cls = SSGRegistry.get_renderer(theme_name)
        if not renderer_cls:
            if theme_name == "sovereign":
                from themes.sovereign.adapters.sovereign import SovereignSSGAdapter
                renderer_cls = SovereignSSGAdapter
            else:
                from core.adapters.egress.ssg.generic import GenericSSGAdapter
                renderer_cls = GenericSSGAdapter

        adapter = renderer_cls(engine=engine)
        rendered_body, _ = adapter.render(body, fm={}, target_lang=lang, sub_path=sub_path)

        # 提取渲染后生成的所有最终超链接
        extracted_rendered_urls = []
        for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', rendered_body):
            extracted_rendered_urls.append((m.group(1), m.group(2)))
        for m in re.finditer(r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', rendered_body):
            extracted_rendered_urls.append((m.group(2), m.group(1)))

        slug_map = get_doc_slug_map(engine) if engine else {}

        for alias, url in extracted_rendered_urls:
            clean_url = url.split('#')[0].strip()
            anchor = url.split('#')[1] if '#' in url else ''
            
            # 1. 检查是否存在残留未转译的双链语法
            if '[[' in url or ']]' in url:
                issues.append({
                    "theme": theme_name, "lang": lang, "alias": alias, "url": url,
                    "level": "CRITICAL", "message": "残留未解析的 Obsidian 双链语法",
                    "friendly_title": "残留未解析的 Obsidian 双链语法",
                    "friendly_cause": f"超链接 \"{alias}\" 中仍包含 [[...]] 语法符号，发布后访客将看到原始代码而非可点击链接。",
                    "friendly_suggestion": "请检查原稿中该处双链是否书写规范，或是否包含未闭合的双括号 ]]。"
                })

            # 2. Nextra 特异性规则断言
            if theme_name == "nextra":
                # Nextra 所有文档平铺在 pages 根目录，严禁带有 docs/ 虚假目录前缀
                if clean_url.startswith(('./docs/', '/docs/', 'docs/')):
                    issues.append({
                        "theme": theme_name, "lang": lang, "alias": alias, "url": url,
                        "level": "ERROR", "message": "Nextra 页面链接包含虚假的 docs/ 目录前缀，将导致 404",
                        "friendly_title": "页面链接包含多余的 docs/ 路径前缀",
                        "friendly_cause": "Nextra 采用扁平根目录路由，若携带 docs/ 前缀会导致访客点击后跳转 404 页面丢失。",
                        "friendly_suggestion": "建议将原稿中的 ./docs/xxx 相对路径简化为 ./xxx.md，或依赖系统的根目录自愈规则处理。"
                    })

            # 3. Starlight 特异性规则断言
            if theme_name == "starlight":
                # Starlight Clean URL 严禁出现重复语言前缀 (如 /ja/ja/)
                if lang and lang != "zh" and f"/{lang}/{lang}/" in clean_url:
                    issues.append({
                        "theme": theme_name, "lang": lang, "alias": alias, "url": url,
                        "level": "ERROR", "message": f"Starlight 链接出现重复语言前缀: /{lang}/{lang}/",
                        "friendly_title": "多语言跳转路径重复叠加",
                        "friendly_cause": f"链接路径中出现了 /{lang}/{lang}/ 双重语种前缀，导致链接解析失败。",
                        "friendly_suggestion": "请确保链接规范化引擎在 Clean URL 模式下的语种剥离守卫已生效。"
                    })
                # 非默认语言必须具备该语种的前缀
                if lang in ("en", "ja") and not clean_url.startswith(f"/{lang}/") and not clean_url.startswith("http"):
                    issues.append({
                        "theme": theme_name, "lang": lang, "alias": alias, "url": url,
                        "level": "WARNING", "message": f"Starlight 多语言页面 ({lang}) 的内链丢失了 /{lang}/ 前缀",
                        "friendly_title": "多语言页面内链缺少语种前缀",
                        "friendly_cause": f"在 {lang.upper()} 外语页面中，点击此内链可能会跳回默认中文版页面。",
                        "friendly_suggestion": "建议在「翻译规则」中确保「站内链接自动对齐目标语言」为开启状态。"
                    })

            # 4. 目标 Slug 存在性基础校验
            target_slug = os.path.splitext(os.path.basename(clean_url.rstrip('/')))[0].lower()
            if slug_map and target_slug not in ('', 'index'):
                found = (target_slug in slug_map) or any(v.get('slug') == target_slug for v in slug_map.values())
                if not found and not clean_url.startswith(('http://', 'https://', '/')):
                    issues.append({
                        "theme": theme_name, "lang": lang, "alias": alias, "url": url,
                        "level": "WARNING", "message": f"链接目标 slug '{target_slug}' 未在文库映射账本中登记",
                        "friendly_title": "引用了未在文库中找到的目标稿件",
                        "friendly_cause": f"文档中引用的目标 \"{target_slug}\" 在当前文库中没有匹配的 Markdown 文件。",
                        "friendly_suggestion": "请检查被引用的文稿名称是否发生变更，或在原稿中更新链接为最新文件名。"
                    })

        return issues

    @classmethod
    def run_full_vault_audit(cls, vault_dir: str, engine: Any = None) -> Dict[str, Any]:
        """对文库内所有原稿执行五大主流 SSG 全语种全息扫描"""
        total_files = 0
        total_links = 0
        report = {"total_files": 0, "total_links": 0, "issues": [], "passed": True}

        if not os.path.exists(vault_dir):
            return report

        for root, dirs, files in os.walk(vault_dir):
            # 🛡️ 过滤隐藏目录（例如 .plenipes, .obsidian, .git 等），仅遍历文库原稿
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.endswith('.md'):
                    total_files += 1
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    except Exception:
                        continue

                    raw_links = cls.extract_links_from_markdown(content)
                    total_links += len(raw_links)
                    if not raw_links:
                        continue

                    rel_sub = os.path.relpath(file_path, vault_dir)
                    for theme in cls.THEMES:
                        for lang in cls.LOCALES:
                            sub_issues = cls.diagnose_content_links(
                                content, theme_name=theme, lang=lang, sub_path=rel_sub, engine=engine
                            )
                            for iss in sub_issues:
                                iss["file"] = rel_sub
                                report["issues"].append(iss)

        report["total_files"] = total_files
        report["total_links"] = total_links
        criticals = [i for i in report["issues"] if i["level"] in ("ERROR", "CRITICAL")]
        report["passed"] = (len(criticals) == 0)
        return report
