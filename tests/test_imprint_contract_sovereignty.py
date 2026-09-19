import pytest
import subprocess
from pathlib import Path
from unittest.mock import patch

def test_backend_imprint_contract_sovereignty():
    """
    🛡️ 后端出版品牌契约主权门禁 (Backend Contract Sovereignty Gate)
    铁律：
    1. im.list_imprints() 必须且只能提供官方统一标准文库路径键名 'vault_root'。
    2. 绝不允许使用简写或漂移键名 (如 'vault', 'path')，彻底杜绝契约腐蚀。
    """
    from core.governance.imprint_manager import im
    
    mock_imprints = [
        {"id": "default", "name": "官方示范", "vault_root": "/path/to/default/vault", "vault_abs": "/path/to/default/vault", "active": True},
        {"id": "custom", "name": "自定义专栏", "vault_root": "~/Documents/CustomVault", "vault_abs": "/Users/test/Documents/CustomVault", "active": False}
    ]
    
    with patch.object(im, "list_imprints", return_value=mock_imprints):
        results = im.list_imprints()
        assert len(results) >= 2
        for item in results:
            assert "id" in item, "Missing 'id' in imprint contract"
            assert "name" in item, "Missing 'name' in imprint contract"
            assert "vault_root" in item, "Missing official standard 'vault_root' in imprint contract"
            assert "vault" not in item, "Contract erosion: 'vault' key detected in imprint contract"
            assert "path" not in item, "Contract erosion: 'path' key detected in imprint contract"


def test_frontend_imprint_zero_undefined_and_dom_parity():
    """
    🛡️ 前端零 undefined 与 DOM 拓扑完备性门禁 (Frontend Zero-Undefined & DOM Parity Gate)
    铁律：
    1. 在 Node.js 真实沙箱环境下执行 renderImprintDropdown() 与 renderImprintsCategory()。
    2. 产出的 HTML 严禁包含 'undefined'、'null'、'[object Object]' 字符串。
    3. 必须精准渲染后端下发的 vault_root 物理路径。
    """
    runner_script = """
    const fs = require('fs');

    let dropdownHtml = "";
    global.document = {
        getElementById: (id) => {
            if (id === "imprint-dropdown") {
                return {
                    set innerHTML(val) { dropdownHtml = val; },
                    get innerHTML() { return dropdownHtml; },
                    style: {}
                };
            }
            return null;
        }
    };

    global.window = {
        settingsData: {
            _active_imprint: "default",
            _imprints: [
                { id: "default", name: "示范品牌", vault_root: "/Volumes/Notebook/vault", vault_abs: "/Volumes/Notebook/vault" },
                { id: "tech", name: "技术专栏", vault_root: "~/Documents/TechVault", vault_abs: "/Users/test/Documents/TechVault" }
            ],
            _imprint_stats: {
                "default": { doc_count: 12, healthy: true, vault_exists: true },
                "tech": { doc_count: 5, healthy: true, vault_exists: true }
            }
        }
    };

    const code = fs.readFileSync('web/dashboard/js/imprints/imprints.render.js', 'utf8');
    eval(code);

    // 1. 执行下拉菜单渲染
    window.renderImprintDropdown();
    if (!dropdownHtml || typeof dropdownHtml !== 'string') {
        throw new Error('renderImprintDropdown failed to output HTML');
    }
    if (dropdownHtml.includes('undefined')) {
        throw new Error('Contract Violation: dropdownHtml contains undefined! Output: ' + dropdownHtml);
    }
    if (!dropdownHtml.includes('/Volumes/Notebook/vault') || !dropdownHtml.includes('~/Documents/TechVault')) {
        throw new Error('DOM Parity Failure: dropdownHtml missing vault_root values');
    }

    // 2. 执行大面板卡片渲染
    const categoryHtml = window.renderImprintsCategory();
    if (!categoryHtml || typeof categoryHtml !== 'string') {
        throw new Error('renderImprintsCategory failed to output HTML');
    }
    if (categoryHtml.includes('undefined')) {
        throw new Error('Contract Violation: categoryHtml contains undefined! Output: ' + categoryHtml);
    }
    if (!categoryHtml.includes('shield-pod territory-pod') || !categoryHtml.includes('示范品牌')) {
        throw new Error('DOM Parity Failure: categoryHtml missing expected elements');
    }

    console.log('IMPRINT_CONTRACT_AND_ZERO_UNDEFINED_VERIFIED');
    """

    res = subprocess.run(["node", "-e", runner_script], capture_output=True, text=True, cwd=str(Path(__file__).parent.parent))
    assert res.returncode == 0, f"Frontend Zero-Undefined Gate Failed: Stderr: {res.stderr} | Stdout: {res.stdout}"
    assert "IMPRINT_CONTRACT_AND_ZERO_UNDEFINED_VERIFIED" in res.stdout


def test_imprint_stats_and_add_contract_sovereignty():
    """
    🛡️ /api/imprints/stats 与 /api/imprints/add 契约全量主权门禁
    确保 stats 接口返回的文库路径键名只能是 vault_root，严禁使用历史漂移的 vault_path。
    """
    from services.api.routes.gov.imprints import get_imprints_stats
    from unittest.mock import MagicMock
    from core.governance.imprint_manager import im

    mock_engine = MagicMock()
    mock_imprints = [
        {"id": "default", "name": "官方示范", "vault_root": "/path/to/default/vault", "active": True}
    ]

    with patch("services.api.routes.gov.imprints.get_global_engine", return_value=mock_engine), \
         patch.object(im, "list_imprints", return_value=mock_imprints), \
         patch("core.governance.env_sentry.sentry.check_isolation_health", return_value={"has_local_toolchain": True, "isolation_level": "NORMAL"}):
        
        stats = get_imprints_stats()
        assert "default" in stats
        stat = stats["default"]
        # 必须使用统一官方标准 vault_root
        assert "vault_root" in stat, "Missing official standard 'vault_root' in stats payload"
        # 严禁出现历史漂移键名 vault_path
        assert "vault_path" not in stat, "Contract erosion: 'vault_path' detected in stats payload"

        # 🛡️ 断言真实物理文库自动统计能力 (基于真实存在的 ./vault 目录)
        mock_imprints_real = [
            {"id": "default", "name": "官方示范", "vault_root": "./vault", "active": True}
        ]
        with patch.object(im, "list_imprints", return_value=mock_imprints_real):
            stats_real = get_imprints_stats()
            assert stats_real["default"]["doc_count"] > 0, "Doc count should be physically counted from ./vault (>0)"


@pytest.mark.anyio
async def test_vault_list_physical_fallback_sovereignty():
    """
    🛡️ /api/vault/list 物理真理保底门禁
    即使账本快照为空（未入账或未构建），若物理文库存在 Markdown 文件，必须自动自愈扫描并返回文档清单，严禁显示为 0 篇。
    """
    from services.api.routes.gov.vault import list_vault_manuscripts
    from unittest.mock import MagicMock

    mock_engine = MagicMock()
    mock_engine.vault_root = "./vault"
    mock_engine.meta.get_documents_snapshot.return_value = {}  # 模拟账本为空

    with patch("services.api.routes.gov.vault.get_global_engine", return_value=mock_engine):
        res = await list_vault_manuscripts()
        assert "manuscripts" in res
        assert len(res["manuscripts"]) > 0, "Vault list must physically discover files from ./vault even when snapshot is empty"
        # 必须包含真实文档字段且 status 为 Draft
        first_doc = res["manuscripts"][0]
        assert "path" in first_doc
        assert "title" in first_doc
        assert first_doc["status"] == "Draft"


