"""
📑 [V125.2] 多语平行对照装订与功能入口完整性测试
测试重点：
1. 多语对照模式下装订参数的正确收集 (主语言 + 平行对照栏)；
2. 未翻译章节/段落注入友好待译提示 (wb-poly-pending) 与原文参考，杜绝伪装成母语；
3. 生成的 EPUB 包含多语双栏/多栏平行对照 CSS 样式与分栏 DOM；
4. 前端组件在 Node.js 沙箱中的拓扑完备性与事件联动。
"""
import os
import subprocess
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
def setup_polyglot_vault(tmp_path_factory):
    vault = tmp_path_factory.mktemp("polyglot_vault")
    docs = vault / "Docs"
    docs.mkdir(parents=True, exist_ok=True)
    
    # 建立中文原稿
    ch1 = docs / "01_intro.md"
    ch1.write_text("---\ntitle: 系统导论\n---\n# 系统导论\n\n欢迎来到 Illacme Plenipes 系统。\n\n这是第二段内容，介绍核心功能架构。\n", encoding="utf-8")
    
    # 建立英文译文
    en_dir = vault / "en" / "Docs"
    en_dir.mkdir(parents=True, exist_ok=True)
    ch1_en = en_dir / "01_intro.md"
    ch1_en.write_text("---\ntitle: System Introduction\n---\n# System Introduction\n\nWelcome to Illacme Plenipes.\n\nThis is paragraph two.\n", encoding="utf-8")
    
    # 建立只有中文没有英文的第 2 篇
    ch2 = docs / "02_deep.md"
    ch2.write_text("---\ntitle: 深度原理\n---\n# 深度原理\n\n本章节探讨架构细节。\n", encoding="utf-8")
    
    return str(vault)


def test_polyglot_aligner_direct():
    """测试 PolyglotAligner 的块级对齐与未翻译友好提示注入"""
    from core.bindery.polyglot_aligner import PolyglotAligner
    
    # 模拟双语齐全的章节
    ch_zh = {"title": "系统导论", "html_body": "<p>欢迎来到系统。</p><p>这是第二段。</p>"}
    ch_en = {"title": "System Intro", "html_body": "<p>Welcome to system.</p><p>This is para 2.</p>"}
    
    res = PolyglotAligner.align_chapter_polyglot({"zh": ch_zh, "en": ch_en}, primary_lang="zh", ordered_langs=["zh", "en"])
    assert "wb-polyglot-block" in res["html_body"]
    assert "欢迎来到系统。" in res["html_body"]
    assert "Welcome to system." in res["html_body"]
    assert 'class="wb-lang-badge">ZH</span>' in res["html_body"]
    assert 'class="wb-lang-badge">EN</span>' in res["html_body"]
    
    # 模拟对照栏尚未翻译的章节
    ch_pending = {"title": "深度原理", "html_body": "<p>本章节探讨架构细节。</p>"}
    res_pending = PolyglotAligner.align_chapter_polyglot({"zh": ch_pending}, primary_lang="zh", ordered_langs=["zh", "en"])
    assert "wb-poly-pending" in res_pending["html_body"]
    assert "对照译文待生成" in res_pending["html_body"]
    assert "本章节探讨架构细节。" in res_pending["html_body"]


