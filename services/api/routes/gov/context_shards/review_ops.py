# -*- coding: utf-8 -*-
"""
🔒 [I5] Translation Human Review Ops
职责：翻译人工校对回流的业务原子逻辑实现。
遵循职责分离 SOP：路由层仅注册端点，业务逻辑全量下沉至此文件。
"""

import re
from core.utils.tracing import tlog


def _split_paragraphs(body: str) -> list:
    """
    将 Markdown 正文切割为段落块列表，用于前端段落级校对（Q1=C）。
    切割规则：
      - 普通段落：双换行分隔
      - Callout 块：::: ... ::: 作为整体块
      - 代码块：``` ... ``` 作为只读整体块
    返回：[{"index": int, "type": "paragraph"|"callout"|"code", "text": str}]

    🛡️ [UI 防污染] 在分段前剥离 Sovereign-Tag 系统追踪注释。
    这些注释（如 <!-- Sovereign-Tag: [[AEL-Iter-ID: ...]] -->）是系统内部
    用于溯源的元数据，对普通用户无意义，在校对工作台中显示容易造成困惑。
    原始 .md 文件磁盘内容不受影响，系统溯源功能照常工作。
    """
    if not body:
        return []

    # 剥离系统内部追踪注释（Sovereign-Tag），不在校对 UI 中对用户展示
    body = re.sub(r'\s*<!--\s*Sovereign-Tag:.*?-->', '', body, flags=re.DOTALL).strip()

    blocks = []
    idx = 0
    lines = body.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # 代码块：只读整体
        if line.strip().startswith("```"):
            end_j = i + 1
            while end_j < len(lines) and not lines[end_j].strip().startswith("```"):
                end_j += 1
            if end_j < len(lines):
                end_j += 1
            blocks.append({
                "index": idx,
                "type": "code",
                "text": "\n".join(lines[i:end_j])
            })
            idx += 1
            i = end_j
            continue

        # Callout 块（::: 语法）
        if line.strip().startswith(":::"):
            end_j = i + 1
            while end_j < len(lines) and not lines[end_j].strip().startswith(":::"):
                end_j += 1
            if end_j < len(lines):
                end_j += 1
            blocks.append({
                "index": idx,
                "type": "callout",
                "text": "\n".join(lines[i:end_j])
            })
            idx += 1
            i = end_j
            continue

        # 普通段落：收集连续非空行
        if line.strip():
            para_lines = []
            while i < len(lines) and lines[i].strip():
                para_lines.append(lines[i])
                i += 1
            blocks.append({
                "index": idx,
                "type": "paragraph",
                "text": "\n".join(para_lines)
            })
            idx += 1
        else:
            i += 1

    return blocks


import os
from core.utils.text import parse_frontmatter
from services.api.logic.content_ops_shards.safe_ops import resolve_safe_path

