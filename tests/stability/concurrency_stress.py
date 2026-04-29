import sys
import os
import time
import concurrent.futures
sys.path.append(os.getcwd())

from core.logic.orchestration.task_orchestrator import OrchestratedExecutor, TaskPriority

def test_nested_deadlock_prevention():
    """
    🚀 [V11-Stress] 并发死锁防御测试
    场景：模拟有限池子下的嵌套任务提交。
    """
    print("🧪 [测试开始] 正在探测嵌套并发安全性...")
    
    # 1. 创建一个超小容量的池子 (仅 2 个工位)
    pool = OrchestratedExecutor(max_workers=2)
    
    def leaf_task(val):
        # 模拟原子计算
        return val * 2

    def parent_task(name):
        print(f"  └── 🏗️ 父任务 {name} 启动，正在请求原子算力...")
        # 🚀 模拟嵌套提交
        # 如果架构不健壮，这里同步等待 result() 会瞬间填满池子导致死锁
        f = pool.submit(leaf_task, 10, priority=TaskPriority.TRANSLATION)
        res = f.result(timeout=5) # 5秒超时保护
        print(f"  ✅ 父任务 {name} 拿到结果: {res}")
        return res

    try:
        start_time = time.time()
        # 2. 同时提交 5 个父任务 (远超池子工位)
        print("🚀 正在注入 5 个重载父任务...")
        futures = [pool.submit(parent_task, f"Task-{i}", priority=TaskPriority.INGRESS) for i in range(5)]
        
        # 3. 收集结果
        results = []
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result(timeout=10))
            
        duration = time.time() - start_time
        print(f"🎉 [测试通过] 5 个嵌套任务全部完成！耗时: {duration:.2f}s")
        print("💡 结论：系统已具备物理级别的嵌套死锁免疫力。")
        
    except concurrent.futures.TimeoutError:
        print("❌ [测试失败] 探测到潜在死锁！任务在 10 秒内未返回。")
        sys.exit(1)
    except Exception as e:
        print(f"❌ [测试异常] {e}")
        sys.exit(1)
    finally:
        pool.shutdown(wait=False)

if __name__ == "__main__":
    test_nested_deadlock_prevention()
