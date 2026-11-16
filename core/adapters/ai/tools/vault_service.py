import os
from typing import Tuple, Optional

def get_secure_vault_path() -> str:
    """
    🏢 动态获取当前品牌的原稿文库（Vault）的物理路径，作为 AI 模块的默认安全沙箱工作目录
    """
    from core.runtime.engine_singleton import get_global_engine
    engine = get_global_engine()
    if engine and hasattr(engine, 'config') and getattr(engine.config, 'vault_root', None):
        return os.path.abspath(engine.config.vault_root)
    return os.path.abspath("./vault")

def verify_sandbox_path(vault_path: str, target_path: str) -> bool:
    """
    🛡️ 安全沙箱锁定检查：使用 os.path.commonpath 防止任何穿越逃逸。
    确保目标绝对路径绝对限制在 secure vault_path 的子树分支中。
    """
    try:
        abs_vault = os.path.abspath(vault_path)
        abs_target = os.path.abspath(target_path)
        return os.path.commonpath([abs_vault]) == os.path.commonpath([abs_vault, abs_target])
    except Exception:
        return False

def fuzzy_match_document(vault_path: str, relative_path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    🌟 [自愈自适应路径定位]：若直接路径不存在，尝试在文稿库中进行模糊与子目录智能搜索匹配。
    参数:
        vault_path: 文稿库绝对路径
        relative_path: 待定位的相对路径或文件名
    返回:
        (matched_full_path, matched_relative_path, error_message)
        - 定位成功: 返回 (绝对路径, 规范化相对路径, None)
        - 定位失败（越界/逃逸）: 返回 (None, None, "Error: Path traversal detected...")
        - 定位失败（找到多个）: 返回 (None, None, "Error: Multiple matching files...")
        - 找不到匹配: 返回 (None, None, None)
    """
    try:
        # 1. 尝试直接拼接绝对路径
        full_path = os.path.abspath(os.path.join(vault_path, relative_path))
        
        # 如果文件直接存在，优先校验其沙箱安全性并直通返回
        if os.path.exists(full_path):
            if verify_sandbox_path(vault_path, full_path):
                return full_path, relative_path, None
            return None, None, "Error: Path traversal detected. Access denied outside the secure manuscript vault."
            
        # 2. 尝试执行模糊自愈定位与子目录智能搜索
        norm_rel = relative_path.replace("\\", "/").strip("/")
        filename = os.path.basename(norm_rel)
        if not filename.endswith('.md') and '.' not in filename:
            filename += '.md'
            
        candidates = []
        for root, dirs, files in os.walk(vault_path):
            if '.plenipes' in root or '.git' in root:
                continue
            for file in files:
                if file.lower() == filename.lower() or file.lower() == norm_rel.lower():
                    cand_path = os.path.abspath(os.path.join(root, file))
                    if verify_sandbox_path(vault_path, cand_path):
                        candidates.append(cand_path)
                        
        if len(candidates) == 1:
            matched_full = candidates[0]
            matched_rel = os.path.relpath(matched_full, vault_path)
            return matched_full, matched_rel, None
        elif len(candidates) > 1:
            rel_cands = [os.path.relpath(c, vault_path) for c in candidates]
            return None, None, f"Error: Multiple matching files found: {', '.join(rel_cands)}. Please specify the exact relative path."
            
        return None, None, None
    except Exception as e:
        return None, None, f"Error in path resolution: {str(e)}"


def sync_document_to_engine(vault_path: str, full_path: str, content: str) -> str:
    """将 AI 工具写入或增量修补后的文档同步注册至 SQLite 元数据账本、双链图谱与 3D 知识星谱"""
    rel_path = os.path.relpath(os.path.abspath(full_path), os.path.abspath(vault_path)).replace("\\", "/")
    try:
        from core.runtime.engine_singleton import get_global_engine
        from core.utils.text import parse_frontmatter
        engine = get_global_engine()
        if not engine:
            return rel_path
        fm, _, _ = parse_frontmatter(content or "")
        meta = fm if isinstance(fm, dict) else {}
        stem = os.path.splitext(os.path.basename(rel_path))[0]
        title = str(meta.get("title") or stem)
        slug = str(meta.get("slug") or stem)
        extra = {}
        if hasattr(engine, "meta") and engine.meta:
            old_info = engine.meta.get_doc_info(rel_path) if hasattr(engine.meta, "get_doc_info") else None
            if isinstance(old_info, dict):
                extra.update({k: v for k, v in old_info.items() if k not in ("title", "slug")})
            for k in ("podcast", "cover", "description", "summary", "tags", "category"):
                if k in meta:
                    extra[k] = meta[k]
            engine.meta.register_document(rel_path, title, slug=slug, **extra)
        if hasattr(engine, "link_graph") and isinstance(engine.link_graph, dict):
            existing_lg = engine.link_graph.get(rel_path)
            links = existing_lg.get("links", []) if isinstance(existing_lg, dict) else []
            engine.link_graph[rel_path] = {
                "links": links,
                "metadata": {
                    "title": title,
                    "lang": "zh",
                    "size": len(content or ""),
                    "mtime": os.path.getmtime(full_path) if os.path.exists(full_path) else None,
                    "tags": meta.get("tags") if isinstance(meta.get("tags"), list) else [],
                }
            }
        if hasattr(engine, "knowledge_graph") and hasattr(engine.knowledge_graph, "nodes"):
            with engine.knowledge_graph._lock:
                if isinstance(engine.knowledge_graph.nodes, dict):
                    node = engine.knowledge_graph.nodes.get(rel_path)
                    if isinstance(node, dict):
                        node["title"] = title
                    else:
                        engine.knowledge_graph.nodes[rel_path] = {
                            "title": title, "connections": {}, "manual_connections": {}, "entities": {}, "gist": ""
                        }
    except Exception:
        pass
    return rel_path


import json as _json
from typing import Dict as _Dict, Any as _Any, List as _List
from core.adapters.ai.tool_protocol import IllacmeTool as _IllacmeTool


class RetryDispatchFailuresTool(_IllacmeTool):
    """🔄 [Feature: Editorial Chief Agent] 死信队列与分发任务自动重试工具"""
    name = "retry_dispatch_failures"
    description = "Retry failed syndication/hosting dispatch tasks in the dead-letter queue (optionally filtered by rel_path or target_id) and trigger immediate background processing."

    def __init__(self):
        super().__init__(name=self.name, description=self.description, parameters=self.get_parameters_schema())

    @classmethod
    def get_parameters_schema(cls) -> _Dict[str, _Any]:
        return {"type": "object", "properties": {"rel_path": {"type": "string", "description": "Optional relative document path to retry."}, "target_id": {"type": "string", "description": "Optional platform/channel ID to retry (e.g. 'wechat', 'devto')."}}, "required": []}

    def execute(self, rel_path: str = "", target_id: str = "") -> str:
        try:
            from core.runtime.engine_singleton import get_global_engine
            engine = get_global_engine()
            if not engine or not hasattr(engine, "meta"):
                return "Error: Engine or metadata ledger is not initialized."
            rp, tid = (rel_path.strip() or None), (target_id.strip() or None)
            engine.meta.retry_syndication_task(rp, tid)
            triggered = False
            try:
                from core.syndication.hub import ContentSyndicator
                syndicator = ContentSyndicator(syndication_cfg=getattr(engine.config, "syndication", {}), site_url=getattr(engine.config, "site_url", ""), sys_tuning_cfg={"vault_root": getattr(engine, "vault_root", os.getcwd())}, meta=engine.meta)
                syndicator.process_pending_retries()
                triggered = True
            except Exception:
                pass
            return _json.dumps({"status": "success", "rel_path": rp or "ALL", "target_id": tid or "ALL", "background_worker_triggered": triggered, "message": "已将匹配的失败分发任务重置为待重试状态并唤醒后台分发队列。"}, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Error retrying dispatch failures: {str(e)}"


class SearchKnowledgeGraphTool(_IllacmeTool):
    """🪐 [Feature: Editorial Chief Agent] 知识星谱实体与拓扑关联检索工具"""
    name = "search_knowledge_graph"
    description = "Search the 3D Knowledge Graph and link topology by keyword, entity, or topic to discover semantically related manuscripts and neighbor connections."

    def __init__(self):
        super().__init__(name=self.name, description=self.description, parameters=self.get_parameters_schema())

    @classmethod
    def get_parameters_schema(cls) -> _Dict[str, _Any]:
        return {"type": "object", "properties": {"query": {"type": "string", "description": "Topic, entity, tag, or document title keyword to search in the knowledge graph."}, "limit": {"type": "integer", "description": "Maximum number of matched nodes to return (default 8)."}}, "required": ["query"]}

    def execute(self, query: str, limit: int = 8) -> str:
        try:
            from core.runtime.engine_singleton import get_global_engine
            engine = get_global_engine()
            if not engine:
                return "Error: Engine not initialized."
            q = (query or "").strip().lower()
            if not q:
                return "Error: Query cannot be empty."
            kg = getattr(engine, "knowledge_graph", None)
            nodes = getattr(kg, "nodes", {}) if kg else {}
            lg = getattr(engine, "link_graph", {}) or {}
            matches: _List[_Dict[str, _Any]] = []
            if isinstance(nodes, dict):
                for rp, node in nodes.items():
                    if not isinstance(node, dict): continue
                    title = str(node.get("title") or os.path.splitext(os.path.basename(rp))[0])
                    gist = str(node.get("gist") or "")
                    entities = list((node.get("entities") or {}).keys()) if isinstance(node.get("entities"), dict) else []
                    tags = lg[rp]["metadata"].get("tags") or [] if isinstance(lg.get(rp), dict) and isinstance(lg[rp].get("metadata"), dict) else []
                    if q in " ".join([rp, title, gist, " ".join(entities), " ".join(str(t) for t in tags)]).lower():
                        conns = list((node.get("connections") or {}).keys())[:5]
                        manual = list((node.get("manual_connections") or {}).keys())[:5]
                        matches.append({"rel_path": rp, "title": title, "gist": gist[:180], "entities": entities[:8], "tags": tags[:6], "neighbors": list(dict.fromkeys(manual + conns))[:6]})
            if not matches and isinstance(lg, dict):
                for rp, entry in lg.items():
                    meta = (entry.get("metadata") or {}) if isinstance(entry, dict) else {}
                    title = str(meta.get("title") or os.path.splitext(os.path.basename(rp))[0])
                    tags = meta.get("tags") or []
                    if q in f"{rp} {title} {' '.join(str(t) for t in tags)}".lower():
                        matches.append({"rel_path": rp, "title": title, "gist": "", "entities": [], "tags": tags[:6], "neighbors": (entry.get("links") or [])[:6]})
            max_n = max(1, min(int(limit or 8), 25))
            return _json.dumps({"status": "success", "query": query, "matched_count": len(matches), "results": matches[:max_n]}, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"Error searching knowledge graph: {str(e)}"
