# -*- coding: utf-8 -*-
"""
向后兼容性代理：重定向至 generic_webhook.py
"""
from .generic_webhook import GenericWebhookDriver

__all__ = ["GenericWebhookDriver"]
