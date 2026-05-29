from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json

from core.runtime.engine_singleton import get_global_engine
from core.adapters.ai.agent_loop import AutonomousAgent, active_hitl_sessions

router = APIRouter(prefix="/api/agent", tags=["agent"])

class AgentTaskRequest(BaseModel):
    user_prompt: str
    system_prompt: str = "You are the Sovereign Copilot, an advanced AI coordinator operating within the sovereign engine Illacme Plenipes. Always be professional, extremely concise, direct, and action-oriented. Avoid repeating generic greetings, boilerplate descriptions, or introductions (such as '你好！我是 Illacme Plenipes 中的 AI 助手') unless explicitly requested by the user. You MUST always respond in the same language as the user's input (e.g., respond in Chinese if the input is Chinese, and in English if the input is in English), unless explicitly instructed otherwise."
    max_iterations: int = 10
    reasoning_enabled: bool = True
    reasoning_effort: str = "medium"
    autopilot_enabled: bool = False

class AgentAuthorizeRequest(BaseModel):
    hitl_id: str
    decision: str  # "approve" or "reject"

import os
import logging
import requests

logger = logging.getLogger(__name__)
CACHE_PATH = ".plenipes/capabilities_cache.json"

class DynamicCapabilityProber:
    _cache = {}
    _probing_models = set()

    @classmethod
    def load_cache(cls):
        if not cls._cache and os.path.exists(CACHE_PATH):
            try:
                with open(CACHE_PATH, 'r', encoding='utf-8') as f:
                    cls._cache = json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ Failed to load capabilities cache: {e}")
        return cls._cache

    @classmethod
    def save_cache(cls):
        try:
            os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
            with open(CACHE_PATH, 'w', encoding='utf-8') as f:
                json.dump(cls._cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"🛑 Failed to save capabilities cache: {e}")

    @classmethod
    def get_capabilities(cls, adapter, model_name: str) -> dict:
        cls.load_cache()
        
        # 1. 基础默认值 (启发式降级)
        model_lower = model_name.lower() if model_name else ""
        cot_supported = any(kw in model_lower for kw in ["r1", "o1", "o3", "thinking", "reasoning", "qwen3.5", "qwen2.5", "qwen35"])
        tools_supported = any(c.__name__ == "OpenAICompatibleTranslator" for c in adapter.__class__.__mro__) and adapter.__class__.__name__ != "MockAIProvider"
        vision_supported = any(kw in model_lower for kw in ["vl", "vision", "gpt-4o", "claude-3-5", "qwen3.5", "qwen2.5", "qwen35"])
        
        default_caps = {
            "cot": cot_supported,
            "tools": tools_supported,
            "stream": True,
            "vision": vision_supported
        }
        
        if adapter.__class__.__name__ == "MockAIProvider":
            return {"cot": False, "tools": False, "stream": True, "vision": False}
            
        url = getattr(adapter, 'safe_get_url', lambda: "")()
        if not url:
            return default_caps
            
        cache_key = f"{url}:{model_name}"
        if cache_key in cls._cache:
            # 已经有缓存，直接返回
            return cls._cache[cache_key]
            
        # 2. 如果没有缓存，且当前没有在探测中，则启动后台异步探测任务
        if cache_key not in cls._probing_models:
            cls._probing_models.add(cache_key)
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(cls._async_probe(adapter, model_name, cache_key, default_caps))
            except RuntimeError:
                # 🛡️ 容错对正：若当前没有在运行的 asyncio 事件循环（如在 sync / Trio 单元测试中），则使用新开的后台守护线程执行协程，实现 100% 物理自愈
                import threading
                def run_in_thread():
                    try:
                        asyncio.run(cls._async_probe(adapter, model_name, cache_key, default_caps))
                    except Exception:
                        pass
                threading.Thread(target=run_in_thread, daemon=True).start()
            
        # 在后台探测完成前，先安全降级返回启发式默认值，零延迟响应
        return default_caps

    @classmethod
    async def _async_probe(cls, adapter, model_name: str, cache_key: str, default_caps: dict):
        """
        🌐 后台异步探测模型真实物理能力，绝不阻塞用户 UI 线程
        """
        logger.info(f"🔮 [Dynamic Probe] Background active prober starting for: {model_name}")
        
        # 默认继承启发式探测的初始状态
        probed_caps = default_caps.copy()
        
        try:
            url = adapter.safe_get_url()
        except Exception:
            url = ""
            
        if not url:
            cls._probing_models.discard(cache_key)
            return
            
        if not url.endswith("/chat/completions") and not url.endswith("/completions"):
            url = f"{url.rstrip('/')}/chat/completions"
            
        headers = {"Content-Type": "application/json"}
        api_key = getattr(adapter, 'safe_get_config', lambda k: "")('api_key')
        if api_key and api_key not in ["not-needed", "none", "empty"]:
            headers["Authorization"] = f"Bearer {api_key}"
            
        # 1. 探测工具调用支持 (Tools Probe)
        tools_payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": "Respond only with 'OK'."}],
            "max_tokens": 1,
            "temperature": 0.0,
            "tools": [{
                "type": "function",
                "function": {
                    "name": "probe_capability_tool",
                    "description": "A dummy tool used to verify if the LLM endpoint accepts tool definitions.",
                    "parameters": {"type": "object", "properties": {}}
                }
            }],
            "tool_choice": "none"
        }
        
        try:
            loop = asyncio.get_running_loop()
            run_async = True
        except RuntimeError:
            run_async = False
            
        def send_tools_probe():
            session = getattr(adapter, '_session', requests)
            return session.post(url, json=tools_payload, headers=headers, timeout=5)
            
        try:
            if run_async:
                resp = await loop.run_in_executor(None, send_tools_probe)
            else:
                resp = send_tools_probe()
                
            if resp.status_code == 200:
                probed_caps["tools"] = True
            else:
                probed_caps["tools"] = False
        except Exception as e:
            logger.warning(f"⚠️ [Dynamic Probe] Tools active probe failed: {e}")
            
        # 2. 探测思维链推理支持 (CoT Probe)
        cot_payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": "Which is larger: 9.11 or 9.9?"}],
            "max_tokens": 15,
            "temperature": 0.0
        }
        
        def send_cot_probe():
            session = getattr(adapter, '_session', requests)
            return session.post(url, json=cot_payload, headers=headers, timeout=5)
            
        try:
            if run_async:
                resp = await loop.run_in_executor(None, send_cot_probe)
            else:
                resp = send_cot_probe()
                
            if resp.status_code == 200:
                resp_json = resp.json()
                choices = resp_json.get("choices", [])
                if choices:
                    message = choices[0].get("message", {})
                    if ("reasoning_content" in message and message["reasoning_content"]) or \
                       ("<think>" in message.get("content", "")) or \
                       ("thinking" in message):
                        probed_caps["cot"] = True
                    else:
                        probed_caps["cot"] = False
                else:
                    probed_caps["cot"] = False
            else:
                probed_caps["cot"] = False
        except Exception as e:
            logger.warning(f"⚠️ [Dynamic Probe] CoT active probe failed: {e}")
            
        # 3. 写入缓存并落盘
        cls._cache[cache_key] = probed_caps
        cls.save_cache()
        cls._probing_models.discard(cache_key)
        logger.info(f"✨ [Dynamic Probe] Active probe complete for {model_name}: {probed_caps}")

