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
        # 🚀 [V51.0] 动态算力载荷：从配置中读取批处理参数，支持 Dashboard 实时调节
        batch_cfg = getattr(engine.config.system, 'batch_processing', None)
        self.batch_size = getattr(batch_cfg, 'size', 10) if batch_cfg else 10
        self.context_limit = getattr(batch_cfg, 'context_limit', 1000) if batch_cfg else 1000

    def batch_generate_seo(self, task_queue, force=False):
        """
        🚀 全量扫描任务队列，为缺失 SEO 的文档进行“一站式”算力补全
        """
        if self.engine.no_ai: return

        # 1. 过滤需要补全的文档
        pending_docs = []
        for task_path, prefix, src_rel, target_slot in task_queue:
            # 🚀 物理路径归一化
            rel_path = os.path.relpath(
                os.path.abspath(task_path),
                os.path.abspath(self.engine.vault_root)
            ).replace('\\', '/')
            doc_info = self.engine.meta.get_doc_info(rel_path)

            # 如果没有 SEO 数据 且（强制更新 或 是新文件）
            if not doc_info.get('seo_data') or force:
                try:
                    with open(task_path, 'r', encoding='utf-8') as f:
                        # 🚀 使用动态限额读取摘要
                        content = f.read()[:self.context_limit]
                        pending_docs.append({
                            "rel_path": rel_path,
                            "content": content
                        })
                except Exception: continue

        if not pending_docs:
            return

        tlog.info(f"🏎️ [Batcher] 发现 {len(pending_docs)} 个文档缺失元数据，正在开启分批算力补全 (BatchSize: {self.batch_size})...")

        # 2. 分批处理
        for i in range(0, len(pending_docs), self.batch_size):
            batch = pending_docs[i:i + self.batch_size]
            try:
                self._process_batch(batch)
            except Exception as be:
                tlog.error(f"❌ [Batcher] 单批次执行故障: {be}")

    def _process_batch(self, batch):
        """单批次 AI 交互逻辑"""
        prompt_items = []
        for idx, doc in enumerate(batch):
            prompt_items.append(f"Document ID: {idx}\nContent: {doc['content']}\n---")

        system_prompt = (
            "You are an SEO expert. For each document provided below, generate a JSON object with: "
            "'description' (max 150 chars), 'keywords' (list), and a 'slug' (kebab-case). "
            "Output MUST be a JSON array of objects, one for each document ID in order. "
            "Do not include any conversational text, only the raw JSON array."
        )

        user_prompt = "\n".join(prompt_items)

        try:
            # 🚀 调用 AI 网关执行批处理任务 (此处已具备 Fallback 能力)
            raw_response = self.engine.translator.raw_inference(user_prompt, system_prompt)
            if not raw_response:
                return

            # 🚀 [V15.5] 增强型 JSON 解析逻辑
            from core.logic.ai.ai_logic_hub import AILogicHub
            repaired_json = AILogicHub.repair_json_array(raw_response)

            if repaired_json and repaired_json.strip().startswith('['):
                try:
                    results = json.loads(repaired_json)
                    for idx, res in enumerate(results):
                        if idx < len(batch):
                            doc = batch[idx]
                            tlog.info(f"✨ [Batcher] 为 {doc['rel_path']} 补全元数据成功。")
                            self.engine._old_info_cache[doc['rel_path']] = {
                                "seo_data": {
                                    "description": res.get('description', ''),
                                    "keywords": res.get('keywords', []),
                                    "slug": res.get('slug', '')
                                }
                            }
                except json.JSONDecodeError as je:
                    tlog.error(f"⚠️ [Batcher] JSON 解码失败: {je} | Raw: {raw_response[:100]}...")
            else:
                tlog.warning(f"⚠️ [Batcher] AI 返回格式非数组，批处理跳过。节点: {self.engine.translator.node_name}")
        except Exception as e:
            raise e
