# -*- coding: utf-8 -*-
"""
🛡️ [V100.8] License Management API Routes (设备准入与许可治理路由)
职责：暴露获取设备机器指纹、准入状态查询、许可证激活落盘及注销接口。
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
from core.governance.license_guard import LicenseGuard
from ..system import verify_token

router = APIRouter()

class ActivateRequest(BaseModel):
    license_text: str

@router.get("/api/governance/license/info", dependencies=[Depends(verify_token)])
async def get_license_info() -> Dict[str, Any]:
    """获取设备唯一标识 (机器指纹)、许可证状态及准入能力清单"""
    return LicenseGuard.get_license_info()

@router.post("/api/governance/license/activate", dependencies=[Depends(verify_token)])
async def activate_license(req: ActivateRequest) -> Dict[str, Any]:
    """点火激活并物理落盘准入许可证"""
    if not req.license_text:
        return {"status": "error", "message": "许可证数据为空"}

    success, message = LicenseGuard.activate_license(req.license_text)
    if success:
        return {"status": "success", "message": message, "info": LicenseGuard.get_license_info()}
    return {"status": "error", "message": message}

@router.post("/api/governance/license/revoke", dependencies=[Depends(verify_token)])
@router.delete("/api/governance/license/revoke", dependencies=[Depends(verify_token)])
async def revoke_license() -> Dict[str, Any]:
    """注销并解绑当前准入许可证"""
    success, message = LicenseGuard.revoke_license()
    if success:
        return {"status": "success", "success": True, "message": message, "info": LicenseGuard.get_license_info()}
    return {"status": "error", "success": False, "message": message}
