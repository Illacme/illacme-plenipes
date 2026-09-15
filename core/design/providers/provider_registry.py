# -*- coding: utf-8 -*-
"""
🎨 Image Creation & Management Module (ICMM) - Provider Registry & Gateway
职责：图像创作提供商注册表、凭证动态加载与连通性自愈校验。
🛡️ [SOP-01] 物理行数控制在 300 行以内。
"""

from typing import Dict, Any, Type, Optional, List
from core.utils.tracing import tlog
from core.design.providers.base_provider import BaseImageProvider
from core.design.providers.openai_dalle import OpenAIDalleProvider
from core.design.providers.sd_webui import SDWebUIProvider
from core.design.providers.comfyui import ComfyUIProvider
from core.design.providers.unsplash_provider import UnsplashProvider
from core.design.providers.flux_provider import FluxImageProvider
from core.design.providers.google_imagen import GoogleImagenProvider
from core.design.providers.midjourney_provider import MidjourneyProvider
from core.design.providers.stability_provider import StabilityImageProvider
from core.design.providers.zhipu_cogview import ZhipuCogViewProvider
from core.design.providers.pexels_provider import PexelsProvider
from core.design.providers.pixabay_provider import PixabayProvider
from core.design.providers.picsum_provider import PicsumProvider
from core.design.providers.local_og_provider import LocalOGProvider

