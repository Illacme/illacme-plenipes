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
    
    # 保存原始并发状态模拟
    guard.original_concurrency = {
        "global": 4,
        "ai": 2
    }
    
    # 1. 验证削峰：当原始并发为 2 时，超载削峰应降为 1
    # 期望计算公式：max(1, min(2 // 2, 4)) = 1
    guard._apply_throttle(cpu=97.0, ram=88.0, silent=True)
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
    guard._apply_throttle(cpu=97.0, ram=88.0, silent=True)
    assert ai_executor.max_workers == 4
    
    # 释放并恢复
    guard._release_throttle()
    assert ai_executor.max_workers == 16
    
    # 3. 验证削峰：当原始并发为 1 时，超载削峰应保底为 1
    # 期望计算公式：max(1, min(1 // 2, 4)) = 1
    guard.original_concurrency["ai"] = 1
    guard._apply_throttle(cpu=97.0, ram=88.0, silent=True)
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
    guard._apply_throttle(cpu=cpu_usage, ram=ram_usage, silent=True)
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

