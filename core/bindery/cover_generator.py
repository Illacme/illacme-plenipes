# -*- coding: utf-8 -*-
"""
📚 [V125.0] Illacme Plenipes - Book Cover Generator & Discoverer Shard
职责：原稿文库原生封面挖掘、多风格矢量排版艺术封面自动生成与光栅化渲染。
规范：遵循 SOP-01 规范，纯 Python 极简优雅架构，单文件行数严格 ≤ 300 行。
"""

import os
import io
import re
import base64
from typing import Optional, Dict, Any, List
from xml.sax.saxutils import escape

# 预设高档装帧排版配色与设计矩阵
COVER_STYLES = {
    "dark_emerald": {
        "id": "dark_emerald",
        "name": "黑曜翡翠",
        "bg_top": "#0b1219",
        "bg_bottom": "#030708",
        "accent": "#10b981",
        "accent_glow": "rgba(16, 185, 129, 0.4)",
        "accent_sub": "#059669",
        "text_main": "#ffffff",
        "text_sub": "#94a3b8",
        "border": "#10b981"
    },
    "classic_navy": {
        "id": "classic_navy",
        "name": "藏青午夜",
        "bg_top": "#0f172a",
        "bg_bottom": "#020617",
        "accent": "#38bdf8",
        "accent_glow": "rgba(56, 189, 248, 0.4)",
        "accent_sub": "#0284c7",
        "text_main": "#f8fafc",
        "text_sub": "#94a3b8",
        "border": "#38bdf8"
    },
    "obsidian_gold": {
        "id": "obsidian_gold",
        "name": "黑金雅致",
        "bg_top": "#181411",
        "bg_bottom": "#090706",
        "accent": "#f59e0b",
        "accent_glow": "rgba(245, 158, 11, 0.4)",
        "accent_sub": "#d97706",
        "text_main": "#fef3c7",
        "text_sub": "#a8a29e",
        "border": "#f59e0b"
    }
}


