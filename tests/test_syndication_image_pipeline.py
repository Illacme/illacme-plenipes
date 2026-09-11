#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 [V114.0] 测试社媒图床中枢与外网图片绝对链接转换全链路
验证点：
1. MarkdownASTProcessor 处理标准 Markdown、HTML 及 Obsidian Wiki 格式图片。
2. ImageUploader 自动回退至独立站原生 CDN 外链 (Hosting CDN Fallback)。
3. ImageUploader 动态挂载第三方图床驱动与上传代理。
4. GitHubImageHost 自动推导关联仓库。
"""

import os
import tempfile
import pytest
from core.editorial.ast_processor import MarkdownASTProcessor
from core.syndication.uploader import ImageUploader
from adapters.egress.image_hosting.github import GitHubImageHost

def test_ast_process_images_markdown_and_wiki():
    """测试 AST 解析器对相对路径与 Obsidian 语法的解析与替换"""
    processor = MarkdownASTProcessor()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建临时图片文件
        img_path = os.path.join(temp_dir, "cover.png")
        with open(img_path, "wb") as f:
            f.write(b"fake image data")
            
        doc_dir = temp_dir
        sample_md = (
            "# 测试文章\n\n"
            "这是标准相对图片：![封面图](./cover.png)\n\n"
            "这是带参数图片：![图2](cover.png?v=123)\n\n"
            "这是 Obsidian 嵌入语法：![[cover.png]]\n\n"
            "这是带尺寸的 Obsidian 语法：![[cover.png|400x300]]\n\n"
            "这是 HTML 标签：<img src=\"cover.png\" alt=\"html pic\">\n\n"
            "这是外网图片保持不变：![远程](https://example.com/pic.jpg)\n"
        )
        
        # 模拟上传函数
        def mock_upload(p: str) -> str:
            assert os.path.isfile(p)
            return "https://cdn.example.com/images/" + os.path.basename(p)
            
        res = processor.process_images(sample_md, doc_dir, mock_upload)
        
        # 断言替换结果
        assert "![封面图](https://cdn.example.com/images/cover.png)" in res
        assert "![图2](https://cdn.example.com/images/cover.png?v=123)" in res
        assert "![cover.png](https://cdn.example.com/images/cover.png)" in res
        assert "![400x300](https://cdn.example.com/images/cover.png)" in res
        assert '<img src="https://cdn.example.com/images/cover.png" alt="html pic">' in res
        assert "![远程](https://example.com/pic.jpg)" in res

def test_image_uploader_hosting_cdn_fallback():
    """测试未配置第三方图床时，自动回退到独立站原生 CDN 外链"""
    with tempfile.TemporaryDirectory() as temp_vault:
        assets_dir = os.path.join(temp_vault, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        img_file = os.path.join(assets_dir, "banner.png")
        with open(img_file, "wb") as f:
            f.write(b"banner image")
            
        # 构造带有 site_url 但无外部图床的上下文
        sys_tuning = {
            "vault_root": temp_vault,
            "site_url": "https://illacme.github.io/illacme-press",
            "image_hosting": {}
        }
        
        uploader = ImageUploader(syndication_cfg={}, sys_tuning=sys_tuning)
        
        # 应该自动回退到 site_url CDN
        url = uploader.upload_image(img_file)
        assert url == "https://illacme.github.io/illacme-press/assets/banner.png"

def test_image_uploader_with_custom_host():
    """测试配置第三方图床时的正常装配与调用"""
    class DummyHost:
        def __init__(self, cfg, sys_tuning):
            self.cfg = cfg
        def upload(self, path):
            return f"https://my-bucket.s3.amazonaws.com/{os.path.basename(path)}"
            
    with tempfile.TemporaryDirectory() as temp_dir:
        img_file = os.path.join(temp_dir, "pic.jpg")
        with open(img_file, "wb") as f:
            f.write(b"data")
            
        sys_tuning = {
            "image_hosting": {
                "s3": {
                    "enabled": True,
                    "bucket": "my-bucket"
                }
            }
        }
        
        uploader = ImageUploader(syndication_cfg={}, sys_tuning=sys_tuning)
        # 注入 mock 实例
        uploader.host_instance = DummyHost({}, sys_tuning)
        
        url = uploader.upload_image(img_file)
        assert url == "https://my-bucket.s3.amazonaws.com/pic.jpg"

def test_github_image_host_repo_auto_resolution():
    """测试 GitHub 图床驱动自动从 GitHub Pages 上下文中推导仓库"""
    sys_tuning = {
        "publish_control": {
            "direct_upload": {
                "github_pages": {
                    "repo_url": "https://github.com/Illacme/illacme-press.git"
                }
            }
        }
    }
    
    # 未配置 repo，但传入了 token
    config = {
        "token": "ghp_mock_token_123",
        "repo": ""
    }
    
    host = GitHubImageHost(config, sys_tuning)
    resolved = host._resolve_repo()
    assert resolved == "Illacme/illacme-press"
    assert host.repo == "Illacme/illacme-press"
