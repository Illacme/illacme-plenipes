#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Juejin Syndicator
模块职责：负责将稿件同步分发至稀土掘金平台草稿箱。
"""

import requests
from core.adapters.syndication.base import BaseSyndicator
from core.utils.tracing import tlog


# 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上
_last_juejin_time = 0.0

class JuejinSyndicator(BaseSyndicator):
    PLUGIN_ID = "juejin"
    DISPLAY_NAME = "稀土掘金"
    VERSION = "V1.0"
    DESCRIPTION = "将文章同步保存至稀土掘金的草稿箱，支持 Cookie 或 API Token 验证。"
    
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        digest = metadata.get("description") or metadata.get("digest") or (content[:100] + "...")
        return {
            "title": title,
            "brief_content": digest,
            "mark_content": content,  # Markdown 源码内容
            "category_id": metadata.get("juejin_category_id") or "6809637767543259144",  # 默认分类：后端/开发
            "tag_ids": metadata.get("juejin_tag_ids") or [],
            "html_content": ""
        }

    def push(self, payload: dict):
        import time
        import random

        cookie = getattr(self.config, 'cookie', None) or self.config.get('cookie')
        api_token = getattr(self.config, 'api_token', None) or self.config.get('api_token')

        if not cookie and not api_token:
            tlog.warning("⚠️ [稀土掘金] 缺少 cookie 或 api_token 凭据，分发跳过。")
            return

        url = "https://api.juejin.cn/content_api/v1/article_draft/create"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        if cookie:
            headers["Cookie"] = cookie
        if api_token:
            headers["X-Juejin-Token"] = api_token

        # 🛡️ 1. 全局平滑流控防线：强制控制两次发送的间隔时间在 1.5 秒以上
        global _last_juejin_time
        try:
            _last_juejin_time
        except NameError:
            _last_juejin_time = 0.0

        while True:
            elapsed = time.time() - _last_juejin_time
            if elapsed < 1.5:
                time.sleep(1.5 - elapsed)
            else:
                break

        _last_juejin_time = time.time()

        # 🛡️ 2. 指数退避重试循环 (对冲 429 频控)
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                _last_juejin_time = time.time()

                if resp.status_code == 429:
                    if attempt < max_attempts - 1:
                        sleep_time = 3.0 * (2 ** attempt) + random.uniform(0.1, 0.5)
                        time.sleep(sleep_time)
                        continue
                    else:
                        raise RuntimeError("对端稀土掘金接口频控限制 (429 Too Many Requests)，请稍后重试。")

                if resp.status_code == 200:
                    resp_data = resp.json()
                    err_no = resp_data.get("err_no")
                    if err_no == 0:
                        draft_id = resp_data.get('data', {}).get('draft_id')
                        tlog.info(f"🚀 [稀土掘金分发成功] 成功保存草稿，Draft ID: {draft_id}")
                        return {"draft_id": draft_id}
                    elif err_no in (401, 403, 3000):
                        raise RuntimeError(f"稀土掘金登录凭证已失效 (err_no {err_no})，请在配置中重新录入 Cookie 或 X-Juejin-Token。")
                    else:
                        raise RuntimeError(f"稀土掘金业务接口报错 (err_no {err_no}): {resp_data.get('err_msg')}")
                else:
                    raise RuntimeError(f"稀土掘金接口 HTTP 错误 ({resp.status_code}): {resp.text}")

            except requests.RequestException as req_err:
                if attempt < max_attempts - 1:
                    sleep_time = 2.0 + random.uniform(0.1, 0.5)
                    time.sleep(sleep_time)
                    continue
                else:
                    tlog.error(f"🛑 [稀土掘金] 网络请求失败: {req_err}")
                    raise RuntimeError(f"稀土掘金网络请求失败: {req_err}") from req_err
            except Exception as e:
                tlog.error(f"🛑 [稀土掘金失败]: {e}")
                raise e
