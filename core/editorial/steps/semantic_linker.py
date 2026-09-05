#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes V18 Pipeline Step - Semantic Linker
职责：利用向量检索自动发现当前文档与其他已索引文档间的语义关联。
"""

import os
import json
from core.editorial.registry import StepRegistry, PipelineStep
from core.utils.tracing import tlog

@StepRegistry.register("semantic_linker")
class SemanticLinkerStep(PipelineStep):
    """🚀 [V18.0] 语义关联提取：自动织就知识网"""
    PLUGIN_ID = "semantic_linker"
    DISPLAY_NAME = "Semantic Linker"
    VERSION = "V5.3"
    DESCRIPTION = "基于文章语义感应相关内容，并自动织入双向链接（Backlinks），构建高维度的知识网络。"
    
    def process(self, ctx):
        engine = ctx.engine
        doc_id = ctx.rel_path
        title = ctx.fm_dict.get("title", doc_id)
        
        # 1. 基础检查
        if not hasattr(engine, "knowledge_graph"):
            return ctx

        # 🚀 [V24.5] 算力平移：将耗时的语义挖掘任务提交至 ai_executor
        from core.logic.orchestration.task_orchestrator import ai_executor, TaskPriority
        
        # 准备任务负载，确保闭包引用正确
        body = getattr(ctx, "ai_pure_body", ctx.body_content)
        
        def _async_semantic_mining():
            try:
                # 🚀 [V24.5] 初始化 NLP 适配器 (Lazy Load)
                if not hasattr(engine, "nlp_adapter"):
                    from core.adapters.ai.nlp import NLPAdapter
                    engine.nlp_adapter = NLPAdapter(engine)

                # 🚀 [V100.2] NLP Cache Guard: 增量 AI 缓存防线
                cached_node = engine.knowledge_graph.nodes.get(doc_id)
                need_nlp = True
                entities = None
                gist = None

                if isinstance(cached_node, dict) and cached_node.get("source_hash") == ctx.current_hash:
                    if isinstance(cached_node.get("entities"), dict) and cached_node.get("gist"):
                        entities = cached_node["entities"]
                        gist = cached_node["gist"]
                        need_nlp = False
                        tlog.info(f"✨ [NLP Cache Guard] 语义实体已命中缓存，跳过 AI 提取: {doc_id}")

                if need_nlp:
                    # 🚀 [跨主题图谱缓存穿透] 优先探测其他已有主题的图谱缓存，实现语义实体与摘要 100% 秒级复用
                    themes_meta_dir = os.path.dirname(os.path.dirname(getattr(engine.knowledge_graph, 'graph_path', '')))
                    if themes_meta_dir and os.path.isdir(themes_meta_dir):
                        for other_t in os.listdir(themes_meta_dir):
                            other_graph_p = os.path.join(themes_meta_dir, other_t, f"knowledge_graph_{other_t}.json")
                            if os.path.exists(other_graph_p) and other_graph_p != engine.knowledge_graph.graph_path:
                                try:
                                    with open(other_graph_p, 'r', encoding='utf-8') as f_other:
                                        other_nodes = json.load(f_other)
                                    o_node = other_nodes.get(doc_id)
                                    if isinstance(o_node, dict) and o_node.get("source_hash") == ctx.current_hash:
                                        if isinstance(o_node.get("entities"), dict) and o_node.get("gist"):
                                            entities = o_node["entities"]
                                            gist = o_node["gist"]
                                            need_nlp = False
                                            engine.knowledge_graph.upsert_node(doc_id, title, entities=entities, gist=gist, source_hash=ctx.current_hash)
                                            tlog.info(f"✨ [NLP Cache Guard] 成功跨主题复用知识图谱缓存 ({other_t}): {doc_id}")
                                            break
                                except Exception:
                                    pass

                if need_nlp:
                    # 🚀 [V24.5] 初始化 NLP 适配器 (Lazy Load)
                    if not hasattr(engine, "nlp_adapter"):
                        from core.adapters.ai.nlp import NLPAdapter
                        engine.nlp_adapter = NLPAdapter(engine)

                    # 1. 执行深度语义挖掘 (NER & Gist)
                    tlog.debug(f"🧠 [SemanticMining] 正在执行深度 NLP 分析: {doc_id}")
                    entities = engine.nlp_adapter.extract_entities(body)
                    gist = engine.nlp_adapter.generate_gist(body)

                    # 2. 更新图谱节点 (包含实体与摘要)
                    engine.knowledge_graph.upsert_node(doc_id, title, entities=entities, gist=gist, source_hash=ctx.current_hash)

                # 3. 生成语义特征 (仅在必要时)
                embedding = getattr(ctx, "embedding", None)
                if embedding is None and engine.embedding_adapter:
                    embedding = engine.embedding_adapter.embed_text(body)

                # 4. 执行向量检索与关联 (Vector Similarity)
                discovery_count = 0
                if embedding and hasattr(engine, "vector_index"):
                    hits = engine.vector_index.search(embedding, top_k=6)
                    for target_id, score in hits:
                        if target_id != doc_id and score > 0.75:
                            engine.knowledge_graph.link(doc_id, target_id, strength=score, rel_type="SEMANTIC_SIMILARITY")
                            discovery_count += 1
                
                # 🚀 [V24.5] 逻辑织网：基于实体共享的强关联 (Shared Entities)
                if isinstance(entities, dict):
                    all_entities = set()
                    for cat_list in entities.values():
                        if isinstance(cat_list, list):
                            all_entities.update(cat_list)
                    
                    if all_entities:
                        STOP_ENTITIES = {
                            "Illacme Plenipes", "Illacme", "Plenipes",
                            "主权数字出版底座", "主权出版系统", "系统",
                            "好未来：数字教育未来趋势白皮书", "数字教育未来趋势白皮书",
                            "好未来", "数字教育", "未来趋势", "白皮书", "welcome-to-illacme"
                        }
                        
                        filtered_all = {e for e in all_entities if e not in STOP_ENTITIES and len(e) > 1}
                        
                        # 🚀 [V100.1] 优先采用极速反向索引匹配算法，解除 100 限制
                        if hasattr(engine.knowledge_graph, "get_shared_entities_candidates"):
                            common_counts = engine.knowledge_graph.get_shared_entities_candidates(doc_id, filtered_all, STOP_ENTITIES)
                            for other_id, common_len in common_counts.items():
                                strength = min(0.5 + (common_len * 0.1), 0.95)
                                engine.knowledge_graph.link(doc_id, other_id, strength=strength, rel_type="SHARED_ENTITY")
                                discovery_count += 1
                        else:
                            # Fallback 兼容
                            for other_id, other_node in list(engine.knowledge_graph.nodes.items())[:100]:
                                if other_id == doc_id: continue
                                if not isinstance(other_node, dict): continue
                                
                                other_entities = set()
                                o_ent_data = other_node.get("entities", {})
                                if isinstance(o_ent_data, dict):
                                    for cat_list in o_ent_data.values():
                                        if isinstance(cat_list, list): other_entities.update(cat_list)
                                
                                filtered_other = {e for e in other_entities if e not in STOP_ENTITIES and len(e) > 1}
                                common = filtered_all.intersection(filtered_other)
                                if len(common) >= 2:
                                    strength = min(0.5 + (len(common) * 0.1), 0.95)
                                    engine.knowledge_graph.link(doc_id, other_id, strength=strength, rel_type="SHARED_ENTITY")
                                    discovery_count += 1

                if discovery_count > 0:
                    concept_count = 0
                    if isinstance(entities, dict):
                        concept_count = len(entities.get('concepts', []))
                    tlog.info(f"🌌 [KnowledgeGalaxy] 后台发现 {discovery_count} 条链路并提取了 {concept_count} 个概念: {doc_id}")
                
                engine.knowledge_graph.save()
            except Exception as e:
                tlog.error(f"⚠️ [SemanticMining] 后台分析故障 ({doc_id}): {e}")

        # 异步点火，不阻塞当前流水线步进
        ai_executor.submit(
            _async_semantic_mining,
            priority=TaskPriority.SEO, # 使用 SEO 级优先级
            task_name=f"SemanticMining-{doc_id}"
        )

        return ctx
