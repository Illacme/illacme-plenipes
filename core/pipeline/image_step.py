#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Image Processing Step
模块职责：负责 AI 驱动的图片 Alt 描述生成与多语言元数据同步 (ADMI v2.0)。
🛡️ [AEL-Iter-v5.3]：基于 TDR 复健的解耦流水线工序。
"""
import os
import re
import hashlib
import logging
from core.pipeline.runner import PipelineStep

from core.utils.tracing import tlog

class ContextualImageAltStep(PipelineStep):
    """阶段 12.5: AI 驱动的媒体智能引擎 (ADMI v2.0)"""
    PLUGIN_ID = "image_alt"
    def process(self, ctx):
        if ctx.is_aborted or ctx.is_dry_run or ctx.is_silent_edit:
            return

        image_cfg = getattr(ctx.engine.config, 'image_settings', None)
        admi_enabled = getattr(image_cfg, 'generate_alt', False)
        multilingual_enabled = getattr(image_cfg, 'multilingual_alt', False)

        if not admi_enabled: return

        pattern = re.compile(r'!\[\s*\]\(([^)]+)\)')
        matches = list(pattern.finditer(ctx.body_content))
        if not matches: return

        tlog.info(f"🔍 [ADMI] 在 {ctx.rel_path} 中侦测到 {len(matches)} 处空白图片标签...")

        offset = 0
        new_content = ctx.body_content

        for m in matches:
            img_path = m.group(1)
            img_name = os.path.basename(img_path)

            abs_img_path = ""
            if img_path.startswith(('http://', 'https://', 'data:')): continue

            potential_paths = [
                os.path.join(os.path.dirname(ctx.src_path), img_path),
                os.path.join(ctx.engine.paths.get('vault', '.'), img_path.lstrip('/'))
            ]

            for p in potential_paths:
                if os.path.exists(p):
                    abs_img_path = p
                    break

            alt_text = ""
            asset_hash = ""
            source_lang = ctx.engine.i18n.source.lang_code or "zh"

            if abs_img_path:
                try:
                    with open(abs_img_path, 'rb') as f:
                        img_bytes = f.read()
                        asset_hash = hashlib.md5(img_bytes).hexdigest()

                    cached_meta = ctx.engine.meta.get_asset_metadata(asset_hash)
                    if cached_meta and cached_meta.get("alt_texts", {}).get(source_lang):
                        alt_text = cached_meta.get("alt_texts", {}).get(source_lang)
                    elif cached_meta and cached_meta.get("alt_text"):
                        alt_text = cached_meta.get("alt_text")
                    else:
                        ext = os.path.splitext(abs_img_path)[1].lower().lstrip('.')
                        mime_type = f"image/{ext}" if ext != 'jpg' else "image/jpeg"

                        start_idx = max(0, m.start() - 300)
                        end_idx = min(len(ctx.body_content), m.end() + 300)
                        surrounding_text = ctx.body_content[start_idx:end_idx]

                        desc = ctx.engine.translator.describe_image(img_bytes, mime_type, context_text=surrounding_text)
                        if desc:
                            alt_text = desc.strip()
                            ctx.engine.meta.register_asset_metadata(asset_hash, alt_text=alt_text, lang=source_lang)
                except Exception: pass

            if not alt_text:
                start_idx = max(0, m.start() - 250)
                end_idx = min(len(ctx.body_content), m.end() + 250)
                surrounding_text = ctx.body_content[start_idx:end_idx]
                prompt = f"请根据上下文推测图片 '{img_name}' 展示的内容，生成一句精确的 SEO Alt 描述。\n\n【上下文】:\n{surrounding_text}"
                try:
                    raw_alt = ctx.engine.translator.translate(prompt, "Auto", "Image Alt Generation")
                    alt_text = raw_alt.strip().replace('\n', '').replace('"', '').replace('[', '').replace(']', '')
                    if asset_hash:
                        ctx.engine.meta.register_asset_metadata(asset_hash, alt_text=alt_text, lang=source_lang)
                except Exception: continue

            if asset_hash and multilingual_enabled:
                for target in ctx.engine.i18n.targets:
                    t_code = target.lang_code
                    if t_code == source_lang: continue
                    current_meta = ctx.engine.meta.get_asset_metadata(asset_hash)
                    if t_code in current_meta.get("alt_texts", {}): continue

                    try:
                        if t_code:
                            target_lang_name = ctx.engine.get_lang_name_by_code(t_code)
                            t_alt = ctx.engine.translator.translate(alt_text, "Auto", target_lang_name, context_type="alt_text")
                            ctx.engine.meta.register_asset_metadata(asset_hash, alt_text=t_alt.strip(), lang=str(t_code).strip().lower())
                    except Exception: pass

            new_img_md = f"![{alt_text}]({img_path})"
            new_content = new_content[:m.start()+offset] + new_img_md + new_content[m.end()+offset:]
            offset += len(new_img_md) - len(m.group(0))

        ctx.body_content = new_content
