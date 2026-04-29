#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Service - Preflight (预检服务)
模块职责：负责启动前的环境嗅探、源语种自动探测与全量可用性检查。
🛡️ [AEL-Iter-v1.0]：主权预检自动化核心。
"""
import os
from core.utils.tracing import tlog
from core.utils.language_hub import LanguageHub

class PreflightService:
    @staticmethod
    def auto_detect_language(engine) -> str:
        """🚀 [V15.8] 自动探测源语种 (Source Auto-Discovery)"""
        i18n = engine.config.i18n_settings
        if i18n.source.lang_code and i18n.source.lang_code != "auto":
            return i18n.source.lang_code

        first_doc = next(iter(engine.md_index.keys()), None)
        if not first_doc:
            return "zh" # 默认回退

        abs_path = os.path.join(engine.paths['vault'], first_doc)
        try:
            # 🚀 [V15.8] 使用政策定义的超时与长度
            with open(abs_path, 'r', encoding='utf-8') as f:
                text = f.read(2000)
                detected = LanguageHub.detect_source_lang(text, engine.translator)
                tlog.info(f"🔍 [Preflight] 自动探测源语种为: {detected}")
                return detected
        except Exception as e:
            tlog.warning(f"⚠️ [Preflight] 语种探测故障: {e}")
            return "zh"
            
    @staticmethod
    def perform_checks(engine):
        """执行全量预检任务"""
        # 1. 自动驾驶：静默修复已知物理与逻辑故障
        from core.governance.autopilot import Autopilot
        Autopilot.perform_safe_surgery(engine)

        # 2. 语种探测
        engine.config.i18n_settings.source.lang_code = PreflightService.auto_detect_language(engine)
