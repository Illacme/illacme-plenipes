# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Utility Module
模块职责：提供全局无状态的工具支持。
🛡️ [V24.6 Refactored]：解耦后的轻量化工具基座。
"""
import os
import re
import yaml
import logging
from logging.handlers import RotatingFileHandler

# 🚀 [V24.6] 导入外挂的工具模块
from .text import TokenCounter, sanitize_ai_response, strip_technical_noise
from .io import atomic_write

class ColoredFormatter(logging.Formatter):
    """视觉分级：自定义 ANSI 彩色日志格式化器"""
    GREY, GREEN, YELLOW, RED = "\033[90m", "\033[92m", "\033[93m", "\033[91m"
    RESET = "\033[0m"
    FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
    LEVEL_MAP = {
        logging.DEBUG: GREY, logging.INFO: GREEN,
        logging.WARNING: YELLOW, logging.ERROR: RED, logging.CRITICAL: RED
    }

    def format(self, record):
        log_fmt = self.LEVEL_MAP.get(record.levelno, self.RESET) + self.FORMAT + self.RESET
        return logging.Formatter(log_fmt, datefmt='%H:%M:%S').format(record)

def setup_logger(log_dir="logs"):
    """初始化工业级日志管线 (支持主权路径重定向)"""
    os.makedirs(log_dir, exist_ok=True)
    from core.utils.tracing import tlog
    if tlog.hasHandlers(): tlog.handlers.clear()
    
    log_file = os.path.join(log_dir, 'plenipes.log')
    fh = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
    fh.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
    tlog.addHandler(fh)
    return tlog

def extract_frontmatter(content):
    """安全隔离器：物理分离 YAML 属性与正文"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        try: return yaml.safe_load(match.group(1)) or {}, content[match.end():]
        except Exception: pass
    return {}, content

def normalize_keywords(kw_data):
    """数据降维清洗器：标准化标签矩阵"""
    if not kw_data: return []
    if isinstance(kw_data, list): return [str(k).strip() for k in kw_data if str(k).strip()]
    if isinstance(kw_data, str): return [k.strip() for k in re.split(r'[,，;；]', kw_data) if k.strip()]
    return [str(kw_data).strip()] if str(kw_data).strip() else []
