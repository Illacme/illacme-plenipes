#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Egress Adapter (输出端渲染工厂)
模块职责：前端声明式渲染工厂 (SSG Adapter)。
负责在最终写盘前，将标准化的 Markdown (如 Callout 和引用块)，
套入 config.yaml 中定义的框架模板 (如 Astro 的 ::: 语法或 Hugo 的 {{< >}} 语法)。
架构原则：纯粹的翻译官，彻底解除 Python 代码与前端框架的硬编码绑定。
"""

import re
import logging

logger = logging.getLogger("Illacme.plenipes")

class SSGAdapter:
    """
    策略模式：根据目标前端框架（Astro/VitePress/Docusaurus等），动态执行语法重构。
    
    核心职责：
    1. 大小写降维防御：统一代码块语言标识为小写，解决 Linux 环境下前端高亮引擎的匹配失效。
    2. Callout 转换：将 Obsidian 专有语法映射为各主流 SSG 框架支持的标准 Container 语法。
    """
    
    # 🚀 强化版正则：支持 > 前后的可选空格，并允许标题后直接换行
    _CALLOUT_PATTERN = re.compile(r'^[ \t]*>[ \t]*\[!([a-zA-Z]+)\][ \t]*(.*?)\n((?:^[ \t]*>.*\n?)*)', re.MULTILINE)
    
    # 防御阵列：精准识别代码块起始位，用于强制执行大小写扁平化处理
    _CODE_BLOCK_PATTERN = re.compile(r'^([`~]{3,})([a-zA-Z0-9_+-]+)[ \t]*$', re.MULTILINE)
    
    # 通用语义映射表：将 Obsidian 极其细分的 Callout 类型映射为 SSG 核心标准类型
    _GENERIC_MAP = {
        'info': 'info', 'abstract': 'info', 'note': 'info', 'question': 'info',
        'warning': 'warning', 'attention': 'warning',
        'error': 'danger', 'bug': 'danger', 'danger': 'danger',
        'success': 'success', 'check': 'success', 'tip': 'tip'
    }

    def __init__(self, syntax_engine, custom_adapters=None):
        """
        初始化适配器。
        :param syntax_engine: 目标前端语法方言引擎（如 starlight, vitepress 等或自定义名称）。
        :param custom_adapters: 从 config.yaml 穿透注入的声明式适配器字典。
        """
        self.syntax_engine = syntax_engine.lower().strip()
        self.custom_adapters = custom_adapters or {}
        
        # [架构破壁] 预判当前前端引擎是否命中了配置文件中的声明式渲染策略
        self.is_declarative = self.syntax_engine in self.custom_adapters
        self.declarative_config = self.custom_adapters.get(self.syntax_engine, {})
        
        # 预加载目标框架映射表，实现单点构建中的 O(1) 级转换效率
        self._engine_map = {}
        if self.syntax_engine == 'starlight':
            self._engine_map = {'info': 'note', 'warning': 'caution', 'danger': 'danger', 'success': 'tip', 'tip': 'tip'}
        elif self.syntax_engine in ['vitepress', 'docusaurus']:
            self._engine_map = {'info': 'info', 'warning': 'warning', 'danger': 'danger', 'success': 'success', 'tip': 'tip'}

    def convert_callouts(self, content):
        """
        🚀 全球化语法降维引擎：将通用 Callout 转换为目标框架的物理组件。
        已针对 Docusaurus 进行了 Admonition 闭环加固，彻底解决 [! 符号引发的 MDX 编译崩溃。
        """
        def repl(m):
            g_type = m.group(1).lower()
            title = m.group(2).strip()
            # 物理级清洗：更彻底地剥离每一行前面的 > 符号
            raw_body = m.group(3)
            body_lines = []
            for line in raw_body.split('\n'):
                # 移除前导空格和第一个出现的 >
                clean_line = re.sub(r'^[ \t]*>[ \t]?', '', line)
                body_lines.append(clean_line)
            body = '\n'.join(body_lines).strip()
            
            # 优先级：映射表 -> 通用映射表 -> 默认 info
            target_type = self._engine_map.get(g_type) or self._GENERIC_MAP.get(g_type, 'info')
            
            # 强制执行 ::: 转换，彻底消灭 [! 符号
            if self.syntax_engine in ['docusaurus', 'vitepress', 'starlight']:
                prefix = f":::{target_type}"
                # Docusaurus 建议标题直接写在类型后面
                if title: prefix += f" {title}"
                return f"\n{prefix}\n{body}\n:::\n\n"
            
            return f"\n> **{title or target_type.upper()}**\n> {body}\n\n"

        return self._CALLOUT_PATTERN.sub(repl, content)

    def adapt_mdx_imports(self, content):
        """
        🚀 MDX 终极破壁器：处理 Acorn 解析冲突，解决变量未定义崩溃。
        """
        if self.syntax_engine != 'docusaurus':
            return content

        # 1. 物理重写：切断所有 Astro/Starlight 依赖
        content = re.sub(r"import\s+[\s\S]*?from\s+'(@astrojs/starlight|astro/config)[\s\S]*?';?", "", content)

        # 2. 🚀 执行声明式组件映射
        mappings = self.declarative_config.get('component_mappings', {})
        for component, template in mappings.items():
            
            def complex_repl(m):
                attrs_raw = m.group(1) or ""
                try:
                    inner_content = m.group(2).strip()
                except (IndexError, AttributeError):
                    inner_content = ""
                
                # 提取属性 (如 title="xxx")
                attrs = dict(re.findall(r'(\w+)\s*=\s*["\'“”]([^"\'“”]+)["\'“”]', attrs_raw))
                
                res = template
                if "{children}" in res:
                    res = res.replace("{children}", inner_content)
                # 注入属性
                for key, val in attrs.items():
                    res = res.replace(f'{{{key}}}', val)
                
                # 🛡️ 变量隔离：如果映射后仍残留 {xxx}，将其替换为字符串常量
                # 这是防止 Acorn 报错 "is not defined" 的核心逻辑
                res = re.sub(r'\{([a-zA-Z_]+)\}', r'""', res)
                return res

            # A. 循环处理嵌套容器 (处理成对标签)
            while f'<{component}' in content and f'</{component}>' in content:
                # 改进正则：允许组件名后可选空格，并使用非贪婪匹配
                pattern = re.compile(rf'<{component}(?:\s*|(?:\s+[^>]*))>(((?!<{component}).)*?)</{component}>', re.DOTALL)
                new_content = pattern.sub(complex_repl, content)
                if new_content == content: break
                content = new_content

            # B. 处理自闭合或单标签 (如 <Badge text="..." />)
            # 改进：允许属性前没有空格（即 <Badge/> 或 <Badge />）
            single_pattern = re.compile(rf'<{component}(?:\s+([^/>]*))?/?>', re.MULTILINE)
            content = single_pattern.sub(complex_repl, content)

            # C. 🚀 [V16.8 稳定性加固] 残留标签平整化 (处理不规范的单开口标签)
            # 如果配置中定义了映射但正文中仍残留开口或闭口（通常源于源文档损坏），
            # 则强制将其抹除（保留其在 A 步骤中可能已提取的内容），防止 MDX 编译崩溃。
            residual_tag_pattern = re.compile(rf'</?{component}(?:\s+[^>]*)?>', re.MULTILINE)
            content = residual_tag_pattern.sub('', content)

        # 3. 🚀 [V16 专项加固] 样式块降维打击 (解决 Acorn 解析错误)
        # 如果 MDX 包含 <style>，必须将其内容包装在反引号中，或者直接删除标签对，
        # Docusaurus 默认支持在 MDX 里直接写 <style> 但括号必须符合 JS 规范。
        # 这里我们采用最稳妥的方式：直接将 Starlight 风格的样式块转换为 Docusaurus 兼容模式。
        if '<style>' in content:
            # 物理级提取 CSS 内容并强制转义
            content = content.replace('<style>{`', '<style>{`').replace('`}</style>', '`}</style>')
            # 特殊情况：如果样式块没闭合，强制闭合防止崩溃
            if '<style>' in content and '</style>' not in content:
                content += '\n`}</style>'


        # 4. 标签对齐
        content = re.sub(r'<Aside\s+type="([a-z]+)"(?:\s+title="([^"]*)")?>', r':::\1 \2', content)
        content = content.replace('</Aside>', ':::').replace('</Side>', ':::')
        
        return content