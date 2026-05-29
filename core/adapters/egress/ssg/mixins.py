# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - SSG Mixins
模块职责：提供 SSG 适配器的通用能力混入（物理容量降维分离）。
🛡️ [AEL-Iter-v5.3]：为缩减基座规模而进行的结构性抽象。
"""

class CITemplateMixin:
    """抽象 CI/CD 集成模板数据，分离自 BaseSSGAdapter 核心逻辑"""
    
    @classmethod
    def get_deploy_script_template(cls) -> str:
        """🚀 [V78.0] 返回本地一键部署的通用 shell 脚本模板"""
        return """#!/bin/bash
# 🚀 Illacme Plenipes Sovereign Local Deployment Script
# SSG Type: {ssg_type}
# Generated at: {datetime}

set -e

echo "🟢 1. 正在执行 {ssg_type} 的依赖核验与安装..."
if [ -f "package.json" ]; then
    npm install
fi

echo "📦 2. 开始构建生产环境静态站点..."
{build_cmd}

echo "🚀 3. 部署资产对正完毕，就绪发布！"
"""

    @classmethod
    def get_github_actions_template(cls) -> str:
        """🚀 [V78.0] 返回 GitHub Actions CI/CD 流水线模板"""
        return """name: Deploy Sovereign Website

on:
  push:
    branches:
      - main
      - master

permissions:
  contents: write
  pages: write
  id-token: write

concurrency:
  group: 'pages'
  cancel-in-progress: true

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          
      - name: Install Dependencies
        run: npm ci || npm install
        
      - name: Build Site
        run: {build_cmd}
        
      - name: Upload Artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: {site_dir}
          
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
"""
