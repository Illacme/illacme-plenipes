#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ Illacme-plenipes V24.5 - Semantic Sovereignty Integration Test
职责：验证异步语义挖掘、实体提取与 Term Guard 术语护卫在真实链路下的闭环一致性。
"""

import os
import sys
import shutil
import time
import logging
from unittest.mock import MagicMock

# 🚀 路径自愈
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)


# 配置测试日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("SemanticTest")

TEST_VAULT = os.path.join(BASE_DIR, "content-vault/Semantic_Integration_Test")

def setup_environment():
    """构造全真测试语料"""
    logger.info("🛠️  [1/5] 正在准备全真链路测试语料...")
    if os.path.exists(TEST_VAULT): shutil.rmtree(TEST_VAULT)
    os.makedirs(TEST_VAULT, exist_ok=True)

    # 1. 定义文档：包含一个核心术语
    with open(os.path.join(TEST_VAULT, "concept_definition.md"), "w", encoding='utf-8') as f:
        f.write("""---
title: Hyper-Gravity Propulsion Guide
keywords: Hyper-Gravity Engine
---
The **Hyper-Gravity Engine** is a revolutionary technology for interstellar travel. 
It utilizes quantized fluctuations in the local space-time fabric to generate thrust.
""")

    # 2. 关联文档：引用上述术语
    with open(os.path.join(TEST_VAULT, "usage_report.md"), "w", encoding='utf-8') as f:
        f.write("""---
