#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Tracing Utility
模块职责：全链路可观测性中枢。
提供 Trace-ID (ael_iter_id) 的生成、传递与结构化日志修饰功能。
🛡️ [AEL-Iter-v10.0]：让每一颗算力原子都清晰可见。
"""
import uuid
import contextvars
import re
import logging
import threading
from threading import Lock
import functools
import json
import time
from datetime import datetime
from typing import Optional, Callable, Any
from contextvars import ContextVar

# 使用 contextvars 确保 Trace-ID 和元数据在协程/线程间安全传递
_trace_id_ctx = contextvars.ContextVar("ael_iter_id", default=None)
_trace_metadata_ctx = contextvars.ContextVar("ael_trace_metadata", default={})

logger = logging.getLogger("Illacme.plenipes")
logger.propagate = False # 🛡️ [V16.6] 防止日志冒泡导致控制台双重打印

def setup_file_logging(log_dir: str, level=logging.INFO):
    """🚀 [V34.9] 工业级日志持久化：配置滚动日志文件"""
    import os
    from logging.handlers import RotatingFileHandler

    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "plenipes.log")

    # 🛡️ 保持 7 个历史版本，每个文件最大 10MB
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=7,
        encoding="utf-8"
    )

    # 格式化：时间 [TraceID] 等级 - 消息
    formatter = logging.Formatter('%(asctime)s %(message)s')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # 挂载到主日志器
    logger.addHandler(file_handler)
    logger.info(f"📁 [日志中枢] 物理持久化已激活: {log_file}")

# 🚀 [V16.6] 日志中枢原子化适配
_CONSOLE_OUTPUT = None
_LOG_HISTORY = {} # msg -> last_time
_LOG_LOCK = Lock()

def set_tlog_console(console):
    """🛡️ 注册物理控制台，实现日志与进度条的共生渲染"""
    global _CONSOLE_OUTPUT
    _CONSOLE_OUTPUT = console

def tlog_info(msg): emit_tlog(msg, "INFO")
def tlog_warn(msg): emit_tlog(msg, "WARNING")
def tlog_error(msg): emit_tlog(msg, "ERROR")

def emit_tlog(msg, level="INFO"):
    """
    [AEL-Iter-v16.7] 工业级审计追踪
    支持基于全局日志级别 (Log Level) 的物理过滤，杜绝调试信息干扰生产环境。
    """
    global _CONSOLE_OUTPUT
    
    # 🚀 [V16.7] 接入标准 logging 级别映射，执行物理过滤
    level_num = getattr(logging, level.upper(), logging.INFO)
    if level_num < logger.getEffectiveLevel():
        return

    now = time.time()
    timestamp_str = time.strftime('%H:%M:%S')
    
    # 🚀 [去重策略] 针对物理消息执行 1.0s 窗口内的原子级拦截
    with _LOG_LOCK:
        last_time = _LOG_HISTORY.get(msg, 0)
        if now - last_time < 1.0:
            return
        _LOG_HISTORY[msg] = now

    # 🚀 [双轨分流]
    # 1. UI 轨道：由 Rich 或标准 print 接管，负责视觉反馈
    if _CONSOLE_OUTPUT:
        style = "green" if level == "INFO" else "yellow" if level == "WARNING" else "bold red"
        _CONSOLE_OUTPUT.print(f"[{timestamp_str}] {level}: {msg}", style=style)
    else:
        # 🛡️ 备选：非交互模式下直接输出，确保日志可见
        print(f"[{timestamp_str}] {level}: {msg}")

    # 2. 持久化轨道：由标准 logging 接管，负责写入文件
    # ⚠️ 注意：不要直接调用 tlog.info，否则会引发无限递归！
    # 直接操作底层的 logger (logging.Logger 实例)
    if level == "INFO": logger.info(msg)
    elif level == "WARNING": logger.warning(msg)
    elif level == "ERROR": logger.error(msg)

def SovereignCore(func):
    """
    🚀 [V11.6] 主权核心装饰器 (Interface Locking)
    标记该方法为项目最高等级核心逻辑。
    任何对带此标记的方法的签名修改、返回值变更或核心逻辑重构，必须经过物理复核。
    """
    func._is_sovereign_core = True
    return func

class Tracer:
    @staticmethod
    def generate_id() -> str:
        """生成一个新的物理追踪 ID"""
        return str(uuid.uuid4())[:8]

    @staticmethod
    def set_id(trace_id: str):
        """显式设置当前上下文的 Trace-ID"""
        _trace_id_ctx.set(trace_id)

    @staticmethod
    def get_id() -> Optional[str]:
        """获取当前上下文的 Trace-ID"""
        return _trace_id_ctx.get()

    @staticmethod
    def format_msg(msg: str) -> str:
        """为日志消息注入 Trace-ID 装饰器"""
        tid = Tracer.get_id() or "Main"
        return f"[{tid}] {msg}"

    @staticmethod
    def trace_context(trace_id: str, metadata: dict = None):
        """
        装饰器：在函数执行期间锁定 Trace-ID 和初始元数据。
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                token_id = _trace_id_ctx.set(trace_id)
                token_meta = _trace_metadata_ctx.set(metadata or {})
                try:
                    return func(*args, **kwargs)
                finally:
                    _trace_id_ctx.reset(token_id)
                    _trace_metadata_ctx.reset(token_meta)
            return wrapper
        return decorator

    @staticmethod
    def add_metadata(key: str, value: Any):
        """🚀 [V11.0] 动态注入当前上下文的业务元数据 (如 AI 思维片段)"""
        meta = _trace_metadata_ctx.get().copy()
        meta[key] = value
        _trace_metadata_ctx.set(meta)

    @staticmethod
    def get_metadata() -> dict:
        """获取当前上下文的所有元数据"""
        return _trace_metadata_ctx.get()

    @staticmethod
    def trace_scope(trace_id: str):
        """
        上下文管理器：用于 with 语句。
        with Tracer.trace_scope(id):
            ...
        """
        class TraceScope:
            def __init__(self, tid):
                self.tid = tid
                self.token = None
            def __enter__(self):
                self.token = _trace_id_ctx.set(self.tid)
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                _trace_id_ctx.reset(self.token)
        return TraceScope(trace_id)

