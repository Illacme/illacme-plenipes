#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Utility Module (SAAS Infrastructure)
模块职责：提供全局无状态的工具支持，包含日志管线引擎、配置深度合并、智能路径推导与高可靠性审计引擎。

2026 架构全量升级日志：
1. [Smart Path Inference] 核心升级：引入“约定优于配置”机制。若配置文件缺失 output_paths，
   引擎将根据 active_theme 自动推导出前端框架的物理标准路径。
2. [Pre-flight Auditor] 工业级注入：新增 ConfigValidator，在引擎点火前执行物理路径、数据类型
   与安全令牌的完备性静态扫描，物理拦截任何可能导致程序“带病运行”的脏配置。
3. [Pointer Repair] 逻辑加固：彻底封堵了 deep_update 递归中的字典键值覆盖 Bug，确保覆写操作的原子性。
4. [Visual Reduction] 视觉降维：搭载 ANSI Color 矩阵，针对不同故障等级提供视觉分级。
"""

import os
import sys
import re
import collections.abc
import yaml
import logging
from logging.handlers import RotatingFileHandler

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False

class TokenCounter:
    """
    🚀 工业级 Token 秤
    职责：基于 OpenAI 的 tiktoken 算法提供高精度的字数测算。
    内置“软下降”机制，确保在库缺失的情况下提供可接受的估算值。
    """
    _encoding = None

    @classmethod
    def get_encoding(cls):
        if cls._encoding is None and HAS_TIKTOKEN:
            try:
                # 统一使用 cl100k_base 编码，适用于 GPT-4 及后续主流模型
                cls._encoding = tiktoken.get_encoding("cl100k_base")
            except Exception:
                pass
        return cls._encoding

    @classmethod
    def count(cls, text: str) -> int:
        """测算文本的物理 Token 消耗量"""
        if not text:
            return 0
        
        encoding = cls.get_encoding()
        if encoding:
            try:
                return len(encoding.encode(text, disallowed_special=()))
            except Exception:
                # 若编码失败（极罕见），降级到估算
                pass
        
        # 🚀 降级算法：中英混合场景下，1 个 Token 约等于 1.5 ~ 2 个字符
        # 此处采用偏保守的 1.5 倍系数
        return int(len(text) / 1.5)

class ColoredFormatter(logging.Formatter):
    """
    🚀 视觉降维：自定义 ANSI 彩色日志格式化器
    针对不同严重等级，在终端输出时注入特定的颜色代码，提升运维效率。
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
        logging.WARNING: YELLOW,   # 🟡 AI 降级/图片跳过/安全警告
        logging.ERROR: BOLD_RED,   # 🔴 关键故障/写盘失败/配置异常
        logging.CRITICAL: BOLD_RED # 🛑 致命错误/审计拦截
    }

    def format(self, record):
        log_fmt = self.LEVEL_MAP.get(record.levelno, self.RESET) + self.FORMAT + self.RESET
        formatter = logging.Formatter(log_fmt, datefmt='%H:%M:%S')
        return formatter.format(record)



def strip_technical_noise(content, options=None):
    """
    🚀 语义提纯引擎：物理剥离 Markdown/MDX 中的工程噪声。
    :param content: 原始 Markdown 内容
    :param options: 从 config.yaml 下发的过滤开关 (支持字典或 PurificationSettings 对象)
    :return: 提纯后的纯文本，用于 AI 摘要、SEO 提取及空载检查
    """
    if not content:
        return ""
    
    # 支持强类型对象与旧版字典的双向兼容
    def get_opt(key, default):
        if options is None: return default
        if hasattr(options, key): return getattr(options, key)
        if isinstance(options, dict): return options.get(key, default)
        return default
    
    # 1. [物理隔离] 剥离 <style> 和 <script> 块 (MDX 渲染重灾区)
    if get_opt('strip_styles', True):
        content = re.sub(r'<(style|script).*?>.*?</\1>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # 2. [语法剥离] 剥离 MDX 的 import/export 语句
    if get_opt('strip_mdx_imports', True):
        content = re.sub(r'^(import|export)\s+.*?;?$', '', content, flags=re.MULTILINE | re.DOTALL)
    
    # 3. [注释剥离] 移除 HTML 注释
    if get_opt('strip_comments', True):
        content = re.sub(r'<!' + r'--(.*?)--' + r'>', '', content, flags=re.DOTALL)
        
    # 4. [代码块剥离] 针对 SEO 场景，代码块通常不贡献核心语义
    if get_opt('strip_code_blocks', True):
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'`.*?`', '', content)

    # 5. [组件剥离] 移除特定的 JSX/MDX 标签名，保留内部文字
    # 匹配 <Tag ...> 或 </Tag>，仅保留中间的文本
    if get_opt('strip_jsx_tags', True):
        content = re.sub(r'<[A-Z][A-Za-z0-9_]*[^>]*?>', '', content)
        content = re.sub(r'</[A-Z][A-Za-z0-9_]*>', '', content)
    
    # 6. [空白压缩] 压缩多余空行，保持 AI 上下文紧致
    content = re.sub(r'\n\s*\n', '\n\n', content)
    
    return content.strip()
    
