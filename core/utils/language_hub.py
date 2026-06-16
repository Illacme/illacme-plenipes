#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Language Hub (全球语种智库)
模块职责：实现全球语种识别、ISO 归一化及主题感知的路径对齐。
🛡️ [AEL-Iter-v10.2]：引入噪声过滤与标题中文优先启发式，并解决 300 行红线物理规避。
"""

import logging
import re

from core.utils.tracing import tlog
from core.utils.language_data import SUPPORTED_MATRIX, REVERSE_MAP

class LanguageHub:
    """🚀 [V10.2] 全球语种智库：支持 100+ 语种的自动对齐与 AI 联觉识别"""

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

    # 🚀 [V55.4] 官方支持的语种矩阵 (从 language_data 动态挂载)
    SUPPORTED_MATRIX = SUPPORTED_MATRIX

    @classmethod
    def get_supported_matrix(cls):
        """获取系统当前支持的语种大盘"""
        return cls.SUPPORTED_MATRIX

    @classmethod
    def resolve_to_native_name(cls, iso_code: str) -> str:
        """🚀 获取 ISO -> 官方本地化/友好名称"""
        if not iso_code: return "English"
        code = iso_code.lower().strip()
        for item in cls.SUPPORTED_MATRIX:
            if item["code"] == code:
                return item["name"]
        return cls.resolve_to_name(iso_code)

    @staticmethod
    def resolve_to_name(iso_code: str) -> str:
        """🚀 反向解析：ISO -> 友好名称"""
        if not iso_code: return "English"

        code = iso_code.lower().strip()
        # 模糊匹配
        if code == "auto": return "Auto Detect"
        if "zh-hans" in code or code == "zh-cn" or code == "zh": return "Chinese (Simplified)"
        if "zh-hant" in code or code == "zh-tw": return "Chinese (Traditional)"
        if "en" in code: return "English"

        return REVERSE_MAP.get(iso_code, iso_code)

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
    def _clean_noise(text: str) -> str:
        """
        🚀 清洗 Markdown / HTML 噪声：物理移除代码块、超链接及 html 标签
        """
        if not text: return ""
        # 1. 移除多行及行内代码块
        t = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        t = re.sub(r'`[^`\n]+`', '', t)
        # 2. 移除 Markdown 链接与图片以及 Obsidian 双链
        t = re.sub(r'!\[.*?\]\(.*?\)', '', t)
        t = re.sub(r'\[.*?\]\(.*?\)', '', t)
        t = re.sub(r'!\[\[.*?\]\]', '', t)
        t = re.sub(r'\[\[.*?\]\]', '', t)
        # 3. 移除纯 URL 链接
        t = re.sub(r'https?://\S+', '', t)
        # 4. 移除 HTML 标签
        t = re.sub(r'<[^>]+>', '', t)
        return t

    @staticmethod
    def detect_source_lang(text: str, ai_client=None) -> str:
        """
        🚀 智感源语种探测：支持开关感知的自动降级与噪音排除、标题优先机制
        """
        if not text: return "zh-Hans"

        # 1. 优先提取标题进行强中文字符判别
        title = ""
        fm_match = re.search(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
        if fm_match:
            title_match = re.search(r'title:\s*([^\n]+)', fm_match.group(1))
            if title_match:
                title = title_match.group(1).strip()
        if not title:
            h1_match = re.search(r'^#\s+([^\n]+)', text, re.MULTILINE)
            if h1_match:
                title = h1_match.group(1).strip()

        if title:
            title_zh = len(re.findall(r'[\u4e00-\u9fff]', title))
            title_en = len(re.findall(r'[a-zA-Z]', title))
            # 只要标题包含 2 个以上汉字，且汉字占比偏高，则强优先判定为中文
            if title_zh > 1 and (title_zh > title_en * 0.5 or title_en == 0):
                return "zh-Hans"

        # 2. 排除代码块与超级链接等无语义英文语法噪声
        clean_text = LanguageHub._clean_noise(text)

        # 3. 简单统计学探测 (极快，无需 AI)
        zh_count = len(re.findall(r'[\u4e00-\u9fff]', clean_text))
        en_count = len(re.findall(r'[a-zA-Z]', clean_text))

        if zh_count > 10 and zh_count > en_count * 0.5: return "zh-Hans"
        if en_count > 50 and en_count > zh_count * 5: return "en"

        # 4. [V10.0] AI 深度探测开关检查
        if ai_client:
            # 🚀 [V10.0] 检查全局 AI 推理开关
            is_enabled = getattr(ai_client.trans_cfg, 'enable_ai', True)
            if is_enabled:
                try:
                    return LanguageHub._resolve_via_ai(clean_text[:500], ai_client, is_detection=True)
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

        res = ai_client.raw_inference(user_prompt, system_prompt)
        if not res: return "en"

        clean_res = res.strip().lower()
        if "zh-hans" in clean_res: return "zh-Hans"
        if "zh-hant" in clean_res: return "zh-Hant"
        return clean_res

    @staticmethod
    def get_physical_path(iso_code: str, theme: str = "generic", source_lang: str = "zh", force_prefix: bool = False) -> str:
        """🚀 [V57.0] 动态主权路径适配：支持原稿路径的灵活挂载"""
        if not iso_code: return ""
        theme = theme.lower() if theme else "generic"

        if iso_code.lower() == source_lang.lower() and not force_prefix:
            if theme in ["starlight", "docusaurus"]:
                return ""

        return iso_code.lower()
