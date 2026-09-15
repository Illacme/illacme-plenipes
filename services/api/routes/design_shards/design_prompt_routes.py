# -*- coding: utf-8 -*-
"""
🎨 Design Studio - AI Prompt Refinement Route Shard
职责：接收简短中文/英文提示词，调用多模型算力网关扩写为专业级视觉生图 Prompt。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
🛡️ [Protocols] 遵守大模型思维链清洗与载荷对准规约。
"""

import re
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from core.runtime.engine_singleton import get_global_engine
from core.adapters.ai.payload_manager import PayloadManager
from core.utils.tracing import tlog

router = APIRouter()

def verify_token(x_token: Optional[str] = Header(None, alias="X-Token")) -> None:
    """验证 API 访问令牌"""
    engine = get_global_engine()
    if not engine or not getattr(engine, 'config', None) or not getattr(engine.config, 'system', None) or not getattr(engine.config.system, 'api_token', None):
        return
    if x_token != engine.config.system.api_token:
        raise HTTPException(status_code=403, detail="Unauthorized")

class RefinePromptRequest(BaseModel):
    prompt: str
    style: Optional[str] = "cinematic"

STYLE_MODIFIERS = {
    "cinematic": "cinematic concept art, dramatic studio rim lighting, 8k resolution, octane render, photorealistic depth of field",
    "cyberpunk": "cyberpunk aesthetics, volumetric neon lighting, holographic HUD elements, high tech dystopian atmosphere, unreal engine 5",
    "watercolor": "traditional Chinese ink wash and watercolor illustration, delicate brushstrokes, misty atmospheric landscape, poetic elegance",
    "3d_render": "modern 3D isometric clay render, Pixar style, soft ambient occlusion, cute aesthetic, vibrant studio lighting",
    "photorealistic": "award-winning National Geographic documentary photography, 35mm film grain, Hasselblad lens, ultra-sharp focus, natural lighting",
    "minimalist": "minimalist flat vector graphic, clean negative space, Swiss design layout, geometric harmony, soothing color palette"
}

@router.post("/api/design/prompt/refine", dependencies=[Depends(verify_token)])
async def refine_prompt(req: RefinePromptRequest):
    """
    🪄 调用后端大模型提炼扩写专业生图 Prompt
    """
    raw_prompt = req.prompt.strip()
    if not raw_prompt:
        raise HTTPException(status_code=400, detail="提示词不能为空")

    chosen_style = req.style or "cinematic"
    style_suffix = STYLE_MODIFIERS.get(chosen_style, STYLE_MODIFIERS["cinematic"])

    engine = get_global_engine()
    ai_adapter = getattr(engine, "translator", None) if engine else None

    # 1. 尝试调用后端已激活的 LLM 进行智能扩写
    if ai_adapter:
        try:
            system_prompt = (
                "You are an expert AI visual art director and prompt engineer for modern diffusion models (FLUX.1, Midjourney, SDXL). "
                "Your job: Transform the user's brief concept into a visually compelling, detailed, atmospheric English prompt. "
                "Include concrete visual elements: subject details, artistic lighting, color harmony, spatial composition, and camera perspective. "
                f"Artistic tone target: {chosen_style}. "
                "CRITICAL RULES: "
                "1. Output ONLY the final polished English prompt text. "
                "2. NEVER include preambles, greetings, quotes, or markdown explanations. "
                "3. Keep the prompt compact, coherent, and under 80 words."
            )
            user_content = f"Brief Concept: {raw_prompt}\nTarget Style: {chosen_style}"
            payload = PayloadManager.prepare_payload(
                ai_adapter, system_prompt, user_content, is_json=False, payload_max_tokens=512
            )

            tlog.info(f"🪄 [PromptRefine] 正在请求大模型提炼视觉提示词: {raw_prompt[:30]}...")
            raw_res = ai_adapter.ask_ai_with_retry(payload) or ""

            # 🛡️ 规约对齐：彻底剥离思维链标签 (<think>...</think>)
            cleaned = re.sub(r'<think>.*?</think>', '', raw_res, flags=re.DOTALL).strip()
            cleaned = cleaned.strip('"`\' \n\r')

            # 过滤诸如 "Here is the prompt:" 的无意义前导词
            cleaned = re.sub(r'^(here\s+is\s+.*?:\s*|prompt:\s*)', '', cleaned, flags=re.IGNORECASE).strip()

            if len(cleaned) > 10:
                tlog.info(f"✨ [PromptRefine] 大模型提炼成功: {cleaned[:50]}...")
                return {
                    "success": True,
                    "refined_prompt": cleaned,
                    "original_prompt": raw_prompt,
                    "engine_used": getattr(ai_adapter, "node_name", "llm_adapter")
                }
        except Exception as e:
            tlog.warning(f"⚠️ [PromptRefine] 大模型提炼调用异常，平滑降级至规则提炼: {e}")

    # 2. 优雅规则保底：智能双语词汇拼装
    fallback_prompt = f"Concept visual art of \"{raw_prompt}\", {style_suffix}, masterpiece, exceptional composition"
    return {
        "success": True,
        "refined_prompt": fallback_prompt,
        "original_prompt": raw_prompt,
        "engine_used": "heuristic_refiner"
    }
