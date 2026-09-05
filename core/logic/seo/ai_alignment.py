#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Alignment SEO Processor
职责：智能增强模式的「AI 算法对齐」策略。
🚀 [V53.0] 利用 AI 优化 CTR 和关键词埋点，精准投喂搜索引擎。

处理逻辑：
1. AI 分析全文语义，生成高点击率的 SEO 标题
2. AI 提取高热搜索词并自然埋入描述
3. AI 生成精准的 keywords 标签
4. 所有结果遵守"元数据优先"底线
"""

import json
from .base import BaseSeoProcessor
from core.logic.ai.ai_logic_hub import AILogicHub
from core.utils.tracing import tlog




class AIAlignmentProcessor(BaseSeoProcessor):
    """🛰️ AI 算法对齐：智能增强模式的默认 SEO 策略。

    利用 AI 深度分析内容语义，生成高 CTR 的标题和描述，
    并将高热搜索词自然埋入元数据，实现对搜索引擎的"精准投喂"。
    """

    def process(self, ctx) -> dict:
        import hashlib
        body = getattr(ctx, 'ai_pure_body', '') or getattr(ctx, 'raw_body', '')
        # 截取前 2000 字避免超出 Token 限制
        body_excerpt = body[:2000] if len(body) > 2000 else body
        rel_path = getattr(ctx, 'rel_path', '') or getattr(ctx, 'title', '')
        current_hash = getattr(ctx, 'current_hash', None) or hashlib.md5(body_excerpt.encode('utf-8')).hexdigest()
        engine_meta = getattr(getattr(ctx, 'engine', None), 'meta', None)

        # 🚀 [V101.0] 增量缓存：基于原稿内容 Hash 检查母语 AI 算法对齐 SEO 缓存
        if engine_meta and rel_path and current_hash and not getattr(ctx, 'clear_cache', False):
            doc_info = engine_meta.get_doc_info(rel_path) or {}
            cached_seo = doc_info.get("ai_seo_alignment")
            if isinstance(cached_seo, dict) and cached_seo.get("hash") == current_hash and cached_seo.get("data"):
                tlog.info(f"✨ [AI 算法对齐] 命中本地 SEO 缓存，跳过大模型投喂 ({ctx.title})")
                return self._respect_frontmatter(ctx.fm_dict, cached_seo.get("data", {}))
            existing_seo = doc_info.get("seo_data")
            if (isinstance(existing_seo, dict) and (existing_seo.get("description") or existing_seo.get("keywords"))
                    and doc_info.get("source_hash") == current_hash):
                tlog.info(f"✨ [AI 算法对齐] 命中账本已有 SEO 资产，跳过大模型投喂 ({ctx.title})")
                return self._respect_frontmatter(ctx.fm_dict, existing_seo)

        tlog.info(f"🛰️ [AI 算法对齐] 正在为 '{ctx.title}' 执行智能 SEO 投喂...")

        translator = getattr(ctx.engine, 'translator', None)
        if not translator:
            tlog.warning("⚠️ [AI 算法对齐] AI 引擎未就绪，回退至启发式处理")
            from .heuristic import HeuristicSeoProcessor
            return HeuristicSeoProcessor().process(ctx)
        
        source_lang = getattr(ctx, 'source_lang', 'zh')
        from core.utils.language_hub import LanguageHub
        lang_name = LanguageHub.resolve_to_name(source_lang)

        seo_result = {}

        try:
            # 构建 AI 请求
            from core.adapters.ai.payload_manager import PayloadManager
            
            # 🚀 动态加载方言与风格提示词
            style = None
            if hasattr(ctx, "route_source") and ctx.route_source:
                from core.governance.license_guard import LicenseGuard
                if LicenseGuard.is_pro_feature_allowed("multi_dialect"):
                    for item in ctx.engine.config.route_matrix:
                        if getattr(item, 'source', None) == ctx.route_source:
                            style = getattr(item, 'style', None)
                            break
            
            resolved_style = style or getattr(translator.trans_cfg, 'active_style', 'default')
            p = translator.trans_cfg.prompts
            if resolved_style:
                from core.logic.ai.ai_factory import TranslatorFactory
                imprint_id = getattr(translator, 'imprint_id', 'default') or 'default'
                p = TranslatorFactory.get_prompts_for_style(resolved_style, imprint_id, p)
                
            system_prompt = PayloadManager.format_prompt(p.seo_system, lang_name=lang_name)
            user_content = PayloadManager.format_prompt(p.seo_user, title=ctx.title, text=body_excerpt, lang_name=lang_name)
            payload = PayloadManager.prepare_payload(
                translator, system_prompt, user_content, is_json=True
            )
            if "params" not in payload:
                payload["params"] = {}
            payload["params"]["max_tokens"] = 512

            # 调用 AI
            raw_response = translator.ask_ai_with_retry(payload)
            if hasattr(raw_response, 'text'): raw_response = getattr(raw_response, 'text')
            elif hasattr(raw_response, 'content'): raw_response = getattr(raw_response, 'content')
            if not isinstance(raw_response, (str, bytes, bytearray)):
                raw_response = '{"seo_title": "", "description": "", "keywords": []}'

            repaired = AILogicHub.repair_json(raw_response)
            data = json.loads(repaired) if isinstance(repaired, str) else {}

            # 提取结果
            if data.get('seo_title'):
                seo_result['og_title'] = data['seo_title'][:self.MAX_TITLE_LENGTH]
            if data.get('description'):
                seo_result['description'] = data['description'][:self.MAX_DESCRIPTION_LENGTH]
            if data.get('keywords'):
                kw = data['keywords']
                if isinstance(kw, str):
                    kw = [k.strip() for k in kw.split(',') if k.strip()]
                seo_result['keywords'] = kw[:self.MAX_KEYWORDS_COUNT]
            if data.get('og_title'):
                seo_result['og_title'] = data['og_title'][:self.MAX_TITLE_LENGTH]

            tlog.info(f"✅ [AI 算法对齐] 投喂完成，生成字段: {list(seo_result.keys())}")

        except Exception as e:
            tlog.warning(f"⚠️ [AI 算法对齐] AI 处理异常: {e}，回退至启发式")
            from .heuristic import HeuristicSeoProcessor
            return HeuristicSeoProcessor().process(ctx)

        # 🚀 [V101.0] 持久化缓存：将新生成的 SEO 投喂数据记录至账本
        if engine_meta and rel_path and current_hash and seo_result:
            try:
                doc_info = engine_meta.get_doc_info(rel_path) or {}
                engine_meta.sqlite.upsert_document(rel_path, {**doc_info, "ai_seo_alignment": {"hash": current_hash, "data": seo_result}})
            except Exception as e:
                tlog.debug(f"⚠️ [AI 算法对齐] 写入 SEO 缓存失败: {e}")

        # 应用元数据优先原则
        seo_result = self._respect_frontmatter(ctx.fm_dict, seo_result)
        return seo_result
