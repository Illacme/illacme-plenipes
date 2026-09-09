# -*- coding: utf-8 -*-
"""
🧪 [Test] Docusaurus Internal Link Healing Test
职责：断言 Docusaurus 跨插件与同 docs 插件内部 Markdown 链接自愈能力，消除 404 断链与告警。
"""

import os
import tempfile
from core.adapters.egress.ssg.base_shards.docusaurus_i18n_synthesizer import DocusaurusI18nSynthesizer


def test_docusaurus_link_healing_internal_and_cross():
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. 模拟 docs 插件目录
        docs_dir = os.path.join(tmpdir, "docs")
        os.makedirs(docs_dir, exist_ok=True)
        doc_file = os.path.join(docs_dir, "index.md")
        with open(doc_file, "w", encoding="utf-8") as f:
            f.write("Welcome: [Quick Start](../docs/quick-start.md) and [Auth](./docs/auth.md)")

        # 2. 模拟 pages 插件目录
        pages_dir = os.path.join(tmpdir, "src", "pages")
        os.makedirs(pages_dir, exist_ok=True)
        page_file = os.path.join(pages_dir, "welcome.md")
        with open(page_file, "w", encoding="utf-8") as f:
            f.write("Intro: [Guide](../docs/guide.md), [Blog](../blog/post.md), [About](../about.md) and [WikiLinks](./wikilinks.md)")

        # 执行自愈
        DocusaurusI18nSynthesizer._heal_internal_links(tmpdir)

        # 断言 docs 内部链接已被纠正为同插件内的相对链接
        with open(doc_file, "r", encoding="utf-8") as f:
            doc_content = f.read()
            assert "[Quick Start](./quick-start.md)" in doc_content
            assert "[Auth](./auth.md)" in doc_content

        # 断言 pages 跨插件链接已被纠正为站内绝对路由
        with open(page_file, "r", encoding="utf-8") as f:
            page_content = f.read()
            assert "[Guide](/docs/guide)" in page_content
            assert "[Blog](/blog/post)" in page_content
            assert "[About](/about)" in page_content
            assert "**WikiLinks**" in page_content
