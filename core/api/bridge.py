#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Event Streaming Bridge
模块职责：将内部 EventBus 信号桥接至外部消费队列（如 SSE/WebSockets）。
🚀 [V14.0] 观测性基座：实现引擎运行状态的实时外溢。
"""

import queue
import json
import threading
from core.utils.event_bus import bus

class EventBridge:
    """事件桥接器：订阅总线并将信号转存至线程安全队列"""
    def __init__(self, max_size=1000):
        self.queue = queue.Queue(maxsize=max_size)
        self._is_active = False

    def start(self):
        """激活全量订阅"""
        if self._is_active: return

        # 订阅所有关键 UI 信号
        bus.subscribe("UI_PROGRESS_ADVANCE", self._on_event("progress_advance"))
        bus.subscribe("UI_PROGRESS_START", self._on_event("progress_start"))
        bus.subscribe("UI_PROGRESS_STOP", self._on_event("progress_stop"))
        bus.subscribe("UI_ERROR", self._on_event("error"))
        bus.subscribe("SYNC_COMPLETED", self._on_event("sync_completed"))
        bus.subscribe("ENGINE_STARTED", self._on_event("engine_started"))

        # 🚀 [V11.0] 算力与思维链追踪订阅
        bus.subscribe("AI_CALL_COMPLETED", self._on_event("ai_call"))
        bus.subscribe("AI_REASONING_FRAGMENT", self._on_event("ai_reasoning"))
        bus.subscribe("SYNC_DOC_START", self._on_event("doc_start"))

        self._is_active = True

    def _on_event(self, event_type):
        def wrapper(*args, **kwargs):
            payload = {
                "type": event_type,
                "data": kwargs if kwargs else (args[0] if args else {})
            }
            try:
                self.queue.put_nowait(payload)
            except queue.Full:
                # 溢出保护：丢弃最旧的事件
                try: self.queue.get_nowait()
                except queue.Empty: pass
                self.queue.put_nowait(payload)
        return wrapper

    def stream(self):
        """生成器：供 FastAPI SSE 消费"""
        while True:
            event = self.queue.get()
            yield f"data: {json.dumps(event)}\n\n"

# 全局单例桥接器
global_bridge = EventBridge()
