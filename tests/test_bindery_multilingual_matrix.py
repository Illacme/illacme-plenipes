# -*- coding: utf-8 -*-
"""
🌍 [V125.2] Test Suite for Multilingual E-Book Publication Matrix
测试目标：
1. /api/bindery/scopes 返回 available_languages 元数据与翻译统计
2. /api/bindery/build 矩阵并发装订模式（languages 数组参数）
3. 矩阵出版成果落盘命名规则与货架陈列
4. 容错与单语向下兼容机制
"""

import os
import shutil
import sqlite3
import pytest
from fastapi.testclient import TestClient

from services.api.server import app
from services.api.routes.system import verify_token


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[verify_token] = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(verify_token, None)


@pytest.fixture(scope="module")
def setup_multilingual_vault(tmp_path_factory):
    """构建支持多语种翻译缓存的沙箱文库"""
    base_dir = tmp_path_factory.mktemp("matrix_vault")
    docs_dir = base_dir / "Docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # 写入两篇源稿
    (docs_dir / "01_intro.md").write_text(
        "---\ntitle: 系统引言\norder: 1\n---\n# 系统引言\n这是第一章内容，欢迎阅读。\n",
        encoding="utf-8"
    )
    (docs_dir / "02_advanced.md").write_text(
        "---\ntitle: 进阶架构\norder: 2\n---\n# 进阶架构\n这是第二章内容，涉及系统架构。\n",
        encoding="utf-8"
    )

    # 构建 .plenipes/cache/ledger.db 模拟已有的翻译记录
    cache_dir = base_dir / ".plenipes" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    db_path = str(cache_dir / "ledger.db")
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                rel_path TEXT,
                lang_code TEXT,
                status TEXT,
                result_json TEXT,
                PRIMARY KEY (rel_path, lang_code)
            )
        """)
        conn.execute("INSERT INTO translations (rel_path, lang_code, status) VALUES ('Docs/01_intro.md', 'en', 'DONE')")
        conn.execute("INSERT INTO translations (rel_path, lang_code, status) VALUES ('Docs/02_advanced.md', 'en', 'DONE')")
        conn.execute("INSERT INTO translations (rel_path, lang_code, status) VALUES ('Docs/01_intro.md', 'ja', 'DONE')")
        conn.commit()

    return str(base_dir)


def test_scopes_returns_available_languages(client, setup_multilingual_vault, monkeypatch):
    """测试 /api/bindery/scopes 正确勘测到多语种元数据"""
    mock_engine = type("MockEngine", (), {
        "vault_root": setup_multilingual_vault,
        "site_name": "Matrix Press",
        "author": "Matrix Editor"
    })()
    monkeypatch.setattr("services.api.routes.gov.bindery.get_global_engine", lambda: mock_engine)

    res = client.get("/api/bindery/scopes")
    assert res.status_code == 200
    data = res.json()
    assert data.get("success") is True
    assert "available_languages" in data
    langs = data["available_languages"]
    assert len(langs) >= 3

    # 验证源语种
    zh = next((l for l in langs if l["code"] == "zh"), None)
    assert zh is not None
    assert zh["is_source"] is True

    # 验证翻译语种统计
    en = next((l for l in langs if l["code"] == "en"), None)
    assert en is not None
    assert en["count"] == 2

    ja = next((l for l in langs if l["code"] == "ja"), None)
    assert ja is not None
    assert ja["count"] == 1


def test_build_multilingual_matrix_epub(client, setup_multilingual_vault, monkeypatch):
    """测试 /api/bindery/build 矩阵并发批量装订 EPUB 丛书"""
    mock_engine = type("MockEngine", (), {
        "vault_root": setup_multilingual_vault,
        "site_name": "Matrix Press",
        "author": "Matrix Editor"
    })()
    monkeypatch.setattr("services.api.routes.gov.bindery.get_global_engine", lambda: mock_engine)

    out_dir = os.path.abspath("dist/books")
    os.makedirs(out_dir, exist_ok=True)

    payload = {
        "format": "epub",
        "scope": "all",
        "languages": ["zh", "en", "ja"],
        "title": "Matrix Test Series",
        "author": "Matrix Team",
        "cover_mode": "none"
    }

    res = client.post("/api/bindery/build", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data.get("success") is True
    assert data.get("mode") == "matrix"
    assert data.get("total_built") == 3
    results = data.get("results", [])
    assert len(results) == 3

    # 验证各个语种均独立生成了文件
    lang_codes = [r["language"] for r in results]
    assert "zh" in lang_codes
    assert "en" in lang_codes
    assert "ja" in lang_codes

    for r in results:
        fname = r["filename"]
        assert fname.endswith(".epub")
        fpath = os.path.join(out_dir, fname)
        assert os.path.isfile(fpath)
        assert r["chapter_count"] >= 1
        assert r["size_bytes"] > 0
        assert "download_url" in r

    # 验证货架接口中已包含这些矩阵产物
    shelf_res = client.get("/api/bindery/shelf")
    assert shelf_res.status_code == 200
    shelf_data = shelf_res.json()
    shelf_fnames = [b["filename"] for b in shelf_data.get("books", [])]
    for r in results:
        assert r["filename"] in shelf_fnames

    # 清理本次测试产物
    for r in data.get("results", []):
        p = os.path.join(out_dir, r.get("filename", ""))
        if os.path.exists(p):
            os.remove(p)


def test_build_multilingual_matrix_webbook(client, setup_multilingual_vault, monkeypatch):
    """测试 /api/bindery/build 矩阵并发批量装订 WebBook 网页书"""
    mock_engine = type("MockEngine", (), {
        "vault_root": setup_multilingual_vault,
        "site_name": "Matrix Press",
        "author": "Matrix Editor"
    })()
    monkeypatch.setattr("services.api.routes.gov.bindery.get_global_engine", lambda: mock_engine)

    out_dir = os.path.abspath("dist/books")
    os.makedirs(out_dir, exist_ok=True)

    payload = {
        "format": "webbook",
        "scope": "all",
        "languages": ["zh", "en"],
        "title": "Matrix WebBook Series",
        "author": "WebBook Team",
        "cover_mode": "none"
    }

    res = client.post("/api/bindery/build", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data.get("mode") == "matrix"
    assert data.get("total_built") == 2
    for r in data.get("results", []):
        assert r["filename"].endswith(".html")
        assert os.path.isfile(os.path.join(out_dir, r["filename"]))

    for r in data.get("results", []):
        p = os.path.join(out_dir, r.get("filename", ""))
        if os.path.exists(p):
            os.remove(p)


def test_translation_resolver_content_fidelity():
    """测试 TranslationResolver 真实提取目标语种标题与正文，杜绝母语混杂"""
    from core.bindery.translation_resolver import TranslationResolver
    TranslationResolver.reset_cache()

    # 1. 英文版正文与标题断言
    en_title, en_body = TranslationResolver.resolve_chapter(
        "about.md", "en", fallback_title="关于", fallback_body="母语中文正文", vault_dir="vault"
    )
    assert "About" in en_title
    assert "is dedicated to breaking down digital barriers" in en_body
    assert "母语中文正文" not in en_body

    # 2. 日文版正文与标题断言
    ja_title, ja_body = TranslationResolver.resolve_chapter(
        "about.md", "ja", fallback_title="关于", fallback_body="母语中文正文", vault_dir="vault"
    )
    assert "出版チーム" in ja_title
    assert "創作の自由" in ja_body
    assert "母语中文正文" not in ja_body


def test_bindery_shelf_filtering_and_rebind_js_integrity():
    """验证书架资产管理 JS 沙箱运行、格式胶囊过滤、关键词检索与 Re-bind 重新装订功能"""
    import subprocess
    runner = """
    const fs = require('fs');
    let shelfInner = '';
    global.window = {};
    global.document = {
        getElementById: (id) => {
            if (id === 'bindery-shelf-list') {
                return {
                    get innerHTML() { return shelfInner; },
                    set innerHTML(val) { shelfInner = val; }
                };
            }
            if (id === 'bindery-shelf-badge') return { textContent: '' };
            if (id === 'bindery-input-title') return { value: '' };
            if (id === 'bindery-select-lang') return { value: '', querySelector: () => ({ value: 'ja' }), dispatchEvent: () => {} };
            return null;
        }
    };
    global.Event = class {};
    eval(fs.readFileSync('web/dashboard/js/vault/vault.bindery.shelf.js', 'utf8'));

    if (typeof window.renderBinderyShelfHtml !== 'function') throw new Error('renderBinderyShelfHtml not registered');
    if (typeof window.setBinderyShelfFilter !== 'function') throw new Error('setBinderyShelfFilter not registered');
    if (typeof window.rebindBookFromShelf !== 'function') throw new Error('rebindBookFromShelf not registered');

    // 1. 模拟渲染带多格式的书架数据
    const mockBooks = [
        { filename: 'illacme-press-指南-zh.html', format: 'webbook', size_display: '120 KB', mtime: 1700000000, preview_url: '/preview/zh.html', download_url: '/dl/zh.html' },
        { filename: 'illacme-press-指南-en.epub', format: 'epub', size_display: '250 KB', mtime: 1700000000, preview_url: null, download_url: '/dl/en.epub' }
    ];
    window.renderBinderyShelfHtml(mockBooks);

    if (!shelfInner.includes('全部 (2)')) throw new Error('缺少 全部 (2) 筛选胶囊');
    if (!shelfInner.includes('网页书 (1)')) throw new Error('缺少 网页书 (1) 筛选胶囊');
    if (!shelfInner.includes('电子书 (1)')) throw new Error('缺少 电子书 (1) 筛选胶囊');
    if (!shelfInner.includes('🔄')) throw new Error('缺少 重新装订 🔄 按钮');
    if (!shelfInner.includes('window.rebindBookFromShelf')) throw new Error('缺少 rebindBookFromShelf 绑定');

    // 2. 格式过滤测试
    window.setBinderyShelfFilter('webbook');
    if (!shelfInner.includes('illacme-press-指南-zh.html')) throw new Error('WebBook 过滤应包含 html');
    if (shelfInner.includes('illacme-press-指南-en.epub')) throw new Error('WebBook 过滤不应包含 epub');

    // 3. 关键词过滤测试
    window.setBinderyShelfFilter('all');
    window.setBinderyShelfQuery('not_exist_book');
    if (!shelfInner.includes('未找到匹配的电子书')) throw new Error('未命中时应提示未找到匹配');

    console.log('SHELF_JS_INTEGRITY_OK');
    """
    res = subprocess.run(['node', '-e', runner], capture_output=True, text=True)
    assert res.returncode == 0, f"Node 执行失败: {res.stderr}"
    assert "SHELF_JS_INTEGRITY_OK" in res.stdout

