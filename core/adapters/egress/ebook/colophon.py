# -*- coding: utf-8 -*-
"""
📚 [V125.0] Illacme Plenipes - Book Colophon (版记 / 出版版权页) Builder
职责：统计全书指标（字数、章节）、提取 Git 指纹与时间戳，渲染标准出版物版记 XHTML。
规范：遵循 SOP-01 规范，单文件行数严格 ≤ 300 行。
"""

import re
import datetime
import subprocess
from typing import Dict, Any, List
from xml.sax.saxutils import escape


class ColophonBuilder:
    """数字出版物版记与物权指纹组装器"""

    @classmethod
    def get_git_commit_hash(cls) -> str:
        """提取当前仓库的短提交哈希"""
        try:
            res = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
            return res if res else "HEAD-RELEASE"
        except Exception:
            return "HEAD-RELEASE"

    @classmethod
    def calculate_total_words(cls, manuscript_tree: List[Dict[str, Any]]) -> int:
        """精确统计全书纯文本总字数 (中文字符 + 英文词)"""
        total = 0
        tag_re = re.compile(r'<[^>]+>')
        zh_re = re.compile(r'[\u4e00-\u9fa5]')
        en_re = re.compile(r'[a-zA-Z0-9_-]+')

        for ch in manuscript_tree:
            raw_html = ch.get("html_body") or ""
            clean_text = tag_re.sub(' ', raw_html)
            title = ch.get("title") or ""
            text = f"{title} {clean_text}"

            zh_count = len(zh_re.findall(text))
            en_count = len(en_re.findall(text))
            total += (zh_count + en_count)

        return total

    @classmethod
    def build_colophon_data(
        cls,
        manuscript_tree: List[Dict[str, Any]],
        book_metadata: Dict[str, Any],
        format_name: str = "EPUB 3.0 (IDPF / W3C 标准流式版式)"
    ) -> Dict[str, Any]:
        """汇总全书版记指标与元数据"""
        total_words = book_metadata.get("word_count")
        if total_words is None:
            total_words = cls.calculate_total_words(manuscript_tree)

        git_hash = book_metadata.get("git_hash") or cls.get_git_commit_hash()
        build_time = book_metadata.get("build_time") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        license_text = book_metadata.get(
            "license",
            "保留所有权利 · All Rights Reserved (基于 Illacme Plenipes 出版体系规范装订)"
        )

        return {
            "title": book_metadata.get("title", "未命名出版物"),
            "author": book_metadata.get("author", "极客创作者"),
            "publisher": book_metadata.get("publisher", "Illacme Plenipes Global Private Press"),
            "format_name": format_name,
            "chapter_count": len(manuscript_tree),
            "total_words": total_words,
            "build_time": build_time,
            "git_hash": git_hash,
            "uuid": book_metadata.get("uuid", "N/A"),
            "license": license_text
        }

    @classmethod
    def render_xhtml(cls, data: Dict[str, Any], iso_lang: str = "zh-CN") -> str:
        """渲染高质感版记 XHTML 页面"""
        return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{iso_lang}">
<head>
  <title>版记 · Colophon</title>
  <link rel="stylesheet" href="../styles/epub.css"/>
</head>
<body class="colophon-page">
  <div class="colophon-card">
    <div class="colophon-header">📖 出版物版记 · COLOPHON</div>
    <table class="colophon-grid">
      <tr><td class="k">作品名称</td><td class="v"><strong>{escape(str(data['title']))}</strong></td></tr>
      <tr><td class="k">著作者</td><td class="v">{escape(str(data['author']))}</td></tr>
      <tr><td class="k">出版出品</td><td class="v">{escape(str(data['publisher']))}</td></tr>
      <tr><td class="k">装帧规格</td><td class="v">{escape(str(data['format_name']))}</td></tr>
      <tr><td class="k">篇目容量</td><td class="v">{data['chapter_count']} 篇章节</td></tr>
      <tr><td class="k">全书规模</td><td class="v">约 {data['total_words']:,} 字</td></tr>
      <tr><td class="k">装订时间</td><td class="v">{escape(str(data['build_time']))}</td></tr>
      <tr><td class="k">构建指纹</td><td class="v"><code>{escape(str(data['git_hash']))}</code></td></tr>
      <tr><td class="k">物权编码</td><td class="v"><small>{escape(str(data['uuid']))}</small></td></tr>
    </table>
    <div class="colophon-footer">
      <p>{escape(str(data['license']))}</p>
      <p style="margin-top: 8px; opacity: 0.75;">Compiled with ♥ by Illacme Plenipes Bindery Engine</p>
    </div>
  </div>
</body>
</html>"""
