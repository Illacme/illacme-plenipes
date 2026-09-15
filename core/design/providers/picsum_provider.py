# -*- coding: utf-8 -*-
"""
🎨 Image Creation & Management Module (ICMM) - Lorem Picsum Free Stock Provider
职责：Lorem Picsum 免 Key 高清占位图库驱动 (零配置门槛、确定性 Seed、自适应尺寸与排版滤镜)。
🛡️ [SOP-01] 物理行数控制在 300 行以内。
"""

import hashlib
import requests
from typing import Dict, Any, Optional, Tuple
from core.utils.tracing import tlog
from core.design.providers.base_provider import BaseImageProvider

class PicsumProvider(BaseImageProvider):
    PROVIDER_ID = "picsum"
    PROVIDER_NAME = "Lorem Picsum"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.base_url = (self.config.get("base_url") or "https://picsum.photos").rstrip("/")
        self.grayscale = bool(self.config.get("grayscale", False))
        self.blur = int(self.config.get("blur", 0))
        self.timeout = int(self.config.get("timeout", 20))

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        style: str = "vivid",
        **kwargs
    ) -> Tuple[Optional[bytes], Optional[str]]:
        w, h = self.parse_dimensions(aspect_ratio)
        seed_str = prompt.strip() or "illacme_editorial_nature"
        seed_hash = hashlib.md5(seed_str.encode("utf-8")).hexdigest()[:12]

        url = f"{self.base_url}/seed/{seed_hash}/{w}/{h}"
        params = []
        if self.grayscale or kwargs.get("grayscale"):
            params.append("grayscale")
        blur_val = kwargs.get("blur", self.blur)
        if blur_val and int(blur_val) > 0:
            params.append(f"blur={min(max(int(blur_val), 1), 10)}")

        if params:
            url = f"{url}?{'&'.join(params)}"

        try:
            tlog.info(f"📸 [Lorem Picsum] 正在请求自适应高解析素材 ({w}x{h}, seed={seed_hash})...")
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
            resp = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            if resp.status_code == 200 and len(resp.content) > 1000:
                return resp.content, None
            return None, f"Lorem Picsum 返回异常状态码: {resp.status_code}"
        except Exception as e:
            tlog.error(f"🛑 [Lorem Picsum] 素材拉取失败: {e}")
            return None, f"Lorem Picsum 连接超时或异常: {e}"

    def test_connection(self) -> Dict[str, Any]:
        import time
        test_url = f"{self.base_url}/v2/list?page=1&limit=1"
        start_t = time.time()
        try:
            resp = requests.get(test_url, timeout=self.timeout)
            latency = int((time.time() - start_t) * 1000)
            if resp.status_code == 200 and isinstance(resp.json(), list):
                return {"success": True, "message": "Lorem Picsum 节点通信正常 (100% 免Key可用)", "latency_ms": latency}
            return {"success": False, "message": f"Lorem Picsum 状态异常 HTTP {resp.status_code}", "latency_ms": latency}
        except Exception as e:
            latency = int((time.time() - start_t) * 1000)
            return {"success": False, "message": f"Lorem Picsum 连接失败: {e}", "latency_ms": latency}
