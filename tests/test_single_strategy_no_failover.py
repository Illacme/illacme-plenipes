# -*- coding: utf-8 -*-
"""
验证在 translation.strategy 为 'single' (单点模式) 时，
若在翻译过程中发生算力节点故障，系统绝不会越权调用 SmartRouter 执行 Failover 故障转移切流。
"""
from unittest.mock import MagicMock
from core.logic.ai.ai_scheduler_shards.dispatch_ops import AISchedulerDispatchOps

def test_single_strategy_no_failover_on_exception(monkeypatch):
    # 1. 模拟运行引擎与配置，并显式指定 bool 属性为 Python 原生类型以防止 MagicMock 的 True 穿透
    engine = MagicMock()
    engine.abort_sync = False  # 避免任务被取消
    engine.no_ai = False
    
    engine.config.translation.strategy = "single"
    engine.config.translation.primary_node = "primary_mock"
    engine.config.translation.enable_ai = True
    engine.config.translation.max_retries = 3
    engine.config.translation.llm_concurrency = 1
    
    # 模拟 i18n
    engine.i18n.enabled = True
    engine.i18n.source.lang_code = "zh"
    engine.i18n.source.prompt_lang = "zh"
    
    target_lang = MagicMock()
    target_lang.lang_code = "en"
    target_lang.prompt_lang = "English"
    engine.i18n.targets = [target_lang]
    
    # 模拟 meter 防止扣费限制触发
    engine.meter.check_and_block.return_value = True
    
    # 模拟 translator 适配器
    mock_translator = MagicMock()
    mock_translator.node_name = "primary_mock"
    
    # 让 translate 接口在被调用时强行抛出异常，模拟瞬时故障
    mock_translator.translate.side_effect = Exception("Mock API Connection Error")
    engine.translator = mock_translator
    
    # 模拟 circuit_breaker 机制
    mock_breaker = MagicMock()
    # 它的 call 应该透传调用 active_translator.translate 从而抛出异常
    mock_breaker.call.side_effect = lambda fn, *args, **kwargs: fn(*args, **kwargs)
    engine.circuit_breakers = {"ai": mock_breaker}
    
    # 模拟 smart_router 防止即使进去了也会误过，但我们断言它决不会被调用
    mock_router = MagicMock()
    engine.smart_router = mock_router
    
    # 模拟 dispatcher
    engine.dispatcher.dispatch = MagicMock()
    engine.meta.is_watch_mode = False
    
    # 2. 模拟 ctx (Context)
    ctx = MagicMock()
    ctx.base_fm = {}
    ctx.raw_content = "Some raw text"
    ctx.ai_health_flag = [True]
    
    # 3. 执行 dispatch_targets，拦截或捕获行为
    # 模拟 block_parser 和 markdown 结构
    mock_block = MagicMock()
    mock_block.type = "paragraph"
    mock_block.content = "Hello World"
    mock_block.fingerprint = "hash123"
    
    from core.logic.block_parser import MarkdownBlockParser
    monkeypatch.setattr(MarkdownBlockParser, "parse", lambda self, content: [mock_block])
    
    # 执行目标测试，在单点模式下，故障会一直抛出，直到重试次数耗尽
    res = AISchedulerDispatchOps.dispatch_targets(
        engine=engine,
        ctx=ctx,
        targets=[target_lang],
        route_prefix="",
        route_source="",
        force_sync=True,
        rel_path="test.md",
        is_dry_run=True,
        seo_data={}
    )
    
    # 4. 断言验证
    # 验证 get_failover_node 从未被调用
    assert mock_router.get_failover_node.call_count == 0, "在 single 策略下不应该调用 get_failover_node 进行故障转移！"
    
    # 验证 translate 被调用了 3 次（对应 max_retries=3，1 次初试 + 2 次重试）
    # 由于 retry_count 从 0 开始，当失败后 retry_count += 1
    # 循环条件是 retry_count < max_retries (3)，所以当第 3 次调用完后，retry_count 变为 3，不满足 < 3，退出循环，故总调用次数为 3 次。
    assert mock_translator.translate.call_count == 3, f"应该重试 3 次，但被调用了 {mock_translator.translate.call_count} 次"
