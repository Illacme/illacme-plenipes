# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Test Suite for Plain Text (.txt) EBook Adapter & Endpoints
测试目标：
1. TxtBookAdapter 编译生成标准纯文本便携书实体 (.txt)
2. 验证纯文本版记、卷首框线、目录大纲与 Markdown 符号清洗
3. /api/bindery/scopes 动态发现注册 txt 格式
4. /api/bindery/shelf 货架扫描识别 txt 出版物
5. /api/bindery/view 与 /api/bindery/download 正确支持 .txt
6. /api/bindery/export-zip 批量归档打包包含 .txt 文件
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import zipfile
import pytest
from fastapi.testclient import TestClient

from services.api.server import app
from services.api.routes.system import verify_token
from core.adapters.egress.ebook import EBookRegistry
from core.adapters.egress.ebook.txt import TxtBookAdapter


@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[verify_token] = lambda: True
    yield TestClient(app)
    app.dependency_overrides.pop(verify_token, None)


def test_txt_adapter_registration():
    """测试 TxtBookAdapter 是否已被自动扫描发现并注册"""
    names = EBookRegistry.get_all_names()
    assert "txt" in names
    cls_ = EBookRegistry.get_adapter("txt")
    assert cls_ is TxtBookAdapter
    assert cls_.OUTPUT_EXTENSION == ".txt"
    assert "text/plain" in cls_.MIME_TYPE


def test_txt_book_adapter_generation(tmp_path):
    """测试 TxtBookAdapter 编译纯文本便携书排版结构"""
    adapter = TxtBookAdapter()
    out_file = tmp_path / "portable_book.txt"

    manuscript_tree = [
        {
            "id": "ch_1",
            "title": "极简数字出版",
            "slug": "minimal_press",
            "raw_body": (
                "# 第一节 纯文本之美\n\n"
                "纯文本格式是数字文明中最坚固耐用的信息载体。\n\n"
                "```python\n"
                "def hello():\n"
                "    print('Hello World')\n"
                "```\n\n"
                "> [!NOTE]\n"
                "> 引用块信息，适合阅读器墨水屏呈现。\n\n"
                "- 优点一：体积轻量\n"
                "- 优点二：极致便携\n"
                "1. 第一步：编排\n"
                "2. 第二步：装订\n"
            ),
            "headings": [{"title": "第一节 纯文本之美", "level": 2}],
            "assets": []
        }
    ]

    metadata = {
        "title": "纯文本便携典籍",
        "author": "Illacme Master",
        "publisher": "Illacme Global Press",
        "description": "专为低资源与墨水屏设备打造的纯文本典藏"
    }

    success = adapter.bind_book(
        manuscript_tree=manuscript_tree,
        book_metadata=metadata,
        target_lang="zh",
        output_file_path=str(out_file)
    )

    assert success is True
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")

    # 验证卷首扉页框线与元数据
    assert "《 纯文本便携典籍 》" in content
    assert "著 / 编  ：Illacme Master" in content
    assert "出  品   ：Illacme Global Press" in content

    # 验证目录大纲
    assert "【 目 录 大 纲 】" in content
    assert "01. 极简数字出版" in content
    assert "第一节 纯文本之美" in content

    # 验证章节格式化
    assert "第 01 章  极简数字出版" in content
    assert "--- [代码开始] ---" in content
    assert "def hello():" in content
    assert "• 优点一：体积轻量" in content


    # 验证出版版记
    assert "【 出 版 版 记 (Colophon) 】" in content
    assert "Illacme Plenipes Sovereign Digital Bindery Hub" in content


def test_api_bindery_txt_shelf_and_download(client, tmp_path, monkeypatch):
    """测试 /api/bindery 接口对 .txt 出版物的勘测、下载、阅览与打包"""
    books_dir = tmp_path / "dist" / "books"
    books_dir.mkdir(parents=True, exist_ok=True)

    txt_book = books_dir / "illacme-press-test.txt"
    txt_book.write_text("Hello Plain Text Book!\n", encoding="utf-8")

    original_cwd = os.getcwd()
    os.chdir(str(tmp_path))
    try:
        # 1. 勘测接口
        res_scopes = client.get("/api/bindery/scopes")
        assert res_scopes.status_code == 200
        fmts = [f["id"] for f in res_scopes.json()["formats"]]
        assert "txt" in fmts

        # 2. 书架接口
        res_shelf = client.get("/api/bindery/shelf")
        assert res_shelf.status_code == 200
        books = res_shelf.json()["books"]
        txt_items = [b for b in books if b["format"] == "txt"]
        assert len(txt_items) == 1
        assert txt_items[0]["filename"] == "illacme-press-test.txt"

        # 3. 在线阅览接口
        res_view = client.get("/api/bindery/view?file=illacme-press-test.txt")
        assert res_view.status_code == 200
        assert "text/plain" in res_view.headers["content-type"]
        assert "Hello Plain Text Book!" in res_view.text

        # 4. 下载接口
        res_dl = client.get("/api/bindery/download?file=illacme-press-test.txt")
        assert res_dl.status_code == 200
        assert "text/plain" in res_dl.headers["content-type"]

        # 5. ZIP 打包归档接口
        res_zip = client.post("/api/bindery/export-zip", json={"filenames": ["illacme-press-test.txt"]})
        assert res_zip.status_code == 200
        assert res_zip.headers["content-type"] == "application/zip"
    finally:
        os.chdir(original_cwd)
