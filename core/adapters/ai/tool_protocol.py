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