def get_translation_snapshot_impl(engine, doc_id: str) -> dict:
    """
    获取文档所有已翻译语种的快照（含锁定状态、段落分割）。
    数据来源：translation_reviews 账本 + 物理缓存（Q6=B）。
    """
    if not engine or not engine.meta:
        return {"error": "Engine not initialized", "langs": {}}

    doc_info = engine.meta.get_doc_info(doc_id) or {}

    # 1. 查询该文档有哪些已翻译的语种
    t_rows = engine.meta.sqlite._get_conn().execute(
        "SELECT lang_code, status FROM translations WHERE rel_path = ?", (doc_id,)
    ).fetchall()
    t_map = {dict(t)["lang_code"]: dict(t) for t in t_rows}
    
    # 2. 查询人工校对表
    r_rows = engine.meta.sqlite._get_conn().execute(
        "SELECT lang_code, reviewed_body, reviewed_title, reviewed_desc, is_stale, reviewed_at, reviewed_by FROM translation_reviews WHERE doc_id = ?", (doc_id,)
    ).fetchall()
    r_map = {dict(r)["lang_code"]: dict(r) for r in r_rows}

    # 3. 获取原文用于对比
    src_abs = resolve_safe_path(engine, doc_id)
    source_body = ""
    source_title = ""
    source_desc = ""
    if src_abs and os.path.exists(src_abs):
        try:
            with open(src_abs, "r", encoding="utf-8") as f:
                fm_dict, source_body, _ = parse_frontmatter(f.read())
                source_title = fm_dict.get("title", "")
                source_desc = fm_dict.get("description", "")
        except Exception:
            pass

    # 🛡️ [UI 降级自愈] 如果物理原文中没有定义 title 前置属性（例如无 frontmatter 标题）
    # 则自动回落到账本中登记的标题（即从文件名生成的标题），解决原文标题显示为“无标题”的问题。
    if not source_title:
        source_title = doc_info.get("title", "")

    source_paras = _split_paragraphs(source_body)

    langs = {}
    
    # 准备路径解析依赖
    route_prefix = doc_info.get("route_prefix")
    sub_dir = doc_info.get("sub_dir")
    slug = doc_info.get("slug")
    target_slot = doc_info.get("target_slot", "docs")
    cache_dir = engine.paths.get("cache") if hasattr(engine, "paths") else None
    target_ext = os.path.splitext(doc_id)[1].lower() or ".md"

    # 获取全量目标语种配置（仅使用当前版图配置中激活的语种）
    # 🛡️ [UI 防污染] 不将 translations 表中的历史過期语种（如旧版本的 PT）并入展示，
    # 只展示当前 i18n_settings.targets 配置的语种，避免用户看到不应展示的 Tab。
    target_codes = []
    if hasattr(engine, "config") and hasattr(engine.config, "i18n_settings"):
        target_codes = [t.lang_code for t in engine.config.i18n_settings.targets]

    for lang_code in target_codes:
        td = t_map.get(lang_code, {})
        st = td.get("status", "MISSING")
        
        r_data = r_map.get(lang_code, {})
        has_review = bool(r_data)
        
        body = r_data.get("reviewed_body")
        title = r_data.get("reviewed_title")
        desc = r_data.get("reviewed_desc")

        # 若无人工校对数据，且翻译状态不为错误或缺失，则从物理缓存磁盘读取最新 AI 译文快照
        if not body and cache_dir and hasattr(engine, "route_manager"):
            try:
                cache_mirror = engine.route_manager.resolve_physical_path(
                    cache_dir, lang_code, route_prefix, sub_dir, slug, target_ext, source_type=target_slot
                )
                if os.path.exists(cache_mirror):
                    with open(cache_mirror, "r", encoding="utf-8") as f:
                        fm_dict, pure_content, _ = parse_frontmatter(f.read())
                        body = pure_content
                        title = title or fm_dict.get("title", "")
                        desc = desc or fm_dict.get("description", "")
            except Exception as e:
                from core.utils.tracing import tlog
                tlog.warning(f"Failed to read AI translation snapshot for {doc_id} / {lang_code}: {e}")

        # 如果没有读到正文，则标记为空状态，但不跳过渲染
        if not body:
            # 🚀 [BugFix] 如果底层翻译状态已经明确标识为 ERROR（如 OOM、断网多次重试后放弃）
            # 则强制结束 is_missing 轮询，向前端明确下发错误状态，避免前端无限转圈
            if st == "ERROR":
                langs[lang_code] = {
                    "is_missing": False,
                    "title": title or "⚠️ 翻译失败 / Translation Failed",
                    "desc": desc or "AI 引擎处理该语种时发生严重错误，请检查后台日志或节点连通性。",
                    "paragraphs": [{"index": 0, "type": "paragraph", "text": "*(该语种生成失败，请稍后重试或检查 LLM 配置)*"}],
                    "human_approved": False,
                    "review_is_stale": False,
                }
            else:
                langs[lang_code] = {
                    "is_missing": True,
                    "title": "",
                    "desc": "",
                    "paragraphs": [],
                    "human_approved": False,
                    "review_is_stale": False,
                }
            continue

        langs[lang_code] = {
            "is_missing": False,
            "title": title or "",
            "desc": desc or "",
            "paragraphs": _split_paragraphs(body),
            "human_approved": True if has_review else False,
            "review_is_stale": bool(r_data.get("is_stale", False)),
            "reviewed_at": r_data.get("reviewed_at"),
            "reviewed_by": r_data.get("reviewed_by"),
        }

    return {
        "doc_id": doc_id,
        "doc_title": doc_info.get("title", ""),
        "source_title": source_title,
        "source_desc": source_desc,
        "source_hash": doc_info.get("source_hash", ""),
        "source_paragraphs": source_paras,
        "langs": langs
    }


def save_human_review_impl(engine, doc_id: str, lang_code: str,
                            paragraphs: list, title: str = None,
                            desc: str = None) -> dict:
    """
    保存人工校对结果并上锁（语种级，Q2=A）。
    存储 SSG 渲染前中间态 Markdown（Q4=A）。
    paragraphs 为前端返回的段落列表（含用户修改）。
    """
    if not engine or not engine.meta:
        return {"ok": False, "error": "Engine not initialized"}

    # 重建完整正文（将已编辑段落合并回整文）
    body_parts = []
    for para in (paragraphs or []):
        body_parts.append(para.get("text", ""))
    reviewed_body = "\n\n".join(body_parts)

    # 计算当前原稿 hash，写入锁定记录
    doc_info = engine.meta.get_doc_info(doc_id) or {}
    source_hash = doc_info.get("source_hash", "")

    engine.meta.set_human_lock(
        doc_id=doc_id,
        lang_code=lang_code,
        reviewed_body=reviewed_body,
        reviewed_title=title or None,
        reviewed_desc=desc or None,
        source_hash=source_hash,
        reviewed_by="commander"
    )

    tlog.info(f"🔒 [I5] 校对结果已保存并上锁: {doc_id} / {lang_code}")
    return {"ok": True, "doc_id": doc_id, "lang_code": lang_code}


def unlock_human_review_impl(engine, doc_id: str, lang_code: str) -> dict:
    """
    解除人工校对锁（用户主动操作，重置为 AI 重译）。
    """
    if not engine or not engine.meta:
        return {"ok": False, "error": "Engine not initialized"}

    engine.meta.clear_human_lock(doc_id=doc_id, lang_code=lang_code)
    tlog.info(f"🗑️ [I5] 校对锁已解除: {doc_id} / {lang_code}")
    return {"ok": True, "doc_id": doc_id, "lang_code": lang_code}
