# -*- coding: utf-8 -*-
"""
🧠 Illacme Plenipes Content Operations Shard - galaxy_title_ops
职责：实现 3D 知识星谱节点与原稿文库“母语标题真理智能对齐”算法，防止纯文件名/Slug 覆盖创作者的母语/源语种真实标题。
符合 SOP-02 模块拆分协议与 300 行核心复杂度红线。
"""

import os
import re
from typing import Any, Dict, Optional


def resolve_node_true_title(
    rel_path: str,
    raw_title: Optional[str] = None,
    docs_snapshot: Optional[Dict[str, Any]] = None,
    engine: Any = None
) -> str:
    """
    🚀 [V106.2 知识星谱节点标题真理智能回填 - 全球化通用设计]
    对齐原稿文库列表的标题回填逻辑：
    无论创作者母语是中文、英文、日文、法文或西文，均优先提取原稿真实母语标题 (Native Title)，
    彻底防止磁盘文件系统的 Slug/裸文件名 (如 unnamed-draft-2 / getting-started) 退化覆盖展示标题。
    优先层级：
    1. raw_title (若非空且不等于纯文件名与相对路径)
    2. SQLite 账本中的 title (若存在且非纯文件名)
    3. SQLite 账本中的 seo_data.title (若存在且非纯文件名)
    4. 物理文件首部极速嗅探 (Frontmatter title / # 一级标题)
    5. 降级为 raw_title 或文件名
    """
    if not rel_path:
        return raw_title or ""

    base_name = os.path.splitext(os.path.basename(rel_path))[0]

    # 1. 若原始标题有效且不是退化的纯文件名或相对路径，直接使用
    if raw_title and raw_title.strip() and raw_title.strip() != base_name and raw_title.strip() != rel_path:
        return raw_title.strip()

    # 2 & 3. 联动 SQLite 账本 (快照优先，单查保底)
    doc_info = None
    if docs_snapshot and isinstance(docs_snapshot, dict):
        doc_info = docs_snapshot.get(rel_path)
    elif engine and hasattr(engine, "meta") and hasattr(engine.meta, "sqlite"):
        try:
            doc_info = engine.meta.sqlite.get_document(rel_path)
        except Exception:
            pass

    if doc_info and isinstance(doc_info, dict):
        sqlite_title = doc_info.get("title")
        if sqlite_title and sqlite_title.strip() and sqlite_title.strip() != base_name and sqlite_title.strip() != rel_path:
            return sqlite_title.strip()
        seo_data = doc_info.get("seo_data")
        if isinstance(seo_data, dict):
            seo_title = seo_data.get("title")
            if seo_title and seo_title.strip() and seo_title.strip() != base_name and seo_title.strip() != rel_path:
                return seo_title.strip()

    # 4. 物理文件极速嗅探 (仅当标题仍为 base_name 或空时，读取头部至多 1KB)
    vault_root = getattr(engine, "vault_root", None) if engine else None
    if vault_root:
        abs_file = os.path.join(vault_root, rel_path)
        if os.path.exists(abs_file):
            try:
                with open(abs_file, "r", encoding="utf-8", errors="ignore") as f:
                    header_sample = f.read(1024)
                # 检查 frontmatter
                if header_sample.startswith("---"):
                    parts = header_sample.split("---", 2)
                    if len(parts) >= 3:
                        m = re.search(r'title:\s*(.*)', parts[1])
                        if m:
                            cand = m.group(1).strip(" \"'")
                            if cand and cand != base_name:
                                return cand
                # 检查 # 一级标题
                for line in header_sample.splitlines():
                    line_s = line.strip()
                    if line_s.startswith("# "):
                        cand = line_s[2:].strip()
                        if cand and cand != base_name:
                            return cand
            except Exception:
                pass

    return (raw_title.strip() if raw_title else "") or base_name
