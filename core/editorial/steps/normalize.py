# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Pipeline Steps Shard
工序职责：ReadAndNormalizeStep (物理读取与归一化)
🛡️ [AEL-Iter-v5.3]：基于分层架构的 TDR 复健版本。
"""

import re
from core.utils import extract_frontmatter
from core.utils.tracing import tlog
from core.editorial.runner import PipelineStep
from core.utils.language_hub import LanguageHub

class ReadAndNormalizeStep(PipelineStep):
    """阶段 3-4: 物理读取与编辑器方言抹平"""
    PLUGIN_ID = "read_normalize"
    DISPLAY_NAME = "物理读取与归一化"
    VERSION = "V5.3"
    DESCRIPTION = "从金库读取原始稿件，并执行方言识别与 Frontmatter 归一化。"

    def process(self, ctx):
        try:
            with open(ctx.src_path, 'r', encoding='utf-8') as f:
                ctx.raw_content = f.read()
        except Exception as e:
            tlog.error(f"🛑 读取失败 {ctx.src_path}: {e}")
            ctx.is_aborted = True
            return

        fm_dict, raw_body = extract_frontmatter(ctx.raw_content)
        ctx.raw_body, ctx.fm_dict = ctx.engine.input_adapter.normalize(raw_body, fm_dict)

        # 🚀 [V15.9] 标题主权对齐：Frontmatter 显式定义优先于物理文件名
        if ctx.fm_dict.get('title'):
            ctx.title = ctx.fm_dict.get('title')

        raw_ai_sync = ctx.fm_dict.get('ai_sync')
        ctx.is_silent_edit = (str(raw_ai_sync).lower() == 'false') if raw_ai_sync is not None else False

        # 🚀 [V105.0] 字数统计逻辑：全球全语种通用度量 (Universal Multilingual Word Count)
        from core.utils.text import calculate_universal_word_count
        ctx.seo_data['word_count'] = calculate_universal_word_count(ctx.raw_body)

        # 🚀 [V7.7] 逐文件语种识别 (Per-Document Granular Detection)
        # [V52.13 优化]：优先级：Frontmatter 显式定义 > 动态识别 (if auto) > 全局配置
        explicit_lang = ctx.fm_dict.get('lang') or ctx.fm_dict.get('language')
        config_src = ctx.engine.i18n.source.lang_code
        
        if explicit_lang:
            ctx.source_lang = explicit_lang
        elif config_src == "auto" or not config_src:
            ctx.source_lang = LanguageHub.detect_source_lang(ctx.raw_content, ctx.services.translator)
        else:
            ctx.source_lang = config_src
