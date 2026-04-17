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

    def __init__(self, theme_settings):
        """
        初始化适配器。
        :param theme_settings: ThemeSettings 强类型配置对象。
        """
        self.theme = theme_settings
        self.syntax_engine = self.theme.syntax_engine.lower().strip()
        
        # 预加载目标框架映射表，实现单点构建中的 O(1) 级转换效率
        # 优先级：YAML 配置 > 内部各引擎默认值 > 通用映射表
        self._engine_map = self.theme.type_mapping or {}
        
        # 🧪 [专家回旋] 如果映射表为空，则尝试载入已知框架的生产级预置值
        if not self._engine_map:
            if self.syntax_engine == 'starlight':
                self._engine_map = {'info': 'note', 'warning': 'caution', 'danger': 'danger', 'success': 'tip', 'tip': 'tip'}
            elif self.syntax_engine in ['vitepress', 'docusaurus']:
                self._engine_map = {'info': 'info', 'warning': 'warning', 'danger': 'danger', 'success': 'success', 'tip': 'tip'}

    def convert_callouts(self, content):
        """
        🚀 全球化语法降维引擎：将通用 Callout 转换为目标框架的物理组件。
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
            
            # 🚀 [V32] 声明式渲染优先
            if self.theme.callout_template and self.theme.callout_template != "\n> **{title}**\n> {body_quoted}\n\n":
                res = self.theme.callout_template.replace('{type}', target_type).replace('{title}', title).replace('{body}', body)
                return res

            # 兼容性兜底：强制执行 ::: 转换 (Starlight/Docusaurus/VitePress)
            if self.syntax_engine in ['docusaurus', 'vitepress', 'starlight']:
                prefix = f":::{target_type}"
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
        mappings = self.theme.component_mappings
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
                res = re.sub(r'\{([a-zA-Z_]+)\}', r'""', res)
                return res

            # A. 循环处理嵌套容器 (处理成对标签)
            while f'<{component}' in content and f'</{component}>' in content:
                pattern = re.compile(rf'<{component}(?:\s*|(?:\s+[^>]*))>(((?!<{component}).)*?)</{component}>', re.DOTALL)
                new_content = pattern.sub(complex_repl, content)
                if new_content == content: break
                content = new_content

            # B. 处理自闭合或单标签
            single_pattern = re.compile(rf'<{component}(?:\s+([^/>]*))?/?>', re.MULTILINE)
            content = single_pattern.sub(complex_repl, content)

            # C. 🚀 [V16.8 稳定性加固] 残留标签平整化
            residual_tag_pattern = re.compile(rf'</?{component}(?:\s+[^>]*)?>', re.MULTILINE)
            content = residual_tag_pattern.sub('', content)

        # 3. 🚀 [V16 专项加固] 样式块降维打击
        if '<style>' in content:
            content = content.replace('<style>{`', '<style>{`').replace('`}</style>', '`}</style>')
            if '<style>' in content and '</style>' not in content:
                content += '\n`}</style>'

        # 4. 标签对齐
        content = re.sub(r'<Aside\s+type="([a-z]+)"(?:\s+title="([^"]*)")?>', r':::\1 \2', content)
        content = content.replace('</Aside>', ':::').replace('</Side>', ':::')
        
        return content

    def adapt_metadata(self, fm_dict, date_obj, author_name):
        """
        🚀 语义对齐投影仪：将原始 Frontmatter 根据目标框架进行全量投影适配。
        """
        mapping = self.theme.metadata_mapping
        new_fm = fm_dict.copy()
        
        # 1. 🚀 [时空分流] 时间映射 (继承 V24-V25 逻辑)
        mod_cfg = mapping.get('last_modified', {})
        if mod_cfg:
            key = mod_cfg.get('key', 'last_modified')
            style = mod_cfg.get('style', 'plain')
            
            if style == 'object':
                new_fm[key] = {'date': date_obj, 'author': author_name}
            else:
                new_fm[key] = date_obj
        
        # 2. 🚀 [语义对齐] 作者映射
        auth_cfg = mapping.get('author', {})
        if auth_cfg and 'author' in new_fm:
            target_key = auth_cfg.get('key', 'author')
            if target_key != 'author':
                new_fm[target_key] = new_fm.pop('author')
                
        # 3. 🚀 [语义对齐] 关键词/标签重构
        kw_cfg = mapping.get('keywords', {})
        if kw_cfg:
            source_key = 'keywords'
            target_key = kw_cfg.get('key', 'tags')
            
            # 如果源数据中有 keywords 且目标框架期待 tags，则执行物理重映射
            if source_key in new_fm and target_key != source_key:
                new_fm[target_key] = new_fm.pop(source_key)
                
        # 4. 🚀 [噪音治理] 系统字段可见性控制 (如 _illacme_ver)
        sys_cfg = mapping.get('system_fields', {})
        for field, action in sys_cfg.items():
            if action == 'hidden' and field in new_fm:
                new_fm.pop(field)
                
        return new_fm