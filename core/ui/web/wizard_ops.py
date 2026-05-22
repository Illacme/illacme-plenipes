#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧙‍♂️ wizard_ops.py - Hub 逻辑中枢门面 (Facade)
引入子包中的四个原子逻辑分片，并提供统一的逻辑委托层接口。
"""

from core.ui.web.wizard_ops_shards.probe_ops import probe_nodes_logic
from core.ui.web.wizard_ops_shards.fs_ops import list_files_logic
from core.ui.web.wizard_ops_shards.ai_ops import get_ai_models_logic, validate_ai_logic
from core.ui.web.wizard_ops_shards.init_ops import init_press_logic