def test_build_polyglot_epub_api(client, setup_polyglot_vault, monkeypatch):
    """测试通过 /api/bindery/build 生成双语对照版 EPUB 电子书"""
    mock_engine = type("MockEngine", (), {
        "vault_root": setup_polyglot_vault,
        "site_name": "Polyglot Press",
        "author": "Polyglot Team"
    })()
    monkeypatch.setattr("services.api.routes.gov.bindery.get_global_engine", lambda: mock_engine)
    
    out_dir = os.path.abspath("dist/books")
    os.makedirs(out_dir, exist_ok=True)
    
    payload = {
        "format": "epub",
        "scope": "all",
        "polyglot_mode": True,
        "languages": ["zh", "en"],
        "title": "Bilingual Study Guide",
        "author": "Editorial Board",
        "cover_mode": "none"
    }
    
    res = client.post("/api/bindery/build", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data.get("success") is True
    fname = data.get("filename", "")
    assert fname.endswith(".epub")
    assert "zh-en" in fname or "polyglot" in fname
    
    fpath = os.path.join(out_dir, fname)
    assert os.path.isfile(fpath)
    assert os.path.getsize(fpath) > 0
    
    if os.path.exists(fpath):
        os.remove(fpath)


def test_polyglot_frontend_interaction_in_node():
    """在 Node.js 沙箱中验证多语对照前端 UI 交互与参数收集"""
    runner = """
    const fs = require('fs');
    global.window = global;
    global.document = {
        documentElement: { getAttribute: () => 'dark' },
        createElement: (tag) => ({ id: '', className: '', style: {}, appendChild: () => {}, innerHTML: '' }),
        body: { appendChild: () => {} },
        getElementById: (id) => null,
        querySelectorAll: () => []
    };

    require('./web/dashboard/js/vault/vault.bindery.templates.js');
    require('./web/dashboard/js/vault/vault.bindery.js');
    require('./web/dashboard/js/vault/vault.bindery.build.js');

    const tpl = window.BinderyTemplates;
    if (!tpl) throw new Error('BinderyTemplates 未挂载');

    const scopesData = {
        site_name: 'Test Press',
        default_author: 'Test Team',
        available_languages: [
            { code: 'zh', name: '简体中文', icon: '🇨🇳', count: 10, is_source: true },
            { code: 'en', name: 'English', icon: '🇬🇧', count: 8, is_source: false },
            { code: 'ja', name: '日本語', icon: '🇯🇵', count: 0, is_source: false }
        ],
        categories: [{ id: 'all', name: '全库' }]
    };

    const html = tpl.buildModalCardHtml(scopesData, 'all', '测试出版集');
    
    if (!html.includes('id="bindery-poly-chips-row"')) throw new Error('缺少 bindery-poly-chips-row');
    if (!html.includes('class="bindery-poly-cb"')) throw new Error('缺少 bindery-poly-cb 复选框');
    if (!html.includes('value="polyglot"')) throw new Error('缺少 polyglot 选项');

    console.log('POLYGLOT_FRONTEND_NODE_OK');
    """
    res = subprocess.run(['node', '-e', runner], capture_output=True, text=True)
    assert res.returncode == 0, f"Node 执行失败: {res.stderr}"
    assert "POLYGLOT_FRONTEND_NODE_OK" in res.stdout


def test_epub_reader_polyglot_dual_mode_support():
    """验证 EPUB 阅读器外壳正确集成多语分栏 CSS 与多语交互脚本，并支持卷轴/翻页双模"""
    from core.adapters.egress.ebook.epub_reader_template import build_epub_reader_shell
    from core.adapters.egress.ebook.epub_reader_polyglot_css import get_epub_polyglot_css
    from core.adapters.egress.ebook.epub_reader_polyglot_js import get_epub_reader_polyglot_js

    # 1. 验证多语 CSS 包含卷轴与翻页模式的分栏声明
    poly_css = get_epub_polyglot_css()
    assert ".er-polyglot-bar" in poly_css
    assert "body.wb-concordance .wb-polyglot-block" in poly_css
    assert "display: flex !important; flex-direction: row !important;" in poly_css
    assert '[data-read-mode="paginated"] body.wb-concordance .wb-polyglot-block' in poly_css
    assert "border-right: 1px dashed var(--border)" in poly_css

    # 2. 验证阅读器外壳模板完整注入了样式与脚本
    shell_html = build_epub_reader_shell("Polyglot Book", "<ol></ol>", "<div>正文</div>")
    assert ".er-polyglot-bar" in shell_html
    assert "initPolyglotBar" in shell_html

    # 3. 验证多语交互脚本在 Node 沙箱中的语法合法性
    poly_js = get_epub_reader_polyglot_js()
    runner = f"""
    global.window = global;
    global.document = {{
      readyState: 'complete',
      addEventListener: () => {{}},
      body: {{ classList: {{ toggle: () => {{}}, add: () => {{}}, remove: () => {{}} }} }},
      querySelector: () => null,
      querySelectorAll: () => []
    }};
    {poly_js}
    console.log('POLYGLOT_READER_JS_SYNTAX_OK');
    """
    res = subprocess.run(['node', '-e', runner], capture_output=True, text=True)
    assert res.returncode == 0, f"Node 执行失败: {res.stderr}"
    assert "POLYGLOT_READER_JS_SYNTAX_OK" in res.stdout


def test_epub_polyglot_cover_and_nav_generation(tmp_path):
    """验证多语对照装订时，封面与目录均以双栏 .wb-polyglot-block 结构输出，对照栏内容完备"""
    import zipfile
    from core.adapters.egress.ebook.epub import EpubAdapter

    cover_file = tmp_path / "cover.png"
    cover_file.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")

    tree = [{
        "title": "第一章 绪论",
        "titles_by_lang": {"zh": "第一章 绪论", "en": "Chapter 1 Introduction"},
        "headings": [{"title": "背景", "anchor": "bg", "level": 2}],
        "headings_by_lang": {
            "zh": [{"title": "背景", "anchor": "bg", "level": 2}],
            "en": [{"title": "Background", "anchor": "bg", "level": 2}]
        },
        "html_body": "<p>正文</p>"
    }]
    meta = {
        "title": "多语对照测试典籍",
        "author": "测试团队",
        "polyglot_langs": ["zh", "en"]
    }
    out_epub = str(tmp_path / "test_poly.epub")
    adapter = EpubAdapter()
    ok = adapter.bind_book(tree, meta, cover_image_path=str(cover_file), output_file_path=out_epub)
    assert ok is True

    with zipfile.ZipFile(out_epub, "r") as zf:
        cover_xhtml = zf.read("OEBPS/text/cover.xhtml").decode("utf-8")
        assert "wb-polyglot-block wb-polyglot-columns" in cover_xhtml
        assert 'data-lang="zh"' in cover_xhtml
        assert 'data-lang="en"' in cover_xhtml
        assert "Cover" in cover_xhtml or "cover" in cover_xhtml
        assert "cover_en.svg" in cover_xhtml
        assert "OEBPS/images/cover_en.svg" in zf.namelist()

        nav_xhtml = zf.read("OEBPS/nav.xhtml").decode("utf-8")
        assert "wb-polyglot-block wb-polyglot-columns" in nav_xhtml
        assert 'data-lang="zh"' in nav_xhtml
        assert 'data-lang="en"' in nav_xhtml
        assert "第一章 绪论" in nav_xhtml
        assert "Chapter 1 Introduction" in nav_xhtml
        assert "Background" in nav_xhtml


def test_epub_reader_polyglot_paging_in_node():
    """验证翻页模式下，多语对照支持章内多语协同整屏翻页，翻到底自动进入下一章"""
    from core.adapters.egress.ebook.epub_reader_polyglot_js import get_epub_reader_polyglot_js

    poly_js = get_epub_reader_polyglot_js()
    runner = f"""
    global.window = global;
    const mockCol = {{ clientHeight: 800, scrollHeight: 2400, scrollTop: 0 }};
    const mockCard = {{
      classList: {{ add: () => {{}}, remove: () => {{}} }},
      querySelectorAll: (sel) => [mockCol, {{ clientHeight: 800, scrollHeight: 2300, scrollTop: 0 }}]
    }};
    global.document = {{
      readyState: 'complete',
      addEventListener: () => {{}},
      body: {{ classList: {{ contains: (c) => c === 'wb-concordance', toggle: () => {{}}, add: () => {{}}, remove: () => {{}} }} }},
      documentElement: {{ getAttribute: (attr) => attr === 'data-read-mode' ? 'paginated' : '' }},
      getElementById: (id) => ({{ textContent: '', style: {{ width: '' }} }}),
      querySelector: () => null,
      querySelectorAll: (sel) => sel === '.er-chapter-card' ? [mockCard, {{ querySelectorAll: () => [] }}] : []
    }};
    global.getReaderCurPage = () => 0;

    {poly_js}

    if (typeof handlePolyglotPaging !== 'function') throw new Error('handlePolyglotPaging 未挂载');
    const handledFirstStep = handlePolyglotPaging(true);
    if (!handledFirstStep) throw new Error('首屏翻页应当在卷内协同翻页并拦截');
    if (mockCol.scrollTop <= 0) throw new Error('翻页目标位置异常: ' + mockCol.scrollTop);

    // 模拟已经到达本卷最后一页
    mockCard._subPage = 4;
    const handledSecondStep = handlePolyglotPaging(true);
    if (handledSecondStep) throw new Error('触底后再翻页应放行交由阅读器切入下一卷');

    console.log('POLYGLOT_PAGING_NODE_OK');
    """
    res = subprocess.run(['node', '-e', runner], capture_output=True, text=True)
    assert res.returncode == 0, f"Node 执行失败: {res.stderr}"
    assert "POLYGLOT_PAGING_NODE_OK" in res.stdout

