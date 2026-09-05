#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Imprint Wizard E2E Flow Regression Test Suite
职责：自动化深度审查与断言品牌建站向导全链路（DOM 结构、6 大主题完整性、默认 Sovereign 选中、前后端数据落盘）。
"""

import os
import yaml
import pytest
from unittest.mock import patch

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODALS_JS = os.path.join(WORKSPACE_ROOT, "web", "dashboard", "js", "ui", "modals.js")
IMPRINTS_JS = os.path.join(WORKSPACE_ROOT, "web", "dashboard", "js", "dashboard.imprints.js")
LAUNCHPAD_JS = os.path.join(WORKSPACE_ROOT, "web", "dashboard", "js", "ui", "launchpad.js")


def test_wizard_modal_dom_topology():
    """断言向导弹窗包含标准的 3 步结构与独立的品牌创建成功就绪确认页组件"""
    with open(MODALS_JS, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 断言向导主容器存在
    assert 'id="imprint-wizard-modal"' in content, "向导弹窗根容器缺少 id='imprint-wizard-modal'"
    
    # 2. 断言 3 个 Step 节点与面板完全镜像
    assert 'id="wiz-node-1"' in content
    assert 'id="wiz-node-2"' in content
    assert 'id="wiz-node-3"' in content
    assert 'id="wiz-step-1"' in content
    assert 'id="wiz-step-2"' in content
    assert 'id="wiz-step-3"' in content

    # 3. 断言步骤标题
    assert "关联原稿文库" in content
    assert "定制品牌与装帧" in content or "品牌名称与装帧" in content
    assert "接入算力与分发" in content or "算力底座与分发" in content

    # 4. 断言独立的出版品牌创建成功就绪确认页组件 (Success Modal & Workbench Handoff)
    assert 'id="imprint-success-modal"' in content
    assert 'id="succ-imprint-brand"' in content
    assert 'id="succ-imprint-theme"' in content
    assert 'id="succ-imprint-vault"' in content
    assert 'id="succ-imprint-compute"' in content
    assert 'id="succ-imprint-lang"' in content
    assert 'id="succ-imprint-dispatch"' in content
    assert 'window.dismissImprintSuccessSwitch' in content
    assert 'window.dismissImprintSuccessStay' in content


def test_wizard_all_six_themes_exist_and_sovereign_default():
    """断言向导 Step 2 中 6 大官方装帧主题全部存在且默认选中 Sovereign"""
    with open(MODALS_JS, "r", encoding="utf-8") as f:
        content = f.read()

    themes = ["sovereign", "universal", "docusaurus", "starlight", "nextra", "vitepress"]
    for th in themes:
        assert f'data-theme="{th}"' in content, f"Step 2 主题选择列表中缺少官方主题: {th}"

    # 断言默认隐藏字段值为 sovereign
    assert 'id="wiz-selected-theme" value="sovereign"' in content or 'value="sovereign"' in content
    # 断言 Sovereign 卡片默认 active
    assert 'data-theme="sovereign"' in content and 'active' in content


def test_wizard_backend_multi_theme_initialization(tmp_path, monkeypatch):
    """断言后端 init_sovereign_imprint 支持写入不同 theme 并在 config.imprint.yaml 中固化"""
    from core.governance.imprint_manager import ImprintManager
    from core.governance.license_guard import LicenseGuard

    imprint_root = str(tmp_path / "imprints")
    os.makedirs(imprint_root, exist_ok=True)
    
    # 实例化 Manager
    im = ImprintManager(root_dir=str(tmp_path))
    im.imprint_root = imprint_root

    with patch.object(LicenseGuard, "get_max_imprints", return_value=10):
        # 1. 默认创建 -> 默认 sovereign
        success = im.init_sovereign_imprint("test_brand_sov", str(tmp_path / "notes"), "Sovereign Brand")
        assert success is True
        cfg_file = os.path.join(imprint_root, "test_brand_sov", "configs", "config.imprint.yaml")
        assert os.path.exists(cfg_file)
        with open(cfg_file, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        assert cfg.get("theme") == "sovereign", f"默认主题未落盘为 sovereign: {cfg.get('theme')}"

        # 2. 指定创建 starlight 主题
        success2 = im.init_sovereign_imprint("test_brand_star", str(tmp_path / "notes"), "Starlight Brand", theme="starlight")
        assert success2 is True
        cfg_file2 = os.path.join(imprint_root, "test_brand_star", "configs", "config.imprint.yaml")
        assert os.path.exists(cfg_file2)
        with open(cfg_file2, "r", encoding="utf-8") as f:
            cfg2 = yaml.safe_load(f)
        assert cfg2.get("theme") == "starlight", f"指定主题未落盘为 starlight: {cfg2.get('theme')}"


def test_launchpad_header_and_sample_theme_text():
    """断言 Launchpad 欢迎文案与标头规范"""
    shards_dir = os.path.join(WORKSPACE_ROOT, "web", "dashboard", "js", "ui", "launchpad_shards")
    shards_content = ""
    if os.path.isdir(shards_dir):
        for fname in sorted(os.listdir(shards_dir)):
            if fname.endswith(".js"):
                with open(os.path.join(shards_dir, fname), "r", encoding="utf-8") as sf:
                    shards_content += sf.read() + "\n"

    with open(LAUNCHPAD_JS, "r", encoding="utf-8") as f:
        content = f.read() + "\n" + shards_content

    assert ("开启您的数字出版与全球分发之旅" in content) or ("欢迎" in content)
    assert "Sovereign 旗舰装帧" in content
    assert "✨ 开启品牌创建向导 (开始建站) →" in content


def test_wizard_vault_isolation_and_picker_guard():
    """断言创建向导文库路径隔离（不预填自带示范文库）以及文件夹拾取器定义完整性"""
    shards_dir = os.path.join(WORKSPACE_ROOT, "web", "dashboard", "js", "imprints", "imprints_shards")
    shards_content = ""
    if os.path.isdir(shards_dir):
        for fname in sorted(os.listdir(shards_dir)):
            if fname.endswith(".js"):
                with open(os.path.join(shards_dir, fname), "r", encoding="utf-8") as sf:
                    shards_content += sf.read() + "\n"

    with open(IMPRINTS_JS, "r", encoding="utf-8") as f:
        imprints_content = f.read() + "\n" + shards_content
    with open(MODALS_JS, "r", encoding="utf-8") as f:
        modals_content = f.read()

    # 1. 断言 window.pickWizardVaultDirectory 存在且完整实现
    assert "window.pickWizardVaultDirectory = async" in imprints_content, "缺少 pickWizardVaultDirectory 定义"
    assert "window.pickWizardVaultDirectory()" in modals_content, "向导模态框按钮缺少 pickWizardVaultDirectory 调用"

    # 2. 断言新建品牌时文库路径必须置空，禁止默认填充自带示范文库
    assert "vaultInput.value = ''" in imprints_content, "向导初始化时未将文库路径置空"
    assert "settingsData?.vault_root" not in imprints_content, "向导中禁止从 settingsData.vault_root 回填演示文库路径"


@pytest.mark.anyio
async def test_imprint_add_uniqueness_audit():
    """断言 /api/imprints/add 接口对品牌名称和品牌 ID 的唯一性拦截校验"""
    from services.api.routes.gov.imprints import add_imprint
    from core.governance.imprint_manager import im

    mock_existing = [
        {"id": "press_tech", "name": "极客前沿", "press_name": "极客前沿"},
        {"id": "press_daily", "name": "每日精选", "press_name": "每日精选"}
    ]

    with patch.object(im, "list_imprints", return_value=mock_existing):
        # 1. 测试品牌 ID 重复拦截
        res_dup_id = await add_imprint({
            "imprint_id": "press_tech",
            "imprint_name": "全新的极客品牌",
            "path": "./manuscripts/test"
        })
        assert res_dup_id["success"] is False
        assert "已存在" in res_dup_id["error"]

        # 2. 测试品牌展示名称重复拦截
        res_dup_name = await add_imprint({
            "imprint_id": "press_brand_new",
            "imprint_name": "极客前沿",
            "path": "./manuscripts/test"
        })
        assert res_dup_name["success"] is False
        assert "已被占用" in res_dup_name["error"]


def test_wizard_step3_dom_topology():
    """断言向导 Step 3 包含渐进式开箱概要与高级自定义配置项 DOM 结构"""
    with open(MODALS_JS, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 渐进式呈现双层容器
    assert 'id="wiz-step3-streamlined-view"' in content
    assert 'id="wiz-step3-custom-view"' in content
    assert 'id="wiz-summary-compute-title"' in content
    assert 'id="wiz-summary-dispatch-title"' in content

    # 2. 算力引擎卡片与隐藏字段
    assert 'id="wiz-ai-provider"' in content
    assert 'id="wiz-probe-badge"' in content
    assert 'data-provider="deepseek"' in content
    assert 'data-provider="siliconflow"' in content
    assert 'data-provider="lmstudio"' in content
    assert 'data-provider="none"' in content

    # 3. 🎯 模型选择下拉框与状态
    assert 'id="wiz-ai-model-select"' in content
    assert 'id="wiz-model-status"' in content

    # 4. API 密钥输入
    assert 'id="wiz-ai-key"' in content

    # 5. 目标语种矩阵药丸
    assert 'data-lang="en"' in content
    assert 'data-lang="ja"' in content
    assert 'data-lang="de"' in content

    # 6. 全域分发渠道卡片与隐藏字段
    assert 'id="wiz-dispatch-platform"' in content
    assert 'data-dispatch="github_pages"' in content
    assert 'data-dispatch="cloudflare_pages"' in content
    assert 'data-dispatch="local_preview"' in content

    # 7. 🚀 真实分发托管展开式面板
    assert 'id="wiz-dispatch-github-pane"' in content
    assert 'id="wiz-gh-repo"' in content
    assert 'id="wiz-gh-token"' in content
    assert 'id="wiz-gh-branch"' in content
    assert 'id="wiz-dispatch-cloudflare-pane"' in content
    assert 'id="wiz-cf-project"' in content


def test_wizard_compute_probe_api():
    """断言 /api/compute/probe 能正常返回本地算力与凭据发现状态"""
    from services.api.routes.compute import probe_compute
    res = probe_compute()
    assert "local_nodes" in res
    assert "has_local_compute" in res
    assert "recommended_provider" in res
    assert "github" in res


@pytest.mark.anyio
async def test_wizard_step3_backend_persistence(tmp_path, monkeypatch):
    """断言 /api/imprints/add 成功将 Step 3 的算力、真实模型与分发托管参数完整写入 config.imprint.yaml"""
    from services.api.routes.gov.imprints import add_imprint
    from core.governance.imprint_manager import im
    from core.governance.license_guard import LicenseGuard

    imprint_root = str(tmp_path / "imprints")
    monkeypatch.setattr(im, "imprint_root", imprint_root)

    with patch.object(LicenseGuard, "get_max_imprints", return_value=10):
        res = await add_imprint({
            "imprint_id": "press_global_news",
            "imprint_name": "全球科技观察",
            "path": str(tmp_path / "vault"),
            "theme": "sovereign",
            "enable_ai": True,
            "ai_provider": "lmstudio",
            "ai_model": "qwen2.5-7b-instruct",
            "ai_api_key": "",
            "target_langs": ["en", "ja", "de"],
            "deploy_platform": "github_pages",
            "deploy_repo": "geek/my-press-site",
            "deploy_token": "ghp_mock_token_123456",
            "deploy_branch": "gh-pages"
        })
        assert res["success"] is True

        cfg_file = os.path.join(imprint_root, "press_global_news", "configs", "config.imprint.yaml")
        assert os.path.exists(cfg_file)
        with open(cfg_file, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        assert cfg.get("imprint_name") == "全球科技观察"
        assert cfg.get("target_languages") == ["en", "ja", "de"]
        assert cfg.get("translation", {}).get("enable_ai") is True
        assert cfg.get("translation", {}).get("primary_node") in ("lmstudio", "lmstudio_local")
        assert cfg.get("governance", {}).get("deploy_platform") == "github_pages"
        assert cfg.get("distribution", {}).get("github_repo") == "geek/my-press-site"
        assert cfg.get("distribution", {}).get("github_branch") == "gh-pages"



