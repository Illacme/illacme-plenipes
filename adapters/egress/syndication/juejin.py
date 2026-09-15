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
    ICON = "🧱"
    VERSION = "V1.0"
    DESCRIPTION = "将文章同步保存至稀土掘金的草稿箱，支持 Cookie 或 API Token 验证。"
    SLA_TIER = "tier2"
    SLA_LABEL = "Cookie辅助"
    SLA_DESC = "依赖掘金 sessionid Cookie，有效期受平台登录态控制，建议定期校验。"
    
    REQUIRED_PACKAGES = ["requests"]

    def format_payload(self, title: str, slug: str, content: str, metadata: dict, canonical_url: str = None) -> dict:
        metadata = metadata or {}
        raw_digest = metadata.get("description") or metadata.get("digest") or ""
        if not raw_digest:
            import re
            clean_text = re.sub(r'[#*`_~\[\]\(\)>!]', '', content).strip()
            clean_text = re.sub(r'\s+', ' ', clean_text)
            raw_digest = (clean_text[:95] + "...") if len(clean_text) > 95 else clean_text

        raw_cat = metadata.get("juejin_category_id")
        if not raw_cat:
            if isinstance(self.config, dict):
                raw_cat = self.config.get('category_id')
            elif hasattr(self.config, 'category_id'):
                val = getattr(self.config, 'category_id')
                if isinstance(val, (str, int)) and str(val).strip():
                    raw_cat = val

        category_id = str(raw_cat) if raw_cat else "6809637767543259144"
        tag_ids = metadata.get("juejin_tag_ids") or []

        return {
            "title": title,
            "brief_content": raw_digest[:100],
            "mark_content": content,  # Markdown 源码内容
            "edit_type": 10,  # 🚀 必须指定 edit_type: 10 (Markdown 模式)，否则掘金按富文本处理导致正文为空
            "category_id": category_id,
            "tag_ids": list(tag_ids) if isinstance(tag_ids, (list, tuple)) else [],
            "html_content": ""
        }

    def push(self, payload: dict, remote_id: str = None, **kwargs):
        import time
        import random

        cfg_dict = self.config if isinstance(self.config, dict) else getattr(self.config, '__dict__', {})
        cookie = getattr(self.config, 'cookie', None) or cfg_dict.get('cookie')
        api_token = getattr(self.config, 'api_token', None) or cfg_dict.get('api_token')
        proxy = getattr(self.config, 'proxy', None) or cfg_dict.get('proxy')

        if not cookie and not api_token:
            tlog.warning("⚠️ [稀土掘金] 缺少 cookie 或 api_token 凭据，分发跳过。")
            return None

        # 🚀 幂等更新草稿与创建草稿无缝切换
        req_payload = dict(payload)
        if remote_id:
            url = "https://api.juejin.cn/content_api/v1/article_draft/update"
            req_payload["id"] = str(remote_id)
            action_name = "增量更新草稿"
        else:
            url = "https://api.juejin.cn/content_api/v1/article_draft/create"
            action_name = "创建草稿"

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        if cookie:
            clean_cookie = cookie.strip()
            if "sessionid" not in clean_cookie and "=" not in clean_cookie and len(clean_cookie) >= 16:
                clean_cookie = f"sessionid={clean_cookie}"
            headers["Cookie"] = clean_cookie
        if api_token:
            headers["X-Juejin-Token"] = api_token

        proxies = None
        if proxy and str(proxy).lower() != "direct":
            proxies = {"http": proxy, "https": proxy}

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
                resp = requests.post(url, json=req_payload, headers=headers, proxies=proxies, timeout=self.timeout)
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
                        data_block = resp_data.get('data') or {}
                        draft_id = data_block.get('draft_id') or data_block.get('id') or remote_id
                        draft_url = f"https://juejin.cn/editor/drafts/{draft_id}"
                        tlog.info(f"🚀 [稀土掘金{action_name}成功] 草稿 ID: {draft_id}，在线编辑: {draft_url}")
                        return {
                            "draft_id": str(draft_id),
                            "remote_id": str(draft_id),
                            "url": draft_url,
                            "dashboard_url": draft_url,
                            "draft": True
                        }
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

