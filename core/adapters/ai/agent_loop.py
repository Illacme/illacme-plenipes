import logging
import json
from typing import Dict, Any, List, Optional

from core.adapters.ai.tool_protocol import ToolCallEvent
from core.adapters.ai.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)

import uuid
import asyncio

active_hitl_sessions = {}

class AutonomousAgent:
    """
    🏢 [V75.0] Illacme Plenipes Autonomous Agent Loop
    负责包裹底层的 _ask_ai_stream/_ask_ai，实现多轮循环的 Tool 执行闭环。
    """
    def __init__(self, ai_adapter, max_iterations: int = 10):
        self.ai_adapter = ai_adapter
        self.max_iterations = max_iterations
        self.registry = ToolRegistry()

    async def execute_task_stream(self, system_prompt: str, user_content: str):
        """
        异步流式生成器，执行任务并抛出关键节点的状态。
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        iteration = 0
        yield {"type": "status", "message": "[Agent] Booting autonomous core...\n"}
        yield {"type": "status", "message": "[Agent] Interrogating ToolRegistry...\n"}

        while iteration < self.max_iterations:
            iteration += 1
            logger.info(f"🚀 [Agent Loop] Iteration {iteration}/{self.max_iterations}")
            
            tools = self.registry.export_all_schemas()
            if not tools: tools = None

            # 1. 呼叫大模型 (在线程池中运行防阻塞)
            loop = asyncio.get_event_loop()
            
            payload = {
                "model": getattr(self.ai_adapter.trans_cfg, 'primary_model', 'gpt-4o') if hasattr(self.ai_adapter, 'trans_cfg') else 'gpt-4o',
                "messages": messages,
                "tools": tools,
                "params": {"temperature": 0.2}
            }
            
            response = await loop.run_in_executor(None, lambda: self.ai_adapter.ask_ai_with_retry(payload))
            
            # 如果是普通的文本回复，意味着任务结束
            if isinstance(response, str):
                yield {"type": "final", "message": response}
                return
                
            # 如果是列表且包含 ToolCallEvent，说明模型要求执行工具
            if isinstance(response, list) and len(response) > 0 and isinstance(response[0], ToolCallEvent):
                tool_calls_payload = []
                for event in response:
                    tool_calls_payload.append({
                        "id": event.id, "type": "function",
                        "function": {"name": event.name, "arguments": json.dumps(event.arguments, ensure_ascii=False)}
                    })
                messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls_payload})

                # 2. 本地执行每个工具
                for event in response:
                    logger.info(f"🛠️ [Agent Loop] Executing Tool: {event.name} with {event.arguments}")
                    yield {"type": "step", "message": f"[🔧 SYSTEM CALL: {event.name}]\n"}
                    
                    # HITL 拦截逻辑
                    if event.name in ["write_document", "git_commit"]:
                        hitl_id = str(uuid.uuid4())
                        # 创建挂起事件
                        resume_event = asyncio.Event()
                        # 共享状态用于存放用户决策结果
                        session_state = {"status": "pending", "event": resume_event, "tool_name": event.name, "args": event.arguments}
                        active_hitl_sessions[hitl_id] = session_state
                        
                        yield {
                            "type": "hitl_required",
                            "hitl_id": hitl_id,
                            "tool": event.name,
                            "args": event.arguments,
                            "message": f"⚠️ [HITL] 工具 {event.name} 需要物理授权"
                        }
                        
                        logger.info(f"🛑 [HITL] 挂起等待人类授权... hitl_id={hitl_id}")
                        await resume_event.wait()
                        
                        decision = session_state.get("decision", "reject")
                        del active_hitl_sessions[hitl_id]
                        
                        if decision == "approve":
                            result_str = self.registry.execute_tool(event.name, event.arguments)
                        else:
                            result_str = "Error: Execution blocked by human override."
                    else:
                        result_str = self.registry.execute_tool(event.name, event.arguments)
                    
                    logger.debug(f"🛠️ [Agent Loop] Result: {result_str[:100]}...")
                    messages.append({"role": "tool", "tool_call_id": event.id, "name": event.name, "content": result_str})
                    
                continue
            
            # 不认识的对象
            logger.warning(f"⚠️ [Agent Loop] Unknown response type: {type(response)}")
            yield {"type": "final", "message": str(response)}
            return

        yield {"type": "final", "message": f"🚨 [Agent Loop] Max iterations ({self.max_iterations}) reached."}
