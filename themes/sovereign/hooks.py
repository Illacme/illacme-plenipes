#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Default Theme Hooks
职责：处理默认主题特有的生命周期逻辑，如博客列表合成。
"""

import sys
import os

# 🚀 [V1.1] 动态加载主题内部脚本 (实现主权闭环)
theme_dir = os.path.dirname(__file__)
scripts_dir = os.path.join(theme_dir, "scripts")
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

try:
    from blog_synthesizer import BlogSynthesizer
except ImportError:
    # 兼容性兜底
    from .scripts.blog_synthesizer import BlogSynthesizer

from core.utils.tracing import tlog

def on_post_sync(engine):
    """
    当同步完成后，默认主题会自动合成博客列表，并自动生成根目录重定向 index.html。
    """
    args = getattr(engine, 'args', None)
    if args and getattr(args, 'dry_run', False):
        tlog.info("🧪 [主题钩子] 处于演练模式，跳过默认主题博客列表合成与重定向生成。")
        return

    tlog.info("🎨 [主题钩子] 默认主题正在执行资产合成...")
    
    # 🚀 [V1.2] 获取动态品牌输出路径
    dist_dir = engine.paths.get('site_dir') or engine.paths.get('target_base')
    if not dist_dir:
        tlog.error("❌ [主题钩子] 无法解析输出根目录 site_dir 或 target_base！")
        return
        
    # 调用主题私有合成器
    BlogSynthesizer.synthesize(engine, dist_dir)

    # 🚀 [V1.3] 动态扫描真实存在的静态文档，自动推导最佳首页入口
    all_html_files = []
    for root, _, files in os.walk(dist_dir):
        for f in files:
            if f.endswith(".html") and f != "index.html":
                rel = os.path.relpath(os.path.join(root, f), dist_dir).replace("\\", "/")
                all_html_files.append(rel)

    force_prefix = getattr(getattr(engine.config, 'i18n_settings', None), 'force_source_prefix', False)
    default_lang = getattr(getattr(engine.config, 'i18n_settings', None), 'source', None)
    default_code = getattr(default_lang, 'lang_code', 'zh') if default_lang else 'zh'

    if force_prefix:
        preferred_order = [
            lambda p: p.startswith(f"{default_code}/docs") and ("creator-5-minute" in p or "quick-start" in p),
            lambda p: p.startswith(f"{default_code}/docs"),
            lambda p: "creator-5-minute" in p or "quick-start" in p,
            lambda p: p.startswith(f"{default_code}/"),
            lambda p: True
        ]
    else:
        preferred_order = [
            lambda p: p.startswith("docs/") and ("creator-5-minute" in p or "quick-start" in p),
            lambda p: p.startswith("docs/"),
            lambda p: "creator-5-minute" in p or "quick-start" in p,
            lambda p: not p.startswith(f"{default_code}/") and "docs" in p,
            lambda p: True
        ]
    redirect_url = f"{default_code}/docs/creator-5-minute-quick-start-guide.html" if force_prefix else "docs/creator-5-minute-quick-start-guide.html"
    for matcher in preferred_order:
        matched = [p for p in all_html_files if matcher(p)]
        if matched:
            redirect_url = matched[0]
            break

    # 🚀 [V1.4] 检查是否已存在真实渲染的首页内容 (如来自 vault/index.md)
    index_file = os.path.join(dist_dir, "index.html")
    has_real_index = False
    if os.path.exists(index_file):
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 判定是否为真正的内容首页（带有主权引擎样式结构，而非跳转脚手架）
                if ("sovereign-engine" in content or "glass-header" in content) and "http-equiv=\"refresh\"" not in content:
                    has_real_index = True
                    tlog.info("🏠 [主题钩子] 侦测到物理主权真实首页 (index.html)，保留内容，豁免重定向覆盖。")
        except Exception:
            pass

    if not has_real_index:
        tlog.info(f"✨ [主题钩子] 自动锚定站点首选着陆页: {redirect_url}")
        # 生成高大上赛博风格重定向文件
        redirect_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url={redirect_url}">
    <title>正在进入发行指挥中心...</title>
    <style>
        body {{
            background-color: #0b0f19;
            color: #f3f4f6;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            overflow: hidden;
        }}
        .container {{
            text-align: center;
        }}
        .spinner {{
            width: 48px;
            height: 48px;
            border: 3px solid rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            border-top-color: #3b82f6;
            animation: spin 1s ease-in-out infinite;
            margin: 0 auto 24px;
        }}
        .title {{
            font-size: 18px;
            font-weight: 500;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
            opacity: 0.9;
        }}
        .sub {{
            font-size: 14px;
            color: #9ca3af;
            opacity: 0.8;
        }}
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="spinner"></div>
        <div class="title">正在加载出版成品...</div>
        <div class="sub">即将进入指挥中心</div>
    </div>
    <script>
        window.location.replace("{redirect_url}");
    </script>
</body>
</html>"""

        try:
            os.makedirs(os.path.dirname(index_file), exist_ok=True)
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(redirect_html)
            tlog.info(f"✨ [主题钩子] 已自动生成根目录重定向文件: {index_file} -> {redirect_url}")
        except Exception as e:
            tlog.error(f"❌ [主题钩子] 自动生成重定向文件失败: {e}")

    # 🛡️ 递归为所有缺少 index.html 的子目录生成自愈重定向，彻底杜绝 Directory listing
    for root, dirs, files in os.walk(dist_dir):
        if "index.html" not in files:
            rel_to_root = os.path.relpath(dist_dir, root).replace("\\", "/")
            target_rel_url = redirect_url if rel_to_root == "." else f"{rel_to_root}/{redirect_url}"
            sub_redirect_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url={target_rel_url}">
    <title>正在进入发行指挥中心...</title>
</head>
<body>
    <script>window.location.replace("{target_rel_url}");</script>
</body>
</html>"""
            try:
                with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as f:
                    f.write(sub_redirect_html)
            except Exception:
                pass

