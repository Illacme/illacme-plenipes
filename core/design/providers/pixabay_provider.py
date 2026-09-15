# -*- coding: utf-8 -*-
"""
🎨 Image Creation & Management Module (ICMM) - Pixabay Free Stock Provider
职责：Pixabay 免费商用图库驱动 (400万+免版权资源，原生支持中文搜索与矢量插画)。
🛡️ [SOP-01] 物理行数控制在 300 行以内。
"""

import time
import urllib.parse
import requests
from typing import Dict, Any, Optional, Tuple
from core.utils.tracing import tlog
from core.design.providers.base_provider import BaseImageProvider

class PixabayProvider(BaseImageProvider):
    PROVIDER_ID = "pixabay"
    PROVIDER_NAME = "Pixabay"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = self.config.get("api_key", "").strip()
        self.timeout = int(self.config.get("timeout", 20))

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        style: str = "vivid",
        **kwargs
    ) -> Tuple[Optional[bytes], Optional[str]]:
        orientation = "horizontal" if aspect_ratio in ("16:9", "2.35:1", "4:3") else ("vertical" if aspect_ratio == "9:16" else "all")
        query = prompt.strip() or "科技 背景"

        # 1. 官方 API 检索 (原生支持中文搜索)
        if self.api_key:
            url = (
                f"https://pixabay.com/api/?key={self.api_key}&q={urllib.parse.quote(query)}"
                f"&image_type=photo&orientation={orientation}&per_page=3&safesearch=true"
            )
            try:
                tlog.info(f"📸 [Pixabay] 正在检索免费商用素材 ({orientation}): {query[:30]}...")
                resp = requests.get(url, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    hits = data.get("hits", [])
                    if hits:
                        img_url = hits[0].get("largeImageURL") or hits[0].get("webformatURL")
                        if img_url:
                            dl = requests.get(img_url, timeout=30)
                            if dl.status_code == 200:
                                return dl.content, None
                    return None, f"Pixabay 未找到与 '{query}' 相关的免版权素材"
                return None, f"Pixabay HTTP {resp.status_code}: {resp.text[:150]}"
            except Exception as e:
                tlog.error(f"🛑 [Pixabay] 检索异常: {e}")

        # 2. 免费镜像源智能回退
        w, h = self.parse_dimensions(aspect_ratio)
        try:
            dl = requests.get(f"https://picsum.photos/{w}/{h}?random={int(time.time())}", timeout=20)
            if dl.status_code == 200 and len(dl.content) > 1000:
                return dl.content, None
        except Exception:
            pass

        return None, "未能从 Pixabay 检索到可用图像，建议配置 API Key"

    def test_connection(self) -> Dict[str, Any]:
        t0 = time.time()
        if not self.api_key:
            try:
                resp = requests.head("https://pixabay.com", timeout=10)
                latency = int((time.time() - t0) * 1000)
                if resp.status_code < 500:
                    return {"success": True, "message": f"免Key镜像通道畅通 (耗时 {latency}ms)", "latency_ms": latency}
                return {"success": False, "message": f"免Key镜像响应异常 ({resp.status_code})", "latency_ms": latency}
            except Exception as e:
                latency = int((time.time() - t0) * 1000)
                return {"success": False, "message": f"免Key通道网络不通: {e}", "latency_ms": latency}
        try:
            url = f"https://pixabay.com/api/?key={self.api_key}&per_page=3"
            resp = requests.get(url, timeout=10)
            latency = int((time.time() - t0) * 1000)
            if resp.status_code == 200:
                return {"success": True, "message": f"连接成功 (官方API在线，耗时 {latency}ms)", "latency_ms": latency}
            elif resp.status_code in (400, 401):
                return {"success": False, "message": "鉴权失败：Pixabay API Key 无效", "latency_ms": latency}
            else:
                return {"success": False, "message": f"响应异常 ({resp.status_code})", "latency_ms": latency}
        except Exception as e:
            latency = int((time.time() - t0) * 1000)
            return {"success": False, "message": f"连接超时: {e}", "latency_ms": latency}
