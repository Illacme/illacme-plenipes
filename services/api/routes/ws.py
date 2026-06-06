#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - WebSocket Control Plane
模块职责：提供全双工事件推送，将 EventBus 信号实时投射至 Dashboard。
🛡️ [V52.0]：商用级实时观测系统。
"""

import asyncio
import threading
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.utils.event_bus import bus
from core.utils.tracing import tlog
import json
import time

buffer_lock = threading.Lock()
message_buffer = [] # 最大容量 1000
global_msg_counter = 0
server_start_time = time.time()

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        tlog.info(f"🔌 [WS] 仪表盘已接入主权链路。在线席位: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            tlog.info(f"🔌 [WS] 仪表盘连接已断开。剩余席位: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        # 批量广播
        if not self.active_connections:
            return
        
        # 🚀 [V52.3] 增强型序列化：强制将无法识别的对象转为字符串，确保链路永不崩溃
        payload = json.dumps(message, default=str)
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# --- 🛰️ Event Bus Integration ---
_main_loop = None

def handle_bus_event(event_name, **kwargs):
    """EventBus 回调，通过线程安全方式中转至 WS 广播"""
    global _main_loop, global_msg_counter
    
    # 🚀 [V55.9] 物理脱敏：过滤掉无法序列化的复杂对象 (如 engine)
    safe_payload = {}
    for k, v in kwargs.items():
        if isinstance(v, (str, int, float, bool, list, dict, type(None))):
            safe_payload[k] = v
            
    with buffer_lock:
        global_msg_counter += 1
        msg_id = global_msg_counter
        payload = {
            "msg_id": msg_id,
            "type": event_name, # 🛡️ 强制使用正确的事件名称作为 WS 类型
            "timestamp": time.time(),
            "payload": safe_payload
        }
        message_buffer.append(payload)
        if len(message_buffer) > 1000:
            message_buffer.pop(0)
            
    if _main_loop and _main_loop.is_running():
        _main_loop.call_soon_threadsafe(
            lambda: asyncio.create_task(manager.broadcast(payload))
        )

# 🚀 [V55.9] 动态订阅引擎：确保每个信号都带着自己的身份标识
def bind_event(name):
    return lambda **kwargs: handle_bus_event(name, **kwargs)

# 订阅关键事件
bus.subscribe("AUDIT_LOG", bind_event("AUDIT_LOG"))
bus.subscribe("SYNC_STARTED", bind_event("SYNC_STARTED"))
bus.subscribe("SYNC_COMPLETED", bind_event("SYNC_COMPLETED"))
bus.subscribe("FILE_SYNCED", bind_event("FILE_SYNCED"))
bus.subscribe("HEALTH_UPDATE", bind_event("HEALTH_UPDATE"))
bus.subscribe("UI_PROGRESS_START", bind_event("UI_PROGRESS_START"))
bus.subscribe("UI_PROGRESS_ADVANCE", bind_event("UI_PROGRESS_ADVANCE"))
bus.subscribe("UI_PROGRESS_STOP", bind_event("UI_PROGRESS_STOP"))
bus.subscribe("UI_TERMINAL_DATA", bind_event("UI_TERMINAL_DATA"))
 # 🚀 [V55.9] 关键桥接：将终端日志信号投射至 WS 链路
bus.subscribe("KNOWLEDGE_BATCH_READY", bind_event("KNOWLEDGE_BATCH_READY"))
 # 🪐 [混合渐进式] AI 织网分批完成时推送增量星系数据至 Dashboard
bus.subscribe("UI_AI_BREAKER_TRIPPED", bind_event("UI_AI_BREAKER_TRIPPED"))


@router.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    global _main_loop
    _main_loop = asyncio.get_running_loop()
    
    # 解析 last_msg_id query 参数
    query_params = websocket.query_params
    last_msg_id_str = query_params.get("last_msg_id")
    
    await manager.connect(websocket)
    try:
        # 初始握手包
        await websocket.send_json({
            "type": "SYSTEM_CONNECTED",
            "message": "主权实时链路已建立",
            "timestamp": time.time(),
            "server_instance_id": server_start_time
        })
        
        # 执行离线消息重放
        if last_msg_id_str:
            try:
                last_id = int(last_msg_id_str)
                with buffer_lock:
                    replay_msgs = [msg for msg in message_buffer if msg["msg_id"] > last_id]
                if replay_msgs:
                    tlog.info(f"🔄 [WS] 正在为重连链路重放 {len(replay_msgs)} 条离线消息...")
                    await websocket.send_json({
                        "type": "REPLAY_EVENTS",
                        "events": replay_msgs,
                        "timestamp": time.time()
                    })
            except ValueError:
                pass
        
        while True:
            # 保持连接，监听客户端消息（如指令）
            await websocket.receive_text()
            # 目前仅作为心跳/保持
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        tlog.error(f"❌ [WS] 链路异常: {e}")
        manager.disconnect(websocket)
