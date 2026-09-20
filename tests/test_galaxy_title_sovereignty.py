# -*- coding: utf-8 -*-
"""
🛡️ Illacme Plenipes - 知识星谱节点标题真理智能对齐主权审计门禁
测试验证：
1. resolve_node_true_title 能够跨层级优先使用 SQLite 真实标题、SEO 标题与物理原稿 H1，杜绝英文文件名退化覆盖。
2. get_galaxy_graph_logic 在骨架与全量模式下 100% 呈现真实中文标题。
3. VaultIndexer._quick_parse_meta 在无 frontmatter title 时能正确兜底提取 # 一级标题。
4. create_document_logic 在新建原稿时同步更新内存中的 link_graph 与 knowledge_graph。
5. 前端 updateGalaxyLabelElements 与 socket.galaxy_sync 在 Node.js 真实沙箱下保障 DOM 与批次标题不退化。
"""

import os
import tempfile
import pytest
from unittest.mock import MagicMock
from services.api.logic.content_ops_shards.galaxy_title_ops import resolve_node_true_title
from services.api.logic.content_ops_shards.galaxy_ops import get_galaxy_graph_logic
from core.editorial.vault_indexer import VaultIndexer
from services.api.logic.content_ops_shards.vault_file_ops import create_document_logic


def test_resolve_node_true_title_priority():
    """验证标题真理智能回填的优先级层级"""
    rel_path = "unnamed-draft-2.md"
    base_name = "unnamed-draft-2"

    # 1. 原始标题已为中文有效标题
    assert resolve_node_true_title(rel_path, "未命名原稿 2") == "未命名原稿 2"

    # 2. 原始标题为英文文件名，但 SQLite 快照中有中文标题
    snapshot = {
        "unnamed-draft-2.md": {
            "title": "未命名原稿 2 (SQLite)",
            "seo_data": {"title": "SEO 标题"}
        }
    }
    assert resolve_node_true_title(rel_path, base_name, docs_snapshot=snapshot) == "未命名原稿 2 (SQLite)"

    # 3. SQLite title 亦退化为文件名，但 seo_data 有真实标题
    snapshot_seo = {
        "unnamed-draft-2.md": {
            "title": base_name,
            "seo_data": {"title": "SEO 真实中文标题"}
        }
    }
    assert resolve_node_true_title(rel_path, base_name, docs_snapshot=snapshot_seo) == "SEO 真实中文标题"

    # 4. 物理文件嗅探 (Frontmatter)
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_engine = MagicMock()
        mock_engine.vault_root = tmpdir
        mock_engine.meta = None

        doc_file = os.path.join(tmpdir, rel_path)
        with open(doc_file, "w", encoding="utf-8") as f:
            f.write("---\ntitle: 物理文件元数据标题\n---\n# 占位正文")

        assert resolve_node_true_title(rel_path, base_name, engine=mock_engine) == "物理文件元数据标题"

    # 5. 物理文件嗅探 (无 Frontmatter title，仅有 # 一级大标题)
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_engine = MagicMock()
        mock_engine.vault_root = tmpdir
        mock_engine.meta = None

        doc_file = os.path.join(tmpdir, rel_path)
        with open(doc_file, "w", encoding="utf-8") as f:
            f.write("---\ndate: 2026-09-20\n---\n\n# 物理文件一级大标题\n\n正文内容...")

        assert resolve_node_true_title(rel_path, base_name, engine=mock_engine) == "物理文件一级大标题"


def test_get_galaxy_graph_logic_true_title():
    """验证 get_galaxy_graph_logic 骨架与全量模式下均对齐真实中文标题"""
    mock_engine = MagicMock()
    mock_engine.vault_root = "/fake/vault"
    mock_engine.link_graph = {
        "articles/unnamed-draft-2.md": {
            "links": [],
            "metadata": {"title": "unnamed-draft-2"}  # 模拟尚未扫描到中文标题的退化态
        }
    }
    mock_engine.knowledge_graph.get_galaxy_graph.return_value = {
        "nodes": [{"id": "articles/unnamed-draft-2.md", "title": "unnamed-draft-2"}],
        "links": []
    }
    mock_engine.meta.get_documents_snapshot.return_value = {
        "articles/unnamed-draft-2.md": {
            "title": "未命名原稿 2",
            "seo_data": {"title": "未命名原稿 2 (SEO)"}
        }
    }

    # 骨架模式验证
    skeleton = get_galaxy_graph_logic(mock_engine, mode="skeleton")
    assert len(skeleton["nodes"]) == 1
    assert skeleton["nodes"][0]["title"] == "未命名原稿 2"

    # 全量模式验证
    full = get_galaxy_graph_logic(mock_engine, mode="full")
    assert len(full["nodes"]) == 1
    assert full["nodes"][0]["title"] == "未命名原稿 2"