@router.get("/model_info")
async def get_active_model_info():
    """
    🏢 动态获取当前激活的 AI 模型及其底层能力矩阵 (V76.3)
    """
    engine = get_global_engine()
    ai_adapter = getattr(engine, 'translator', None)
    if not ai_adapter:
        return {
            "model_name": "未就绪",
            "capabilities": {"cot": False, "tools": False, "stream": False, "vision": False}
        }
    
    # 🕵️ [V76.4] 主权策略层穿透：若采用了 Fallback 或 SmartRouting 等包装策略，则递归穿透至底层物理算力节点
    actual_adapter = ai_adapter
    while hasattr(actual_adapter, 'primary') and getattr(actual_adapter, 'primary', None) is not None:
        actual_adapter = actual_adapter.primary
        
    model_name = "Unknown"
    if hasattr(actual_adapter, 'config') and hasattr(actual_adapter.config, 'model'):
        model_name = actual_adapter.config.model
    elif hasattr(actual_adapter, 'trans_cfg') and hasattr(actual_adapter.trans_cfg, 'primary_model'):
        model_name = actual_adapter.trans_cfg.primary_model
        
    short_name = model_name.split("/")[-1] if model_name else "Unknown"
    
    # 🚀 使用全动态探测系统
    capabilities = DynamicCapabilityProber.get_capabilities(actual_adapter, model_name)
    
    return {
        "model_name": short_name,
        "capabilities": capabilities
    }

@router.post("/task")
async def execute_agent_task(request: AgentTaskRequest):
    """
    接收用户指令，实例化 AutonomousAgent，并在后台执行任务。
    为了简化实现，这里先采用阻塞转异步或假流式的方式返回最终结果，后续可接入完整的多轮事件流(SSE)。
    """
    engine = get_global_engine()
    
    try:
        if not engine or not hasattr(engine, 'translator'):
            raise Exception("AI Translator not initialized on engine")
        
        # 获取一个有效的 AI Adapter
        ai_adapter = getattr(engine, 'translator', None)
        if not ai_adapter:
            raise Exception("No primary AI adapter available (engine.translator is None)")
            
        agent = AutonomousAgent(ai_adapter, max_iterations=request.max_iterations)
        
        async def task_generator():
            try:
                async for event in agent.execute_task_stream(
                    request.system_prompt,
                    request.user_prompt,
                    reasoning_enabled=request.reasoning_enabled,
                    reasoning_effort=request.reasoning_effort,
                    autopilot_enabled=request.autopilot_enabled
                ):
                    yield "data: " + json.dumps(event) + "\n\n"
            except Exception as inner_e:
                yield "data: " + json.dumps({"type": "final", "message": f"[Fatal Error] {inner_e}"}) + "\n\n"

        return StreamingResponse(task_generator(), media_type="text/event-stream")

    except Exception as e:
        error_msg = str(e)
        async def err_gen():
            yield "data: " + json.dumps({"type": "final", "message": f"🚨 引擎加载失败: {error_msg}"}) + "\n\n"
        return StreamingResponse(err_gen(), media_type="text/event-stream")

@router.post("/authorize")
async def authorize_agent_task(request: AgentAuthorizeRequest):
    """
    接收前端的人类审查决策，解锁后端挂起的大模型。
    """
    if request.hitl_id not in active_hitl_sessions:
        raise HTTPException(status_code=404, detail="HITL session not found or already processed.")
        
    session = active_hitl_sessions[request.hitl_id]
    session["decision"] = request.decision
    session["event"].set()  # 解锁 asyncio.Event
    
    return {"status": "success", "decision": request.decision}
