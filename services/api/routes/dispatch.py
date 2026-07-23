#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 [V68.0] Illacme Plenipes - Dispatch Hub API (Router Hub Facade)
职责：作为资产分发控制中枢的纯净门面路由器，聚合挂载三大分片路由并零破坏重导出处理函数。
"""

from fastapi import APIRouter

# 1. 引入并挂载 Vault 调度分片
from .dispatch_shards.vault_routes import (
    router as vault_router,
    get_dispatch_status,
    toggle_lab,
    trigger_re_dispatch,
    destroy_artifact,
    get_pending_syndication
)

# 2. 引入并挂载 CLI 平台 OAuth 授权分片
from .dispatch_shards.platform_oauth_routes import (
    router as platform_oauth_router,
    cloudflare_oauth_login,
    cloudflare_oauth_status,
    netlify_oauth_login,
    netlify_oauth_status,
    vercel_oauth_login,
    vercel_oauth_status,
    firebase_oauth_login,
    firebase_oauth_status
)

# 3. 引入并挂载 环境与凭据感应分片
from .dispatch_shards.sensing_routes import (
    router as sensing_router,
    github_ssh_status,
    aws_credentials_status,
    sftp_ssh_status,
    gitee_git_status,
    docker_auth_status,
    sensing_git_credentials
)

router = APIRouter()

# 聚合子路由树
router.include_router(vault_router)
router.include_router(platform_oauth_router)
router.include_router(sensing_router)

__all__ = [
    "router",
    "get_dispatch_status",
    "toggle_lab",
    "trigger_re_dispatch",
    "destroy_artifact",
    "get_pending_syndication",
    "cloudflare_oauth_login",
    "cloudflare_oauth_status",
    "netlify_oauth_login",
    "netlify_oauth_status",
    "vercel_oauth_login",
    "vercel_oauth_status",
    "firebase_oauth_login",
    "firebase_oauth_status",
    "github_ssh_status",
    "aws_credentials_status",
    "sftp_ssh_status",
    "gitee_git_status",
    "docker_auth_status",
    "sensing_git_credentials"
]
