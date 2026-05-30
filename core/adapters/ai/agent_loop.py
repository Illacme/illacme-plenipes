import logging
import json
import uuid
import asyncio
from typing import Dict, Any, List, Optional
from core.adapters.ai.tool_protocol import ToolCallEvent
from core.adapters.ai.tool_registry import ToolRegistry
from core.adapters.ai.hitl import active_hitl_sessions
from core.adapters.ai.tool_runner import call_llm_stream

logger = logging.getLogger(__name__)

class AutonomousAgent:
    """
    🏢 [V75.0] Illacme Plenipes Autonomous Agent Loop
    负责包裹底层的 _ask_ai_stream/_ask_ai，实现多轮循环的 Tool 执行闭环。
    """
    def __init__(self, ai_adapter, max_iterations: int = 10):
        self.ai_adapter = ai_adapter
        self.max_iterations = max_iterations
        self.registry = ToolRegistry()
        self._repetition_count = 0
        # 📁 [V75.6] 物理安全沙箱对正：初始化工作目录为当前活跃版图的原稿文库
        import os
        from core.runtime.engine_singleton import get_global_engine
        engine = get_global_engine()
        self.working_dir = os.path.abspath(engine.config.vault_root) if engine and hasattr(engine, 'config') and getattr(engine.config, 'vault_root', None) else os.path.abspath("./vault")
        logger.info(f"📁 [Agent Sandbox] AI module default working directory locked to: {self.working_dir}")

    async def execute_task_stream(self, system_prompt: str, user_content: str, reasoning_enabled: bool = True, reasoning_effort: str = "medium", autopilot_enabled: bool = False):
        """
        异步流式生成器，执行任务并抛出关键节点的状态。
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        iteration = 0
        logger.info("🤖 [Agent Loop] Booting autonomous core & interrogating ToolRegistry")

        while iteration < self.max_iterations:
            iteration += 1
            logger.info(f"🚀 [Agent Loop] Iteration {iteration}/{self.max_iterations}")
            
            # 🚀 [V75.1] 智能极速网关：对简单的日常问候，首轮自动绕过庞大的工具集注入，将 Token 上下文缩减 95%，大幅提升 Local LLM 推理响应速度
            is_simple_greeting = False
            if iteration == 1:
                cleaned_prompt = user_content.strip().lower().replace("!", "").replace("！", "")
                if cleaned_prompt in ["你好", "hello", "hi", "hey", "你好啊", "在吗", "早上好", "下午好", "晚上好"]:
                    is_simple_greeting = True

            tools = None if is_simple_greeting else self.registry.export_all_schemas()
            if not tools: tools = None

            # 🚀 [V75.4] 智能上下文压缩：若估计的 Token 总数超过 8000，对陈旧的较长 read_document 工具输出执行无损折叠/摘要压缩，释放宝贵的 Prompt 上下文，防止 4096 溢出截断
            est_tokens = 0
            for m in messages:
                if m.get("content"):
                    est_tokens += len(m["content"])
                if m.get("tool_calls"):
                    est_tokens += len(json.dumps(m["tool_calls"]))
            est_tokens = est_tokens // 3  # 中英混合估算比例
            
            if est_tokens > 8000:
                # 仅折叠历史/陈旧的 read_document 工具响应，强制保留最新一次响应以防死循环
                read_doc_indices = [i for i, m in enumerate(messages) if m.get("role") == "tool" and m.get("name") == "read_document"]
                if len(read_doc_indices) > 1:
                    logger.warning(f"⚠️ [Agent Loop] Context size estimate ({est_tokens} tokens) is high. Compressing old read_document tool responses...")
                    yield {"type": "step", "message": "⚠️ [Sentinel] 历史上下文逼近 limit 限制，已自动启用微创历史剪枝，为大模型预留生成空间...\n"}
                    for idx in read_doc_indices[:-1]:
                        m = messages[idx]
                        orig_content = m.get("content", "")
                        if len(orig_content) > 500:
                            # 压缩为精简的概要指纹
                            m["content"] = f"[Manuscript content of '{m.get('tool_call_id')}' omitted for context pruning (originally {len(orig_content)} characters). File content is already read in previous history. Please use patch_document with exact search_content to incremental modify this file.]"

            # 1. 呼叫流式大模型，实时吐出思维链与文本 Chunk
            response = None
            async for chunk in self._call_llm_stream(messages, tools, reasoning_enabled, reasoning_effort):
                if chunk["type"] == "thinking_chunk":
                    yield {"type": "thinking_chunk", "delta": chunk["delta"]}
                elif chunk["type"] == "content_chunk":
                    yield {"type": "content_chunk", "delta": chunk["delta"]}
                elif chunk["type"] == "tool_calls":
                    response = chunk["events"]
                elif chunk["type"] == "final_text":
                    response = chunk["text"]
            
            # 如果是普通的文本回复，意味着任务结束
            if isinstance(response, str):
                yield {"type": "final", "message": response}
                return
                
            # 如果是列表且包含 ToolCallEvent，说明模型要求执行工具
            if isinstance(response, list) and len(response) > 0 and isinstance(response[0], ToolCallEvent):
                # 🚀 [V75.3] 重复动作自哨兵检测
                current_calls = sorted([(event.name, json.dumps(event.arguments, sort_keys=True, ensure_ascii=False)) for event in response])
                
                tool_calls_payload = []
                for event in response:
                    tool_calls_payload.append({
                        "id": event.id, "type": "function",
                        "function": {"name": event.name, "arguments": json.dumps(event.arguments, ensure_ascii=False)}
                    })
                messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls_payload})

                # 2. 本地执行每个工具并收集结果
                current_results = []
                for event in response:
                    logger.info(f"🛠️ [Agent Loop] Executing Tool: {event.name} with {event.arguments}")
                    yield {"type": "step", "message": f"[🔧 CALL: {event.name}]\n"}
                    
                    # HITL 拦截逻辑 (仅当未开启 autopilot 且属于高危工具时拦截)
                    if not autopilot_enabled and event.name in ["write_document", "git_commit"]:
                        hitl_id = str(uuid.uuid4())
                        resume_event = asyncio.Event()
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
                    current_results.append((event.name, result_str))
                
                # 🚀 [V75.3] 熔断机制评估
                if hasattr(self, '_prev_calls') and hasattr(self, '_prev_results') and self._prev_calls is not None:
                    if self._prev_calls == current_calls and self._prev_results == current_results:
                        self._repetition_count += 1
                        logger.warning(f"🚨 [Agent Loop] Repetitive loop detected ({self._repetition_count}/3). Calls: {current_calls}")
                        if self._repetition_count >= 3:
                            yield {"type": "step", "message": "🚨 [Sentinel] 熔断警告：检测到大模型在执行相同操作时陷入死循环且结果无变化。自动熔断以防止 Token 浪费。\n"}
                            yield {"type": "final", "message": f"🚨 [Sentinel] 已成功熔断大模型无限死循环环路。发生重复的工具为: {', '.join([c[0] for c in current_calls])}。请检查输入指令。"}
                            return
                    else:
                        self._repetition_count = 0
                else:
                    self._repetition_count = 0
                
                self._prev_calls = current_calls
                self._prev_results = current_results
                continue
            
            logger.warning(f"⚠️ [Agent Loop] Unknown response type: {type(response)}")
            yield {"type": "final", "message": str(response)}
            return

        yield {"type": "final", "message": f"🚨 [Agent Loop] Max iterations ({self.max_iterations}) reached."}

    async def execute_task(self, system_prompt: str, user_content: str) -> str:
        """
        [Sovereign Core] 物理同步封装器。
        """
        final_message = ""
        async for event in self.execute_task_stream(system_prompt, user_content):
            if event.get("type") == "final":
                final_message = event.get("message", "")
        return final_message

    async def _call_llm_stream(self, messages: list, tools: list, reasoning_enabled: bool, reasoning_effort: str):
        """
        [Sovereign Core] 算力物理流式转发器，用于防腐与测试隔离。
        """
        async for chunk in call_llm_stream(self.ai_adapter, messages, tools, reasoning_enabled, reasoning_effort):
            yield chunk
