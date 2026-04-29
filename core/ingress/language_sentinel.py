#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Ingress - Language Sentinel
职责：原稿语种自动探测与主权语种锁执行。
🛡️ [V35.0]：智能语种识别网关。
"""

import re
from typing import Optional
from core.utils.tracing import tlog
from core.governance.license_guard import LicenseGuard

class LanguageSentinel:
    """🚀 [V35.0] 语种哨兵：负责识别、验证并执行语种主权拦截"""
    
    @staticmethod
    def detect_language(content: str, filename: str = "") -> str:
        """🚀 [V35.1] 混合探测引擎：Frontmatter -> 内容特征 -> 文件名启发"""
        # 1. 优先检查 Frontmatter
        fm_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if fm_match:
            lang_match = re.search(r'lang:\s*(\w+)', fm_match.group(1))
            if lang_match:
                return lang_match.group(1).lower()

        # 2. 内容特征探测 (简单启发式)
        # 统计中文字符比例
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content[:2000]))
        if chinese_chars > 5: # 降低阈值以支持短篇稿件
            return "zh"

            
        # 3. 默认回退
        return "en"

    @staticmethod
    def is_language_allowed(lang: str, current_target_lang: str) -> bool:
        """🚀 [V35.1] 语种锁拦截逻辑"""
        # 授权版用户允许所有语种矩阵
        if LicenseGuard.is_pro_feature_allowed("multi_language"):
            return True
            
        # 免费版用户：源语种不能与目标语种冲突，且目标语种只能有一种
        # 这里执行“单线程主权”逻辑
        if lang == current_target_lang:
            tlog.warning(f"⚠️ [语种拦截] 原稿语种 '{lang}' 与目标语种冲突，已被过滤。")
            return False
            
        return True

    @staticmethod
    def clear_shadow_cache_on_switch(territory_path: str):
        """当免费版切换语种时，物理清除影子库旧数据"""
        import os
        import shutil
        from core.runtime.engine_factory import EngineFactory
        cache_dir = os.path.join(territory_path, EngineFactory.SOVEREIGN_LAYOUT["cache"])
        if os.path.exists(cache_dir):
            tlog.info("🧹 [主权同步] 检测到语种切换，正在物理清空旧语种影子库...")
            shutil.rmtree(cache_dir)
            os.makedirs(cache_dir)

