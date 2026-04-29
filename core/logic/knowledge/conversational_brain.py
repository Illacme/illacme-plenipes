#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Logic - Conversational Brain (RAG)
模块职责：检索增强生成 (RAG) 编排器。
通过向量检索召回文档片段，结合用户提问生成基于事实的专业回答。
🛡️ [AEL-Iter-v1.0]：支持本地算力驱动的知识问答。
"""

import os
from typing import List, Dict, Any
from core.utils.tracing import tlog

class ConversationalBrain:
    """🚀 [V1.0] 智脑编排器：让文档会说话"""
    
    def __init__(self, engine):
        self.engine = engine

    def ask(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """
        RAG 核心流程：提问 -> 检索 -> 答复
        """
        if not self.engine.embedding_adapter or not self.engine.vector_index:
            return {"answer": "抱歉，语义引擎尚未初始化，无法回答该问题。", "references": []}

        # 1. 向量化用户提问
        query_vector = self.engine.embedding_adapter.get_embedding(question)
        if not query_vector:
            return {"answer": "无法理解您的提问，请稍后再试。", "references": []}

        # 2. 检索相关文档
        search_results = self.engine.vector_index.search(query_vector, top_k=top_k)
        if not search_results:
            return {"answer": "翻遍了您的文档库，似乎没有找到相关的信息。您可以尝试换个问法。", "references": []}

        # 3. 提取文档内容作为上下文
        context_chunks = []
        references = []
        for rel_path, score in search_results:
            abs_path = os.path.join(self.engine.vault_root, rel_path)
            if os.path.exists(abs_path):
                try:
                    with open(abs_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 仅提取前 2000 字作为上下文
                        context_chunks.append(f"--- Document: {rel_path} ---\n{content[:2000]}")
                        references.append({"path": rel_path, "score": score})
                except Exception: continue

        full_context = "\n\n".join(context_chunks)

        # 4. 构建 RAG Prompt
        prompt = f"""您是一个专业的知识助手。请根据以下提供的文档内容（Context）来回答用户的问题。
如果文档中没有相关信息，请诚实地告诉用户。回答时请尽量简洁、专业。

[Context]
{full_context}

[User Question]
{question}

[Final Answer]"""

        # 5. 调用 AI 生成回答 (优先使用主算力节点)
        try:
            # 🚀 [V15.0] 复用已有的 Translator 逻辑进行文本生成
            from core.adapters.ai.base import AIScheduler
            # 我们直接通过引擎的 API 适配器发送原始 Prompt
            answer = self.engine.translator.raw_chat(prompt)
            return {
                "answer": answer,
                "references": references
            }
        except Exception as e:
            tlog.error(f"🛑 [RAG 生成失败]: {e}")
            return {"answer": f"AI 思考时发生了故障: {e}", "references": references}
