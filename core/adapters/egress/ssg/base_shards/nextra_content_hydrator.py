# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Nextra Content Hydrator Shard
模块职责：为 Nextra 知识库主题执行全域多语言内容与落地页索引的深度水合。
彻底根治 Nextra 下英文/日文页面正文与索引残留中文的物理缺陷。
"""

import os
import re
from typing import List, Dict, Any, Optional

from core.utils.tracing import tlog
from .ssg_slot_matrix import SLOT_DOC_FALLBACK


class NextraContentHydrator:
    """🚀 Nextra 物理多语言 Markdown 内容全息水合器"""

    @classmethod
    def get_translation_search_roots(cls, engine: Any = None, pages_dir: str = "") -> List[str]:
        """确定所有可用的多语言译文检索真理源"""
        roots = []
        if engine and hasattr(engine, 'paths') and engine.paths:
            c_dir = engine.paths.get("cache")
            if c_dir and os.path.exists(c_dir):
                roots.append(c_dir)

        project_root = os.getcwd()
        runtime_cache = os.path.join(project_root, "vault", ".plenipes", "cache", "runtime")
        if os.path.exists(runtime_cache) and runtime_cache not in roots:
            roots.append(runtime_cache)

        if pages_dir:
            parts = pages_dir.replace("\\", "/").split("/")
            if "imprints" in parts:
                imp_idx = parts.index("imprints")
                if len(parts) > imp_idx + 2:
                    imp_brand = "/".join(parts[:imp_idx + 3])
                    starlight_docs = os.path.join(imp_brand, "themes", "starlight", "src", "content", "docs")
                    if os.path.exists(starlight_docs) and starlight_docs not in roots:
                        roots.append(starlight_docs)
                    universal_docs = os.path.join(imp_brand, "themes", "universal", "src", "content")
                    if os.path.exists(universal_docs) and universal_docs not in roots:
                        roots.append(universal_docs)
                    sovereign_docs = os.path.join(imp_brand, "themes", "sovereign", "src", "content")
                    if os.path.exists(sovereign_docs) and sovereign_docs not in roots:
                        roots.append(sovereign_docs)

        return roots

    @classmethod
    def find_translated_file(cls, search_roots: List[str], rel_dir: str, slug: str, lang: str, ext: str) -> Optional[str]:
        """在多语言真理源池中检索特定语言的真实翻译文件"""
        candidates = []
        if rel_dir and rel_dir != ".":
            candidates.append(os.path.join(lang, rel_dir, f"{slug}{ext}"))
            candidates.append(os.path.join(lang, f"{slug}{ext}"))
            candidates.append(os.path.join(rel_dir, f"{slug}.{lang}{ext}"))
        else:
            candidates.append(os.path.join(lang, f"{slug}{ext}"))
            candidates.append(f"{slug}.{lang}{ext}")

        for s_root in search_roots:
            for cand in candidates:
                cand_path = os.path.join(s_root, cand)
                if os.path.exists(cand_path) and os.path.isfile(cand_path):
                    try:
                        with open(cand_path, "r", encoding="utf-8", errors="ignore") as rf:
                            head = "".join([rf.readline() for _ in range(5)])
                        if "<!DOCTYPE html>" not in head:
                            return cand_path
                    except Exception:
                        pass
        return None

    @classmethod
    def hydrate_pages_directory(cls, pages_dir: str, locales: List[str], default_locale: str, engine: Any = None):
        """全域递归扫描 pages 目录并水合多语言物理实体文件"""
        if not os.path.exists(pages_dir) or not os.path.isdir(pages_dir):
            return

        search_roots = cls.get_translation_search_roots(engine, pages_dir)
        cls.ensure_directory_indexes(pages_dir, locales, default_locale)

        for root, _, files in os.walk(pages_dir):
            if any(p.startswith(".") or p == "node_modules" for p in root.split(os.sep)):
                continue
            rel_dir = os.path.relpath(root, pages_dir)

            for f in files:
                if not f.endswith((".md", ".mdx")) or f.startswith((".", "_", "index.")):
                    continue

                raw_slug, ext = os.path.splitext(f)
                if re.search(r'\.(?:[a-z]{2}(?:-[A-Z]{2})?)$', raw_slug):
                    continue

                for lang in locales:
                    loc_file = os.path.join(root, f"{raw_slug}.{lang}{ext}")
                    source_file = os.path.join(root, f)

                    if lang == default_locale or lang == "zh":
                        if not os.path.exists(loc_file):
                            try:
                                with open(source_file, "r", encoding="utf-8", errors="ignore") as rf:
                                    open(loc_file, "w", encoding="utf-8").write(rf.read())
                            except Exception:
                                pass
                        continue

                    trans_source = cls.find_translated_file(search_roots, rel_dir, raw_slug, lang, ext)
                    needs_update = True

                    if os.path.exists(loc_file):
                        try:
                            with open(loc_file, "r", encoding="utf-8", errors="ignore") as ef:
                                existing_content = ef.read(2048)
                            has_chinese = bool(re.search(r'[\u4e00-\u9fa5]', existing_content))
                            if not has_chinese and trans_source is None:
                                needs_update = False
                        except Exception:
                            needs_update = True

                    if not needs_update:
                        continue

                    if trans_source:
                        try:
                            with open(trans_source, "r", encoding="utf-8", errors="ignore") as tf:
                                trans_content = tf.read()
                            target_title = cls._extract_title_for_lang(root, raw_slug, lang)
                            if target_title:
                                trans_content = re.sub(r'^title:\s*.*$', f'title: "{target_title}"', trans_content, flags=re.M)
                            trans_content = cls._purify_content_for_lang(trans_content, lang)
                            with open(loc_file, "w", encoding="utf-8") as wf:
                                wf.write(trans_content)
                            tlog.debug(f"🌐 [Nextra 水合] 成功为 {rel_dir}/{raw_slug} 注入 {lang} 真实译文")
                        except Exception as e:
                            tlog.warning(f"⚠️ [Nextra 水合异常] {e}")
                    else:
                        try:
                            with open(source_file, "r", encoding="utf-8", errors="ignore") as sf:
                                raw_c = sf.read()
                            target_title = cls._extract_title_for_lang(root, raw_slug, lang) or raw_slug.replace("-", " ").title()
                            raw_c = re.sub(r'^title:\s*.*$', f'title: "{target_title}"', raw_c, flags=re.M)
                            raw_c = re.sub(r'^#\s+.*$', f'# {target_title}', raw_c, flags=re.M)
                            notice = "> [!NOTE]\n> *English version is being synchronized. Showing content overview.*" if lang == "en" else "> [!NOTE]\n> *翻訳版を同期中です。概要を表示しています。*"
                            raw_c = f"{raw_c}\n\n{notice}\n"
                            with open(loc_file, "w", encoding="utf-8") as wf:
                                wf.write(raw_c)
                        except Exception:
                            pass

    @classmethod
    def ensure_directory_indexes(cls, pages_dir: str, locales: List[str], default_locale: str):
        """为所有专区子目录全自动合成/刷新多语言 landing index.{lang}.md"""
        if not os.path.exists(pages_dir) or not os.path.isdir(pages_dir):
            return

        from .nextra_meta_synthesizer import NextraMetaSynthesizer
        slot_map = NextraMetaSynthesizer.SLOT_LABEL_MAP

        for item in sorted(os.listdir(pages_dir)):
            sub_dir = os.path.join(pages_dir, item)
            if not os.path.isdir(sub_dir) or item.startswith((".", "_")) or item in ("node_modules", "public"):
                continue

            sub_docs = []
            for f in sorted(os.listdir(sub_dir)):
                if f.endswith((".md", ".mdx")) and not f.startswith((".", "_", "index.")):
                    pure = re.sub(r'\.(?:[a-z]{2}(?:-[A-Z]{2})?)$', '', os.path.splitext(f)[0])
                    if pure not in sub_docs:
                        sub_docs.append(pure)

            for lang in locales:
                title = slot_map.get(lang, slot_map["zh"]).get(item, {}).get("title", item.replace("-", " ").title())
                lines = ["---", f'title: "{title}"', "---", "", f"# {title}", ""]
                intro = "欢迎浏览本专栏内容与文档索引：\n" if lang in ("zh", "zh-CN", "zh-Hans") else (
                    "本セクションのドキュメント一覧：\n" if lang == "ja" else "Welcome to this section's documentation and guides:\n"
                )
                lines.append(intro)
                for s in sub_docs:
                    doc_title = cls._extract_title_for_lang(sub_dir, s, lang) or s.replace("-", " ").title()
                    lines.append(f"- **[{doc_title}](/{item}/{s})**")

                content = "\n".join(lines) + "\n"

                loc_file = os.path.join(sub_dir, f"index.{lang}.md")
                try:
                    open(loc_file, "w", encoding="utf-8").write(content)
                except Exception:
                    pass
                if lang == default_locale or lang == "zh":
                    try:
                        open(os.path.join(sub_dir, "index.md"), "w", encoding="utf-8").write(content)
                    except Exception:
                        pass

                root_loc = os.path.join(pages_dir, f"{item}.{lang}.md")
                try:
                    open(root_loc, "w", encoding="utf-8").write(content)
                except Exception:
                    pass
                if lang == default_locale or lang == "zh":
                    try:
                        open(os.path.join(pages_dir, f"{item}.md"), "w", encoding="utf-8").write(content)
                    except Exception:
                        pass

    @classmethod
    def _extract_title_for_lang(cls, dir_path: str, slug: str, lang: str) -> str:
        """优先提取多语言对照字典，严格防御在非中文环境下返回中文字符"""
        if slug in SLOT_DOC_FALLBACK and lang in SLOT_DOC_FALLBACK[slug]:
            return SLOT_DOC_FALLBACK[slug][lang]

        for cand_name in (f"{slug}.{lang}.md", f"{slug}.{lang}.mdx", f"{slug}.md", f"{slug}.mdx"):
            p = os.path.join(dir_path, cand_name)
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        c = "".join([f.readline() for _ in range(30)])
                    m = re.search(r"^title:\s*[\"']?(.*?)[\"']?\s*$", c, re.M | re.I) or re.search(r"^#\s+(.*?)\s*$", c, re.M)
                    if m:
                        t = m.group(1).strip()
                        if lang in ("zh", "zh-CN", "zh-Hans") or not re.search(r'[\u4e00-\u9fa5]', t):
                            return t
                except Exception:
                    pass
        return slug.replace("-", " ").title() if lang not in ("zh", "zh-CN", "zh-Hans") else ""

    @classmethod
    def _purify_content_for_lang(cls, content: str, lang: str) -> str:
        """针对非中文语种执行典型中文段落与图表节点的语言纯净化，并自愈相对文档链接"""
        if not content:
            return content

        # 🛡️ [Nextra 根文档槽位链接自愈] 剥离由于通用 docs 频道名产生的虚假 docs/ 路径前缀
        content = re.sub(r'\]\(\s*(?:\.\./|\./|/)docs/([^)]+)\)', r'](./\1)', content)

        # 🛡️ [Nextra Layout 契约自愈] Nextra 仅支持 default/full/raw，将文档型 docs 自愈为 default 激活 TOC
        content = re.sub(r'^layout:\s*docs\s*$', 'layout: default', content, flags=re.M)

        if lang in ("zh", "zh-CN", "zh-Hans"):
            return content

        if lang == "ja":
            # 1. 替换典型 Callout 中文提示语
            c_tip_zh = "原稿零污染，彻底消除所有静态框架语法断层"
            c_tip_zh_2 = "原稿零污染，抹平所有静态框架语法断层"
            ja_tip_repl = (
                "**原稿零汚染、すべての静的フレームワーク構文断層を解消**："
                "Obsidian、Docusaurus、VitePress、Astro、Hugo はそれぞれ互換性のない Markdown 方言拡張を持っています。"
                "Illacme Plenipes はエンタープライズ級の AST 抽象構文木変換パイプラインを内蔵し、メモリ上で構文断層を動的に解消。"
                "原稿リポジトリのコードを 1 行も変更することなく、8 大フレームワークで完璧に表示できます！"
            )
            content = re.sub(rf'\*\*(?:{c_tip_zh}|{c_tip_zh_2})\*\*.*?(?=\n\n|\n---|---)', ja_tip_repl, content, flags=re.S)

            # 2. 替换 Mermaid 流程图中的中文节点
            ja_node_map = {
                "创作者原稿 Markdown": "原稿 Markdown",
                "AST 词法与语法分析器": "AST 構文解析器",
                "Obsidian Callouts 提示块": "Obsidian Callouts",
                "Mermaid 动态拓扑图表": "Mermaid ダイアグラム",
                "MathJax / KaTeX LaTeX 公式": "MathJax / KaTeX 数式",
                "双向链接 WikiLinks 与嵌入附件": "双方向リンク WikiLinks",
                "AST 跨框架语义转换中枢": "AST 変換ハブ",
                "Sovereign 原生 HTML5 / CSS3": "Sovereign 原生 HTML5 / CSS3",
                "Docusaurus MDX 2 组件": "Docusaurus MDX 2 コンポーネント",
                "VitePress Vue 3 容器": "VitePress Vue 3 コンテナ",
                "Astro Starlight 静态孤岛": "Astro Starlight アイランド"
            }
            for zh_k, ja_v in ja_node_map.items():
                content = content.replace(zh_k, ja_v)

        elif lang == "en":
            # 替换 Mermaid 流程图中的中文节点
            en_node_map = {
                "创作者原稿 Markdown": "Creator Raw Markdown",
                "AST 词法与语法分析器": "AST Lexer & Parser",
                "Obsidian Callouts 提示块": "Obsidian Callouts",
                "Mermaid 动态拓扑图表": "Mermaid Dynamic Diagrams",
                "MathJax / KaTeX LaTeX 公式": "MathJax / KaTeX Formulas",
                "双向链接 WikiLinks 与嵌入附件": "WikiLinks & Attachments",
                "AST 跨框架语义转换中枢": "AST Semantic Bridging Hub",
                "Sovereign 原生 HTML5 / CSS3": "Sovereign Native HTML5 / CSS3",
                "Docusaurus MDX 2 组件": "Docusaurus MDX 2 Components",
                "VitePress Vue 3 容器": "VitePress Vue 3 Containers",
                "Astro Starlight 静态孤岛": "Astro Starlight Static Islands"
            }
            for zh_k, en_v in en_node_map.items():
                content = content.replace(zh_k, en_v)

        return content
