# -*- coding: utf-8 -*-
"""
🎨 Design Studio & Image Creation REST API Routes
职责：提供设计中心、图像策略与封面即时工作室的 RESTful API 接口。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import os
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from core.runtime.engine_singleton import get_global_engine
from core.design.image_hub import image_hub
from core.utils.tracing import tlog

from .design_shards import assets_router, prompt_router, hosting_router, upload_router, batch_router

router = APIRouter()
router.include_router(assets_router)
router.include_router(prompt_router)
router.include_router(hosting_router)
router.include_router(upload_router)
router.include_router(batch_router)
from .system import verify_token

class CoverPreviewRequest(BaseModel):
    doc_id: str
    strategy: Optional[str] = "auto"
    aspect_ratio: Optional[str] = "16:9"
    offset: Optional[int] = 0
    title: Optional[str] = None
    lang_code: Optional[str] = None
    focal_y: Optional[float] = 0.5
    focal_x: Optional[float] = 0.5

class ImagePolicyUpdateRequest(BaseModel):
    default_strategy: str = "auto"
    aspect_ratio: str = "16:9"
    enable_watermark: bool = True
    unsplash_query: Optional[str] = "technology,minimalist"

from .design_shards.cover_asset_healer import serve_cover_asset_or_heal, serve_default_cover

@router.get("/api/design/assets/covers/{filename}")
async def get_cover_asset(filename: str):
    """静态文件服务：向前端安全返回封面图片（集成 JIT 即时自愈与零 404 防线）"""
    engine = get_global_engine()
    vault_root = getattr(engine, "vault_root", os.getcwd()) if engine else os.getcwd()
    return serve_cover_asset_or_heal(filename, vault_root=vault_root)

@router.get("/api/design/assets/default-cover.jpg")
async def get_default_cover_asset():
    """官方统一默认科技感极光毛玻璃占位封面端点"""
    engine = get_global_engine()
    vault_root = getattr(engine, "vault_root", os.getcwd()) if engine else os.getcwd()
    return serve_default_cover(vault_root=vault_root)

@router.post("/api/design/cover/preview", dependencies=[Depends(verify_token)])
async def preview_cover(req: CoverPreviewRequest):
    """
    单篇封面即时解析与渲染端点。
    供社媒分发抽屉 (Syndicate Drawer) 实时切换策略与预览使用。
    """
    engine = get_global_engine()
    doc_id = req.doc_id
    title = req.title or ""
    author = "Illacme Plenipes"
    category = "Engineering"
    slug = ""
    brand_id = "default"
    brand_name = "ILLACME SOVEREIGN"

    if engine:
        brand_id = getattr(engine, "imprint_id", "default") or "default"
        vault_root = getattr(engine, "vault_root", os.getcwd())
        image_hub.vault_root = vault_root
        image_hub.cache_dir = os.path.join(vault_root, ".plenipes", "cache", "covers")
        os.makedirs(image_hub.cache_dir, exist_ok=True)

        doc_meta = engine.meta.get_doc_info(doc_id) if hasattr(engine, "meta") else None
        if doc_meta:
            title = title or doc_meta.get("title") or os.path.basename(doc_id)
            slug, author, category = doc_meta.get("slug") or "", doc_meta.get("author") or author, doc_meta.get("category") or category
    
        if req.lang_code and str(req.lang_code).lower() not in ("auto", "source", "zh", "zh-hans"):
            try:
                from services.api.logic.dispatch_ops_shards.pipeline_shards.pipeline_syndicate_loader import load_syndicated_article_payload
                t_payload = load_syndicated_article_payload(engine, doc_id, req.lang_code)
                if t_payload and t_payload.get("title"): title = t_payload["title"]
            except Exception: pass

        existing_cover = (doc_meta.get("cover") or "") if doc_meta else ""
        if not existing_cover and engine:
            try:
                from services.api.logic.content_ops_shards.safe_ops import resolve_safe_path
                from core.utils.text import parse_frontmatter
                p = resolve_safe_path(engine, doc_id) or resolve_safe_path(engine, f"{doc_id}.md")
                if p and os.path.isfile(p):
                    with open(p, "r", encoding="utf-8") as f: existing_cover = parse_frontmatter(f.read())[0].get("cover") or ""
            except Exception: pass
        if existing_cover and (not req.strategy or req.strategy in ("auto", "global", "doc_frontmatter")) and (req.offset or 0) == 0:
            target_r = req.aspect_ratio or "16:9"
            if target_r not in ("16:9", "auto", "default", "none"):
                from core.design.cover_engine.cover_deriver import derive_cover_asset
                d_url, d_bytes = derive_cover_asset(existing_cover, target_r, focal_y=req.focal_y or 0.5, focal_x=req.focal_x or 0.5, vault_root=vault_root)
                if d_url:
                    return {"success": True, "doc_id": doc_id, "strategy_used": "doc_frontmatter", "url": d_url, "cover_url": d_url, "size_bytes": len(d_bytes) if d_bytes else 0, "aspect_ratio": target_r, "title": title}
            return {"success": True, "doc_id": doc_id, "strategy_used": "doc_frontmatter", "url": existing_cover, "cover_url": existing_cover, "size_bytes": 0, "aspect_ratio": target_r, "title": title}

    if not title: title = os.path.splitext(os.path.basename(doc_id))[0]

    rel_url, img_bytes, used_strat = image_hub.generate_cover_for_document(
        doc_id=doc_id,
        title=title,
        slug=slug,
        author=author,
        category=category,
        brand_id=brand_id,
        brand_name=brand_name,
        strategy=req.strategy or "auto",
        aspect_ratio=req.aspect_ratio or "16:9",
        offset=req.offset or 0
    )

    return {
        "success": True,
        "doc_id": doc_id,
        "strategy_used": used_strat,
        "url": rel_url,
        "cover_url": rel_url,
        "size_bytes": len(img_bytes),
        "aspect_ratio": req.aspect_ratio or "16:9",
        "title": title
    }

@router.get("/api/gov/image-policy", dependencies=[Depends(verify_token)])
async def get_image_policy():
    """读取当前品牌的图像策略配置"""
    engine = get_global_engine()
    if not engine or not getattr(engine, "config", None):
        return {"default_strategy": "auto", "aspect_ratio": "16:9", "enable_watermark": True}
    
    img_policy = getattr(engine.config, "image_policy", {}) or {}
    if hasattr(img_policy, "model_dump"): img_policy = img_policy.model_dump()
    elif hasattr(img_policy, "__dict__"): img_policy = img_policy.__dict__
    elif not isinstance(img_policy, dict): img_policy = {}

    return {
        "default_strategy": img_policy.get("default_strategy", "auto"),
        "aspect_ratio": img_policy.get("aspect_ratio", "16:9"),
        "enable_watermark": img_policy.get("enable_watermark", True),
        "unsplash_query": img_policy.get("unsplash_query", "technology,minimalist")
    }

@router.post("/api/gov/image-policy", dependencies=[Depends(verify_token)])
async def update_image_policy(req: ImagePolicyUpdateRequest):
    """保存并持久化当前品牌的图像策略配置"""
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not ready")

    from services.api.routes.gov.config_shards.config_persistence_ops import persist_config_to_disk
    from services.api.routes.gov.config_shards.config_reload_ops import live_reload_engine_config

    payload = {
        "image_policy": {
            "default_strategy": req.default_strategy,
            "aspect_ratio": req.aspect_ratio,
            "enable_watermark": req.enable_watermark,
            "unsplash_query": req.unsplash_query
        }
    }

    try:
        imprint_id = getattr(engine, "imprint_id", "default") or "default"
        persist_config_to_disk(engine, payload, imprint_id=imprint_id)
        live_reload_engine_config(engine, payload)
        tlog.info(f"✨ [图像策略] 品牌 {imprint_id} 图像策略已持久化成功: {req.default_strategy}")
        return {"success": True, "message": "图像策略已成功保存并实时生效"}
    except Exception as e:
        tlog.error(f"🛑 [图像策略] 保存失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class ProviderTestRequest(BaseModel):
    provider_id: str
    config: Optional[Dict[str, Any]] = None

class ImageGenerateRequest(BaseModel):
    provider_id: str = "unsplash"
    prompt: str
    aspect_ratio: str = "16:9"
    style: str = "vivid"
    doc_id: Optional[str] = ""
    config: Optional[Dict[str, Any]] = None

class ProviderSaveConfigRequest(BaseModel):
    provider_id: str
    config: Dict[str, Any]

class ProviderSyncComputeRequest(BaseModel):
    provider_id: str = "openai"
    node_id: Optional[str] = None

@router.get("/api/design/providers", dependencies=[Depends(verify_token)])
async def list_image_providers():
    """获取所有支持的生图驱动及其表单元数据"""
    from core.design.providers import ProviderRegistry
    return {"success": True, "providers": ProviderRegistry.list_supported_providers()}

@router.get("/api/design/providers/config", dependencies=[Depends(verify_token)])
async def get_providers_config(provider_id: str = "openai"):
    """获取已持久化的生图驱动配置与算力基座智能候选"""
    from core.design.providers.provider_config_manager import ProviderConfigManager
    return {
        "success": True,
        "configs": ProviderConfigManager.get_all_configs(mask_secrets=True),
        "suggested": ProviderConfigManager.detect_suggested_credentials(provider_id)
    }

@router.post("/api/design/providers/config", dependencies=[Depends(verify_token)])
async def save_provider_config(req: ProviderSaveConfigRequest):
    """保存并持久化指定生图引擎的参数配置"""
    from core.design.providers.provider_config_manager import ProviderConfigManager
    ok = ProviderConfigManager.save_provider_config(req.provider_id, req.config)
    return {"success": ok, "message": "配置已成功保存并实时生效" if ok else "保存失败"}

@router.post("/api/design/providers/sync-compute", dependencies=[Depends(verify_token)])
async def sync_provider_from_compute(req: ProviderSyncComputeRequest):
    """一键从算力中心同源节点导入凭据"""
    from core.design.providers.provider_config_manager import ProviderConfigManager
    suggested = ProviderConfigManager.detect_suggested_credentials(req.provider_id)
    node_id = req.node_id or suggested.get("raw_node_id")
    if not node_id:
        return {"success": False, "message": f"未在算力基座中探测到可用的 [{req.provider_id}] 兼容节点"}
    ok = ProviderConfigManager.import_credentials_from_compute_node(req.provider_id, node_id)
    return {"success": ok, "message": f"已成功从算力节点 [{node_id}] 同步凭据" if ok else "同步失败"}

@router.post("/api/design/providers/test", dependencies=[Depends(verify_token)])
async def test_image_provider(req: ProviderTestRequest):
    """测试生图驱动连通性与鉴权"""
    from core.design.providers import ProviderRegistry
    res = ProviderRegistry.test_provider_connection(req.provider_id, req.config)
    return res

@router.post("/api/design/generate", dependencies=[Depends(verify_token)])
async def generate_image_asset(req: ImageGenerateRequest):
    """
    🎨 设计中心自由生图工作台端点
    调用指定 Provider 生成图片、落盘缓存并记录进物权资产表
    """
    import hashlib
    import time
    from core.design.providers import ProviderRegistry
    engine = get_global_engine()
    vault_root = getattr(engine, "vault_root", os.getcwd()) if engine else os.getcwd()

    provider = ProviderRegistry.create_provider(req.provider_id, req.config)
    if not provider:
        raise HTTPException(status_code=400, detail=f"不支持的生图驱动: {req.provider_id}")

    img_bytes, err = provider.generate_image(
        prompt=req.prompt,
        aspect_ratio=req.aspect_ratio,
        style=req.style
    )
    if err or not img_bytes:
        return {"success": False, "message": err or "生图失败"}

    # 缓存落盘
    covers_dir = os.path.join(vault_root, ".plenipes", "cache", "covers")
    os.makedirs(covers_dir, exist_ok=True)
    hash_seed = f"{req.provider_id}_{req.prompt}_{time.time()}"
    fn = f"gen_{hashlib.md5(hash_seed.encode('utf-8')).hexdigest()[:12]}.jpg"
    full_path = os.path.join(covers_dir, fn)

    with open(full_path, "wb") as f:
        f.write(img_bytes)

    rel_url = f"/api/design/assets/covers/{fn}"

    # 物权账本记录
    if engine and hasattr(engine, "meta"):
        image_hub.record_visual_asset(
            meta_manager=engine.meta,
            rel_path=req.doc_id or "studio_generation",
            asset_type="cover",
            strategy=f"ai_{req.provider_id}",
            source_url=rel_url,
            prompt=req.prompt
        )

    return {
        "success": True,
        "url": rel_url,
        "size_bytes": len(img_bytes),
        "aspect_ratio": req.aspect_ratio,
        "provider": req.provider_id
    }
