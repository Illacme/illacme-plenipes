# -*- coding: utf-8 -*-
"""
⚙️ Illacme API Infrastructure - Logging (日志基础设施)
职责：提供 API 层的日志增强与流量过滤功能。
🛡️ [V50.5]：实现静默心跳过滤，确保终端输出的主权整洁。
"""

import logging

class HeartbeatFilter(logging.Filter):
    """🚀 静默心跳过滤器：物理过滤掉高频的同步请求日志"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        执行日志过滤判定。
        
        Args:
            record: 待处理的日志记录
            
        Returns:
            bool: 是否允许该日志记录通过
        """
        msg = record.getMessage()
        # 屏蔽仪表盘的高频数据轮询与心跳日志，防止污染控制台
        ignored_endpoints = [
            "/health",
            "/api/system/health",
            "/api/system/stats",
            "/api/system/health/matrix",
            "/api/system/context",
            "/api/imprints",
            "/api/billing/stats",
            "/api/galaxy/graph"
        ]
        return not any(endpoint in msg for endpoint in ignored_endpoints)

def setup_api_logging(logger_name: str = "uvicorn.access") -> None:
    """
    初始化并配置 API 访问日志过滤器。
    
    Args:
        logger_name: 目标日志记录器名称，默认为 uvicorn 访问日志。
    """
    logger = logging.getLogger(logger_name)
    logger.addFilter(HeartbeatFilter())
