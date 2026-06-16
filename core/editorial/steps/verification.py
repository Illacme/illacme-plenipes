# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Pipeline Steps Shard
工序职责：VerificationStep (全息主权验证)
🛡️ [AEL-Iter-v5.3]：基于分层架构的 TDR 复健版本。
"""

from core.utils.tracing import tlog
from core.editorial.runner import PipelineStep

class VerificationStep(PipelineStep):
    """阶段 15: 全息主权验证"""
    PLUGIN_ID = "verification"
    DISPLAY_NAME = "全息主权验证"
    VERSION = "V5.3"
    DESCRIPTION = "执行终极物理验证，确保资产完整性与出版主权 100% 对正。"

    def process(self, ctx):
        tlog.info(f"🛡️ [全息审计] 正在验证资产完整性: {ctx.rel_path}")

        # 1. 占位符对齐校验 (Mask Integrity)
        # 我们检查还原后的 body 中是否仍包含 STB_MASK 标记
        if "[[STB_MASK_" in ctx.body_content:
            err = "文档编译失败：侦测到残留占位符（部分代码或文本保护标记在翻译还原中未被正常恢复），请重新分发或尝试更换 AI 引擎。"
            tlog.error(f"❌ [审计失败] {err}")
            ctx.engine.brain.log_lesson("MASK_INTEGRITY", err, {"path": ctx.rel_path})
            ctx.is_aborted = True
            ctx.abort_reason = err
            return

        # 2. 括号匹配度审计 (Sovereignty Shield)
        # 验证 [[SECRET_TAG]] 等关键结构的完整性（如果原文有，译文也必须有）
        if "[[SECRET_TAG]]" in ctx.raw_content and "[[SECRET_TAG]]" not in ctx.body_content:
            err = "文档校验失败：敏感标签 [[SECRET_TAG]] 在流转中丢失，请检查翻译结果与原稿中的标记是否对应。"
            tlog.warning(f"⚠️ [审计警告] {err}")
            ctx.engine.brain.log_lesson("SOVEREIGNTY_SHIELD", err, {"path": ctx.rel_path})
            # 这是一个强约束，在商业级模式下应视为失败
            ctx.is_aborted = True
            ctx.abort_reason = err
            return

        # 3. 多语言矩阵对齐校验 (SEO Alignment)
        if hasattr(ctx, 'hreflangs') and len(ctx.hreflangs) < 1:
            tlog.warning("⚠️ [审计警告] 缺失多语言指向矩阵 (hreflangs)。")

        tlog.info("✨ [审计通过] 资产完整性 100% 严丝合缝。")
