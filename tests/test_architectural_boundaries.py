#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ Architectural Boundary Integrity Tests
物理领地边界防错单元测试。
确保 publishers/ 目录下绝对不混入图床驱动，image_hosting/ 目录下绝对不混入全站托管驱动。
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath('.'))

def test_publishers_directory_purity():
    """
    🛡️ 验证 publishers 目录的物理纯洁性。
    严禁将 aliyun_oss, tencent_cos, upyun_uss 等图床驱动混入 publishers 目录。
    """
    publishers_dir = os.path.abspath("adapters/egress/publishers")
    forbidden_image_host_files = {"aliyun_oss.py", "tencent_cos.py", "upyun_uss.py", "sm_ms.py", "imgur.py", "loli_io.py"}
    
    if os.path.exists(publishers_dir):
        files = set(os.listdir(publishers_dir))
        forbidden_present = files.intersection(forbidden_image_host_files)
        assert len(forbidden_present) == 0, f"🛑 发现图床驱动错放在 publishers 目录下: {forbidden_present}！请严格遵循 Sovereign Rule 9。"

def test_image_hosting_directory_purity():
    """
    🛡️ 验证 image_hosting 目录的物理纯洁性。
    严禁将 github_pages, netlify, vercel, cloudflare_pages 等全站托管驱动混入 image_hosting 目录。
    """
    image_hosting_dir = os.path.abspath("adapters/egress/image_hosting")
    forbidden_publisher_files = {"github_pages.py", "netlify.py", "vercel.py", "cloudflare_pages.py", "gitee_pages.py"}
    
    if os.path.exists(image_hosting_dir):
        files = set(os.listdir(image_hosting_dir))
        forbidden_present = files.intersection(forbidden_publisher_files)
        assert len(forbidden_present) == 0, f"🛑 发现全站托管驱动错放在 image_hosting 目录下: {forbidden_present}！请严格遵循 Sovereign Rule 9。"
