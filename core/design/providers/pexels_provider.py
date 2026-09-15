# -*- coding: utf-8 -*-
"""
🎨 Image Creation & Management Module (ICMM) - Pexels Free Stock Provider
职责：Pexels 高清摄影图库驱动 (Canva 旗下，100% 免费商用免版权素材)。
🛡️ [SOP-01] 物理行数控制在 300 行以内。
"""

import time
import urllib.parse
import requests
from typing import Dict, Any, Optional, Tuple
from core.utils.tracing import tlog
from core.design.providers.base_provider import BaseImageProvider

class PexelsProvider(BaseImageProvider):
    PROVIDER_ID = "pexels"
    PROVIDER_NAME = "Pexels"

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
        orientation = "landscape" if aspect_ratio in ("16:9", "2.35:1", "4:3") else ("portrait" if aspect_ratio == "9:16" else "square")
        query = prompt.strip() or "nature landscape technology"

        # 1. 官方 API 检索
        if self.api_key:
            url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=1&orientation={orientation}"
            headers = {"Authorization": self.api_key}
            try:
                tlog.info(f"📸 [Pexels] 正在检索免费商用摄影 ({orientation}): {query[:30]}...")
                resp = requests.get(url, headers=headers, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    photos = data.get("photos", [])
                    if photos:
                        img_url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("large")
                        if img_url:
                            dl = requests.get(img_url, timeout=30)
                            if dl.status_code == 200:
                                return dl.content, None
                    return None, f"Pexels 未找到关于 '{query}' 的免版权图片"
                return None, f"Pexels HTTP {resp.status_code}: {resp.text[:150]}"
            except Exception as e:
                tlog.error(f"🛑 [Pexels] 检索异常: {e}")

        # 2. 免费镜像源回退检索 (无需 API Key)
        w, h = self.parse_dimensions(aspect_ratio)
        mirror_url = f"https://images.pexels.com/photos/random?w={w}&h={h}&fit=crop"
        try:
            dl = requests.get(f"https://loremflickr.com/{w}/{h}/{urllib.parse.quote(query)}", timeout=20)
            if dl.status_code == 200 and len(dl.content) > 1000:
                return dl.content, None
        except Exception:
            pass

        return None, "未能从 Pexels 检索到可用图像，建议配置 API Key"

    def test_connection(self) -> Dict[str, Any]:
        t0 = time.time()
        if not self.api_key:
            try:
                resp = requests.head("https://images.pexels.com", timeout=10)
                latency = int((time.time() - t0) * 1000)
                if resp.status_code < 500:
                    return {"success": True, "message": f"免Key镜像通道畅通 (耗时 {latency}ms)", "latency_ms": latency}
                return {"success": False, "message": f"免Key镜像响应异常 ({resp.status_code})", "latency_ms": latency}
            except Exception as e:
                latency = int((time.time() - t0) * 1000)
                return {"success": False, "message": f"免Key通道网络不通: {e}", "latency_ms": latency}
        try:
            url = "https://api.pexels.com/v1/curated?per_page=1"
            resp = requests.get(url, headers={"Authorization": self.api_key}, timeout=10)
            latency = int((time.time() - t0) * 1000)
            if resp.status_code == 200:
                return {"success": True, "message": f"连接成功 (官方API在线，耗时 {latency}ms)", "latency_ms": latency}
            elif resp.status_code == 401:
                return {"success": False, "message": "鉴权失败：Pexels API Key 无效", "latency_ms": latency}
            else:
                return {"success": False, "message": f"响应异常 ({resp.status_code})", "latency_ms": latency}
        except Exception as e:
            latency = int((time.time() - t0) * 1000)
            return {"success": False, "message": f"连接超时: {e}", "latency_ms": latency}
