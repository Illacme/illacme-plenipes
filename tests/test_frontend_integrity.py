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
        # 路由与多语言
        'js/route/route.render.js',
        'js/route/route.sync.js',
        'js/dashboard.localization.js',
        'js/localization/localization.render.js',
        'js/localization/localization.review.js',
        # 算力与系统
        'js/dashboard.compute.js',
        'js/dashboard.system.js',
        'js/dashboard.imprints.js',
        'js/dashboard.modes.js',
        'js/dashboard.guardrails.js',
    ]

    missing_core = [mod for mod in CRITICAL_MODULES if mod not in imported_set]
    assert not missing_core, "关键核心业务引擎在 index.html 中缺失:\n" + "\n".join(missing_core)
