#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 OpenAI 协议下 Tool Use 的拦截与大一统协议栈。
"""

import sys
import os

# 确保能找到 core 包
sys.path.insert(0, os.path.abspath('.'))

from core.adapters.ai.tool_protocol import IllacmeTool, ToolCallEvent
from core.adapters.ai.payload_manager import PayloadManager
from adapters.compute.openai import OpenAICompatibleTranslator

# 构造一个极简的 Config Mock
class MockConfig:
    model = "deepseek-chat"
    temperature = 0.1
    max_tokens = 512
    params = {}
    
class MockLimits:
    max_concurrency = 5
    timeout = 30.0

class MockTransCfg:
    def __init__(self):
        self.compute_nodes = {}
    
    @property
    def api_timeout(self):
        return 30.0

def main():
    print("🚀 启动 Tool Use 大一统协议拦截测试...")
    
    trans_cfg = MockTransCfg()
    node_config = MockConfig()
    node_config.limits = MockLimits()
    node_config.base_url = "https://api.deepseek.com/v1"
    # 这里不需要真实的 API KEY，只要请求发出去看 Payload 是否正确即可
    # 如果要看真实拦截，填入你本地的真实 API Key
    node_config.api_key = os.environ.get("DEEPSEEK_API_KEY", "not-needed")
    
    trans_cfg.compute_nodes["test_node"] = node_config
    
    adapter = OpenAICompatibleTranslator("test_node", trans_cfg)
    adapter._intelligence_hub = type('MockHub', (), {'get_intelligent_payload': lambda *args, **kwargs: {}})()
    
    # 构造工具兵器库
    tools = [
        IllacmeTool(
            name="search_web",
            description="联网搜索获取实时信息",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"}
                },
                "required": ["query"]
            }
        )
    ]
    
    # 模拟一次强制工具调用的请求
    print("\n📦 正在装配中立意图对象 (Neutral Intent Object)...")
    payload = PayloadManager.prepare_payload(
        adapter,
        system_prompt="You are a helpful assistant.",
        user_content="请帮我搜索一下马斯克最新的火星计划新闻",
        tools=tools
    )
    
    print("\n📡 发起底层协议通信 (_ask_ai)...")
    if node_config.api_key == "not-needed":
        print("⚠️ 未提供真实的 API Key，跳过真实网络请求。您可以设置 DEEPSEEK_API_KEY 环境变量运行以查看真实链路拦截。")
        # 直接 mock 一次 _ask_ai 内部网络调用的 payload 看组装
        messages = payload.get("messages", [])
        if not messages:
            messages = [
                {"role": "system", "content": payload.get("system")},
                {"role": "user", "content": payload.get("user")}
            ]

        openai_payload = {
            "model": payload.get("model"),
            "messages": messages,
            **payload.get("params", {})
        }
        
        openai_tools = []
        for t in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters
                }
            })
        openai_payload["tools"] = openai_tools
        
        print("\n✅ 翻译后的 OpenAI 兼容载荷: ")
        import json
        print(json.dumps(openai_payload, indent=2, ensure_ascii=False))
        return
        
    try:
        result = adapter.ask_ai_with_retry(payload)
        print("\n✅ [拦截器截获结果]:")
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], ToolCallEvent):
            print("🎯 成功捕获 ToolCallEvent 数组! ")
            for evt in result:
                print(f"   -> 动作: {evt.tool_name}")
                print(f"   -> 参数: {evt.arguments}")
                print(f"   -> 原始ID: {evt.raw_call_id}")
        else:
            print(f"💬 模型返回了普通文本: {result}")
    except Exception as e:
        print(f"❌ 通信异常: {e}")

if __name__ == "__main__":
    main()
