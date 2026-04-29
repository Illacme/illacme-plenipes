#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import abc
from core.utils.tracing import SovereignCore

class BaseSyncStrategy(abc.ABC):
    """🚀 [V11.0] 同步策略基座：定义同步行为的标准化契约"""

    def __init__(self, engine):
        self.engine = engine

    @abc.abstractmethod
    @SovereignCore
    def execute(self, rel_path, route_prefix, route_source, is_dry_run, force_sync=False, is_sandbox=False):
        """执行同步操作的核心入口"""
        pass
