#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚙️ Illacme Plenipes - AI Capability Probing Constants
该模块集中定义了算力适配器全动态主动探测系统所需要的各种静态 Payload 载荷与数据，
实现数据与业务逻辑的物理分离。 (V77.8)
"""

# 1像素透明 PNG 图片 Base64 数据串，用于极轻量多模态视觉通道嗅探
TRANSPARENT_1X1_PNG = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

# 1. 探测工具调用支持 (Tools Probe Payload)
TOOLS_PROBE_PAYLOAD_TEMPLATE = {
    "messages": [{"role": "user", "content": "Respond only with 'OK'."}],
    "max_tokens": 1,
    "temperature": 0.0,
    "tools": [{
        "type": "function",
        "function": {
            "name": "probe_capability_tool",
            "description": "A dummy tool used to verify if the LLM endpoint accepts tool definitions.",
            "parameters": {"type": "object", "properties": {}}
        }
    }],
    "tool_choice": "none"
}

# 2. 探测思维链推理支持 (CoT Probe Payload)
COT_PROBE_PAYLOAD_TEMPLATE = {
    "messages": [{"role": "user", "content": "Which is larger: 9.11 or 9.9?"}],
    "max_tokens": 15,
    "temperature": 0.0
}

# 3. 探测多模态视觉支持 (Vision Probe Payload)
VISION_PROBE_PAYLOAD_TEMPLATE = {
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "Respond OK"},
            {"type": "image_url", "image_url": {"url": TRANSPARENT_1X1_PNG}}
        ]
    }],
    "max_tokens": 1,
    "temperature": 0.0
}
