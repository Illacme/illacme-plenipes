# -*- coding: utf-8 -*-
"""
前端脚本依赖拓扑与关键组件完整性自动化测试
确保 web/dashboard/index.html 中引入的所有 script 标签完整无遗漏、无 404、无孤儿组件。
"""
import os
import re

DASHBOARD_DIR = os.path.join(os.path.dirname(__file__), '..', 'web', 'dashboard')
INDEX_HTML_PATH = os.path.join(DASHBOARD_DIR, 'index.html')


def get_html_scripts():
    assert os.path.exists(INDEX_HTML_PATH), f"index.html not found at {INDEX_HTML_PATH}"
    with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
    # 提取所有 <script src="...">
    return re.findall(r'<script\s+[^>]*src=[\"\']([^\"\']+)[\"\']', html)


def test_index_html_scripts_exist_on_disk():
    """断言 index.html 中引入的所有脚本均物理存在于磁盘上 (0 个 404)"""
    scripts = get_html_scripts()
    assert len(scripts) > 0, "index.html 中未解析到任何 script 标签"

    missing = []
    for s in scripts:
        clean_s = s.split('?')[0]
        # 跳过 http/https 外部 CDN 脚本
        if clean_s.startswith('http://') or clean_s.startswith('https://') or clean_s.startswith('//'):
            continue
        file_path = os.path.join(DASHBOARD_DIR, clean_s)
        if not os.path.isfile(file_path):
            missing.append(f"{s} -> {file_path}")

    assert not missing, "发现 index.html 中引用的脚本在磁盘上不存在 (404):\n" + "\n".join(missing)


def test_no_orphaned_dashboard_js_files():
    """断言 web/dashboard/js 目录下的所有 JS 业务文件均被 index.html 引用 (0 个孤儿文件)"""
    scripts = get_html_scripts()
    imported_set = set(s.split('?')[0].replace('\\', '/') for s in scripts)

    orphaned = []
    js_root = os.path.join(DASHBOARD_DIR, 'js')
    assert os.path.exists(js_root), f"js directory not found at {js_root}"

    for root, dirs, files in os.walk(js_root):
        for f in files:
            if f.endswith('.js'):
                rel_path = os.path.relpath(os.path.join(root, f), DASHBOARD_DIR).replace('\\', '/')
                if rel_path not in imported_set:
                    orphaned.append(rel_path)

    assert not orphaned, (
        "发现磁盘上的 JS 文件未在 index.html 中被引入 (孤儿模块/漏引):\n" +
        "\n".join(orphaned) +
        "\n请在 web/dashboard/index.html 中按依赖顺序补齐 script 标签！"
    )


def test_critical_core_components_present():
    """断言系统核心模块（文库、插件、分发、多语言、算力、主题）的关键主引擎未被意外篡改抹除"""
    scripts = get_html_scripts()
    imported_set = set(s.split('?')[0].replace('\\', '/') for s in scripts)

    CRITICAL_MODULES = [
        # 文库核心
        'js/dashboard.vault.js',
        'js/vault/vault.list.js',
        'js/vault/vault.tree.js',
        'js/vault/vault.ops.js',
        'js/vault/vault.drawer.js',
        # 插件核心
        'js/dashboard.plugins.js',
        'js/plugins/plugins.editor.js',
        'js/plugins/plugins.platforms.js',
        'js/plugins/render_shards/plugins.render.badges.js',
        'js/plugins/render_shards/plugins.render.pod.js',
        'js/plugins/render_shards/plugins.render.physics.js',
        # 路由与多语言
        'js/route/route_shards/route.slug_render.js',
        'js/route/route_shards/route.slug_actions.js',
        'js/route/route.slug.sandbox.js',
        'js/route/route.render.js',
        'js/route/route.sync.js',
        'js/dashboard.localization.js',
        'js/localization/localization.render.js',
        'js/localization/localization.review.js',
        # 算力与系统
        'js/core/core.terminal.js',
        'js/core/core_shards/core.deploy_summary.js',
        'js/dashboard.compute.js',
        'js/dashboard.system.js',
        'js/dashboard.imprints.js',
        'js/dashboard.modes.js',
        'js/dashboard.guardrails.js',
        # 全局弹窗体系
        'js/ui/modal_shards/modals.system.js',
        'js/ui/modal_shards/modals.wizard_step3.js',
        'js/ui/modal_shards/modals.wizard_success.js',
        'js/ui/modals.js',
    ]

    missing_core = [mod for mod in CRITICAL_MODULES if mod not in imported_set]
    assert not missing_core, "关键核心业务引擎在 index.html 中缺失:\n" + "\n".join(missing_core)


def test_index_html_stylesheets_exist_on_disk():
    """断言 index.html 中引入的所有 CSS 样式表均物理存在于磁盘上 (0 个 404)"""
    assert os.path.exists(INDEX_HTML_PATH), f"index.html not found at {INDEX_HTML_PATH}"
    with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
    stylesheets = re.findall(r'<link\s+[^>]*href=[\"\']([^\"\']+\.css(?:\?[^\"\']*)?)[\"\']', html)
    assert len(stylesheets) > 0, "index.html 中未解析到任何 CSS link 标签"

    missing = []
    for s in stylesheets:
        clean_s = s.split('?')[0]
        if clean_s.startswith('http://') or clean_s.startswith('https://') or clean_s.startswith('//'):
            continue
        file_path = os.path.join(DASHBOARD_DIR, clean_s)
        if not os.path.isfile(file_path):
            missing.append(f"{s} -> {file_path}")

    assert not missing, "发现 index.html 中引用的样式表在磁盘上不存在 (404):\n" + "\n".join(missing)


def test_brand_flip_component_dom_parity():
    """断言左上角品牌 3D 翻牌组件的 DOM 拓扑、三段文案与亮色/暗色主题规则完备性"""
    assert os.path.exists(INDEX_HTML_PATH), f"index.html not found at {INDEX_HTML_PATH}"
    with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. 断言容器与 ID 存在
    assert 'class="brand-flip-wrapper"' in html, "缺少 .brand-flip-wrapper 容器"
    assert 'id="brand-title-flip"' in html, "缺少 #brand-title-flip 3D 翻牌视口"

    # 2. 断言三位一体核心文案完备
    assert "ILLACME" in html and "PLENIPES" in html, "缺少品牌主体与产品代号 (ILLACME PLENIPES)"
    assert "全球私人出版社" in html, "缺少主产品定位 (全球私人出版社)"
    assert "出版发行工作台" in html, "缺少当前工作台定位 (出版发行工作台)"

    # 3. 断言 CSS 样式存在并包含亮色模式专属适配
    css_path = os.path.join(DASHBOARD_DIR, 'css', 'components', 'brand.flip.css')
    assert os.path.isfile(css_path), f"brand.flip.css 不存在: {css_path}"
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    assert '[data-theme="light"]' in css_content, "brand.flip.css 缺少亮色模式 [data-theme='light'] 适配规则"
    assert '.brand-part-press' in css_content, "brand.flip.css 缺少全球私人出版社高光样式"
    assert '.brand-part-workbench' in css_content, "brand.flip.css 缺少出版发行工作台样式"

    # 4. 断言 JS 控制器存在且声明了 rotateBrandTitle
    js_path = os.path.join(DASHBOARD_DIR, 'js', 'ui', 'brand.flip.js')
    assert os.path.isfile(js_path), f"brand.flip.js 不存在: {js_path}"
    with open(js_path, 'r', encoding='utf-8') as f:
        js_content = f.read()
    assert "rotateBrandTitle" in js_content, "brand.flip.js 未暴露 rotateBrandTitle 函数"

