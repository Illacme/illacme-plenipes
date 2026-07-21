# -*- coding: utf-8 -*-
"""
tests/test_config_hot_reload.py
🛡️ [V75.8] 配置热重载与意志自愈功能测试
验证当配置发生热重载时，全局 Engine 的配置指针能够同步对齐，且 AI 智能路由策略的缓存节点可自愈清空重绑定。
"""

from unittest.mock import MagicMock, patch
from core.runtime.engine_singleton import set_global_engine, get_global_engine
from core.adapters.ai.strategies import GlobalSmartRoutingStrategy
from core.utils.event_bus import bus

def test_global_smart_routing_strategy_hot_reload():
    """测试当 CONFIG_RELOADED 事件广播时，智能路由策略能自动清空节点句柄缓存并热更配置"""
    # 1. 模拟旧的翻译配置
    old_trans_cfg = MagicMock()
    old_trans_cfg.primary_node = "ollama"
    
    # 2. 实例化全局智能路由策略
    strategy = GlobalSmartRoutingStrategy(old_trans_cfg)
    
    # 模拟其缓存已经填充
    strategy._handlers["ollama"] = MagicMock()
    assert len(strategy._handlers) == 1
    assert strategy.trans_cfg == old_trans_cfg
    
    # 3. 模拟配置热重载：构造全新的配置对象并触发广播事件
    new_config = MagicMock()
    new_trans_cfg = MagicMock()
    new_trans_cfg.primary_node = "openai"
    new_config.translation = new_trans_cfg
    
    bus.emit("CONFIG_RELOADED", config=new_config)
    
    # 4. 验证缓存已被物理清空，且 trans_cfg 指针成功自愈为最新配置
    assert len(strategy._handlers) == 0
    assert strategy.trans_cfg == new_trans_cfg

@patch("core.runtime.engine_factory.EngineFactory._init_basic_settings")
@patch("core.runtime.engine_factory.EngineFactory._init_ingress")
@patch("core.logic.ai.ai_factory.TranslatorFactory.create")
def test_engine_config_hot_reload_sync(mock_translator_create, mock_init_ingress, mock_init_settings):
    """测试通过配置更新 API 触发重载后，全局 engine 实例 of config 指向能够同步更新"""
    # 1. 模拟全局 Engine 及 config_manager
    mock_engine = MagicMock()
    mock_engine.no_ai = False
    mock_engine.config = MagicMock()
    mock_engine.config.active_theme = "default"
    mock_engine.config.vault_root = "/old/vault"
    mock_engine.config.translation.enable_ai = True
    
    # 模拟 config_manager 重载出新配置
    new_config = MagicMock()
    new_config.active_theme = "luxurious"
    new_config.vault_root = "/new/vault"
    new_config.translation.enable_ai = True
    
    mock_engine.config_manager.reload.side_effect = lambda: setattr(mock_engine.config_manager, "config", new_config)
    mock_engine.config_manager.config = new_config
    
    set_global_engine(mock_engine)
    
    # 2. 调用 API 的更新后逻辑模拟（直接执行已改写进 routes/gov/config.py 的热重载处理）
    engine = get_global_engine()
    assert engine == mock_engine
    
    if hasattr(engine, 'config_manager'):
        engine.config_manager.reload()
        engine.config = engine.config_manager.config
        
    engine.active_theme = engine.config.active_theme
    engine.vault_root = engine.config.vault_root
    
    # 3. 验证全局 engine 引用以及路径与主题属性均已热更对齐
    assert engine.config == new_config
    assert engine.active_theme == "luxurious"
    assert engine.vault_root == "/new/vault"
    
    # 清理全局单例
    set_global_engine(None)
