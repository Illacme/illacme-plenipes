#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Dev.to Syndicator
模块职责：负责将内容分发至 Dev.to 平台。
🛡️ [AEL-Iter-v5.3]：全自治插件实现。
"""
import requests
from core.adapters.syndication.base import BaseSyndicator

from core.utils.tracing import tlog

import threading

# 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上
_last_devto_time = 0.0
_devto_lock = threading.Lock()

class DevToSyndicator(BaseSyndicator):
    PLUGIN_ID = "devto"
    DISPLAY_NAME = "Dev.to"
    VERSION = "V1.0"
    DESCRIPTION = "将内容同步分发至全球开发者社区 Dev.to，支持标签映射与原文链接回溯。"
    
    # 🚀 [V11.3] 声明运行时依赖契约
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        tags = metadata.get('tags', [])
        # Canonical URL 优先使用传入值，否则 Fallback 推导
        if not canonical_url and self.site_url:
            canonical_url = f"{self.site_url}/{slug}".replace('//', '/').replace(':/', '://')
        
        payload = {
            "article": {
                "title": title,
                "body_markdown": content,
                "published": self.config.get('published', False) if isinstance(self.config, dict) else getattr(self.config, 'published', False),
                "tags": tags[:4]
            }
        }
        
        # 🛡️ [V89.3] 极其强顺的公网 Canonical URL 校验
        if canonical_url and (canonical_url.startswith("http://") or canonical_url.startswith("https://")):
            payload["article"]["canonical_url"] = canonical_url
            
        return payload

    def push(self, payload: dict):
        import time
        import random

        api_key = self.config.get('api_key') if isinstance(self.config, dict) else getattr(self.config, 'api_key', None)
        if not api_key:
            raise RuntimeError("缺少 API Key，分发自动熔断。")
            
        url = "https://dev.to/api/articles"
        headers = {"api-key": api_key, "Content-Type": "application/json"}
        
        # 🛡️ 指数退避重试循环 (加上临界锁严格防线：每一次尝试发送，都必须串行流控间隔 3.0 秒以上)
        max_attempts = 3
        global _last_devto_time
        
        for attempt in range(max_attempts):
            with _devto_lock:
                while True:
                    elapsed = time.time() - _last_devto_time
                    if elapsed < 3.0:
                        # 线程让步冷却，防止在算力集群中扎堆
                        time.sleep(3.0 - elapsed)
                    else:
                        break
                
                _last_devto_time = time.time()
                
                try:
                    resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                    _last_devto_time = time.time()
                except requests.exceptions.RequestException as req_err:
                    _last_devto_time = time.time()
                    if attempt < max_attempts - 1:
                        sleep_time = 2.0 + random.uniform(0.1, 0.5)
                        tlog.warning(f"⚠️ [Dev.to 网络失败] 正在休眠 {sleep_time:.2f} 秒后重新排队进行第 {attempt + 2} 次重试...")
                        time.sleep(sleep_time)
                        continue
                    else:
                        tlog.error(f"🛑 [Dev.to 网络失败]: {req_err}")
                        raise req_err
                except Exception as e:
                    _last_devto_time = time.time()
                    tlog.error(f"🛑 [Dev.to 失败]: {e}")
                    raise e
            
            # 释放锁后检查接口响应
            if resp.status_code == 201:
                publish_url = resp.json().get('url')
                tlog.info(f"🚀 [Dev.to 分发成功] 预览: {publish_url}")
                return {"url": publish_url}
            elif resp.status_code == 429:
                if attempt < max_attempts - 1:
                    sleep_time = 6.0 * (2 ** attempt) + random.uniform(0.2, 0.5)
                    tlog.warning(f"⚠️ [Dev.to Rate Limit] 探测到对端 429 频率超限，正在执行指数退避，休眠 {sleep_time:.2f} 秒后重新排队进行第 {attempt + 2} 次重试...")
                    time.sleep(sleep_time)
                    continue
                else:
                    raise RuntimeError("对端接口返回错误 (状态码 429): 频率超限。请在治理中心中稍微调大 system.network_timeout 或分批分步发布。")
            elif resp.status_code == 422:
                err_txt = resp.text
                if "Title has already been used" in err_txt:
                    raise RuntimeError("Dev.to 存在同名保护策略 (5分钟内禁止发布相同标题的文章，例如多个'未命名原稿')。请先修改此文稿的标题 (Title) 后重新同步。")
                else:
                    raise RuntimeError(f"对端接口验证失败 (状态码 422): {err_txt[:150]}")
            else:
                raise RuntimeError(f"对端接口返回错误 (状态码 {resp.status_code}): {resp.text[:200]}")
