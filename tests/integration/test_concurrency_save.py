import os
import time
import threading
from core.logic.knowledge.knowledge_graph import KnowledgeGraph

def test_concurrency_debounce_save():
    """🚀 [量化测试] 并发防抖与非阻塞写入竞态测试用例"""
    temp_graph_path = "tests/integration/temp_knowledge_graph_test.json"
    if os.path.exists(temp_graph_path):
        os.remove(temp_graph_path)
        
    # 物理初始化
    kg = KnowledgeGraph(temp_graph_path)
    
    # 重置物理写计数器
    if hasattr(kg, "disk_write_count"):
        kg.disk_write_count = 0
        
    threads = []
    
    def worker(i):
        # 1. 模拟并发插入节点与高维语义链接
        kg.upsert_node(f"doc_{i}", f"Title {i}")
        kg.link(f"doc_{i}", "central_hub", strength=0.9)
        # 2. 模拟高频防抖写入
        kg.save(debounce=True)
        
    # 启动 30 个超密集并发加工线程
    for i in range(30):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        
    for t in threads:
        t.start()
        
    for t in threads:
        t.join()
        
    # 此时防抖计时器应该已激活（0.5s 物理合并）。
    # 让我们等待 0.7 秒，使防抖刷盘物理流彻底刷入磁盘
    time.sleep(0.7)
    
    # 3. 物理读写计数校验与强一致断言
    assert hasattr(kg, "disk_write_count")
    print(f"\n📊 并发 30 个加工任务结束。磁盘实际物理覆写次数: {kg.disk_write_count}")
    
    # 并发防抖合并后，物理磁盘覆写次数应当被严格压缩在 3 次以内 (通常为 1-2 次)，完美降低 95% 冗余 I/O 吞吐
    assert kg.disk_write_count <= 3, f"防抖合并失效，物理覆写次数为: {kg.disk_write_count}"
    
    # 4. 验证强行强制物理落盘 (Sync Channel)
    prev_count = kg.disk_write_count
    kg.upsert_node("doc_sync_immediate", "Sync Immediate Title")
    kg.save(debounce=False)  # 强制同步落盘
    
    assert kg.disk_write_count == prev_count + 1, "同步强制通道物理未执行立即落盘！"
    
    # 5. 验证防抖期间内存与 API 读强一致性 (Eventually Consistent but memory is atomic)
    # 我们应该即使在防抖计时中，依然能从内存节点中强一致地读取到最新的数据
    kg.upsert_node("doc_mem_instant", "Mem Instant Title")
    kg.save(debounce=True)
    
    # 内存必须是实时立即可读的！
    assert "doc_mem_instant" in kg.nodes
    assert kg.nodes["doc_mem_instant"]["title"] == "Mem Instant Title"
    
    # 优雅注销图谱生命周期，确保挂起的 Timer 被全部销毁
    if hasattr(kg, "shutdown"):
        kg.shutdown()
    else:
        # 如果有 Timer 在悬挂，进行清理
        if hasattr(kg, "_debounce_timer") and kg._debounce_timer:
            kg._debounce_timer.cancel()
            
    # 清理临时物理垃圾
    if os.path.exists(temp_graph_path):
        os.remove(temp_graph_path)
    temp_tmp = temp_graph_path + ".tmp"
    if os.path.exists(temp_tmp):
        os.remove(temp_tmp)