title: Flight Mission Report
keywords: Hyper-Gravity Engine
---
During the mission, the **Hyper-Gravity Engine** performed within expected parameters. 
Thermal management remained stable throughout the jump.
""")

def wait_for_ai_pool(engine, timeout=30):
    """等待 AI 算力池完成所有任务"""
    from core.logic.orchestration.task_orchestrator import ai_executor
    start = time.time()
    while time.time() - start < timeout:
        stats = ai_executor.get_stats()
        if stats["queue_size"] == 0 and stats["active_workers"] == 0:
            # 额外等待一小会儿确保磁盘写入完成
            time.sleep(0.5)
            return True
        time.sleep(0.5)
    return False

def run_integration_test():
    """执行集成测试核心逻辑"""
    # 🚀 [V24.5] 使用工业级工厂模式创建引擎
    from core.runtime.engine_factory import EngineFactory
    from core.config.config import ConfigManager
    
    config_path = os.path.join(BASE_DIR, "config.yaml")
    cm = ConfigManager(config_path)
    config = cm.config
    
    # 强制注入影子根目录，防止测试污染真实数据
    config.system.data_root = TEST_VAULT
    config.vault_root = TEST_VAULT
    config.metadata_db = os.path.join(TEST_VAULT, "test_ledger.json")
    
    # 强制重定向知识图谱与向量索引路径
    config.system.data_paths["link_graph"] = "test_link_graph.json"
    config.system.data_paths["vectors_json"] = "test_vectors.json"
    
    # 使用工厂创建全功能引擎
    engine = EngineFactory.create_engine(config, workspace_id="semantic_test")
    
    if not engine:
        logger.error("❌ 引擎工厂启动失败！请检查 ContractGuard 审计日志。")
        return False

    # 🚀 [V16.6 核心对齐]：显式修正路径
    engine.vault_root = TEST_VAULT
    engine.paths['vault'] = TEST_VAULT
    
    # 🛡️ 建立 Mock AI 阵地 (防止真实 API 调用消耗)
    # 我们需要 Mock extract_entities, generate_gist 和 translate
    def mock_extract_entities(text):
        if "Hyper-Gravity Engine" in text:
            return {"concepts": ["Hyper-Gravity Engine"], "technologies": ["Interstellar Travel"]}
        return {"concepts": [], "technologies": []}
    
    def mock_generate_gist(text):
        return "Technical guide for advanced propulsion systems."

    # 注入 Mock 适配器
    from core.adapters.ai.nlp import NLPAdapter
    engine.nlp_adapter = NLPAdapter(engine)
    engine.nlp_adapter.extract_entities = MagicMock(side_effect=mock_extract_entities)
    engine.nlp_adapter.generate_gist = MagicMock(side_effect=mock_generate_gist)
    
    # ---------------------------------------------------------
    # STEP A: 同步定义文档 (Trigger Async Mining)
    # ---------------------------------------------------------
    logger.info("📡 [3/5] 正在同步定义文档并触发异步挖掘任务...")
    def_path = os.path.join(TEST_VAULT, "concept_definition.md")
    # 🚀 [V24.6] 强制隔离审计账本，防止污染真实账本且避开全局配额熔断
    from core.governance.audit_ledger import ledger
    ledger.db_path = os.path.join(TEST_VAULT, "test_audit.db")
    ledger._init_db()
    logger.info(f"🧱 [测试治理] 审计账本已重定向至隔离环境: {ledger.db_path}")

    # 提升预算上限
    config.governance.daily_budget = 10000.0

    engine.sync_document(def_path, "docs", "content-vault", is_dry_run=False)
    
    # 验证主流程不阻塞 (即刻返回)
    logger.info("   └── ✅ 主流程已即刻返回，正在等待后台语义入库...")
    
    if not wait_for_ai_pool(engine):
        logger.error("❌ 异步挖掘任务超时未完成！")
        return False
    
    # 验证知识图谱数据
    # 注意：rel_path 现在是相对于 vault_root 的
    rel_path = "concept_definition.md"
    node = engine.knowledge_graph.nodes.get(rel_path)
    if node and "Hyper-Gravity Engine" in node.get("entities", {}).get("concepts", []):
        logger.info(f"   └── ✨ [知识固化校验] 成功捕获实体: Hyper-Gravity Engine (节点: {rel_path})")
    else:
        logger.error(f"❌ 知识固化失败！节点数据: {node}")
        return False

    # ---------------------------------------------------------
    # STEP B: 同步关联文档 (Trigger Term Guard)
    # ---------------------------------------------------------
    logger.info("📡 [4/5] 正在同步关联文档并验证术语护卫 (Term Guard)...")
    
    # 🚀 [V24.6] 使用 patch 拦截 get_best_translator，确保始终使用 Mock 实例
    from unittest.mock import patch
    mock_translator = MagicMock()
    mock_translator.translate = MagicMock(return_value="Mocked Translation")
    mock_translator.node_name = engine.translator.node_name
    
    with patch("core.logic.ai.ai_scheduler.AIScheduler.get_best_translator", return_value=mock_translator):
        usage_path = os.path.join(TEST_VAULT, "usage_report.md")
        engine.sync_document(usage_path, "docs", "content-vault", is_dry_run=False)
        
        # 等待异步挖掘
        wait_for_ai_pool(engine)

        # 验证 Term Guard 注入
        found_context = False
        for call in mock_translator.translate.call_args_list:
            kwargs = call.kwargs
            if "knowledge_context" in kwargs and "Hyper-Gravity Engine" in kwargs["knowledge_context"]:
                found_context = True
                break
            
    if found_context:
        logger.info("   └── ✨ [术语护卫校验] 成功检测到跨文档上下文注入！")
    else:
        logger.error("❌ 术语护卫失效：未能检测到关联知识上下文的透传。")
        return False

    # 验证自动织网 (Shared Entity Link)
    links = engine.knowledge_graph.get_related("usage_report.md")
    shared_link = next((l for l in links if l["id"] == "concept_definition.md" and l["type"] == "SHARED_ENTITY"), None)
    
    if shared_link:
        logger.info(f"   └── ✨ [自动织网校验] 成功建立强语义链路: {shared_link['type']} (强度: {shared_link['strength']:.2f})")
    else:
        logger.error("❌ 自动织网失效：未能在图谱中发现共享实体链路。")
        return False

    return True

def main():
    logger.info("="*50)
    logger.info("Omni-Hub V24.5 Semantic Sovereignty Full-Flow Test")
    logger.info("="*50)
    
    try:
        setup_environment()
        if run_integration_test():
            logger.info("\n🎉 [SUCCESS] 全真链路集成测试通过！语义主权架构已坚不可摧。")
            sys.exit(0)
        else:
            logger.info("\n🛑 [FAILED] 测试未通过，请检查上述逻辑错误。")
            sys.exit(1)
    except Exception as e:
        logger.error(f"🚨 [CRASH] 测试执行崩溃: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
