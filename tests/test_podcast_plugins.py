# -*- coding: utf-8 -*-
"""
🧪 Test Suite for Podcast Plugins in Plugin Center (能力矩阵播客平台)
验证：
1. 插件矩阵装配器组装出的 podcast 分类插件列表完整性；
2. 播客全网发行 (podcast_hub)、小宇宙 (podcast_xiaoyuzhou)、Apple Podcasts、Spotify 平台元数据；
3. 播客凭据就绪校验器 (is_plugin_config_ready) 逻辑；
4. 插件中心物理自检探测 API (/api/plugins/probe) 联动；
5. 全域活动插件列表 API (/api/plugins/list) 包含 podcast 类别。
🛡️ [SOP-01] 物理行数严格收敛于 300 行以内。
"""

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from services.api.server import app
from services.api.routes.gov.plugin_mapper import assemble_plugin_matrix
from services.api.routes.gov.plugin_collector_channels import (
    is_plugin_config_ready
)

client = TestClient(app)


def test_assemble_plugin_matrix_contains_podcast_category():
    """验证插件矩阵中包含完整的 podcast 分类插件"""
    engine_mock = MagicMock()
    engine_mock.config.podcast = {}
    engine_mock.config.plugins.disabled_plugins = []
    engine_mock.config.active_theme = "default"

    with patch("services.api.routes.gov.plugin_mapper.get_global_engine", return_value=engine_mock):
        matrix = assemble_plugin_matrix()

    podcast_plugins = [p for p in matrix if p.get("category") == "podcast"]
    assert len(podcast_plugins) == 5

    p_ids = [p["id"] for p in podcast_plugins]
    assert "podcast_hub" in p_ids
    assert "podcast_xiaoyuzhou" in p_ids
    assert "podcast_apple" in p_ids
    assert "podcast_spotify" in p_ids
    assert "podcast_r2_storage" in p_ids

    hub = next(p for p in podcast_plugins if p["id"] == "podcast_hub")
    assert hub["category_name"] == "🎙️ 播客平台"
    assert hub["is_in_use"] is True
    assert hub["is_manageable"] is True
    assert hub["is_configurable"] is True


def test_podcast_config_readiness():
    """验证播客平台凭据就绪判定逻辑"""
    # 1. podcast_hub 自带开箱即用默认配置，无需必填第三方 token
    assert is_plugin_config_ready("podcast", "podcast_hub", {}) is True

    # 2. 小宇宙需要有效 token 或 podcast_id
    assert is_plugin_config_ready("podcast", "podcast_xiaoyuzhou", {}) is False
    assert is_plugin_config_ready("podcast", "podcast_xiaoyuzhou", {"token": ""}) is False
    assert is_plugin_config_ready("podcast", "podcast_xiaoyuzhou", {"token": "YOUR_TOKEN"}) is False
    assert is_plugin_config_ready("podcast", "podcast_xiaoyuzhou", {"token": "valid_token_123"}) is True
    assert is_plugin_config_ready("podcast", "podcast_xiaoyuzhou", {"podcast_id": "xyz_123"}) is True

    # 3. Apple Podcasts
    assert is_plugin_config_ready("podcast", "podcast_apple", {}) is False
    assert is_plugin_config_ready("podcast", "podcast_apple", {"apple_id": "1234567890"}) is True

    # 4. Spotify
    assert is_plugin_config_ready("podcast", "podcast_spotify", {}) is False
    assert is_plugin_config_ready("podcast", "podcast_spotify", {"show_id": "spotify_show_123"}) is True


def test_api_plugins_list_endpoint():
    """测试 /api/plugins/list API 端点中包含 podcast 插件"""
    engine_mock = MagicMock()
    engine_mock.config.podcast = {}
    engine_mock.config.plugins.disabled_plugins = []
    engine_mock.config.active_theme = "default"

    with patch("services.api.routes.gov.context_shards.plugin_ops.get_global_engine", return_value=engine_mock), \
         patch("services.api.routes.gov.plugin_mapper.get_global_engine", return_value=engine_mock):
        resp = client.get("/api/plugins/list")

    assert resp.status_code == 200
    data = resp.json()
    assert "plugins" in data
    podcasts = [p for p in data["plugins"] if p.get("category") == "podcast"]
    assert len(podcasts) == 5
    ids = {p["id"] for p in podcasts}
    assert ids == {"podcast_hub", "podcast_xiaoyuzhou", "podcast_apple", "podcast_spotify", "podcast_r2_storage"}


