# -*- coding: utf-8 -*-
"""
🧪 Test Suite: Image Creation & Management Module (ICMM) & CoverEngine
验证：
1. 动态 OG 科技卡片渲染 (中英文自适应与多语种折行)；
2. 品牌母本图库算法合成与轮巡；
3. 极简文字首字母徽章渲染；
4. CoverResolver 策略路由与智能阶梯回退；
5. ImageHub 缓存落盘机制。
"""

import io
from PIL import Image
from core.design.cover_engine.og_card_renderer import render_og_card
from core.design.cover_engine.brand_presets_rotator import resolve_brand_preset_cover, generate_procedural_gradient
from core.design.cover_engine.minimal_badge_renderer import render_minimal_badge
from core.design.cover_engine.cover_resolver import CoverResolver
from core.design.image_hub import ImageHub

def test_og_card_renderer_chinese_and_english():
    """断言动态 OG 卡片在包含中文、英文与长标题时成功渲染合规图片"""
    long_title = "物理隔离架构与分发技术原理深入解析：从单例端口到物权账本闭环治理"
    data = render_og_card(
        title=long_title,
        author="Sovereign Architect",
        category="Architecture",
        aspect_ratio="16:9"
    )
    assert len(data) > 1000
    img = Image.open(io.BytesIO(data))
    assert img.format == "JPEG"
    assert img.size == (1200, 675)

def test_og_card_renderer_wechat_ratio():
    """断言微信公众号 2.35:1 比例能够正确生效 (900x383)"""
    data = render_og_card(
        title="微信公众号头条封面测试",
        aspect_ratio="2.35:1"
    )
    img = Image.open(io.BytesIO(data))
    assert img.size == (900, 383)

def test_brand_presets_rotator():
    """断言品牌母本轮巡与流体渐变合成"""
    data = generate_procedural_gradient(palette_idx=0, width=1200, height=675)
    img = Image.open(io.BytesIO(data))
    assert img.size == (1200, 675)

    cover1 = resolve_brand_preset_cover(doc_id="doc1", slug="slug1", offset=0)
    cover2 = resolve_brand_preset_cover(doc_id="doc1", slug="slug1", offset=1)
    assert len(cover1) > 500
    assert len(cover2) > 500
    # 不同 offset 生成不同色调底图
    assert cover1 != cover2

def test_minimal_badge_renderer():
    """断言极简文字徽章排版"""
    data_cn = render_minimal_badge(title="架构原理", aspect_ratio="16:9")
    img_cn = Image.open(io.BytesIO(data_cn))
    assert img_cn.size == (1200, 675)

    data_en = render_minimal_badge(title="Cloud Native Protocol", aspect_ratio="2.35:1")
    img_en = Image.open(io.BytesIO(data_en))
    assert img_en.size == (900, 383)

def test_cover_resolver_fallbacks():
    """断言 CoverResolver 策略解析与阶梯回退"""
    # 显式指定 og_card
    data_og, strat_og = CoverResolver.resolve_cover(title="Test", strategy="og_card")
    assert strat_og == "og_card"
    assert len(data_og) > 1000

    # 显式指定 presets
    data_p, strat_p = CoverResolver.resolve_cover(title="Test", strategy="brand_presets")
    assert strat_p == "brand_presets"
    assert len(data_p) > 500

    # 显式指定 minimal_badge
    data_b, strat_b = CoverResolver.resolve_cover(title="Test", strategy="minimal_badge")
    assert strat_b == "minimal_badge"
    assert len(data_b) > 500

    # auto 智能阶梯模式
    data_auto, strat_auto = CoverResolver.resolve_cover(title="Auto Fallback Test", strategy="auto")
    assert strat_auto in ("og_card", "brand_presets", "minimal_badge")
    assert len(data_auto) > 500

