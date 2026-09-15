# -*- coding: utf-8 -*-
"""
🎨 CoverEngine Shard - AI Cover Generator Dispatcher
职责：智能调度系统活跃生图引擎为文稿渲染专属 AI 封面插画。
特性：
1. 智能嗅探已配置且可用的生图驱动（云端 API 或本地开源节点）；
2. 若未配置付费 Key，智能借道免 Key 的高质量摄影插画源（如 Lorem Picsum / Unsplash）；
3. 结合文稿标题、语种与技术分类自动构建高对比度、现代科技感的视觉 Prompt；
4. 容错自愈：发生网络抖动或鉴权异常时，安全返回 None 触发上层阶梯回退。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import os
from typing import Optional, Tuple, Dict, Any
from core.utils.tracing import tlog
from core.design.providers import ProviderRegistry
from core.design.providers.provider_config_manager import ProviderConfigManager

# 优选生图驱动优先级序列 (已配置优先)
AI_PROVIDER_CANDIDATES = [
    "flux",
    "openai",
    "imagen",
    "zhipu",
    "midjourney",
    "stability",
    "comfyui",
    "sd_webui",
    "picsum"  # 100% 免 Key 确定性高清插画保底驱动
]

def _build_ai_prompt(title: str, category: str = "Technology", offset: int = 0) -> str:
    """构建精炼视觉概念 Prompt"""
    clean_title = (title or "Digital Technology Future").strip()
    style_tags = [
        "minimalist modern aesthetic",
        "cyber neon glow and subtle particles",
        "geometric architecture and abstract lighting",
        "clean composition, cinematic atmosphere, 8k resolution"
    ]
    tag_idx = offset % len(style_tags)
    return f"Concept visual art for {clean_title}, {category} topic, {style_tags[tag_idx]}"

def generate_ai_cover(
    title: str,
    category: str = "Technology",
    aspect_ratio: str = "16:9",
    offset: int = 0,
    preferred_provider: Optional[str] = None
) -> Optional[Tuple[bytes, str]]:
    """
    智能调用已就绪的 AI 生图驱动渲染封面。
    返回元组: (图片二进制 bytes, 驱动名称) 或 None
    """
    all_meta = ProviderRegistry.list_supported_providers()
    configured_map: Dict[str, Dict[str, Any]] = {
        item["id"]: item for item in all_meta
    }

    # 1. 确定本次尝试的候选驱动列表
    candidates = []
    if preferred_provider and preferred_provider in configured_map:
        candidates.append(preferred_provider)

    # 优先加入已配置凭据的云端或本地驱动
    for pid in AI_PROVIDER_CANDIDATES:
        if pid in configured_map:
            meta = configured_map[pid]
            if meta.get("is_configured") and pid not in candidates:
                candidates.append(pid)

    # 确保 picsum 作为最后的保底免 Key 生成器
    if "picsum" not in candidates:
        candidates.append("picsum")

    prompt = _build_ai_prompt(title, category, offset)

    for pid in candidates:
        try:
            tlog.info(f"🔮 [AICoverGenerator] 尝试通过驱动 [{pid}] 渲染 AI 封面 (画幅: {aspect_ratio})...")
            provider = ProviderRegistry.create_provider(pid)
            if not provider:
                continue

            img_bytes, err = provider.generate_image(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                style="vivid",
                blur=0
            )

            if img_bytes and len(img_bytes) > 1000:
                tlog.info(f"✨ [AICoverGenerator] 驱动 [{pid}] 成功生成封面 ({len(img_bytes)} 字节)")
                return img_bytes, f"ai_gen ({pid})"
            else:
                tlog.warning(f"⚠️ [AICoverGenerator] 驱动 [{pid}] 出图失败: {err or '空二进制'}")
        except Exception as e:
            tlog.warning(f"⚠️ [AICoverGenerator] 驱动 [{pid}] 发生异常: {e}")

    return None
