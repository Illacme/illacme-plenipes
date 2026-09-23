"""
tests/test_bindery_shelf_pagination.py
📚 出版典籍书架 (Bindery Shelf) 分页控制器回归测试套件
验证前端数据切片、翻页控制器、格式/搜索过滤自动重置以及独立装订构建执行模块完整性。
"""

import subprocess
import pytest


def test_bindery_shelf_pagination_in_node_sandbox():
    """在 Node 沙箱中全链路模拟验证书架分页逻辑与 DOM 拓扑"""
    runner = """
    const fs = require('fs');

    let shelfInner = '';
    const mockShelfList = {
        set innerHTML(val) { shelfInner = val; },
        get innerHTML() { return shelfInner; }
    };

    global.window = {
        apiFetch: null,
        fetch: null,
        showToast: () => {},
        document: {
            getElementById: (id) => {
                if (id === 'bindery-shelf-list') return mockShelfList;
                if (id === 'bindery-shelf-badge') return { textContent: '' };
                return null;
            }
        }
    };
    global.document = global.window.document;

    // 1. 加载书架管理模块
    eval(fs.readFileSync('web/dashboard/js/vault/vault.bindery.shelf.js', 'utf8'));

    if (typeof window.renderBinderyShelfHtml !== 'function') throw new Error('缺少 renderBinderyShelfHtml');
    if (typeof window.changeBinderyShelfPage !== 'function') throw new Error('缺少 changeBinderyShelfPage');
    if (window._binderyShelfPage !== 1) throw new Error('初始页码应为 1');
    if (window._binderyShelfPageSize !== 5) throw new Error('每页容量应默认为 5');

    // 2. 模拟注入 12 本已装订出版物
    const mockBooks = [];
    for (let i = 1; i <= 12; i++) {
        mockBooks.push({
            filename: `book-vol-${String(i).padStart(2, '0')}.epub`,
            format: 'epub',
            size_display: '1.2 MB',
            mtime: 1700000000 + i * 100,
            download_url: `/dl/book-${i}.epub`
        });
    }

    window.renderBinderyShelfHtml(mockBooks);

    // 验证第 1 页展示
    if (!shelfInner.includes('第 <span style="color:var(--accent, #10b981); font-weight:700;">1</span> / 3 页 · 共 <strong style="color:var(--text-bright, #fff);">12</strong> 本出版物')) {
        throw new Error('第 1 页分页状态栏渲染不符合预期');
    }
    if (!shelfInner.includes('book-vol-01.epub')) throw new Error('第 1 页应包含第 1 本');
    if (!shelfInner.includes('book-vol-05.epub')) throw new Error('第 1 页应包含第 5 本');
    if (shelfInner.includes('book-vol-06.epub')) throw new Error('第 1 页切片不应包含第 6 本');

    // 验证上一页在第 1 页时禁用
    if (!shelfInner.includes('disabled style="opacity:0.35; cursor:not-allowed; padding:3px 7px; font-size:0.72rem;"')) {
        throw new Error('第 1 页时上一页按钮应被禁用');
    }

    // 3. 翻至第 2 页
    window.changeBinderyShelfPage(2);
    if (!shelfInner.includes('第 <span style="color:var(--accent, #10b981); font-weight:700;">2</span> / 3 页')) {
        throw new Error('翻页后应为第 2 页');
    }
    if (shelfInner.includes('book-vol-05.epub')) throw new Error('第 2 页不应包含第 5 本');
    if (!shelfInner.includes('book-vol-06.epub')) throw new Error('第 2 页应包含第 6 本');
    if (!shelfInner.includes('book-vol-10.epub')) throw new Error('第 2 页应包含第 10 本');
    if (shelfInner.includes('book-vol-11.epub')) throw new Error('第 2 页不应包含第 11 本');

    // 4. 翻至尾页 (第 3 页)
    window.changeBinderyShelfPage(3);
    if (!shelfInner.includes('第 <span style="color:var(--accent, #10b981); font-weight:700;">3</span> / 3 页')) {
        throw new Error('翻页后应为第 3 页');
    }
    if (!shelfInner.includes('book-vol-11.epub')) throw new Error('第 3 页应包含第 11 本');
    if (!shelfInner.includes('book-vol-12.epub')) throw new Error('第 3 页应包含第 12 本');

    // 5. 格式筛选联动重置页码
    window.setBinderyShelfFilter('webbook');
    if (window._binderyShelfPage !== 1) throw new Error('切换过滤条件后页码应自动重置为 1');

    // 6. 搜索过滤联动重置页码
    window.changeBinderyShelfPage(2);
    window.setBinderyShelfQuery('vol-01');
    if (window._binderyShelfPage !== 1) throw new Error('搜索过滤后页码应自动重置为 1');

    console.log('SHELF_PAGINATION_ALL_TESTS_PASS');
    """
    res = subprocess.run(['node', '-e', runner], capture_output=True, text=True)
    assert res.returncode == 0, f"Node 执行失败: {res.stderr}"
    assert "SHELF_PAGINATION_ALL_TESTS_PASS" in res.stdout


def test_bindery_build_shard_syntax_and_registration():
    """验证独立拆分出来的 build shard 语法有效且函数已正确挂载"""
    runner = """
    const fs = require('fs');
    global.window = {};
    eval(fs.readFileSync('web/dashboard/js/vault/vault.bindery.build.js', 'utf8'));
    if (typeof window.executeBookBinding !== 'function') {
        throw new Error('executeBookBinding 未能正确注册在 window 上');
    }
    console.log('BINDERY_BUILD_SHARD_OK');
    """
    res = subprocess.run(['node', '-e', runner], capture_output=True, text=True)
    assert res.returncode == 0, f"Node 执行失败: {res.stderr}"
    assert "BINDERY_BUILD_SHARD_OK" in res.stdout
