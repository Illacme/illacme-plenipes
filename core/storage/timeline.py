#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Timeline Manager
模块职责：记录物理与语义事件的审计时间轴。
提供异步落盘与自动化 Markdown 报表导出能力。
"""

import os
import time
import json
import logging
import threading
from datetime import datetime
from typing import Dict, List, Any

from core.utils.tracing import tlog

class TimelineManager:
    """审计时间轴管理器：掌管创作历史的物理留档"""
    def __init__(self, engine):
        self.engine = engine
        self.cfg = engine.config.timeline
        self.json_path = os.path.abspath(os.path.expanduser(self.cfg.json_path))
        self.markdown_path = os.path.abspath(os.path.expanduser(self.cfg.markdown_path))
        self.max_entries = self.cfg.max_entries

        self.lock = threading.Lock()
        self.events = self._load_events()
        self._dirty = False

        if self.cfg.enabled:
            # 开启异步落盘线程
            self._stop_event = threading.Event()
            self._flusher_thread = threading.Thread(target=self._auto_flush_worker, daemon=True)
            self._flusher_thread.start()

    def _load_events(self) -> List[Dict[str, Any]]:
        """初始化加载历史记录"""
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data if isinstance(data, list) else []
            except Exception as e:
                tlog.warning(f"⚠️ 无法加载历史时间轴数据: {e}")
        return []

    def log_event(self, event_type: str, rel_path: str, status: str = "PENDING", details: str = ""):
        """记录一个新事件"""
        if not self.cfg.enabled:
            return

        with self.lock:
            event = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": time.time(),
                "type": event_type,
                "path": rel_path,
                "status": status,
                "details": details
            }
            self.events.insert(0, event)
            # 维持记录上限
            if len(self.events) > self.max_entries:
                self.events = self.events[:self.max_entries]
            self._dirty = True

    def update_event_status(self, rel_path: str, status: str, details: str = ""):
        """更新最近一次相关路径事件的状态"""
        if not self.cfg.enabled:
            return

        with self.lock:
            for event in self.events:
                if event.get("path") == rel_path and event.get("status") == "PENDING":
                    event["status"] = status
                    if details:
                        event["details"] = details
                    self._dirty = True
                    break

    def _auto_flush_worker(self):
        """异步写盘线程"""
        while not self._stop_event.is_set():
            # 🚀 [V15.8] 使用配置定义的节流延迟
            time.sleep(self.engine.config.system.throttle.timeline_write_delay)
            if self._dirty:
                self.flush()

    def flush(self):
        """执行物理落盘与 Markdown 导出"""
        with self.lock:
            if not self._dirty:
                return
            events_copy = list(self.events)
            self._dirty = False

        try:
            # 1. 写入 JSON
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(events_copy, f, indent=2, ensure_ascii=False)

            # 2. 导出 Markdown
            self._export_markdown(events_copy)
        except Exception as e:
            tlog.error(f"🛑 审计时间轴落盘失败: {e}")

    def _export_markdown(self, events: List[Dict[str, Any]]):
        """生成用户友好的 Markdown 时间轴展示"""
        lines = [
            "# 📝 Illacme-plenipes 创作审计时间轴",
            f"\n> 最后更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n| 发生时间 | 操作路径 | 事件类型 | 执行状态 | 备注 |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ]

        # 只取最近 100 条显示在 Markdown 中
        for ev in events[:100]:
            ev_status = ev.get('status', 'UNKNOWN')
            status_ico = "✅" if ev_status in ['UPDATED', 'SYNCED', 'SKIP'] else "🛑" if ev_status == 'ERROR' else "🔄"
            lines.append(f"| {ev.get('time', '')} | `{ev.get('path', '')}` | **{ev.get('type', '')}** | {status_ico} {ev_status} | {ev.get('details', '')} |")

        with open(self.markdown_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

    def stop(self):
        """注销服务"""
        if self.cfg.enabled:
            self._stop_event.set()
            self.flush()
