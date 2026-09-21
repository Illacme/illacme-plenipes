# -*- coding: utf-8 -*-
"""
🧪 [V107.8] 原稿文库列表与实时预览路径对齐及服务唤醒测试
职责：验证前端统一路径推演算子及列表页与预览路径对齐逻辑，杜绝路径断层与 404。
"""

import subprocess


def test_doc_url_path_calculation_in_sandbox():
    """验证 Node.js 沙箱环境下 calculateDocUrlPath 的三模态正确推演"""
    node_script = """
    const fs = require('fs');
    const vm = require('vm');

    const editorCode = fs.readFileSync('web/dashboard/js/vault/vault.editor.js', 'utf8');
    const listCode = fs.readFileSync('web/dashboard/js/vault/vault.list.js', 'utf8');

    const mockWindow = {
        settingsData: {
            translation: { slug_dir_mode: 'nested' },
            system: { serve_port: 43213 }
        },
        activeDocId: 'Docs/quick-start.md'
    };
    const mockDocument = {
        getElementById: () => ({ value: 'quick-start', innerText: '', classList: { contains: () => false, add: () => {}, remove: () => {} }, addEventListener: () => {} }),
        querySelectorAll: () => [],
        addEventListener: () => {}
    };

    const sandbox = {
        window: mockWindow,
        document: mockDocument,
        setTimeout: () => {},
        localStorage: { getItem: () => null },
        apiFetch: async () => ({ items: [], total: 0 }),
        console: console
    };

    vm.createContext(sandbox);
    vm.runInContext(editorCode, sandbox);
    vm.runInContext(listCode, sandbox);

    // 1. 测试 nested 目录树复刻
    const nestedRes = sandbox.window.calculateDocUrlPath('Docs/quick-start.md', 'quick-start');
    if (nestedRes.path !== 'docs/quick-start.html') {
        process.stderr.write(`Expected docs/quick-start.html, got ${nestedRes.path}`);
        process.exit(1);
    }

    // 2. 测试 flat 极简根目录
    sandbox.window.settingsData.translation.slug_dir_mode = 'flat';
    const flatRes = sandbox.window.calculateDocUrlPath('Docs/quick-start.md', 'quick-start');
    if (flatRes.path !== 'quick-start.html') {
        process.stderr.write(`Expected quick-start.html, got ${flatRes.path}`);
        process.exit(1);
    }

    // 3. 测试 prefix 智能前缀
    sandbox.window.settingsData.translation.slug_dir_mode = 'prefix';
    const prefixRes = sandbox.window.calculateDocUrlPath('Docs/quick-start.md', 'quick-start');
    if (prefixRes.path !== 'docs-quick-start.html') {
        process.stderr.write(`Expected docs-quick-start.html, got ${prefixRes.path}`);
        process.exit(1);
    }

    // 4. 测试全局主页与频道主页
    sandbox.window.settingsData.translation.slug_dir_mode = 'nested';
    const homeRes = sandbox.window.calculateDocUrlPath('index.md', 'index');
    if (homeRes.path !== 'index.html') {
        process.stderr.write(`Expected index.html, got ${homeRes.path}`);
        process.exit(1);
    }

    process.exit(0);
    """
    res = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
    assert res.returncode == 0, f"Node sandbox failed: {res.stderr}"


def test_file_line_limits_and_syntax():
    """验证文件未超 300 行且语法通过 V8 编译"""
    target_files = [
        "web/dashboard/js/vault/vault.editor.js",
        "web/dashboard/js/vault/vault.list.js",
        "web/dashboard/js/galaxy/galaxy.hud.director.js",
        "web/dashboard/js/vault/drawer_shards/vault.drawer.lifecycle.js",
        "web/dashboard/js/editorial/syndicate_shards/syndicate.render.js",
        "web/dashboard/js/design/design_shards/design.doc_cover_modal.js",
    ]
    for file_path in target_files:
        compile_res = subprocess.run(["node", "-c", file_path], capture_output=True, text=True)
        assert compile_res.returncode == 0, f"Syntax error in {file_path}: {compile_res.stderr}"

        with open(file_path, "r", encoding="utf-8") as f:
            lines = len(f.readlines())
        assert lines <= 300, f"{file_path} exceeds 300 lines (current: {lines})"


