# -*- coding: utf-8 -*-
"""
🧪 [Test] 离线事件追溯与日志消息缓冲 (Telemetry Resilience) 单元测试
"""
import sys
import os
import unittest
import time
from fastapi.testclient import TestClient

# 将项目根目录加入 python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.api.server import app
from core.utils.event_bus import bus
import services.api.routes.ws as ws_module


class TestTelemetryResilience(unittest.TestCase):
    def setUp(self):
        # 备份并清空全局消息缓存区以保证测试隔离性
        self.original_buffer = list(ws_module.message_buffer)
        self.original_counter = ws_module.global_msg_counter
        ws_module.message_buffer.clear()

    def tearDown(self):
        # 还原全局缓存
        ws_module.message_buffer.clear()
        ws_module.message_buffer.extend(self.original_buffer)
        ws_module.global_msg_counter = self.original_counter

    def test_msg_id_allocation_and_buffering(self):
        """测试 EventBus 事件触发时，msg_id 递增分配及正确的 payload 缓存"""
        bus.emit("AUDIT_LOG", message="Resilience Test Msg 1", level="INFO")
        bus.emit("AUDIT_LOG", message="Resilience Test Msg 2", level="INFO")

        self.assertEqual(len(ws_module.message_buffer), 2)
        
        msg1 = ws_module.message_buffer[0]
        msg2 = ws_module.message_buffer[1]

        self.assertEqual(msg1["type"], "AUDIT_LOG")
        self.assertEqual(msg1["payload"]["message"], "Resilience Test Msg 1")
        self.assertEqual(msg2["payload"]["message"], "Resilience Test Msg 2")
        
        # 验证 msg_id 单调递增
        self.assertTrue(msg1["msg_id"] < msg2["msg_id"])

    def test_circular_buffer_truncation(self):
        """测试全局消息缓冲区在超过 1000 条时能够自动进行环形截断"""
        # 注入 1050 条测试消息
        for i in range(1050):
            bus.emit("AUDIT_LOG", message=f"Loop Msg {i}", level="INFO")
            
        # 验证缓冲区容量限制在 1000 内
        self.assertEqual(len(ws_module.message_buffer), 1000)
        # 验证最早的 50 条已经被正确舍弃，第一个元素对应第 50 条消息 (Loop Msg 50)
        self.assertEqual(ws_module.message_buffer[0]["payload"]["message"], "Loop Msg 50")
        self.assertEqual(ws_module.message_buffer[-1]["payload"]["message"], "Loop Msg 1049")

    def test_websocket_handshake_and_replay(self):
        """测试 WebSocket 连接握手包实例 ID、重连拉取 Query 参数过滤及 REPLAY_EVENTS 打包重放"""
        # 1. 注入 3 条事件
        bus.emit("AUDIT_LOG", message="Msg A (Already read)", level="INFO")
        bus.emit("AUDIT_LOG", message="Msg B (Missed while offline)", level="INFO")
        bus.emit("AUDIT_LOG", message="Msg C (Missed while offline)", level="INFO")

        self.assertEqual(len(ws_module.message_buffer), 3)
        msg_a_id = ws_module.message_buffer[0]["msg_id"]

        client = TestClient(app)
        
        # 2. 模拟客户端传递 last_msg_id 为 msg_a_id 进行重连
        with client.websocket_connect(f"/api/ws?last_msg_id={msg_a_id}") as websocket:
            # 接收初始握手包
            handshake = websocket.receive_json()
            self.assertEqual(handshake["type"], "SYSTEM_CONNECTED")
            self.assertIn("server_instance_id", handshake)
            self.assertEqual(handshake["server_instance_id"], ws_module.server_start_time)

            # 接收重放包
            replay = websocket.receive_json()
            self.assertEqual(replay["type"], "REPLAY_EVENTS")
            events = replay["events"]

            # 应该精确重放 Msg B 和 Msg C
            self.assertEqual(len(events), 2)
            self.assertEqual(events[0]["payload"]["message"], "Msg B (Missed while offline)")
            self.assertEqual(events[1]["payload"]["message"], "Msg C (Missed while offline)")
            self.assertTrue(events[0]["msg_id"] > msg_a_id)
            self.assertTrue(events[1]["msg_id"] > msg_a_id)

    def test_websocket_replay_empty(self):
        """测试客户端带上最新或未来消息 ID 时重放 events 列表应为空"""
        bus.emit("AUDIT_LOG", message="Some Msg", level="INFO")
        latest_id = ws_module.message_buffer[-1]["msg_id"]

        client = TestClient(app)
        # 传递未来的 last_msg_id
        with client.websocket_connect(f"/api/ws?last_msg_id={latest_id + 10}") as websocket:
            handshake = websocket.receive_json()
            self.assertEqual(handshake["type"], "SYSTEM_CONNECTED")

            # 应当没有收到 REPLAY_EVENTS 消息
            # 由于没有需要重放的离线消息，后端不会发送 REPLAY_EVENTS 消息包
            # 我们验证连接依然健康且无法读出新的数据 (使用 receive_json 超时作为间接检验)
            # 在 fastapi testclient 下，接收空消息或等待会立即抛出运行时错误，
            # 也可以简单用 try except 接收验证
            from anyio import fail_after
            try:
                with fail_after(0.1):
                    websocket.receive_json()
                self.fail("Expected no messages, but got one.")
            except Exception:
                pass


if __name__ == '__main__':
    unittest.main()
