#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes AI Adapter - NLP Processor
模块职责：深度语义分析。利用大模型提取文档实体、生成智能摘要并执行语义聚类。
🛡️ [V24.5] 语义主权：驱动知识图谱从邻接表向实体矩阵进化。
"""

import json
from typing import List, Dict, Any, Optional
from core.utils.tracing import tlog

class NLPAdapter:
    """🚀 [V24.5] 深度语义适配器：主权知识挖掘核心"""
    
    def __init__(self, engine):
        self.engine = engine
        self.translator = engine.translator

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        🚀 异步实体提取 (NER)：自动识别人名、地名、技术名词、概念
        """
        system_prompt = (
            "You are a knowledge graph expert. Extract key entities from the provided text. "
            "Categorize them into 'concepts', 'technologies', 'people', and 'projects'. "
            "Return the result in standard JSON format. ONLY return JSON."
        )
        user_prompt = f"Extract entities from this markdown content:\n\n{text[:2000]}"
        
        try:
            # 复用翻译器的推断接口 (确保已挂载 AI 算力)
            res = self.translator.raw_inference(user_prompt, system_prompt)
            if not res: return {}
            
            # 简单清洗 Markdown 装饰
            clean_res = res.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_res)
            
            # 🚀 [V48.3] 强类型卫士：确保 AI 返回的是结构化字典
            if not isinstance(data, dict):
                tlog.warning(f"⚠️ [NLP] AI 返回了非字典格式 ({type(data).__name__})，正在执行降级对齐。")
                return {}
                
            tlog.debug(f"🧠 [NLP] 实体提取成功，发现领域词汇: {list(data.keys())}")
            return data
        except Exception as e:
            tlog.error(f"⚠️ [NLP] 实体提取故障 (Raw: {res[:100] if 'res' in locals() else 'N/A'}): {e}")
            return {}

    def generate_gist(self, text: str) -> str:
        """
        🚀 智能摘要 (Gist)：生成 100 字以内的核心语义指纹
        """
        system_prompt = "Summarize the following text into a single, concise sentence in the same language. Max 100 characters."
        user_prompt = text[:3000]
        
        try:
            res = self.translator.raw_inference(user_prompt, system_prompt)
            return res.strip() if res else ""
        except Exception as e:
            tlog.error(f"⚠️ [NLP] 摘要生成故障: {e}")
            return ""

    def calculate_thematic_clustering(self, doc_ids: List[str]) -> Dict[str, List[str]]:
        """
        🚀 语义聚类：根据已有图谱自动划分星簇 (后续扩展)
        """
        pass
