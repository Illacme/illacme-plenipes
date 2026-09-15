# -*- coding: utf-8 -*-
"""
🎨 Image Creation & Management Module (ICMM) - FLUX.1 Image Provider
职责：FLUX.1 旗舰开源/云端生图模型驱动 (支持 SiliconFlow / Fal.ai / OpenAI 兼容端点)。
🛡️ [SOP-01] 物理行数控制在 300 行以内。
"""

import time
import requests
from typing import Dict, Any, Optional, Tuple
from core.utils.tracing import tlog
from core.design.providers.base_provider import BaseImageProvider

class FluxImageProvider(BaseImageProvider):
    PROVIDER_ID = "flux"
    PROVIDER_NAME = "FLUX.1 (Black Forest Labs)"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = self.config.get("api_key", "").strip()
        raw_base = self.config.get("base_url", "https://api.siliconflow.cn/v1").strip()
        self.base_url = raw_base.rstrip("/")
        self.model = self.config.get("model", "black-forest-labs/FLUX.1-schnell").strip()
        self.timeout = int(self.config.get("timeout", 60))

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        style: str = "vivid",
        **kwargs
    ) -> Tuple[Optional[bytes], Optional[str]]:
        if not self.api_key:
            return None, "未配置 FLUX.1 API Key"

        # FLUX 推荐适配分辨率 (必须为 64 或 32 的倍数)
        if aspect_ratio == "16:9":
            image_size = "1024x576"
        elif aspect_ratio == "2.35:1":
            image_size = "1024x448"
        elif aspect_ratio == "9:16":
            image_size = "576x1024"
        elif aspect_ratio == "4:3":
            image_size = "1024x768"
        else:
            image_size = "1024x1024"

        url = f"{self.base_url}/images/generations"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "prompt": prompt,
            "image_size": image_size,
            "n": 1,
            "seed": kwargs.get("seed", 42)
        }

        try:
            tlog.info(f"🎨 [FLUX] 正在调用生图接口 ({self.model} / {image_size}): {prompt[:40]}...")
            resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                import base64
                images = data.get("images") or data.get("data") or []
                if images and isinstance(images, list):
                    first = images[0]
                    if isinstance(first, dict):
                        b64_str = first.get("b64_json")
                        if b64_str:
                            return base64.b64decode(b64_str), None
                        url_val = first.get("url")
                        if url_val:
                            dl = requests.get(url_val, timeout=30)
                            if dl.status_code == 200:
                                return dl.content, None
                    elif isinstance(first, str) and first.startswith("http"):
                        dl = requests.get(first, timeout=30)
                        if dl.status_code == 200:
                            return dl.content, None
                return None, "FLUX 接口未返回有效的图像数据"
            else:
                err_msg = f"HTTP {resp.status_code}: {resp.text[:200]}"
                tlog.error(f"🛑 [FLUX] 生图请求失败: {err_msg}")
                return None, err_msg
        except Exception as e:
            tlog.error(f"🛑 [FLUX] 异常: {e}")
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
            if resp.status_code in (200, 201):
                return {"success": True, "message": f"连接成功 (FLUX 节点就绪，耗时 {latency}ms)", "latency_ms": latency}
            elif resp.status_code == 401:
                return {"success": False, "message": "鉴权失败：API Key 无效", "latency_ms": latency}
            else:
                return {"success": False, "message": f"响应异常 ({resp.status_code})", "latency_ms": latency}
        except Exception as e:
            return {"success": False, "message": f"连接超时或网络错误: {e}", "latency_ms": 0}
