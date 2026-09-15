# -*- coding: utf-8 -*-
"""
🎨 Design Routes Shards Module
"""
from .design_assets_routes import router as assets_router
from .design_prompt_routes import router as prompt_router
from .design_hosting_routes import router as hosting_router
from .design_upload_routes import router as upload_router
from .design_batch_routes import router as batch_router

__all__ = ["assets_router", "prompt_router", "hosting_router", "upload_router", "batch_router"]
