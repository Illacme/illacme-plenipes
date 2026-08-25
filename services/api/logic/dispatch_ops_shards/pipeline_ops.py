#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 [V68.0] Illacme Plenipes - Dispatch Pipeline Shard (Facade)
职责：管线异步重分发编译分发与物理销毁自愈门面中枢。
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]：逻辑解耦核心，具体算子已物理拆解至 pipeline_shards/。
"""

from .pipeline_shards import (
    _async_redispatch_task,
    trigger_re_dispatch_logic,
    destroy_artifact_logic,
    get_pending_syndication_logic
)

__all__ = [
    "_async_redispatch_task",
    "trigger_re_dispatch_logic",
    "destroy_artifact_logic",
    "get_pending_syndication_logic"
]
