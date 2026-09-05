# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Scheduler Shards - Metadata & SEO Polish Pipeline
职责：SEO 纯净数据注入、大模型标题润色、描述提炼与元数据多语言润色管线
🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
"""
import re
from typing import Dict, Any, List, Optional
from core.utils.tracing import tlog
from core.logic.ai.ai_logic_hub import AILogicHub


class DispatchMetaPolish:
    @staticmethod
    def extract_seo_data(seo_data: Optional[Dict[str, Any]], code: str) -> Dict[str, Any]:
        """
        🚀 优先使用新出版模式（global 模式）预先生成的译文 SEO 数据
        包含思维链脱毒与防污染墙。
        """
        t_seo_data = {}
        if seo_data and "i18n_seo" in seo_data and isinstance(seo_data["i18n_seo"], dict):
            lang_seo = seo_data["i18n_seo"].get(code)
            if lang_seo and isinstance(lang_seo, dict):
                desc_candidate = lang_seo.get("description", "") or ""
                # 🛡️ [物理防污染墙] 检查预生成描述是否包含上一轮残留的思维链/系统提示词垃圾
                dirty_keywords = ["reasoning process", "final result", "Thinking Process:", "Analyze the Input", "Output ONLY"]
                if any(kw.lower() in desc_candidate.lower() for kw in dirty_keywords):
                    tlog.warning(f"⚠️ [SEO 防污染] 发现预生成的 {code} 语种 SEO 描述包含历史思维链垃圾，已强行剥离纯净化。")
                    desc_candidate = ""

                if desc_candidate or lang_seo.get("keywords"):
                    t_seo_data = {
                        "description": desc_candidate,
                        "keywords": lang_seo.get("keywords", []),
                        "og_title": lang_seo.get("seo_title", "")
                    }
                    if "search_intent_note" in lang_seo:
                        t_seo_data["search_intent_note"] = lang_seo["search_intent_note"]
                    tlog.info(f"✨ [SEO] 命中新版全局模式预生成的纯净译文 SEO 数据 ({code})")
        return t_seo_data

    @staticmethod
    def polish_metadata(
        engine: Any,
        ctx: Any,
        target_fm: Dict[str, Any],
        t_seo_data: Dict[str, Any],
        code: str,
        name: str,
        is_dry_run: bool,
        style: Optional[str],
        translated_blocks: List[Any],
        active_translator: Any
    ) -> Dict[str, Any]:
        """
        🚀 [V10.5 / V80.0] 元数据与 SEO 润色管线
        涵盖 Title Polish、Description 翻译/提取、Keywords/Tags/Category 批量处理。
        """
        # 🚀 [V10.5] 优先注入：如果 AI SEO 处理器产出了对应语种数据且非强制重译，直接反向覆盖 Frontmatter
        if t_seo_data and not getattr(ctx, 'clear_cache', False):
            if t_seo_data.get("description"):
                target_fm["description"] = t_seo_data["description"]
            if t_seo_data.get("keywords"):
                target_fm["keywords"] = t_seo_data["keywords"]

        if not is_dry_run and not getattr(engine, 'no_ai', False):
            source_title = target_fm.get('title', ctx.title)
            # 🚀 [V80.0] 性能优化：如果全局预生成的 SEO 译文中已经包含了 SEO Title 或者是 og_title，直接使用该结果，跳过大模型标题润色串行调用
            if not getattr(ctx, 'clear_cache', False) and t_seo_data and t_seo_data.get("og_title"):
                target_fm['title'] = t_seo_data["og_title"]
                tlog.info(f"✨ [Title Polish] 命中缓存 SEO 标题，跳过大模型润色 ({code})")
            else:
                tlog.info(f"✍️ [Title Polish] 正在为 {name} 版本润色标题...")
                translated_title = engine.circuit_breakers["ai"].call(
                    active_translator.translate_title,
                    source_title, code, is_dry_run, style=style
                )
                target_fm['title'] = translated_title

            if 'tags' in target_fm:
                # 🚀 [V80.0] 性能优化：若有预生成 SEO 缓存且非重译，说明此篇已在缓存层闭环，不再高频翻译 Tags
                if t_seo_data and not getattr(ctx, 'clear_cache', False):
                    tlog.info(f"✨ [Meta Polish] 命中缓存，跳过 Tags 大模型翻译 ({code})")
                else:
                    tlog.info(f"🏷️ [Meta Polish] 正在为 {name} 版本翻译 Tags...")
                    target_fm['tags'] = engine.circuit_breakers["ai"].call(
                        active_translator.translate_metadata,
                        target_fm['tags'], 'tags', code, is_dry_run, style=style
                    )

            # 🚀 [V10.6] 译文描述 (Description) 兜底补全与智能生成
            # 优先复用预生成 SEO 缓存或已有译文描述，杜绝重复调用大模型
            base_desc = ctx.base_fm.get('description') or ""
            if not getattr(ctx, 'clear_cache', False) and target_fm.get('description') and str(target_fm['description']).strip():
                tlog.info(f"✨ [Meta Polish] 命中缓存 SEO 描述，跳过 Description 大模型翻译 ({code})")
            elif base_desc and base_desc.strip() and base_desc != "无描述":
                tlog.info(f"📝 [Meta Polish] 正在为 {name} 版本翻译 Description...")
                target_fm['description'] = engine.circuit_breakers["ai"].call(
                    active_translator.translate_metadata,
                    base_desc.strip(), 'description', code, is_dry_run, style=style
                )
            else:
                # 🛡️ 物理清空继承自上一语种的残留描述，强制使用当前语种的译文第一段提炼
                target_fm.pop('description', None)
                first_para = ""
                if translated_blocks:
                    for b in translated_blocks:
                        b_str = str(b).strip()
                        if b_str and not b_str.startswith("#") and not b_str.startswith("```"):
                            clean_text = re.sub(r'\[\[.*?\]\]', '', b_str)
                            clean_text = re.sub(r'\[.*?\]\(.*?\)', '', clean_text)
                            clean_text = re.sub(r'__B_MASK_\d+__', '', clean_text).strip()
                            if len(clean_text) >= 5:
                                first_para = clean_text[:150]
                                break
                target_title = target_fm.get('title', source_title)
                if first_para:
                    raw_seed = f"{target_title}: {first_para}"
                else:
                    raw_seed = f"本文围绕「{target_title}」内容展开，提供清晰简明的内容说明。"
                tlog.info(f"✨ [Meta Polish] 源文无 Description，自动为 {name} 版本生成 SEO 描述...")
                gen_desc = engine.circuit_breakers["ai"].call(
                    active_translator.translate_metadata,
                    raw_seed, 'description', code, is_dry_run, style=style
                )
                target_fm['description'] = gen_desc or first_para or target_title

            if target_fm.get('description'):
                target_fm['description'] = AILogicHub.clean_metadata_value(target_fm['description'])

            # 🚀 [V10.5] 翻译兜底：对 Keywords 进行翻译处理（支持列表与单字符串结构）
            if 'keywords' in target_fm and target_fm['keywords'] == ctx.base_fm.get('keywords'):
                tlog.info(f"🔑 [Meta Polish] 正在为 {name} 版本翻译 Keywords...")
                kws = target_fm['keywords']
                if isinstance(kws, list):
                    translated_kws = []
                    for kw in kws:
                        t_kw = engine.circuit_breakers["ai"].call(
                            active_translator.translate_metadata,
                            kw, 'keywords', code, is_dry_run, style=style
                        )
                        if t_kw:
                            translated_kws.append(t_kw)
                    target_fm['keywords'] = translated_kws
                else:
                    target_fm['keywords'] = engine.circuit_breakers["ai"].call(
                        active_translator.translate_metadata,
                        kws, 'keywords', code, is_dry_run, style=style
                    )

            if 'category' in target_fm:
                # 🚀 [V80.0] 性能优化：若有预生成 SEO 缓存，说明此篇已在缓存层闭环，不再高频翻译 Category
                if t_seo_data:
                    tlog.info(f"✨ [Meta Polish] 命中缓存，跳过 Category 大模型翻译 ({code})")
                else:
                    tlog.info(f"📁 [Meta Polish] 正在为 {name} 版本翻译 Category...")
                    target_fm['category'] = engine.circuit_breakers["ai"].call(
                        active_translator.translate_metadata,
                        target_fm['category'], 'category', code, is_dry_run, style=style
                    )

        return target_fm
