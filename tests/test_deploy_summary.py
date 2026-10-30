# -*- coding: utf-8 -*-
from unittest.mock import MagicMock
from core.bindery.deployment_manager import DeploymentManager

def test_deployment_summary_generation():
    """验证全域发布完成后推送统计汇总与访问 URL 推导逻辑"""
    mock_config = MagicMock()
    mock_config.publish_control = {
        "primary_hosting_id": "vercel"
    }

    mgr = DeploymentManager(imprint_config=mock_config)

    # 构造 mock publisher
    mock_vercel = MagicMock()
    mock_vercel.__class__.__name__ = "VercelPublisher"
    mock_vercel.PLUGIN_ID = "vercel"
    mock_vercel.project_name = "illacme-press"

    mock_gh = MagicMock()
    mock_gh.__class__.__name__ = "GitHubPagesPublisher"
    mock_gh.PLUGIN_ID = "github_pages"
    mock_gh._parse_owner_repo.return_value = ("ziyuandaili", "illacme-press")

    mgr.publishers = [mock_vercel, mock_gh]

    # 模拟推送结果
    mock_results = {
        "channels": {
            "VercelPublisher": {
                "status": "success",
                "files": 12,
                "response": {"url": "https://illacme-press.vercel.app/"}
            },
            "GitHubPagesPublisher": {
                "status": "success",
                "files": 12,
                "response": {}
            }
        }
    }

    summary = mgr._build_deployment_summary(mock_results)
    assert summary["total_channels"] == 2
    assert summary["success_count"] == 2
    assert summary["fail_count"] == 0

    # 渠道 0 应该为官方主站 Vercel
    ch0 = summary["channels"][0]
    assert ch0["name"] == "Vercel"
    assert ch0["is_primary"] is True
    assert ch0["url"] == "https://illacme-press.vercel.app/"

    # 渠道 1 应该为 GitHub Pages，且自动推导出 https://ziyuandaili.github.io/illacme-press/
    ch1 = summary["channels"][1]
    assert ch1["name"] == "GitHub Pages"
    assert ch1["is_primary"] is False
    assert ch1["url"] == "https://ziyuandaili.github.io/illacme-press/"


def test_vercel_hash_instance_url_normalization():
    """验证即使 Vercel CLI 返回带有 hash 的部署实例 URL，在生产模式下依然稳定归一化为官方主站域名"""
    mock_config = MagicMock()
    mock_config.publish_control = {
        "primary_hosting_id": "vercel"
    }

    mgr = DeploymentManager(imprint_config=mock_config)

    mock_vercel = MagicMock()
    mock_vercel.__class__.__name__ = "VercelPublisher"
    mock_vercel.PLUGIN_ID = "vercel"
    mock_vercel.project_name = "illacme-press"
    mock_vercel.prod = True

    mgr.publishers = [mock_vercel]

    mock_results = {
        "channels": {
            "VercelPublisher": {
                "status": "success",
                "files": 12,
                "response": {
                    "url": "https://illacme-press-3na3i4kv9-acme-31eb.vercel.app",
                    "deployment_url": "https://illacme-press-3na3i4kv9-acme-31eb.vercel.app"
                }
            }
        }
    }

    summary = mgr._build_deployment_summary(mock_results)
    ch0 = summary["channels"][0]
    assert ch0["name"] == "Vercel"
    assert ch0["is_primary"] is True
    assert ch0["url"] == "https://illacme-press.vercel.app/"


def test_primary_channel_first_ordering():
    """验证当将 GitHub Pages 设为主站时，主站渠道必定被稳定排在第一位率先投递"""
    mock_config = MagicMock()
    mock_config.publish_control = {
        "primary_hosting_id": "github_pages"
    }

    mgr = DeploymentManager(imprint_config=mock_config)

    mock_vercel = MagicMock()
    mock_vercel.__class__.__name__ = "VercelPublisher"
    mock_vercel.PLUGIN_ID = "vercel"
    mock_vercel.project_name = "illacme-press"
    mock_vercel.prod = True
    mock_vercel.get_proxy.return_value = None
    mock_vercel.push.return_value = {"status": "success", "url": "https://illacme-press.vercel.app/"}

    mock_gh = MagicMock()
    mock_gh.__class__.__name__ = "GitHubPagesPublisher"
    mock_gh.PLUGIN_ID = "github_pages"
    mock_gh.get_proxy.return_value = None
    mock_gh._parse_owner_repo.return_value = ("Illacme", "illacme-press")
    mock_gh.push.return_value = {"status": "success", "url": "https://illacme.github.io/illacme-press/"}

    # 故意将 Vercel 放在前面
    mgr.publishers = [mock_vercel, mock_gh]

    # 执行排序
    mgr._sort_publishers_by_primary()

    # 断言 GitHub Pages 被提升到第 0 位（率先投递）
    assert mgr.publishers[0].PLUGIN_ID == "github_pages"
    assert mgr.publishers[1].PLUGIN_ID == "vercel"

    # 验证 deploy_all 执行时传递的 metadata 中携带正确的 is_primary 与 channel_role
    mgr.deploy_all(bundle_path="/fake/path", metadata={"version": "1.0"})

    gh_meta = mock_gh.push.call_args[0][1]
    assert gh_meta["is_primary"] is True
    assert gh_meta["channel_role"] == "primary"

    vercel_meta = mock_vercel.push.call_args[0][1]
    assert vercel_meta["is_primary"] is False
    assert vercel_meta["channel_role"] == "mirror"


