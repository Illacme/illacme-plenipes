# -*- coding: utf-8 -*-
"""
Illacme Plenipes - EBook Math & Code Syntax Highlighting Test Suite
模块职责：验证 LaTeX 离线转译为 MathML、货币防误伤、Pygments 代码高亮及 EPUB 3.0 MathML 属性契约。
"""

import os
import zipfile
import tempfile
import xml.etree.ElementTree as ET
import markdown
import pytest

from core.bindery.math_packager import MathPackager
from core.bindery.book_assembler import BookAssembler


def test_math_packager_block_and_inline():
    """验证块级与行内 LaTeX 数学公式正确转译为 MathML"""
    # 1. 行内公式
    inline_md = "爱因斯坦质能方程为 $E = mc^2$ 描述了质量与能量的关系。"
    healed_inline = MathPackager.heal_latex_formulas(inline_md)
    assert '<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">' in healed_inline
    assert 'E' in healed_inline
    assert 'm' in healed_inline
    assert 'c' in healed_inline

    # 2. 块级公式
    block_md = """
公式如下：
$$
\\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}
$$
以上是求根公式。
"""
    healed_block = MathPackager.heal_latex_formulas(block_md)
    assert '<div class="math-block">' in healed_block
    assert '<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">' in healed_block
    assert '<mfrac>' in healed_block
    assert '<msqrt>' in healed_block

    # 3. 复杂公式（求和与积分）
    sum_md = "$$\\sum_{i=1}^{n} x_i$$"
    healed_sum = MathPackager.heal_latex_formulas(sum_md)
    assert '<munderover>' in healed_sum or '<msubsup>' in healed_sum or '<mo>' in healed_sum


def test_math_packager_currency_and_escape_guard():
    """验证金额符号与转义字符不被误转译为数学公式"""
    # 1. 金额符号 $100, $50.00
    currency_md = "该服务费用为 $100 美元，月付只需 $50.00。"
    healed_cur = MathPackager.heal_latex_formulas(currency_md)
    assert "<math" not in healed_cur
    assert "$100" in healed_cur
    assert "$50.00" in healed_cur

    # 2. 普通无公式纯文本
    plain_md = "这是没有数学公式的纯中文文档。"
    assert MathPackager.heal_latex_formulas(plain_md) == plain_md


def test_code_syntax_highlighting_markdown_integration():
    """验证 Markdown 结合 codehilite 扩展正确输出 Pygments 代码着色高亮结构"""
    code_md = """
```python
def calculate_area(radius: float) -> float:
    # 计算圆面积
    pi = 3.1415926
    return pi * (radius ** 2)
```
"""
    md_converter = markdown.Markdown(
        extensions=['extra', 'codehilite', 'tables'],
        extension_configs={'codehilite': {'css_class': 'codehilite', 'guess_lang': False}}
    )
    html = md_converter.convert(code_md)
    assert '<div class="codehilite">' in html
    assert '<span class="k">def</span>' in html
    assert 'calculate_area' in html
    assert '<span class="c1"># 计算圆面积</span>' in html or '<span class="c">' in html


def test_end_to_end_epub_with_math_and_code_highlighting():
    """端到端装订测试：验证导出的 EPUB 包含代码高亮样式、MathML 标签及 OPF properties='mathml' 声明"""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_dir = os.path.join(tmpdir, "vault")
        docs_dir = os.path.join(vault_dir, "science")
        os.makedirs(docs_dir, exist_ok=True)

        doc_1 = os.path.join(docs_dir, "01-physics.md")
        with open(doc_1, "w", encoding="utf-8") as f:
            f.write("""---
title: 现代物理与数值算法
order: 1
---

# 现代物理与数值算法

行内能量公式：$E = mc^2$。

块级牛顿第二定律公式：
$$
F = m \\cdot a
$$

### Python 仿真算法

```python
def simulate_force(mass: float, acceleration: float) -> float:
    return mass * acceleration
```
""")

        assembler = BookAssembler(vault_dir=vault_dir)
        epub_path = assembler.assemble_and_bind(
            category="science",
            format_type="epub",
            target_lang="zh",
            custom_title="计算物理与前沿科技",
            custom_author="量子研习社",
            cover_mode="none",
            output_dir=os.path.join(tmpdir, "dist")
        )

        assert epub_path is not None
        assert os.path.exists(epub_path)

        with zipfile.ZipFile(epub_path, "r") as zf:
            # 1. 验证 content.opf 清单具有 properties="mathml" 规范声明
            opf_str = zf.read("OEBPS/content.opf").decode("utf-8")
            assert 'id="ch_1"' in opf_str
            assert 'properties="mathml"' in opf_str

            # 2. 验证章节 XHTML 中渲染了 MathML 标签与代码高亮结构
            ch1_str = zf.read("OEBPS/text/ch_1.xhtml").decode("utf-8")
            assert '<math xmlns="http://www.w3.org/1998/Math/MathML"' in ch1_str
            assert '<div class="math-block">' in ch1_str
            assert '<div class="codehilite">' in ch1_str
            assert '<span class="k">def</span>' in ch1_str

            # 3. 验证 CSS 包含代码高亮与数学公式排版规则
            css_str = zf.read("OEBPS/styles/epub.css").decode("utf-8")
            assert ".codehilite" in css_str
            assert ".math-block" in css_str
            assert "math {" in css_str

            # 4. XML 严格解析断言：确保 XHTML 格式合法无残缺
            root = ET.fromstring(ch1_str)
            assert root.tag.endswith("html")