def test_image_hub_generation_and_caching(tmp_path):
    """断言 ImageHub 能为文档生成封面并落盘至指定缓存目录"""
    hub = ImageHub(vault_root=str(tmp_path), cache_dir=str(tmp_path / "covers"))
    rel_url, data, strat = hub.generate_cover_for_document(
        doc_id="Docs/architecture.md",
        title="架构全景",
        strategy="og_card"
    )
    assert rel_url.startswith("/api/design/assets/covers/")
    assert len(data) > 1000
    assert strat == "og_card"
    # 验证磁盘物理文件存在
    cached_files = list((tmp_path / "covers").glob("cover_*.jpg"))
    assert len(cached_files) == 1

def test_image_providers_registry_and_dimensions():
    """断言生图提供商注册表元数据完备且画幅尺寸计算精确"""
    from core.design.providers import ProviderRegistry, OpenAIDalleProvider, SDWebUIProvider, ComfyUIProvider, UnsplashProvider

    supported = ProviderRegistry.list_supported_providers()
    provider_ids = [p["id"] for p in supported]
    assert "openai" in provider_ids
    assert "sd_webui" in provider_ids
    assert "comfyui" in provider_ids
    assert "unsplash" in provider_ids

    # 实例创建与比例换算
    dalle = ProviderRegistry.create_provider("openai", {"api_key": "test_key"})
    assert isinstance(dalle, OpenAIDalleProvider)
    assert dalle.parse_dimensions("16:9") == (1792, 1024)
    assert dalle.parse_dimensions("1:1") == (1024, 1024)

    sd = ProviderRegistry.create_provider("sd_webui")
    assert isinstance(sd, SDWebUIProvider)

    comfy = ProviderRegistry.create_provider("comfyui")
    assert isinstance(comfy, ComfyUIProvider)

    unsplash = ProviderRegistry.create_provider("unsplash")
    assert isinstance(unsplash, UnsplashProvider)
    # 免 key 模式测试连接应为 success
    res = unsplash.test_connection()
    assert res["success"] is True

def test_image_provider_missing_key_behavior():
    """断言未配置 key 时的优雅降级与防御性拦截"""
    from core.design.providers import OpenAIDalleProvider
    provider = OpenAIDalleProvider({})
    res = provider.test_connection()
    assert res["success"] is False
    assert "未配置" in res["message"]
    img_bytes, err = provider.generate_image("A futuristic city")
    assert img_bytes is None
    assert "未配置" in err

def test_design_assets_apply_cover_to_markdown(tmp_path):
    """断言将媒体资产设为封面能够精确注入文档 frontmatter"""
    from services.api.routes.design_shards.design_assets_routes import apply_asset_as_cover, ApplyCoverRequest
    from core.utils.text import parse_frontmatter
    from unittest.mock import MagicMock, patch

    doc_file = tmp_path / "article_test.md"
    doc_file.write_text("---\ntitle: 测试文档\n---\n\n这是正文内容。\n", encoding="utf-8")

    mock_engine = MagicMock()
    mock_engine.vault_root = str(tmp_path)

    with patch("services.api.routes.design_shards.design_assets_routes.get_global_engine", return_value=mock_engine):
        import asyncio
        req = ApplyCoverRequest(doc_id="article_test.md", cover_url="/api/design/assets/covers/test.jpg")
        res = asyncio.run(apply_asset_as_cover(req))
        assert res["success"] is True

        updated_text = doc_file.read_text(encoding="utf-8")
        meta, body, _ = parse_frontmatter(updated_text)
        assert meta.get("cover") == "/api/design/assets/covers/test.jpg"
        assert meta.get("title") == "测试文档"
        assert "这是正文内容。" in body

