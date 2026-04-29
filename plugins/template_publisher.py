#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Plugin Template: Sample Publisher
模块职责：演示如何编写一个自定义的分发插件。
开发者只需继承 BasePublisher 并实现 publish 方法即可。
"""

from core.adapters.egress.base import BasePublisher
from core.utils.tracing import tlog

class SamplePublisher(BasePublisher):
    """🚀 [Developer Kit] 示例分发插件"""
    
    def publish(self, payload: dict):
        """
        处理分发逻辑。
        payload 包含：
            - rel_path: 相对路径
            - title: 文章标题
            - content: 处理后的文章内容
            - metadata: 完整的 Frontmatter 元数据
        """
        title = payload.get("title")
        tlog.info(f"✨ [Sample Plugin] 正在模拟分发文章: {title}")
        
        # 在这里编写你的逻辑，例如：
        # 1. 发送 Webhook
        # 2. 上传至特定云存储
        # 3. 触发外部 API
        
        return True
