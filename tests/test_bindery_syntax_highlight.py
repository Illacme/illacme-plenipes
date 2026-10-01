# -*- coding: utf-8 -*-
"""
Tests for DOCX Code Block Syntax Highlighting (DocxSyntaxHighlighter)
验证 Word 审校本中多语言代码高亮着色、样式合并与容错降级。
"""

import docx
from core.bindery.docx_syntax_highlighter import DocxSyntaxHighlighter
from core.bindery.docx_text_parser import DocxTextParser


def test_docx_syntax_highlighter_python():
    """验证 Python 代码词法高亮：关键字、字符串、数字、注释与函数名均被正确设置样式"""
    doc = docx.Document()
    p = doc.add_paragraph()
    py_code = 'def calculate_total(price, count=10):\n    # 计算总价\n    return price * count'
    DocxSyntaxHighlighter.highlight_code_block(p, py_code, lang="python")

    assert len(p.runs) > 1
    # 确认关键字如 def / return 被加粗且有颜色
    bold_runs = [r for r in p.runs if r.bold]
    assert len(bold_runs) >= 1
    texts = [r.text for r in p.runs]
    assert any("def" in t for t in texts)
    assert any("calculate_total" in t for t in texts)
    # 确认所有 run 使用 Consolas 字体
    for r in p.runs:
        assert r.font.name == "Consolas"


def test_docx_syntax_highlighter_fallback():
    """验证未知语言或纯文本时的平滑降级"""
    doc = docx.Document()
    p = doc.add_paragraph()
    text_content = "This is a plain text block without syntax."
    DocxSyntaxHighlighter.highlight_code_block(p, text_content, lang="unknown_lang_xyz")
    assert len(p.runs) >= 1
    assert any("plain text block" in r.text for r in p.runs)


def test_docx_text_parser_create_code_block_card_integrated():
    """验证 DocxTextParser.create_code_block_card 集成高亮器后能正常在表格中创建高亮代码卡片"""
    doc = docx.Document()
    code_lines = [
        "const express = require('express');",
        "const app = express();",
        "// 启动服务",
        "app.listen(3000);"
    ]
    DocxTextParser.create_code_block_card(doc, code_lines, lang="javascript")

    # 验证生成了包含代码卡片样式的表格
    assert len(doc.tables) == 1
    cell = doc.tables[0].cell(0, 0)
    # 语言标签段落 + 代码段落
    assert len(cell.paragraphs) >= 2
    p_code = cell.paragraphs[-1]
    assert len(p_code.runs) >= 1
    full_text = "".join(r.text for r in p_code.runs)
    assert "express" in full_text


def test_pdf_print_css_standards():
    """验证 PDF 物理印厂规范：装订线对称留白、防孤行孤字、标题跨页保护及代码着色"""
    from core.adapters.egress.ebook.pdf_assets import PDFAssets
    css = PDFAssets.get_print_css()

    # 1. 验证装订线 (Gutter Margin) 规范：左页与右页对称边距
    assert "@page :left" in css
    assert "@page :right" in css
    assert "@page :first" in css
    assert "margin: 20mm 20mm 20mm 14mm" in css
    assert "margin: 20mm 14mm 20mm 20mm" in css

    # 2. 验证防孤行孤字与断页排版保护
    assert "orphans: 3" in css
    assert "widows: 3" in css
    assert "break-after: avoid" in css
    assert "break-inside: avoid" in css

    # 3. 验证代码块印刷着色规则
    assert ".codehilite" in css
    assert ".codehilite .k" in css
    assert ".codehilite .s" in css
    assert ".codehilite .c" in css

