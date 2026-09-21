# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Math Packager (数学公式离线排版与 MathML 转译器)
模块职责：将 Obsidian / Markdown 中的 LaTeX 数学公式离线编译为 W3C EPUB 3.0 MathML 矢量语义标记。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import re
from typing import Optional
from core.utils.tracing import tlog


class MathPackager:
    """📐 电子书数学公式与科学符号离线渲染器"""

    @classmethod
    def heal_latex_formulas(cls, markdown_text: str) -> str:
        """
        全场景 LaTeX 公式安全编译管线：
        1. 优先提取并编译块级数学公式 ($$...$$)
        2. 随后编译行内数学公式 ($...$)，严格规避货币符号与转义字符
        3. 若环境未预装转换器或语法有误，优雅降级为保留源码排版块
        """
        if not markdown_text or '$' not in markdown_text:
            return markdown_text

        # 1. 块级公式转译 ($$...$$ 支持跨行与单行)
        def block_repl(m):
            raw_formula = m.group(1).strip()
            if not raw_formula:
                return ""
            mathml = cls._latex_to_mathml(raw_formula, display="block")
            if mathml:
                return f"\n\n<div class=\"math-block\">{mathml}</div>\n\n"
            return f"\n\n<div class=\"math-block\"><code class=\"math-latex\">$${raw_formula}$$</code></div>\n\n"

        text_after_blocks = re.sub(r'\$\$(.+?)\$\$', block_repl, markdown_text, flags=re.DOTALL)

        # 2. 行内公式转译 ($...$ 排除 \\$ 转义与纯数字金额如 $100)
        def inline_repl(m):
            raw_formula = m.group(1).strip()
            if not raw_formula:
                return m.group(0)
            # 规避纯金额数字如 $100, $ 50.00
            if re.match(r'^\s*[\d,]+(?:\.\d+)?\s*$', raw_formula):
                return m.group(0)
            mathml = cls._latex_to_mathml(raw_formula, display="inline")
            if mathml:
                return mathml
            return f'<code class="math-latex">${raw_formula}$</code>'

        # 负向零宽断言：确保不匹配以 \\ 转义的 \\$、纯货币金额符号 ($100) 以及跨行文本
        healed_text = re.sub(r'(?<![\w\\\$])\$(?!\s|\d)([^\$\n]+?)(?<!\s)\$(?![\w\$])', inline_repl, text_after_blocks)
        return healed_text

    @classmethod
    def _latex_to_mathml(cls, latex: str, display: str = "inline") -> Optional[str]:
        """将 LaTeX 字符串编译为标准 MathML，具备异常优雅降级"""
        try:
            from latex2mathml.converter import convert
            clean_latex = latex.replace(r'\,', ' ').strip()
            mathml = convert(clean_latex, display=display)
            # 确保 XML 兼容自闭合与实体标准
            return mathml.strip()
        except ImportError:
            tlog.debug("ℹ️ [数学公式] 未检测到 latex2mathml，保留 LaTeX 源码排版")
            return None
        except Exception as e:
            tlog.debug(f"⚠️ [数学公式] 公式编译容错跳过 ({latex[:30]}...): {e}")
            return None
