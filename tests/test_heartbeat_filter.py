# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Heartbeat Filter Test Suite
验证心跳与轮询日志过滤器的有效性，确保高频请求不污染控制台且不误伤普通业务接口。
"""

import logging
from services.api.infrastructure.logging import HeartbeatFilter

def test_heartbeat_filter_blocks_polling_endpoints():
    """断言心跳与轮询日志被静默过滤"""
    h_filter = HeartbeatFilter()
    
    blocked_messages = [
        '127.0.0.1:49603 - "GET /api/dispatch/overview HTTP/1.1" 200 OK',
        '127.0.0.1:49603 - "GET /health HTTP/1.1" 200 OK',
        '127.0.0.1:49603 - "GET /api/system/health HTTP/1.1" 200 OK',
        '127.0.0.1:49603 - "GET /api/galaxy/graph HTTP/1.1" 200 OK',
        '127.0.0.1:49603 - "GET /api/billing/stats HTTP/1.1" 200 OK',
        '127.0.0.1:61861 - "GET /api/system/sync/status HTTP/1.1" 200 OK',
        '127.0.0.1:61880 - "GET /api/system/preview/status HTTP/1.1" 200 OK',
    ]
    
    for msg in blocked_messages:
        record = logging.LogRecord(
            name="uvicorn.access",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg=msg,
            args=(),
            exc_info=None
        )
        assert h_filter.filter(record) is False, f"应被过滤但放行了: {msg}"

    # 同时断言真实的 Uvicorn tuple args 格式被拦截
    uvicorn_record = logging.LogRecord(
        name="uvicorn.access",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg='%s - "%s %s HTTP/%s" %d',
        args=('127.0.0.1:61861', 'GET', '/api/system/sync/status', '1.1', 200),
        exc_info=None
    )
    assert h_filter.filter(uvicorn_record) is False, "真实 Uvicorn 元组参数应被静默拦截"

def test_heartbeat_filter_allows_business_endpoints():
    """断言核心业务操作日志正常放行"""
    h_filter = HeartbeatFilter()
    
    allowed_messages = [
        '127.0.0.1:49603 - "POST /api/sync/execute HTTP/1.1" 200 OK',
        '127.0.0.1:49603 - "GET /api/vault/files HTTP/1.1" 200 OK',
        '127.0.0.1:49603 - "POST /api/translation/execute HTTP/1.1" 200 OK',
        '127.0.0.1:49603 - "GET /api/config HTTP/1.1" 200 OK',
        '127.0.0.1:49603 - "POST /api/editorial/publish HTTP/1.1" 200 OK',
    ]
    
    for msg in allowed_messages:
        record = logging.LogRecord(
            name="uvicorn.access",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg=msg,
            args=(),
            exc_info=None
        )
        assert h_filter.filter(record) is True, f"业务日志不应被过滤: {msg}"
