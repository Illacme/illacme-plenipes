# -*- coding: utf-8 -*-
"""
📚 [V125.0] Illacme Plenipes - Book Colophon (版记 / 出版版权页) Builder
职责：统计全书指标（字数、章节）、提取 Git 指纹与时间戳，渲染标准出版物版记 XHTML。
规范：遵循 SOP-01 规范，单文件行数严格 ≤ 300 行。
"""

import os
import re
import uuid
import datetime
import subprocess
from typing import Dict, Any, List
from xml.sax.saxutils import escape

COLOPHON_I18N = {
    "zh": {
        "header": "📖 出版物版记 · COLOPHON",
        "title": "作品名称",
        "author": "著作者",
        "publisher": "出版出品",
        "format": "装帧规格",
        "chapters": "篇目容量",
        "chapters_val": "{count} 篇章节",
        "words": "全书规模",
        "words_val": "约 {words:,} 字",
        "build_time": "装订时间",
        "fingerprint": "构建指纹",
        "uuid": "物权编码",
        "default_license": "保留所有权利 · All Rights Reserved (基于 Illacme Plenipes 出版体系规范装订)",
        "footer": "Compiled with ♥ by Illacme Plenipes Bindery Engine",
        "epub_format": "EPUB 3.0 (IDPF / W3C 标准流式版式)",
        "webbook_format": "WebBook (单文件离线交互式典籍)",
        "nav_label": "版记 · Colophon"
    },
    "en": {
        "header": "📖 COLOPHON",
        "title": "Title",
        "author": "Author",
        "publisher": "Publisher",
        "format": "Edition Format",
        "chapters": "Contents",
        "chapters_val": "{count} Chapters",
        "words": "Length",
        "words_val": "Approx. {words:,} words",
        "build_time": "Publication Date",
        "fingerprint": "Build Fingerprint",
        "uuid": "Digital Identifier (UUID)",
        "default_license": "All Rights Reserved (Compiled via Illacme Plenipes Bindery Hub)",
        "footer": "Compiled with ♥ by Illacme Plenipes Bindery Engine",
        "epub_format": "EPUB 3.0 (IDPF / W3C Flowable Standard)",
        "webbook_format": "WebBook (Interactive Single-File Edition)",
        "nav_label": "Colophon"
    },
    "ja": {
        "header": "📖 奥付 · COLOPHON",
        "title": "作品名",
        "author": "著者",
        "publisher": "発行元",
        "format": "装丁仕様",
        "chapters": "収録規模",
        "chapters_val": "{count} 項目",
        "words": "総文字数",
        "words_val": "約 {words:,} 字",
        "build_time": "発行日",
        "fingerprint": "ビルド識別子",
        "uuid": "デジタル物権コード (UUID)",
        "default_license": "無断複写・転載を禁ず · All Rights Reserved (Illacme Plenipes 出版体系規範)",
        "footer": "Compiled with ♥ by Illacme Plenipes Bindery Engine",
        "epub_format": "EPUB 3.0 (IDPF / W3C 標準リフロー版)",
        "webbook_format": "WebBook (対話型スタンドアロン電子典籍)",
        "nav_label": "奥付 · Colophon"
    }
}


