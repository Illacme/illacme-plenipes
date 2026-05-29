import sys
import os
import asyncio
import logging

# 确保能找到项目根目录模块
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from adapters.compute.openai import OpenAICompatibleTranslator
from core.adapters.ai.tool_registry import ToolRegistry
from core.adapters.ai.agent_loop import AutonomousAgent
from core.adapters.ai.tools.vault_tools import SearchVaultTool, ReadDocumentTool
from core.adapters.ai.tools.system_tools import CheckHealthTool, GitStatusTool

# 配置最基础的日志以便于观察 Tool Call 拦截
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

class MockConfig:
    model = "deepseek-chat"
    temperature = 0.1
    max_tokens = 512
    params = {}
    base_url = "https://api.deepseek.com/v1"
    api_key = os.environ.get("DEEPSEEK_API_KEY", "not-needed")
    limits = type('MockLimits', (), {'max_concurrency': 5, 'timeout': 30.0})()
    
class MockTransCfg:
    def __init__(self):
        self.compute_nodes = {"test_node": MockConfig()}
    @property
    def api_timeout(self):
        return 30.0

async def main():
    print("🚀 [TEST] Initializing System for Agent Loop...")
    
    # 注册工具
    registry = ToolRegistry()
    registry.register(SearchVaultTool)
    registry.register(ReadDocumentTool)
    registry.register(CheckHealthTool)
    registry.register(GitStatusTool)
    
    print(f"✅ Registered {len(registry._tools)} tools.")
    
    # 准备适配器 (以 OpenAI 为例，假设环境变量已有 OPENAI_API_KEY)
    print("🔌 Booting OpenAI Adapter...")
    trans_cfg = MockTransCfg()
    adapter = OpenAICompatibleTranslator("test_node", trans_cfg)
    adapter._intelligence_hub = type('MockHub', (), {'get_intelligent_payload': lambda *args, **kwargs: {}})()
    
    # 初始化 Agent
    agent = AutonomousAgent(ai_adapter=adapter, max_iterations=5)
    
    system_prompt = "You are Illacme Plenipes, an advanced AI system. You have access to tools to read the file system and check system health. Use them when necessary to answer user questions."
    user_prompt = "请帮我检查一下系统的健康状态（CPU/内存等），然后再在这个项目里搜索一下包含 'SOP-01' 的文件，并告诉我它是什么。"
    
    print(f"\n🗣️ [USER]: {user_prompt}\n")
    print("🧠 [AGENT LOOP] Starting execution...")
    
    # 触发自主执行
    try:
        final_answer = await agent.execute_task(system_prompt, user_prompt)
        print("\n==============================\n")
        print("🎯 [FINAL ANSWER]:\n")
        print(final_answer)
        print("\n==============================")
    except Exception as e:
        print(f"❌ Execution failed: {e}")

if __name__ == "__main__":
    # 需要在 async 环境中运行
    asyncio.run(main())
