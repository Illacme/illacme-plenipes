# -*- coding: utf-8 -*-
"""
🎨 Image Creation & Management Module (ICMM) - Stability AI Provider
职责：Stability AI (SD3.5 Large / Turbo / Core) 官方原厂云端大模型驱动。
🛡️ [SOP-01] 物理行数控制在 300 行以内。
"""

import time
import requests
from typing import Dict, Any, Optional, Tuple
from core.utils.tracing import tlog
from core.design.providers.base_provider import BaseImageProvider

class StabilityImageProvider(BaseImageProvider):
    PROVIDER_ID = "stability"
    PROVIDER_NAME = "Stability AI (SD 3.5)"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = self.config.get("api_key", "").strip()
        raw_base = self.config.get("base_url", "https://api.stability.ai/v2beta/stable-image/generate").strip()
        self.base_url = raw_base.rstrip("/")
        self.model = self.config.get("model", "sd3.5-large").strip()
        self.timeout = int(self.config.get("timeout", 60))

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        style: str = "vivid",
        **kwargs
    ) -> Tuple[Optional[bytes], Optional[str]]:
        if not self.api_key:
            return None, "未配置 Stability AI API Key"

        # Stability 支持 16:9, 1:1, 21:9, 4:5, 9:16 等标准比例
        ratio_map = {
            "16:9": "16:9",
            "1:1": "1:1",
            "2.35:1": "21:9",
            "9:16": "9:16",
            "4:3": "4:3"
        }
        st_ratio = ratio_map.get(aspect_ratio, "16:9")

        # 1. 优先调用 Stability 官方原生 v2beta REST 端点
        if "stability.ai" in self.base_url:
            sub_path = "sd3" if "sd3" in self.model else "core"
            url = f"{self.base_url}/{sub_path}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "image/*"
            }
            data = {
                "prompt": prompt,
                "model": self.model,
                "aspect_ratio": st_ratio,
                "output_format": "jpeg"
            }
            try:
                tlog.info(f"🎨 [Stability] 正在调用官方生图接口 ({self.model} / {st_ratio}): {prompt[:40]}...")
                resp = requests.post(url, headers=headers, files={"none": ""}, data=data, timeout=self.timeout)
                if resp.status_code == 200:
                    return resp.content, None
                else:
                    err_msg = f"HTTP {resp.status_code}: {resp.text[:200]}"
                    tlog.error(f"🛑 [Stability] 请求失败: {err_msg}")
                    return None, err_msg
            except Exception as e:
                tlog.error(f"🛑 [Stability] 异常: {e}")
                return None, str(e)

        # 2. 兼容第三方 OpenAI-like 格式中转
        url = f"{self.base_url}/images/generations"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "prompt": prompt,
            "size": "1024x1024" if aspect_ratio == "1:1" else "1792x1024",
            "response_format": "b64_json"
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                import base64
                res_data = resp.json()
                b64_str = res_data.get("data", [{}])[0].get("b64_json")
                if b64_str:
                    return base64.b64decode(b64_str), None
            return None, f"HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as e:
            return None, str(e)

    def test_connection(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"success": False, "message": "未配置 API Key", "latency_ms": 0}
        t0 = time.time()
        url = "https://api.stability.ai/v1/user/account" if "stability.ai" in self.base_url else f"{self.base_url}/models"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            latency = int((time.time() - t0) * 1000)
            if resp.status_code == 200:
                return {"success": True, "message": f"连接成功 (Stability 节点在线，耗时 {latency}ms)", "latency_ms": latency}
            elif resp.status_code == 401:
                return {"success": False, "message": "鉴权失败：API Key 无效", "latency_ms": latency}
            else:
                return {"success": False, "message": f"响应状态 ({resp.status_code})", "latency_ms": latency}
        except Exception as e:
            return {"success": False, "message": f"连接超时: {e}", "latency_ms": 0}
