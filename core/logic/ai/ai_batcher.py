#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Batcher (TDR Optimizer)
模块职责：将高频小任务（如元数据生成）合并为单次 AI 推理，降低 TDR 成本。
🚀 [V15.0] 智慧升级：算力批处理，支持全域 SEO 自动化补全。
"""

import os
import json
from core.utils.tracing import tlog

class AIBatcher:
    """🚀 [V15.0] AI 批处理器：减少 Token 浪费，提升同步速度"""

    def __init__(self, engine):
        self.engine = engine
        self.batch_size = 10 # 默认每批处理 10 个文档

    def batch_generate_seo(self, task_queue, force=False):
        """
        🚀 全量扫描任务队列，为缺失 SEO 的文档进行“一站式”算力补全
        """
        if self.engine.no_ai: return

        # 1. 过滤需要补全的文档
        pending_docs = []
        for task_path, prefix, src_rel in task_queue:
            # 🚀 物理路径归一化
            # 🚀 [V34.9] 路径归一化加固：强制使用绝对路径计算相对位移，消除 ../ 等路径震荡
            rel_path = os.path.relpath(
                os.path.abspath(task_path),
                os.path.abspath(self.engine.vault_root)
            ).replace('\\', '/')
            doc_info = self.engine.meta.get_doc_info(rel_path)

            # 如果没有 SEO 数据 且（强制更新 或 是新文件）
            if not doc_info.get('seo_data') or force:
                try:
                    with open(task_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:1000] # 仅读取摘要以节省 Token
                        pending_docs.append({
                            "rel_path": rel_path,
                            "content": content
                        })
                except Exception: continue

        if not pending_docs:
            return

        tlog.info(f"🏎️ [Batcher] 发现 {len(pending_docs)} 个文档缺失元数据，正在开启并发批处理...")

        # 2. 分批处理
        for i in range(0, len(pending_docs), self.batch_size):
            batch = pending_docs[i:i + self.batch_size]
            self._process_batch(batch)

    def _process_batch(self, batch):
        """单批次 AI 交互逻辑"""
        # 构建批处理 Prompt
        prompt_items = []
        for idx, doc in enumerate(batch):
            prompt_items.append(f"Document ID: {idx}\nContent: {doc['content']}\n---")

        system_prompt = (
            "You are an SEO expert. For each document provided below, generate a JSON object with: "
            "'description' (max 150 chars), 'keywords' (list), and a 'slug' (kebab-case). "
            "Output MUST be a JSON array of objects, one for each document ID in order."
        )

        user_prompt = "\n".join(prompt_items)

        try:
            # 🚀 调用 AI 网关执行批处理任务
            raw_response = self.engine.translator.raw_inference(user_prompt, system_prompt)

            # 🚀 [V15.5] 增强型 JSON 解析逻辑
            from core.logic.ai.ai_logic_hub import AILogicHub
            repaired_json = AILogicHub.repair_json_array(raw_response)

            if repaired_json and repaired_json != "[]":
                results = json.loads(repaired_json)
                for idx, res in enumerate(results):
                    if idx < len(batch):
                        doc = batch[idx]
                        tlog.info(f"✨ [Batcher] 为 {doc['rel_path']} 补全元数据成功。")
                        # 暂时将结果存入内存缓存，由 sync_document 消费
                        self.engine._old_info_cache[doc['rel_path']] = {
                            "seo_data": {
                                "description": res.get('description', ''),
                                "keywords": res.get('keywords', []),
                                "slug": res.get('slug', '')
                            }
                        }
            else:
                tlog.warning("⚠️ [Batcher] AI 返回格式异常，批处理跳过。")
        except Exception as e:
            tlog.error(f"❌ [Batcher] 批处理故障: {e}")