def test_knowledge_graph_inverted_index_and_caching():
    """🚀 [测试] 验证知识图谱内存反向索引建立与增量哈希判定"""
    temp_graph_path = "tests/integration/temp_kg_inverted_index_test.json"
    if os.path.exists(temp_graph_path):
        os.remove(temp_graph_path)

    kg = KnowledgeGraph(temp_graph_path)

    # 1. 模拟写入两个有共享实体的节点
    kg.upsert_node("doc_a", "Doc A", entities={"concepts": ["LLM", "Agent", "Sovereign"]}, source_hash="hash_a")
    kg.upsert_node("doc_b", "Doc B", entities={"concepts": ["LLM", "Agent", "Docusaurus"]}, source_hash="hash_b")
    kg.upsert_node("doc_c", "Doc C", entities={"concepts": ["LLM", "VitePress"]}, source_hash="hash_c")

    # 2. 断言反向索引已建立
    assert "LLM" in kg.entity_inverted_index
    assert kg.entity_inverted_index["LLM"] == {"doc_a", "doc_b", "doc_c"}
    assert kg.entity_inverted_index["Agent"] == {"doc_a", "doc_b"}
    assert kg.entity_inverted_index["Sovereign"] == {"doc_a"}

    # 3. 验证通过候选匹配方法寻找共享实体 (doc_a 应该与 doc_b 共享 LLM 和 Agent，个数为 2)
    stop_entities = {"Sovereign"} # 假设 Sovereign 是停用词
    candidates = kg.get_shared_entities_candidates("doc_a", {"LLM", "Agent", "Sovereign"}, stop_entities)
    
    assert "doc_b" in candidates
    assert candidates["doc_b"] == 2 # 共享 LLM 和 Agent
    assert "doc_c" not in candidates # 共享 LLM (仅 1 个)，应该被过滤掉

    # 4. 增量更新：修改 doc_a 增加 Python 实体 (根据 upsert_node 原生合并逻辑，Agent 依然保留，Python 被合入)
    kg.upsert_node("doc_a", "Doc A", entities={"concepts": ["LLM", "Python", "Sovereign"]}, source_hash="hash_a_new")
    
    # 验证新合入的 Python 已被录入反向索引，Agent 仍存在
    assert "Agent" in kg.entity_inverted_index
    assert kg.entity_inverted_index["Agent"] == {"doc_a", "doc_b"}
    assert "Python" in kg.entity_inverted_index
    assert kg.entity_inverted_index["Python"] == {"doc_a"}
    assert kg.nodes["doc_a"]["source_hash"] == "hash_a_new"

    # 清理
    kg.shutdown()
    if os.path.exists(temp_graph_path):
        os.remove(temp_graph_path)

def test_orchestrator_rescue_limit_and_global_delegation():
    """🚀 [测试] 验证全局算力委托与 OrchestratedExecutor 救援线程数量上限限制防护"""
    from core.logic.orchestration.task_orchestrator import OrchestratedExecutor, ai_executor
    
    # 1. 验证全局 ai_executor 可以正常提交并执行任务
    def simple_task(x):
        return x * 2
        
    future = ai_executor.submit(simple_task, 21)
    assert future.result() == 42
    
    # 2. 验证自愈救援线程上限防御
    # 创建一个 max_workers=2 的执行器，预期救援线程上限为 max(4, 2//2) = 4
    test_executor = OrchestratedExecutor(max_workers=2)
    
    # 重置或模拟当前线程已在执行器的 worker 中
    # 我们将当前线程假装命名为包含 @<id(test_executor)> 的名字，从而触发嵌套死锁检测
    original_name = threading.current_thread().name
    threading.current_thread().name = f"OrchestratorWorker-Test@{id(test_executor)}"
    
    try:
        futures = []
        # 并发嵌套提交 15 个任务，触发自愈救援逻辑
        for i in range(15):
            f = test_executor.submit(simple_task, i)
            futures.append(f)
            
        # 收集结果
        results = [f.result() for f in futures]
        assert results == [i * 2 for i in range(15)]
        
        # 统计以 OrchestratorRescue 开头的救援工人数量
        rescue_workers = [w for w in test_executor.workers if w.name.startswith("OrchestratorRescue-")]
        # 救援上限应该严格 <= 4
        assert len(rescue_workers) <= 4
        print(f"\n📊 嵌套提交自愈救援测试成功。实际生成救援工人数: {len(rescue_workers)}，受上限安全阀控制。")
        
    finally:
        # 恢复线程名字，关闭测试执行器
        threading.current_thread().name = original_name
        test_executor.shutdown(wait=True)