def test_design_prompt_refinement():
    """断言意境提炼接口能够调用大模型并精确脱毒思维链标签"""
    from services.api.routes.design_shards.design_prompt_routes import refine_prompt, RefinePromptRequest
    from unittest.mock import MagicMock, patch
    import asyncio

    # 1. 模拟带思维链标签的大模型回复
    mock_engine = MagicMock()
    mock_adapter = MagicMock()
    mock_adapter.trans_cfg = {"temperature": 0.2, "max_tokens": 4096}
    mock_adapter.config = {"model": "test-model"}
    mock_adapter._intelligence_hub.get_intelligent_payload.return_value = {}
    mock_adapter.ask_ai_with_retry.return_value = (
        "<think>Let me craft an epic concept art prompt...</think>\n"
        "\"Cinematic concept art of distributed publishing network, neon data streams, dramatic lighting, 8k\""
    )
    mock_adapter.node_name = "mock_lmstudio"
    mock_engine.translator = mock_adapter

    with patch("services.api.routes.design_shards.design_prompt_routes.get_global_engine", return_value=mock_engine):
        req = RefinePromptRequest(prompt="分布式出版网络", style="cinematic")
        res = asyncio.run(refine_prompt(req))
        assert res["success"] is True
        assert "<think>" not in res["refined_prompt"]
        assert "distributed publishing network" in res["refined_prompt"]
        assert res["engine_used"] == "mock_lmstudio"

    # 2. 模拟无大模型时的保底机制
    with patch("services.api.routes.design_shards.design_prompt_routes.get_global_engine", return_value=None):
        req_fallback = RefinePromptRequest(prompt="赛博朋克空间站", style="cyberpunk")
        res_fb = asyncio.run(refine_prompt(req_fallback))
        assert res_fb["success"] is True
        assert "cyberpunk aesthetics" in res_fb["refined_prompt"]
        assert res_fb["engine_used"] == "heuristic_refiner"
def test_aspect_ratio_parsing():
    """断言 BaseImageProvider 对 2.35:1 与 3:4 等新增画幅的尺寸归一化解析"""
    from core.design.providers.base_provider import BaseImageProvider
    class DummyProvider(BaseImageProvider):
        async def generate_image(self, prompt, **kwargs): pass
        async def test_connection(self): pass

    p = DummyProvider()
    assert p.parse_dimensions("2.35:1") == (1920, 817)
    assert p.parse_dimensions("3:4") == (900, 1200)
    assert p.parse_dimensions("16:9") == (1792, 1024)
    assert p.parse_dimensions("1:1") == (1024, 1024)

def test_cleanup_idle_visual_assets(tmp_path):
    """断言安全清理闲置资产接口能够准确识别在用与闲置资产，绝对豁免保护在用资产"""
    import asyncio
    from unittest.mock import patch, MagicMock
    from services.api.routes.design_shards.design_assets_routes import cleanup_idle_assets

    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value = mock_cur
    # 模拟两张资产：一张闲置(id=1)，一张在用(id=2)
    mock_cur.fetchall.return_value = [
        (1, "/static/covers/idle_img.jpg"),
        (2, "/static/covers/used_img.jpg"),
    ]

    mock_engine = MagicMock()
    mock_engine.meta.sqlite.get_connection.return_value = mock_conn
    mock_engine.vault_root = str(tmp_path)

    # 在 tmp_path 下创建一个引用了 used_img.jpg 的 Markdown 文件
    article = tmp_path / "post.md"
    article.write_text("---\ntitle: 测试在用资产\ncover: /static/covers/used_img.jpg\n---\n内容正文", encoding="utf-8")

    with patch("services.api.routes.design_shards.design_assets_routes.get_global_engine", return_value=mock_engine):
        res = asyncio.run(cleanup_idle_assets())
        assert res["success"] is True
        assert res["cleaned_count"] == 1
        # 验证只对 id=1 (idle_img.jpg) 进行了数据库删除
        delete_calls = [c for c in mock_cur.execute.call_args_list if "DELETE FROM visual_assets" in str(c)]
        assert len(delete_calls) == 1
        assert "(1,)" in str(delete_calls[0])