def test_vault_indexer_quick_parse_h1_fallback():
    """验证 VaultIndexer._quick_parse_meta 在无 YAML title 时能自动提取 # H1"""
    content_without_fm_title = "---\ndate: '2026-09-20'\n---\n\n# 知识星谱真理核心\n\n正文测试"
    meta = VaultIndexer._quick_parse_meta(content_without_fm_title)
    assert meta["title"] == "知识星谱真理核心"

    content_with_fm_title = "---\ntitle: 显式Frontmatter标题\n---\n# 一级标题\n\n正文测试"
    meta2 = VaultIndexer._quick_parse_meta(content_with_fm_title)
    assert meta2["title"] == "显式Frontmatter标题"


def test_create_document_syncs_link_graph_and_kg():
    """验证新建原稿时同步写入 link_graph 与 knowledge_graph 内存"""
    with tempfile.TemporaryDirectory() as tmpdir:
        mock_engine = MagicMock()
        mock_engine.vault_root = tmpdir
        mock_engine.link_graph = {}
        mock_engine.knowledge_graph = MagicMock()
        mock_engine.knowledge_graph.nodes = {}
        mock_engine.meta = MagicMock()

        req = {
            "doc_id": "test-new-draft.md",
            "title": "新建中文测试原稿"
        }
        res = create_document_logic(mock_engine, req)
        assert res.get("success") is True

        # 验证 link_graph 内存秒级注册中文标题
        assert "test-new-draft.md" in mock_engine.link_graph
        assert mock_engine.link_graph["test-new-draft.md"]["metadata"]["title"] == "新建中文测试原稿"

        # 验证 knowledge_graph 内存秒级注册中文标题
        assert "test-new-draft.md" in mock_engine.knowledge_graph.nodes
        assert mock_engine.knowledge_graph.nodes["test-new-draft.md"]["title"] == "新建中文测试原稿"


def test_frontend_node_label_and_socket_sync_sandbox():
    """在 Node.js 真实沙箱中验证 galaxy.labels.js 实时更新与 socket.galaxy_sync 防退化"""
    import subprocess
    runner_script = """
    const fs = require('fs');
    const path = require('path');

    // 1. 初始化 Mock 浏览器环境
    global.window = {};
    global.document = {
        createElement: (tag) => ({
            className: '',
            id: '',
            innerText: '',
            style: {},
            remove: () => {}
        })
    };

    // 2. 加载 galaxy.labels.js 模块
    const labelsCode = fs.readFileSync(path.resolve(__dirname, '../web/dashboard/js/galaxy/galaxy.labels.js'), 'utf8');
    eval(labelsCode);

    // 模拟先创建了一个退化的英文标签
    const initialNodes = [{ id: 'unnamed-draft-2.md', title: 'unnamed-draft-2' }];
    window.updateGalaxyLabelElements(initialNodes);
    
    // 通过标签创建逻辑模拟 DOM 缓存
    const dummyEl = { innerText: 'unnamed-draft-2' };
    window._labelPool.set('unnamed-draft-2.md', dummyEl);

    // 3. 当后台解析完中文后更新节点
    const updatedNodes = [{ id: 'unnamed-draft-2.md', title: '未命名原稿 2' }];
    window.updateGalaxyLabelElements(updatedNodes);

    if (dummyEl.innerText !== '未命名原稿 2') {
        throw new Error('DOM label innerText was not updated! Got: ' + dummyEl.innerText);
    }

    // 4. 加载 socket.galaxy_sync.js 模块
    window.galaxyGraph = {
        graphData: () => ({
            nodes: [{ id: 'unnamed-draft-2.md', title: '未命名原稿 2' }],
            links: []
        }),
        cooldownTicks: () => {},
        d3Reheat: () => {}
    };

    const syncCode = fs.readFileSync(path.resolve(__dirname, '../web/dashboard/js/socket_shards/socket.galaxy_sync.js'), 'utf8');
    eval(syncCode);

    // 模拟 WebSocket 下发了一个包含退化英文文件名的批次
    let resultGraphData = null;
    window.galaxyGraph.graphData = (newData) => {
        if (newData) resultGraphData = newData;
        return { nodes: [{ id: 'unnamed-draft-2.md', title: '未命名原稿 2' }], links: [] };
    };

    window._wsHandleGalaxySync({
        payload: {
            batch_index: 1,
            nodes: [{ id: 'unnamed-draft-2.md', title: 'unnamed-draft-2' }],
            links: []
        }
    });

    const targetNode = resultGraphData.nodes.find(n => n.id === 'unnamed-draft-2.md');
    if (!targetNode || targetNode.title !== '未命名原稿 2') {
        throw new Error('Socket sync degraded Chinese title to base_name! Got: ' + (targetNode ? targetNode.title : 'null'));
    }

    console.log('SANDBOX_PASSED');
    """

    res = subprocess.run(
        ["node", "-e", runner_script],
        cwd=os.path.dirname(os.path.abspath(__file__)),
        capture_output=True,
        text=True
    )
    assert res.returncode == 0, f"Node.js Sandbox Failed: {res.stderr}\n{res.stdout}"
    assert "SANDBOX_PASSED" in res.stdout
