#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 Frontmatter YAML 物理自愈修复器单元测试套件
"""
import pytest
from core.utils.yaml_healer import FrontmatterHealer
from core.utils.text import parse_frontmatter
from core.utils.common import extract_frontmatter

def test_normal_yaml():
    yaml_str = """
title: Standard Title
description: Standard Description
tags: [dev, python]
"""
    res = FrontmatterHealer.heal_and_parse_yaml(yaml_str)
    assert res["title"] == "Standard Title"
    assert res["tags"] == ["dev", "python"]

def test_unclosed_quote_yaml():
    yaml_str = """
title: "Unclosed Title String
description: 'Unclosed Description
"""
    res = FrontmatterHealer.heal_and_parse_yaml(yaml_str)
    assert "title" in res
    assert "description" in res

def test_unquoted_colon_yaml():
    yaml_str = """
title: Guide: How to build a blog
description: Notice: important note
"""
    res = FrontmatterHealer.heal_and_parse_yaml(yaml_str)
    assert res["title"] == "Guide: How to build a blog"
    assert res["description"] == "Notice: important note"

def test_tab_indent_yaml():
    yaml_str = "title: Tab Test\n\ttags: [a, b]\n"
    res = FrontmatterHealer.heal_and_parse_yaml(yaml_str)
    assert res["title"] == "Tab Test"

def test_damaged_frontmatter_integration():
    raw_md = """---
title: Broken: Frontmatter Example
description: "Missing closing quote
tags: [test, healer]
---

# Hello World Body
This is the body content.
"""
    meta, body, has_fm = parse_frontmatter(raw_md)
    assert has_fm is True
    assert meta.get("title") == "Broken: Frontmatter Example"
    assert "Hello World Body" in body

def test_extract_frontmatter_healed():
    raw_md = """---
title: Damaged: Title
---
Content Body
"""
    meta, body = extract_frontmatter(raw_md)
    assert meta.get("title") == "Damaged: Title"
    assert "Content Body" in body
