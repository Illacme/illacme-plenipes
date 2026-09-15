# -*- coding: utf-8 -*-
"""
Illacme Plenipes — WeChat Article Formatter
职责：
1. 自动将正文中的外链提取并转换为优雅的角标与文末「参考资料」脚注；
2. 将 Markdown 编译并注入高颜值 Inline CSS 富文本，解决微信编辑器样式过滤问题。
🛡️ [SOP-01] 物理行数限制：保持在 300 行以内。
"""

import re
import markdown
from typing import Tuple, List, Dict, Any

WECHAT_WHITELIST_DOMAINS = (
    "weixin.qq.com",
    "mp.weixin.qq.com",
    "qq.com"
)

# 🎨 现代高质感内联样式字典
INLINE_STYLES = {
    "container": "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif; font-size: 15px; color: #334155; line-height: 1.8; letter-spacing: 0.5px; word-break: break-word;",
    "h1": "font-size: 22px; font-weight: 700; color: #0f172a; margin: 32px 0 16px; padding-bottom: 8px; border-bottom: 2px solid #2563eb; line-height: 1.4;",
    "h2": "font-size: 18px; font-weight: 700; color: #0f172a; margin: 26px 0 14px; padding-left: 10px; border-left: 4px solid #2563eb; line-height: 1.4;",
    "h3": "font-size: 16px; font-weight: 600; color: #1e293b; margin: 20px 0 10px; line-height: 1.4;",
    "h4": "font-size: 15px; font-weight: 600; color: #334155; margin: 16px 0 8px; line-height: 1.4;",
    "p": "font-size: 15px; color: #334155; line-height: 1.8; margin: 16px 0;",
    "blockquote": "margin: 20px 0; padding: 12px 18px; background: #f8fafc; border-left: 4px solid #3b82f6; border-radius: 4px; color: #475569; font-size: 14.5px; line-height: 1.7;",
    "code_inline": "background: #f1f5f9; color: #e11d48; padding: 2px 6px; border-radius: 4px; font-family: Consolas, Monaco, monospace; font-size: 13.5px; margin: 0 2px;",
    "pre": "background: #0f172a; color: #f8fafc; padding: 14px 16px; border-radius: 8px; overflow-x: auto; font-family: Consolas, Monaco, monospace; font-size: 13px; line-height: 1.65; margin: 20px 0;",
    "code_block": "color: #f8fafc; font-family: Consolas, Monaco, monospace; font-size: 13px;",
    "ul": "padding-left: 24px; margin: 14px 0; color: #334155; font-size: 15px; line-height: 1.8;",
    "ol": "padding-left: 24px; margin: 14px 0; color: #334155; font-size: 15px; line-height: 1.8;",
    "li": "margin-bottom: 6px;",
    "table": "width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; text-align: left;",
    "th": "background: #f1f5f9; border: 1px solid #cbd5e1; padding: 10px 14px; font-weight: 600; color: #0f172a;",
    "td": "border: 1px solid #e2e8f0; padding: 8px 14px; color: #475569;",
    "hr": "border: none; border-top: 1px dashed #cbd5e1; margin: 28px 0;",
    "strong": "font-weight: 700; color: #0f172a;",
    "em": "font-style: italic; color: #475569;",
    "img": "max-width: 100%; border-radius: 8px; margin: 16px auto; display: block; box-shadow: 0 4px 12px rgba(0,0,0,0.06);"
}


def is_external_link(url: str) -> bool:
    """判断是否为需要转换的非微信外链"""
    if not url:
        return False
    u = url.strip()
    if u.startswith("#") or u.startswith("javascript:"):
        return False
    # 白名单域名放行
    for domain in WECHAT_WHITELIST_DOMAINS:
        if domain in u:
            return False
    return u.startswith("http://") or u.startswith("https://")


