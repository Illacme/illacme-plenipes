# -*- coding: utf-8 -*-
"""
🎨 Image Creation & Management Module (ICMM) - Google Imagen Provider
职责：通过 Gemini API 的 generateContent 端点调用 Google 图像生成模型。
🛡️ [SOP-01] 物理行数控制在 300 行以内。

⚠️ 历史说明：
  - 旧版 imagen-3.0-generate-002 模型名属于 Vertex AI (Google Cloud) 专属端点，
    需要 GCP 服务账户密钥与 aiplatform.googleapis.com 端点，不可用于 Gemini API Key。
  - 在 generativelanguage.googleapis.com (Google AI Studio / Gemini API Key) 中，
    图像生成通过 Gemini multimodal 模型完成，使用 generateContent + responseModalities=["IMAGE"]。
  - 可用模型包括：gemini-2.5-flash-image, gemini-3-pro-image, gemini-3.1-flash-image 等。
"""

import io
import time
import base64
import requests
from typing import Dict, Any, Optional, Tuple
from core.utils.tracing import tlog
from core.design.providers.base_provider import BaseImageProvider


class GoogleImagenProvider(BaseImageProvider):
    PROVIDER_ID = "imagen"
    PROVIDER_NAME = "Google Imagen 3"

    # Gemini API 图像生成默认模型
    DEFAULT_MODEL = "gemini-2.5-flash-image"
    DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.api_key = self.config.get("api_key", "").strip()
        raw_base = self.config.get("base_url", self.DEFAULT_BASE_URL).strip()
        self.base_url = raw_base.rstrip("/")
        self.model = self.config.get("model", self.DEFAULT_MODEL).strip()
        self.timeout = int(self.config.get("timeout", 90))

    def _is_gemini_api(self) -> bool:
        """判断是否为 Google 官方 Gemini API (generativelanguage.googleapis.com)"""
        return "googleapis.com" in self.base_url

    def _map_aspect_ratio(self, aspect_ratio: str) -> str:
        """将通用宽高比映射为 Gemini API 支持的格式"""
        ratio_map = {
            "16:9": "16:9", "1:1": "1:1", "9:16": "9:16",
            "4:3": "4:3", "3:4": "3:4", "2.35:1": "16:9"
        }
        return ratio_map.get(aspect_ratio, "16:9")

    def _generate_via_gemini(self, prompt: str, aspect_ratio: str) -> Tuple[Optional[bytes], Optional[str]]:
        """通过 Gemini generateContent 端点生成图像"""
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseModalities": ["IMAGE", "TEXT"]
            }
        }
        try:
            tlog.info(f"🎨 [GoogleImagen] Gemini generateContent ({self.model} / {aspect_ratio}): {prompt[:50]}...")
            resp = requests.post(url, json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                return self._extract_image_from_gemini_response(resp.json())
            err_msg = f"HTTP {resp.status_code}: {resp.text[:200]}"
            tlog.error(f"🛑 [GoogleImagen] 失败: {err_msg}")
            return None, err_msg
        except Exception as e:
            tlog.error(f"🛑 [GoogleImagen] 异常: {e}")
            return None, str(e)

    def _extract_image_from_gemini_response(self, data: dict) -> Tuple[Optional[bytes], Optional[str]]:
        """从 Gemini generateContent 响应中提取图像二进制数据"""
        candidates = data.get("candidates", [])
        if not candidates:
            # 检查 promptFeedback 安全过滤
            feedback = data.get("promptFeedback", {})
            block_reason = feedback.get("blockReason", "")
            if block_reason:
                return None, f"提示词被安全策略拦截 ({block_reason})"
            return None, "响应中未包含有效候选结果"

        parts = candidates[0].get("content", {}).get("parts", [])
        for part in parts:
            inline = part.get("inlineData")
            if inline and inline.get("data"):
                try:
                    return base64.b64decode(inline["data"]), None
                except Exception as e:
                    return None, f"Base64 解码失败: {e}"

        return None, "响应中未包含内嵌图像数据 (inlineData)"

    def _generate_via_openai_compat(self, prompt: str, aspect_ratio: str) -> Tuple[Optional[bytes], Optional[str]]:
        """兼容 OpenAI Images API 规范的第三方中转网关"""
        url = f"{self.base_url}/images/generations"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        size = "1792x1024" if aspect_ratio in ("16:9", "2.35:1") else "1024x1024"
        payload = {
            "model": self.model, "prompt": prompt,
            "size": size, "n": 1, "response_format": "b64_json"
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                b64_str = data.get("data", [{}])[0].get("b64_json")
                if b64_str:
                    return base64.b64decode(b64_str), None
                url_val = data.get("data", [{}])[0].get("url")
                if url_val:
                    dl = requests.get(url_val, timeout=30)
                    if dl.status_code == 200:
                        return dl.content, None
            return None, f"HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as e:
            return None, str(e)

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        style: str = "vivid",
        **kwargs
    ) -> Tuple[Optional[bytes], Optional[str]]:
        if not self.api_key:
            return None, "未配置 Google Gemini / Imagen API Key"

        g_ratio = self._map_aspect_ratio(aspect_ratio)

        if self._is_gemini_api():
            return self._generate_via_gemini(prompt, g_ratio)
        return self._generate_via_openai_compat(prompt, g_ratio)

    def test_connection(self) -> Dict[str, Any]:
        if not self.api_key:
            return {"success": False, "message": "未配置 API Key", "latency_ms": 0}
        t0 = time.time()
        try:
            if self._is_gemini_api():
                # Gemini API: 通过 GET /models/{model} 验证模型可达性
                url = f"{self.base_url}/models/{self.model}?key={self.api_key}"
                resp = requests.get(url, timeout=10)
            else:
                url = f"{self.base_url}/models"
                resp = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"}, timeout=10)
            latency = int((time.time() - t0) * 1000)
            if resp.status_code in (200, 201):
                return {"success": True, "message": f"连接成功 (Google Imagen 在线，耗时 {latency}ms)", "latency_ms": latency}
            elif resp.status_code == 400 and "API_KEY_INVALID" in resp.text:
                return {"success": False, "message": "鉴权失败：API Key 无效", "latency_ms": latency}
            elif resp.status_code == 404:
                return {"success": False, "message": f"模型不存在: {self.model}。请使用 gemini-2.5-flash-image 等 Gemini 图像模型", "latency_ms": latency}
            elif resp.status_code == 429:
                return {"success": True, "message": f"鉴权成功 (模型已识别，当前配额已满，耗时 {latency}ms)", "latency_ms": latency}
            else:
                return {"success": False, "message": f"响应状态 ({resp.status_code})", "latency_ms": latency}
        except Exception as e:
            return {"success": False, "message": f"连接超时或网络异常: {e}", "latency_ms": 0}
