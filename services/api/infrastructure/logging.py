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


def setup_api_logging(logger_name: str = "uvicorn.access") -> None:
    """
    初始化并配置 API 访问日志过滤器。
    
    Args:
        logger_name: 目标日志记录器名称，默认为 uvicorn 访问日志。
    """
    logger = logging.getLogger(logger_name)
    if not any(isinstance(f, HeartbeatFilter) for f in logger.filters):
        logger.addFilter(HeartbeatFilter())
