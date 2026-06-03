# -*- coding: utf-8 -*-
"""
📝 Illacme API Logic - Content Operations (Hub 调度中心)
职责：退化为极简路由中枢门面，完全向上兼容路由接口，委派具体任务至实体物理分片包。
符合 SOP-02 模块拆分协议与 300 行核心复杂度红线。
"""

from services.api.logic.content_ops_shards.safe_ops import (
    resolve_safe_path as resolve_safe_path,
    get_vault_asset_logic as get_vault_asset_logic
)
from services.api.logic.content_ops_shards.galaxy_ops import (
    get_galaxy_graph_logic as get_galaxy_graph_logic,
    rebuild_node_semantics_logic as rebuild_node_semantics_logic
)
from services.api.logic.content_ops_shards.vault_ops import (
    search_vault_logic as search_vault_logic,
    get_document_detail_logic as get_document_detail_logic,
    update_document_metadata_logic as update_document_metadata_logic,
    save_document_logic as save_document_logic,
    create_document_logic as create_document_logic,
    create_directory_logic as create_directory_logic,
    delete_directory_logic as delete_directory_logic,
    move_document_logic as move_document_logic,
    upload_asset_logic as upload_asset_logic
)