def transmute_footnotes(content: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    将正文中的外链提取并转换为优雅的上标角标，返回处理后的内容与脚注列表。
    保持相同链接编号去重复用。
    """
    footnotes: List[Dict[str, str]] = []
    seen_urls: Dict[str, int] = {}

    # 正则匹配 [text](url)
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    def replace_link(match):
        text = match.group(1).strip()
        url = match.group(2).strip()

        if not is_external_link(url):
            return match.group(0)

        if url in seen_urls:
            idx = seen_urls[url]
        else:
            idx = len(footnotes) + 1
            seen_urls[url] = idx
            footnotes.append({"index": idx, "text": text, "url": url})

        sup_style = "color: #2563eb; font-weight: 600; font-size: 11px; margin-left: 2px;"
        return f'{text}<sup style="{sup_style}">[{idx}]</sup>'

    new_content = link_pattern.sub(replace_link, content)
    return new_content, footnotes


def build_footnotes_section(footnotes: List[Dict[str, str]]) -> str:
    """构造文末优雅的「参考资料」HTML 块"""
    if not footnotes:
        return ""

    items_html = []
    for fn in footnotes:
        items_html.append(
            f'<li style="margin-bottom: 6px; word-break: break-all;">'
            f'<span style="color: #2563eb; font-weight: 600;">[{fn["index"]}]</span> '
            f'{fn["text"]}: <span style="color: #64748b; text-decoration: underline;">{fn["url"]}</span>'
            f'</li>'
        )

    section_html = (
        '<section style="margin-top: 36px; padding-top: 20px; border-top: 1px dashed #cbd5e1; font-size: 13px; color: #64748b; line-height: 1.75;">'
        '<div style="font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 10px; display: flex; align-items: center; gap: 6px;">'
        '<span>📚 参考资料</span>'
        '</div>'
        '<ul style="list-style: none; padding-left: 0; margin: 0;">'
        + "".join(items_html) +
        '</ul>'
        '</section>'
    )
    return section_html


def apply_inline_styles(html: str) -> str:
    """为常用的 HTML 标签注入优雅内联 CSS 样式"""
    # 替换各种容器和排版标签
    replacements = [
        (r'<h1>', f'<h1 style="{INLINE_STYLES["h1"]}">'),
        (r'<h2>', f'<h2 style="{INLINE_STYLES["h2"]}">'),
        (r'<h3>', f'<h3 style="{INLINE_STYLES["h3"]}">'),
        (r'<h4>', f'<h4 style="{INLINE_STYLES["h4"]}">'),
        (r'<p>', f'<p style="{INLINE_STYLES["p"]}">'),
        (r'<blockquote>', f'<blockquote style="{INLINE_STYLES["blockquote"]}">'),
        (r'<hr\s*/?>', f'<hr style="{INLINE_STYLES["hr"]}">'),
        (r'<strong>', f'<strong style="{INLINE_STYLES["strong"]}">'),
        (r'<b>', f'<b style="{INLINE_STYLES["strong"]}">'),
        (r'<em>', f'<em style="{INLINE_STYLES["em"]}">'),
        (r'<ul>', f'<ul style="{INLINE_STYLES["ul"]}">'),
        (r'<ol>', f'<ol style="{INLINE_STYLES["ol"]}">'),
        (r'<li>', f'<li style="{INLINE_STYLES["li"]}">'),
        (r'<table>', f'<table style="{INLINE_STYLES["table"]}">'),
        (r'<th>', f'<th style="{INLINE_STYLES["th"]}">'),
        (r'<td>', f'<td style="{INLINE_STYLES["td"]}">'),
        (r'<img([^>]*)>', f'<img\\1 style="{INLINE_STYLES["img"]}">'),
    ]

    # 特殊处理 code 和 pre：区分代码块与行内代码
    mac_header = (
        '<div style="display: flex; align-items: center; gap: 6px; padding: 8px 12px; background: rgba(255,255,255,0.04); border-bottom: 1px solid rgba(255,255,255,0.08);">'
        '<span style="width: 9px; height: 9px; border-radius: 50%; background: #ff5f56; display: inline-block;"></span>'
        '<span style="width: 9px; height: 9px; border-radius: 50%; background: #ffbd2e; display: inline-block;"></span>'
        '<span style="width: 9px; height: 9px; border-radius: 50%; background: #27c93f; display: inline-block;"></span>'
        '</div>'
    )
    pre_wrapper_style = "background: #0f172a; border-radius: 8px; overflow: hidden; margin: 20px 0; box-shadow: 0 4px 14px rgba(0,0,0,0.12);"

    # 规范化 markdown codehilite 产生的类外壳
    html = re.sub(r'<div class="codehilite">', '', html)

    html = re.sub(
        r'<pre[^>]*>(?:\s*<span></span>\s*)?<code(?:\s+class="([^"]*)")?>',
        f'<div style="{pre_wrapper_style}">{mac_header}<pre style="{INLINE_STYLES["pre"]}; margin: 0; border-radius: 0;"><code style="{INLINE_STYLES["code_block"]}">',
        html
    )
    html = re.sub(r'</code></pre>(?:\s*</div>)?', '</code></pre></div>', html)

    # 处理未被 pre 包裹的行内 code
    def replace_inline_code(match):
        content = match.group(1)
        return f'<code style="{INLINE_STYLES["code_inline"]}">{content}</code>'

    # 使用分步替换保护代码块内部
    code_blocks = []
    def save_pre(m):
        code_blocks.append(m.group(0))
        return f"__WECHAT_PRE_BLOCK_{len(code_blocks)-1}__"

    html = re.sub(r'<div style="background: #0f172a.*?</code></pre>\s*</div>', save_pre, html, flags=re.DOTALL)
    html = re.sub(r'<code>(.*?)</code>', replace_inline_code, html, flags=re.DOTALL)
    for i, block in enumerate(code_blocks):
        html = html.replace(f"__WECHAT_PRE_BLOCK_{i}__", block)

    for pattern, repl in replacements:
        html = re.sub(pattern, repl, html)

    return f'<section style="{INLINE_STYLES["container"]}">{html}</section>'


def render_wechat_html(content: str, config: Dict[str, Any] = None) -> str:
    """
    将原始 Markdown 渲染为专为微信公众号定制的高保真富文本 HTML。
    可配置 convert_footnotes（默认为 True）。
    """
    config = config or {}
    convert_footnotes = config.get("convert_footnotes", True)

    # 剥离 Markdown 顶部的 YAML Frontmatter（避免元数据污染微信正文）
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2].strip()

    footnotes = []
    if convert_footnotes:
        content, footnotes = transmute_footnotes(content)

    # 编译 Markdown 为 HTML
    md_extensions = ['extra', 'codehilite', 'tables', 'nl2br']
    raw_html = markdown.markdown(content, extensions=md_extensions)

    # 注入内联 CSS
    styled_html = apply_inline_styles(raw_html)

    # 追加文末脚注卡片
    if footnotes:
        fn_section = build_footnotes_section(footnotes)
        styled_html += fn_section

    return styled_html
