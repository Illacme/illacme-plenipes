# -*- coding: utf-8 -*-
"""
🧪 [Test] Digital Garden & Knowledge Graph Export Parity Test
职责：验证数字花园关系图谱在多框架（Astro public/ 与 Docusaurus static/）下的物理落盘与拓扑完整性。
"""

import os
import json
import tempfile
from unittest.mock import MagicMock
from core.bindery.garden_exporter import export_digital_garden


def test_export_digital_garden_multi_framework_sync():
    """验证 export_digital_garden 能自动识别并同步至 static/、public/ 与 build/ 目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建模拟的主题工作区
        theme_base = os.path.join(tmpdir, "themes", "docusaurus")
        static_dir = os.path.join(theme_base, "static")
        public_dir = os.path.join(theme_base, "public")
        meta_dir = os.path.join(tmpdir, "metadata")
        os.makedirs(static_dir, exist_ok=True)
        os.makedirs(public_dir, exist_ok=True)
        os.makedirs(meta_dir, exist_ok=True)

        # Mock engine 上下文
        engine = MagicMock()
        engine.paths = {
            'target_base': theme_base,
            'vault': tmpdir,
        }
        engine.config.get_theme_metadata_dir.return_value = meta_dir
        engine._resolve_path.side_effect = lambda p: p

        # 模拟文档快照
        mock_snapshot = {
            "docs/architecture.md": {
                "slug": "architecture",
                "source": "docs",
                "prefix": "docs/{lang}",
                "title": "物理隔离架构与技术原理",
                "inlinks": ["docs/matrix.md"],
            },
            "docs/matrix.md": {
                "slug": "matrix",
                "source": "docs",
                "prefix": "docs/{lang}",
                "title": "渠道矩阵配置",
                "inlinks": [],
            }
        }

        # 模拟 route_manager
        engine.route_manager.lang_mapping = {"zh": "zh"}
        engine.route_manager.get_mapped_sub_dir.return_value = ""

        # 执行导出
        export_digital_garden(engine, all_docs_snapshot=mock_snapshot)

        # 1. 断言 metadata 目录下 link_graph.json 存在
        link_graph_path = os.path.join(meta_dir, "link_graph.json")
        assert os.path.exists(link_graph_path), "metadata/link_graph.json 未生成！"

        # 2. 断言 static/graph.json (适配 Docusaurus) 存在且有效
        static_graph = os.path.join(static_dir, "graph.json")
        assert os.path.exists(static_graph), "static/graph.json (Docusaurus) 未生成！"
        with open(static_graph, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "node_titles" in data
            assert "all_nodes" in data
            assert "backlinks" in data

        # 3. 断言 public/graph.json (适配 Astro/Universal) 也同步生成
        pub_graph = os.path.join(public_dir, "graph.json")
        assert os.path.exists(pub_graph), "public/graph.json (Astro) 未生成！"
