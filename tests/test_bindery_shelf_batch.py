"""
tests/test_bindery_shelf_batch.py
📚 出版典籍书架 (Bindery Shelf) 批量管理与磁盘占用感知回归测试套件
验证后端批量删除 API、物理磁盘总容量统计以及前端 Node 沙箱批量管理交互。
"""

import os
import subprocess
import pytest
from fastapi.testclient import TestClient
from services.api.server import app
from services.api.routes.system import verify_token


@pytest.fixture
def auth_client():
    app.dependency_overrides[verify_token] = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(verify_token, None)


def test_bindery_shelf_total_disk_size_and_batch_delete(auth_client, tmp_path):
    """验证书架磁盘总容量统计与批量安全删除 API"""
    books_dir = os.path.abspath("dist/books")
    os.makedirs(books_dir, exist_ok=True)

    test_file_1 = os.path.join(books_dir, "pytest-batch-test-01.epub")
    test_file_2 = os.path.join(books_dir, "pytest-batch-test-02.html")
    with open(test_file_1, "wb") as f:
        f.write(b"0" * 2048)  # 2 KB
    with open(test_file_2, "wb") as f:
        f.write(b"0" * 4096)  # 4 KB

    try:
        # 1. 验证获取书架与磁盘总容量
        res = auth_client.get("/api/bindery/shelf")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "total_size_bytes" in data
        assert "total_size_display" in data
        assert data["total_size_bytes"] >= 6144

        # 2. 验证批量删除 API
        del_res = auth_client.post("/api/bindery/delete", json={
            "filenames": ["pytest-batch-test-01.epub", "pytest-batch-test-02.html"]
        })
        assert del_res.status_code == 200
        del_data = del_res.json()
        assert del_data["success"] is True
        assert del_data["count"] == 2
        assert not os.path.exists(test_file_1)
        assert not os.path.exists(test_file_2)

        # 3. 验证空参数防御拦截
        err_res = auth_client.post("/api/bindery/delete", json={})
        assert err_res.status_code == 400

    finally:
        for p in [test_file_1, test_file_2]:
            if os.path.exists(p):
                os.remove(p)


def test_bindery_shelf_batch_mode_in_node_sandbox():
    """在 Node 沙箱中全链路模拟验证书架批量管理模式与选择状态"""
    runner = """
    const fs = require('fs');

    let shelfInner = '';
    let headerActionsInner = '';
    const mockShelfList = {
        set innerHTML(val) { shelfInner = val; },
        get innerHTML() { return shelfInner; }
    };
    const mockHeaderActions = {
        set innerHTML(val) { headerActionsInner = val; },
        get innerHTML() { return headerActionsInner; }
    };

    global.window = {
        apiFetch: null,
        fetch: null,
        showToast: () => {},
        document: {
            getElementById: (id) => {
                if (id === 'bindery-shelf-list') return mockShelfList;
                if (id === 'bindery-shelf-header-actions') return mockHeaderActions;
                if (id === 'bindery-shelf-badge') return { textContent: '' };
                return null;
            }
        }
    };
    global.document = global.window.document;

    eval(fs.readFileSync('web/dashboard/js/vault/vault.bindery.shelf.js', 'utf8'));

    // 1. 模拟注入出版物与总容量
    const mockBooks = [
        { filename: 'book-batch-01.epub', format: 'epub', size_display: '1.2 MB', mtime: 1700000000, download_url: '/dl/1' },
        { filename: 'book-batch-02.html', format: 'webbook', size_display: '500 KB', mtime: 1700000001, download_url: '/dl/2', preview_url: '/pv/2' }
    ];
    window._binderyShelfTotalSize = '1.7 MB';
    window.renderBinderyShelfHtml(mockBooks);

    if (!headerActionsInner.includes('💾 占用 1.7 MB')) {
        throw new Error('未能在 Tab 头部右侧渲染磁盘占用总容量');
    }
    if (!headerActionsInner.includes('☑️ 批量管理')) {
        throw new Error('未能在 Tab 头部右侧渲染批量管理按钮');
    }

    // 2. 开启批量管理模式
    window.toggleBinderyShelfBatchMode();
    if (!window._binderyShelfBatchMode) throw new Error('批量模式切换失败');
    if (!headerActionsInner.includes('✖️ 退出批量')) throw new Error('批量激活态按钮未更新');
    if (!shelfInner.includes('☑️ 全选/取消当前页')) throw new Error('缺少全选当前页操作');
    if (!shelfInner.includes('type="checkbox"')) throw new Error('卡片中缺少多选框');

    // 3. 勾选第一本书
    window.toggleBinderyShelfSelect('book-batch-01.epub', true);
    if (!window._binderyShelfSelected.has('book-batch-01.epub')) throw new Error('单选勾选失败');
    if (!shelfInner.includes('已选 <strong style="color:var(--accent, #10b981);">1</strong> 本')) {
        throw new Error('已选计数显示不正确');
    }
    if (!shelfInner.includes('批量清理 (1)')) throw new Error('批量清理按钮文案未带计数');

    // 4. 当前页全选
    window.toggleAllBinderyShelfSelect(['book-batch-01.epub', 'book-batch-02.html']);
    if (window._binderyShelfSelected.size !== 2) throw new Error('当前页全选计数应为 2');

    // 5. 退出批量模式
    window.toggleBinderyShelfBatchMode();
    if (window._binderyShelfBatchMode) throw new Error('应已退出批量模式');
    if (window._binderyShelfSelected.size !== 0) throw new Error('退出批量模式应清空选中集合');

    console.log('BINDERY_BATCH_SHELF_OK');
    """
    res = subprocess.run(['node', '-e', runner], capture_output=True, text=True)
    assert res.returncode == 0, f"Node 执行失败: {res.stderr}"
    assert "BINDERY_BATCH_SHELF_OK" in res.stdout
