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
import threading
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

        purify_opts = ctx.engine.sys_tuning.get('ai_context_purification', {
            'strip_styles': True, 'strip_mdx_imports': True, 
            'strip_comments': True, 'strip_code_blocks': True
        })
        ctx.ai_pure_body = strip_technical_noise(ctx.body_content, purify_opts)
        
        substance_threshold = ctx.engine.config.get('empty_content_threshold', ctx.engine.sys_cfg.get('empty_content_threshold', 15))
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
        if 'keywords' in ctx.base_fm:
            ctx.base_fm['keywords'] = normalize_keywords(ctx.base_fm['keywords'])
        
        if 'slug' in ctx.base_fm: del ctx.base_fm['slug']

        ctx.current_hash = hashlib.md5((str(ctx.base_fm) + ctx.body_content).encode('utf-8')).hexdigest()
        ctx.engine.meta.register_document(ctx.rel_path, ctx.title)
        ctx.doc_info = ctx.engine.meta.get_doc_info(ctx.rel_path)

        is_toxic_slug = '%' in str(ctx.doc_info.get("slug", ""))
        if not ctx.force_sync and not is_toxic_slug and ctx.doc_info.get("hash") == ctx.current_hash: 
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
        
        # 🚀 强化排雷：只要历史账本的 slug 里哪怕沾了一个中文字符，强行作废重做
        if slug_raw and ('%' in slug_raw or bool(re.search(r'[\u4e00-\u9fa5]', slug_raw))):
            slug_raw = None
        
        if not slug_raw:
            if not ctx.is_silent_edit:
                # [AI 翻译模式]
                if ctx.is_dry_run:
                    slug_raw, slug_success = f"dry-run-{int(time.time())}", True
                else:
                    try:
                        prompt = f"Translate the following title to a URL slug. ONLY output lowercase english & hyphens: '{ctx.title}'"
                        raw_slug_res = ctx.engine.translator.translate(prompt, "Auto", "URL Slug")
                        slug_raw = re.sub(r'[^a-z0-9\-]', '', raw_slug_res.lower().replace(' ', '-').strip('-'))
                        slug_success = bool(slug_raw)
                    except Exception:
                        slug_success, slug_raw = False, None
                if not slug_success: ctx.ai_health_flag[0] = False
            else:
                # 🚀 [核心修复] 静默降级模式下的绝对纯净兜底
                # 1. 暴力抹除所有非英文字母和数字
                english_only = re.sub(r'[^a-z0-9\-]', '', ctx.title.lower().replace(' ', '-'))
                clean_slug = re.sub(r'-+', '-', english_only).strip('-')
                
                # 2. 如果标题全是中文，抹除后变成空字符串了，则触发 Hash 算法生成唯一短链接
                if not clean_slug:
                    import hashlib
                    clean_slug = f"doc-{hashlib.md5(ctx.title.encode('utf-8')).hexdigest()[:6]}"
                    
                slug_raw = clean_slug
                
        ctx.slug = slug_raw

        ctx.seo_data = ctx.doc_info.get("seo", {})
        if 'description' in ctx.seo_data or 'keywords' in ctx.seo_data: ctx.seo_data = {}