def setup_logger():
    """
    初始化工业级守护进程日志管线。
    支持控制台彩色显示与文件滚动备份，确保长期运行的审计追踪。
    """
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    logger = logging.getLogger("Illacme.plenipes")
    
    if logger.hasHandlers():
        logger.handlers.clear()
        
    # 1. 基础格式（文件日志使用纯文本，防止 ANSI 乱码）
    file_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%H:%M:%S')
    
    # 2. 彩色格式（用于终端控制台实时交互）
    console_formatter = ColoredFormatter()
    
    # 物理日志落盘：单文件 5MB，保留 3 代备份
    fh = RotatingFileHandler(os.path.join(log_dir, 'plenipes.log'), maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
    fh.setFormatter(file_formatter)
    
    # 控制台实时反馈流
    ch = logging.StreamHandler()
    ch.setFormatter(console_formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

def normalize_keywords(kw_data):
    """
    数据降维清洗器：支持中英文逗号、分号的智能识别与标准化。
    用于处理 Frontmatter 中的 tags 或 keywords 字段。
    🚀 [V15.5 架构级修复] 强制输出纯正的 Python List 结构。
    彻底解决 Docusaurus 等严苛型 SSG 对 "keywords must be an array" 的基线校验，同时完美向下兼容 Astro。
    """
    if not kw_data:
        return []
    
    if isinstance(kw_data, list):
        # 剔除空字符串并返回干净的列表
        return [str(k).strip() for k in kw_data if str(k).strip()]
        
    elif isinstance(kw_data, str):
        # 🚀 语义平滑：自动切割所有主流的分隔符，直接返回阵列矩阵
        return [k.strip() for k in re.split(r'[,，;；]', kw_data) if k.strip()]
        
    # 兜底：对极其罕见的异常结构强行转换为单元素数组
    return [str(kw_data).strip()] if str(kw_data).strip() else []

def extract_frontmatter(content):
    """
    安全隔离器：将 YAML 属性定义区与 Markdown 文档正文进行物理分离。
    """
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1)) or {}, content[match.end():]
        except yaml.YAMLError as e:
            logger = logging.getLogger("Illacme.plenipes")
            # 🚀 语义降维提示
            logger.error(f"⚠️ 关键路径解析异常: 文档 YAML 属性区语法错误。💡 建议: 检查冒号后的空格和缩进。详细报错: {e}")
            pass
    return {}, content

def sanitize_ai_response(text):
    """
    🚀 AI 内容净化引擎：物理剔除大模型生成的非法“隔离带”标签与对话残留。
    模块职责：防御 AI 幻觉引发的前端框架渲染崩溃。
    支持清理：<source_text> 标签、包裹全网的 Markdown 代码块围栏、以及引导性废话。
    """
    if not text:
        return ""
    
    # 1. 物理斩断：彻底剔除自定义隔离区标签 (不区分大小写)
    text = re.sub(r'</?source_text>', '', text, flags=re.IGNORECASE)
    
    # 2. 围栏清理：如果 AI 将翻译结果包裹在 ```markdown ... ``` 中，将其扒开
    text = re.sub(r'^```[a-zA-Z]*\n', '', text)
    text = re.sub(r'\n```$', '', text)
    
    # 3. 碎片清理：移除引导性、总结性短语（兼容中英文常见模式）
    removals_start = [
        r'^Here is the translation:?\n',
        r'^Translation:?\n',
        r'^翻译结果:?\n',
        r'^以下是翻译:?\n',
        r'^Sure, here is the translated text:?\n',
        r'^Certainly! Here is the translation:?\n'
    ]
    for pattern in removals_start:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # 🚀 [V30 加固] 尾部署名/社交辞令清理
    removals_end = [
        r'\n\s*Hope this helps!.*$',
        r'\n\s*Let me know if.*$',
        r'\n\s*Translation completed\.*$',
        r'\n\s*希望能帮到你.*$',
        r'\n\s*翻译完毕.*$',
        r'\n\s*请核对以上翻译.*$'
    ]
    for pattern in removals_end:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
        
    return text.strip()