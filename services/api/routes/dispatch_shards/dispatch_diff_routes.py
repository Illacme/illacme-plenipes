# -*- coding: utf-8 -*-
"""
🚀 [V126.0] Illacme Plenipes - Dispatch Ledger Diff Inspection Routes
职责：提供单篇分发原稿增量 Diff 比对与决策辅助，精准对比当前文库文件与上次发布时的快照差异。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import subprocess
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query
from core.runtime.engine_singleton import get_global_engine

router = APIRouter(tags=["Dispatch Diff"])


def _extract_git_diff_at_publish_time(
    abs_file_path: str,
    vault_root: str,
    published_at: Optional[str]
) -> Dict[str, Any]:
    """通过 Git 历史追溯上次发布时间点前后的物理原稿增量 Diff"""
    if not os.path.isfile(abs_file_path):
        return {"has_diff": False, "error": "文件不存在", "diff_lines": [], "additions": 0, "deletions": 0}

    # 1. 尝试使用发布时间检索当时及之前的最近一次提交快照
    commit_hash = None
    if published_at:
        try:
            cmd_find = [
                "git", "log", f"--before={published_at}", "-n", "1",
                "--format=%H", "--", abs_file_path
            ]
            res_find = subprocess.run(cmd_find, cwd=vault_root, capture_output=True, text=True, timeout=5)
            if res_find.returncode == 0 and res_find.stdout.strip():
                commit_hash = res_find.stdout.strip()
        except Exception:
            commit_hash = None

    # 2. 如果未找到指定时间之前的提交，尝试获取该文件最初的一次提交作为基线
    if not commit_hash:
        try:
            cmd_first = ["git", "log", "--reverse", "-n", "1", "--format=%H", "--", abs_file_path]
            res_first = subprocess.run(cmd_first, cwd=vault_root, capture_output=True, text=True, timeout=5)
            if res_first.returncode == 0 and res_first.stdout.strip():
                commit_hash = res_first.stdout.strip()
        except Exception:
            commit_hash = None

    if not commit_hash:
        return {
            "has_diff": False,
            "error": "未检索到原稿的历史 Git 提交快照",
            "diff_lines": [],
            "additions": 0,
            "deletions": 0
        }

    # 3. 执行 git diff 获取差异
    try:
        cmd_diff = ["git", "diff", "-U3", commit_hash, "--", abs_file_path]
        res_diff = subprocess.run(cmd_diff, cwd=vault_root, capture_output=True, text=True, timeout=8)
        raw_diff = res_diff.stdout if res_diff.returncode == 0 else ""
    except Exception as e:
        return {"has_diff": False, "error": f"执行 Git Diff 异常: {e}", "diff_lines": [], "additions": 0, "deletions": 0}

    if not raw_diff.strip():
        return {
            "has_diff": False,
            "commit_id": commit_hash[:8],
            "diff_lines": [],
            "additions": 0,
            "deletions": 0
        }

    # 4. 解析 Unified Diff 文本为结构化行
    lines = raw_diff.split("\n")
    diff_lines: List[Dict[str, Any]] = []
    add_count = 0
    del_count = 0
    in_hunk = False

    for line in lines:
        if line.startswith("@@"):
            in_hunk = True
            diff_lines.append({"type": "header", "text": line})
            continue
        if not in_hunk:
            continue
        if line.startswith("+"):
            add_count += 1
            diff_lines.append({"type": "addition", "text": line[1:]})
        elif line.startswith("-"):
            del_count += 1
            diff_lines.append({"type": "deletion", "text": line[1:]})
        else:
            diff_lines.append({"type": "context", "text": line[1:] if line.startswith(" ") else line})

    return {
        "has_diff": True,
        "commit_id": commit_hash[:8],
        "additions": add_count,
        "deletions": del_count,
        "diff_raw": raw_diff,
        "diff_lines": diff_lines[:300]
    }


def _calc_time_delta_human(t_published: Optional[float], t_modified: Optional[float]) -> str:
    """计算发布时间与修改时间的人性化中文差值"""
    if not t_published or not t_modified:
        return ""
    diff_sec = int(t_modified - t_published)
    if diff_sec <= 0:
        return "与发布版本一致"
    if diff_sec < 60:
        return f"发布后 {diff_sec} 秒修订"
    if diff_sec < 3600:
        return f"发布后 {diff_sec // 60} 分钟修订"
    if diff_sec < 86400:
        return f"发布后 {diff_sec // 3600} 小时修订"
    return f"发布后 {diff_sec // 86400} 天修订"


@router.get("/api/dispatch/ledger/diff")
async def get_dispatch_ledger_doc_diff(
    rel_path: str = Query(..., description="文稿在文库中的相对路径"),
    target_id: Optional[str] = Query(None, description="目标分发渠道标识")
) -> Dict[str, Any]:
    """
    🔍 [单篇改动差异感知] 获取指定文档当前原稿相较于上次分发时的物理增量 Diff
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=500, detail="引擎实例未就绪")

    vault_root = getattr(engine, "vault_root", "") or (
        getattr(engine.config, "vault_root", "") if hasattr(engine, "config") else ""
    ) or os.getcwd()
    abs_file = os.path.join(vault_root, rel_path)

    if not os.path.isfile(abs_file):
        raise HTTPException(status_code=404, detail=f"文稿不存在: {rel_path}")

    # 1. 查找该文稿对应的分发记录
    published_at = None
    target_name = target_id or "社交媒体"
    remote_url = ""
    meta = getattr(engine, "meta", None)
    if meta and hasattr(meta, "list_all_syndication_records"):
        try:
            records = meta.list_all_syndication_records(limit=200)
            matched = [
                r for r in records
                if isinstance(r, dict) and r.get("rel_path") == rel_path
                and (not target_id or r.get("target_id") == target_id)
            ]
            if matched:
                rec = matched[0]
                published_at = str(rec.get("updated_at") or rec.get("published_at") or "")
                remote_url = str(rec.get("remote_url") or "")
        except Exception:
            pass

    # 2. 获取当前文件最后修改时间
    f_stat = os.stat(abs_file)
    f_mtime = f_stat.st_mtime
    from datetime import datetime
    f_mtime_str = datetime.fromtimestamp(f_mtime).strftime("%Y-%m-%d %H:%M:%S")

    pub_ts = None
    if published_at:
        try:
            pub_ts = datetime.fromisoformat(published_at.replace(" ", "T")).timestamp()
        except Exception:
            pub_ts = None

    time_delta = _calc_time_delta_human(pub_ts, f_mtime)

    # 3. 提取 Git Diff
    diff_res = _extract_git_diff_at_publish_time(abs_file, vault_root, published_at)

    return {
        "status": "success",
        "data": {
            "rel_path": rel_path,
            "target_id": target_id or "",
            "target_name": target_name,
            "remote_url": remote_url,
            "published_at": published_at or "未记录",
            "modified_at": f_mtime_str,
            "time_delta_human": time_delta,
            "has_diff": diff_res.get("has_diff", False),
            "commit_id": diff_res.get("commit_id", ""),
            "additions": diff_res.get("additions", 0),
            "deletions": diff_res.get("deletions", 0),
            "diff_raw": diff_res.get("diff_raw", ""),
            "diff_lines": diff_res.get("diff_lines", []),
            "error": diff_res.get("error")
        }
    }
