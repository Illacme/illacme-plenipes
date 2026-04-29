#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Language Hub (全球语种智库)
模块职责：实现全球语种识别、ISO 归一化及主题感知的路径对齐。
🛡️ [AEL-Iter-v7.6.5]：实现“全量语种矩阵”与“AI 联觉识别”。
"""

import logging
import re

from core.utils.tracing import tlog

class LanguageHub:
    """🚀 [V7.6.5] 全球语种智库：支持 100+ 语种的自动对齐与 AI 联觉识别"""

    # 🌍 全量语种矩阵 (ISO 639-1)
    # 涵盖全球主要国家、地区及方言的自然语言映射
    ISO_KNOWLEDGE_BASE = {
        # --- 中文系 ---
        "zh": "zh", "zh-cn": "zh", "简体中文": "zh", "chinese": "zh",
        "zh-hans": "zh", "traditional chinese": "zh-Hant", "繁体中文": "zh-Hant",
        "zh-tw": "zh-Hant", "zh-hk": "zh-Hant", "zh-hant": "zh-Hant", "粤语": "zh", # 暂时归类

        # --- 英语系 ---
        "en": "en", "english": "en", "英语": "en", "en-us": "en", "en-gb": "en", "en-au": "en",

        # --- 欧洲语系 ---
        "fr": "fr", "french": "fr", "法语": "fr", "de": "de", "german": "de", "德语": "de",
        "es": "es", "spanish": "es", "西班牙语": "es", "it": "it", "italian": "it", "意大利语": "it",
        "ru": "ru", "russian": "ru", "俄语": "ru", "pt": "pt", "portuguese": "pt", "葡萄牙语": "pt",
        "nl": "nl", "dutch": "nl", "荷兰语": "nl", "pl": "pl", "polish": "pl", "波兰语": "pl",
        "sv": "sv", "swedish": "sv", "瑞典语": "sv", "da": "da", "danish": "da", "丹麦语": "da",
        "fi": "fi", "finnish": "fi", "芬兰语": "fi", "no": "no", "norwegian": "no", "挪威语": "no",
        "el": "el", "greek": "el", "希腊语": "el", "tr": "tr", "turkish": "tr", "土耳其语": "tr",
        "cs": "cs", "czech": "cs", "捷克语": "cs", "hu": "hu", "hungarian": "hu", "匈牙利语": "hu",
        "ro": "ro", "romanian": "ro", "罗马尼亚语": "ro", "uk": "uk", "ukrainian": "uk", "乌克兰语": "uk",

        # --- 亚洲语系 ---
        "ja": "ja", "japanese": "ja", "日本語": "ja", "日语": "ja", "日文": "ja",
        "ko": "ko", "korean": "ko", "한국어": "ko", "韩语": "ko", "韩文": "ko",
        "th": "th", "thai": "th", "泰语": "th", "vi": "vi", "vietnamese": "vi", "越南语": "vi",
        "id": "id", "indonesian": "id", "印尼语": "id", "ms": "ms", "malay": "ms", "马来语": "ms",
        "hi": "hi", "hindi": "hi", "印地语": "hi", "bn": "bn", "bengali": "bn", "孟加拉语": "bn",
        "pa": "pa", "punjabi": "pa", "旁遮普语": "pa", "ta": "ta", "tamil": "ta", "泰米尔语": "ta",
        "ar": "ar", "arabic": "ar", "阿拉伯语": "ar", "he": "he", "hebrew": "he", "希伯来语": "he",
        "fa": "fa", "persian": "fa", "波斯语": "fa", "ur": "ur", "urdu": "ur", "乌尔都语": "ur",

        # --- 其他及方言 ---
        "la": "la", "latin": "la", "拉丁语": "la", "af": "af", "afrikaans": "af",
        "sw": "sw", "swahili": "sw", "斯瓦希里语": "sw",
    }

    @staticmethod
    def resolve_to_name(iso_code: str) -> str:
        """🚀 反向解析：ISO -> 友好名称"""
        if not iso_code: return "English"

        # 建立反向索引
        reverse_map = {
            "zh": "Chinese (Simplified)",
            "zh-Hant": "Chinese (Traditional)",
            "en": "English",
            "ja": "Japanese",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
            "it": "Italian",
            "ko": "Korean",
            "ru": "Russian"
        }
        code = iso_code.lower().strip()
        # 模糊匹配
        if "zh-hans" in code or code == "zh-cn": return "Chinese (Simplified)"
        if "zh-hant" in code or code == "zh-tw": return "Chinese (Traditional)"
        if "en" in code: return "English"

        return reverse_map.get(iso_code, iso_code)

    @staticmethod
    def resolve_to_iso(name: str, ai_client=None) -> str:
        """
        🚀 终极解析逻辑：本地库 -> 启发式 -> AI 联觉
        """
        if not name: return "en"
        raw = name.lower().strip()

        # 1. 本地库精准匹配
        if raw in LanguageHub.ISO_KNOWLEDGE_BASE:
            return LanguageHub.ISO_KNOWLEDGE_BASE[raw]

        # 2. 启发式正则推导
        if "zh" in raw: return "zh-Hant" if any(x in raw for x in ["tw", "hk", "traditional"]) else "zh-Hans"
        if "en" in raw: return "en"
        if "jp" in raw or "ja" in raw: return "ja"

        # 3. [V7.6.5] AI 联觉识别降级逻辑
        if ai_client:
            try:
                return LanguageHub._resolve_via_ai(name, ai_client)
            except Exception as e:
                tlog.error(f"❌ [LanguageHub] AI 语种识别失败: {e}")

        tlog.warning(f"⚠️ [LanguageHub] 未能识别语种 '{name}'，将执行透传。")
        return name

    @staticmethod
    def detect_source_lang(text: str, ai_client=None) -> str:
        """
        🚀 智感源语种探测：支持开关感知的自动降级
        """
        if not text: return "zh-Hans"

        # 1. 简单统计学探测 (极快，无需 AI)
        zh_count = len(re.findall(r'[\u4e00-\u9fff]', text))
        en_count = len(re.findall(r'[a-zA-Z]', text))

        if zh_count > 10 and zh_count > en_count * 0.5: return "zh-Hans"
        if en_count > 50 and en_count > zh_count * 5: return "en"

        # 2. [V10.0] AI 深度探测开关检查
        if ai_client:
            # 🚀 [V10.0] 检查全局 AI 推理开关
            is_enabled = getattr(ai_client.trans_cfg, 'enable_ai', True)
            if is_enabled:
                try:
                    return LanguageHub._resolve_via_ai(text[:500], ai_client, is_detection=True)
                except Exception:
                    pass
            else:
                tlog.debug("⏭️ [AI 语种探测跳过] 根据全局开关执行本地兜底。")

        return "zh-Hans" # 默认兜底

    @staticmethod
    def _resolve_via_ai(input_str: str, ai_client, is_detection=False) -> str:
        """调用 AI 接口进行语种识别"""
        system_prompt = (
            "You are a language expert. Identify the ISO 639-1 code for the given input. "
            "Return ONLY the code (e.g., 'en', 'zh-Hans', 'fr'). No explanations."
        )
        if is_detection:
            user_prompt = f"Detect the language of this text:\n\n{input_str}"
        else:
            user_prompt = f"What is the ISO 639-1 code for language name: '{input_str}'?"

        # 这里的 ai_client 应该是适配了项目的 Translator 接口
        res = ai_client.raw_inference(user_prompt, system_prompt)
        if not res: return "en"

        clean_res = res.strip().lower()
        # 简单清洗
        if "zh-hans" in clean_res: return "zh-Hans"
        if "zh-hant" in clean_res: return "zh-Hant"
        return clean_res

    @staticmethod
    def get_physical_path(iso_code: str, theme: str = "generic") -> str:
        """主题感知的物理路径适配"""
        if not iso_code: return "en"
        theme = theme.lower() if theme else "generic"
        return iso_code.lower()
