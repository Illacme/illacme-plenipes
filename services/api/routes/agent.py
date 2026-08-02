from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from core.runtime.engine_singleton import get_global_engine
from core.adapters.ai.agent_loop import AutonomousAgent
from core.adapters.ai.hitl import active_hitl_sessions

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

import logging
from core.adapters.ai.prober import DynamicCapabilityProber

logger = logging.getLogger(__name__)

@router.get("/model_info")
async def get_active_model_info():
    """
    🏢 动态获取当前激活的 AI 模型及其底层能力矩阵 (V76.3)
    """
    engine = get_global_engine()
    ai_cfg = getattr(engine, 'config', None).translation if getattr(engine, 'config', None) else None
    enable_ai = getattr(ai_cfg, 'enable_ai', True) if ai_cfg else True
    if getattr(engine, 'no_ai', False):
        enable_ai = False

    ai_adapter = getattr(engine, 'translator', None)
    if not enable_ai or not ai_adapter:
        return {
            "model_name": "已关闭" if not enable_ai else "未就绪",
            "disabled": not enable_ai,
            "capabilities": {"cot": False, "tools": False, "stream": False, "vision": False}
        }
    
    # 🕵️ [V76.4] 主权策略层穿透：若采用了 Fallback 或 SmartRouting 等包装策略，则递归穿透至底层物理算力节点
    actual_adapter = ai_adapter
    while hasattr(actual_adapter, 'primary') and getattr(actual_adapter, 'primary', None) is not None:
        actual_adapter = actual_adapter.primary
        
    raw_model = getattr(actual_adapter.config, 'model', None) or getattr(actual_adapter.config, 'model_name', None)
    if not raw_model and hasattr(actual_adapter, 'trans_cfg') and actual_adapter.trans_cfg:
        tc = actual_adapter.trans_cfg
        raw_model = tc.get('primary_model', None) if isinstance(tc, dict) else getattr(tc, 'primary_model', None)
    if not raw_model:
        raw_model = "qwen/qwen3.5-9b"
        
    model_name = str(raw_model)
    short_name = model_name.split("/")[-1] if model_name else "qwen3.5-9b"
    
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

class AgentRollbackRequest(BaseModel):
    patch_id: str

@router.post("/rollback")
async def rollback_agent_patch(request: AgentRollbackRequest):
    """
    🏢 物理逆转与一键撤销指定的微创补丁 (Rollback) (V76.6)
    """
    from core.adapters.ai.agent_loop import active_patches
    if request.patch_id not in active_patches:
        raise HTTPException(status_code=404, detail="找不到对应的补丁记录，或补丁已过期/已被回滚。")
        
    patch = active_patches[request.patch_id]
    rel_path = patch["relative_path"]
    search_content = patch["search_content"]
    replace_content = patch["replace_content"]
    
    from core.adapters.ai.tools.vault_service import get_secure_vault_path, fuzzy_match_document, verify_sandbox_path
    
    try:
        vault_path = get_secure_vault_path()
        full_path, resolved_rel, err_msg = fuzzy_match_document(vault_path, rel_path)
        if err_msg or not full_path:
            raise Exception(err_msg or "无法定位该原稿文件。")
            
        # 🛡️ 物理越界校验，防止沙箱穿越逃逸
        if not verify_sandbox_path(vault_path, full_path):
            raise Exception("Access denied. Path traversal blocked.")
            
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 物理唯一性精准匹配，若被二次修改导致无匹配或多匹配，为防误伤予以拒绝并安全自愈拦截
        occurrences = content.count(replace_content)
        if occurrences == 0:
            raise Exception("文件当前内容已被后续修改，无法精准定位需撤销的补丁块，已物理拦截回滚。")
        elif occurrences > 1:
            raise Exception("定位的补丁内容在文件中有多个完全相同的复本，为防误伤已物理拦截回退。")
            
        # 物理逆转还原
        new_content = content.replace(replace_content, search_content, 1)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
            
        # 回撤成功后清理内存缓存，物理保证单次消费
        del active_patches[request.patch_id]
        
        return {
            "status": "success",
            "message": f"已成功物理逆转回滚原稿文件 '{resolved_rel}' 的补丁更改！"
        }
    except Exception as e:
        logger.error(f"❌ [Rollback Error] Failed to rollback patch {request.patch_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
