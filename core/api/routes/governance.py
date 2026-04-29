# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends
from core.runtime.cli_bootstrap import get_global_engine
from .system import verify_token

router = APIRouter()

@router.get("/api/billing/stats", dependencies=[Depends(verify_token)])
def get_billing_stats():
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    from core.governance.audit_ledger import ledger
    return {
        "daily_spent": ledger.get_today_cost(),
        "weekly_trend": ledger.get_weekly_stats()
    }

@router.get("/api/territories", dependencies=[Depends(verify_token)])
def list_territories():
    from core.governance.territory_manager import wm
    return {"territories": wm.list_territories(), "active": wm.get_active_territory()}