class TracedLogger:
    """包装原始 Logger，自动注入 Trace-ID 并保持协议兼容，同时支持 Rich 渲染与去重"""
    def __init__(self, name: str):
        self._logger = logging.getLogger(name)

    def __getattr__(self, name):
        return getattr(self._logger, name)

    def _wrap_msg(self, msg):
        return Tracer.format_msg(msg)

    def info(self, msg, *args, **kwargs):
        emit_tlog(self._wrap_msg(msg), "INFO")

    def debug(self, msg, *args, **kwargs):
        emit_tlog(self._wrap_msg(msg), "DEBUG")

    def warning(self, msg, *args, **kwargs):
        emit_tlog(self._wrap_msg(msg), "WARNING")

    def error(self, msg, *args, **kwargs):
        emit_tlog(self._wrap_msg(msg), "ERROR")

    def critical(self, msg, *args, **kwargs):
        emit_tlog(self._wrap_msg(msg), "CRITICAL")

    def exception(self, msg, *args, **kwargs):
        # 🚀 [V16.6] 异常需要特殊处理以保留堆栈信息
        import traceback
        error_msg = f"{msg}\n{traceback.format_exc()}"
        emit_tlog(self._wrap_msg(error_msg), "ERROR")

# 🚀 预定义的全局追踪日志器
tlog = TracedLogger("Illacme.plenipes")

class JsonFormatter(logging.Formatter):
    """🚀 [V10.1] 结构化日志格式化器"""
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "trace_id": Tracer.get_id() or "AEL-ROOT",
            "metadata": Tracer.get_metadata(),
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)
