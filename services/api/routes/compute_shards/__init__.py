# -*- coding: utf-8 -*-
"""
🚀 [V66.5] Compute Shards Package
职责：算力治理物理节点管理、连通性探针与动态模型发现分片。
"""

from .node_mgmt_ops import (
    list_compute_nodes_logic,
    update_compute_node_logic,
    delete_node_logic,
    switch_primary_node_logic,
    switch_fallback_node_logic,
)
from .node_probe_ops import (
    probe_compute_logic,
    test_node_connectivity_logic,
    get_node_models_logic,
)

__all__ = [
    "list_compute_nodes_logic",
    "update_compute_node_logic",
    "delete_node_logic",
    "switch_primary_node_logic",
    "switch_fallback_node_logic",
    "probe_compute_logic",
    "test_node_connectivity_logic",
    "get_node_models_logic",
]
