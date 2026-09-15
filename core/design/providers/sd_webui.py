# -*- coding: utf-8 -*-
"""
🎨 Image Creation & Management Module (ICMM) - Stable Diffusion WebUI / Forge Provider
职责：本地/远程 SD WebUI (Automatic1111 / Forge / SD.Next) 图像生成驱动。
🛡️ [SOP-01] 物理行数控制在 300 行以内。
"""

import time
import base64
import requests
from typing import Dict, Any, Optional, Tuple
from core.utils.tracing import tlog
from core.design.providers.base_provider import BaseImageProvider

class SDWebUIProvider(BaseImageProvider):
    PROVIDER_ID = "sd_webui"
    PROVIDER_NAME = "SD WebUI / Forge"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        raw_base = self.config.get("base_url", "http://127.0.0.1:7860").strip()
        self.base_url = raw_base.rstrip("/")
        self.sampler_name = self.config.get("sampler_name", "Euler a")
        self.steps = int(self.config.get("steps", 20))
        self.cfg_scale = float(self.config.get("cfg_scale", 7.0))
        self.timeout = int(self.config.get("timeout", 120))
        self.auth_username = self.config.get("username", "")
        self.auth_password = self.config.get("password", "")

    def _get_auth(self):
        if self.auth_username and self.auth_password:
            return (self.auth_username, self.auth_password)
        return None

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        style: str = "vivid",
        **kwargs
    ) -> Tuple[Optional[bytes], Optional[str]]:
        # SD 常用分辨率微调 (保持 8 的倍数)
        ratio_dims = {
            "16:9": (896, 512),
            "1:1": (512, 512),
            "2.35:1": (960, 408),
            "4:3": (768, 576),
            "9:16": (512, 896)
        }
        width, height = ratio_dims.get(aspect_ratio, (896, 512))

        # 智能风格负向提示词增强
        neg_prompt = kwargs.get(
            "negative_prompt",
            "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"
        )

        url = f"{self.base_url}/sdapi/v1/txt2img"
        payload = {
            "prompt": prompt,
            "negative_prompt": neg_prompt,
            "sampler_name": kwargs.get("sampler_name", self.sampler_name),
            "steps": kwargs.get("steps", self.steps),
            "cfg_scale": kwargs.get("cfg_scale", self.cfg_scale),
            "width": width,
            "height": height,
            "enable_hr": False
        }

        try:
            tlog.info(f"🎨 [SD WebUI] 正在调度本地生图 ({width}x{height}): {prompt[:40]}...")
            resp = requests.post(url, json=payload, auth=self._get_auth(), timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                images = data.get("images", [])
                if images:
                    img_data = images[0]
                    return base64.b64decode(img_data), None
                return None, "SD WebUI 未返回有效图像列表"
            else:
                return None, f"SD WebUI HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as e:
            tlog.error(f"🛑 [SD WebUI] 异常: {e}")
            return None, str(e)

    def test_connection(self) -> Dict[str, Any]:
        t0 = time.time()
        url = f"{self.base_url}/sdapi/v1/options"
        try:
            resp = requests.get(url, auth=self._get_auth(), timeout=5)
            latency = int((time.time() - t0) * 1000)
            if resp.status_code == 200:
                return {"success": True, "message": f"连接成功 (本地 SD 服务在线，延迟 {latency}ms)", "latency_ms": latency}
            elif resp.status_code == 401:
                return {"success": False, "message": "SD WebUI 开启了账号密码认证，请检查配置", "latency_ms": latency}
            else:
                return {"success": False, "message": f"响应异常 ({resp.status_code})", "latency_ms": latency}
        except Exception as e:
            return {"success": False, "message": f"无法连接到 SD WebUI: {e}", "latency_ms": 0}
