#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI - Mock Simulator Provider
模块职责：提供零成本的算力模拟器，用于全链路集成测试。
🛡️ [AEL-Iter-v11.7]：模拟模式，支持多语种占位翻译。
"""

import json
import re
from typing import Dict, Any
from core.adapters.ai.base import BaseTranslator


class MockAIProvider(BaseTranslator):
    """🚀 算力模拟器：在不调用真实 API 的情况下模拟翻译过程"""
    PLUGIN_ID = 'mock'

    def _ask_ai(self, payload: Dict[str, Any]) -> str:
        """模拟原子操作：根据任务类型返回模拟数据"""
        system_prompt = (payload.get("system") or "").lower()
        user_content = payload.get("user") or ""
        
        # 调试信息
        # tlog.info(f"🔮 [Mock Debug] System Prompt: {system_prompt}")

        # 1. 模拟 Slug 任务 (识别 generate 或 slug)
        if "slug" in system_prompt or "generate" in system_prompt:
            # 🚀 [V11.8] 强力标题提取：支持 ### Title ### 或 Title:
            title_match = re.search(r"(?:### Title ###|Title:)\s*(.*)", user_content, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else user_content
            
            # 物理清洗
            clean = re.sub(r'[^\w\-]', '', title.replace(' ', '-').lower())
            return clean if clean else "simulated-slug"

        # 2. 模拟 SEO 任务 (识别 seo, analyze 或 json)
        if "seo" in system_prompt or "analyze" in system_prompt or "json" in system_prompt:
            return json.dumps({
                "description": "[MOCK] This is a simulated SEO description for testing.",
                "keywords": ["mock", "test", "resonance"]
            })

        # 3. 模拟翻译任务
        target_lang = "target"
        if "translate to" in system_prompt:
            target_lang = system_prompt.split("translate to")[-1].strip().split(" ")[0]
        
        return f"[{target_lang.upper()} SIMULATED] {user_content[:100]}..."

    def get_archetype_params(self) -> Dict[str, Any]:
        return {"mock_mode": True}
