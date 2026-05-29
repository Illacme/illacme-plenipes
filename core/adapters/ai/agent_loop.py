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

    async def execute_task_stream(self, system_prompt: str, user_content: str, reasoning_enabled: bool = True, reasoning_effort: str = "medium"):
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

    async def execute_task(self, system_prompt: str, user_content: str) -> str:
        """
        [Sovereign Core] 物理同步封装器。
        累积 execute_task_stream 抛出的所有事件，返回最终答案以兼容现有测试与同步调用。
        """
        final_message = ""
        async for event in self.execute_task_stream(system_prompt, user_content):
            if event.get("type") == "final":
                final_message = event.get("message", "")
        return final_message

    async def _call_llm_stream(self, messages: list, tools: list, reasoning_enabled: bool, reasoning_effort: str):
        """
        [Sovereign Core] 统一的 LLM 物理流式调用器。
        支持实时分发 thinking_chunk 与 content_chunk，同时累积 tool_calls。
        """
        import requests
        # 1. 检验适配器类型，必须是 OpenAICompatibleTranslator 家族 (利用 class MRO 避免循环导入)
        is_openai_compatible = any(c.__name__ == "OpenAICompatibleTranslator" for c in self.ai_adapter.__class__.__mro__)
        if not is_openai_compatible:
            # 降级：走非流式保底通道
            logger.info("⚠️ [Agent Stream] Non-OpenAI adapter detected, falling back to sync path.")
            payload = {
                "model": getattr(self.ai_adapter.trans_cfg, 'primary_model', 'gpt-4o') if hasattr(self.ai_adapter, 'trans_cfg') else 'gpt-4o',
                "messages": messages,
                "tools": tools,
                "params": {"temperature": 0.2}
            }
            response = self.ai_adapter.ask_ai_with_retry(payload)
            if isinstance(response, str):
                yield {"type": "final_text", "text": response}
            else:
                yield {"type": "tool_calls", "events": response}
            return

        # 2. 准备基础请求参数
        model_name = getattr(self.ai_adapter.config, 'model', 'gpt-4o')
        
        # 3. 对齐主权翻译参数组装
        openai_tools = []
        if tools:
            from core.adapters.ai.tool_protocol import IllacmeTool
            for t in tools:
                if isinstance(t, IllacmeTool):
                    openai_tools.append({
                        "type": "function",
                        "function": {
                            "name": t.name,
                            "description": t.description,
                            "parameters": t.parameters
                        }
                    })
                elif isinstance(t, dict):
                    openai_tools.append(t)

        # 4. 精准思维链参数对正
        reasoning_params = self._assemble_reasoning_params(self.ai_adapter, model_name, reasoning_enabled, reasoning_effort)

        openai_payload = {
            "model": model_name,
            "messages": messages,
            "stream": True,
            "temperature": 0.2 if reasoning_enabled else 0.1,
            **reasoning_params
        }
        if openai_tools:
            openai_payload["tools"] = openai_tools

        # 5. 拼接 API 物理地址与 Headers
        url = self.ai_adapter.safe_get_url()
        if not url.endswith("/chat/completions") and not url.endswith("/completions"):
            url = f"{url.rstrip('/')}/chat/completions"

        headers = {
            "Content-Type": "application/json"
        }
        api_key = self.ai_adapter.safe_get_config('api_key')
        if api_key and api_key not in ["not-needed", "none", "empty"]:
            headers["Authorization"] = f"Bearer {api_key}"

        proxies = None
        proxy_url = self.ai_adapter.safe_get_config('proxy') or getattr(self.ai_adapter.trans_cfg, 'global_proxy', None)
        if proxy_url:
            proxies = {"http": proxy_url, "https": proxy_url}

        # 6. 在线程池中发起流式 HTTP 连接，防止 IO 阻塞 asyncio 循环
        loop = asyncio.get_event_loop()
        
        def run_post():
            return self.ai_adapter._session.post(
                url, json=openai_payload, headers=headers, proxies=proxies,
                timeout=self.ai_adapter.timeout, stream=True
            )

        try:
            resp = await loop.run_in_executor(None, run_post)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"🛑 [Agent Stream] HTTP POST failed: {e}, falling back to sync path.")
            # 发生任何网络建立异常，立即走非流式保底通道
            payload = {
                "model": model_name,
                "messages": messages,
                "tools": tools,
                "params": {"temperature": 0.2}
            }
            response = self.ai_adapter.ask_ai_with_retry(payload)
            if isinstance(response, str):
                yield {"type": "final_text", "text": response}
            else:
                yield {"type": "tool_calls", "events": response}
            return

        # 7. 逐行读取流数据
        accumulated_tools = {}
        accumulated_content = []
        
        # 内部生成器：在线程池里读取流响应行
        def line_generator():
            try:
                for line in resp.iter_lines():
                    if line:
                        yield line.decode('utf-8')
            except Exception as stream_err:
                logger.error(f"🛑 [Agent Stream] error iterating stream lines: {stream_err}")

        try:
            for line in line_generator():
                if not line.strip(): continue
                # 去除可能的 data: 前缀
                data_line = line.strip()
                if data_line.startswith("data: "):
                    data_str = data_line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    
                    try:
                        chunk = json.loads(data_str)
                    except Exception:
                        continue
                        
                    choices = chunk.get("choices", [])
                    if not choices: continue
                    delta = choices[0].get("delta", {})
                    
                    # A. 提取思维链 Chunk (R1 / reasoning_content)
                    reasoning_chunk = delta.get("reasoning_content", "")
                    if reasoning_chunk:
                        yield {"type": "thinking_chunk", "delta": reasoning_chunk}
                        continue
                        
                    # B. 提取普通文本 Chunk
                    content_chunk = delta.get("content", "")
                    if content_chunk:
                        accumulated_content.append(content_chunk)
                        yield {"type": "content_chunk", "delta": content_chunk}
                        continue
                        
                    # C. 提取工具调用 delta
                    tool_calls_delta = delta.get("tool_calls", [])
                    for tc in tool_calls_delta:
                        idx = tc.get("index", 0)
                        if idx not in accumulated_tools:
                            accumulated_tools[idx] = {"id": "", "name": "", "arguments": ""}
                        
                        if tc.get("id"):
                            accumulated_tools[idx]["id"] = tc.get("id")
                        
                        func = tc.get("function", {})
                        if func.get("name"):
                            accumulated_tools[idx]["name"] = func.get("name")
                        if func.get("arguments"):
                            accumulated_tools[idx]["arguments"] += func.get("arguments")
                            
        except Exception as e:
            logger.error(f"🛑 [Agent Stream] Error during stream processing: {e}")
        finally:
            try:
                resp.close()
            except Exception:
                pass

        # 8. 完成流处理，如果累积了工具调用，组装成 ToolCallEvent 并返回
        if accumulated_tools:
            from core.adapters.ai.tool_protocol import ToolCallEvent
            events = []
            for idx, tc in sorted(accumulated_tools.items()):
                try:
                    args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                except Exception:
                    args = {}
                events.append(ToolCallEvent(
                    tool_name=tc["name"],
                    arguments=args,
                    raw_call_id=tc["id"]
                ))
            yield {"type": "tool_calls", "events": events}
        else:
            # 如果没有工具调用，返回最终的完整普通文本
            full_text = "".join(accumulated_content)
            yield {"type": "final_text", "text": full_text}

    def _assemble_reasoning_params(self, adapter, model_name: str, enabled: bool, effort: str) -> dict:
        """
        🏢 智能大模型思维链参数精准对正器 (Sovereignty Precision Alignment)
        根据适配器类型与模型名称，输出精确对正的 API 扩展参数。
        """
        params = {}
        model_name_lower = model_name.lower()
        adapter_class_name = adapter.__class__.__name__
        
        # 1. OpenRouter 规范
        if "OpenRouter" in adapter_class_name:
            params["reasoning"] = {
                "enabled": enabled,
                "effort": "medium" if effort == "medium" else ("low" if effort == "low" else "high")
            }
        
        # 2. Together AI 规范
        elif "Together" in adapter_class_name:
            params["reasoning"] = {"enabled": enabled}
            if enabled:
                params["reasoning_effort"] = effort

        # 3. SiliconFlow 规范
        elif "SiliconFlow" in adapter_class_name:
            if enabled:
                params["thinking_budget"] = 1024
            else:
                params["thinking_budget"] = 0

        # 4. Ollama 规范
        elif "Ollama" in adapter_class_name:
            params["think"] = enabled
            params["thinking"] = enabled

        # 5. OpenAI 官方 o1/o3-mini 规范
        elif "OpenAI" in adapter_class_name and ("o1" in model_name_lower or "o3" in model_name_lower):
            if enabled:
                params["reasoning_effort"] = effort

        # 6. 通用/本地兼容逻辑（如 LM Studio, vLLM 等）
        else:
            params["enable_thinking"] = enabled
            params["think"] = enabled
            if enabled:
                params["thinking_budget"] = 1024
                params["reasoning_effort"] = effort
            else:
                params["thinking_budget"] = 0
                
        return params
