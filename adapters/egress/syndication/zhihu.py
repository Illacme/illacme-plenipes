#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Zhihu Syndicator
模块职责：负责将稿件同步分发至知乎专栏。
"""

import requests
import threading
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog


# 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上
_last_zhihu_time = 0.0
_zhihu_lock = threading.Lock()

class ZhihuSyndicator(BaseSyndicator):
    PLUGIN_ID = "zhihu"
    DISPLAY_NAME = "知乎"
    VERSION = "V1.0"
    DESCRIPTION = "将文章同步发表至指定的知乎专栏，支持 Markdown 内容排版。"
    
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        if not canonical_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        
        # 知乎官方及常见扩展通常接受 HTML 或 Markdown 格式的内容
        return {
            "title": title,
            "content": content,
            "column_id": getattr(self.config, 'column_id', None) or self.config.get('column_id'),
            "source_url": canonical_url,
            "state": "draft"  # 默认发布为草稿以保防误触
        }

    def push(self, payload: dict):
        import time
        import random

        token = getattr(self.config, 'token', None) or self.config.get('token')
        column_id = payload.get("column_id")

        if not token:
            tlog.warning("⚠️ [知乎专栏] 缺少 token 配置，分发跳过。")
            return
        if not column_id:
            tlog.warning("⚠️ [知乎专栏] 缺少 column_id 配置，分发跳过。")
            return

        url = f"https://api.zhihu.com/columns/{column_id}/articles"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "Illacme-Plenipes-Client"
        }

        # 🛡️ 指数退避重试循环 (加上临界锁严格防线：每一次尝试发送，都必须串行流控间隔 3.0 秒以上)
        max_attempts = 3
        global _last_zhihu_time
        for attempt in range(max_attempts):
            with _zhihu_lock:
                while True:
                    elapsed = time.time() - _last_zhihu_time
                    if elapsed < 3.0:
                        time.sleep(3.0 - elapsed)
                    else:
                        break

                _last_zhihu_time = time.time()
                try:
                    resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                    _last_zhihu_time = time.time()
                except requests.RequestException as req_err:
                    _last_zhihu_time = time.time()
                    if attempt < max_attempts - 1:
                        sleep_time = 2.0 + random.uniform(0.1, 0.5)
                        tlog.warning(f"⚠️ [知乎网络失败] 正在休眠 {sleep_time:.2f} 秒后重新排队进行第 {attempt + 2} 次重试...")
                        time.sleep(sleep_time)
                        continue
                    else:
                        tlog.error(f"🛑 [知乎] 网络请求失败: {req_err}")
                        raise RuntimeError(f"知乎网络请求失败: {req_err}") from req_err
                except Exception as e:
                    _last_zhihu_time = time.time()
                    tlog.error(f"🛑 [知乎失败]: {e}")
                    raise e

            # 释放锁后检查接口响应
            if resp.status_code == 429:
                if attempt < max_attempts - 1:
                    sleep_time = 6.0 * (2 ** attempt) + random.uniform(0.2, 0.5)
                    tlog.warning(f"⚠️ [知乎 Rate Limit] 探测到对端 429 频率超限，正在执行指数退避，休眠 {sleep_time:.2f} 秒后重新排队进行第 {attempt + 2} 次重试...")
                    time.sleep(sleep_time)
                    continue
                else:
                    raise RuntimeError("对端知乎接口频控限制 (429 Too Many Requests)，请稍后重试。")

            if resp.status_code in [200, 201]:
                tlog.info(f"🚀 [知乎分发成功] 文章已成功同步至专栏 '{column_id}'。")
                return {"success": True, "column_id": column_id}
            elif resp.status_code in (401, 403):
                raise RuntimeError("知乎认证失败（401/403）：Token 无效或已过期，请在配置中重新录入知乎 API Token。")
            else:
                raise RuntimeError(f"知乎 API 报错 ({resp.status_code}): {resp.text}")
