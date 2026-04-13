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

class ConfigValidator:
    """
    🚀 预飞行审计引擎 (Pre-flight Auditor)
    模块职责：在核心引擎启动前，对合并及推导后的全量配置进行静态语义检查。
    拦截维度：物理路径存活性、数据类型契约一致性、翻译令牌安全隔离检查。
    """
    def __init__(self, config):
        self.cfg = config
        self.logger = logging.getLogger("Illacme.plenipes")
        self.has_error = False

    def _log_error(self, msg):
        self.logger.error(f"🛑 [配置审计失败] {msg}")
        self.has_error = True

    def validate(self):
        """执行全量审计流水线"""
        self.logger.info("🛡️ 正在执行系统点火前的全量配置审计...")
        
        # 1. 物理路径存活性核验 (源头检测)
        self._check_source_paths()
        
        # 2. 核心数据类型契约核验 (物理免疫 'str' object has no attribute 'get' 崩溃)
        self._check_data_structures()
        
        # 3. 翻译引擎与密钥隔离审计 (环境优先原则)
        self._check_translation_safety()
        
        if self.has_error:
            self.logger.critical("❌ 预飞行审计未通过！为了保护笔记数据与 AI 额度安全，引擎已自动切断点火程序。")
            self.logger.critical("💡 建议：请根据上方红字提示修正 config.yaml 或 config.local.yaml 后重试。")
            sys.exit(1)
        
        self.logger.info("✨ 预飞行审计完美通过，系统安全屏障已建立。")

    def _check_source_paths(self):
        """审计物理路径是否存在，解决“找不到映射物理目录”的根源问题"""
        vault_root = self.cfg.get('vault_root')
        if not vault_root:
            self._log_error("配置项 'vault_root' 缺失。引擎无法定位您的笔记库基座。")
        else:
            abs_vault = os.path.abspath(os.path.expanduser(vault_root))
            if not os.path.exists(abs_vault):
                self._log_error(f"笔记库路径不存在: {abs_vault}\n   └── 💡 诊断：请检查外置硬盘是否挂载，或 config.local.yaml 中的路径书写是否有误。")

    def _check_data_structures(self):
        """
        审计数据类型结构。
        防止用户在 config.local.yaml 中将原本应是字典的对象误写成了字符串。
        """
        # 审计重灾区名单：配置项名称 -> 期望的类型契约
        critical_structs = {
            'system': collections.abc.Mapping,
            'translation': collections.abc.Mapping,
            'image_settings': collections.abc.Mapping,
            'output_paths': collections.abc.Mapping,
            'i18n_settings': collections.abc.Mapping
        }
        
        for key, expected_type in critical_structs.items():
            val = self.cfg.get(key)
            # 如果配置项存在，则强制校验其类型
            if val is not None and not isinstance(val, expected_type):
                self._log_error(
                    f"配置项 '{key}' 类型违约。期望 {expected_type.__name__}，实际解析为 {type(val).__name__}。\n"
                    f"   └── 💡 诊断：通常是由于 YAML 缩进不当，导致解析器将其误认为纯文本。请确保冒号后有空格且层级正确。"
                )

    def _check_translation_safety(self):
        """
        审计翻译令牌安全性。
        贯彻“环境变量最高特权”逻辑：如果环境变量存在，则忽略配置文件的 key 状态。
        """
        trans_cfg = self.cfg.get('translation', {})
        if not isinstance(trans_cfg, collections.abc.Mapping):
            return # 交给类型核验模块拦截
            
        provider = str(trans_cfg.get('provider', 'none')).lower()
        if provider == 'none':
            return
            
        # 优先级审计：系统环境变量 > 配置文件读取
        env_key = os.environ.get('ILLACME_API_KEY')
        cfg_key = trans_cfg.get('api_key')
        
        if not env_key:
            # 若环境变量缺失，则检查配置文件是否填了有效 Key
            if not cfg_key or cfg_key in ['unused', 'your-key-here', '']:
                self.logger.warning("🟡 [安全警告] 翻译引擎已激活，但未探测到任何 API 密钥。")
                self.logger.warning("   └── 💡 建议：请在环境变量中注入 ILLACME_API_KEY，或在配置文件中补齐 api_key 字段。")

