# -*- coding: utf-8 -*-
"""
🎨 Image Creation & Management Module (ICMM) - OpenAI DALL-E 3 Provider
职责：OpenAI 及兼容中转接口生图驱动。
🛡️ [SOP-01] 物理行数控制在 300 行以内。
"""

import time
import requests
from typing import Dict, Any, Optional, Tuple
from core.utils.tracing import tlog
from core.design.providers.base_provider import BaseImageProvider

class OpenAIDalleProvider(BaseImageProvider):
    PROVIDER_ID = "openai"
    PROVIDER_NAME = "OpenAI DALL-E 3"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = self.config.get("api_key", "").strip()
        raw_base = self.config.get("base_url", "https://api.openai.com/v1").strip()
        self.base_url = raw_base.rstrip("/")
        self.model = self.config.get("model", "dall-e-3").strip()
        self.timeout = int(self.config.get("timeout", 60))

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        style: str = "vivid",
        **kwargs
    ) -> Tuple[Optional[bytes], Optional[str]]:
        if not self.api_key:
            return None, "未配置 OpenAI API Key"

        # DALL-E 3 仅支持 1024x1024, 1792x1024 (宽幅), 1024x1792 (纵向)
        if aspect_ratio in ("16:9", "2.35:1"):
            dalle_size = "1792x1024"
        elif aspect_ratio == "9:16":
            dalle_size = "1024x1792"
        else:
            dalle_size = "1024x1024"

        url = f"{self.base_url}/images/generations"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "prompt": prompt,
            "n": 1,
            "size": dalle_size,
            "quality": kwargs.get("quality", "standard"),
            "style": style if style in ("vivid", "natural") else "vivid",
            "response_format": "b64_json"
        }

        try:
            tlog.info(f"🎨 [DALL-E] 正在调用生图接口 ({dalle_size}): {prompt[:40]}...")
            resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                import base64
                b64_data = data.get("data", [{}])[0].get("b64_json")
                if b64_data:
                    return base64.b64decode(b64_data), None
                # 回退支持 url 下载
                img_url = data.get("data", [{}])[0].get("url")
                if img_url:
                    img_resp = requests.get(img_url, timeout=30)
                    if img_resp.status_code == 200:
                        return img_resp.content, None
                return None, "接口未返回有效图像数据"
            else:
                err_msg = f"HTTP {resp.status_code}: {resp.text[:200]}"
                tlog.error(f"🛑 [DALL-E] 生图请求失败: {err_msg}")
                return None, err_msg
        except Exception as e:
            tlog.error(f"🛑 [DALL-E] 异常: {e}")
            return None, str(e)

    def test_connection(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"success": False, "message": "未配置 API Key", "latency_ms": 0}
        t0 = time.time()
        url = f"{self.base_url}/models"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            latency = int((time.time() - t0) * 1000)
            if resp.status_code == 200:
                return {"success": True, "message": f"连接成功 (模型库在线，耗时 {latency}ms)", "latency_ms": latency}
            elif resp.status_code == 401:
                return {"success": False, "message": "鉴权失败：API Key 无效", "latency_ms": latency}
            else:
                return {"success": False, "message": f"响应异常 ({resp.status_code})", "latency_ms": latency}
        except Exception as e:
            return {"success": False, "message": f"连接超时或网络错误: {e}", "latency_ms": 0}
