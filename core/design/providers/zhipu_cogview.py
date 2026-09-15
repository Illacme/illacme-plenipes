# -*- coding: utf-8 -*-
"""
🎨 Image Creation & Management Module (ICMM) - Zhipu CogView Provider
职责：智谱清言 CogView-3 / CogView-3-Plus 原生中文大模型驱动。
🛡️ [SOP-01] 物理行数控制在 300 行以内。
"""

import time
import requests
from typing import Dict, Any, Optional, Tuple
from core.utils.tracing import tlog
from core.design.providers.base_provider import BaseImageProvider

class ZhipuCogViewProvider(BaseImageProvider):
    PROVIDER_ID = "zhipu"
    PROVIDER_NAME = "智谱清言 CogView-3"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = self.config.get("api_key", "").strip()
        raw_base = self.config.get("base_url", "https://open.bigmodel.cn/api/paas/v4").strip()
        self.base_url = raw_base.rstrip("/")
        self.model = self.config.get("model", "cogview-3-plus").strip()
        self.timeout = int(self.config.get("timeout", 60))

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        style: str = "vivid",
        **kwargs
    ) -> Tuple[Optional[bytes], Optional[str]]:
        if not self.api_key:
            return None, "未配置智谱开放平台 API Key"

        # 智谱 CogView 推荐比例尺寸
        if aspect_ratio in ("16:9", "2.35:1"):
            c_size = "1440x720"
        elif aspect_ratio == "9:16":
            c_size = "720x1440"
        elif aspect_ratio == "4:3":
            c_size = "1024x768"
        else:
            c_size = "1024x1024"

        url = f"{self.base_url}/images/generations"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "prompt": prompt,
            "size": c_size
        }

        try:
            tlog.info(f"🎨 [CogView] 正在调用智谱生图接口 ({self.model} / {c_size}): {prompt[:40]}...")
            resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                img_url = data.get("data", [{}])[0].get("url")
                if img_url:
                    dl = requests.get(img_url, timeout=30)
                    if dl.status_code == 200:
                        return dl.content, None
                return None, "智谱 CogView 未返回有效图片链接"
            else:
                err_msg = f"HTTP {resp.status_code}: {resp.text[:200]}"
                tlog.error(f"🛑 [CogView] 生图失败: {err_msg}")
                return None, err_msg
        except Exception as e:
            tlog.error(f"🛑 [CogView] 异常: {e}")
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
                return {"success": True, "message": f"连接成功 (智谱节点在线，耗时 {latency}ms)", "latency_ms": latency}
            elif resp.status_code == 401:
                return {"success": False, "message": "鉴权失败：API Key 无效", "latency_ms": latency}
            else:
                return {"success": True, "message": f"网关连通 (HTTP {resp.status_code})", "latency_ms": latency}
        except Exception as e:
            return {"success": False, "message": f"连接超时: {e}", "latency_ms": 0}
