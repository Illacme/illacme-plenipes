#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 [Test] 遥测心跳历史物理持久化与冷启动数据继承防灾自愈测试
职责：全面覆盖 HeartbeatService 的历史点扩容、冷启动物理加载以及文件破损防灾等边界情况。
"""

import sys
import os
import tempfile
import json

# 将项目根目录加入 python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.governance.heartbeat import HeartbeatService

class MockConfig:
    def __init__(self, pulse_path: str):
        self._pulse_path = pulse_path
        self.active_theme = "sovereign"

    def get_pulse_path(self) -> str:
        return self._pulse_path

class MockEngine:
    def __init__(self, pulse_path: str):
        self.config = MockConfig(pulse_path)

    def _resolve_path(self, path: str) -> str:
        return path

def test_heartbeat_no_history():
    """测试无历史物理文件时，默认初始化为 150 个 0.0"""
    with tempfile.TemporaryDirectory() as temp_dir:
        pulse_path = os.path.join(temp_dir, "pulse_nonexistent.json")
        engine = MockEngine(pulse_path)
        
        service = HeartbeatService(engine)
        
        assert service.history_limit == 150
        assert len(service.history_cpu) == 150
        assert service.history_cpu == [0.0] * 150
        assert service.history_mem == [0.0] * 150

def test_heartbeat_corrupt_history():
    """测试物理文件损坏或非合法 JSON 时，系统防灾自愈，以全 0 初始化，且不崩溃"""
    with tempfile.TemporaryDirectory() as temp_dir:
        pulse_path = os.path.join(temp_dir, "pulse_corrupt.json")
        with open(pulse_path, 'w', encoding='utf-8') as f:
            f.write("{invalid_json: null,}")  # 写入非法的 JSON 文本
            
        engine = MockEngine(pulse_path)
        service = HeartbeatService(engine)
        
        assert service.history_limit == 150
        assert len(service.history_cpu) == 150
        assert service.history_cpu == [0.0] * 150

def test_heartbeat_restore_history_partial():
    """测试物理文件存在且有部分较短的历史数据时，系统成功反序列化并高位补齐 0.0"""
    with tempfile.TemporaryDirectory() as temp_dir:
        pulse_path = os.path.join(temp_dir, "pulse_partial.json")
        
        mock_data = {
            "history": {
                "cpu": [10.0, 20.0],
                "memory": [30.0, 40.0],
                "compute_memory": [50.0, 60.0],
                "tokens_rate": [5.0, 10.0],
                "active_workers": [1.0, 2.0]
            }
        }
        with open(pulse_path, 'w', encoding='utf-8') as f:
            json.dump(mock_data, f)
            
        engine = MockEngine(pulse_path)
        service = HeartbeatService(engine)
        
        assert service.history_limit == 150
        assert len(service.history_cpu) == 150
        # 验证前 148 项补 0.0，后两项成功继承
        assert service.history_cpu[:148] == [0.0] * 148
        assert service.history_cpu[-2:] == [10.0, 20.0]
        
        assert service.history_mem[-2:] == [30.0, 40.0]
        assert service.history_comp[-2:] == [50.0, 60.0]
        assert service.history_tokens_rate[-2:] == [5.0, 10.0]
        assert service.history_active_workers[-2:] == [1.0, 2.0]

def test_heartbeat_restore_and_truncate():
    """测试物理文件中的历史数据超过 150 项时，成功反序列化并裁剪保留最后的 150 项"""
    with tempfile.TemporaryDirectory() as temp_dir:
        pulse_path = os.path.join(temp_dir, "pulse_long.json")
        
        long_cpu = list(range(1, 201))  # 200 个点
        mock_data = {
            "history": {
                "cpu": long_cpu,
                "memory": [80.0] * 200,
                "compute_memory": [0.0] * 200,
                "tokens_rate": [0.0] * 200,
                "active_workers": [0.0] * 200
            }
        }
        with open(pulse_path, 'w', encoding='utf-8') as f:
            json.dump(mock_data, f)
            
        engine = MockEngine(pulse_path)
        service = HeartbeatService(engine)
        
        assert service.history_limit == 150
        assert len(service.history_cpu) == 150
        # 验证裁剪保留最后的 150 项，即 51 到 200
        assert service.history_cpu == list(range(51, 201))

def test_heartbeat_adaptive_coalescing():
    """测试心跳服务自适应物理写盘的降频节流机制"""
    import time
    with tempfile.TemporaryDirectory() as temp_dir:
        pulse_path = os.path.join(temp_dir, "pulse_adaptive.json")
        engine = MockEngine(pulse_path)
        service = HeartbeatService(engine)
        service._gather_pulse = lambda: {}
        
        # 1. 模拟活跃（Busy）状态：CPU > 5% 
        service.history_cpu[-1] = 12.0
        service.history_active_workers[-1] = 0.0
        
        # 第一次写入，last_write_time 初始化为 0.0，必然写入
        service._pulse_step()
        assert os.path.exists(pulse_path)
        assert service.last_write_time > 0.0
        
        t1 = service.last_write_time
        os.remove(pulse_path)
        
        # 依然活跃状态
        service._pulse_step()
        assert os.path.exists(pulse_path)
        t2 = service.last_write_time
        assert t2 >= t1 # 即时写入
        
        # 2. 模拟闲置（Idle）状态：CPU < 5%，Active Workers = 0
        service.history_cpu[-1] = 2.0
        service.history_active_workers[-1] = 0.0
        
        # 删除物理文件
        os.remove(pulse_path)
        
        # 闲置状态，且距离上一次写入小于 10 秒，应该跳过落盘，即文件不会被创建
        service._pulse_step()
        assert not os.path.exists(pulse_path)
        
        # 3. 模拟闲置状态下，时间跨度超过 10 秒后，应该再次触发物理写入
        service.last_write_time = time.time() - 11.0 # 强制调整上次写入时间至 11 秒前
        service._pulse_step()
        assert os.path.exists(pulse_path)

def test_heartbeat_dynamic_history_limit():
    """测试在配置中动态调小/调大 telemetry_history_limit 时，心跳内存时序自动缩放且不崩溃"""
    class DynamicSystemConfig:
        def __init__(self):
            self.telemetry_history_limit = 150

    class DynamicConfig:
        def __init__(self, p_path):
            self.system = DynamicSystemConfig()
            self.active_theme = "sovereign"
            self._pulse_path = p_path
        
        def get_pulse_path(self):
            return self._pulse_path

    class DynamicEngine:
        def __init__(self, p_path):
            self.config = DynamicConfig(p_path)
            
        def _resolve_path(self, path):
            return path

    with tempfile.TemporaryDirectory() as temp_dir:
        pulse_path = os.path.join(temp_dir, "pulse_dynamic.json")
        engine = DynamicEngine(pulse_path)
        
        # 使用动态 Mock 引擎创建心跳服务
        service = HeartbeatService(engine)
        service._gather_pulse = lambda: {} # mock 掉防止影响 history_cpu
        
        # 初始应为 150 限制，时序长度均为 150
        assert service.history_limit == 150
        assert len(service.history_cpu) == 150
        
        # 填充一些值
        for i in range(150):
            service.history_cpu[i] = float(i)
            
        # 1. 模拟动态调小为 50 点
        engine.config.system.telemetry_history_limit = 50
        service._pulse_step()
        
        # 时序应自适应截断为 50，且保留最后的 50 个元素（即 100 到 149）
        assert service.history_limit == 50
        assert len(service.history_cpu) == 50
        assert service.history_cpu == [float(x) for x in range(100, 150)]
        
        # 2. 模拟动态调大为 80 点
        engine.config.system.telemetry_history_limit = 80
        service._pulse_step()
        
        # 时序应高位补零扩容为 80 个元素，前 30 个为 0.0，后 50 个为 100-149
        assert service.history_limit == 80
        assert len(service.history_cpu) == 80
        assert service.history_cpu[:30] == [0.0] * 30
        assert service.history_cpu[-50:] == [float(x) for x in range(100, 150)]

def test_heartbeat_archive_downsampling():
    """测试时序数据降采样缓冲区累加、计算均值晋升归档以及强制写盘的闭环自愈表现"""
    import time
    class DynamicSystemConfig:
        def __init__(self):
            self.telemetry_history_limit = 10
            self.telemetry_archive_interval_seconds = 6 # 6秒归档一次，相当于 3 次 tick (6s/2s)
            self.telemetry_archive_limit = 5

    class DynamicConfig:
        def __init__(self, p_path):
            self.system = DynamicSystemConfig()
            self.active_theme = "sovereign"
            self._pulse_path = p_path
        
        def get_pulse_path(self):
            return self._pulse_path

    class DynamicEngine:
        def __init__(self, p_path):
            self.config = DynamicConfig(p_path)
            
        def _resolve_path(self, path):
            return path

    with tempfile.TemporaryDirectory() as temp_dir:
        pulse_path = os.path.join(temp_dir, "pulse_archive.json")
        engine = DynamicEngine(pulse_path)
        
        service = HeartbeatService(engine)
        service.history_cpu = [0.0] * 10
        service.history_active_workers = [0.0] * 10
        
        # 1. 模拟多次 tick 采集以累加缓冲区
        # 第一次 tick：填充负载为 10.0，不触发归档，计数器为 1
        service._gather_pulse = lambda: {
            "history": {
                "cpu": [10.0],
                "memory": [20.0],
                "compute_memory": [5.0],
                "tokens_rate": [100.0],
                "active_workers": [1.0]
            }
        }
        # 手动塞进高精度时序中，以便 _pulse_step 抓取最新值
        service.history_cpu[-1] = 10.0
        service.history_mem[-1] = 20.0
        service.history_comp[-1] = 5.0
        service.history_tokens_rate[-1] = 100.0
        service.history_active_workers[-1] = 1.0
        
        service._pulse_step()
        assert service.tick_counter == 1
        assert service.archive_buffer_cpu == [10.0]
        
        # 第二次 tick
        service.history_cpu[-1] = 20.0
        service.history_mem[-1] = 30.0
        service.history_comp[-1] = 15.0
        service.history_tokens_rate[-1] = 200.0
        service.history_active_workers[-1] = 3.0
        
        service._pulse_step()
        assert service.tick_counter == 2
        assert service.archive_buffer_cpu == [10.0, 20.0]
        
        # 第三次 tick：触发归档 (ticks_needed = 6s/2s = 3)，计数器重置为 0
        service.history_cpu[-1] = 30.0
        service.history_mem[-1] = 40.0
        service.history_comp[-1] = 25.0
        service.history_tokens_rate[-1] = 300.0
        service.history_active_workers[-1] = 5.0
        
        # 清除刚才产生的物理文件以验证归档强落盘
        if os.path.exists(pulse_path):
            os.remove(pulse_path)
            
        # 模拟系统闲置状态，看是否能被强制落盘无视 10s idle 限制
        service.history_cpu[-1] = 1.0 # 强制设置低于 5%
        service.history_active_workers[-1] = 0.0
        service.last_write_time = time.time() # 设定 0 秒前才写过，如果非强落盘必定被 skip
        
        service._pulse_step()
        
        # 检查计数器是否重置，缓冲区是否清空
        assert service.tick_counter == 0
        assert len(service.archive_buffer_cpu) == 0
        
        # 检查归档时序最后一位是否是前三次 tick 负载的均值：
        # cpu 均值 = (10 + 20 + 1) / 3 = 10.333333333333334
        # mem 均值 = (20 + 30 + 40) / 3 = 30.0
        assert abs(service.history_archive_cpu[-1] - 10.333) < 0.01
        assert service.history_archive_mem[-1] == 30.0
        
        # 验证归档触发了强制物理落盘
        assert os.path.exists(pulse_path)
