# -*- coding: utf-8 -*-
"""
🪄 [V118.0] Plugin Cookie Auto-Capture & Identity Binding Engine
职责：接收本地浏览器或外部小书签一键同步推送的凭据（Cookie/Token），
真实探测平台创作者身份并全自动持久化写入本地配置。
"""

import requests
from typing import Dict, Any
from core.utils.tracing import tlog
from core.runtime.engine_singleton import get_global_engine


async def auto_capture_cookie_impl(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    🔌 接收浏览器一键推送的 Cookie/Token，自动核验身份并更新本地配置
    """
    plugin_id = (payload.get("plugin_id") or payload.get("id") or "").lower().strip()
    cookie = (payload.get("cookie") or "").strip()
    api_token = (payload.get("api_token") or payload.get("token") or "").strip()

    if not plugin_id:
        return {"success": False, "error": "缺少 plugin_id 参数"}
    if not cookie and not api_token:
        return {"success": False, "error": "缺少 cookie 或 token 凭据内容"}

    engine = get_global_engine()
    if not engine:
        return {"success": False, "error": "出版系统引擎尚未就绪"}

    # 1. 稀土掘金身份探测与自动绑定
    if plugin_id == "juejin":
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        if cookie:
            clean_cookie = cookie.strip()
            if "sessionid" not in clean_cookie and "=" not in clean_cookie and len(clean_cookie) >= 16:
                clean_cookie = f"sessionid={clean_cookie}"
            headers["Cookie"] = clean_cookie
            cookie = clean_cookie
        if api_token:
            headers["X-Juejin-Token"] = api_token

        try:
            resp = requests.get("https://api.juejin.cn/user_api/v1/user/get", headers=headers, timeout=12)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("err_no") == 0:
                    user_data = res_json.get("data") or {}
                    user_name = user_data.get("user_name") or "掘金创作者"
                    user_id = str(user_data.get("user_id") or "")

                    from services.api.routes.gov.config import update_config
                    cfg_req = {"syndication.juejin.cookie": cookie}
                    if api_token: cfg_req["syndication.juejin.api_token"] = api_token
                    await update_config(cfg_req)
                    tlog.info(f"🪄 [掘金 Cookie 自动捕获成功] 已绑定创作者: {user_name} (UID: {user_id})")

                    return {
                        "success": True, "plugin_id": "juejin", "user_name": user_name,
                        "user_id": user_id, "cookie": cookie,
                        "message": f"🎉 稀土掘金账号已成功同步！创作者: {user_name} (UID: {user_id})"
                    }
                else:
                    err_msg = res_json.get("err_msg") or f"错误码 {res_json.get('err_no')}"
                    return {"success": False, "error": f"掘金会话校验未通过: {err_msg}。请确认处于登录有效状态。"}
            return {"success": False, "error": f"连接掘金接口异常 (HTTP {resp.status_code})"}
        except Exception as e:
            return {"success": False, "error": f"校验掘金身份时发生异常: {e}"}

    # 2. 知乎 (Zhihu) 身份探测与自动绑定
    if plugin_id == "zhihu":
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        # 提取 z_c0 作为 Token
        z_c0 = api_token
        if not z_c0 and cookie:
            for item in cookie.split(";"):
                if "z_c0=" in item:
                    z_c0 = item.split("z_c0=")[1].split(";")[0].strip().strip('"')
                    break
        if cookie: headers["Cookie"] = cookie
        if z_c0: headers["Authorization"] = f"Bearer {z_c0}"

        try:
            resp = requests.get("https://www.zhihu.com/api/v4/me", headers=headers, timeout=12)
            user_name = "知乎创作者"
            user_id = ""
            if resp.status_code == 200:
                res_json = resp.json()
                user_name = res_json.get("name") or res_json.get("headline") or "知乎创作者"
                user_id = str(res_json.get("id") or "")
            elif resp.status_code not in (200, 401, 403):
                return {"success": False, "error": f"连接知乎接口异常 (HTTP {resp.status_code})"}

            from services.api.routes.gov.config import update_config
            cfg_req = {}
            if cookie: cfg_req["syndication.zhihu.cookie"] = cookie
            if z_c0: cfg_req["syndication.zhihu.token"] = z_c0
            await update_config(cfg_req)
            tlog.info(f"🪄 [知乎凭据自动捕获成功] 已绑定创作者: {user_name} (UID: {user_id})")

            return {
                "success": True, "plugin_id": "zhihu", "user_name": user_name,
                "user_id": user_id, "cookie": cookie, "token": z_c0,
                "message": f"🎉 知乎账号已成功同步！创作者: {user_name}"
            }
        except Exception as e:
            return {"success": False, "error": f"校验知乎身份时发生异常: {e}"}

    # 3. Bilibili (B站) 身份探测与自动绑定
    if plugin_id == "bilibili":
        sessdata = ""
        bili_jct = ""
        if cookie:
            for item in cookie.split(";"):
                part = item.strip()
                if part.startswith("SESSDATA="):
                    sessdata = part.split("SESSDATA=")[1].strip()
                elif part.startswith("bili_jct="):
                    bili_jct = part.split("bili_jct=")[1].strip()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Cookie": cookie
        }
        try:
            resp = requests.get("https://api.bilibili.com/x/web-interface/nav", headers=headers, timeout=12)
            if resp.status_code == 200:
                res_json = resp.json()
                if res_json.get("code") == 0:
                    data = res_json.get("data") or {}
                    user_name = data.get("uname") or "B站UP主"
                    user_id = str(data.get("mid") or "")

                    from services.api.routes.gov.config import update_config
                    cfg_req = {}
                    if sessdata: cfg_req["syndication.bilibili.sessdata"] = sessdata
                    if bili_jct: cfg_req["syndication.bilibili.bili_jct"] = bili_jct
                    if cookie: cfg_req["syndication.bilibili.cookie"] = cookie
                    await update_config(cfg_req)
                    tlog.info(f"🪄 [B站凭据自动捕获成功] 已绑定UP主: {user_name} (UID: {user_id})")

                    return {
                        "success": True, "plugin_id": "bilibili", "user_name": user_name,
                        "user_id": user_id, "sessdata": sessdata, "bili_jct": bili_jct,
                        "message": f"🎉 B站账号已成功同步！UP主: {user_name} (UID: {user_id})"
                    }
                else:
                    return {"success": False, "error": f"B站身份校验未通过: {res_json.get('message', '未登录')}"}
            return {"success": False, "error": f"连接 B 站接口异常 (HTTP {resp.status_code})"}
        except Exception as e:
            return {"success": False, "error": f"校验 B 站身份时发生异常: {e}"}

    # 4. 其他平台通用兜底自动回填
    try:
        from services.api.routes.gov.config import update_config
        cfg_req = {}
        if cookie: cfg_req[f"syndication.{plugin_id}.cookie"] = cookie
        if api_token: cfg_req[f"syndication.{plugin_id}.token"] = api_token
        await update_config(cfg_req)
        tlog.info(f"🪄 [渠道 {plugin_id} 凭据自动回填成功]")
        return {"success": True, "plugin_id": plugin_id, "message": f"渠道 [{plugin_id}] 凭据已自动同步并保存。"}
    except Exception as e:
        return {"success": False, "error": f"持久化凭据失败: {e}"}


async def auto_sniff_local_browser_impl(payload: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    🪄 [CDP 会话自动嗅探] 从本地运行的 Chrome 实例中免密提取 HttpOnly Cookie 并自动回填
    """
    import urllib.request
    import json
    import websockets

    payload = payload or {}
    plugin_id = (payload.get("plugin_id") or payload.get("id") or "juejin").lower().strip()

    SNIFF_PLATFORMS = {
        "juejin": {
            "name": "稀土掘金", "domains": ["juejin.cn"],
            "urls": ["https://juejin.cn", "https://api.juejin.cn"],
            "key_cookie": "sessionid"
        },
        "zhihu": {
            "name": "知乎", "domains": ["zhihu.com"],
            "urls": ["https://www.zhihu.com", "https://api.zhihu.com"],
            "key_cookie": "z_c0"
        },
        "bilibili": {
            "name": "Bilibili", "domains": ["bilibili.com"],
            "urls": ["https://www.bilibili.com", "https://api.bilibili.com"],
            "key_cookie": "SESSDATA"
        }
    }

    meta = SNIFF_PLATFORMS.get(plugin_id)
    if not meta:
        meta = {
            "name": plugin_id.upper(), "domains": [f"{plugin_id}.com"],
            "urls": [f"https://{plugin_id}.com"], "key_cookie": "token"
        }

    plat_name = meta["name"]
    target_domains = meta["domains"]

    try:
        req = urllib.request.Request("http://localhost:9222/json", headers={"User-Agent": "Illacme/1.0"})
        with urllib.request.urlopen(req, timeout=3) as response:
            pages = json.loads(response.read().decode())
    except Exception as e:
        return {
            "success": False,
            "error": f"未检测到本地浏览器调试通道 (9222): {e}。请确认已打开 Chrome 浏览器。"
        }

    target_page = None
    for p in pages:
        page_url = p.get("url", "")
        if any(d in page_url for d in target_domains):
            target_page = p
            break

    if not target_page:
        return {
            "success": False,
            "error": f"未在当前 Chrome 中检测到打开的 [{plat_name}] 标签页。请先在浏览器中打开 {plat_name} 并保持登录状态。"
        }

    ws_url = target_page.get("webSocketDebuggerUrl")
    if not ws_url:
        return {"success": False, "error": f"目标 [{plat_name}] 页面未暴露调试通信链路"}

    try:
        async with websockets.connect(ws_url, close_timeout=3) as ws:
            await ws.send(json.dumps({
                "id": 101,
                "method": "Network.getCookies",
                "params": {"urls": meta["urls"]}
            }))
            raw_res = await ws.recv()
            data = json.loads(raw_res)
            cookies_list = data.get("result", {}).get("cookies", [])
            if not cookies_list:
                return {"success": False, "error": f"未能从当前页面捕获到 Cookie，请先在 {plat_name} 完成登录。"}

            cookie_parts = []
            has_key_cookie = False
            for c in cookies_list:
                name = c.get("name")
                val = c.get("value")
                cookie_parts.append(f"{name}={val}")
                if meta["key_cookie"].lower() in name.lower():
                    has_key_cookie = True

            if not has_key_cookie:
                return {"success": False, "error": f"捕获到的 Cookie 中缺少核心凭据 [{meta['key_cookie']}]，请确认在 {plat_name} 已处于登录状态。"}

            full_cookie_str = "; ".join(cookie_parts)
            return await auto_capture_cookie_impl({
                "plugin_id": plugin_id,
                "cookie": full_cookie_str
            })

    except Exception as we:
        return {"success": False, "error": f"通过调试协议提取凭据失败: {we}"}