class ProviderRegistry:
    """提供商注册中枢"""

    _PROVIDERS: Dict[str, Type[BaseImageProvider]] = {
        LocalOGProvider.PROVIDER_ID: LocalOGProvider,
        SDWebUIProvider.PROVIDER_ID: SDWebUIProvider,
        ComfyUIProvider.PROVIDER_ID: ComfyUIProvider,
        OpenAIDalleProvider.PROVIDER_ID: OpenAIDalleProvider,
        FluxImageProvider.PROVIDER_ID: FluxImageProvider,
        GoogleImagenProvider.PROVIDER_ID: GoogleImagenProvider,
        MidjourneyProvider.PROVIDER_ID: MidjourneyProvider,
        StabilityImageProvider.PROVIDER_ID: StabilityImageProvider,
        ZhipuCogViewProvider.PROVIDER_ID: ZhipuCogViewProvider,
        UnsplashProvider.PROVIDER_ID: UnsplashProvider,
        PexelsProvider.PROVIDER_ID: PexelsProvider,
        PixabayProvider.PROVIDER_ID: PixabayProvider,
        PicsumProvider.PROVIDER_ID: PicsumProvider,
    }


    @classmethod
    def list_supported_providers(cls) -> List[Dict[str, Any]]:
        """获取系统当前支持的生图驱动列表与元数据"""
        meta = [
            {
                "id": "local_og",
                "name": "极客排版 · 本地 OG 卡片",
                "category": "local_opensource",
                "icon": "🎨",
                "tag": "0Token / 极客排版 / 免Key",
                "desc": "基于 Pillow 的高质量中英文字体自适应排版引擎，支持暗夜科技极客风 (OG Card) 与极简微标渐变风，毫秒级纯离线生成",
                "fields": [
                    {"key": "brand_name", "label": "品牌徽标署名", "type": "text", "default": "ILLACME SOVEREIGN"},
                    {"key": "author", "label": "默认署名作者", "type": "text", "default": "Illacme Plenipes"},
                    {"key": "category", "label": "技术栏目分类", "type": "text", "default": "Engineering"}
                ]
            },
            {
                "id": "picsum",
                "name": "Lorem Picsum",
                "category": "stock_library",
                "icon": "🖼️",
                "tag": "极客占位 / 100%免Key / 自由尺寸",
                "desc": "全球公认免配置高清图库，零鉴权门槛，基于 Unsplash 社区摄影，支持任意尺寸与模糊/灰度滤镜",
                "fields": [
                    {"key": "base_url", "label": "服务地址 (可选自定义镜像)", "type": "text", "default": "https://picsum.photos"},
                    {"key": "grayscale", "label": "黑白艺术胶片风 (true/false)", "type": "text", "default": "false"},
                    {"key": "blur", "label": "背景虚化等级 (0-10, 适合文本背景)", "type": "text", "default": "0"}
                ]
            },
            {
                "id": "unsplash",
                "name": "Unsplash",
                "category": "stock_library",
                "icon": "📸",
                "tag": "艺术概念摄影 / 免版权",
                "desc": "极具美感与艺术调性的免版权摄影图库，胶片质感出众，支持语义匹配与免Key镜像检索",
                "fields": [
                    {"key": "access_key", "label": "Access Key (可选，留空走免Key镜像源)", "type": "password"}
                ]
            },
            {
                "id": "pexels",
                "name": "Pexels",
                "category": "stock_library",
                "icon": "🖼️",
                "tag": "Canva旗下 / 现代科技质感",
                "desc": "全球公认高质感免版权素材库，亚太CDN极速，现代科技与办公商务题材极佳",
                "fields": [
                    {"key": "api_key", "label": "Pexels API Key (可选，留空走免Key通道)", "type": "password"}
                ]
            },
            {
                "id": "pixabay",
                "name": "Pixabay",
                "category": "stock_library",
                "icon": "🎨",
                "tag": "中文原生搜索 / 插画矢量",
                "desc": "超400万免版权资源老牌图库，原生支持中文直接搜索，兼具摄影实拍与矢量插画",
                "fields": [
                    {"key": "api_key", "label": "Pixabay API Key (可选，留空走免Key通道)", "type": "password"}
                ]
            },
            {
                "id": "sd_webui",
                "name": "Stable Diffusion WebUI / Forge",
                "category": "local_opensource",
                "icon": "⚡",
                "tag": "本地开源旗舰 / 离线零成本",
                "desc": "本地开源旗舰工具，生态极广，支持 SDXL / SD 1.5 及其 LoRA 与微调模型",
                "fields": [
                    {"key": "base_url", "label": "服务地址 (含端口)", "type": "text", "default": "http://127.0.0.1:7860"},
                    {"key": "username", "label": "认证用户名 (可选)", "type": "text"},
                    {"key": "password", "label": "认证密码 (可选)", "type": "password"}
                ]
            },
            {
                "id": "comfyui",
                "name": "ComfyUI 节点引擎",
                "category": "local_opensource",
                "icon": "🧩",
                "tag": "节点工作流 / 极致轻量",
                "desc": "极客可视化工作流利器，显存开销小，速度极快，适合定制流水线",
                "fields": [
                    {"key": "base_url", "label": "ComfyUI 地址", "type": "text", "default": "http://127.0.0.1:8188"}
                ]
            },
            {
                "id": "openai",
                "name": "OpenAI DALL-E 3",
                "category": "cloud_api",
                "icon": "🤖",
                "tag": "顶级长Prompt理解",
                "desc": "云端顶级大模型，长句语义还原最精准，适合复杂意境画面与技术卡片",
                "fields": [
                    {"key": "api_key", "label": "API Key", "type": "password", "required": True},
                    {"key": "base_url", "label": "Base URL", "type": "text", "default": "https://api.openai.com/v1"},
                    {"key": "model", "label": "Model", "type": "text", "default": "dall-e-3"}
                ]
            },
            {
                "id": "flux",
                "name": "FLUX.1 (BFL / 硅基流动)",
                "category": "cloud_api",
                "icon": "🌊",
                "tag": "开源SOTA / 极速出图",
                "desc": "时代级文生图标杆，文字排版精准，手部与光影极为逼真，支持硅基流动高性价比API",
                "fields": [
                    {"key": "api_key", "label": "API Key", "type": "password", "required": True},
                    {"key": "base_url", "label": "Base URL", "type": "text", "default": "https://api.siliconflow.cn/v1"},
                    {"key": "model", "label": "Model", "type": "text", "default": "black-forest-labs/FLUX.1-schnell"}
                ]
            },
            {
                "id": "imagen",
                "name": "Google Imagen 3",
                "category": "cloud_api",
                "icon": "✨",
                "tag": "HDR摄影写实 / 文本渲染",
                "desc": "Google DeepMind 旗舰模型，真实光影追踪质感，画面细节与排版能力出众",
                "fields": [
                    {"key": "api_key", "label": "API Key (Gemini)", "type": "password", "required": True},
                    {"key": "base_url", "label": "Base URL", "type": "text", "default": "https://generativelanguage.googleapis.com/v1beta"},
                    {"key": "model", "label": "Model", "type": "text", "default": "gemini-2.5-flash-image"}
                ]
            },
            {
                "id": "midjourney",
                "name": "Midjourney Proxy",
                "category": "cloud_api",
                "icon": "🎨",
                "tag": "商业插画 / 艺术天花板",
                "desc": "全球公认的艺术调性巅峰，视觉张力极强，支持 Midjourney-Proxy 与中转网关",
                "fields": [
                    {"key": "api_key", "label": "API Key / Token", "type": "password", "required": True},
                    {"key": "base_url", "label": "Proxy Base URL", "type": "text", "default": "https://api.midjourney.com/v1"},
                    {"key": "model", "label": "Model (v6.1 / niji6)", "type": "text", "default": "v6.1"}
                ]
            },
            {
                "id": "stability",
                "name": "Stability AI (SD 3.5)",
                "category": "cloud_api",
                "icon": "🚀",
                "tag": "原厂旗舰 / SD3.5 Large",
                "desc": "Stability AI 官方云端服务，原汁原味 SD3.5 Large/Turbo，风格多样化",
                "fields": [
                    {"key": "api_key", "label": "API Key", "type": "password", "required": True},
                    {"key": "base_url", "label": "Base URL", "type": "text", "default": "https://api.stability.ai/v2beta/stable-image/generate"},
                    {"key": "model", "label": "Model", "type": "text", "default": "sd3.5-large"}
                ]
            },
            {
                "id": "zhipu",
                "name": "智谱清言 CogView-3",
                "category": "cloud_api",
                "icon": "🇨🇳",
                "tag": "原生中文理解 / 东方美学",
                "desc": "国内领先文生图模型，原生理解中文成语、古诗词意境与中国古典水墨国潮风格",
                "fields": [
                    {"key": "api_key", "label": "API Key", "type": "password", "required": True},
                    {"key": "base_url", "label": "Base URL", "type": "text", "default": "https://open.bigmodel.cn/api/paas/v4"},
                    {"key": "model", "label": "Model", "type": "text", "default": "cogview-3-plus"}
                ]
            }
        ]
        from core.design.providers.provider_config_manager import ProviderConfigManager
        saved_cfgs = ProviderConfigManager.get_all_configs(mask_secrets=True)
        for item in meta:
            pid = item["id"]
            cfg = saved_cfgs.get(pid, {})
            cat = item["category"]

            if pid in ("picsum", "local_og"):
                item["is_configured"] = True
                item["requires_credentials"] = False
                item["config_status"] = "out_of_box"
            elif cat == "cloud_api":
                item["requires_credentials"] = True
                api_key = str(cfg.get("api_key", "")).strip()
                is_valid = bool(api_key and not api_key.startswith("sk-mock"))
                item["is_configured"] = is_valid
                item["config_status"] = "configured" if is_valid else "unconfigured"
            elif cat == "local_opensource":
                item["requires_credentials"] = False
                base_url = str(cfg.get("base_url", "")).strip()
                is_valid = bool(base_url)
                item["is_configured"] = is_valid
                item["config_status"] = "configured" if is_valid else "unconfigured"
            elif cat == "stock_library":
                item["requires_credentials"] = False
                k = str(cfg.get("access_key") or cfg.get("api_key") or "").strip()
                is_valid = bool(k)
                item["is_configured"] = is_valid
                item["config_status"] = "configured" if is_valid else "optional_key"

            item["saved_config"] = cfg
        return meta

    @classmethod
    def create_provider(cls, provider_id: str, config: Optional[Dict[str, Any]] = None) -> Optional[BaseImageProvider]:
        """根据 ID 实例化驱动，若未显式传入 config 则自动装载持久化凭证"""
        provider_cls = cls._PROVIDERS.get(provider_id)
        if not provider_cls:
            tlog.warning(f"⚠️ [ProviderRegistry] 未知生图提供商: {provider_id}")
            return None
        if config is None:
            from core.design.providers.provider_config_manager import ProviderConfigManager
            config = ProviderConfigManager.get_provider_config(provider_id, mask_secrets=False)
        return provider_cls(config=config)

    @classmethod
    def test_provider_connection(cls, provider_id: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行指定驱动的连通性嗅探"""
        inst = cls.create_provider(provider_id, config)
        if not inst:
            return {"success": False, "message": f"提供商 {provider_id} 未注册", "latency_ms": 0}
        return inst.test_connection()
