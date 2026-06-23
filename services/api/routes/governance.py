# -*- coding: utf-8 -*-
"""
🛡️ [V74.55] Gov Route Hub
职责：治理路由的入口枢纽。
架构：已按 SOP-04 执行物理降解，逻辑已委派至 gov/ 子目录。
"""

from fastapi import APIRouter
from .gov import context, imprints, config, vault, actions, audit, translation_review, syndication_queue
from . import dispatch

router = APIRouter()

# 🚀 [主权对正] 挂载降解后的原子路由模块
router.include_router(context.router)
router.include_router(imprints.router)
router.include_router(config.router)
router.include_router(vault.router)
router.include_router(dispatch.router)
router.include_router(actions.router)
router.include_router(audit.router)
router.include_router(translation_review.router)  # 🔒 [I5] 翻译人工校对回流
router.include_router(syndication_queue.router)   # 📡 多渠道分发死信/重试队列

