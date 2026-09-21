# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Image Packager (电子书插图打包与离线路径自愈器)
模块职责：探测并解析文档中的本地图片引用，安全重定向为电子书内部 images/ 规范路径并抽取物理资产。
🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
"""

import os
import re
import hashlib
from typing import Dict, Any, List, Tuple, Optional


class ImagePackager:
    """🖼️ 电子书插图打包与离线路径自愈器"""

    MIME_MAP = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
        ".bmp": "image/bmp"
    }

    @classmethod
    def heal_obsidian_embedded_images(cls, markdown_text: str) -> str:
        """
        将 Obsidian 特有的 ![[image.png]] 或 ![[image.png|300]] 语法
        转译为标准 Markdown / HTML 图像语法
        """
        def repl(m):
            raw_target = m.group(1).strip()
            parts = raw_target.split('|')
            img_file = parts[0].strip()
            ext = os.path.splitext(img_file)[1].lower()
            if ext not in cls.MIME_MAP:
                return m.group(0)

            width_style = ""
            if len(parts) > 1:
                spec = parts[1].strip()
                w_match = re.match(r'^(\d+)(?:x\d+)?$', spec)
                if w_match:
                    width_style = f' style="max-width: {w_match.group(1)}px;"'

            alt_text = os.path.splitext(os.path.basename(img_file))[0]
            return f'<img src="{img_file}" alt="{alt_text}"{width_style} />'

        return re.sub(r'!\[\[([^\]]+)\]\]', repl, markdown_text)

    @classmethod
    def locate_local_image(cls, raw_src: str, doc_path: str, vault_dir: str) -> Optional[str]:
        """
        多层级本地物理图片寻址探测算法：
        1. 章节当前所在目录及其 ./assets, ./attachments
        2. 文库根目录与全局 assets / attachments 目录
        3. 相对项目根目录
        """
        if not raw_src or raw_src.startswith(('http://', 'https://', 'data:', 'mailto:', 'tel:')):
            return None

        clean_src = raw_src.split('?')[0].split('#')[0].strip()
        doc_dir = os.path.dirname(os.path.abspath(doc_path))
        base_name = os.path.basename(clean_src)

        candidates = [
            os.path.normpath(os.path.join(doc_dir, clean_src)),
            os.path.normpath(os.path.join(doc_dir, "assets", base_name)),
            os.path.normpath(os.path.join(doc_dir, "attachments", base_name)),
            os.path.normpath(os.path.join(vault_dir, clean_src.lstrip('/'))),
            os.path.normpath(os.path.join(vault_dir, "assets", base_name)),
            os.path.normpath(os.path.join(vault_dir, "attachments", base_name)),
            os.path.normpath(os.path.join(".", clean_src.lstrip('/')))
        ]

        for cand in candidates:
            if os.path.isfile(cand):
                return cand

        return None

    @classmethod
    def extract_and_heal_images(
        cls,
        html_content: str,
        doc_path: str,
        vault_dir: str
    ) -> Tuple[str, List[Dict[str, str]]]:
        """
        扫描 HTML 正文中的所有 <img> 标签，定位物理图片并重写为电子书规范路径 ../images/xxx
        返回：(自愈后的 HTML, 收集到的物理资产列表)
        """
        assets: List[Dict[str, str]] = []
        seen_paths: Dict[str, str] = {}

        def repl(m):
            full_tag = m.group(0)
            raw_src = m.group(1).strip()
            abs_img_path = cls.locate_local_image(raw_src, doc_path, vault_dir)

            if not abs_img_path:
                return full_tag

            if abs_img_path in seen_paths:
                target_name = seen_paths[abs_img_path]
            else:
                ext = os.path.splitext(abs_img_path)[1].lower() or ".png"
                name_hash = hashlib.md5(abs_img_path.encode('utf-8')).hexdigest()[:8]
                clean_stem = re.sub(r'[^\w\-]+', '_', os.path.splitext(os.path.basename(abs_img_path))[0])
                target_name = f"img_{name_hash}_{clean_stem}{ext}"
                seen_paths[abs_img_path] = target_name

                assets.append({
                    "src_path": abs_img_path,
                    "abs_path": abs_img_path,
                    "target_name": target_name,
                    "mime_type": cls.MIME_MAP.get(ext, "image/png"),
                    "original_src": raw_src
                })

            new_src = f"../images/{target_name}"
            healed_tag = full_tag.replace(f'src="{raw_src}"', f'src="{new_src}"')
            healed_tag = healed_tag.replace(f"src='{raw_src}'", f"src='{new_src}'")
            return healed_tag

        healed_html = re.sub(r'<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*>', repl, html_content)
        return healed_html, assets
