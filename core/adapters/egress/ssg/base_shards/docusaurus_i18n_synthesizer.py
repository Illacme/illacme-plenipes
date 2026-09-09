#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Docusaurus i18n Synthesizer Shard
模块职责：为 Docusaurus 静态站点全自动水合与合成多语言导航菜单与国际化主题字典。
🛡️ [SOP-02 模块拆分 / SOP-13 母本物理隔离]
"""
import os
import json
from typing import Dict, Any


class DocusaurusI18nSynthesizer:
    """🚀 Docusaurus 多语言全景导航与界面字典合成器"""

    @classmethod
    def synthesize(cls, theme_dir: str, options: Dict[str, Any]) -> bool:
        """为 Docusaurus 派生主题目录自动生成 i18n/{locale}/docusaurus-theme-classic/navbar.json"""
        if not theme_dir or not os.path.exists(theme_dir):
            return False

        # 🛡️ SOP-13: 严禁污染 themes/ 只读母本目录，仅对品牌版图或派生目录执行落盘
        norm_dir = os.path.abspath(theme_dir)
        mother_prefix = os.path.abspath(os.path.join(os.getcwd(), "themes"))
        if norm_dir == mother_prefix or (norm_dir.startswith(mother_prefix + os.sep) and "imprints" not in norm_dir):
            return False

        i18n_conf = options.get("i18n", {})
        locales = i18n_conf.get("locales", []) if isinstance(i18n_conf, dict) else []
        navbar_items_i18n = options.get("navbar_items_i18n", {})
        if not locales:
            locales = list(navbar_items_i18n.keys()) if isinstance(navbar_items_i18n, dict) else []
        if not locales:
            i18n_dir = os.path.join(theme_dir, "i18n")
            if os.path.exists(i18n_dir):
                locales = [d for d in os.listdir(i18n_dir) if os.path.isdir(os.path.join(i18n_dir, d))]

        # 🛡️ 无论 navbar_items 是否存在，始终执行 showcase 展厅页面自愈与多语言同步
        cls._heal_showcase_pages(theme_dir, locales)

        navbar_items = options.get("navbar_items", [])
        if not isinstance(navbar_items, list) or not navbar_items:
            return True

        site_name = options.get("site_name", "Illacme Press")

        for loc in locales:
            if not isinstance(loc, str) or not loc.strip():
                continue

            loc_key = loc.strip()
            loc_items = None
            if isinstance(navbar_items_i18n, dict):
                loc_items = navbar_items_i18n.get(loc_key)
                if not loc_items and "-" in loc_key:
                    short_key = loc_key.split("-")[0]
                    loc_items = navbar_items_i18n.get(short_key)
                if not loc_items:
                    loc_items = navbar_items_i18n.get(loc_key.lower())

            if not isinstance(loc_items, list):
                continue

            nav_dict: Dict[str, Dict[str, str]] = {
                "title": {
                    "message": site_name,
                    "description": "The title in the navbar"
                },
                "logo.alt": {
                    "message": "Plenipis",
                    "description": "The alt text of navbar logo"
                }
            }

            for idx, def_item in enumerate(navbar_items):
                if not isinstance(def_item, dict):
                    continue
                orig_label = def_item.get("label", "").strip()
                if not orig_label:
                    continue

                trans_label = ""
                if idx < len(loc_items) and isinstance(loc_items[idx], dict):
                    c_item = loc_items[idx]
                    trans_label = c_item.get("label") or c_item.get("raw_label") or ""

                if not trans_label:
                    def_slot = def_item.get("target_slot") or def_item.get("slot")
                    if def_slot:
                        for c_item in loc_items:
                            if isinstance(c_item, dict) and (c_item.get("target_slot") == def_slot or c_item.get("slot") == def_slot):
                                trans_label = c_item.get("label") or c_item.get("raw_label") or ""
                                break

                if not trans_label:
                    trans_label = orig_label

                key = f"item.label.{orig_label}"
                nav_dict[key] = {
                    "message": trans_label,
                    "description": f"Navbar item with label {orig_label}"
                }

            target_file = os.path.join(theme_dir, "i18n", loc_key, "docusaurus-theme-classic", "navbar.json")
            try:
                os.makedirs(os.path.dirname(target_file), exist_ok=True)
                if os.path.exists(target_file):
                    try:
                        with open(target_file, "r", encoding="utf-8") as rf:
                            existing = json.load(rf)
                            if isinstance(existing, dict):
                                existing.update(nav_dict)
                                nav_dict = existing
                    except Exception:
                        pass
                with open(target_file, "w", encoding="utf-8") as wf:
                    json.dump(nav_dict, wf, indent=2, ensure_ascii=False)
            except Exception:
                pass

        # 🛡️ 自愈多语言 showcase 页面物理落盘与 JSX 清洗
        cls._heal_showcase_pages(theme_dir, locales)
        # 🛡️ 自愈 Markdown 内部相对路径与跨插件绝对路由映射 (构建 0 断链)
        cls._heal_internal_links(theme_dir)

        return True

    @classmethod
    def _heal_showcase_pages(cls, theme_dir: str, locales: list):
        """🚀 [V50.3] 自愈与同步 Showcase 展厅页面至 Docusaurus Pages 插件多语言物理槽位"""
        import re
        import yaml

        def _clean_mdx(content: str, is_index: bool, stem: str, loc_prefix: str = "") -> str:
            # 1. 注释转 JSX
            healed = re.sub(r'<!--(.*?)-->', r'{/*\1*/}', content, flags=re.DOTALL)
            # 2. 内联 style 转 JSX
            def _style_to_jsx(m):
                raw = m.group(1).strip()
                pairs = [p.strip() for p in raw.split(';') if ':' in p]
                props = []
                for p in pairs:
                    k, v = p.split(':', 1)
                    k, v = k.strip(), v.strip().replace("'", "\\'")
                    parts = k.split('-')
                    camel_k = parts[0] + ''.join(x.capitalize() for x in parts[1:])
                    props.append(f"{camel_k}: '{v}'")
                return f"style={{{{{', '.join(props)}}}}}"
            healed = re.sub(r'style="([^"]*)"', _style_to_jsx, healed)
            healed = re.sub(r"style='([^']*)'", _style_to_jsx, healed)
            # 3. 转义非 JSX 占位符 (例如 {lang} -> {'{lang}'})
            healed = healed.replace("{lang}", "{'{lang}'}")

            # 4. 规范化多行 p 标签，消除 HTML 压缩告警
            healed = re.sub(r'<p>\s+([^<]+?)\s+</p>', r'<p>\1</p>', healed)

            # 5. 🛡️ 注入带有当前语种前缀的绝对展示橱窗路径，彻底杜绝相对路径丢失 /showcase/ 前缀
            showcase_base = f"{loc_prefix}/showcase" if loc_prefix else "/showcase"
            def _replace_card_href(m):
                target = m.group(1).strip()
                clean_target = os.path.splitext(target)[0].lstrip('./')
                return f'href="{showcase_base}/{clean_target}"'
            healed = re.sub(r'href="\./([^"]+?)"', _replace_card_href, healed)

            # 6. 规范化 frontmatter slug
            if healed.startswith("---"):
                parts = healed.split("---", 2)
                if len(parts) >= 3:
                    try:
                        fm = yaml.safe_load(parts[1]) or {}
                        fm['slug'] = '/showcase' if is_index else f"/showcase/{stem}"
                        fm_str = yaml.dump(fm, allow_unicode=True, sort_keys=False).strip()
                        healed = f"---\n{fm_str}\n---{parts[2]}"
                    except Exception:
                        pass
            return healed

        def _sync_dir(src_d: str, dest_d: str, loc_prefix: str = ""):
            if not os.path.exists(src_d):
                return
            os.makedirs(dest_d, exist_ok=True)
            for fname in os.listdir(src_d):
                if not fname.endswith(".md"):
                    continue
                src_fp = os.path.join(src_d, fname)
                dest_fp = os.path.join(dest_d, fname)
                try:
                    with open(src_fp, "r", encoding="utf-8") as rf:
                        content = rf.read()
                    stem = os.path.splitext(fname)[0]
                    is_idx = (stem == "index")
                    cleaned = _clean_mdx(content, is_idx, stem, loc_prefix=loc_prefix)
                    with open(dest_fp, "w", encoding="utf-8") as wf:
                        wf.write(cleaned)
                except Exception:
                    pass

        # 1. 默认语言同步: showcase -> src/pages/showcase (loc_prefix="")
        root_showcase = os.path.join(theme_dir, "showcase")
        dest_default = os.path.join(theme_dir, "src", "pages", "showcase")
        _sync_dir(root_showcase, dest_default, loc_prefix="")

        # 2. 多语言同步: {loc}/showcase -> i18n/{loc}/docusaurus-plugin-content-pages/showcase
        for loc in locales:
            if not isinstance(loc, str) or not loc.strip():
                continue
            loc_clean = loc.strip()
            loc_prefix = f"/{loc_clean}" if loc_clean != "zh-Hans" and not loc_clean.startswith("zh") else ""
            # 兼容 ja / ja-JP / en 等各种别名目录
            for candidate in [loc_clean, loc_clean.split("-")[0], loc_clean.lower()]:
                src_loc_d = os.path.join(theme_dir, candidate, "showcase")
                if os.path.exists(src_loc_d):
                    dest_loc_d = os.path.join(theme_dir, "i18n", loc_clean, "docusaurus-plugin-content-pages", "showcase")
                    _sync_dir(src_loc_d, dest_loc_d, loc_prefix=loc_prefix)
                    break

    @classmethod
    def _heal_internal_links(cls, theme_dir: str):
        """🚀 [V108.0] 自愈 Docusaurus 跨插件与同插件内部 Markdown 链接，达到 0 Broken Links"""
        import re

        def _heal_file(filepath: str, is_docs_plugin: bool):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                orig = content
                if is_docs_plugin:
                    # 同一 docs 插件内寻址：消除 ../docs/ 或 ./docs/ 引起的跨目录寻址错误
                    content = re.sub(r'\]\(\.\./docs/([^\)]+?\.md)\)', r'](./\1)', content)
                    content = re.sub(r'\]\(\./docs/([^\)]+?\.md)\)', r'](./\1)', content)
                else:
                    # 跨插件（pages 或 blog）寻址：转写为 Docusaurus 官方要求的绝对路由
                    content = re.sub(r'\]\(\.\./docs/([^\)]+?)\.md\)', r'](/docs/\1)', content)
                    content = re.sub(r'\]\(\./docs/([^\)]+?)\.md\)', r'](/docs/\1)', content)
                    content = re.sub(r'\]\(\.\./blog/([^\)]+?)\.md\)', r'](/blog/\1)', content)
                    content = re.sub(r'\]\(\.\./about\.md\)', r'](/about)', content)
                    content = re.sub(r'\[WikiLinks\]\(\./wikilinks\.md\)', r'**WikiLinks**', content)
                if content != orig:
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
            except Exception:
                pass

        # 1. 扫描 docs 插件目录 (docs/ 与 i18n/*/docusaurus-plugin-content-docs/current/)
        docs_dirs = [os.path.join(theme_dir, "docs")]
        i18n_root = os.path.join(theme_dir, "i18n")
        if os.path.exists(i18n_root):
            for loc in os.listdir(i18n_root):
                dp = os.path.join(i18n_root, loc, "docusaurus-plugin-content-docs", "current")
                if os.path.exists(dp):
                    docs_dirs.append(dp)

        for d in docs_dirs:
            if os.path.exists(d):
                for root, _, files in os.walk(d):
                    for fn in files:
                        if fn.endswith(".md"):
                            _heal_file(os.path.join(root, fn), is_docs_plugin=True)

        # 2. 扫描跨插件目录 (src/pages/, blog/, i18n/*/docusaurus-plugin-content-pages/, i18n/*/blog/)
        cross_dirs = [
            os.path.join(theme_dir, "src", "pages"),
            os.path.join(theme_dir, "blog"),
        ]
        if os.path.exists(i18n_root):
            for loc in os.listdir(i18n_root):
                for sub in ("docusaurus-plugin-content-pages", "docusaurus-plugin-content-blog"):
                    cp = os.path.join(i18n_root, loc, sub)
                    if os.path.exists(cp):
                        cross_dirs.append(cp)

        for d in cross_dirs:
            if os.path.exists(d):
                for root, _, files in os.walk(d):
                    for fn in files:
                        if fn.endswith(".md"):
                            _heal_file(os.path.join(root, fn), is_docs_plugin=False)


