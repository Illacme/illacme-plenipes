#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Parser Engine (Syntax Adapter)
模块职责：AST（抽象语法树）与正则降维层。负责 Obsidian 专有语法的翻译、嵌套文档展开与全域基础语法兼容。
架构原则：贯彻“内容即数据”的设计哲学，通过递归解析处理文档间的嵌套逻辑，并通过策略模式适配主流 SSG 前端。
"""

import os
import re
import logging
import threading
from .utils import extract_frontmatter

# 初始化核心日志句柄，用于输出具备“保姆级”诊断建议的日志
logger = logging.getLogger("Illacme.plenipes")

class TransclusionResolver:
    """
    处理 Obsidian 特有的 ![[嵌套文档]] 双链展开逻辑。
    
    该类通过递归扫描 Markdown 内容中的嵌入指令，将引用的子文档内容直接注入到父文档中，
    并内置了双重检查锁定 (DCL) 缓存机制以优化高并发下的 I/O 吞吐性能。
    """
    def __init__(self, md_index, asset_index, max_depth=3):
        """
        初始化嵌套解析器。
        :param md_index: 全局 Markdown 文件寻址倒排索引。
        :param asset_index: 全局静态资产寻址索引。
        :param max_depth: 最大嵌套递归深度，防止出现循环引用导致的进程栈溢出。
        """
        self.md_index = md_index
        self.asset_index = asset_index
        
        # 🚀 动态读取嵌套层数防线，默认配置为 3 层，足以覆盖绝大多数复杂的知识建模场景
        self.max_depth = max_depth
        
        # 架构升级：注入线程安全的内存级防抖缓存，确保同一子文档在一次构建中仅被读取一次
        # [2026 补丁] 升级为感知物理修改时间 (mtime) 的智能淘汰字典
        self._cache = {}
        self._cache_lock = threading.Lock()
        
        # 预编译正则表达式，确保在高频文本匹配中拥有极致的性能表现
        self._pattern = re.compile(r'^[ \t]*\!\[\[([^\]]+)\]\]', re.MULTILINE)

    def expand(self, content, current_depth=0):
        """
        递归且物理地展开嵌套引用。
        
        采用深度优先搜索 (DFS) 算法，逐层剥离并注入嵌套的引用标记。
        若达到最大深度限制，将触发主动预判告警并停止穿透，保留原始标记以保护进程安全。
        """
        # 🚀 主动预判：当递归深度跨越水位线时，强制中断以防止循环引用导致的死循环
        if current_depth > self.max_depth: 
            logger.warning(f"⚠️ 嵌套递归受限: 节点展开深度已达上限 ({self.max_depth})。💡 建议: 请检查是否存在 A 引用 B、B 又引用 A 的循环引用逻辑。")
            return content 
            
        def repl(m):
            # 提取链接目标，并精准剥离 Obsidian 可能包含的别名 (|) 和锚点 (#) 后缀
            link_target = m.group(1).split('|')[0].split('#')[0].strip()
            
            # 如果命中的是静态资产（如图片），则不属于文档展开范畴，原样退回给后续的资产管线接管
            if link_target in self.asset_index: 
                return m.group(0) 
            
            # 从全局寻址索引中获取该文档的物理路径
            target_abs_path = self.md_index.get(link_target)
            if target_abs_path and os.path.exists(target_abs_path):
                
                # 🚀 探针升级：获取被引用文件的当前物理修改时间
                current_mtime = os.path.getmtime(target_abs_path)
                
                # 双重检查锁定 (DCL) 内存缓存读取：阻断多线程环境下的重复磁盘 I/O 竞争
                with self._cache_lock:
                    cached_node = self._cache.get(target_abs_path)
                    # 🚀 防毒化验证：只有当缓存存在，且缓存的写入时间大于等于当前文件的物理时间时，才允许使用缓存
                    if cached_node and cached_node['mtime'] >= current_mtime:
                        cached_body = cached_node['content']
                    else:
                        cached_body = None
                    
                if cached_body is None:
                    try:
                        with open(target_abs_path, 'r', encoding='utf-8') as f: 
                            t_content = f.read()
                        
                        # 仅提取 Body 内容，剔除 Frontmatter 元数据，防止污染父文档的属性区
                        _, t_body = extract_frontmatter(t_content)
                        
                        with self._cache_lock:
                            # 🚀 刷新缓存，记录最新的修改时间戳
                            self._cache[target_abs_path] = {
                                'mtime': current_mtime,
                                'content': t_body
                            }
                            cached_body = t_body
                    except Exception as e:
                        # 🚀 语义化诊断：提供更具指导意义的错误提示
                        logger.warning(f"⚠️ 引用展开失败: 无法读取文件 '{link_target}'。💡 诊断: 该文件可能已被锁定、正在被其他程序占用，或者源路径包含系统无法识别的特殊字符。")
                        return m.group(0)
                
                # 递归执行深度展开，步进深度计数器
                expanded = self.expand(cached_body, current_depth + 1)
                return f"\n\n{expanded}\n\n"
                
            return m.group(0)
            
        return self._pattern.sub(repl, content)

class SSGAdapter:
    """
    策略模式：根据目标前端框架（Astro/VitePress/Docusaurus等），动态执行语法重构。
    
    核心职责：
    1. 大小写降维防御：统一代码块语言标识为小写，解决 Linux 环境下前端高亮引擎的匹配失效。
    2. Callout 转换：将 Obsidian 专有语法映射为各主流 SSG 框架支持的标准 Container 语法。
    """
    
    # 🚀 将正则和语义映射表提升为类级常量，彻底消灭运行时高频正则编译的 CPU 开销
    # 匹配规则：精确捕获 Callout 类型标识、自定义标题及后续连续的引用行块
    _CALLOUT_PATTERN = re.compile(r'^>[ \t]*\[!([a-zA-Z]+)\](.*?)\n((?:^[ \t]*>.*\n?)*)', re.MULTILINE)
    
    # 🚀 防御阵列：精准识别代码块起始位，用于强制执行大小写扁平化处理
    _CODE_BLOCK_PATTERN = re.compile(r'^([`~]{3,})([a-zA-Z0-9_+-]+)[ \t]*$', re.MULTILINE)
    
    # 通用语义映射表：将 Obsidian 极其细分的 Callout 类型映射为 SSG 核心标准类型
    _GENERIC_MAP = {
        'info': 'info', 'abstract': 'info', 'note': 'info', 'question': 'info',
        'warning': 'warning', 'attention': 'warning',
        'error': 'danger', 'bug': 'danger', 'danger': 'danger',
        'success': 'success', 'check': 'success', 'tip': 'tip'
    }

    def __init__(self, engine_name):
        """
        初始化适配器。
        :param engine_name: 目标前端引擎名称（如 starlight, vitepress, docusaurus, hugo, hexo）。
        """
        self.engine = engine_name.lower().strip()
        
        # 预加载目标框架映射表，实现单点构建中的 O(1) 级转换效率
        self._engine_map = {}
        if self.engine == 'starlight':
            self._engine_map = {'info': 'note', 'warning': 'caution', 'danger': 'danger', 'success': 'tip', 'tip': 'tip'}
        elif self.engine in ['vitepress', 'docusaurus']:
            self._engine_map = {'info': 'info', 'warning': 'warning', 'danger': 'danger', 'success': 'success', 'tip': 'tip'}

    def convert_callouts(self, text):
        """
        执行语法全量转换与防御性预处理。
        
        处理链路：
        1. 执行“大小写降维防御”，将 ```YAML 强转为 ```yaml，确保 Linux 环境部署时语法高亮不会由于严格匹配而失效。
        2. 执行 Callout 策略转换，将 Obsidian 引用块映射为目标 SSG 的标准 Container（如 ::: 语法）。
        """
        # 🚀 架构级防御：先抹平代码块的大写问题，彻底消灭前端渲染引擎常见的 Language Not Found 警告
        text = self._CODE_BLOCK_PATTERN.sub(lambda m: f"{m.group(1)}{m.group(2).lower()}", text)

        def repl(m):
            ctype = m.group(1).lower()
            title = m.group(2).strip()
            body = m.group(3)
            
            # 清理引用行中的每一行前导 '>' 标记，提取出纯净的 Callout 内容主体
            body = re.sub(r'^[ \t]*>[ \t]?', '', body, flags=re.MULTILINE).strip()
            g_type = self._GENERIC_MAP.get(ctype, 'info')

            # 策略分发：根据配置文件定义的引擎类型，生成对应的物理语法结构
            if self.engine == 'starlight':
                return f"\n:::{self._engine_map.get(g_type, 'note')} {title}\n{body}\n:::\n\n"
            elif self.engine in ['vitepress', 'docusaurus']:
                return f"\n:::{self._engine_map.get(g_type, 'info')} {title}\n{body}\n:::\n\n"
            elif self.engine == 'hugo':
                return f"\n{{{{< admonition type=\"{g_type}\" title=\"{title}\" >}}}}\n{body}\n{{{{< /admonition >}}}}\n\n"
            elif self.engine == 'hexo':
                return f"\n{{% note {g_type} %}}\n**{title}**\n{body}\n{{% endnote %}}\n\n"
            else:
                # 兜底方案：如果是不受支持的引擎类型，自动降级为 Markdown 标准加粗引用格式
                body_quoted = '\n> '.join(body.split('\n'))
                return f"\n> **{title}**\n> {body_quoted}\n\n"
                
        return self._CALLOUT_PATTERN.sub(repl, text)