def test_api_plugins_probe_endpoint():
    """测试 /api/plugins/probe 探测端点对各类播客平台的响应"""
    engine_mock = MagicMock()
    engine_mock.config.podcast = {}
    with patch("services.api.routes.gov.context_shards.plugin_ops.get_global_engine", return_value=engine_mock):
        for pid in ["podcast_hub", "podcast_xiaoyuzhou", "podcast_apple", "podcast_spotify", "podcast_r2_storage"]:
            resp = client.post("/api/plugins/probe", json={"id": pid, "category": "podcast"})
            assert resp.status_code == 200
            result = resp.json()
            assert result["success"] is True
            assert "healthy" in result
            assert len(result["message"]) > 0


def test_podcast_frontend_card_render_contract():
    """验证前端能力卡片渲染契约：所有播客平台必须具备 CONFIG 与测试连接按钮"""
    import subprocess
    node_script = """
    const fs = require('fs');
    global.window = global;
    global.document = { querySelector: () => null, getElementById: () => null };
    global.settingsData = { podcast: {} };
    global.PLATFORM_PORTAL_LINKS = {};

    eval(fs.readFileSync('web/dashboard/js/plugins/render_shards/plugins.render.badges.js', 'utf8'));
    eval(fs.readFileSync('web/dashboard/js/plugins/platforms_shards/platforms.links.js', 'utf8'));
    eval(fs.readFileSync('web/dashboard/js/plugins/platforms_shards/platforms.sensing_judger.js', 'utf8'));
    eval(fs.readFileSync('web/dashboard/js/plugins/render_shards/plugins.render.status.js', 'utf8'));
    eval(fs.readFileSync('web/dashboard/js/plugins/render_shards/plugins.render.pod.js', 'utf8'));

    const pids = ['podcast_hub', 'podcast_xiaoyuzhou', 'podcast_apple', 'podcast_spotify', 'podcast_r2_storage'];
    for (const pid of pids) {
        const p = { id: pid, name: pid, category: 'podcast', is_enabled: true, is_in_use: false, is_manageable: true, is_configurable: true, has_config: true };
        if (!window.isPluginConfigurable(p)) throw new Error(pid + ' must be configurable');
        const html = window.buildPluginPodHtml(p, false);
        if (!html.includes('⚙️ CONFIG')) throw new Error(pid + ' missing CONFIG button');
        if (!html.includes('⚡ 测试连接')) throw new Error(pid + ' missing test button');
        if (html.includes('物理内置驱动 (免配置)')) throw new Error(pid + ' has invalid zero-config text');
    }
    """
    proc = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
    assert proc.returncode == 0, f"Node.js rendering error: {proc.stderr}"


def test_podcast_dry_run_endpoint():
    """测试 /api/plugins/dry-run 抽屉连通性测试接口对播客平台的响应"""
    for pid in ["podcast_hub", "podcast_xiaoyuzhou", "podcast_apple", "podcast_spotify", "podcast_r2_storage"]:
        resp = client.post("/api/plugins/dry-run", json={
            "id": pid,
            "parentId": "podcast",
            "settings": {"title": "测试专辑", "token": "test_tok", "apple_id": "1234567890", "show_id": "sp_123"}
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "logs" in data
        assert len(data["logs"]) > 0
        assert any("播客分发引擎" in l.get("message", "") for l in data["logs"])


def test_podcast_drawer_wizard_and_dryrun_contract():
    """验证前端抽屉极简向导 (Wizard) 与测试连接 (DryRun) 契约"""
    import subprocess
    node_script = """
    const fs = require('fs');
    global.window = global;
    global.document = { querySelector: () => null, getElementById: () => null };

    eval(fs.readFileSync('web/dashboard/js/plugins/editor_shards/editor.wizard.js', 'utf8'));

    const pids = ['podcast_hub', 'podcast_xiaoyuzhou', 'podcast_apple', 'podcast_spotify', 'podcast_r2_storage'];
    for (const pid of pids) {
        const steps = window.getPluginWizardSteps(pid, 'podcast');
        if (!steps || steps.length < 3) throw new Error(pid + ' wizard steps must be >= 3');
        const headerHtml = window.renderPluginStepWizardHeader(pid, 'podcast');
        if (!headerHtml.includes('极简向导')) throw new Error(pid + ' wizard header missing 极简向导');
        if (!headerHtml.includes('wiz-step')) throw new Error(pid + ' wizard header missing wiz-step');
    }
    """
    proc = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
    assert proc.returncode == 0, f"Node.js wizard contract error: {proc.stderr}"


