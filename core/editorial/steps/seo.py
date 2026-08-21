# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Pipeline Steps Shard
工序职责：AISlugAndSEOStep (Slug 重塑与 SEO 引擎)
🛡️ [AEL-Iter-v5.3]：基于分层架构的 TDR 复健版本。
"""

import os
import re
import hashlib
from core.utils.tracing import tlog
from core.editorial.runner import PipelineStep

class AISlugAndSEOStep(PipelineStep):
    """阶段 11-12: Slug 重塑与 SEO 引擎"""
    PLUGIN_ID = "ai_slug_seo"
    DISPLAY_NAME = "AI Slug 与 SEO 治理"
    VERSION = "V5.3"
    DESCRIPTION = "利用 AI 自动生成友好的 URL Slug，并注入工业级 SEO 元数据。"

    def process(self, ctx):
        slug_raw = ctx.doc_info.get("slug")
        
        # 👑 [物理主权显式声明最高优先级]
        explicit_slug = getattr(ctx, 'explicit_slug', None) or (getattr(ctx, 'fm_dict', None) or {}).get('slug')
        if explicit_slug and str(explicit_slug).strip():
            slug_raw = str(explicit_slug).strip()
            tlog.info(f"🏷️ [显式 Slug] 采用原稿 Frontmatter 声明的 Slug: '{slug_raw}' (文档: {ctx.rel_path})")

        # 🛡️ [V48.3] 首页主权防护：强制锁定 Index.md 的 Slug 为 'index'
        is_homepage = ctx.rel_path.lower().endswith('index.md') or ctx.rel_path.lower().endswith('index.mdx')
        if is_homepage:
            slug_raw = "index"
            tlog.info(f"🏠 [首页防护] 强制将 {ctx.rel_path} 的 Slug 锁定为 'index'")

        # 🚀 [V26.5] 显性重构支持：如果开启了 --re-slug，强制重置非首页的 Slug
        if getattr(ctx.engine, 'args', None) and getattr(ctx.engine.args, 're_slug', False) and not is_homepage and not explicit_slug:
            tlog.info(f"🔄 [Slug 重塑] 检测到 --re-slug 标志，正在强制重新生成 {ctx.rel_path} 的 URL...")
            slug_raw = None

        if slug_raw and not explicit_slug:
            is_json_leak = any(k in slug_raw.lower() for k in ["description", "keywords", "{", "\""])
            # 🛡️ 拆分基本文件名部分校验，避免嵌套路径长度防错误杀
            slug_leaf = os.path.basename(slug_raw)
            if is_json_leak or len(slug_leaf) > 80 or '%' in slug_raw or bool(re.search(r'[\u4e00-\u9fa5]', slug_raw)):
                tlog.warning(f"⚠️ [Slug 拦截] 侦测到非法 Slug: {slug_raw[:30]}... 已强制重置")
                slug_raw = None

        # 计算映射后的子目录路径以用于 Slug 路径增强
        vault_path = ctx.engine.paths.get('vault', '.')
        sub = os.path.dirname(os.path.relpath(ctx.src_path, os.path.join(vault_path, ctx.route_source))).replace('\\', '/')
        if sub == '.': sub = ""
        mapped_sub = ctx.engine.route_manager.get_mapped_sub_dir(sub, allow_ai=not ctx.is_silent_edit)

        if not slug_raw:
            slug_mode = ctx.engine.config.translation.slug_mode
            # 🚀 [V74.98] 算力总控前置防御：只有开启了 AI 算力，才尝试走 AI 生成 Slug 路径
            if slug_mode == 'ai' and getattr(ctx.engine.config.translation, 'enable_ai', True) and not ctx.is_silent_edit:
                if ctx.is_dry_run:
                    slug_raw, slug_success = f"dry-run-{re.sub(r'[^a-z0-9]', '-', ctx.title.lower())[:30]}", True
                else:
                    try:
                        # 🛡️ [V35.1] AI 熔断保护
                        if ctx.engine.translator:
                            slug_raw, slug_success = ctx.engine.translator.generate_slug(ctx.title, is_dry_run=False)
                        else: slug_success, slug_raw = False, None
                    except Exception: slug_success, slug_raw = False, None
                if not slug_success: ctx.ai_health_flag[0] = False

        # 🚀 [V35.1] 物理主权自愈兜底：如果 AI 失败或模式不支持，优先采用拼音转化/英文字符清洗
        if not slug_raw:
            english_only = re.sub(r'[^a-z0-9\-]', '', ctx.title.lower().replace(' ', '-'))
            slug_raw = re.sub(r'-+', '-', english_only).strip('-')
            if not slug_raw and ctx.title:
                try:
                    import pypinyin
                    py_list = pypinyin.lazy_pinyin(ctx.title)
                    py_str = "-".join(py_list)
                    slug_raw = re.sub(r'[^a-z0-9\-]', '', py_str.lower())
                    slug_raw = re.sub(r'-+', '-', slug_raw).strip('-')
                except Exception:
                    pass
            if not slug_raw:
                slug_raw = f"doc-{hashlib.md5((ctx.title or 'untitled').encode('utf-8')).hexdigest()[:6]}"

        # 🛡️ [Slug 目录增强自愈] 结合翻译配置中的 slug_dir_mode 做物理前缀或路径嵌套处理 (包含前缀去重防护)
        from core.logic.ai.ai_logic_hub import AILogicHub
        slug_dir_mode = getattr(ctx.engine.config.translation, 'slug_dir_mode', 'flat')
        if slug_dir_mode in ('prefix', 'nested') and mapped_sub:
            if slug_dir_mode == 'prefix':
                safe_dir = mapped_sub.replace('/', '-')
                prefix = f"{safe_dir}-"
                if not slug_raw.startswith(prefix):
                    slug_raw = AILogicHub.clean_slug(f"{safe_dir}-{slug_raw}")
                else:
                    slug_raw = AILogicHub.clean_slug(slug_raw)
            elif slug_dir_mode == 'nested':
                prefix = f"{mapped_sub}/"
                if not slug_raw.startswith(prefix):
                    slug_raw = AILogicHub.clean_slug(f"{mapped_sub}/{slug_raw}")
                else:
                    slug_raw = AILogicHub.clean_slug(slug_raw)
        else:
            slug_raw = AILogicHub.clean_slug(slug_raw)

        ctx.slug = slug_raw.lower() if slug_raw else "index" if is_homepage else "untitled"


        # 🚀 [V52.13] SEO 载荷合并逻辑：优先保留当前 Context 中已计算的物理指标 (如 word_count)
        # 仅当 Context 中缺失且账本中有值时，才从账本中同步。
        ledger_seo = ctx.doc_info.get("seo_data") or ctx.doc_info.get("seo") or {}
        if not ctx.seo_data:
            ctx.seo_data = ledger_seo
        else:
            # 增量合并：保留 Context 中的物理指标，补全账本中的 SEO 描述
            for k, v in ledger_seo.items():
                if k not in ctx.seo_data or not ctx.seo_data[k]:
                    ctx.seo_data[k] = v
        
        # 🚀 [V52.13] 物理指标持久化：确保字数等关键参数不被 AI 覆盖逻辑抹除
        if hasattr(ctx, 'seo_data') and 'word_count' not in ctx.seo_data:
             # 如果之前没算，这里补算一次（通常在 read_normalize 已经算过了）
             clean_text = re.sub(r'[\s\n\t]+', ' ', ctx.raw_body)
             en_words = len(re.findall(r'[a-zA-Z0-9\-\']+', clean_text))
             zh_chars = len(re.findall(r'[\u4e00-\u9fa5]', ctx.raw_body))
             ctx.seo_data['word_count'] = en_words + zh_chars

        # 🚀 [V53.0] 出版模式 SEO 策略分流：根据当前治理蓝图调度对应的处理器
        try:
            from core.logic.seo.factory import SeoProcessorFactory
            gov = ctx.engine.config.governance
            processor = SeoProcessorFactory.create(gov.publishing_mode, gov.seo_strategy)
            seo_enhancement = processor.process(ctx)
            if seo_enhancement:
                # 增量合并：处理器输出不覆盖已有的物理指标（如 word_count）
                for k, v in seo_enhancement.items():
                    if k not in ctx.seo_data or not ctx.seo_data[k]:
                        ctx.seo_data[k] = v
        except Exception as e:
            tlog.warning(f"⚠️ [SEO 策略] 处理器执行异常，已安全降级: {e}")
