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

    @classmethod
    def sanitize_keywords(cls, prompt: str) -> str:
        """
        🛡️ 防御性提炼：将长提示词或中文摘要提炼为适合 Unsplash 摄影检索的英文关键词。
        """
        if not prompt or not prompt.strip():
            return "technology minimal"
        import re
        raw = prompt.strip()
        words = re.findall(r'[A-Za-z0-9_-]+', raw)
        if words:
            clean_words = [w for w in words if w.lower() not in ("8k", "4k", "uhd", "hd", "prompt", "masterpiece", "octane", "render", "vivid")]
            if clean_words:
                return " ".join(clean_words[:3])

        # 中文主题语义映射
        topic_map = [
            (r'多语言|国际化|全球|矩阵|i18n', "global technology network"),
            (r'架构|设计|治理|系统|工程', "modern architecture structure"),
            (r'代码|开发|编程|算法|前端|后端', "software technology code"),
            (r'设计|艺术|视觉|装帧|封面', "minimal graphic design abstract"),
            (r'安全|合规|密码|防御|守卫', "cybersecurity digital security"),
            (r'数据|分析|星谱|知识|账本', "data visualization abstract"),
        ]
        for pat, kw in topic_map:
            if re.search(pat, raw, re.IGNORECASE):
                return kw
        return "minimal technology"

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        style: str = "vivid",
        **kwargs
    ) -> Tuple[Optional[bytes], Optional[str]]:
        # 🛡️ 智能提炼关键词
        query = self.sanitize_keywords(prompt)
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

        # 免 Key 智能降级拉取 Source 图片（支持按文章语义与相移滚动的高清多样性图池）
        try:
            dims = {"16:9": (1280, 720), "1:1": (800, 800), "2.35:1": (1200, 510)}
            w, h = dims.get(aspect_ratio, (1280, 720))
            offset = int(kwargs.get("offset") or 0)
            curated_pool = [
                "photo-1618005182384-a83a8bd57fbe",  # 抽象流体光影
                "photo-1518770660439-4636190af475",  # 科技芯片硬件
                "photo-1451187580459-43490279c0fa",  # 全球数字化网络
                "photo-1526374965328-7f61d4dc18c5",  # 矩阵黑客二进制
                "photo-1507238691740-187a5b1d37b8",  # 现代极简设计工作台
                "photo-1550751827-4bd374c3f58b",  # 赛博朋克极简暗调
                "photo-1486406146926-c627a92ad1ab",  # 现代几何建筑
                "photo-1519681393784-d120267933ba",  # 极简星空山川
                "photo-1504384308090-c894fdcc538d",  # 科技服务器阵列
                "photo-1498050108023-c5249f4df085",  # 现代代码工作空间
                "photo-1558494949-ef010cbdcc31",  # 云端数据中心流光
                "photo-1534972195531-a756b1126f24",  # 极简自然绿植光影
            ]
            import hashlib
            base_idx = int(hashlib.md5(query.encode('utf-8')).hexdigest()[:6], 16)
            seed_idx = (base_idx + offset) % len(curated_pool)
            photo_id = curated_pool[seed_idx]
            fallback_url = f"https://images.unsplash.com/{photo_id}?w={w}&h={h}&fit=crop&auto=format&q=80"
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
