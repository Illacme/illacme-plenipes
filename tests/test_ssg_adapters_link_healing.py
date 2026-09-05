#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - SSG Adapters Link Healing Test Suite
验证所有第三方 SSG 适配器对双链（Wikilinks）与相对链接自愈清洗能力的完备性。
"""

import pytest
from core.adapters.egress.ssg.base import BaseSSGAdapter
from adapters.egress.ssg.docusaurus import DocusaurusAdapter
from adapters.egress.ssg.vitepress import VitepressAdapter
from adapters.egress.ssg.starlight import StarlightAdapter
from adapters.egress.ssg.nextra import NextraAdapter
from adapters.egress.ssg.hugo import HugoAdapter
from adapters.egress.ssg.hexo import HexoAdapter


class ConcreteSSGAdapter(BaseSSGAdapter):
    def render(self, body, fm, seo_data=None, target_lang="zh", sub_path=""):
        return body, fm


def test_base_ssg_adapter_normalize_markdown_content():
    adapter = ConcreteSSGAdapter()
    
    # 模拟包含双链、带别名双链、锚点双链、html 后缀链接的 Markdown
    raw_markdown = """# 测试文档
欢迎阅读 [[guide|安装指南]]，系统架构请参考 [[architecture]]。
章节跳转：[[faq#q1|常见问题Q1]]。
普通相对链接自愈：[关于我们](./about.html)。
外部绝对链接不受影响：[GitHub](https://github.com/example/repo)。
"""
    healed = adapter.normalize_markdown_content(raw_markdown, sub_path="docs/intro.md", target_lang="zh")
    
    # 1. 断言不存在任何非法残留的 [[ 或 ]]
    assert "[[" not in healed
    assert "]]" not in healed
    
    # 2. 断言双链正确转换为标准 Markdown 语法
    assert "[安装指南](./guide.md)" in healed
    assert "[architecture](./architecture.md)" in healed
    assert "[常见问题Q1](./faq.md#q1)" in healed
    
    # 3. 断言 .html 被自愈为 .md 以契合 SPA 路由
    assert "[关于我们](./about.md)" in healed
    
    # 4. 断言外部链接未被误伤
    assert "[GitHub](https://github.com/example/repo)" in healed


@pytest.mark.parametrize("adapter_cls", [
    DocusaurusAdapter,
    VitepressAdapter,
    StarlightAdapter,
    NextraAdapter,
    HugoAdapter,
    HexoAdapter
])
def test_all_third_party_adapters_link_healing(adapter_cls):
    adapter = adapter_cls()
    raw_body = """# 页面内容
了解更多请点击 [[tutorial|新手教程]] 与 [[api/reference]]。
查看 [更新日志](./changelog.html)。
"""
    fm = {"title": "测试标题", "slug": "test-slug"}
    
    rendered_body, rendered_fm = adapter.render(
        raw_body,
        fm=fm,
        seo_data={"description": "SEO 描述", "keywords": "test,ssg"},
        target_lang="zh",
        sub_path="docs/test.md"
    )
    
    # 验证双链 100% 被清洗
    assert "[[" not in rendered_body
    assert "]]" not in rendered_body
    
    # 验证链接自愈
    if getattr(adapter, 'IS_CLEAN_URL', False):
        assert "[新手教程](/docs/tutorial/)" in rendered_body
        assert "[api/reference](/api/reference/)" in rendered_body
        assert "[更新日志](/docs/changelog/)" in rendered_body
    else:
        assert "[新手教程](./tutorial.md)" in rendered_body
        assert "[api/reference](./api/reference.md)" in rendered_body
        assert "[更新日志](./changelog.md)" in rendered_body
    
    # 验证 frontmatter 保留或注入成功
    assert rendered_fm["title"] in ("测试标题", "页面内容")