class ColophonBuilder:
    """数字出版物版记与物权指纹组装器"""

    @classmethod
    def get_i18n_dict(cls, lang: str) -> Dict[str, str]:
        """获取目标语种的版记国际化字典"""
        code = (lang or "zh").lower().split("-")[0].split("_")[0]
        return COLOPHON_I18N.get(code, COLOPHON_I18N.get("en", COLOPHON_I18N["zh"]))

    @classmethod
    def get_nav_label(cls, lang: str) -> str:
        """获取目录跳转项的标题（如 版记 / Colophon / 奥付）"""
        return cls.get_i18n_dict(lang).get("nav_label", "版记 · Colophon")

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
        """精确统计全书纯文本总字数 (中日韩字符 + 英文词)"""
        total = 0
        tag_re = re.compile(r'<[^>]+>')
        cjk_re = re.compile(r'[\u4e00-\u9fa5\u3040-\u30ff\uac00-\ud7af]')
        en_re = re.compile(r'[a-zA-Z0-9_-]+')

        for ch in manuscript_tree:
            raw_html = ch.get("html_body") or ""
            clean_text = tag_re.sub(' ', raw_html)
            title = ch.get("title") or ""
            text = f"{title} {clean_text}"
            cjk_count = len(cjk_re.findall(text))
            en_count = len(en_re.findall(text))
            total += (cjk_count + en_count)

        return total

    @classmethod
    def build_colophon_data(
        cls,
        manuscript_tree: List[Dict[str, Any]],
        book_metadata: Dict[str, Any],
        format_name: str = "epub"
    ) -> Dict[str, Any]:
        """汇总全书版记指标、自动注入物权编码 UUID 与多语言本地化配置"""
        lang = str(book_metadata.get("language") or "zh").lower()
        i18n = cls.get_i18n_dict(lang)

        total_words = book_metadata.get("word_count")
        if total_words is None:
            total_words = cls.calculate_total_words(manuscript_tree)

        git_hash = book_metadata.get("git_hash") or cls.get_git_commit_hash()
        build_time = book_metadata.get("build_time") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 物权编码自愈：杜绝 N/A，生成全局唯一数字物权标识 (URN:UUID)
        raw_uuid = book_metadata.get("uuid")
        if not raw_uuid or str(raw_uuid).strip() in ("N/A", "none", "None", ""):
            raw_uuid = f"urn:uuid:{uuid.uuid4()}"
        elif not str(raw_uuid).startswith("urn:uuid:"):
            raw_uuid = f"urn:uuid:{raw_uuid}"
        book_metadata["uuid"] = raw_uuid

        # 格式规格名称多语言适配
        fmt_lower = str(format_name).lower()
        if "webbook" in fmt_lower:
            resolved_fmt = i18n["webbook_format"]
        elif "epub" in fmt_lower:
            resolved_fmt = i18n["epub_format"]
        else:
            resolved_fmt = format_name

        raw_lic = book_metadata.get("license")
        if not raw_lic or ("保留所有权利" in str(raw_lic) and lang != "zh"):
            license_text = i18n["default_license"]
        else:
            license_text = raw_lic

        return {
            "title": book_metadata.get("title", "Digital Publication"),
            "author": book_metadata.get("author", "Illacme Press Author"),
            "publisher": book_metadata.get("publisher", "Illacme Plenipes Global Private Press"),
            "format_name": resolved_fmt,
            "format_raw": format_name,
            "chapter_count": len(manuscript_tree),
            "total_words": total_words,
            "build_time": build_time,
            "git_hash": git_hash,
            "uuid": raw_uuid,
            "license": license_text,
            "custom_license": raw_lic,
            "lang": lang
        }

    @classmethod
    def render_xhtml(cls, data: Dict[str, Any], iso_lang: str = "zh-CN") -> str:
        """渲染高质感、自适应多语种版记 (Colophon / 奥付) XHTML"""
        # 核心：必须以当前指定的目标渲染语种 iso_lang 为最高优先级，消除多语种 mul 阴影覆盖
        target_lang = iso_lang or data.get("lang") or "zh"
        if str(target_lang).lower() in ("mul", "polyglot"):
            target_lang = "zh"
        code = str(target_lang).lower().split("-")[0].split("_")[0]
        i18n = cls.get_i18n_dict(code)

        ch_val = i18n["chapters_val"].format(count=data.get('chapter_count', 0))
        w_val = i18n["words_val"].format(words=data.get('total_words', 0))

        # 根据当前语种动态适配规格名称
        fmt_raw = str(data.get("format_raw") or data.get("format_name") or "webbook").lower()
        if "webbook" in fmt_raw:
            resolved_fmt = i18n["webbook_format"]
        elif "epub" in fmt_raw:
            resolved_fmt = i18n["epub_format"]
        else:
            resolved_fmt = data.get("format_name") or fmt_raw

        # 版权声明多语言适配
        custom_lic = data.get("custom_license")
        if not custom_lic or ("保留所有权利" in str(custom_lic) and code != "zh"):
            license_text = i18n["default_license"]
        else:
            license_text = custom_lic

        return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{iso_lang}">
<head>
  <title>{escape(i18n['nav_label'])}</title>
  <link rel="stylesheet" href="../styles/epub.css"/>
</head>
<body class="colophon-page">
  <div class="colophon-card">
    <div class="colophon-header">{escape(i18n['header'])}</div>
    <table class="colophon-grid">
      <tr><td class="k">{escape(i18n['title'])}</td><td class="v"><strong>{escape(str(data['title']))}</strong></td></tr>
      <tr><td class="k">{escape(i18n['author'])}</td><td class="v">{escape(str(data['author']))}</td></tr>
      <tr><td class="k">{escape(i18n['publisher'])}</td><td class="v">{escape(str(data['publisher']))}</td></tr>
      <tr><td class="k">{escape(i18n['format'])}</td><td class="v">{escape(str(resolved_fmt))}</td></tr>
      <tr><td class="k">{escape(i18n['chapters'])}</td><td class="v">{escape(ch_val)}</td></tr>
      <tr><td class="k">{escape(i18n['words'])}</td><td class="v">{escape(w_val)}</td></tr>
      <tr><td class="k">{escape(i18n['build_time'])}</td><td class="v">{escape(str(data['build_time']))}</td></tr>
      <tr><td class="k">{escape(i18n['fingerprint'])}</td><td class="v"><code>{escape(str(data['git_hash']))}</code></td></tr>
      <tr><td class="k">{escape(i18n['uuid'])}</td><td class="v"><small style="font-family:monospace; color:#38bdf8;">{escape(str(data['uuid']))}</small></td></tr>
    </table>
    <div class="colophon-footer">
      <p>{escape(str(license_text))}</p>
      <p style="margin-top: 8px; opacity: 0.75;">{escape(i18n['footer'])}</p>
    </div>
  </div>
 </body>
</html>"""
