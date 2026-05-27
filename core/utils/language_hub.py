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
        # --- 特殊标志 ---
        "auto": "auto",

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
        "mr": "mr", "marathi": "mr", "te": "te", "telugu": "te", "kn": "kn", "kannada": "kn",
        "gu": "gu", "gujarati": "gu", "ml": "ml", "malayalam": "ml", "sd": "sd", "sindhi": "sd",

        # --- 非洲及其他 ---
        "ha": "ha", "hausa": "ha", "sw": "sw", "swahili": "sw", "斯瓦希里语": "sw",
        "yo": "yo", "yoruba": "yo", "ig": "ig", "igbo": "ig", "am": "am", "amharic": "am",
        "om": "om", "oromo": "om", "uz": "uz", "uzbek": "uz", "az": "az", "azerbaijani": "az",
        "tl": "tl", "tagalog": "tl", "jv": "jv", "javanese": "jv", "su": "su", "sundanese": "su",
        "my": "my", "burmese": "my", "ps": "ps", "pashto": "ps",
        "la": "la", "latin": "la", "拉丁语": "la", "af": "af", "afrikaans": "af",
    }

    # 🚀 [V55.4] 官方支持的语种矩阵 (前 50 大语种，带元数据与图标)
    SUPPORTED_MATRIX = [
        {"code": "zh", "name": "简体中文", "icon": "🇨🇳"},
        {"code": "en", "name": "English", "icon": "🇬🇧"},
        {"code": "hi", "name": "हिन्दी", "icon": "🇮🇳"},
        {"code": "es", "name": "Español", "icon": "🇪🇸"},
        {"code": "fr", "name": "Français", "icon": "🇫🇷"},
        {"code": "ar", "name": "العربية", "icon": "🇸🇦"},
        {"code": "bn", "name": "বাংলা", "icon": "🇧🇩"},
        {"code": "pt", "name": "Português", "icon": "🇵🇹"},
        {"code": "ru", "name": "Русский", "icon": "🇷🇺"},
        {"code": "ur", "name": "اردو", "icon": "🇵🇰"},
        {"code": "id", "name": "Bahasa Indonesia", "icon": "🇮🇩"},
        {"code": "de", "name": "Deutsch", "icon": "🇩🇪"},
        {"code": "ja", "name": "日本語", "icon": "🇯🇵"},
        {"code": "mr", "name": "मराठी", "icon": "🇮🇳"},
        {"code": "te", "name": "తెలుగు", "icon": "🇮🇳"},
        {"code": "tr", "name": "Türkçe", "icon": "🇹🇷"},
        {"code": "ta", "name": "தமிழ்", "icon": "🇮🇳"},
        {"code": "vi", "name": "Tiếng Việt", "icon": "🇻🇳"},
        {"code": "tl", "name": "Tagalog", "icon": "🇵🇭"},
        {"code": "ko", "name": "한국어", "icon": "🇰🇷"},
        {"code": "fa", "name": "فارسی", "icon": "🇮🇷"},
        {"code": "ha", "name": "Hausa", "icon": "🇳🇬"},
        {"code": "sw", "name": "Kiswahili", "icon": "🇰🇪"},
        {"code": "jv", "name": "Javanese", "icon": "🇮🇩"},
        {"code": "it", "name": "Italiano", "icon": "🇮🇹"},
        {"code": "pa", "name": "ਪੰਜਾਬੀ", "icon": "🇵🇰"},
        {"code": "kn", "name": "ಕನ್ನಡ", "icon": "🇮🇳"},
        {"code": "gu", "name": "ગુજરાતી", "icon": "🇮🇳"},
        {"code": "th", "name": "ไทย", "icon": "🇹🇭"},
        {"code": "am", "name": "አማርኛ", "icon": "🇪🇹"},
        {"code": "yo", "name": "Yorùbá", "icon": "🇳🇬"},
        {"code": "my", "name": "မြန်မာဘာသာ", "icon": "🇲🇲"},
        {"code": "om", "name": "Oromoo", "icon": "🇪🇹"},
        {"code": "ps", "name": "پښتو", "icon": "🇦🇫"},
        {"code": "uk", "name": "Українська", "icon": "🇺🇦"},
        {"code": "su", "name": "Basa Sunda", "icon": "🇮🇩"},
        {"code": "pl", "name": "Polski", "icon": "🇵🇱"},
        {"code": "uz", "name": "Oʻzbekcha", "icon": "🇺🇿"},
        {"code": "ro", "name": "Română", "icon": "🇷🇴"},
        {"code": "az", "name": "Azərbaycanca", "icon": "🇦🇿"},
        {"code": "ml", "name": "മലയാളം", "icon": "🇮🇳"},
        {"code": "sd", "name": "سنڌي", "icon": "🇵🇰"},
        {"code": "ig", "name": "Igbo", "icon": "🇳🇬"},
        {"code": "hu", "name": "Magyar", "icon": "🇭🇺"},
        {"code": "el", "name": "Ελληνικά", "icon": "🇬🇷"},
        {"code": "cs", "name": "Čeština", "icon": "🇨🇿"},
        {"code": "nl", "name": "Nederlands", "icon": "🇳🇱"},
        {"code": "sv", "name": "Svenska", "icon": "🇸🇪"},
        {"code": "fi", "name": "Suomi", "icon": "🇫🇮"},
        {"code": "no", "name": "Norsk", "icon": "🇳🇴"}
    ]

    @classmethod
    def get_supported_matrix(cls):
        """获取系统当前支持的语种大盘"""
        return cls.SUPPORTED_MATRIX

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
            "ru": "Russian",
            "hi": "Hindi",
            "ar": "Arabic",
            "bn": "Bengali",
            "pt": "Portuguese",
            "ur": "Urdu",
            "id": "Indonesian",
            "tr": "Turkish",
            "vi": "Vietnamese",
            "th": "Thai",
            "pl": "Polish",
            "uk": "Ukrainian",
            "nl": "Dutch",
            "sv": "Swedish",
            "no": "Norwegian",
            "fi": "Finnish",
            "el": "Greek",
            "cs": "Czech",
            "hu": "Hungarian",
            "mr": "Marathi",
            "te": "Telugu",
            "ta": "Tamil",
            "tl": "Tagalog",
            "fa": "Persian",
            "ha": "Hausa",
            "sw": "Swahili",
            "jv": "Javanese",
            "pa": "Punjabi",
            "kn": "Kannada",
            "gu": "Gujarati",
            "am": "Amharic",
            "yo": "Yoruba",
            "my": "Burmese",
            "om": "Oromo",
            "ps": "Pashto",
            "su": "Sundanese",
            "uz": "Uzbek",
            "ro": "Romanian",
            "az": "Azerbaijani",
            "ml": "Malayalam",
            "sd": "Sindhi",
            "ig": "Igbo"
        }
        code = iso_code.lower().strip()
        # 模糊匹配
        if code == "auto": return "Auto Detect"
        if "zh-hans" in code or code == "zh-cn" or code == "zh": return "Chinese (Simplified)"
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
    def get_physical_path(iso_code: str, theme: str = "generic", source_lang: str = "zh", force_prefix: bool = False) -> str:
        """🚀 [V57.0] 动态主权路径适配：支持原稿路径的灵活挂载"""
        if not iso_code: return ""
        theme = theme.lower() if theme else "generic"
        
        # 🛡️ [Sovereignty Logic]
        # 如果是原稿语种，且未开启强制前缀，则返回空前缀（即挂载在 SSG 根目录）
        # 目前主要针对 Starlight 和 Docusaurus 等有 root locale 概念的框架
        if iso_code.lower() == source_lang.lower() and not force_prefix:
            if theme in ["starlight", "docusaurus"]:
                return ""
            
        return iso_code.lower()
