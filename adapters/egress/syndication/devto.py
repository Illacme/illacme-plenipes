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
        
        # 🚀 强制设置 published: True，确保同步发布的文章在 Dev.to 社区公开发布，防范 404 草稿死穴
        is_published = True
        if isinstance(self.config, dict) and self.config.get("published") is True:
            is_published = True
        elif hasattr(self.config, "published") and getattr(self.config, "published") is True:
            is_published = True

        payload = {
            "article": {
                "title": title,
                "body_markdown": content,
                "published": is_published,
                "tags": tags[:4]
            }
        }
        
        # 🛡️ [V89.3] 极其强顺的公网 Canonical URL 校验
        if canonical_url and (canonical_url.startswith("http://") or canonical_url.startswith("https://")):
            payload["article"]["canonical_url"] = canonical_url
            
        return payload

    def push(self, payload: dict, remote_id: str = None):
        import time
        import random

        api_key = self.config.get('api_key') if isinstance(self.config, dict) else getattr(self.config, 'api_key', None)
        if not api_key:
            raise RuntimeError("缺少 API Key，分发自动熔断。")
            
        url = f"https://dev.to/api/articles/{remote_id}" if remote_id else "https://dev.to/api/articles"
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
                    if remote_id:
                        resp = requests.put(url, json=payload, headers=headers, timeout=self.timeout)
                    else:
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
            
            # 释放锁后检查接口响应 (200 OK for PUT, 201 Created for POST)
            if resp.status_code in (200, 201):
                resp_data = resp.json()
                publish_url = resp_data.get('url')
                article_id = resp_data.get('id') or remote_id
                
                # 🛡️ [V113.4] Dev.to 软 404 内容级探测：Dev.to 对未公开文章返回 HTTP 200 但页面渲染 "404 / PAGE NOT FOUND"
                is_soft_404 = False
                if publish_url:
                    try:
                        probe_resp = requests.get(publish_url, timeout=8, headers={"User-Agent": "IllacmePlenipes/1.0"})
                        page_text = probe_resp.text[:3000].lower()
                        if '404' in page_text and 'page not found' in page_text:
                            is_soft_404 = True
                    except Exception as probe_err:
                        tlog.warning(f"⚠️ [Dev.to 探测] 无法验证文章可访问性: {probe_err}")
                
                if is_soft_404:
                    dashboard_url = "https://dev.to/dashboard"
                    if article_id:
                        dashboard_url = f"https://dev.to/{resp_data.get('user', {}).get('username', 'dashboard')}/{resp_data.get('slug', article_id)}/edit"
                    tlog.warning(
                        f"⚠️ [Dev.to 草稿] 文章 (ID: {article_id}) 已推送但公开页面显示 404。"
                        f"Dev.to 可能对新账号强制降级为草稿。请前往仪表盘手动发布: {dashboard_url}"
                    )
                    return {"url": publish_url, "draft": True, "dashboard_url": dashboard_url, "remote_id": str(article_id)}
                else:
                    action_txt = "更新成功" if remote_id else "发布成功"
                    tlog.info(f"🚀 [Dev.to {action_txt}] 文章已对正: {publish_url} (ID: {article_id})")
                    return {"url": publish_url, "remote_id": str(article_id)}
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

    def delete(self, remote_id: str) -> bool:
        """🚀 远程物理下架：先强制下架（Unpublish 设为草稿），再彻底物理销毁"""
        if not remote_id: return False
        api_key = self.config.get('api_key') if isinstance(self.config, dict) else getattr(self.config, 'api_key', None)
        if not api_key: raise RuntimeError("缺少 API Key，下架物理拦截。")
        
        url = f"https://dev.to/api/articles/{remote_id}"
        headers = {"api-key": api_key, "Content-Type": "application/json"}

        # 1. 优先通过 PUT 将 published 设为 false，确保公网立即下线 (变为私有草稿)
        try:
            unpub_payload = {"article": {"published": False}}
            requests.put(url, json=unpub_payload, headers=headers, timeout=self.timeout)
        except Exception as e:
            tlog.warning(f"⚠️ [Dev.to 强制下架告警] PUT unpublish: {e}")

        # 2. 紧接着发送 DELETE 请求物理彻底销毁
        resp = requests.delete(url, headers=headers, timeout=self.timeout)
        if resp.status_code in (200, 204):
            tlog.info(f"🗑️ [Dev.to 物理下架成功] 已成功删除文章 ID: {remote_id}")
            return True
        elif resp.status_code == 404:
            tlog.info(f"🗑️ [Dev.to 物理对正] 对端文章 (ID: {remote_id}) 在 Dev.to 已不存在或已被物理销毁 (HTTP 404)，自动对正解绑本地物理账本。")
            return True
        else:
            tlog.error(f"🛑 [Dev.to 物理下架失败] ID: {remote_id} (HTTP {resp.status_code}): {resp.text[:200]}")
            return False
