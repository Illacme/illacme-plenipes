# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Nextra Meta Synthesizer Shard
模块职责：为 Nextra 知识库主题全自动合成 _meta.json 与 meta.json 侧边栏导航树。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
"""
import os
import re
import json
from typing import Dict, Any, List


class NextraMetaSynthesizer:
    """🚀 Nextra 侧边栏全景元数据合成器"""

    # 推荐的文档体系核心排序权重
    DEFAULT_WEIGHT_ORDER = [
        "index", "quick-start", "authoring-and-vault-guide", "brand-management",
        "governance-dashboard-operation-guide", "dashboard-guide", "architecture",
        "compute-center-ai-translation-setup-guide", "compute-and-ai", "i18n-guide",
        "themes-and-binding-visual-customization", "themes-and-binding",
        "matrix-channel-configuration", "distribution-channels",
        "common-issues-and-troubleshooting-manual-faq", "faq", "about"
    ]

    SLOT_LABEL_MAP = {
        "zh": {
            "blog": {"title": "📰 官方博客", "type": "menu"}, "showcase": {"title": "🎨 产品展示", "type": "menu"},
            "engineering": {"title": "🛠️ 工程架构", "type": "menu"}, "advanced": {"title": "⚡ 高级特性", "type": "menu"},
            "features": {"title": "✨ 核心特性", "type": "menu"}, "themes": {"title": "🎭 装帧主题", "type": "menu"},
        },
        "en": {
            "blog": {"title": "📰 Official Blog", "type": "menu"}, "showcase": {"title": "🎨 Showcase", "type": "menu"},
            "engineering": {"title": "🛠️ Engineering", "type": "menu"}, "advanced": {"title": "⚡ Advanced", "type": "menu"},
            "features": {"title": "✨ Features", "type": "menu"}, "themes": {"title": "🎭 Themes", "type": "menu"},
        },
        "ja": {
            "blog": {"title": "📰 公式ブログ", "type": "menu"}, "showcase": {"title": "🎨 ショーケース", "type": "menu"},
            "engineering": {"title": "🛠️ エンジニアリング", "type": "menu"}, "advanced": {"title": "⚡ 高度な機能", "type": "menu"},
            "features": {"title": "✨ コア機能", "type": "menu"}, "themes": {"title": "🎭 テーマ", "type": "menu"},
        },
    }

    @classmethod
    def synthesize(cls, theme_dir: str, engine: Any = None) -> bool:
        """为指定的 Nextra 主题目录动态合成多语言 _meta.{lang}.json 导航映射"""
        if not theme_dir or not os.path.exists(theme_dir):
            return False

        pages_dir = os.path.join(theme_dir, "pages")
        if not os.path.exists(pages_dir):
            return False

        # 1. 提取支持的语言矩阵与默认语言
        locales = ["zh", "en", "ja"]
        default_locale = "zh"
        theme_opt_file = os.path.join(theme_dir, "theme.options.json")
        if os.path.exists(theme_opt_file):
            try:
                with open(theme_opt_file, "r", encoding="utf-8") as f:
                    opt_data = json.load(f)
                    if opt_data.get("i18n") and isinstance(opt_data["i18n"], list):
                        parsed_locs = [item.get("locale") for item in opt_data["i18n"] if item.get("locale") and item.get("locale") != "auto"]
                        if parsed_locs:
                            locales = parsed_locs
                    if opt_data.get("defaultLocale") and opt_data["defaultLocale"] != "auto":
                        default_locale = opt_data["defaultLocale"]
            except Exception:
                pass

        # 2. 自动收敛旧版孤儿语言子目录 (平铺 pages/en/ 与 pages/ja/ 至同级)
        for loc in ("en", "ja", "ko", "fr", "de", "es", "ru"):
            loc_dir = os.path.join(pages_dir, loc)
            if os.path.exists(loc_dir) and os.path.isdir(loc_dir):
                cls._flatten_legacy_directory(loc_dir, pages_dir, loc)

        # 3. 清理 Duplicate page 冲突源 (官方 demo index.mdx)
        idx_mdx = os.path.join(pages_dir, "index.mdx")
        if os.path.exists(idx_mdx) and os.path.exists(os.path.join(pages_dir, "index.md")):
            try: os.remove(idx_mdx)
            except Exception: pass

        # 4. 全局递归为所有目录水合多语言真实译文副本与落地页索引，杜绝 Nextra 页面 404 与内容中文残留
        from .nextra_content_hydrator import NextraContentHydrator
        NextraContentHydrator.hydrate_pages_directory(pages_dir, locales, default_locale, engine=engine)

        # 5. 提取文档快照元数据并递归合成多语言 _meta.{lang}.json
        doc_meta_map = cls._extract_doc_meta(engine)
        cls._synthesize_directory_i18n(pages_dir, doc_meta_map, locales, default_locale, is_root=True, theme_dir=theme_dir)
        return True

    @classmethod
    def _flatten_legacy_directory(cls, loc_dir: str, pages_dir: str, loc: str):
        """递归平铺孤儿语言子目录内的文件至同级后缀，并物理清除子目录"""
        import shutil
        for root, _, files in os.walk(loc_dir):
            rel = os.path.relpath(root, loc_dir)
            target_sub = pages_dir if rel == "." else os.path.join(pages_dir, rel)
            os.makedirs(target_sub, exist_ok=True)
            for f in files:
                if f.endswith((".md", ".mdx")):
                    base, ext = os.path.splitext(f)
                    name = f if base.endswith(f".{loc}") else f"{base}.{loc}{ext}"
                    dest = os.path.join(target_sub, name)
                    if not os.path.exists(dest):
                        try:
                            shutil.copy2(os.path.join(root, f), dest)
                        except Exception:
                            pass
        try:
            shutil.rmtree(loc_dir, ignore_errors=True)
        except Exception:
            pass

    @classmethod
    def _extract_nav_config(cls, theme_dir: str, engine: Any = None) -> Dict[str, Any]:
        """从 theme.options.json 提取全量多语言导航配置 (真理源源自治理中心 route_matrix)"""
        opt_p = os.path.join(theme_dir, "theme.options.json")
        if os.path.exists(opt_p):
            try:
                with open(opt_p, "r", encoding="utf-8") as f:
                    opt = json.load(f)
                return {
                    "nav_links": opt.get("nav_links", []),
                    "nav_links_i18n": opt.get("nav_links_i18n", {})
                }
            except Exception:
                pass
        return {"nav_links": [], "nav_links_i18n": {}}

    @classmethod
    def _synthesize_directory_i18n(cls, dir_path: str, doc_meta_map: Dict[str, Any], locales: List[str], default_locale: str, is_root: bool = False, theme_dir: str = ""):
        """扫描单个目录并为每个语言独立生成 _meta.{lang}.json"""
        if not os.path.exists(dir_path):
            return

        base_slugs = []
        dir_slugs = []
        known_locales = ("en", "ja", "zh", "ko", "fr", "de", "es", "ru")

        for item in sorted(os.listdir(dir_path)):
            if item.startswith((".", "_")) or item.endswith(".json") or item == "node_modules":
                continue
            full_path = os.path.join(dir_path, item)
            if os.path.isdir(full_path):
                if item not in known_locales:
                    dir_slugs.append(item)
            elif item.endswith((".md", ".mdx")):
                raw_slug = os.path.splitext(item)[0]
                pure_slug = re.sub(r'\.(?:[a-z]{2}(?:-[A-Z]{2})?)$', '', raw_slug)
                if pure_slug not in base_slugs:
                    base_slugs.append(pure_slug)

        def _get_sort_key(s: str) -> tuple:
            s_low = s.lower()
            return (0, cls.DEFAULT_WEIGHT_ORDER.index(s_low)) if s_low in cls.DEFAULT_WEIGHT_ORDER else (1, s_low)

        base_slugs.sort(key=_get_sort_key)
        dir_slugs.sort(key=lambda s: (0 if s in ("blog", "showcase", "features") else 1, s.lower()))

        # 递归为各子目录执行多语言合成并确保落地页
        for d_slug in list(dir_slugs):
            sub_dir = os.path.join(dir_path, d_slug)
            # 自愈同名嵌套子目录 (如 engineering/engineering/)
            nested_sub = os.path.join(sub_dir, d_slug)
            if os.path.exists(nested_sub) and os.path.isdir(nested_sub):
                import shutil
                for nf in os.listdir(nested_sub):
                    n_src = os.path.join(nested_sub, nf)
                    n_dst = os.path.join(sub_dir, nf)
                    if not os.path.exists(n_dst):
                        try:
                            shutil.move(n_src, n_dst)
                        except Exception:
                            pass
                try:
                    shutil.rmtree(nested_sub, ignore_errors=True)
                except Exception:
                    pass

            cls._synthesize_directory_i18n(sub_dir, doc_meta_map, locales, default_locale, is_root=False, theme_dir=theme_dir)

        # 提取治理中心多语言导航配置 (仅在根目录用于 Navbar 映射)
        nav_info = cls._extract_nav_config(theme_dir or os.path.dirname(dir_path)) if is_root else {}
        nav_links_def = nav_info.get("nav_links", [])
        nav_links_i18n = nav_info.get("nav_links_i18n", {})

        # 为每个语言独立合成 _meta.{lang}.json
        for lang in locales:
            entries: Dict[str, Any] = {}
            active_nav = nav_links_i18n.get(lang) or nav_links_def

            # 整理当前语言下的 Navbar 映射表 (仅 show_in_nav 为 true 的项)
            nav_page_map = {}
            ext_nav_items = []
            if is_root and active_nav:
                for item in active_nav:
                    raw_url = str(item.get("url", "")).strip()
                    title = item.get("text") or item.get("raw_text") or ""
                    slot = item.get("slot", "")
                    if item.get("external") or raw_url.startswith("http"):
                        ext_nav_items.append({
                            "title": title,
                            "href": raw_url,
                            "newWindow": True
                        })
                    else:
                        clean_seg = raw_url.strip("/").split("/")[-1]
                        if clean_seg:
                            nav_page_map[clean_seg.lower()] = title
                        if slot and slot not in ("docs", "external"):
                            nav_page_map[slot.lower()] = title

            for slug in base_slugs:
                title = cls._extract_title_for_lang(dir_path, slug, lang)
                if not title and slug.lower() in doc_meta_map:
                    title = doc_meta_map[slug.lower()].get("title")
                doc_title = title or slug.replace("-", " ").title()
                # 若创作者显式将单篇放入了导航栏 (如 about)
                if is_root and slug.lower() in nav_page_map:
                    entries[slug] = {"title": nav_page_map[slug.lower()], "type": "page"}
                else:
                    entries[slug] = doc_title

            slot_defs = cls.SLOT_LABEL_MAP.get(lang, cls.SLOT_LABEL_MAP["zh"])
            for d_slug in dir_slugs:
                fallback_title = slot_defs.get(d_slug, {}).get("title", d_slug.replace("-", " ").title())
                if is_root:
                    # 仅当创作者在治理中心 route_matrix 中启用了该频道导航，才赋予 type: page 占据 Navbar
                    if d_slug.lower() in nav_page_map:
                        entries[d_slug] = {"title": nav_page_map[d_slug.lower()], "type": "page"}
                    else:
                        entries[d_slug] = fallback_title
                else:
                    entries[d_slug] = fallback_title

            if is_root:
                # 注入外部导航项 (如 GitHub 仓库)
                for idx, ext in enumerate(ext_nav_items):
                    ext_key = "github" if "github" in ext["title"].lower() or "github" in ext["href"].lower() else f"ext_nav_{idx}"
                    entries[ext_key] = {
                        "title": ext["title"],
                        "type": "page",
                        "href": ext["href"],
                        "newWindow": True
                    }

                for loc in known_locales:
                    if loc not in entries:
                        entries[loc] = {"display": "hidden"}

            target_file = os.path.join(dir_path, f"_meta.{lang}.json")
            try:
                with open(target_file, "w", encoding="utf-8") as f: json.dump(entries, f, indent=2, ensure_ascii=False)
            except Exception: pass
            if lang == default_locale or lang == "zh":
                try:
                    with open(os.path.join(dir_path, "_meta.json"), "w", encoding="utf-8") as f: json.dump(entries, f, indent=2, ensure_ascii=False)
                except Exception: pass
        for legacy in ("meta.json", "meta.zh.json", "meta.en.json", "meta.ja.json"):
            legacy_p = os.path.join(dir_path, legacy)
            if os.path.exists(legacy_p):
                try: os.remove(legacy_p)
                except Exception: pass

    @classmethod
    def _extract_title_for_lang(cls, dir_path: str, slug: str, lang: str) -> str:
        """优先提取特定语种标题或映射字典，非中文环境下严防返回汉字"""
        try:
            from .ssg_slot_matrix import SLOT_DOC_FALLBACK
            if slug in SLOT_DOC_FALLBACK and lang in SLOT_DOC_FALLBACK[slug]:
                return SLOT_DOC_FALLBACK[slug][lang]
        except Exception: pass
        for p in (os.path.join(dir_path, f"{slug}.{lang}.md"), os.path.join(dir_path, f"{slug}.{lang}.mdx"),
                  os.path.join(dir_path, f"{slug}.md"), os.path.join(dir_path, f"{slug}.mdx")):
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        c = "".join([f.readline() for _ in range(30)])
                    m = re.search(r"^title:\s*[\"']?(.*?)[\"']?\s*$", c, re.M | re.I) or re.search(r"^#\s+(.*?)\s*$", c, re.M)
                    if m:
                        t = m.group(1).strip()
                        if lang == "zh" or not re.search(r'[\u4e00-\u9fa5]', t): return t
                except Exception: pass
        return slug.replace("-", " ").title() if lang != "zh" else ""

    @classmethod
    def _extract_doc_meta(cls, engine: Any = None) -> Dict[str, Any]:
        """从引擎元数据提取所有文档的映射"""
        try:
            from core.adapters.egress.ssg.generic_shards.navigation_builder import get_doc_slug_map
            return get_doc_slug_map(engine)
        except Exception: return {}
