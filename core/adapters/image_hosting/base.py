#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Image Hosting Base (图床基类)
职责：规范化所有第三方图床驱动的接口契约。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import abc
from typing import Dict, Any

class BaseImageHost(abc.ABC):
    """
    💎 图床适配器基座契约
    所有具体图床实现（S3, GitHub, Imgur 等）必须继承此类并实现核心方法。
    """
    def __init__(self, config: Dict[str, Any], sys_tuning: Dict[str, Any] = None):
        self.config = config or {}
        self.sys_tuning = sys_tuning or {}

    @abc.abstractmethod
    def upload(self, local_path: str) -> str:
        """
        🚀 物理上传接口
        将本地物理图片上传到公网，成功则返回公网可访问 CDN 绝对 URL，失败则返回 None。
        """
        pass
