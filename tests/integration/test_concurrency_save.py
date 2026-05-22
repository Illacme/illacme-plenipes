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

if __name__ == "__main__":
    test_concurrency_debounce_save()
