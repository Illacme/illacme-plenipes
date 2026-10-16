# -*- coding: utf-8 -*-
"""
🎨 Image Creation & Management Module (ICMM) - Local OG Card Provider
职责：本地免外部网络依赖、开箱即用的原生极客 OG 技术卡片与极简排版封面引擎。
特性：
1. 0 外部 API Key 与 0 Token 消耗，毫秒级纯本地离线渲染；
2. 基于 Pillow 高画质字体自适应折行算法与 60% 黄金排版安全区；
3. 支持暗夜科技极客风 (og_card) 与极简微标渐变风 (badge)。
🛡️ [SOP-01] 物理行数严格控制在 300 行以内。
"""

import time
from typing import Dict, Any, Optional, Tuple
from core.design.providers.base_provider import BaseImageProvider
from core.design.cover_engine.og_card_renderer import render_og_card
from core.design.cover_engine.minimal_badge_renderer import render_minimal_badge
from core.utils.tracing import tlog


class LocalOGProvider(BaseImageProvider):
    """本地原生排版 · 极客技术卡片驱动"""

    PROVIDER_ID = "local_og"
    PROVIDER_NAME = "本地原生排版 · 极客技术卡片"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.default_brand = (self.config.get("brand_name") or "ILLACME SOVEREIGN").strip()
        self.default_author = (self.config.get("author") or "Illacme Plenipes").strip()
        self.default_category = (self.config.get("category") or "Engineering").strip()
        self.render_mode = (self.config.get("mode") or "og_card").strip()

    @classmethod
    def sanitize_prompt_for_title(cls, prompt: str) -> str:
        """
        🛡️ 防御性清洗：将传入的生图意境描述或复杂 Prompt 清洗为卡片居中正规主标题。
        """
        if not prompt or not prompt.strip():
            return "Illacme Plenipes 技术出版"
        import re
        raw = prompt.strip()

        # 1. 优先提取书名号中的物理文章名
        book_match = re.search(r'[《<]([^》>]+)[》>]', raw)
        if book_match and book_match.group(1).strip():
            return book_match.group(1).strip()

        # 2. 匹配 "为文章 xxx 创作" 或 "文章 xxx：" 等前缀模式
        prefix_match = re.search(r'(?:为文章|关于文章|文章)\s*[:：]?\s*([^，。：\n]+)', raw)
        if prefix_match and prefix_match.group(1).strip():
            return prefix_match.group(1).strip()

        # 3. 剔除常见的 AI 生图意境词缀与风格修饰短语
        cleaned = raw
        ai_noise_patterns = [
            r'(?:，|。|、|\s)*(?:极简(?:现代)?科技意境|电影级光影(?:构图)?|8[kK](?:高清细节)?|现代装帧质感|视觉震撼|富有未来感|高分辨率|科技现代风格封面|创作科技现代风格封面|极简光影|masterpiece|best quality|photorealistic|cinematic lighting|8k resolution).*',
            r'^(?:为|生成|制作|创作).*?(?:封面|海报|插图)[，,：:\s]*',
        ]
        for pattern in ai_noise_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip("，。、：: ,.-_ \t\n")

        # 4. 若有多句（冒号/句号/换行隔开），提取核心第一段
        parts = re.split(r'[：:。\n]', cleaned)
        if parts and parts[0].strip():
            candidate = parts[0].strip()
            if len(candidate) <= 45:
                return candidate

        return cleaned[:40].strip() if cleaned else "Illacme Plenipes 技术出版"

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        style: str = "vivid",
        **kwargs
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        利用本地原生排版算法生成技术卡片封面
        """
        # 🛡️ 启用防御性清洗，提取纯净卡片标题
        title = self.sanitize_prompt_for_title(prompt)
        author = kwargs.get("author") or self.default_author
        category = kwargs.get("category") or self.default_category
        brand_name = kwargs.get("brand_name") or self.default_brand
        mode = "minimal_badge" if style in ("badge", "minimal") or self.render_mode == "minimal_badge" else "og_card"
        offset = int(kwargs.get("offset") or 0)

        try:
            start_t = time.time()
            if mode == "minimal_badge":
                data = render_minimal_badge(
                    title=title,
                    brand_name=brand_name,
                    aspect_ratio=aspect_ratio
                )
            else:
                data = render_og_card(
                    title=title,
                    author=author,
                    category=category,
                    brand_name=brand_name,
                    aspect_ratio=aspect_ratio,
                    offset=offset
                )
            cost_ms = int((time.time() - start_t) * 1000)
            if data:
                tlog.info(f"✨ [LocalOGProvider] 本地技术卡片排版完成: 《{title[:20]}》({aspect_ratio}, 耗时 {cost_ms}ms)")
                return data, None
            return None, "生成产物为空"
        except Exception as e:
            tlog.error(f"❌ [LocalOGProvider] 原生排版异常: {e}")
            return None, str(e)

    def test_connection(self) -> Dict[str, Any]:
        """测试本地引擎连通性与字体可用性"""
        start_t = time.time()
        try:
            test_data = render_og_card(
                title="Sovereignty Diagnostics",
                aspect_ratio="16:9"
            )
            latency = max(1, int((time.time() - start_t) * 1000))
            if test_data and len(test_data) > 0:
                return {
                    "success": True,
                    "message": "本地原生极客排版引擎就绪 (免Key离线运行)",
                    "latency_ms": latency
                }
            return {
                "success": False,
                "message": "本地排版测试输出为空",
                "latency_ms": latency
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"本地排版环境异常: {str(e)}",
                "latency_ms": int((time.time() - start_t) * 1000)
            }
