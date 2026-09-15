# -*- coding: utf-8 -*-
"""
🎨 Image Creation & Management Module (ICMM) - Midjourney Provider
职责：Midjourney 艺术商业生图大模型驱动 (支持 Midjourney-Proxy 与兼容中转网关)。
🛡️ [SOP-01] 物理行数控制在 300 行以内。
"""

import time
import requests
from typing import Dict, Any, Optional, Tuple
from core.utils.tracing import tlog
from core.design.providers.base_provider import BaseImageProvider

class MidjourneyProvider(BaseImageProvider):
    PROVIDER_ID = "midjourney"
    PROVIDER_NAME = "Midjourney Proxy"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = self.config.get("api_key", "").strip()
        raw_base = self.config.get("base_url", "https://api.midjourney.com/v1").strip()
        self.base_url = raw_base.rstrip("/")
        self.model = self.config.get("model", "v6.1").strip()
        self.timeout = int(self.config.get("timeout", 90))

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        style: str = "vivid",
        **kwargs
    ) -> Tuple[Optional[bytes], Optional[str]]:
        if not self.api_key:
            return None, "未配置 Midjourney API Key / Token"

        # Midjourney ar 标志
        ar_flag = "--ar 16:9"
        if aspect_ratio == "1:1":
            ar_flag = "--ar 1:1"
        elif aspect_ratio == "2.35:1":
            ar_flag = "--ar 21:9"
        elif aspect_ratio == "9:16":
            ar_flag = "--ar 9:16"

        full_prompt = f"{prompt} {ar_flag} --v {self.model.replace('v', '')}"

        # 1. 尝试调用通用中转端点 /images/generations
        url = f"{self.base_url}/images/generations"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": f"midjourney-{self.model}",
            "prompt": full_prompt,
            "response_format": "b64_json"
        }

        try:
            tlog.info(f"🎨 [Midjourney] 正在调度任务 ({self.model}): {full_prompt[:50]}...")
            resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                import base64
                b64_str = data.get("data", [{}])[0].get("b64_json")
                if b64_str:
                    return base64.b64decode(b64_str), None
                url_val = data.get("data", [{}])[0].get("url") or data.get("imageUrl")
                if url_val:
                    dl = requests.get(url_val, timeout=30)
                    if dl.status_code == 200:
                        return dl.content, None
                return None, "Midjourney 未返回有效图像"

            # 2. 回退适配 Midjourney-Proxy 标准端点 /mj/submit/imagine
            mj_url = f"{self.base_url}/mj/submit/imagine"
            mj_payload = {"prompt": full_prompt}
            mj_resp = requests.post(mj_url, headers=headers, json=mj_payload, timeout=20)
            if mj_resp.status_code == 200:
                task_id = mj_resp.json().get("result")
                if task_id:
                    return self._poll_mj_task(task_id, headers)
            return None, f"HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as e:
            tlog.error(f"🛑 [Midjourney] 异常: {e}")
            return None, str(e)

    def _poll_mj_task(self, task_id: str, headers: Dict[str, str]) -> Tuple[Optional[bytes], Optional[str]]:
        poll_url = f"{self.base_url}/mj/task/{task_id}/fetch"
        t0 = time.time()
        while time.time() - t0 < self.timeout:
            time.sleep(3)
            try:
                r = requests.get(poll_url, headers=headers, timeout=10)
                if r.status_code == 200:
                    t_data = r.json()
                    status = t_data.get("status")
                    if status == "SUCCESS":
                        img_url = t_data.get("imageUrl")
                        if img_url:
                            dl = requests.get(img_url, timeout=30)
                            if dl.status_code == 200:
                                return dl.content, None
                    elif status in ("FAILURE", "FAILED"):
                        return None, f"任务失败: {t_data.get('failReason')}"
            except Exception:
                pass
        return None, "Midjourney 任务生成超时"

    def test_connection(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"success": False, "message": "未配置 API Key", "latency_ms": 0}
        t0 = time.time()
        try:
            url = f"{self.base_url}/models"
            resp = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"}, timeout=10)
            latency = int((time.time() - t0) * 1000)
            if resp.status_code in (200, 201):
                return {"success": True, "message": f"连接成功 (Midjourney 节点在线，耗时 {latency}ms)", "latency_ms": latency}
            elif resp.status_code == 401:
                return {"success": False, "message": "鉴权失败：API Token 无效", "latency_ms": latency}
            else:
                return {"success": True, "message": f"服务已联通 (HTTP {resp.status_code})", "latency_ms": latency}
        except Exception as e:
            return {"success": False, "message": f"连接超时: {e}", "latency_ms": 0}
