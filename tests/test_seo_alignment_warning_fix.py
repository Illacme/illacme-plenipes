# -*- coding: utf-8 -*-
"""
验证 AIAlignmentProcessor 在使用自定义模板（例如含有 {lang_name} 占位符的 seo.user 模板）时，
格式化过程不会产生 `提示词格式化缺失占位符` 的 KeyError 警告。
"""
from unittest.mock import MagicMock
from core.logic.seo.ai_alignment import AIAlignmentProcessor

def test_seo_alignment_no_warning(caplog):
    # 模拟 translator 和 prompts
    translator = MagicMock()
    translator.config.max_tokens = 4096
    translator.config.base_url = "http://localhost"
    translator.node_name = "test_node"
    
    # 设定 prompts
    prompts = MagicMock()
    prompts.seo_system = "System: {lang_name}"
    prompts.seo_user = "Language: {lang_name}\nText: {text}"
    translator.trans_cfg.prompts = prompts
    translator.trans_cfg.active_style = "default"
    
    # 模拟 ctx
    ctx = MagicMock()
    ctx.title = "Test Title"
    ctx.ai_pure_body = "This is a body excerpt to test."
    ctx.source_lang = "zh"
    ctx.engine.translator = translator
    ctx.fm_dict = {}
    
    # 模拟 ask_ai_with_retry 的返回
    translator.ask_ai_with_retry.return_value = '{"seo_title": "Optimized Title", "description": "Optimized Desc", "keywords": "key, word"}'
    
    # 模拟 Factory 行为防止干扰
    from core.logic.ai.ai_factory import TranslatorFactory
    original_get_prompts = TranslatorFactory.get_prompts_for_style
    TranslatorFactory.get_prompts_for_style = MagicMock(return_value=prompts)
    
    try:
        processor = AIAlignmentProcessor()
        res = processor.process(ctx)
        
        # 打印警告日志
        warnings = [record.message for record in caplog.records if "提示词格式化缺失占位符" in record.message]
        print("Captured prompt format warnings:", warnings)
        
        assert len(warnings) == 0, f"发现缺失占位符警告: {warnings}"
        
        # 验证结果已被正确解析
        assert res['description'] == "Optimized Desc"
        assert res['keywords'] == ["key", "word"]
    finally:
        TranslatorFactory.get_prompts_for_style = original_get_prompts
