#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Internal Event Bus
模块职责：提供轻量级的事件发布/订阅机制，支持组件间的零耦合通信。
🛡️ [AEL-Iter-v7.1]：事件驱动架构基座。
"""
import logging
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from threading import Lock

from core.utils.tracing import tlog

@dataclass
class Event:
    type: str
    data: Dict[str, Any]

class EventBus:
    """🚀 核心事件总线 (Singleton)"""
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EventBus, cls).__new__(cls)
                cls._instance._subscribers: Dict[str, List[Callable]] = {}
        return cls._instance

    def subscribe(self, event_type: str, callback: Callable):
        """订阅事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)
            tlog.debug(f"👂 [事件总线] 已增加订阅者: {callback.__name__} -> {event_type}")

    def on(self, event_type: str):
        """装饰器：订阅事件"""
        def decorator(callback: Callable):
            self.subscribe(event_type, callback)
            return callback
        return decorator

    def emit(self, event_type: str, **kwargs):
        """发布事件"""
        if event_type not in self._subscribers:
            return

        tlog.debug(f"📢 [事件总线] 发布事件: {event_type}")

        for callback in self._subscribers[event_type]:
            try:
                callback(**kwargs)
            except Exception as e:
                tlog.error(f"❌ [事件总线] 订阅者 {callback.__name__} 处理事件 {event_type} 失败: {e}")

# 全局访问点
bus = EventBus()
