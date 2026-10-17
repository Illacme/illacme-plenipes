# -*- coding: utf-8 -*-
"""
⚙️ Illacme API Infrastructure - Logging (日志基础设施)
职责：提供 API 层的日志增强与流量过滤功能。
🛡️ [V50.5]：实现静默心跳过滤，确保终端输出的主权整洁。
"""

import logging

class HeartbeatFilter(logging.Filter):
    """🚀 静默心跳过滤器：物理过滤掉高频的系统同步/状态轮询与心跳日志"""
    
    IGNORED_ENDPOINTS = (
        "/health",
        "/api/system/health",
        "/api/system/sync/status",
        "/api/system/preview/status",
        "/api/system/update/progress",
        "/api/system/check_update",
        "/api/system/stats",
        "/api/system/health/matrix",
        "/api/system/context",
        "/api/imprints",
        "/api/billing/stats",
        "/api/galaxy/graph",
        "/api/translation/review",
        "/api/dispatch/overview",
    )

    def filter(self, record: logging.LogRecord) -> bool:
        """
        执行日志过滤判定。
        
        Args:
            record: 待处理的日志记录
            
        Returns:
            bool: 是否允许该日志记录通过
        """
        # 1. 优先从 uvicorn access log 的 record.args 中快速匹配 URL 路径
        if record.args and len(record.args) >= 3 and isinstance(record.args[2], str):
            path = record.args[2]
            if any(endpoint in path for endpoint in self.IGNORED_ENDPOINTS):
                return False

        # 2. 兜底回退匹配完整格式化消息文本
        msg = record.getMessage()
        return not any(endpoint in msg for endpoint in self.IGNORED_ENDPOINTS)


class WebSocketNoiseFilter(logging.Filter):
    """🚀 过滤底层 WebSocket 握手与连接生命周期日志"""
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        if "WebSocket" in msg and "[accepted]" in msg:
            return False
        if msg in ("connection open", "connection closed"):
            return False
        return True


def setup_api_logging(logger_name: str = "uvicorn.access") -> None:
    """
    初始化并配置 API 访问日志与 WebSocket 握手静默过滤器。
    
    Args:
        logger_name: 目标日志记录器名称，默认为 uvicorn 访问日志。
    """
    logger = logging.getLogger(logger_name)
    if not any(isinstance(f, HeartbeatFilter) for f in logger.filters):
        logger.addFilter(HeartbeatFilter())

    # 静默底层 websockets 库的 connection open/closed 冗余信息
    for ws_log_name in ("websockets.server", "websockets.protocol", "websockets"):
        ws_log = logging.getLogger(ws_log_name)
        ws_log.setLevel(logging.WARNING)

    # 静默 uvicorn.error 上的 WebSocket [accepted] 握手日志
    uvicorn_err = logging.getLogger("uvicorn.error")
    if not any(isinstance(f, WebSocketNoiseFilter) for f in uvicorn_err.filters):
        uvicorn_err.addFilter(WebSocketNoiseFilter())
