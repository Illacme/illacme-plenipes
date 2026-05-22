# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Pipeline Steps Shard
工序职责：MaskingAndRoutingStep (隐私遮蔽与路由矩阵推导)
🛡️ [AEL-Iter-v5.3]：基于分层架构的 TDR 复健版本。
"""

import os
import re
from core.editorial.runner import PipelineStep

class MaskingAndRoutingStep(PipelineStep):
    """阶段 13-14: 物理遮蔽与动态路由推导"""
    PLUGIN_ID = "masking_routing"
    DISPLAY_NAME = "物理遮蔽与路由推导"
    VERSION = "V5.3"
    DESCRIPTION = "执行隐私脱敏，并根据物理路径推导出版物的路由矩阵。"

    def process(self, ctx):
        def mask_fn(m):
            matched = m.group(0)

            # [AEL-Iter-v7.5] 语义链接提取钩子 (Graph Link Extraction)
            if matched.startswith('[[') and not matched.startswith('![['):
                # 提取 Wikilink 目标
                target = matched[2:-2].split('|')[0].strip()
                if target: ctx.node_outlinks.add(target)
            elif matched.startswith('[') and '(' in matched and not matched.startswith('!['):
                # 提取标准 MD 链接目标
                link_match = re.match(r'^\[.*?\]\(([^)]+)\)$', matched)
                if link_match:
                    url = link_match.group(1).split('#')[0].split('?')[0].strip()
                    if url and not url.startswith(('http', 'mailto', 'tel')):
                        ctx.node_outlinks.add(url)

            link_match = re.match(r'^(\!?\[.*?\]\()([^)]+)(\))$', matched)
            if link_match:
                prefix, url_part, suffix = link_match.groups()
                if prefix.startswith('!['):
                    ctx.masks.append(matched)
                    return f"[[STB_MASK_{len(ctx.masks)-1}]]"
                else:
                    ctx.masks.append(f"URL_ONLY_LNK:{url_part}")
                    return f"{prefix}[[STB_MASK_{len(ctx.masks)-1}]]{suffix}"
            ctx.masks.append(matched)
            return f"[[STB_MASK_{len(ctx.masks)-1}]]"

        mask_pattern = ctx.engine.config.system.mask_pattern
        ctx.masked_source = re.sub(mask_pattern, mask_fn, ctx.body_content, flags=re.DOTALL)

        vault_path = ctx.engine.paths.get('vault', '.')
        sub = os.path.dirname(os.path.relpath(ctx.src_path, os.path.join(vault_path, ctx.route_source))).replace('\\', '/')
        if sub == '.': sub = ""
        ctx.mapped_sub_dir = ctx.engine.route_manager.get_mapped_sub_dir(sub, allow_ai=not ctx.is_silent_edit)

        ctx.engine.meta.register_document(
            ctx.rel_path, ctx.title,
            slug=ctx.slug,
            route_prefix=ctx.route_prefix,
            route_source=ctx.route_source,
            seo_data=ctx.seo_data,
            source_lang=getattr(ctx, 'source_lang', None)
        )
