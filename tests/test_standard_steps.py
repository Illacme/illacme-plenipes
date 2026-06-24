#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_standard_steps.py
🛡️ [V88.0] 校验 Pipeline 步骤门面代理导出与实例化。
确保 ReadAndNormalizeStep, ASTAndPurifyStep 等门面定义完整，均继承自 PipelineStep，且插件元数据可达。
"""

import pytest
from core.editorial.runner import PipelineStep
from core.editorial.standard_steps import (
    ReadAndNormalizeStep,
    ASTAndPurifyStep,
    MetadataAndHashStep,
    AISlugAndSEOStep,
    MaskingAndRoutingStep,
    VerificationStep
)


class TestStandardSteps:
    """标准流水线工序门面测试类"""

    def test_facade_exports(self):
        """验证所有工序类是否已被正确导出且继承自 PipelineStep"""
        steps = [
            ReadAndNormalizeStep,
            ASTAndPurifyStep,
            MetadataAndHashStep,
            AISlugAndSEOStep,
            MaskingAndRoutingStep,
            VerificationStep
        ]
        for step_cls in steps:
            assert issubclass(step_cls, PipelineStep)
            assert step_cls.PLUGIN_ID is not None
            assert step_cls.DISPLAY_NAME is not None
            assert step_cls.VERSION is not None

    def test_step_properties(self):
        """对特定工序的元数据进行物理对账"""
        assert ReadAndNormalizeStep.PLUGIN_ID == "read_normalize"
        assert ASTAndPurifyStep.PLUGIN_ID == "purify"
        assert MetadataAndHashStep.PLUGIN_ID == "metadata_hash"
        assert AISlugAndSEOStep.PLUGIN_ID == "ai_slug_seo"
        assert MaskingAndRoutingStep.PLUGIN_ID == "masking_routing"
        assert VerificationStep.PLUGIN_ID == "verification"