def test_audit_ledger_get_recent_logs(tmp_path):
    """验证 AuditLedger.get_recent_logs 支持分类筛选与 metadata 自动反序列化"""
    from core.governance.audit_ledger import AuditLedger
    db_file = str(tmp_path / "test_audit.db")
    ledger = AuditLedger(db_file)

    ledger.log("AI_TRANSACTION", "Model inference", metadata={"cost": 0.05})
    ledger.log("GLOBAL_DEPLOY", "Deploy done", metadata={"summary": {"total_channels": 2, "channels": []}})

    # 查询 GLOBAL_DEPLOY
    deploy_logs = ledger.get_recent_logs(category="GLOBAL_DEPLOY", limit=1)
    assert len(deploy_logs) == 1
    assert deploy_logs[0]["event_type"] == "GLOBAL_DEPLOY"
    assert isinstance(deploy_logs[0]["metadata"], dict)
    assert deploy_logs[0]["metadata"]["summary"]["total_channels"] == 2

    # 查询全部并限制条数
    all_logs = ledger.get_recent_logs(limit=2)
    assert len(all_logs) == 2


def test_get_deployment_summary_api_fallbacks(monkeypatch):
    """验证 /api/governance/deployment-summary 在各种状态下的防御性返回 (绝不返回 None 触发 ResponseValidationError)"""
    import asyncio
    from services.api.routes.gov.actions import get_deployment_summary

    # Case 1: 引擎尚未初始化
    monkeypatch.setattr("services.api.routes.gov.actions.get_global_engine", lambda: None)
    res_no_engine = asyncio.run(get_deployment_summary())
    assert isinstance(res_no_engine, dict)
    assert res_no_engine["status"] == "error"

    # Case 2: 引擎无任何部署与批次历史 (空状态下稳定返回 dict，绝不返回 None)
    mock_engine = MagicMock()
    mock_engine.last_deployment_results = None
    mock_engine.ledger.get_recent_logs.return_value = []
    mock_engine.meta.list_hosting_deploy_batches.return_value = []
    monkeypatch.setattr("services.api.routes.gov.actions.get_global_engine", lambda: mock_engine)

    res_empty = asyncio.run(get_deployment_summary())
    assert isinstance(res_empty, dict)
    assert res_empty["status"] == "empty"
    assert res_empty["summary"] is None

    # Case 3: 从 ledger 恢复
    mock_engine.ledger.get_recent_logs.return_value = [
        {"metadata": {"summary": {"total_channels": 1, "success_count": 1, "fail_count": 0, "channels": [{"id": "gh"}]}}}
    ]
    res_ledger = asyncio.run(get_deployment_summary())
    assert isinstance(res_ledger, dict)
    assert res_ledger["status"] == "success"
    assert res_ledger["summary"]["total_channels"] == 1

    # Case 4: ledger 无记录但 SQLite 托管批次账本存在历史
    mock_engine.ledger.get_recent_logs.return_value = []
    mock_engine.meta.list_hosting_deploy_batches.return_value = [
        {
            "targets": {
                "vercel": {"status": "SUCCESS", "url": "https://test.vercel.app", "duration_sec": 1.2},
                "github": {"status": "FAILED", "error": "timeout", "duration_sec": 5.0}
            },
            "started_at": "2026-10-30 11:00:00"
        }
    ]
    res_batch = asyncio.run(get_deployment_summary())
    assert isinstance(res_batch, dict)
    assert res_batch["status"] == "success"
    summary = res_batch["summary"]
    assert summary["total_channels"] == 2
    assert summary["success_count"] == 1
    assert summary["fail_count"] == 1



