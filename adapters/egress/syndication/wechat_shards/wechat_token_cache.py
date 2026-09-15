#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - WeChat Access Token Persistent Cache Shard
模块职责：提供微信公众号 access_token 的长效双层缓存（内存 + 磁盘持久化）与自动静默刷新。
解决痛点：
1. 微信每日 2000 次全局调用上限保护；
2. 彻底根除因高频获取 Token 触发的 45009 api freq out of limit 频控熔断；
3. 临近过期 (预留 300s) 静默提前续期，遭遇 40001 凭据失效自愈感知刷新。
严格遵守 SOP-01 规范 (< 300 行)。
"""

import os
import re
import time
import json
import hashlib
import threading
from typing import Dict, Any, Optional
import requests
from core.utils.tracing import tlog


def _get_proxies(proxy: Optional[str]) -> Optional[dict]:
    """统一解析网络代理：direct 明确绕过环境变量，具体 URL 则映射 http/https"""
    if not proxy:
        return None
    p = str(proxy).strip()
    if p.lower() == "direct":
        return {"http": None, "https": None}
    return {"http": p, "https": p}

class WeChatTokenCache:
    """微信公众号 Access Token 本地长效持久化缓存管理器 (线程安全)"""
    
    _instance: Optional["WeChatTokenCache"] = None
    _singleton_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._singleton_lock:
                if not cls._instance:
                    cls._instance = super(WeChatTokenCache, cls).__new__(cls)
                    cls._instance._init_cache()
        return cls._instance

    def _init_cache(self):
        self._lock = threading.Lock()
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_dir = os.path.join(os.getcwd(), ".plenipes", "cache", "wechat_tokens")
        try:
            os.makedirs(self._cache_dir, exist_ok=True)
        except Exception:
            pass

    def _compute_cache_key(self, app_id: str, app_secret: str) -> str:
        raw = f"{app_id.strip()}:{app_secret.strip()}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:16]

    def _get_cache_file_path(self, cache_key: str) -> str:
        return os.path.join(self._cache_dir, f"token_{cache_key}.json")

    def _load_from_disk(self, cache_key: str) -> Optional[Dict[str, Any]]:
        path = self._get_cache_file_path(cache_key)
        if not os.path.isfile(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "access_token" in data and "expires_at" in data:
                    return data
        except Exception as e:
            tlog.warning(f"⚠️ [微信 Token 缓存] 读取磁盘缓存失败 ({path}): {e}")
        return None

    def _save_to_disk(self, cache_key: str, data: Dict[str, Any]):
        try:
            os.makedirs(self._cache_dir, exist_ok=True)
            path = self._get_cache_file_path(cache_key)
            # 先写临时文件防断电坏盘
            tmp_path = f"{path}.tmp_{os.getpid()}"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, path)
        except Exception as e:
            tlog.warning(f"⚠️ [微信 Token 缓存] 写入磁盘缓存失败: {e}")

    def get_token(self, app_id: str, app_secret: str, timeout: int = 15, force_refresh: bool = False, proxy: Optional[str] = None) -> str:
        """
        获取合法的微信 Access Token。
        - 缓存未过期且余量 > 300s：直接命中缓存秒级返回；
        - 余量 <= 300s 或强制刷新：发起远程 API 调用静默换新。
        """
        if not app_id or not app_secret:
            raise RuntimeError("微信公众号缺少 AppID 或 AppSecret，无法获取 Access Token。")

        cache_key = self._compute_cache_key(app_id, app_secret)
        now = time.time()

        # 1. 尝试快速读取内存/磁盘缓存 (无锁读)
        if not force_refresh:
            cached = self._memory_cache.get(cache_key)
            if not cached:
                cached = self._load_from_disk(cache_key)
                if cached:
                    self._memory_cache[cache_key] = cached

            if cached:
                expires_at = cached.get("expires_at", 0)
                # 预留 300 秒安全换新窗口
                if now < (expires_at - 300):
                    token = cached.get("access_token")
                    if token:
                        return token

        # 2. 缓存已过期、不足 300 秒或强制刷新 -> 加锁换新
        with self._lock:
            # 临界区双重校验 (Double-checked locking)
            if not force_refresh:
                cached = self._memory_cache.get(cache_key)
                if cached:
                    expires_at = cached.get("expires_at", 0)
                    if time.time() < (expires_at - 300):
                        token = cached.get("access_token")
                        if token:
                            return token

            # 发起真实网络调用
            token = self._fetch_remote_token(app_id, app_secret, timeout=timeout, proxy=proxy)
            return token

    def _fetch_remote_token(self, app_id: str, app_secret: str, timeout: int = 15, proxy: Optional[str] = None) -> str:
        """向微信官方服务器请求新的 access_token"""
        tlog.info("🔄 [微信 Token] 正在向微信官方服务器申请/刷新 Access Token...")
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
        proxies = _get_proxies(proxy)
        resp = requests.get(url, proxies=proxies, timeout=timeout)
        
        if resp.status_code != 200:
            raise RuntimeError(f"微信 Access Token 请求 HTTP 错误: {resp.status_code}")

        data = resp.json()
        errcode = data.get("errcode")
        if errcode:
            if errcode == 40164:
                errmsg = data.get("errmsg", "")
                ip_match = re.search(r"invalid ip\s+([0-9\.]+)", errmsg)
                invalid_ip = ip_match.group(1) if ip_match else "未知"
                raise RuntimeError(
                    f"微信公众号 IP 白名单拦截 (40164)：检测到当前请求出口 IP 为 [{invalid_ip}]。"
                    f"请登录微信公众平台【设置与开发 -> 基本配置 -> IP白名单】添加此 IP。若已配置全局代理，可设置 proxy: direct 尝试直连。"
                )
            elif errcode in (40013, 40001):
                raise RuntimeError("微信公众号授权失败：AppID 或 AppSecret 不正确，请检查插件配置。")
            elif errcode == 45009:
                raise RuntimeError("微信公众号接口调用频控限制 (45009 api freq out of limit)，请稍后重试。")
            else:
                raise RuntimeError(f"获取微信 Token 报错 ({errcode}): {data.get('errmsg')}")

        access_token = data.get("access_token")
        if not access_token:
            raise RuntimeError("微信官方返回数据中未包含 access_token 字段。")

        expires_in = int(data.get("expires_in", 7200))
        now = time.time()
        expires_at = now + expires_in
        cache_key = self._compute_cache_key(app_id, app_secret)

        cache_data = {
            "app_id": app_id,
            "access_token": access_token,
            "expires_in": expires_in,
            "expires_at": expires_at,
            "updated_at": now
        }
        self._memory_cache[cache_key] = cache_data
        self._save_to_disk(cache_key, cache_data)
        tlog.info(f"✨ [微信 Token 刷新成功] Token 有效期 {expires_in}s，已持久化至本地缓存。")
        return access_token

    def invalidate(self, app_id: str, app_secret: str):
        """强制使本地 Token 缓存失效（用于对端报 40001 时自愈）"""
        cache_key = self._compute_cache_key(app_id, app_secret)
        with self._lock:
            self._memory_cache.pop(cache_key, None)
            path = self._get_cache_file_path(cache_key)
            if os.path.isfile(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
        tlog.warning("♻️ [微信 Token] 本地 Token 缓存已强制失效。")


# 全局单例
wechat_token_cache = WeChatTokenCache()
