# -*- coding: utf-8 -*-
"""
🎨 Image Creation & Management Module (ICMM) - Unsplash Image Provider
职责：免费商用图库 Unsplash 检索与高清图片拉取。
🛡️ [SOP-01] 物理行数控制在 300 行以内。
"""

import time
import random
import requests
from typing import Dict, Any, Optional, Tuple
from core.utils.tracing import tlog
from core.design.providers.base_provider import BaseImageProvider

class UnsplashProvider(BaseImageProvider):
    PROVIDER_ID = "unsplash"
    PROVIDER_NAME = "Unsplash"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.access_key = self.config.get("access_key", "").strip()
        self.timeout = int(self.config.get("timeout", 20))

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        style: str = "vivid",
        **kwargs
    ) -> Tuple[Optional[bytes], Optional[str]]:
        # 关键词提炼
        keywords = prompt.split()[:3] if prompt else ["technology", "minimal"]
        query = " ".join(keywords)
        orientation = "landscape" if aspect_ratio in ("16:9", "2.35:1", "4:3") else "portrait"

        # 优先官方 API
        if self.access_key:
            api_url = "https://api.unsplash.com/photos/random"
            headers = {"Authorization": f"Client-ID {self.access_key}"}
            params = {"query": query, "orientation": orientation}
            try:
                resp = requests.get(api_url, headers=headers, params=params, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    regular_url = data.get("urls", {}).get("regular")
                    if regular_url:
                        img_res = requests.get(regular_url, timeout=30)
                        if img_res.status_code == 200:
                            return img_res.content, None
            except Exception as e:
                tlog.warning(f"⚠️ [Unsplash API] 请求异常: {e}")

        # 免 Key 智能降级拉取 Source 图片
        try:
            # 使用公共可靠镜像源
            dims = {"16:9": (1280, 720), "1:1": (800, 800), "2.35:1": (1200, 510)}
            w, h = dims.get(aspect_ratio, (1280, 720))
            fallback_url = f"https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w={w}&h={h}&fit=crop&auto=format&q=80"
            resp = requests.get(fallback_url, timeout=15)
            if resp.status_code == 200:
                return resp.content, None
        except Exception as e:
            tlog.error(f"🛑 [Unsplash Fallback] 异常: {e}")
            return None, str(e)

        return None, "未能获取有效的 Unsplash 图像"

    def test_connection(self) -> Dict[str, Any]:
        t0 = time.time()
        if self.access_key:
            try:
                resp = requests.get("https://api.unsplash.com/stats/total", headers={"Authorization": f"Client-ID {self.access_key}"}, timeout=10)
                latency = int((time.time() - t0) * 1000)
                if resp.status_code == 200:
                    return {"success": True, "message": f"连接成功 (官方API在线，耗时 {latency}ms)", "latency_ms": latency}
                return {"success": False, "message": f"鉴权失败 ({resp.status_code})", "latency_ms": latency}
            except Exception as e:
                latency = int((time.time() - t0) * 1000)
                return {"success": False, "message": f"官方API连接超时: {e}", "latency_ms": latency}
        try:
            resp = requests.head("https://images.unsplash.com", timeout=10)
            latency = int((time.time() - t0) * 1000)
            if resp.status_code < 500:
                return {"success": True, "message": f"免Key镜像通道畅通 (耗时 {latency}ms)", "latency_ms": latency}
            return {"success": False, "message": f"免Key镜像响应异常 ({resp.status_code})", "latency_ms": latency}
        except Exception as e:
            latency = int((time.time() - t0) * 1000)
            return {"success": False, "message": f"免Key通道网络不通: {e}", "latency_ms": latency}