def test_vault_indexer_incremental_cache_short_circuit():
    """🚀 [测试] 验证 VaultIndexer 双链索引构建缓存增量短路与读写回填"""
    from core.editorial.vault_indexer import VaultIndexer
    from core.archives.ledger import MetadataManager
    
    # 临时数据库路径
    temp_db_path = "tests/integration/temp_test_indexer_ledger.db"
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)
        
    ledger = MetadataManager(temp_db_path)
    
    # Mock Config
    class DummyConfig:
        class System:
            allowed_extensions = ['.md']
        system = System()
        class I18n:
            class Source:
                lang_code = 'zh'
            source = Source()
        i18n_settings = I18n()
    config = DummyConfig()

    # Mock Source
    class MockSource:
        def __init__(self):
            self.files = {
                "doc1.md": "---\ntitle: Doc One\ntags: [tag1, tag2]\n---\nHello [[doc2]] world.",
                "doc2.md": "---\ntitle: Doc Two\n---\nTarget node."
            }
            self.mtimes = {
                "doc1.md": 1000.0,
                "doc2.md": 2000.0
            }
            self.read_count = 0

        def list_files(self):
            return list(self.files.keys())

        def read_content(self, rel_path):
            self.read_count += 1
            return self.files[rel_path]

        def get_mtime(self, rel_path):
            return self.mtimes[rel_path]
            
    source = MockSource()

    # 1. 第一次运行：缓存未命中，执行全量读取与解析
    md_idx1, asset_idx1, graph1 = VaultIndexer.build_indexes(source, config, ledger)
    
    # 验证读取次数为 2 并且构建了正确的结构
    assert source.read_count == 2
    assert "doc1.md" in md_idx1
    assert graph1["doc1.md"]["links"] == ["doc2"]
    assert graph1["doc1.md"]["metadata"]["tags"] == ["tag1", "tag2"]
    
    # 验证账本中已经被持久化写入了关键元数据
    doc_info = ledger.get_doc_info("doc1.md")
    assert doc_info.get("mtime") == 1000.0
    assert doc_info.get("links") == ["doc2"]
    assert doc_info.get("tags") == ["tag1", "tag2"]

    # 2. 第二次运行：文件未更改，预期触发极速增量缓存短路
    source.read_count = 0  # 重置读取计数
    md_idx2, asset_idx2, graph2 = VaultIndexer.build_indexes(source, config, ledger)
    
    # 验证读取次数应该为 0（即磁盘 I/O 读被彻底短路复用！）
    assert source.read_count == 0
    assert "doc1.md" in md_idx2
    assert graph2["doc1.md"]["links"] == ["doc2"]
    assert graph2["doc1.md"]["metadata"]["tags"] == ["tag1", "tag2"]
    assert graph2["doc1.md"]["metadata"]["mtime"] == 1000.0

    # 3. 第三次运行：修改其中一个文件的时间，验证可以自愈式穿透缓存读取新内容
    source.mtimes["doc1.md"] = 1005.0  # 更新 mtime
    source.files["doc1.md"] = "---\ntitle: Doc One New\n---\nNo wikilinks here."
    source.read_count = 0
    
    md_idx3, asset_idx3, graph3 = VaultIndexer.build_indexes(source, config, ledger)
    # 因为 doc1.md 发生修改，所以应该读取了该修改文件（1次），而 doc2.md 应该依然命中缓存没有被读取
    assert source.read_count == 1
    assert graph3["doc1.md"]["links"] == []
    assert graph3["doc1.md"]["metadata"]["title"] == "Doc One New"
    
    # 验证账本中对应的修改数据也被增量更新
    doc_info_updated = ledger.get_doc_info("doc1.md")
    assert doc_info_updated.get("mtime") == 1005.0
    assert doc_info_updated.get("links") == []
    assert doc_info_updated.get("title") == "Doc One New"

    # 清理
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)

if __name__ == "__main__":
    test_concurrency_debounce_save()
    test_knowledge_graph_inverted_index_and_caching()
    test_orchestrator_rescue_limit_and_global_delegation()
    test_vault_indexer_incremental_cache_short_circuit()
