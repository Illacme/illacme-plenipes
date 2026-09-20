#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Sovereign Imprint Bootstrapper
职责：为新划定的品牌文库注入标准资产目录与 6 种装帧模板特性演示手稿。
"""

import os
import datetime
from .imprint_showcase_content import (
    get_welcome_content,
    get_sovereign_doc,
    get_universal_doc,
    get_docusaurus_doc,
    get_starlight_doc,
    get_nextra_doc,
    get_vitepress_doc,
    get_about_doc,
)


def inject_template_showcase_manuscripts(vault_path: str, press_name: str = "默认出版空间"):
    """
    🌱 [V75.6] 为每种装帧模板生成中英双语演示手稿与资产目录结构，构建 3D 知识星系拓扑
    涵盖模板类型：
    1. sovereign: 官方旗舰
    2. universal: 通用自适应
    3. docusaurus: 知识库工程
    4. starlight: Astro 极星
    5. nextra: Next.js 极简
    6. vitepress: VitePress 疾速轻量
    """
    today_str = datetime.date.today().isoformat()

    # 1. 建立物理标准目录树
    blog_dir = os.path.join(vault_path, "Blog")
    docs_dir = os.path.join(vault_path, "Docs")
    pages_dir = os.path.join(vault_path, "Pages")
    images_dir = os.path.join(vault_path, "assets", "images")

    for d in [blog_dir, docs_dir, pages_dir, images_dir]:
        os.makedirs(d, exist_ok=True)

    with open(os.path.join(images_dir, ".gitkeep"), "w", encoding="utf-8") as f:
        f.write("")

    # 2. 生成中心创世手稿: welcome-to-illacme.md
    welcome_content = get_welcome_content(press_name, today_str)
    with open(os.path.join(vault_path, "welcome-to-illacme.md"), "w", encoding="utf-8") as f:
        f.write(welcome_content)
    with open(os.path.join(blog_dir, "welcome-to-illacme.md"), "w", encoding="utf-8") as f:
        f.write(welcome_content)

    # 3. 模板特性演示手稿
    showcase_files = [
        (os.path.join(docs_dir, "demo-sovereign.md"), get_sovereign_doc(today_str)),
        (os.path.join(docs_dir, "demo-universal.md"), get_universal_doc(today_str)),
        (os.path.join(docs_dir, "demo-docusaurus.md"), get_docusaurus_doc(today_str)),
        (os.path.join(docs_dir, "demo-starlight.md"), get_starlight_doc(today_str)),
        (os.path.join(docs_dir, "demo-nextra.md"), get_nextra_doc(today_str)),
        (os.path.join(docs_dir, "demo-vitepress.md"), get_vitepress_doc(today_str)),
        (os.path.join(pages_dir, "about.md"), get_about_doc(today_str)),
    ]

    for path, content in showcase_files:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
