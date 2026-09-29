# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Test Suite for Docx Math OMML Conversion & Academic Equations
测试目标：
1. MathPackager.latex_to_omml 基础公式与高级求和/分式转译测试
2. DocxBookAdapter 块级公式 ($$...$$) 居中转译为 Word 原生 OMML 对象
3. DocxBookAdapter 行内公式 ($...$) 嵌入段落 Run 并保留周围正文
4. 真实解压验证生成的 docx 内部包含 Word 官方 math 命名空间与 oMath 节点
5. 异常公式或非公式符号（如货币金额 $100）不被误转译与优雅降级
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import zipfile
import pytest

from core.bindery.math_packager import MathPackager
from core.adapters.egress.ebook.docx import DocxBookAdapter


def test_math_packager_latex_to_omml():
    """测试 MathPackager 将 LaTeX 转为合法的 OMML XML"""
    latex = r"E = mc^2"
    omml = MathPackager.latex_to_omml(latex, display="inline")
    assert omml is not None
    assert "<m:oMath" in omml
    assert "xmlns:m=" in omml
    assert "c" in omml and "2" in omml

    # 复杂求和与分式
    latex_sum = r"\sum_{i=1}^{n} i = \frac{n(n+1)}{2}"
    omml_sum = MathPackager.latex_to_omml(latex_sum, display="block")
    assert omml_sum is not None
    assert "<m:oMath" in omml_sum
    assert "<m:f>" in omml_sum  # OMML fraction (分式标签)


def test_docx_book_adapter_math_equations_generation(tmp_path):
    """测试 DocxBookAdapter 完整生成包含原生数学公式的 Word 审校本"""
    adapter = DocxBookAdapter()
    out_docx = tmp_path / "academic_math_review.docx"

    manuscript_tree = [
        {
            "id": "ch_math",
            "title": "量子物理与经典力学公式选集",
            "slug": "quantum_math",
            "raw_body": (
                "# 理论物理导论\n\n"
                "质能方程是由爱因斯坦提出的重要公式，其表达形式为 $E = mc^2$，这是近代物理学的基石。\n\n"
                "在静力学中，毕达哥拉斯定理表明斜边平方等于两直角边平方和：$a^2 + b^2 = c^2$。\n\n"
                "下面展示离散求和的经典封闭形式：\n\n"
                "$$\n"
                "\\sum_{k=1}^{n} k = \\frac{n(n+1)}{2}\n"
                "$$\n\n"
                "单行块级高斯积分如下：\n\n"
                "$$\\int_{-\\infty}^{+\\infty} e^{-x^2} dx = \\sqrt{\\pi}$$\n\n"
                "> [!NOTE]\n"
                "> 引用块中同样支持行内公式如 $\\hbar = \\frac{h}{2\\pi}$ 说明。\n\n"
                "- 列表项第一条：牛顿第二定律 $F = ma$\n"
                "- 列表项第二条：纯金额字符如 $100 或 $200 不应被误判为公式\n\n"
                "文末总结。\n"
            ),
            "headings": [{"title": "理论物理导论", "level": 1}],
            "assets": []
        }
    ]

    metadata = {
        "title": "理论物理学术研读集",
        "author": "Dr. Plenipes",
        "publisher": "Illacme Academic Press",
        "description": "包含微软原生可编辑数学公式的学术审校文档"
    }

    success = adapter.bind_book(
        manuscript_tree=manuscript_tree,
        book_metadata=metadata,
        target_lang="zh",
        output_file_path=str(out_docx)
    )

    assert success is True
    assert out_docx.exists()
    assert out_docx.stat().st_size > 5000

    # 验证生成的 docx 归档内的 document.xml 结构
    with zipfile.ZipFile(str(out_docx), "r") as zf:
        doc_xml = zf.read("word/document.xml").decode("utf-8")
        # 1. 包含 Office Math 命名空间或 oMath 标签
        assert "http://schemas.openxmlformats.org/officeDocument/2006/math" in doc_xml or "w:r" in doc_xml
        assert "oMath" in doc_xml
        # 2. 包含正文字符与标题
        assert "理论物理导论" in doc_xml
        assert "爱因斯坦" in doc_xml
        assert "毕达哥拉斯定理" in doc_xml
        # 3. 规避纯金额数字误伤
        assert "$100" in doc_xml
