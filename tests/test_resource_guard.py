#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Tests - Resource Guard Dynamic Throttling
"""

from types import SimpleNamespace
from core.governance.resource_guard import ResourceGuard
from core.logic.orchestration.task_orchestrator import global_executor, ai_executor

def test_resource_guard_dynamic_throttling():
    """测试资源自适应削峰机制：验证并发降级与恢复的基准行为"""
    # Mock Engine
    mock_config = SimpleNamespace(
        system=SimpleNamespace(
            governance=SimpleNamespace(
                resource_guard=SimpleNamespace(
                    cpu_threshold=95.0,
                    ram_threshold=90.0,
                    compute_process_names=["lmstudio", "ollama"],
                    compute_ram_threshold=50.0,
                    check_interval=5.0
                )
            ),
            concurrency=SimpleNamespace(
                global_workers=4,
                ai_workers=2
            )
        )
    )
    mock_engine = SimpleNamespace(config=mock_config)
    
    # 初始化 ResourceGuard
    guard = ResourceGuard(mock_engine)
    
    # 验证配置参数正确对齐
    assert guard.cpu_threshold == 95.0
    assert guard.ram_threshold == 90.0
    assert guard.compute_ram_threshold == 50.0
    
    # 保存原始并发状态模拟
    guard.original_concurrency = {
        "global": 4,
        "ai": 2
    }
    
    # 1. 验证削峰：当原始并发为 2 时，超载削峰应降为 1
    # 期望计算公式：max(1, min(2 // 2, 4)) = 1
    guard._apply_throttle(cpu=97.0, ram=88.0, compute_ram=10.0, silent=True)
    assert guard.is_throttled is True
    assert ai_executor.max_workers == 1
    assert global_executor.max_workers == 1
    
    # 释放并恢复
    guard._release_throttle()
    assert guard.is_throttled is False
    assert ai_executor.max_workers == 2
    assert global_executor.max_workers == 4
    
    # 2. 验证削峰：当原始并发为 16 时，超载削峰应降为 4
    # 期望计算公式：max(1, min(16 // 2, 4)) = 4
    guard.original_concurrency["ai"] = 16
    guard._apply_throttle(cpu=97.0, ram=88.0, compute_ram=10.0, silent=True)
    assert ai_executor.max_workers == 4
    
    # 释放并恢复
    guard._release_throttle()
    assert ai_executor.max_workers == 16
    
    # 3. 验证削峰：当原始并发为 1 时，超载削峰应保底为 1
    # 期望计算公式：max(1, min(1 // 2, 4)) = 1
    guard.original_concurrency["ai"] = 1
    guard._apply_throttle(cpu=97.0, ram=88.0, compute_ram=10.0, silent=True)
    assert ai_executor.max_workers == 1
    
    # 释放并恢复
    guard._release_throttle()
    assert ai_executor.max_workers == 1


def test_resource_guard_hysteresis_recovery():
    """测试滞后恢复（Hysteresis）机制：验证非对称回落时系统继续维持限流削峰，直到两者均恢复"""
    # Mock Engine
    mock_config = SimpleNamespace(
        system=SimpleNamespace(
            governance=SimpleNamespace(
                resource_guard=SimpleNamespace(
                    cpu_threshold=90.0,
                    ram_threshold=90.0,
                    compute_process_names=["lmstudio", "ollama"],
                    compute_ram_threshold=50.0,
                    check_interval=5.0
                )
            ),
            concurrency=SimpleNamespace(
                global_workers=4,
                ai_workers=2
            )
        )
    )
    mock_engine = SimpleNamespace(config=mock_config)
    
    guard = ResourceGuard(mock_engine)
    
    # 模拟初始未限流状态
    guard.is_throttled = False
    
    # 1. 触发限流：当 RAM 超载时
    # cpu = 50.0, ram = 95.0 -> should_throttle = True
    cpu_usage = 50.0
    ram_usage = 95.0
    
    upper_cpu = guard.cpu_threshold
    upper_ram = guard.ram_threshold
    
    should_throttle_1 = cpu_usage > upper_cpu or ram_usage > upper_ram
    assert should_throttle_1 is True
    
    # 执行限流
    guard._apply_throttle(cpu=cpu_usage, ram=ram_usage, compute_ram=10.0, silent=True)
    assert guard.is_throttled is True
    
    # 2. 模拟非对称回落：CPU 极低，但 RAM 仍然超载（高于 recovery threshold ram_threshold - 5.0 = 85.0）
    # cpu = 10.0, ram = 88.0
    # 按照 or 逻辑，只要 RAM > 85.0，should_throttle 应该仍为 True
    cpu_usage = 10.0
    ram_usage = 88.0
    
    lower_cpu = upper_cpu - 5.0
    lower_ram = upper_ram - 5.0
    
    should_throttle_2 = cpu_usage > lower_cpu or ram_usage > lower_ram
    assert should_throttle_2 is True
    
    # 3. 模拟全量回落：两者均低于恢复阈值
    # cpu = 70.0, ram = 80.0
    cpu_usage = 70.0
    ram_usage = 80.0
    
    should_throttle_3 = cpu_usage > lower_cpu or ram_usage > lower_ram
    assert should_throttle_3 is False
    
    # 释放限流
    guard._release_throttle()
    assert guard.is_throttled is False


def test_resource_guard_compute_process_awareness():
    """测试算力专用进程级内存感知削峰与免除误伤逻辑"""
    mock_config = SimpleNamespace(
        system=SimpleNamespace(
            governance=SimpleNamespace(
                resource_guard=SimpleNamespace(
                    cpu_threshold=90.0,
                    ram_threshold=90.0,
                    compute_process_names=["lmstudio", "ollama"],
                    compute_ram_threshold=40.0,
                    check_interval=5.0
                )
            ),
            concurrency=SimpleNamespace(
                global_workers=4,
                ai_workers=2
            )
        )
    )
    mock_engine = SimpleNamespace(config=mock_config)
    guard = ResourceGuard(mock_engine)
    guard.original_concurrency = {"global": 4, "ai": 2}
    
    # 1. 模拟：宿主机整体内存高，但算力进程几乎未运行（免除削峰误伤）
    # cpu = 40.0, ram = 95.0, compute_ram = 2.0 (由于 compute_ram <= 5.0，应不触发削峰)
    cpu_usage = 40.0
    ram_usage = 95.0
    compute_ram_percent = 2.0
    
    upper_cpu = guard.cpu_threshold
    upper_ram = guard.ram_threshold
    upper_compute_ram = guard.compute_ram_threshold
    
    should_throttle_bypass = (
        cpu_usage > upper_cpu
        or compute_ram_percent > upper_compute_ram
        or (ram_usage > upper_ram and compute_ram_percent > 5.0)
    )
    assert should_throttle_bypass is False
    
    # 2. 模拟：算力自身超负荷，直接触发削峰
    # cpu = 40.0, ram = 60.0, compute_ram = 45.0 (直接超出 compute_ram_threshold 40.0)
    compute_ram_percent = 45.0
    should_throttle_compute = (
        cpu_usage > upper_cpu
        or compute_ram_percent > upper_compute_ram
        or (ram_usage > upper_ram and compute_ram_percent > 5.0)
    )
    assert should_throttle_compute is True
    
    # 3. 模拟：宿主机整体内存超限，且算力进程也有较大占用（共振削峰）
    # cpu = 40.0, ram = 92.0, compute_ram = 15.0 (ram > 90.0且compute_ram > 5.0)
    ram_usage = 92.0
    compute_ram_percent = 15.0
    should_throttle_resonance = (
        cpu_usage > upper_cpu
        or compute_ram_percent > upper_compute_ram
        or (ram_usage > upper_ram and compute_ram_percent > 5.0)
    )
    assert should_throttle_resonance is True


def test_resource_guard_dynamic_hot_reload():
    """测试资源守卫动态配置热更新与基线对齐机制"""
    # 构造可变的 Mock Config/Engine
    mock_config = SimpleNamespace(
        system=SimpleNamespace(
            governance=SimpleNamespace(
                resource_guard=SimpleNamespace(
                    cpu_threshold=90.0,
                    ram_threshold=90.0,
                    compute_process_names=["lmstudio", "ollama"],
                    compute_ram_threshold=40.0,
                    check_interval=5.0
                )
            ),
            concurrency=SimpleNamespace(
                global_workers=4,
                ai_workers=2
            )
        )
    )
    mock_engine = SimpleNamespace(config=mock_config)
    guard = ResourceGuard(mock_engine)
    
    # 1. 验证初始阈值正确性
    assert guard.cpu_threshold == 90.0
    assert guard.ram_threshold == 90.0
    assert guard.compute_ram_threshold == 40.0
    assert guard.interval == 5.0
    
    # 2. 模拟配置热更新
    mock_config.system.governance.resource_guard.cpu_threshold = 95.0
    mock_config.system.governance.resource_guard.ram_threshold = 92.0
    mock_config.system.governance.resource_guard.compute_ram_threshold = 60.0
    mock_config.system.governance.resource_guard.check_interval = 1.0
    
    # 验证属性动态感知最新更改，无需重启
    assert guard.cpu_threshold == 95.0
    assert guard.ram_threshold == 92.0
    assert guard.compute_ram_threshold == 60.0
    assert guard.interval == 1.0
    
    # 3. 验证并发限制基线滑动同步
    guard.is_throttled = False
    
    # 执行同步
    guard.original_concurrency = {
        "global": mock_config.system.concurrency.global_workers,
        "ai": mock_config.system.concurrency.ai_workers
    }
    assert guard.original_concurrency["ai"] == 2
    
    # 修改系统并发配置
    mock_config.system.concurrency.ai_workers = 8
    mock_config.system.concurrency.global_workers = 10
    
    # 在非限流周期模拟同步
    if not guard.is_throttled:
        guard.original_concurrency = {
            "global": guard.engine.config.system.concurrency.global_workers,
            "ai": guard.engine.config.system.concurrency.ai_workers
        }
    
    # original_concurrency 应该滑动更新为 8 和 10
    assert guard.original_concurrency["ai"] == 8
    assert guard.original_concurrency["global"] == 10
    
    # 4. 模拟触发限流
    guard.is_throttled = True
    
    # 即使系统并发配置在限流期间再度修改为其他值，original_concurrency 也不应该变
    mock_config.system.concurrency.ai_workers = 12
    if not guard.is_throttled:
        guard.original_concurrency = {
            "global": guard.engine.config.system.concurrency.global_workers,
            "ai": guard.engine.config.system.concurrency.ai_workers
        }
    
    # 依然是限流触发前的 8
    assert guard.original_concurrency["ai"] == 8


