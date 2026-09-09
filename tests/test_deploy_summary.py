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