class CoverGenerator:
    """数字出版物封面挖掘与排版生成中枢"""

    @classmethod
    def discover_cover(
        cls,
        vault_dir: str,
        category: str = "",
        chapters: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[str]:
        """多级自愈探测原稿文库中的物理封面图片"""
        if not vault_dir or not os.path.exists(vault_dir):
            return None

        candidates = []
        exts = [".jpg", ".jpeg", ".png", ".webp"]

        # 1. 栏目特定专属封面
        if category:
            cat_dir = os.path.join(vault_dir, category)
            for ext in exts:
                candidates.append(os.path.join(cat_dir, f"cover{ext}"))
                candidates.append(os.path.join(cat_dir, "assets", f"cover{ext}"))
                candidates.append(os.path.join(vault_dir, f"{category}{ext}"))

        # 2. 全局通用资产封面
        for ext in exts:
            candidates.append(os.path.join(vault_dir, "assets", f"cover{ext}"))
            candidates.append(os.path.join(vault_dir, f"cover{ext}"))

        for path in candidates:
            if os.path.isfile(path) and os.path.getsize(path) > 0:
                return os.path.abspath(path)

        # 3. 扫描各章节 Frontmatter 中显式声明的 cover 或 banner
        if chapters:
            for ch in chapters:
                fm = ch.get("frontmatter") or {}
                raw_cover = fm.get("cover") or fm.get("banner")
                if raw_cover and isinstance(raw_cover, str):
                    clean_p = raw_cover.lstrip("./").lstrip("/")
                    # 尝试相对文库路径或绝对路径
                    check_paths = [
                        os.path.join(vault_dir, clean_p),
                        os.path.join(vault_dir, category, clean_p) if category else None,
                        clean_p if os.path.isabs(clean_p) else None
                    ]
                    for p in check_paths:
                        if p and os.path.isfile(p) and os.path.getsize(p) > 0:
                            return os.path.abspath(p)

        return None

    @classmethod
    def generate_svg_cover(
        cls,
        title: str,
        author: str = "Illacme Editorial Team",
        publisher: str = "Illacme Plenipes Press",
        style_key: str = "dark_emerald",
        lang: str = "zh"
    ) -> str:
        """生成国际标准 1:1.6 (1600x2560) 比例的高保真矢量排版装帧封面"""
        style = COVER_STYLES.get(style_key, COVER_STYLES["dark_emerald"])

        clean_title = (title or "数字出版合集").strip()
        clean_author = (author or "Illacme Editorial Team").strip()
        clean_pub = (publisher or "Illacme Plenipes Global Press").strip()

        # 标题多行智能拆分
        words = clean_title.split()
        if len(clean_title) > 12 and len(words) == 1:
            lines = [clean_title[i:i + 10] for i in range(0, len(clean_title), 10)]
        elif len(clean_title) > 20:
            lines = []
            curr = ""
            for w in words:
                if len(curr) + len(w) > 16:
                    lines.append(curr.strip())
                    curr = w + " "
                else:
                    curr += w + " "
            if curr.strip():
                lines.append(curr.strip())
        else:
            lines = [clean_title]

        # 计算字体大小与行高
        title_font_size = 108 if len(lines) <= 2 else 92
        start_y = 1060 - ((len(lines) - 1) * title_font_size * 0.7)

        title_tspans = []
        for i, line in enumerate(lines):
            y_pos = start_y + (i * title_font_size * 1.35)
            title_tspans.append(f'<tspan x="800" y="{y_pos:.0f}">{escape(line)}</tspan>')

        title_block = "\n    ".join(title_tspans)
        lang_badge = "EDITION · 中文版" if lang == "zh" else f"EDITION · {lang.upper()}"

        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 2560" width="1600" height="2560">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{style['bg_top']}"/>
      <stop offset="100%" stop-color="{style['bg_bottom']}"/>
    </linearGradient>
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{style['accent']}"/>
      <stop offset="100%" stop-color="{style['accent_sub']}"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="30" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- 背景画布 -->
  <rect width="1600" height="2560" fill="url(#bgGrad)"/>

  <!-- 艺术外围双内框 -->
  <rect x="90" y="90" width="1420" height="2380" fill="none" stroke="{style['border']}" stroke-width="3" stroke-opacity="0.25" rx="16"/>
  <rect x="110" y="110" width="1380" height="2340" fill="none" stroke="{style['border']}" stroke-width="1.5" stroke-opacity="0.45" rx="12"/>

  <!-- 顶部出版社徽章 -->
  <g transform="translate(800, 360)" text-anchor="middle">
    <rect x="-160" y="-36" width="320" height="72" rx="36" fill="{style['accent']}" fill-opacity="0.12" stroke="{style['accent']}" stroke-width="1.5" stroke-opacity="0.5"/>
    <text y="9" font-family="-apple-system, sans-serif" font-size="28" font-weight="700" fill="{style['accent']}" letter-spacing="4">{lang_badge}</text>
  </g>

  <!-- 顶部装饰几何微标 -->
  <g transform="translate(800, 620)" text-anchor="middle">
    <circle r="44" fill="none" stroke="{style['accent']}" stroke-width="2" stroke-dasharray="6,4" stroke-opacity="0.6"/>
    <polygon points="0,-22 20,14 -20,14" fill="{style['accent']}" fill-opacity="0.8"/>
  </g>

  <!-- 居中主标题 -->
  <g text-anchor="middle" font-family="-apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif" font-weight="800" fill="{style['text_main']}" letter-spacing="2">
    <text font-size="{title_font_size}">
    {title_block}
    </text>
  </g>

  <!-- 装饰水平分割线 -->
  <g transform="translate(800, 1560)">
    <line x1="-300" y1="0" x2="300" y2="0" stroke="{style['accent']}" stroke-width="3" stroke-opacity="0.7"/>
    <circle cx="0" cy="0" r="8" fill="{style['accent']}"/>
  </g>

  <!-- 著者署名 -->
  <g transform="translate(800, 1780)" text-anchor="middle" font-family="-apple-system, 'PingFang SC', sans-serif">
    <text y="0" font-size="36" font-weight="400" fill="{style['text_sub']}" letter-spacing="6">AUTHOR / 著</text>
    <text y="70" font-size="64" font-weight="700" fill="{style['text_main']}" letter-spacing="3">{escape(clean_author)}</text>
  </g>

  <!-- 底部品牌与防伪压印徽章 -->
  <g transform="translate(800, 2220)" text-anchor="middle" font-family="-apple-system, sans-serif">
    <text y="0" font-size="34" font-weight="600" fill="{style['accent']}" letter-spacing="5">{escape(clean_pub)}</text>
    <text y="48" font-size="24" font-weight="400" fill="{style['text_sub']}" letter-spacing="3">DIGITAL LUXURY BINDERY · EPUB 3.0</text>
  </g>
</svg>"""

    @staticmethod
    def _load_font(size: int):
        from PIL import ImageFont
        candidates = [
            "/System/Library/Fonts/STHeiti Light.ttc", "/System/Library/Fonts/Supplemental/Songti.ttc",
            "/System/Library/Fonts/PingFang.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", "C:/Windows/Fonts/msyh.ttc"
        ]
        for c in candidates:
            if os.path.exists(c):
                try: return ImageFont.truetype(c, size=size)
                except Exception: pass
        try: return ImageFont.load_default(size=size)
        except Exception: return ImageFont.load_default()

    @classmethod
    def render_cover_image(
        cls,
        output_path: str,
        title: str,
        author: str = "Illacme Editorial Team",
        publisher: str = "Illacme Plenipes Press",
        style_key: str = "dark_emerald",
        lang: str = "zh"
    ) -> str:
        """渲染封面图片并落盘，使用超高清出版比例与大字号排版"""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        svg_content = cls.generate_svg_cover(title, author, publisher, style_key, lang)
        if output_path.lower().endswith(".svg"):
            with open(output_path, "w", encoding="utf-8") as f: f.write(svg_content)
            return output_path

        try:
            from PIL import Image, ImageDraw
            style = COVER_STYLES.get(style_key, COVER_STYLES["dark_emerald"])
            img = Image.new("RGB", (1600, 2560), style["bg_top"])
            draw = ImageDraw.Draw(img)

            # 内外艺术边框
            draw.rectangle([(90, 90), (1510, 2470)], outline=style["border"], width=4)
            draw.rectangle([(110, 110), (1490, 2450)], outline=style["border"], width=2)

            # 顶部徽章
            draw.rounded_rectangle([(620, 324), (980, 396)], radius=36, fill=style["bg_bottom"], outline=style["accent"], width=2)
            badge_text = "EDITION · 中文版" if lang == "zh" else f"EDITION · {lang.upper()}"
            draw.text((800, 360), badge_text, font=cls._load_font(28), fill=style["accent"], anchor="mm")

            # 居中大字号标题 (智能折行)
            clean_title = (title or "数字出版合集").strip()
            lines = [clean_title[i:i+10] for i in range(0, len(clean_title), 10)] if len(clean_title) > 12 else [clean_title]
            start_y = 1060 - ((len(lines) - 1) * 70)
            for idx, line in enumerate(lines):
                draw.text((800, start_y + idx * 140), line, font=cls._load_font(98), fill=style["text_main"], anchor="mm")

            # 装饰分割线与圆点
            draw.line([(500, 1560), (1100, 1560)], fill=style["accent"], width=3)
            draw.ellipse([(792, 1552), (808, 1568)], fill=style["accent"])
            # 著作者与出品方
            draw.text((800, 1750), "AUTHOR / 著", font=cls._load_font(36), fill=style["text_sub"], anchor="mm")
            draw.text((800, 1830), author or "Illacme Team", font=cls._load_font(58), fill=style["text_main"], anchor="mm")
            draw.text((800, 2220), publisher or "Illacme Press", font=cls._load_font(36), fill=style["accent"], anchor="mm")
            draw.text((800, 2270), "DIGITAL LUXURY BINDERY · EPUB 3.0", font=cls._load_font(24), fill=style["text_sub"], anchor="mm")
            img.save(output_path, quality=95)
            return output_path
        except Exception:
            svg_fallback_path = os.path.splitext(output_path)[0] + ".svg"
            with open(svg_fallback_path, "w", encoding="utf-8") as f: f.write(svg_content)
            return svg_fallback_path

    @classmethod
    def generate_cover_data_uri(
        cls,
        title: str,
        author: str = "Illacme Editorial Team",
        publisher: str = "Illacme Plenipes Press",
        style_key: str = "dark_emerald",
        lang: str = "zh"
    ) -> str:
        """生成供前端直接作为 <img src="..."> 渲染的 SVG Data URL"""
        svg_content = cls.generate_svg_cover(title, author, publisher, style_key, lang)
        b64 = base64.b64encode(svg_content.encode("utf-8")).decode("ascii")
        return f"data:image/svg+xml;base64,{b64}"
