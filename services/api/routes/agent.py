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
    system_prompt: str = "You are a highly capable AI assistant operating within Illacme Plenipes. You can use tools to read and modify files, and check system status."
    max_iterations: int = 10

class AgentAuthorizeRequest(BaseModel):
    hitl_id: str
    decision: str  # "approve" or "reject"

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
                async for event in agent.execute_task_stream(request.system_prompt, request.user_prompt):
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
