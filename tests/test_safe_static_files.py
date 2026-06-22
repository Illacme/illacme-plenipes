#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 [Test] SafeStaticFiles Security Test
职责：测试 SafeStaticFiles 的物理防护拦截，防止敏感的本地配置文件和原稿文库泄露。
"""
import sys
import os
from fastapi.testclient import TestClient

# 将项目根目录加入 python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.api.server import app

def test_safe_static_files_security():
    """🧪 测试 SafeStaticFiles 的物理防护拦截，防止敏感的本地配置文件和原稿文库泄露"""
    client = TestClient(app)
    
    # 1. 尝试越权访问 imprints/ 下 of config.local.yaml 敏感文件
    res_sensitive = client.get("/imprints/luminous_citadel/config.local.yaml")
    assert res_sensitive.status_code == 403, "敏感配置文件越权读取拦截失败！"
    assert "Sovereign Protection Activated" in res_sensitive.text
    
    # 2. 尝试越权访问 manuscripts 原稿文库目录
    res_manuscripts = client.get("/imprints/luminous_citadel/manuscripts/some_post.md")
    assert res_manuscripts.status_code == 403, "隐私原稿文库越权读取拦截失败！"
    
    # 3. 尝试越权访问 metadata 元数据 sqlite/json 目录
    res_metadata = client.get("/imprints/luminous_citadel/metadata/themes/starlight/knowledge_graph.json")
    assert res_metadata.status_code == 403, "元数据物理账本与图谱越权读取拦截失败！"
