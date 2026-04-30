#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes V18 Pipeline Step - Semantic Linker
职责：利用向量检索自动发现当前文档与其他已索引文档间的语义关联。
"""

from core.editorial.registry import StepRegistry, PipelineStep
from core.utils.tracing import tlog

@StepRegistry.register("semantic_linker")
class SemanticLinkerStep(PipelineStep):
    """🚀 [V18.0] 语义关联提取：自动织就知识网"""
    
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

                # 1. 执行深度语义挖掘 (NER & Gist)
                tlog.debug(f"🧠 [SemanticMining] 正在执行深度 NLP 分析: {doc_id}")
                entities = engine.nlp_adapter.extract_entities(body)
                gist = engine.nlp_adapter.generate_gist(body)

                # 2. 更新图谱节点 (包含实体与摘要)
                engine.knowledge_graph.upsert_node(doc_id, title, entities=entities, gist=gist)

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
                # 遍历所有已知节点，寻找共享实体 (简单实现，后续可优化为索引查询)
                if isinstance(entities, dict):
                    all_entities = set()
                    for cat_list in entities.values():
                        if isinstance(cat_list, list):
                            all_entities.update(cat_list)
                    
                    if all_entities:
                        # 仅抽样检查部分节点以防性能抖动
                        for other_id, other_node in list(engine.knowledge_graph.nodes.items())[:100]:
                            if other_id == doc_id: continue
                            
                            # 🚀 [V48.3] 脏数据卫士：如果节点被损坏为非字典类型，安全跳过
                            if not isinstance(other_node, dict): continue
                            
                            other_entities = set()
                            # 🚀 安全获取实体列表
                            o_ent_data = other_node.get("entities", {})
                            if isinstance(o_ent_data, dict):
                                for cat_list in o_ent_data.values():
                                    if isinstance(cat_list, list): other_entities.update(cat_list)
                            
                            common = all_entities.intersection(other_entities)
                            if common:
                                # 共享实体越多，强度越高
                                strength = min(0.5 + (len(common) * 0.1), 0.95)
                                engine.knowledge_graph.link(doc_id, other_id, strength=strength, rel_type="SHARED_ENTITY")
                                discovery_count += 1

                if discovery_count > 0:
                    # 🚀 安全获取 concept 数量
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
