#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Pipeline Steps
模块职责：单向流水线的具体加工工序。
"""

import os
import re
import time
import hashlib
import logging
import shutil
from ..utils import extract_frontmatter, strip_technical_noise, normalize_keywords
from .runner import Step

logger = logging.getLogger("Illacme.plenipes")

class ReadAndNormalizeStep(Step):
    """阶段 3-4: 物理读取与编辑器方言抹平"""
    def process(self, ctx):
        try:
            with open(ctx.src_path, 'r', encoding='utf-8') as f:
                ctx.raw_content = f.read()
        except FileNotFoundError:
            logger.error(f"🛑 同步中断: 文件已在磁盘上消失 {ctx.src_path}")
            ctx.is_aborted = True
            return
        except IOError as e: 
            logger.error(f"🛑 读取失败: 无法访问文章 {ctx.src_path}: {e}")
            ctx.is_aborted = True
            return

        fm_dict, raw_body = extract_frontmatter(ctx.raw_content)
        ctx.raw_body, ctx.fm_dict = ctx.engine.input_adapter.normalize(raw_body, fm_dict)
        
        raw_ai_sync = ctx.fm_dict.get('ai_sync')
        ctx.is_silent_edit = (str(raw_ai_sync).lower() == 'false') if raw_ai_sync is not None else False

class ASTAndPurifyStep(Step):
    """阶段 6-7: AST 降维、语义提纯与空载拦截"""
    def process(self, ctx):
        ctx.body_content = ctx.engine.transclusion_resolver.expand(ctx.raw_body)
        ctx.body_content = ctx.engine.ssg_adapter.convert_callouts(ctx.body_content)

        purify_opts = ctx.engine.config.system.ai_context_purification
        ctx.ai_pure_body = strip_technical_noise(ctx.body_content, purify_opts)
        
        substance_threshold = ctx.engine.config.translation.empty_content_threshold
        is_empty = len(ctx.ai_pure_body.strip()) < substance_threshold
        is_draft = str(ctx.fm_dict.get('draft')).lower() == 'true' or str(ctx.fm_dict.get('publish')).lower() == 'false'
        
        if is_empty or is_draft:
            if ctx.engine.meta.get_doc_info(ctx.rel_path):
                reason = "语义字数不足" if is_empty else "处于 Draft/离线模式"
                logger.info(f"🛑 拦截生效: {ctx.rel_path} {reason}，已执行物理下线。")
                ctx.engine.janitor.gc_node(ctx.rel_path, ctx.route_prefix, ctx.route_source, ctx.is_dry_run)
            ctx.is_aborted = True

class MetadataAndHashStep(Step):
    """阶段 8-9: 元数据注入与指纹核验"""
    def process(self, ctx):
        defaults = ctx.engine.fm_defaults or {}
        ctx.base_fm = {k: v for k, v in defaults.items() if v is not None and str(v).strip() != ""}
        ctx.base_fm.update(ctx.fm_dict)
        
        for array_field in ['keywords', 'tags', 'categories']:
            if array_field in ctx.base_fm:
                ctx.base_fm[array_field] = normalize_keywords(ctx.base_fm[array_field])
        
        if 'slug' in ctx.base_fm: del ctx.base_fm['slug']

        ctx.current_hash = hashlib.md5((str(ctx.base_fm) + ctx.body_content).encode('utf-8')).hexdigest()
        
        old_info = ctx.engine.meta.get_doc_info(ctx.rel_path)
        ctx.engine.meta.register_document(ctx.rel_path, ctx.title, source_hash=ctx.current_hash)
        ctx.doc_info = ctx.engine.meta.get_doc_info(ctx.rel_path)

        if not old_info.get("slug"):
            hit = ctx.engine.meta.find_by_hash(ctx.current_hash)
            if hit and hit.get("slug"):
                ctx.engine.meta.register_document(
                    ctx.rel_path, ctx.title, 
                    slug=hit.get("slug"), 
                    seo_data=hit.get("seo"), 
                    shadow_hash=hit.get("shadow_hash")
                )
                
                try:
                    ext = os.path.splitext(ctx.rel_path)[1].lower()
                    targets = ctx.engine.config.i18n_settings.targets
                    for t in targets:
                        code = t.get('lang_code')
                        if not code: continue
                        
                        old_rel_path = hit.get('_rel_path')
                        old_route_source = hit.get('source')
                        old_route_prefix = hit.get('prefix')
                        
                        abs_old_src_dir = os.path.join(ctx.engine.paths['vault'], old_route_source)
                        old_sub_rel_path = os.path.relpath(os.path.join(ctx.engine.paths['vault'], old_rel_path), abs_old_src_dir).replace('\\', '/')
                        old_sub_dir = os.path.dirname(old_sub_rel_path).replace('\\', '/')
                        if old_sub_dir == '.': old_sub_dir = ""
                        
                        old_mapped_sub_dir = ctx.engine.route_manager.get_mapped_sub_dir(old_sub_dir, is_dry_run=ctx.is_dry_run, allow_ai=False)
                        
                        old_shadow_tgt = ctx.engine.route_manager.resolve_physical_path(
                            ctx.engine.paths['shadow'], code, old_route_prefix, old_mapped_sub_dir, hit.get('slug'), ext
                        )
                        
                        if os.path.exists(old_shadow_tgt):
                            abs_src_dir = os.path.join(ctx.engine.paths['vault'], ctx.route_source)
                            sub_rel_path = os.path.relpath(ctx.src_path, abs_src_dir).replace('\\', '/')
                            sub_dir = os.path.dirname(sub_rel_path).replace('\\', '/')
                            if sub_dir == '.': sub_dir = ""
                            new_mapped_sub_dir = ctx.engine.route_manager.get_mapped_sub_dir(sub_dir, is_dry_run=ctx.is_dry_run, allow_ai=False)
                            
                            new_shadow_tgt = ctx.engine.route_manager.resolve_physical_path(
                                ctx.engine.paths['shadow'], code, ctx.route_prefix, new_mapped_sub_dir, hit.get('slug'), ext
                            )
                            
                            if old_shadow_tgt != new_shadow_tgt:
                                os.makedirs(os.path.dirname(new_shadow_tgt), exist_ok=True)
                                shutil.copy2(old_shadow_tgt, new_shadow_tgt)
                                logger.debug(f"   └── ⚡️ [影子资产漫游] 翻译成品已同步对齐: {code}")
                except Exception as shadow_err:
                    logger.warning(f"   └── ⚠️ [影子漫游失败] 物理对齐过程中断 (不影响主流程): {shadow_err}")

                ctx.doc_info = ctx.engine.meta.get_doc_info(ctx.rel_path)

        is_toxic_slug = '%' in str(ctx.doc_info.get("slug", ""))
        if not ctx.force_sync and not is_toxic_slug and old_info.get("source_hash") == ctx.current_hash: 
            ctx.is_skipped = True
            ctx.is_aborted = True

class AISlugAndSEOStep(Step):
    """阶段 11-12: Slug 重塑与 SEO 引擎"""
    def process(self, ctx):
        ctx.node_start_perf = time.perf_counter()
        prefix_log = "[Dry-Run 演练]" if ctx.is_dry_run else "[创作同步]"
        if ctx.is_silent_edit:
            logger.info(f"🤫 [静默微调] {ctx.rel_path} 正在执行本地排版直传...")
        else:
            logger.info(f"{prefix_log} 正在加工文章: {ctx.rel_path}")

        slug_raw = ctx.doc_info.get("slug")
        max_slug_len = ctx.engine.config.translation.max_slug_length
        if slug_raw and (
            '%' in slug_raw or 
            bool(re.search(r'[\u4e00-\u9fa5]', slug_raw)) or
            len(slug_raw) > max_slug_len or
            "architectural" in slug_raw.lower()
        ):
            logger.warning("🩹 [账本排毒] 检测到放射性长 Slug，正在强行作废并触发物理重构...")
            slug_raw = None
        
        if not slug_raw:
            slug_mode = ctx.engine.config.translation.slug_mode
            if slug_mode == 'ai' and not ctx.is_silent_edit:
                if ctx.is_dry_run:
                    slug_raw, slug_success = f"dry-run-{int(time.time())}", True
                else:
                    try:
                        slug_raw, slug_success = ctx.engine.translator.generate_slug(ctx.title, is_dry_run=False)
                    except Exception:
                        slug_success, slug_raw = False, None
                if not slug_success: ctx.ai_health_flag[0] = False
            else:
                english_only = re.sub(r'[^a-z0-9\-]', '', ctx.title.lower().replace(' ', '-'))
                clean_slug = re.sub(r'-+', '-', english_only).strip('-')
                if not clean_slug:
                    clean_slug = f"doc-{hashlib.md5(ctx.title.encode('utf-8')).hexdigest()[:6]}"
                slug_raw = clean_slug
                
        ctx.slug = slug_raw
        ctx.seo_data = ctx.doc_info.get("seo", {})
        if not ctx.is_silent_edit:
            if 'description' in ctx.seo_data or 'keywords' in ctx.seo_data: 
                ctx.seo_data = {}

class ContextualImageAltStep(Step):
    """阶段 12.5: AI 驱动的媒体智能引擎 (ADMI v2.0 - 视觉感知与语义复用)"""
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

        logger.info(f"🔍 [ADMI 媒体智能] 在 {ctx.rel_path} 中侦测到 {len(matches)} 处空白图片标签，启动视觉感知矩阵...")
        
        offset = 0
        new_content = ctx.body_content

        for m in matches:
            img_path = m.group(1)
            img_name = os.path.basename(img_path)
            
            abs_img_path = ""
            if img_path.startswith(('http://', 'https://', 'data:')):
                continue
                
            potential_paths = [
                os.path.join(os.path.dirname(ctx.src_path), img_path),
                os.path.join(ctx.engine.paths['vault'], img_path.lstrip('/'))
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
                    
                    logger.debug(f"🔍 [资产审计] Hash: {asset_hash[:8]} | File: {img_name}")
                    cached_meta = ctx.engine.meta.get_asset_metadata(asset_hash)
                    if cached_meta and cached_meta.get("alt_texts", {}).get(source_lang):
                        alt_text = cached_meta["alt_texts"][source_lang]
                        logger.info(f"   └── 🧬 [语义复用] '{img_name}' 匹配到指纹缓存 ({source_lang})。")
                    elif cached_meta and cached_meta.get("alt_text"):
                        # 降级处理旧版单字符串缓存
                        alt_text = cached_meta["alt_text"]
                        logger.info(f"   └── 🧬 [语义复用] '{img_name}' 匹配到旧版指纹缓存。")
                    else:
                        ext = os.path.splitext(abs_img_path)[1].lower().lstrip('.')
                        mime_type = f"image/{ext}" if ext != 'jpg' else "image/jpeg"
                        
                        start_idx = max(0, m.start() - 300)
                        end_idx = min(len(ctx.body_content), m.end() + 300)
                        surrounding_text = ctx.body_content[start_idx:end_idx]
                        
                        logger.debug(f"   └── ⏳ [算力请求] 正在对图像执行视觉分析: {img_name}")
                        desc = ctx.engine.translator.describe_image(img_bytes, mime_type, context_text=surrounding_text)
                        
                        if desc:
                            alt_text = desc.strip()
                            ctx.engine.meta.register_asset_metadata(asset_hash, alt_text=alt_text, lang=source_lang)
                            logger.info(f"   └── ✨ [视觉补全] '{img_name}' -> 生成描述: {alt_text}")
                except Exception as e:
                    logger.debug(f"   └── ⚠️ [视觉链路中断] 处理物理图片失败: {e}")

            if not alt_text:
                # 文本语义兜底逻辑
                start_idx = max(0, m.start() - 250)
                end_idx = min(len(ctx.body_content), m.end() + 250)
                surrounding_text = ctx.body_content[start_idx:end_idx]
                prompt = (
                    f"请根据上下文推测图片 '{img_name}' 展示的内容，生成一句精确的 SEO Alt 描述。"
                    f"只输出文本本身，不要引号。\n\n【上下文】:\n{surrounding_text}"
                )
                try:
                    raw_alt = ctx.engine.translator.translate(prompt, "Auto", "Image Alt Generation")
                    alt_text = raw_alt.strip().replace('\n', '').replace('"', '').replace('[', '').replace(']', '')
                    if asset_hash:
                        ctx.engine.meta.register_asset_metadata(asset_hash, alt_text=alt_text, lang=source_lang)
                    logger.info(f"   └── 🩹 [文本兜底] '{img_name}' 基于上下文推断为: {alt_text}")
                except Exception as e:
                    logger.debug(f"   └── 🛑 [全部降级] 图片描述生成失败: {e}")
                    continue

            # 🚀 [Resonance 增强]：执行多语言同步翻译与固化
            if asset_hash and multilingual_enabled:
                targets = ctx.engine.i18n.targets
                for target in targets:
                    t_code = target.lang_code
                    if t_code == source_lang: continue
                    
                    current_meta = ctx.engine.meta.get_asset_metadata(asset_hash)
                    if t_code in current_meta.get("alt_texts", {}):
                        continue
                        
                    try:
                        if t_code:
                            t_code_std = str(t_code).strip().lower()
                            target_lang_name = ctx.engine.get_lang_name_by_code(t_code)
                            t_alt = ctx.engine.translator.translate(alt_text, "Auto", target_lang_name, context_type="alt_text")
                            ctx.engine.meta.register_asset_metadata(asset_hash, alt_text=t_alt.strip(), lang=t_code_std)
                    except Exception as te:
                        logger.debug(f"   └── ⚠️ [语种对齐失败] {t_code}: {te}")

            new_img_md = f"![{alt_text}]({img_path})"
            new_content = new_content[:m.start()+offset] + new_img_md + new_content[m.end()+offset:]
            offset += len(new_img_md) - len(m.group(0))

        ctx.body_content = new_content

class MaskingAndRoutingStep(Step):
    """阶段 13-14: 物理遮蔽与动态路由推导"""
    def process(self, ctx):
        def mask_fn(m):
            matched = m.group(0)
            link_match = re.match(r'^(\!?\[.*?\]\()([^)]+)(\))$', matched)
            if link_match:
                prefix = link_match.group(1) 
                url_part = link_match.group(2) 
                suffix = link_match.group(3) 
                
                # 🚀 [Resonance 架构对齐]：图片标签应整体遮蔽，以确保解蔽时能从 Ledger 提取多语言 Alt
                if prefix.startswith('!['):
                    ctx.masks.append(matched) # 整体遮蔽
                    return f"[[STB_MASK_{len(ctx.masks)-1}]]"
                else:
                    ctx.masks.append(f"URL_ONLY_LNK:{url_part}")
                    return f"{prefix}[[STB_MASK_{len(ctx.masks)-1}]]{suffix}"
            
            ctx.masks.append(matched)
            return f"[[STB_MASK_{len(ctx.masks)-1}]]"
        
        mask_pattern = r'\$\$.*?\$\$|\$[^\$]+\$|\!\[\[[^\]]+\]\]|\[\[[^\]]+\]\]|\!\[[^\]]*\]\([^)]+\)|\[[^\]]*\]\([^)]+\)|\\[!"#$%&\'()*+,\-./:;<=>?@[\\\]^_`{|}~]'
        ctx.masked_source = re.sub(mask_pattern, mask_fn, ctx.body_content, flags=re.DOTALL)

        abs_src_dir = os.path.join(ctx.engine.paths['vault'], ctx.route_source)
        sub_rel_path = os.path.relpath(ctx.src_path, abs_src_dir).replace('\\', '/')
        sub_dir = os.path.dirname(sub_rel_path).replace('\\', '/')
        if sub_dir == '.': sub_dir = ""
        
        ctx.mapped_sub_dir = ctx.engine.route_manager.get_mapped_sub_dir(sub_dir, is_dry_run=ctx.is_dry_run, allow_ai=not ctx.is_silent_edit)
        
        ctx.engine.meta.register_document(
            ctx.rel_path, ctx.title, 
            slug=ctx.slug, 
            route_prefix=ctx.route_prefix, 
            route_source=ctx.route_source
        )