# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Pipeline Steps Shard
工序职责：ASTAndPurifyStep (语义提纯与 AST 解析)
🛡️ [AEL-Iter-v5.3]：基于分层架构的 TDR 复健版本。
"""

from core.utils import strip_technical_noise
from core.editorial.runner import PipelineStep

class ASTAndPurifyStep(PipelineStep):
    """阶段 6-7: AST 降维与语义提纯"""
    PLUGIN_ID = "purify"
    DISPLAY_NAME = "语义提纯与 AST 解析"
    VERSION = "V5.3"
    DESCRIPTION = "对内容执行 AST 转换，移除噪音并为 AI 推理准备纯净语料。"

    def process(self, ctx):
        # 🚀 [V16.0] 切换至全插件化 AST 解析流水线
        ctx.body_content = ctx.engine.ast_resolver.resolve(
            ctx.raw_body,
            ctx.src_path,
            ctx.engine.paths.get('target_base')
        )
        if ctx.services.staticizer:
            ctx.services.staticizer.staticize_callouts(ctx.body_content, ctx.engine.ssg_adapter)

        purify_opts = ctx.engine.config.system.ai_context_purification
        ctx.ai_pure_body = strip_technical_noise(ctx.body_content, purify_opts)

        substance_threshold = ctx.engine.config.translation.empty_content_threshold
        is_empty = len(ctx.ai_pure_body.strip()) < substance_threshold
        is_draft = str(ctx.fm_dict.get('draft')).lower() == 'true' or str(ctx.fm_dict.get('publish')).lower() == 'false'

        if is_empty or is_draft:
            if ctx.engine.meta.get_doc_info(ctx.rel_path):
                ctx.engine.janitor.gc_node(ctx.rel_path, ctx.route_prefix, ctx.route_source, ctx.is_dry_run)
            ctx.is_aborted = True
