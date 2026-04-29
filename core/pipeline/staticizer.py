#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Component Staticizer Step (组件静态化工序)
职责：流水线适配层，将静态化请求分发至 StaticizerService。
🛡️ [AEL-Iter-2026.04.23.SOVEREIGNTY_P1]：工序逻辑已彻底解耦，仅作为 Service 包装器。
"""

import logging
from core.pipeline.runner import PipelineStep

from core.utils.tracing import tlog

class StaticizerStep(PipelineStep):
    """
    🚀 阶段 3.5: 组件语义提取与静态化 (Service 包装版)
    """
    PLUGIN_ID = "staticize"
    def process(self, ctx):
        # 🛡️ 尊重全局开关
        ingress_cfg = ctx.engine.config.ingress_settings
        if not ingress_cfg.staticize_components or not ctx.raw_body:
            return

        # 委托 Service 处理 Tabs 和 Dataview
        staticizer = ctx.services.staticizer
        ctx.raw_body = staticizer.staticize_tabs(ctx.raw_body)
        ctx.raw_body = staticizer.staticize_dataview(ctx.raw_body)

    def process_body(self, ctx):
        """
        处理经过 Transclusion 展开后的全文内容。
        """
        if not ctx.body_content:
            return

        # 委托 Service 处理 Callouts
        ctx.body_content = ctx.services.staticizer.staticize_callouts(
            ctx.body_content,
            ctx.engine.ssg_adapter
        )
