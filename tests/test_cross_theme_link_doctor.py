#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Cross-Theme Link Doctor Test Suite
模块职责：跨主题与多语言内链健康巡检测试套件，全面断言五大 SSG 引擎下零 404 死链。
"""

import os
import pytest
from core.governance.link_doctor import CrossThemeLinkDoctor

def test_extract_links_from_markdown():
    """验证从原始 Markdown 中提取双链与标准链接的能力"""
    md = """# 架构文档
参考 [[compute-and-ai|算力中心]] 与 [[themes-and-binding]]。
外部链接：[GitHub](https://github.com/example/repo)。
相对超链：[快速上手](./quick-start.md)。
"""
    links = CrossThemeLinkDoctor.extract_links_from_markdown(md)
    targets = [l["target"] for l in links]
    assert "compute-and-ai" in targets
    assert "themes-and-binding" in targets
    assert "./quick-start.md" in targets
    assert "https://github.com/example/repo" not in targets

@pytest.mark.parametrize("theme", ["sovereign", "universal", "nextra", "starlight", "docusaurus", "vitepress"])
@pytest.mark.parametrize("lang", ["zh", "en", "ja"])
def test_architecture_further_reading_links_across_all_themes(theme, lang):
    """
    🎯 重点断言：验证物理隔离架构文章底部的 3 条“进一步阅读”双链
    在六大主题、中英日三语种下均能 100% 成功转译，且 0 个 404 / 0 个路径异常。
    """
    raw_further_reading_body = """## 🚀 进一步阅读

- 深入算力与缓存中枢：[[compute-and-ai|算力中心与 AI 翻译]]
- 掌握主题装帧定制：[[themes-and-binding|装帧主题与视觉定制]]
- 配置多渠道全网推送：[[distribution-channels|发行矩阵配置]]
"""
    issues = CrossThemeLinkDoctor.diagnose_content_links(
        body=raw_further_reading_body,
        theme_name=theme,
        lang=lang,
        sub_path="docs/architecture.md"
    )
    
    # 严重与错误级问题必须为 0
    criticals = [i for i in issues if i["level"] in ("CRITICAL", "ERROR")]
    assert len(criticals) == 0, f"发现死链异常 ({theme} - {lang}): {criticals}"

def test_full_vault_link_doctor_audit():
    """验证文库全息扫描巡检能力"""
    vault_dir = "vault"
    if not os.path.exists(vault_dir):
        pytest.skip("文库目录不存在，跳过全库扫描")
    
    report = CrossThemeLinkDoctor.run_full_vault_audit(vault_dir)
    assert report["total_files"] > 0
    assert report["total_links"] > 0
    
    criticals = [i for i in report["issues"] if i["level"] in ("CRITICAL", "ERROR")]
    assert len(criticals) == 0, f"全库跨主题巡检发现严重链接问题: {criticals}"
    assert report["passed"] is True

def test_link_doctor_api_endpoints():
    """验证 Link Doctor API 端点调用与鉴权"""
    from fastapi.testclient import TestClient
    from services.api.server import app
    from core.runtime.engine_singleton import get_global_engine
    engine = get_global_engine()
    token = engine.config.system.api_token if engine and hasattr(engine, "config") and hasattr(engine.config, "system") and hasattr(engine.config.system, "api_token") else ""
    headers = {"X-Token": token} if token else {}
    client = TestClient(app)

    # 1. 验证全库体检接口 GET /api/governance/link-doctor/audit
    res_audit = client.get("/api/governance/link-doctor/audit", headers=headers)
    assert res_audit.status_code == 200
    data_audit = res_audit.json()
    assert "total_files" in data_audit
    assert "total_links" in data_audit
    assert "passed" in data_audit

    # 2. 验证单文即时诊断接口 POST /api/governance/link-doctor/diagnose
    test_payload = {
        "body": "## 测试\n参考 [[quick-start|上手指南]]。\n",
        "sub_path": "docs/test_api.md"
    }
    res_diag = client.post("/api/governance/link-doctor/diagnose", json=test_payload, headers=headers)
    assert res_diag.status_code == 200
    data_diag = res_diag.json()
    assert data_diag.get("passed") is True
    assert "nextra" in data_diag.get("themes", [])
    assert "starlight" in data_diag.get("themes", [])

