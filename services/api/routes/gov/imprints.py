# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Imprint Management Routes (Dispatch Hub)
职责：承载出版品牌 (Imprint) 的枚举、切换、创建与删除等核心治理路由枢纽。
架构：已按照 SOP-01 与 SOP-02 物理拆分至 imprints_shards/ 原子分片，消除大单体红线。
"""

from fastapi import APIRouter, Depends, Query
from core.runtime.engine_singleton import get_global_engine
from ..system import verify_token
from .imprints_shards import (
    check_vault_binding_logic,
    get_imprints_stats_logic,
    add_imprint_logic,
    delete_imprint_logic,
    switch_imprint_logic,
)

router = APIRouter()


@router.get("/api/imprints", dependencies=[Depends(verify_token)])
def list_imprints():
    """🏷️ 获取所有出版品牌列表与当前激活品牌"""
    from core.governance.imprint_manager import im
    return {"imprints": im.list_imprints(), "active": im.get_active_imprint()}


@router.get("/api/imprints/check-vault", dependencies=[Depends(verify_token)])
def check_vault_binding(path: str = Query("", description="待检测的文库物理路径")):
    """🔍 检查所选原稿文库路径是否已被其他出版品牌绑定"""
    return check_vault_binding_logic(path)


@router.get("/api/imprints/stats", dependencies=[Depends(verify_token)])
def get_imprints_stats():
    """🚀 [V52.22] 跨品牌资产大盘与环境健康统计"""
    return get_imprints_stats_logic()


@router.post("/api/imprints/add", dependencies=[Depends(verify_token)])
async def add_imprint(req: dict):
    """🚀 创建新的出版品牌并初始化赋能配置"""
    return await add_imprint_logic(req)


@router.post("/api/imprints/switch", dependencies=[Depends(verify_token)])
async def switch_imprint(req: dict):
    """🚀 热切换当前出版品牌并触发深度重载"""
    return await switch_imprint_logic(req)


@router.post("/api/imprints/delete", dependencies=[Depends(verify_token)])
async def delete_imprint(req: dict):
    """🛡️ 物理注销出版品牌"""
    return await delete_imprint_logic(req)


__all__ = [
    "router",
    "list_imprints",
    "check_vault_binding",
    "get_imprints_stats",
    "add_imprint",
    "switch_imprint",
    "delete_imprint",
    "get_global_engine",
]
