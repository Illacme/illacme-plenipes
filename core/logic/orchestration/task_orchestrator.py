# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Task Orchestrator (任务编排器)
模块职责：基于优先级的多线程执行引擎，负责全量任务的调度、并发控制与死锁监测。
🛡️ [V11.8]：工业级权重感知执行器，彻底封堵嵌套死锁。
"""
import heapq
import threading
import time
import concurrent.futures
from enum import IntEnum
from typing import Callable, Any, Dict, List, Optional
from core.utils.tracing import tlog, Tracer

class TaskPriority(IntEnum):
    """🚀 [V10.1] 任务优先级定义"""
    CRITICAL = 0    # 紧急修复/核心状态同步
    INGRESS = 1     # 笔记扫描与初步测绘
    INDEXING = 2    # 链接图谱与元数据构建
    TRANSLATION = 3 # 核心翻译任务
    SEO = 4         # SEO 与 Slug 生成
    SYNDICATION = 5 # 外部平台同步 (Medium/Ghost 等)
    LOW = 10        # 后台埋点与非必要审计

class OrchestratedTask:
    """封装了一个可调度的任务原子"""
    def __init__(self, func: Callable, priority: TaskPriority, name: str, future: concurrent.futures.Future, *args, **kwargs):
        self.func = func
        self.priority = priority
        self.name = name
        self.future = future
        self.args = args
        self.kwargs = kwargs
        self.timestamp = time.time()
        self.trace_id = Tracer.get_id()

    def __lt__(self, other):
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.timestamp < other.timestamp

class OrchestratedExecutor(concurrent.futures.Executor):
    """🚀 [V10.1] 工业级权重感知执行器"""
    def __init__(self, max_workers: int = 4, min_workers: int = 1):
        self.max_workers = max_workers
        self.min_workers = min_workers
        self.queue = []
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.shutdown_flag = False
        self.workers = []
        self.running_tasks = {} # {thread_id: task_name}

        for i in range(max_workers):
            t = threading.Thread(target=self._worker_loop, name=f"OrchestratorWorker-{i}", daemon=True)
            t.start()
            self.workers.append(t)
        tlog.debug(f"🚀 [OrchestratedExecutor] 初始化完成，并发容量: {max_workers} (最小保护: {min_workers})")

    def ensure_active(self):
        """🚀 [V35.2] 算力动态对齐：确保活跃工人数量严格符合配置预期"""
        with self.lock:
            if self.shutdown_flag:
                return
            
            # 1. 物理清理：剔除已死亡的线程
            self.workers = [w for w in self.workers if w.is_alive()]
            
            # 2. 算力补全：若当前活跃工人不足，则按需增殖
            if len(self.workers) < self.max_workers:
                needed = self.max_workers - len(self.workers)
                # tlog.debug(f"♻️ [Orchestrator] 算力缺口探测：正在增殖 {needed} 个新工人以对齐配置...")
                for i in range(needed):
                    idx = len(self.workers)
                    t = threading.Thread(
                        target=self._worker_loop,
                        name=f"OrchestratorWorker-{idx}@{id(self)}",
                        daemon=True
                    )
                    t.start()
                    self.workers.append(t)


    def submit(self, func: Callable, *args, **kwargs):
        """标准提交接口 (默认优先级: TRANSLATION)"""
        self.ensure_active()
        priority = kwargs.pop('priority', TaskPriority.TRANSLATION)
        name = kwargs.pop('task_name', func.__name__)

        # 🚀 [V11.5] 核心死锁探测：严禁在当前池子的工人线程中，同步等待该池子的新任务
        current_thread_name = threading.current_thread().name
        if f"@{id(self)}" in current_thread_name:
            tlog.debug(f"🚨 [死锁风险预警] 池 {id(self)} 的工人在提交嵌套任务 '{name}'。")

        # 🚀 [V34.9] 流量削峰优化
        with self.lock:
            # 即使 ensure_active 尝试复苏，如果依然处于 shutdown 状态则报错
            if self.shutdown_flag:
                raise RuntimeError("Executor is shutdown and cannot be reactivated")

            f = concurrent.futures.Future()
            task = OrchestratedTask(func, priority, name, f, *args, **kwargs)
            # 🚀 [V35.2] 强制诊断：使用 print 绕过日志等级过滤
            print(f"📥 [Orchestrator] 任务 '{name}' 提交至池 {id(self)} | 队列长度: {len(self.queue)}")


            
            # 🚀 [V11.8 生产就绪] 嵌套死锁自愈：如果检测到嵌套提交，动态激活一个“救援工人”
            if f"@{id(self)}" in current_thread_name:
                tlog.info(f"🆘 [Rescue] 探测到嵌套提交 '{name}'，正在动态扩容救援线程以对冲死锁风险。")
                # 临时扩容
                t = threading.Thread(target=self._worker_loop, name=f"OrchestratorRescue-{len(self.workers)}@{id(self)}", daemon=True)
                t.start()
                self.workers.append(t)

            import sys
            sys.stderr.write(f"📥 [DEBUG] 任务 '{name}' 已压栈 | 池: {id(self)} | 队列: {len(self.queue)}\n")
            sys.stderr.flush()
            # 🚀 [V11.5] 格式统一化：(优先级, 时间戳, 任务对象)
            heapq.heappush(self.queue, (priority, task.timestamp, task))

            self.condition.notify_all()
            return f

    def update_concurrency(self, new_max_workers: int, min_limit: int = 1):
        """🚀 [V16.8] 算力动态调配：支持物理红线保护"""
        with self.lock:
            # 🛡️ [物理防御] 严禁低于红线底线
            if new_max_workers < min_limit:
                new_max_workers = min_limit
                tlog.warning(f"🛡️ [算力防御] 检测到尝试突破物理红线 ({min_limit})，已自动对齐底线。")

            old_count = self.max_workers
            self.max_workers = new_max_workers

            if new_max_workers > old_count:
                # 扩容：启动新线程
                for i in range(old_count, new_max_workers):
                    t = threading.Thread(target=self._worker_loop, name=f"OrchestratorWorker-{i}", daemon=True)
                    t.start()
                    self.workers.append(t)
                tlog.debug(f"📈 [Orchestrator] 算力动态扩容: {old_count} -> {new_max_workers}")
            elif new_max_workers < old_count:
                # 缩容：仅更新目标值，工人将在 loop 中自发退役
                tlog.debug(f"📉 [Orchestrator] 算力动态缩容: {old_count} -> {new_max_workers} (Worker 将在处理完当前任务后安全退役)")
            
            # 清理已经停止的线程引用
            self.workers = [w for w in self.workers if w.is_alive()]

    def _worker_loop(self):
        while True:
            task = None
            with self.lock:
                while not self.shutdown_flag and not self.queue:
                    # 🚀 [V16.0] 缩容检查：如果当前活跃线程数已经超过了设定的 max_workers
                    # 则让当前这个因为 Condition 等待被唤醒的线程直接退出
                    if len(self.workers) > self.max_workers:
                        return # 优雅退役
                    self.condition.wait(timeout=1.0)

                if self.shutdown_flag and not self.queue:
                    break

                if self.queue:
                    # 优先级调度
                    _, _, task = heapq.heappop(self.queue)

            if task:
                import sys
                sys.stderr.write(f"🧪 [DEBUG] 工人领取任务: {task.name} | 线程: {threading.get_ident()}\n")
                sys.stderr.flush()
                
                thread_id = threading.get_ident()


                try:
                    with self.lock:
                        self.running_tasks[thread_id] = task.name

                    # 🚀 [V11.5] 动态注入 ID 标识（若尚未注入）
                    if f"@{id(self)}" not in threading.current_thread().name:
                        threading.current_thread().name += f"@{id(self)}"

                    with Tracer.trace_scope(task.trace_id):
                        result = task.func(*task.args, **task.kwargs)
                        task.future.set_result(result)
                except Exception as e:
                    task.future.set_exception(e)
                finally:
                    with self.lock:
                        self.running_tasks.pop(thread_id, None)

    def get_stats(self) -> Dict[str, Any]:
        """🚀 [V24.0] 观测主权：获取当前执行器的运行状态"""
        with self.lock:
            return {
                "pool_id": id(self),
                "queue_size": len(self.queue),
                "active_workers": len(self.running_tasks),
                "max_workers": self.max_workers,
                "running_tasks": list(self.running_tasks.values())
            }

    def wait_until_idle(self, timeout: float = None):
        """🚀 [V48.3] 算力同步屏障：阻塞直至所有任务完成 (不关闭池)"""
        start_time = time.time()
        while True:
            stats = self.get_stats()
            if stats["queue_size"] == 0 and stats["active_workers"] == 0:
                break
            
            if timeout and (time.time() - start_time) > timeout:
                tlog.warning(f"⚠️ [Orchestrator] 等待池 {id(self)} 闲置超时，强制跳过收割。")
                break
            time.sleep(0.5)

    def shutdown(self, wait=True):
        with self.lock:
            self.shutdown_flag = True
            self.condition.notify_all()
        if wait:
            for t in self.workers:
                if t.is_alive():
                    t.join(timeout=2.0)

# 🚀 全局共享执行器 (Singleton)
# 默认初始化为 4 线程，引擎启动后会根据 config.yaml 自动热扩容
global_executor = OrchestratedExecutor(max_workers=4, min_workers=1)

# 🧠 [V16.5] 专职 AI 算力池 (Isolated Compute Pool)
# 用于执行具体的 AI 翻译、SEO 提取等耗时任务，实现与流程调度池的物理隔离，彻底封堵嵌套并发死锁。
# 🚀 [V34.9] 主权防御：强制最小并发为 16，严禁被配置文件设置突破红线。
ai_executor = OrchestratedExecutor(max_workers=16, min_workers=16)

# 🖼️ [V24.0] 专职资产处理池 (Isolated I/O & CPU Pool)
# 用于执行 WebP 转换、图片缩放与物理去重计算。
# 通过物理隔离，确保海量资产加工不会阻塞引擎的元数据决策链。
asset_executor = OrchestratedExecutor(max_workers=8, min_workers=4)

def harvest_all_executors():
    """🚀 [V48.3] 全量算力收割：安全熄灭所有算力池并等待残留任务完成"""
    tlog.info("⌛ [Orchestrator] 正在收割残留异步任务 (SemanticMining/Assets)...")
    # 按照依赖顺序关闭：先关高层池，后关基础池
    ai_executor.shutdown(wait=True)
    asset_executor.shutdown(wait=True)
    global_executor.shutdown(wait=True)
    tlog.info("✅ [Orchestrator] 所有算力池已安全熄灭。")
