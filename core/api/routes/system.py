# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Header, HTTPException
from typing import Optional
from core.runtime.cli_bootstrap import get_global_engine
from core.logic.orchestration.task_orchestrator import global_executor
import signal
import os

router = APIRouter()

def verify_token(x_token: Optional[str] = Header(None, alias="X-Token")):
    engine = get_global_engine()
    if not engine or not engine.config.system.api_token: return
    if x_token != engine.config.system.api_token:
        raise HTTPException(status_code=403, detail="Unauthorized")

@router.get("/health")
def health_check():
    return {"status": "online", "engine": "Illacme-plenipes"}

@router.get("/stats", dependencies=[Depends(verify_token)])
def get_stats():
    engine = get_global_engine()
    if not engine: return {"error": "Engine not initialized"}
    return {
        "usage": engine.meter.get_summary_report(),
        "active_workers": len([t for t in global_executor.workers if t.is_alive()])
    }

@router.post("/shutdown", dependencies=[Depends(verify_token)])
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)
    return {"status": "accepted"}
