#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omni-Hub V21 - Workspace Manager
职责：管理多套配置文件与工作空间的生命周期。
"""

import os
import glob
from typing import List, Dict
from core.utils.tracing import tlog

class WorkspaceManager:
    """🚀 [V21.0] 工作空间管理器：支持一机多库热切换"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.active_workspace_id = "default"

    def list_workspaces(self) -> List[Dict[str, str]]:
        """扫描根目录下的所有 config.*.yaml 文件"""
        workspaces = []
        
        # 默认配置
        if os.path.exists("config.yaml"):
            workspaces.append({"id": "default", "name": "默认空间", "path": "config.yaml"})
            
        # 扩展配置 config.xxx.yaml
        configs = glob.glob(os.path.join(self.root_dir, "config.*.yaml"))
        for cfg in configs:
            ws_id = os.path.basename(cfg).split('.')[1]
            workspaces.append({
                "id": ws_id,
                "name": f"空间: {ws_id.capitalize()}",
                "path": cfg
            })
            
        return workspaces

    def get_config_path(self, workspace_id: str) -> str:
        """根据 ID 获取对应的配置文件路径"""
        if workspace_id == "default":
            return "config.yaml"
        return f"config.{workspace_id}.yaml"

    def register(self, workspace_id: str, path: str, name: str = None):
        """🚀 [V21.1] 注册一个新的工作空间"""
        tlog.info(f"🛰️ [Workspace] 注册空间: {workspace_id} -> {path}")
        # 这里可以扩展持久化逻辑

    def switch(self, workspace_id: str):
        """切换活跃工作空间"""
        self.active_workspace_id = workspace_id
        tlog.info(f"🔄 [Workspace] 已切换至活跃空间: {workspace_id}")

    def get_active_workspace(self) -> str:
        return self.active_workspace_id

global_workspace_manager = WorkspaceManager()
wm = global_workspace_manager
