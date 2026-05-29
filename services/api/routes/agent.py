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
    model_lower = model_name.lower() if model_name else ""
    cot_supported = any(kw in model_lower for kw in ["r1", "o1", "o3", "thinking", "reasoning", "qwen3.5", "qwen2.5", "qwen35"])
    tools_supported = any(c.__name__ == "OpenAICompatibleTranslator" for c in actual_adapter.__class__.__mro__) and actual_adapter.__class__.__name__ != "MockAIProvider"
    vision_supported = any(kw in model_lower for kw in ["vl", "vision", "gpt-4o", "claude-3-5", "qwen3.5", "qwen2.5", "qwen35"])
    return {
        "model_name": short_name,
        "capabilities": {
            "cot": cot_supported,
            "tools": tools_supported,
            "stream": True,
            "vision": vision_supported
        }
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
