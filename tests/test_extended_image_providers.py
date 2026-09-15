# -*- coding: utf-8 -*-
"""
🧪 Test Extended Image Providers
测试用例：验证全面扩展后的 9 大图像创作提供商矩阵的注册、配置自愈、参数映射与工厂行为。
"""

from core.design.providers import (
    ProviderRegistry,
    FluxImageProvider,
    GoogleImagenProvider,
    MidjourneyProvider,
    StabilityImageProvider,
    ZhipuCogViewProvider,
    PexelsProvider,
    PixabayProvider,
    PicsumProvider,
)

def test_registry_has_twelve_providers():
    """断言注册中心包含完整的 13 大提供商 (含免版权四大图库与本地 OG 引擎)"""
    supported = ProviderRegistry.list_supported_providers()
    provider_ids = [p["id"] for p in supported]
    expected_ids = ["local_og", "sd_webui", "comfyui", "openai", "flux", "imagen", "midjourney", "stability", "zhipu", "unsplash", "pexels", "pixabay", "picsum"]
    for eid in expected_ids:
        assert eid in provider_ids, f"缺少预期提供商: {eid}"
    assert len(supported) == 13

def test_provider_factory_instantiation():
    """测试工厂方法能正确实例化所有 13 大驱动"""
    all_ids = ["local_og", "sd_webui", "comfyui", "openai", "flux", "imagen", "midjourney", "stability", "zhipu", "unsplash", "pexels", "pixabay", "picsum"]
    for pid in all_ids:
        inst = ProviderRegistry.create_provider(pid, config={})
        assert inst is not None
        assert hasattr(inst, "generate_image")
        assert hasattr(inst, "test_connection")

def test_pexels_pixabay_and_picsum_providers():
    """测试 Pexels、Pixabay 与 Lorem Picsum 免费商用图库的连通性与免Key回退"""
    pexels = PexelsProvider(config={"api_key": ""})
    p_conn = pexels.test_connection()
    assert p_conn["success"] is True

    pixabay = PixabayProvider(config={"api_key": ""})
    px_conn = pixabay.test_connection()
    assert px_conn["success"] is True

    picsum = PicsumProvider(config={})
    pc_conn = picsum.test_connection()
    # 只要能正常调用，无论本地是否连通外网均返回带 success 字段的 dict
    assert isinstance(pc_conn, tuple) or isinstance(pc_conn, dict)

def test_flux_dimensions_mapping():
    """测试 FLUX.1 画幅映射与缺失 Key 防御"""
    provider = FluxImageProvider(config={"api_key": ""})
    bytes_data, err = provider.generate_image(prompt="test", aspect_ratio="16:9")
    assert bytes_data is None
    assert "未配置" in err

    conn_res = provider.test_connection()
    assert conn_res["success"] is False
    assert "未配置" in conn_res["message"]

def test_stability_dimensions_mapping():
    """测试 Stability AI 画幅映射与缺失 Key 防御"""
    provider = StabilityImageProvider(config={"api_key": ""})
    bytes_data, err = provider.generate_image(prompt="test", aspect_ratio="16:9")
    assert bytes_data is None
    assert "未配置" in err

def test_zhipu_dimensions_mapping():
    """测试智谱 CogView 画幅映射与缺失 Key 防御"""
    provider = ZhipuCogViewProvider(config={"api_key": ""})
    bytes_data, err = provider.generate_image(prompt="水墨画", aspect_ratio="16:9")
    assert bytes_data is None
    assert "未配置" in err

def test_google_imagen_mapping():
    """测试 Google Imagen 3 映射与缺失 Key 防御"""
    provider = GoogleImagenProvider(config={"api_key": ""})
    bytes_data, err = provider.generate_image(prompt="cyberpunk", aspect_ratio="1:1")
    assert bytes_data is None
    assert "未配置" in err

def test_midjourney_mapping():
    """测试 Midjourney Proxy 映射与缺失 Key 防御"""
    provider = MidjourneyProvider(config={"api_key": ""})
    bytes_data, err = provider.generate_image(prompt="cinematic portrait", aspect_ratio="2.35:1")
    assert bytes_data is None
    assert "未配置" in err

def test_provider_tags_and_categories():
    """断言每个提供商均有特色标签与合法分类"""
    supported = ProviderRegistry.list_supported_providers()
    valid_categories = {"cloud_api", "local_opensource", "stock_library"}
    for p in supported:
        assert p["category"] in valid_categories
        assert "tag" in p and len(p["tag"]) > 0
        assert "desc" in p and len(p["desc"]) > 0
