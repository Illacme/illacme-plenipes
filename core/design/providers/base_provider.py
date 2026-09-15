# -*- coding: utf-8 -*-
"""
🎨 Image Creation & Management Module (ICMM) - Base Image Provider
职责：图像生成与获取提供商基类规约。
🛡️ [SOP-01] 物理行数控制在 300 行以内。
"""

import abc
from typing import Dict, Any, Optional, Tuple

class BaseImageProvider(abc.ABC):
    """图像生成驱动统一抽象基类"""

    PROVIDER_ID = "base"
    PROVIDER_NAME = "Base Provider"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abc.abstractmethod
    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        style: str = "vivid",
        **kwargs
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        执行图像生成
        :param prompt: 提示词
        :param aspect_ratio: 画幅比例 ('16:9', '1:1', '2.35:1', '4:3')
        :param style: 风格预设 ('vivid', 'natural', 'anime', 'photorealistic', 'tech')
        :return: (图片二进制 bytes 或 None, 错误信息描述 或 None)
        """
        pass

    @abc.abstractmethod
    def test_connection(self) -> Dict[str, Any]:
        """
        测试连通性与鉴权状态
        :return: {"success": bool, "message": str, "latency_ms": int}
        """
        pass

    def parse_dimensions(self, aspect_ratio: str) -> Tuple[int, int]:
        """根据画幅比例换算标准生图像素分辨率"""
        dim_map = {
            "2.35:1": (1920, 817),  # 微信公众号头条封面
            "16:9": (1792, 1024),   # 宽屏博客 / 知乎 / B站
            "3:4": (900, 1200),     # 社交图文 / 小红书
            "1:1": (1024, 1024),    # 正方形卡片 / 头像
            "4:3": (1024, 768),
            "9:16": (1024, 1792)
        }
        return dim_map.get(aspect_ratio, (1792, 1024))
