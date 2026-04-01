#!/bin/bash

# 确保脚本有执行权限: chmod +x publish.sh

echo "🌉 Step 1: 运行 Bridge Pro 进行内容同步与 AI 处理..."
python3 bridge.py --sync

echo "🏗️ Step 2: 启动 Starlight (Astro) 静态构建..."
# 确保你在模板库根目录运行
npm run build

echo "🚀 Step 3: 推送网页库至 GitHub Pages..."
# 需要先安装: npm install gh-pages --save-dev
npx gh-pages -d dist -t true --message "Site updated: $(date +'%Y-%m-%d %H:%M:%S')"

echo "✅ 发布流程已全部完成！你的站点正在上线中..."