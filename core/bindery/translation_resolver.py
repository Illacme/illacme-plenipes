# -*- coding: utf-8 -*-
"""
🌍 [V125.3] Translation Resolver for Digital Book Bindery
职责：为数字装订中枢提供多语种已译手稿物理寻址、标题解析与正文提取服务。
规范：遵循 SOP-01 单文件 ≤ 300 行红线，物理查找优先纯 Markdown，彻底消灭未译降级回退母语体验割裂。
"""

import os
import re
import sqlite3
import json
import yaml
from typing import Tuple, Optional, Dict


class TranslationResolver:
    """多语种手稿物理寻址与正文提取中枢"""

    _path_cache: Dict[str, Dict[str, str]] = {}
    _stem_cache: Dict[str, Dict[str, str]] = {}

    @classmethod
    def reset_cache(cls):
        """重置缓存（主要用于测试隔离）"""
        cls._path_cache.clear()
        cls._stem_cache.clear()

    @classmethod
    def warm_up(cls, target_lang: str, base_dir: str = "imprints"):
        """预热并建立目标语种物理 Markdown 文件的全相对路径与无歧义 stem 索引"""
        t_lang = (target_lang or "").strip().lower()
        if t_lang in ("zh", "zh-hans", "zh-cn", ""):
            return

        if t_lang in cls._path_cache:
            return

        path_map: Dict[str, str] = {}
        stem_map: Dict[str, str] = {}
        ambiguous_stems = set()

        if os.path.exists(base_dir):
            for root, dirs, files in os.walk(base_dir):
                for ignore_dir in ("node_modules", ".git", ".astro", "dist", "build", "universal", "sovereign"):
                    if ignore_dir in dirs:
                        dirs.remove(ignore_dir)

                parts = [p.lower() for p in root.split(os.sep)]
                if t_lang in parts:
                    idx = len(parts) - 1 - parts[::-1].index(t_lang)
                    sub_dirs = parts[idx + 1:]
                    for f in files:
                        if f.endswith(".md"):
                            fp = os.path.join(root, f)
                            rel_tokens = sub_dirs + [f.lower()]
                            rel_p = "/".join(rel_tokens)
                            stem = os.path.splitext(f)[0].lower()
                            rel_no_ext = "/".join(sub_dirs + [stem])

                            path_map[rel_p] = fp
                            path_map[rel_no_ext] = fp

                            # 允许只带末级子目录匹配 (如 docs/index.md)
                            if len(sub_dirs) > 1:
                                last_rel_p = f"{sub_dirs[-1]}/{f.lower()}"
                                last_rel_no_ext = f"{sub_dirs[-1]}/{stem}"
                                path_map.setdefault(last_rel_p, fp)
                                path_map.setdefault(last_rel_no_ext, fp)

                            if stem not in ("index", "readme"):
                                stem_map.setdefault(stem, fp)

        cls._path_cache[t_lang] = path_map
        cls._stem_cache[t_lang] = stem_map

    @classmethod
    def resolve_chapter(
        cls,
        file_path: str,
        target_lang: str,
        fallback_title: str,
        fallback_body: str,
        vault_dir: str = "vault"
    ) -> Tuple[str, str]:
        """
        根据原稿相对路径与目标语种，高保真解析目标语言标题与正文。
        优先级：
        1. 人工校对表 translation_reviews (reviewed_title, reviewed_body)
        2. 全相对路径 (docs/index.md, showcase/ast.md) 精准寻址物理 Markdown
        3. 元数据账本 i18n_seo 中的目标语种标题
        4. 回退至母语兜底
        """
        t_lang = (target_lang or "").strip().lower()
        if t_lang in ("zh", "zh-hans", "zh-cn", ""):
            return fallback_title, fallback_body

        if os.path.isabs(file_path):
            rel_p = os.path.relpath(file_path, os.path.abspath(vault_dir)).replace("\\", "/").lower()
        else:
            norm_vault = os.path.normpath(vault_dir).replace("\\", "/").lower()
            norm_fp = os.path.normpath(file_path).replace("\\", "/").lower()
            if norm_fp.startswith(norm_vault + "/"):
                rel_p = norm_fp[len(norm_vault) + 1:]
            elif norm_fp == norm_vault:
                rel_p = ""
            else:
                rel_p = norm_fp

        stem = os.path.splitext(os.path.basename(file_path))[0].lower()
        rel_no_ext = os.path.splitext(rel_p)[0]
        clean_rel_p = re.sub(r'^\d+[-_]', '', rel_p)
        clean_rel_no_ext = re.sub(r'^\d+[-_]', '', rel_no_ext)

        # 1. 优先检查创作者人工校对锁定表
        rev_title, rev_body = cls._get_from_review_table(vault_dir, rel_p, t_lang)
        if rev_body:
            return (rev_title or fallback_title), rev_body

        # 2. 预热目标语种文件索引
        cls.warm_up(t_lang)
        path_map = cls._path_cache.get(t_lang, {})
        stem_map = cls._stem_cache.get(t_lang, {})

        # 提取原稿在 documents 表中记录的 slug 与 i18n_seo 标题
        doc_slug, i18n_title = cls._get_doc_metadata(vault_dir, rel_p, t_lang)

        doc_dir = os.path.dirname(rel_p)
        slug_cands = []
        if doc_slug:
            sl = doc_slug.lower()
            if doc_dir:
                slug_cands.extend([f"{doc_dir}/{sl}.md", f"{doc_dir}/{sl}"])
            slug_cands.extend([f"{sl}.md", sl])

        # 物理寻址探针顺序（全相对路径与 slug 路径优先，绝不允许跨目录乱匹配 index.md）
        target_fp = None
        for cand in [rel_p, rel_no_ext, clean_rel_p, clean_rel_no_ext] + slug_cands:
            if cand and cand in path_map:
                target_fp = path_map[cand]
                break
        if not target_fp and stem not in ("index", "readme"):
            target_fp = stem_map.get(stem) or (stem_map.get(doc_slug.lower()) if doc_slug else None)

        if target_fp and os.path.isfile(target_fp):
            try:
                with open(target_fp, "r", encoding="utf-8", errors="ignore") as fp:
                    content = fp.read()
                if not content.lstrip().startswith("<!DOCTYPE"):
                    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
                    parsed_title = i18n_title
                    parsed_body = content.strip()
                    if m:
                        fm = yaml.safe_load(m.group(1)) or {}
                        parsed_title = fm.get("title") or parsed_title
                        parsed_body = m.group(2).strip()
                    if parsed_title:
                        parsed_title = re.sub(r"^[🌐\s]+", "", str(parsed_title)).strip()
                    return (parsed_title or fallback_title), parsed_body
            except Exception:
                pass

        # 3. 降级：如果仅有 i18n 标题而正文未翻译，使用 i18n 标题 + 原正文
        final_title = i18n_title or fallback_title
        return final_title, fallback_body

    @classmethod
    def _get_from_review_table(cls, vault_dir: str, rel_path: str, lang: str) -> Tuple[Optional[str], Optional[str]]:
        """从 SQLite translation_reviews 提取人工校对文本"""
        try:
            db_path = os.path.join(vault_dir, ".plenipes/cache/ledger.db")
            if not os.path.exists(db_path):
                return None, None
            with sqlite3.connect(db_path) as conn:
                row = conn.execute(
                    "SELECT reviewed_title, reviewed_body FROM translation_reviews WHERE rel_path = ? COLLATE NOCASE AND lang_code = ? COLLATE NOCASE",
                    (rel_path, lang)
                ).fetchone()
                if row and row[1]:
                    return row[0], row[1]
        except Exception:
            pass
        return None, None

    @classmethod
    def _get_doc_metadata(cls, vault_dir: str, rel_path: str, lang: str) -> Tuple[Optional[str], Optional[str]]:
        """从 documents 表获取 slug 与多语言 SEO 翻译标题"""
        try:
            db_path = os.path.join(vault_dir, ".plenipes/cache/ledger.db")
            if not os.path.exists(db_path):
                return None, None
            with sqlite3.connect(db_path) as conn:
                row = conn.execute(
                    "SELECT slug, metadata_json FROM documents WHERE rel_path = ? COLLATE NOCASE",
                    (rel_path,)
                ).fetchone()
                slug = row[0] if row else None
                i18n_title = None
                if row and row[1]:
                    meta = json.loads(row[1])
                    seo = meta.get("seo_data", {})
                    slug = slug or seo.get("slug")
                    i18n_title = seo.get("i18n_seo", {}).get(lang, {}).get("seo_title")
                return slug, i18n_title
        except Exception:
            pass
        return None, None
