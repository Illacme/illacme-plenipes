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
        
        # 🚀 全域数组字段矩阵化：彻底封堵一切以字符串形式存在的结构
        # 将原始解析产生的纯文本字段，通过清洗引擎全部投递为 List 数组
        for array_field in ['keywords', 'tags', 'categories']:
            if array_field in ctx.base_fm:
                ctx.base_fm[array_field] = normalize_keywords(ctx.base_fm[array_field])
        
        if 'slug' in ctx.base_fm: del ctx.base_fm['slug']

        ctx.current_hash = hashlib.md5((str(ctx.base_fm) + ctx.body_content).encode('utf-8')).hexdigest()
        
        # 🚀 [V18.6 关键修复] 同步哈希指纹前先抓取旧快照，用于判定“移动”还是“修改”
        old_info = ctx.engine.meta.get_doc_info(ctx.rel_path)
        ctx.engine.meta.register_document(ctx.rel_path, ctx.title, source_hash=ctx.current_hash)
        ctx.doc_info = ctx.engine.meta.get_doc_info(ctx.rel_path)

        # 🚀 [V18.6 零 Token 搬家优化 V2：影子资产漫游]
        # 如果当前路径是新出现的（没有历史 slug），尝试在全站范围内寻找指纹一致的“前世”
        if not old_info.get("slug"):
            hit = ctx.engine.meta.find_by_hash(ctx.current_hash)
            if hit and hit.get("slug"):
                logger.info(f"🧬 [指纹继承] {ctx.rel_path} 定位到全站相同内容指纹，开始迁移 AI 影子资产...")
                
                # 1. 内存指纹继承
                ctx.engine.meta.register_document(
                    ctx.rel_path, ctx.title, 
                    slug=hit.get("slug"), 
                    seo_data=hit.get("seo"), 
                    shadow_hash=hit.get("shadow_hash")
                )
                
                # 2. 物理影子漫游：将翻译好的影子产物也“搬”到新家对应的位置
                try:
                    ext = os.path.splitext(ctx.rel_path)[1].lower()
                    targets = ctx.engine.config.i18n_settings.targets
                    for t in targets:
                        code = t.get('lang_code')
                        if not code: continue
                        
                        # 构造旧影子路径
                        # 注意：MaskingAndRoutingStep 之后才会确定 mapped_sub_dir，
                        # 但这里我们可以根据 hit 的元数据手动推导
                        old_rel_path = hit.get('_rel_path')
                        old_route_source = hit.get('source')
                        old_route_prefix = hit.get('prefix')
                        
                        abs_old_src_dir = os.path.join(ctx.engine.paths['vault'], old_route_source)
                        old_sub_rel_path = os.path.relpath(os.path.join(ctx.engine.paths['vault'], old_rel_path), abs_old_src_dir).replace('\\', '/')
                        old_sub_dir = os.path.dirname(old_sub_rel_path).replace('\\', '/')
                        if old_sub_dir == '.': old_sub_dir = ""
                        
                        # 模拟路由映射器的旧路径解析
                        old_mapped_sub_dir = ctx.engine.route_manager.get_mapped_sub_dir(old_sub_dir, is_dry_run=ctx.is_dry_run, allow_ai=False)
                        
                        old_shadow_tgt = ctx.engine.route_manager.resolve_physical_path(
                            ctx.engine.paths['shadow'], code, old_route_prefix, old_mapped_sub_dir, hit.get('slug'), ext
                        )
                        
                        # 如果旧影子存在，执行“影子克隆”
                        if os.path.exists(old_shadow_tgt):
                            # 这里我们暂时无法构造“新”影子路径，因为 MaskingAndRoutingStep 还没跑，ctx.mapped_sub_dir 还没定
                            # 提前运行一部分逻辑：
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

                # 重新载入注入后的模型数据
                ctx.doc_info = ctx.engine.meta.get_doc_info(ctx.rel_path)

        is_toxic_slug = '%' in str(ctx.doc_info.get("slug", ""))
        # 🚀 [状态机契约修正]：只有当“旧路径”已经存在，且“哈希一致”时才允许 Abort
        # 如果是新移动过来的路径，old_info["source_hash"] 会是 None，从而强制其至少运行一次以确保写盘。
        if not ctx.force_sync and not is_toxic_slug and old_info.get("source_hash") == ctx.current_hash: 
            # 🚀 [V34.5 修复] 引入显式跳过信号，防止其被误计入“隔离/下线”统计中
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
        
        # 🚀 [V33.5] 旗舰级账本排毒：只要 Slug 包含中文字符、长度过载、或包含指令残留词，一律作废重做
        max_slug_len = ctx.engine.config.translation.max_slug_length
        if slug_raw and (
            '%' in slug_raw or 
            bool(re.search(r'[\u4e00-\u9fa5]', slug_raw)) or
            len(slug_raw) > max_slug_len or
            "architectural" in slug_raw.lower()
        ):
            logger.warning(f"🩹 [账本排毒] 检测到放射性长 Slug，正在强行作废并触发物理重构...")
            slug_raw = None
        
        if not slug_raw:
            # 🚀 [V32 逻辑激活]：根据 slug_mode 决定生成策略
            slug_mode = ctx.engine.config.translation.slug_mode
            
            if slug_mode == 'ai' and not ctx.is_silent_edit:
                # [AI 模式]
                if ctx.is_dry_run:
                    slug_raw, slug_success = f"dry-run-{int(time.time())}", True
                else:
                    try:
                        # 🚀 [V33 专家版回填]：调用全量封测过的工业级 Slug 生成器
                        slug_raw, slug_success = ctx.engine.translator.generate_slug(ctx.title, is_dry_run=False)
                    except Exception:
                        slug_success, slug_raw = False, None
                if not slug_success: ctx.ai_health_flag[0] = False
            else:
                # [Local 模式] 或 [静默编辑模式]：执行本地绝对纯净兜底
                # 1. 暴力抹除所有非英文字母和数字
                english_only = re.sub(r'[^a-z0-9\-]', '', ctx.title.lower().replace(' ', '-'))
                clean_slug = re.sub(r'-+', '-', english_only).strip('-')
                
                # 2. 如果标题全是中文，抹除后变成空字符串了，则触发 Hash 算法生成唯一短链接
                if not clean_slug:
                    clean_slug = f"doc-{hashlib.md5(ctx.title.encode('utf-8')).hexdigest()[:6]}"
                    
                slug_raw = clean_slug
                
        ctx.slug = slug_raw

        # ==========================================
        # 🚀 核心修复：SEO 缓存保护机制
        # ==========================================
        ctx.seo_data = ctx.doc_info.get("seo", {})
        
        # 只有在非静默模式（需要 AI 重新生成时），才主动清空旧的 SEO 数据
        # 如果处于静默模式 (is_silent_edit)，则死死守住旧数据，以供跨语种共享
        if not ctx.is_silent_edit:
            if 'description' in ctx.seo_data or 'keywords' in ctx.seo_data: 
                ctx.seo_data = {}
                
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

        abs_src_dir = os.path.join(ctx.engine.paths['vault'], ctx.route_source)
        sub_rel_path = os.path.relpath(ctx.src_path, abs_src_dir).replace('\\', '/')
        sub_dir = os.path.dirname(sub_rel_path).replace('\\', '/')
        if sub_dir == '.': sub_dir = ""
        
        ctx.mapped_sub_dir = ctx.engine.route_manager.get_mapped_sub_dir(sub_dir, is_dry_run=ctx.is_dry_run, allow_ai=not ctx.is_silent_edit)
        
        # 🚀 [V17.5 终极加固] 路由画像实时固化：在保洁启动前，必须让账本知道最新的“合法地址”
        ctx.engine.meta.register_document(
            ctx.rel_path, 
            ctx.title, 
            slug=ctx.slug, 
            route_prefix=ctx.route_prefix, 
            route_source=ctx.route_source
        )

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