class MaskingAndRoutingStep(Step):
    """阶段 13-14: 物理遮蔽与动态路由推导"""
    def process(self, ctx):
        def mask_fn(m):
            matched = m.group(0)
            
            # 🚀 架构升级：精准暴露 Markdown 图片与链接的可读文本
            link_match = re.match(r'^(\!?\[.*?\]\()([^)]+)(\))$', matched)
            if link_match:
                prefix = link_match.group(1) 
                url_part = link_match.group(2) 
                suffix = link_match.group(3) 
                
                # 强类型标识：在存入 masks 时打上标记，让 engine.py 知道这是个纯 URL
                if prefix.startswith('!['):
                    ctx.masks.append(f"URL_ONLY_IMG:{url_part}")
                else:
                    ctx.masks.append(f"URL_ONLY_LNK:{url_part}")
                    
                # 巧妙的返回：![并发测试图]([[STB_MASK_n]])
                # 这样 AI 就能直接看到中文描述并将其翻译，而 URL 依然处于绝对安全状态
                return f"{prefix}[[STB_MASK_{len(ctx.masks)-1}]]{suffix}"
            
            # 兜底：其他情况（如 $$公式$$）全量屏蔽
            ctx.masks.append(matched)
            return f"[[STB_MASK_{len(ctx.masks)-1}]]"
        
        # 保留原有的基础屏蔽（屏蔽公式、Obsidian 链接等）
        mask_pattern = r'\$\$.*?\$\$|\$[^\$]+\$|\!\[\[[^\]]+\]\]|\[\[[^\]]+\]\]|\!\[[^\]]*\]\([^)]+\)|\[[^\]]*\]\([^)]+\)|\\[!"#$%&\'()*+,\-./:;<=>?@[\\\]^_`{|}~]'
        ctx.masked_source = re.sub(mask_pattern, mask_fn, ctx.body_content, flags=re.DOTALL)

        # 🚀 核心修复：彻底删掉下面这段“过度保护”代码！
        # 让大模型直接“看到”完整的 <Card> 组件，它会遵循 Prompt 乖乖去翻译 title 和内部文本
        # if ctx.rel_path.lower().endswith('.mdx'):
        #     logic_blocks = ctx.engine.mdx_resolver.extract_logic_blocks(ctx.masked_source)
        #     for block in logic_blocks:
        #         if isinstance(block, tuple): block = "".join(block)
        #         ctx.masks.append(block)
        #         ctx.masked_source = ctx.masked_source.replace(block, f"[[STB_MASK_{len(ctx.masks)-1}]]")

        abs_src_dir = os.path.join(ctx.engine.paths['vault'], ctx.route_source)
        sub_rel_path = os.path.relpath(ctx.src_path, abs_src_dir).replace('\\', '/')
        sub_dir = os.path.dirname(sub_rel_path).replace('\\', '/')
        if sub_dir == '.': sub_dir = ""
        
        ctx.mapped_sub_dir = ctx.engine.route_manager.get_mapped_sub_dir(sub_dir, is_dry_run=ctx.is_dry_run, allow_ai=not ctx.is_silent_edit)

class ContextualImageAltStep(Step):
    """阶段 12.5: 上下文感知的图片 Alt 自动生成引擎"""
    def process(self, ctx):
        if ctx.is_aborted or ctx.is_dry_run or ctx.is_silent_edit:
            return

        pattern = re.compile(r'!\[\s*\]\(([^)]+)\)')
        matches = list(pattern.finditer(ctx.body_content))
        
        if not matches: return 

        logger.info(f"🔍 [SEO 引擎] 在 {ctx.rel_path} 中侦测到 {len(matches)} 处空白图片标签，正在启动 AI 上下文推演...")
        
        offset = 0
        new_content = ctx.body_content

        for m in matches:
            img_path = m.group(1)
            img_name = os.path.basename(img_path)

            start_idx = max(0, m.start() - 250)
            end_idx = min(len(ctx.body_content), m.end() + 250)
            surrounding_text = ctx.body_content[start_idx:end_idx]

            prompt = (
                f"你是一个资深的 SEO 专家。请根据以下文章截取的上下文，"
                f"推测这张名为 '{img_name}' 的图片中可能展示了什么内容，"
                f"并为其生成一句简短、精确、利于搜索引擎抓取的图片 Alt 描述。\n\n"
                f"要求：只输出描述文本本身，绝对不要有任何多余的解释、引号或标点。\n\n"
                f"【上下文片段】:\n...{surrounding_text}..."
            )

            try:
                raw_alt = ctx.engine.translator.translate(prompt, "Auto", "Image Alt Generation")
                alt_text = raw_alt.strip().replace('\n', '').replace('"', '').replace('[', '').replace(']', '')
                new_img_md = f"![{alt_text}]({img_path})"
                
                new_content = new_content[:m.start()+offset] + new_img_md + new_content[m.end()+offset:]
                offset += len(new_img_md) - len(m.group(0))
                logger.info(f"   └── ✨ [视觉 SEO 补全] '{img_name}' -> 注入标签: [{alt_text}]")
                
            except Exception as e:
                logger.debug(f"   └── ⚠️ [视觉 SEO 跳过] 推理图片 '{img_name}' 失败: {e}")

        ctx.body_content = new_content