def test_galaxy_director_feature_parity_and_focus_restore():
    """验证星球控制仪全功能矩阵接入及弹窗关闭后自动恢复 3D 聚焦对齐"""
    node_script = """
    const fs = require('fs');
    const vm = require('vm');

    const directorCode = fs.readFileSync('web/dashboard/js/galaxy/galaxy.hud.director.js', 'utf8');
    const editorCode = fs.readFileSync('web/dashboard/js/vault/vault.editor.js', 'utf8');
    const drawerCode = fs.readFileSync('web/dashboard/js/vault/drawer_shards/vault.drawer.lifecycle.js', 'utf8');
    const syndicateCode = fs.readFileSync('web/dashboard/js/editorial/syndicate_shards/syndicate.render.js', 'utf8');

    let focusedNode = null;
    const mockWindow = {
        currentView: 'overview',
        focusNodeIn3D: (n) => { focusedNode = n; },
        openEditor: () => {},
        openArticleLivePreview: () => {},
        openArticleSyndicationDrawer: () => {},
        openVaultDrawer: () => {},
        settingsData: { system: { serve_port: 43213 } },
        apiFetch: async () => ({ word_count: 500, gist: '测试摘要', entities: ['实体A'], frontmatter: {} })
    };

    const domElements = {};
    const createElement = (tag) => ({
        tagName: tag,
        style: {},
        classList: { contains: () => false, add: () => {}, remove: () => {}, toggle: () => {} },
        innerText: '',
        innerHTML: '',
        appendChild: () => {},
        addEventListener: () => {}
    });

    const mockDocument = {
        getElementById: (id) => {
            if (!domElements[id]) {
                domElements[id] = createElement('div');
                domElements[id].id = id;
            }
            return domElements[id];
        },
        createElement,
        querySelectorAll: () => [],
        addEventListener: () => {}
    };
    domElements['galaxy-right-column'] = { appendChild: (c) => { domElements[c.id] = c; } };

    const sandbox = {
        window: mockWindow,
        document: mockDocument,
        setTimeout: (fn) => fn(),
        setInterval: () => 1,
        clearInterval: () => {},
        localStorage: { removeItem: () => null, getItem: () => null },
        apiFetch: mockWindow.apiFetch,
        console: console
    };

    vm.createContext(sandbox);
    vm.runInContext(directorCode, sandbox);
    vm.runInContext(editorCode, sandbox);
    vm.runInContext(drawerCode, sandbox);
    vm.runInContext(syndicateCode, sandbox);

    async function run() {
        sandbox.window.injectGalaxyDirectorDOM();
        const testNode = { id: 'Docs/guide.md', title: '快速指南', slug: 'guide' };
        await sandbox.window.showNodeDirector(testNode);

        // 断言激活节点被追踪
        if (sandbox.window._activeGalaxyNode?.id !== 'Docs/guide.md') process.exit(1);

        // 模拟编辑点击
        const editBtn = sandbox.document.getElementById('node-dir-btn-edit');
        if (!editBtn.onclick) process.exit(2);
        editBtn.onclick();

        // 验证关闭编辑器后自动恢复
        sandbox.window.closeEditor();
        if (focusedNode?.id !== 'Docs/guide.md') process.exit(3);

        // 验证关闭独立站发布抽屉后自动恢复
        focusedNode = null;
        sandbox.window.closeVaultDrawer();
        if (focusedNode?.id !== 'Docs/guide.md') process.exit(4);

        // 验证关闭推流抽屉后自动恢复
        focusedNode = null;
        sandbox.window.closeArticleSyndicationDrawer();
        if (focusedNode?.id !== 'Docs/guide.md') process.exit(5);

        process.exit(0);
    }
    run().catch(() => process.exit(9));
    """
    res = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
    assert res.returncode == 0, f"Galaxy director test failed (exit {res.returncode}): {res.stderr}"
