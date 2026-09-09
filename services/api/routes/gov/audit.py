# -*- coding: utf-8 -*-
"""
🛡️ [V74.56] Gov Configuration Auditing Routes
职责：提供三层配置层级关系与凭据安全审计 API。
"""
from fastapi import APIRouter, Depends
from typing import Optional
from core.runtime.engine_singleton import get_global_engine
from services.api.routes.system import verify_token

router = APIRouter()

@router.get("/api/config/audit", dependencies=[Depends(verify_token)])
def get_config_audit(imprint_id: Optional[str] = None) -> dict:
    """运行三层配置安全继承拓扑审计"""
    engine = get_global_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    
    from core.config.auditor import audit_config_layers
    try:
        report = audit_config_layers(engine.config_manager, imprint_id=imprint_id)
        return report
    except Exception as e:
        return {"error": f"Audit failed: {str(e)}"}

@router.get("/api/governance/audit-logs", dependencies=[Depends(verify_token)])
def get_audit_logs(imprint_id: Optional[str] = None) -> dict:
    """获取操作审计日志列表"""
    engine = get_global_engine()
    if not engine:
        return {"error": "Engine not initialized"}
    try:
        logs = engine.ledger.export_report(imprint_id=imprint_id)
        return {"logs": logs}
    except Exception as e:
        return {"error": f"Failed to fetch audit logs: {str(e)}"}

@router.get("/api/governance/link-doctor/audit", dependencies=[Depends(verify_token)])
def get_link_doctor_audit(imprint_id: Optional[str] = None) -> dict:
    """运行全库跨主题多语言内链健康体检"""
    engine = get_global_engine()
    vault_dir = engine.config.vault_root if engine and hasattr(engine, "config") else "vault"
    from core.governance.link_doctor import CrossThemeLinkDoctor
    try:
        report = CrossThemeLinkDoctor.run_full_vault_audit(vault_dir, engine=engine)
        return report
    except Exception as e:
        return {"error": f"Link Doctor audit failed: {str(e)}", "passed": False, "issues": []}

@router.post("/api/governance/link-doctor/diagnose", dependencies=[Depends(verify_token)])
def diagnose_doc_links(payload: dict) -> dict:
    """针对单篇稿件内容即时诊断跨 5 大主题的链接健康状态"""
    engine = get_global_engine()
    body = payload.get("body", "")
    sub_path = payload.get("sub_path", "docs/untitled.md")
    from core.governance.link_doctor import CrossThemeLinkDoctor
    all_issues = []
    for theme in CrossThemeLinkDoctor.THEMES:
        for lang in CrossThemeLinkDoctor.LOCALES:
            issues = CrossThemeLinkDoctor.diagnose_content_links(
                body=body, theme_name=theme, lang=lang, sub_path=sub_path, engine=engine
            )
            all_issues.extend(issues)
    return {
        "themes": CrossThemeLinkDoctor.THEMES,
        "locales": CrossThemeLinkDoctor.LOCALES,
        "issues": all_issues,
        "passed": len([i for i in all_issues if i["level"] in ("CRITICAL", "ERROR")]) == 0
    }
