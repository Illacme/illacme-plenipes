#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - WeChat Image CDN Uploader Shard
模块职责：自动扫描微信推文中的正文图片，拉取本地或外部图床图片并转存至微信官方 CDN (media/uploadimg)。
彻底根除微信防盗链拦截、破图及本地图片无法显示痛点。
严格遵守 SOP-01 行数规范 (< 300 行)。
"""

import os
import re
from typing import Optional, Tuple, List, Dict
import requests
from core.utils.tracing import tlog
from .wechat_image_optimizer import optimize_image_for_wechat

# 微信白名单 CDN 域名特征，无需重复上传
WECHAT_CDN_DOMAINS = ("qpic.cn", "weixin.qq.com", "qq.com")

def is_wechat_cdn_image(url: str) -> bool:
    """检测 URL 是否已属于微信官方 CDN 或白名单域名"""
    if not url:
        return False
    lower_url = url.lower()
    return any(domain in lower_url for domain in WECHAT_CDN_DOMAINS)

def _get_proxies(proxy: Optional[str]) -> Optional[dict]:
    if not proxy:
        return None
    p = str(proxy).strip()
    return {"http": None, "https": None} if p.lower() == "direct" else {"http": p, "https": p}

def fetch_image_bytes(src: str, doc_dir: Optional[str] = None, proxy: Optional[str] = None, timeout: int = 10) -> Optional[Tuple[bytes, str]]:
    """
    拉取图片二进制数据与文件名
    支持外部网络图片（HTTP/HTTPS）与本地相对路径图片（寻址自愈）
    """
    if not src:
        return None

    # 0. 物理文件与设计中心 / ICMM 封面穿透解析
    clean_src = src.split('?')[0].split('#')[0].strip()
    if os.path.isfile(clean_src):
        try:
            with open(clean_src, "rb") as f: return f.read(), os.path.basename(clean_src)
        except Exception: pass

    cover_fn = os.path.basename(clean_src) if ("/api/design/assets/covers/" in clean_src or clean_src.startswith("covers/")) else None
    if cover_fn:
        c_paths = [
            os.path.join(os.getcwd(), "vault", ".plenipes", "cache", "covers", cover_fn),
            os.path.join(os.getcwd(), ".plenipes", "cache", "covers", cover_fn),
        ]
        try:
            from core.runtime.engine_singleton import get_global_engine
            eng = get_global_engine()
            if eng and getattr(eng, "vault_root", None):
                c_paths.insert(0, os.path.join(eng.vault_root, ".plenipes", "cache", "covers", cover_fn))
        except Exception: pass
        if doc_dir:
            cur = os.path.abspath(doc_dir)
            while cur and cur != os.path.dirname(cur):
                c_paths.extend([os.path.join(cur, ".plenipes", "cache", "covers", cover_fn), os.path.join(cur, "cache", "covers", cover_fn)])
                cur = os.path.dirname(cur)
        for cp in c_paths:
            if os.path.isfile(cp):
                try:
                    with open(cp, "rb") as f: return f.read(), cover_fn
                except Exception: pass
        try:
            from services.api.routes.design_shards.cover_asset_healer import serve_cover_asset_or_heal
            from core.runtime.engine_singleton import get_global_engine
            eng = get_global_engine()
            v_root = getattr(eng, "vault_root", os.getcwd()) if eng else os.getcwd()
            resp = serve_cover_asset_or_heal(cover_fn, vault_root=v_root)
            if hasattr(resp, "path") and os.path.isfile(resp.path):
                with open(resp.path, "rb") as f: return f.read(), cover_fn
        except Exception: pass
    # 1. 外部网络图片
    if src.startswith("http://") or src.startswith("https://"):
        try:
            proxies = _get_proxies(proxy)
            resp = requests.get(src, proxies=proxies, timeout=timeout, headers={"User-Agent": "Mozilla/5.0 PlenipesBot/1.0"})
            if resp.status_code == 200 and resp.content:
                # 推导文件名与扩展名
                clean_path = src.split('?')[0].split('#')[0]
                filename = os.path.basename(clean_path) or "image.png"
                if not any(filename.lower().endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    content_type = resp.headers.get("Content-Type", "")
                    if "jpeg" in content_type or "jpg" in content_type:
                        filename += ".jpg"
                    elif "gif" in content_type:
                        filename += ".gif"
                    else:
                        filename += ".png"
                return resp.content, filename
            else:
                tlog.warning(f"⚠️ [微信图床] 外部图片拉取失败 ({resp.status_code}): {src}")
        except Exception as e:
            tlog.warning(f"⚠️ [微信图床] 拉取外部图片网络异常: {src} -> {e}")
        return None

    # 2. 本地文件多级寻址
    if doc_dir and not src.startswith("data:"):
        clean_path = src.split('?')[0].split('#')[0]
        stripped = clean_path.lstrip('/')
        candidates = [
            os.path.normpath(os.path.join(doc_dir, clean_path)),
            os.path.normpath(os.path.join(doc_dir, stripped)),
            os.path.normpath(os.path.join(doc_dir, "assets", os.path.basename(clean_path))),
            os.path.normpath(os.path.join(doc_dir, "images", os.path.basename(clean_path)))
        ]
        # 向上探测可能的 vault 根目录
        cur = os.path.abspath(doc_dir)
        while cur and cur != os.path.dirname(cur):
            if os.path.exists(os.path.join(cur, ".obsidian")) or os.path.basename(cur).lower() == "vault":
                candidates.extend([
                    os.path.normpath(os.path.join(cur, stripped)),
                    os.path.normpath(os.path.join(cur, "assets", os.path.basename(clean_path))),
                    os.path.normpath(os.path.join(cur, "static", os.path.basename(clean_path)))
                ])
                break
            cur = os.path.dirname(cur)

        for path in candidates:
            if os.path.isfile(path):
                try:
                    with open(path, "rb") as f: return f.read(), os.path.basename(path)
                except Exception as e:
                    tlog.warning(f"⚠️ [微信图床] 读取本地图片失败 {path}: {e}")
                    break
    return None

def upload_to_wechat_uploadimg(image_bytes: bytes, filename: str, access_token: str, proxy: Optional[str] = None, timeout: int = 15) -> Optional[str]:
    """调用微信官方 media/uploadimg 接口上传图片到微信图床，返回永久 CDN 链接"""
    if not image_bytes or not access_token:
        return None
    image_bytes, filename = optimize_image_for_wechat(image_bytes, filename, max_size_bytes=2 * 1024 * 1024)
    if len(image_bytes) > 10 * 1024 * 1024:
        tlog.warning(f"⚠️ [微信图床] 图片 {filename} 超过 10MB 微信限制，跳过。")
        return None
    upload_url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={access_token}"
    proxies = _get_proxies(proxy)
    content_type = "image/png" if filename.lower().endswith(".png") else ("image/gif" if filename.lower().endswith(".gif") else "image/jpeg")
    files = {"media": (filename, image_bytes, content_type)}
    try:
        resp = requests.post(upload_url, files=files, proxies=proxies, timeout=timeout)
        if resp.status_code == 200:
            res_data = resp.json()
            if "url" in res_data:
                wechat_url = res_data["url"]
                tlog.info(f"✨ [微信图床] 图片转存成功: {filename} -> {wechat_url}")
                return wechat_url
            tlog.warning(f"⚠️ [微信图床] 微信接口返回错误: {res_data.get('errcode')} - {res_data.get('errmsg')}")
        else:
            tlog.warning(f"⚠️ [微信图床] 接口 HTTP 响应异常: {resp.status_code}")
    except Exception as e:
        tlog.warning(f"⚠️ [微信图床] 上传异常: {filename} -> {e}")
    return None

def transmute_article_images(articles: List[Dict], access_token: str, doc_dir: Optional[str] = None, proxy: Optional[str] = None, timeout: int = 15) -> List[Dict]:
    """扫描推文文章内容中的图片链接，转存为微信官方 CDN 并原地替换"""
    if not articles or not access_token:
        return articles
    img_src_regex = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
    upload_cache: Dict[str, str] = {}
    for article in articles:
        content = article.get("content")
        if not content:
            continue
        matches = img_src_regex.findall(content)
        if not matches:
            continue
        for orig_src in matches:
            if is_wechat_cdn_image(orig_src):
                continue
            if orig_src in upload_cache:
                wechat_url = upload_cache[orig_src]
                content = content.replace(f'src="{orig_src}"', f'src="{wechat_url}"').replace(f"src='{orig_src}'", f"src='{wechat_url}'")
                continue
            fetched = fetch_image_bytes(orig_src, doc_dir=doc_dir, proxy=proxy, timeout=timeout)
            if fetched:
                img_bytes, filename = fetched
                wechat_url = upload_to_wechat_uploadimg(img_bytes, filename, access_token, proxy=proxy, timeout=timeout)
                if wechat_url:
                    upload_cache[orig_src] = wechat_url
                    content = content.replace(f'src="{orig_src}"', f'src="{wechat_url}"').replace(f"src='{orig_src}'", f"src='{wechat_url}'")
        article["content"] = content
    return articles

def generate_default_cover_bytes() -> bytes:
    """动态生成一张 900x383 微信官方标准 2.35:1 比例的高端科技感暗色封面图"""
    try:
        from PIL import Image, ImageDraw
        import io
        img = Image.new('RGB', (900, 383), color=(20, 24, 36))
        draw = ImageDraw.Draw(img)
        draw.rectangle([16, 16, 884, 367], outline=(0, 242, 254), width=3)
        draw.rectangle([24, 24, 876, 359], outline=(37, 99, 235), width=1)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=90)
        return buf.getvalue()
    except Exception as e:
        tlog.warning(f"⚠️ [微信封面] 封面生成异常: {e}")
        return b""

_thumb_cache: Dict[str, str] = {}

def clear_thumb_cache() -> None:
    """清空微信封面永久素材内存缓存"""
    global _thumb_cache
    _thumb_cache.clear()

def upload_wechat_thumb(image_bytes: bytes, filename: str, access_token: str, proxy: Optional[str] = None, timeout: int = 15) -> Optional[str]:
    """调用微信官方 material/add_material 接口上传封面永久素材并返回 media_id"""
    if not image_bytes or not access_token:
        return None
    image_bytes, filename = optimize_image_for_wechat(image_bytes, filename, max_size_bytes=2 * 1024 * 1024)
    upload_url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"
    proxies = _get_proxies(proxy)
    content_type = "image/png" if filename.lower().endswith(".png") else "image/jpeg"
    files = {"media": (filename, image_bytes, content_type)}
    try:
        resp = requests.post(upload_url, files=files, proxies=proxies, timeout=timeout)
        if resp.status_code == 200:
            res_data = resp.json()
            media_id = res_data.get("media_id")
            if media_id:
                tlog.info(f"✨ [微信封面] 永久素材上传成功，已获取 media_id: {media_id}")
                return media_id
            tlog.warning(f"⚠️ [微信封面] 微信接口未返回 media_id: {res_data.get('errcode')} - {res_data.get('errmsg')}")
        else:
            tlog.warning(f"⚠️ [微信封面] 上传 HTTP 异常 ({resp.status_code}): {resp.text}")
    except Exception as e:
        tlog.warning(f"⚠️ [微信封面] 上传网络异常: {e}")
    return None

def ensure_valid_thumb_media_id(articles: List[Dict], access_token: str, doc_dir: Optional[str] = None, proxy: Optional[str] = None, timeout: int = 15) -> List[Dict]:
    """自愈并保证每个 article 的 thumb_media_id 为真实合法的微信永久素材 ID"""
    global _thumb_cache
    if not articles or not access_token:
        return articles
    for article in articles:
        if article.get("thumb_media_id") and article.get("thumb_media_id") != "media_id_placeholder":
            article.pop("_cover_src", None)
            continue
        target_thumb_src = article.get("_cover_src")
        if not target_thumb_src:
            img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', article.get("content", ""), re.IGNORECASE)
            if img_match:
                target_thumb_src = img_match.group(1)
        media_id = None
        if target_thumb_src:
            if target_thumb_src in _thumb_cache:
                media_id = _thumb_cache[target_thumb_src]
            else:
                fetched = fetch_image_bytes(target_thumb_src, doc_dir=doc_dir, proxy=proxy, timeout=timeout)
                if fetched:
                    img_bytes, filename = fetched
                    media_id = upload_wechat_thumb(img_bytes, filename, access_token, proxy=proxy, timeout=timeout)
                    if media_id:
                        _thumb_cache[target_thumb_src] = media_id
        if not media_id:
            cache_key = "default_plenipes_thumb"
            if cache_key in _thumb_cache:
                media_id = _thumb_cache[cache_key]
            else:
                default_bytes = generate_default_cover_bytes()
                if default_bytes:
                    media_id = upload_wechat_thumb(default_bytes, "cover.jpg", access_token, proxy=proxy, timeout=timeout)
                    if media_id:
                        _thumb_cache[cache_key] = media_id
        if media_id:
            article["thumb_media_id"] = media_id
        article.pop("_cover_src", None)
    return articles


