#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Utility Module (SAAS Infrastructure)
模块职责：提供全局无状态的工具支持，包含日志管线引擎与基础文本清洗器。
架构升级：注入 ANSI Color 矩阵，实现故障等级的视觉降维。
"""

import os
import re
import yaml
import logging
from logging.handlers import RotatingFileHandler

class ColoredFormatter(logging.Formatter):
    """
    🚀 视觉降维：自定义 ANSI 彩色日志格式化器
    针对不同严重等级，在终端输出时注入特定的颜色代码。
    """
    # ANSI 颜色转义序列
    GREY = "\033[90m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD_RED = "\033[1;91m"
    RESET = "\033[0m"

    FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"

    LEVEL_MAP = {
        logging.DEBUG: GREY,
        logging.INFO: GREEN,       # 🟢 同步成功/正常流程
        logging.WARNING: YELLOW,   # 🟡 AI 降级/图片跳过
        logging.ERROR: BOLD_RED,   # 🔴 关键故障/写盘失败
        logging.CRITICAL: BOLD_RED
    }

    def format(self, record):
        log_fmt = self.LEVEL_MAP.get(record.levelno, self.RESET) + self.FORMAT + self.RESET
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)

def setup_logger():
    """
    初始化工业级守护进程日志。
    支持控制台彩色显示与文件滚动备份。
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger("Illacme.plenipes")
    
    if logger.hasHandlers():
        logger.handlers.clear()
        
    # 1. 基础格式（用于文件，不带颜色代码以防乱码）
    file_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S')
    
    # 2. 彩色格式（用于终端控制台）
    console_formatter = ColoredFormatter()
    
    # 文件日志：最大 5MB，保留 3 个滚动备份
    fh = RotatingFileHandler(os.path.join(log_dir, 'plenipes.log'), maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
    fh.setFormatter(file_formatter)
    
    # 控制台标准输出日志 (Stdout)
    ch = logging.StreamHandler()
    ch.setFormatter(console_formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

def normalize_keywords(kw_data):
    """
    数据降维清洗器：支持中英文逗号、分号的智能识别与格式化。
    """
    if not kw_data:
        return ""
    
    if isinstance(kw_data, list):
        clean_list = [str(k).strip() for k in kw_data if str(k).strip()]
        return ", ".join(clean_list)
        
    elif isinstance(kw_data, str):
        # 🚀 兼容性：自动识别各种常见的关键词分隔符
        clean_list = [k.strip() for k in re.split(r'[,，;；]', kw_data) if k.strip()]
        return ", ".join(clean_list)
        
    return str(kw_data).strip()

def extract_frontmatter(content):
    """
    安全剥离器：将 YAML 属性区与 Markdown 正文分离。
    """
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1)) or {}, content[match.end():]
        except yaml.YAMLError as e:
            logger = logging.getLogger("Illacme.plenipes")
            # 🚀 语义降维：提供直观的排查方向
            logger.error(f"⚠️ 格式解析异常: 文章顶部的属性区（YAML）存在语法错误。💡 建议: 请检查是否缺少横线分隔符、缩进不规范，或冒号后缺少空格。底层报错: {e}")
            pass
    return {}, content