#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Tool Use Protocol
模块职责：定义算力网关统一的 Tool Use (Function Calling) 抽象契约。
🛡️ [V75.0] 首次为各大割裂模型协议提供大一统中间层。
"""

from typing import Dict, Any, List, Optional
import json

class IllacmeTool:
    """🚀 标准化工具声明 (Neutral Tool Declaration)"""
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters  # 必须是合法的 JSON Schema 字典

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }

    def to_openai_schema(self) -> dict:
        return self.to_dict()

class ToolCallEvent:
    """🚀 模型发出的工具调用事件 (统一捕获载体)"""
    def __init__(self, tool_name: str, arguments: Dict[str, Any], raw_call_id: str = ""):
        self.tool_name = tool_name
        self.arguments = arguments
        self.raw_call_id = raw_call_id  # 针对 OpenAI 必须透传 the call_id
        
    @property
    def name(self) -> str:
        return self.tool_name

    @property
    def id(self) -> str:
        return self.raw_call_id

    def __repr__(self):
        return f"<ToolCallEvent: {self.tool_name}({self.arguments})>"

class ToolCallResult:
    """🚀 本地执行完毕后，回传给模型的统一结果包裹"""
    def __init__(self, tool_name: str, result: str, raw_call_id: str = ""):
        self.tool_name = tool_name
        self.result = result
        self.raw_call_id = raw_call_id


MCP_PROTOCOL_VERSION = "2024-11-05"

MCP_RESOURCES = [
    {
        "uri": "illacme://vault/index",
        "name": "Vault Document Catalog",
        "description": "Active imprint manuscript catalog, titles, slugs, and podcast/cover readiness.",
        "mimeType": "application/json",
    },
    {
        "uri": "illacme://graph/knowledge",
        "name": "Knowledge Graph Snapshot",
        "description": "3D Knowledge Graph nodes, entities, gists, and cross-document connections.",
        "mimeType": "application/json",
    },
    {
        "uri": "illacme://imprint/config",
        "name": "Active Imprint Configuration",
        "description": "Current publishing imprint identity, source/target languages, and site URL.",
        "mimeType": "application/json",
    },
]

MCP_PROMPTS = [
    {"name": "editorial_readiness_audit", "description": "Audit vault manuscripts, pending podcasts, bound e-books, and dispatch failures.", "arguments": []},
    {"name": "curate_and_bind_book", "description": "Analyze knowledge clusters and assemble a thematic digital book (WebBook/EPUB/PDF).", "arguments": [{"name": "category", "description": "Target vault category or 'all'", "required": True}]},
    {"name": "heal_dispatch_failures", "description": "Diagnose failed syndication/hosting tasks and prepare a remediation & retry plan.", "arguments": [{"name": "target_id", "description": "Optional platform filter", "required": False}]},
]


def _read_mcp_resource(uri: str) -> str:
    import os
    from core.runtime.engine_singleton import get_global_engine
    engine = get_global_engine()
    if uri == "illacme://vault/index":
        snap = engine.meta.get_documents_snapshot() if engine and hasattr(engine, "meta") else {}
        docs = [
            {"rel_path": rp, "title": d.get("title", ""), "slug": d.get("slug", ""), "podcast": bool(d.get("podcast") is True), "cover": d.get("cover", "")}
            for rp, d in (snap.items() if isinstance(snap, dict) else []) if isinstance(d, dict)
        ]
        return json.dumps({"imprint_id": getattr(engine, "imprint_id", "default") if engine else "default", "count": len(docs), "documents": docs}, ensure_ascii=False, indent=2)
    if uri == "illacme://graph/knowledge":
        kg = getattr(engine, "knowledge_graph", None) if engine else None
        nodes = getattr(kg, "nodes", {}) if kg else {}
        summary = {
            rp: {"title": n.get("title", ""), "gist": n.get("gist", ""), "entities": list((n.get("entities") or {}).keys())[:10], "connections": list((n.get("connections") or {}).keys())[:10]}
            for rp, n in (nodes.items() if isinstance(nodes, dict) else []) if isinstance(n, dict)
        }
        return json.dumps({"node_count": len(summary), "nodes": summary}, ensure_ascii=False, indent=2)
    if uri == "illacme://imprint/config":
        cfg = getattr(engine, "config", None) if engine else None
        i18n = getattr(cfg, "i18n_settings", None) if cfg else None
        src = getattr(getattr(i18n, "source", None), "lang_code", "zh") if i18n else "zh"
        targets = [getattr(t, "lang_code", "") for t in (getattr(i18n, "targets", None) or []) if getattr(t, "lang_code", "")]
        return json.dumps({
            "imprint_id": getattr(engine, "imprint_id", "default") if engine else "default",
            "site_name": getattr(cfg, "site_name", "Illacme Plenipes") if cfg else "Illacme Plenipes",
            "vault_root": getattr(engine, "vault_root", os.path.abspath("vault")) if engine else "vault",
            "source_lang": src, "target_langs": targets,
        }, ensure_ascii=False, indent=2)
    raise ValueError(f"Unknown resource URI: {uri}")


def _get_mcp_prompt(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if name == "editorial_readiness_audit":
        text = "Call inspect_publishing_readiness and diagnose_dispatch_failures, then summarize blockers and next publishing actions concisely."
    elif name == "curate_and_bind_book":
        cat = str(args.get("category") or "Docs")
        text = f"Inspect category '{cat}' using curate_topic_collection, then call bind_digital_book(category='{cat}', format_type='webbook')."
    elif name == "heal_dispatch_failures":
        tid = str(args.get("target_id") or "")
        text = f"Call diagnose_dispatch_failures(target_id='{tid}'), inspect root causes, fix any missing frontmatter/assets, and call retry_dispatch_failures."
    else:
        raise ValueError(f"Unknown prompt: {name}")
    return {"description": f"Illacme Plenipes Editorial Workflow: {name}", "messages": [{"role": "user", "content": {"type": "text", "text": text}}]}


async def dispatch_mcp_jsonrpc(req_id: Any, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """处理标准 MCP JSON-RPC 2.0 请求 (initialize, tools/*, resources/*, prompts/*)"""
    import asyncio
    from core import __version__
    from core.adapters.ai.tool_registry import ToolRegistry
    registry = ToolRegistry()
    m, p = (method or "").strip(), (params or {})
    if m == "initialize":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"protocolVersion": MCP_PROTOCOL_VERSION, "capabilities": {"tools": {"listChanged": False}, "resources": {"listChanged": False}, "prompts": {"listChanged": False}}, "serverInfo": {"name": "illacme-plenipes-editorial-mcp", "version": __version__}}}
    if m == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": registry.export_mcp_tools()}}
    if m == "tools/call":
        tool_name = str(p.get("name") or "")
        arguments = p.get("arguments") if isinstance(p.get("arguments"), dict) else {}
        if not registry.get_tool(tool_name):
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool '{tool_name}' not found."}}
        output = await asyncio.to_thread(registry.execute_tool, tool_name, arguments)
        return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": output}], "isError": output.startswith("Error")}}
    if m == "resources/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"resources": MCP_RESOURCES}}
    if m == "resources/read":
        uri = str(p.get("uri") or "")
        try:
            content = await asyncio.to_thread(_read_mcp_resource, uri)
            return {"jsonrpc": "2.0", "id": req_id, "result": {"contents": [{"uri": uri, "mimeType": "application/json", "text": content}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": str(e)}}
    if m == "prompts/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"prompts": MCP_PROMPTS}}
    if m == "prompts/get":
        try:
            return {"jsonrpc": "2.0", "id": req_id, "result": _get_mcp_prompt(str(p.get("name") or ""), p.get("arguments") if isinstance(p.get("arguments"), dict) else {})}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": str(e)}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unsupported MCP method: {m}"}}