def strip_technical_noise(content, options=None):
    """
    🚀 语义提纯引擎：物理剥离 Markdown/MDX 中的工程噪声。
    :param content: 原始 Markdown 内容
    :param options: 从 config.yaml 下发的过滤开关字典
    :return: 提纯后的纯文本，用于 AI 摘要、SEO 提取及空载检查
    """
    if not content:
        return ""
    
    options = options or {}
    
    # 1. [物理隔离] 剥离 <style> 和 <script> 块 (MDX 渲染重灾区)
    if options.get('strip_styles', True):
        content = re.sub(r'<(style|script).*?>.*?</\1>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # 2. [语法剥离] 剥离 MDX 的 import/export 语句
    if options.get('strip_mdx_imports', True):
        content = re.sub(r'^(import|export)\s+.*?;?$', '', content, flags=re.MULTILINE | re.DOTALL)
    
    # 3. [注释剥离] 移除 HTML 注释
    if options.get('strip_comments', True):
        content = re.sub(r'<!' + r'--(.*?)--' + r'>', '', content, flags=re.DOTALL)
        
    # 4. [代码块剥离] 针对 SEO 场景，代码块通常不贡献核心语义
    if options.get('strip_code_blocks', True):
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'`.*?`', '', content)

    # 5. [组件剥离] 移除特定的 JSX/MDX 标签名，保留内部文字
    # 匹配 <Tag ...> 或 </Tag>，仅保留中间的文本
    if options.get('strip_jsx_tags', True):
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
    """
    if not kw_data:
        return ""
    
    if isinstance(kw_data, list):
        clean_list = [str(k).strip() for k in kw_data if str(k).strip()]
        return ", ".join(clean_list)
        
    elif isinstance(kw_data, str):
        # 🚀 语义平滑：自动切割所有主流的分隔符
        clean_list = [k.strip() for k in re.split(r'[,，;；]', kw_data) if k.strip()]
        return ", ".join(clean_list)
        
    return str(kw_data).strip()

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

def load_unified_config(base_config_path):
    """
    🚀 工业级全局统一配置装载中心 (Single Source of Truth)
    模块职责：解析 YAML -> 执行级联合并 -> 智能路径推导 -> 强制占位符抹平 -> 强制审计。
    """
    def deep_update(d, u):
        """深度融合引擎：原地修改目标字典，支持无限层级的嵌套覆写。"""
        if not isinstance(d, collections.abc.Mapping):
            d = {}
        if not isinstance(u, collections.abc.Mapping):
            return d

        for k, v in u.items():
            if isinstance(v, collections.abc.Mapping):
                sub_d = d.get(k, {})
                if not isinstance(sub_d, collections.abc.Mapping):
                    sub_d = {}
                d[k] = deep_update(sub_d, v)
            else:
                d[k] = v
        return d

    # 1. 加载云端/默认基线配置
    abs_base_path = os.path.abspath(os.path.expanduser(base_config_path))
    try:
        with open(abs_base_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
    except Exception as e:
        logging.getLogger("Illacme.plenipes").error(f"🛑 致命错误: 无法读取主配置文件 {abs_base_path}: {e}")
        sys.exit(1)

    # 2. 挂载本地特权沙盒覆盖 (config.local.yaml)
    base_dir = os.path.dirname(abs_base_path)
    local_config_path = os.path.join(base_dir, 'config.local.yaml')
    
    if os.path.exists(local_config_path):
        try:
            with open(local_config_path, 'r', encoding='utf-8') as f:
                local_config = yaml.safe_load(f) or {}
            config = deep_update(config, local_config)
            logging.getLogger("Illacme.plenipes").info("⚙️ 侦测到本地沙盒配置，已激活【特权覆写】引擎。")
        except Exception as e:
            logging.getLogger("Illacme.plenipes").error(f"🛑 解析本地配置失败: {e}。将退回使用基线配置。")

    # 3. 🚀 [核心升级] 智能路径推导与占位符绝对抹平
    theme = config.get('active_theme', 'starlight')
    
    if 'output_paths' not in config or not config['output_paths']:
        paths = {}
        config['output_paths'] = paths
    else:
        paths = config['output_paths']
        if not isinstance(paths, collections.abc.Mapping):
            paths = {}
            config['output_paths'] = paths
            
    # 提取原始路径（包含默认推导逻辑）
    raw_md_dir = paths.get('markdown_dir', "./themes/{theme}/src/content/docs")
    raw_assets_dir = paths.get('assets_dir', "./themes/{theme}/public/assets")

    # 🚨 架构级对齐：在此处直接完成 {theme} 魔法占位符的物理替换
    # 确保下游 engine.py 及其子模块拿到的路径永远是最终确定的绝对物理状态！
    paths['markdown_dir'] = raw_md_dir.replace('{theme}', theme)
    paths['assets_dir'] = raw_assets_dir.replace('{theme}', theme)

    # 4. 触发强制点火审计
    validator = ConfigValidator(config)
    validator.validate()

    return config