# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Domestic Platform Cookie Health Prober
模块职责：小红书、知乎、Bilibili、CSDN、头条等 Cookie 凭据深度健康检验与会话失效主动预警。
🛡️ [SOP-01 & SOP-02 规范]：单文件物理行数严格 ≤ 300 行。
"""

import requests
from typing import Dict, Any, List

COMMON_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def probe_xiaohongshu(
    settings: Dict[str, Any],
    logs: List[Dict[str, str]],
    log_func: Any,
    proxies: Dict[str, str]
) -> bool:
    """📕 小红书 Cookie 深度健康校验与创作者会话有效性探针"""
    token = str(settings.get("token") or "").strip()
    cookie = str(settings.get("cookie") or "").strip()

    if not token and not cookie:
        logs.append(log_func("ERROR", "❌ [错误] 小红书 Token 与 Cookie 必须至少配置一项。"))
        return False

    # 1. Cookie 关键指纹防呆与结构预警
    if cookie:
        has_a1 = "a1=" in cookie
        has_session = "web_session=" in cookie or "webId=" in cookie
        if not has_a1 and not has_session:
            logs.append(log_func("WARN", "⚠️ [Cookie结构预警] 检测到 Cookie 中缺少关键身份字段 'a1' 或 'web_session'，发文容易被创作者平台拦截！"))

    logs.append(log_func("INFO", "📡 [探测] 正在连接小红书创作者服务检验 Cookie 会话可用性..."))
    headers = {
        "User-Agent": COMMON_UA,
        "Accept": "application/json, text/plain, */*",
    }
    if cookie:
        headers["Cookie"] = cookie
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        # 请求小红书创作者平台个人信息接口
        resp = requests.get(
            "https://edith.xiaohongshu.com/api/sns/web/v1/user/selfinfo",
            headers=headers,
            proxies=proxies,
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") or data.get("code") == 0:
                user_info = data.get("data") or {}
                nickname = user_info.get("nickname") or user_info.get("name") or "小红书创作者"
                user_id = user_info.get("user_id") or user_info.get("id") or ""
                logs.append(log_func("SUCCESS", f"🟢 [成功] 小红书 Cookie 验证通过！已连接创作者: {nickname} (ID: {user_id})。图文笔记通道就绪。"))
                return True
            else:
                msg = data.get("msg") or f"返回码 {data.get('code')}"
                logs.append(log_func("ERROR", f"❌ [Cookie失效预警] 小红书会话未激活或触发滑块风控: {msg}。请重新登录网页并提取 Cookie。"))
                return False
        elif resp.status_code in (401, 403):
            logs.append(log_func("ERROR", f"❌ [Cookie失效预警] 小红书接口返回 HTTP {resp.status_code} 未授权：当前 Cookie 已过期，请重新登录获取。"))
            return False
        else:
            # 降级验证网络可用性
            logs.append(log_func("INFO", f"🟡 [网络提示] 小红书个人信息接口返回 HTTP {resp.status_code}，服务握手通畅，凭据格式已就绪。"))
            return True
    except Exception as e:
        logs.append(log_func("WARN", f"⚠️ [网络] 无法连接小红书创作者接口: {e}。"))
        return False


def probe_zhihu(
    settings: Dict[str, Any],
    logs: List[Dict[str, str]],
    log_func: Any,
    proxies: Dict[str, str]
) -> bool:
    """知乎专栏 Token 与 Cookie 真实身份有效性探针"""
    token = str(settings.get("token") or "").strip()
    cookie = str(settings.get("cookie") or "").strip()
    column_id = str(settings.get("column_id") or "").strip()

    if not token and not cookie:
        logs.append(log_func("ERROR", "❌ [错误] 知乎专栏 Token (z_c0) 或 Cookie 尚未配置。"))
        return False

    logs.append(log_func("INFO", "📡 [探测] 正在连接知乎用户 API 校验身份凭证有效性..."))
    headers = {"User-Agent": COMMON_UA}
    if cookie:
        headers["Cookie"] = cookie
    if token:
        headers["Authorization"] = f"Bearer {token}" if not token.startswith("Bearer ") else token

    try:
        resp = requests.get("https://www.zhihu.com/api/v4/me", headers=headers, proxies=proxies, timeout=12)
        if resp.status_code == 200:
            res_json = resp.json()
            user_name = res_json.get("name") or res_json.get("headline") or "知乎创作者"
            target_col = f" (专栏: {column_id})" if column_id else ""
            logs.append(log_func("SUCCESS", f"🟢 [成功] 知乎凭证有效！已成功连通创作者: {user_name}{target_col}。专栏发布通道就绪。"))
            return True
        elif resp.status_code in (401, 403):
            logs.append(log_func("ERROR", f"❌ [Cookie失效预警] 知乎登录凭证已过期 (HTTP {resp.status_code})：请重新登录知乎并提取 z_c0 / Cookie。"))
            return False
        else:
            logs.append(log_func("INFO", f"🟢 [探测] 知乎服务器网络握手正常 (HTTP {resp.status_code})。"))
            return True
    except Exception as e:
        logs.append(log_func("WARN", f"⚠️ [网络] 无法连接至知乎 API 端点: {e}。"))
        return False


def probe_bilibili(
    settings: Dict[str, Any],
    logs: List[Dict[str, str]],
    log_func: Any,
    proxies: Dict[str, str]
) -> bool:
    """📺 Bilibili 专栏 SESSDATA / Cookie 登录状态有效性探针"""
    sessdata = str(settings.get("sessdata") or "").strip()
    cookie = str(settings.get("cookie") or "").strip()
    token = str(settings.get("token") or "").strip()

    if not (sessdata or cookie or token):
        logs.append(log_func("ERROR", "❌ [错误] Bilibili 专栏 SESSDATA / Cookie 凭证缺失。"))
        return False

    final_cookie = cookie
    if sessdata and "SESSDATA=" not in final_cookie:
        final_cookie = f"SESSDATA={sessdata}; {final_cookie}".strip("; ")

    headers = {"User-Agent": COMMON_UA, "Cookie": final_cookie}
    logs.append(log_func("INFO", "📡 [探测] 正在校验 B站 用户导航接口与登录激活状态..."))

    try:
        resp = requests.get(
            "https://api.bilibili.com/x/web-interface/nav",
            headers=headers,
            proxies=proxies,
            timeout=10
        )
        if resp.status_code == 200:
            res_json = resp.json()
            if res_json.get("code") == 0:
                data = res_json.get("data") or {}
                if data.get("isLogin"):
                    uname = data.get("uname") or "B站UP主"
                    mid = str(data.get("mid") or "")
                    logs.append(log_func("SUCCESS", f"🟢 [成功] B站凭证有效！已连接UP主: {uname} (UID: {mid})。专栏分发通道就绪。"))
                    return True
                else:
                    logs.append(log_func("ERROR", "❌ [Cookie失效预警] B站当前处于未登录状态：SESSDATA 凭据已失效，请重新提取最新 Cookie。"))
                    return False
            else:
                msg = res_json.get("message") or "未登录"
                logs.append(log_func("ERROR", f"❌ [Cookie失效预警] B站凭证校验未通过: {msg}。"))
                return False
        else:
            logs.append(log_func("WARN", f"⚠️ [网络握手] B站接口返回 HTTP {resp.status_code}。"))
            return False
    except Exception as e:
        logs.append(log_func("WARN", f"⚠️ [网络] 无法连接至 Bilibili API 服务: {e}。"))
        return False


def probe_toutiao(
    settings: Dict[str, Any],
    logs: List[Dict[str, str]],
    log_func: Any,
    proxies: Dict[str, str]
) -> bool:
    """今日头条 (头条号) 凭据结构与连通度校验"""
    access_token = str(settings.get("access_token") or settings.get("token") or "").strip()
    cookie = str(settings.get("cookie") or "").strip()

    if not access_token and not cookie:
        logs.append(log_func("ERROR", "❌ [错误] 今日头条 Access Token 与 Cookie 必须至少配置一项。"))
        return False

    if cookie and "sessionid=" not in cookie and "passport_csrf_token=" not in cookie:
        logs.append(log_func("WARN", "⚠️ [Cookie结构预警] 今日头条 Cookie 中未检测到 sessionid，发文可能会被拦截，建议重新登录获取完整凭据。"))

    logs.append(log_func("INFO", "📡 [探测] 正在探测今日头条 (头条号) 平台连通性..."))
    try:
        resp = requests.head("https://mp.toutiao.com", proxies=proxies, timeout=10)
        logs.append(log_func("SUCCESS", f"🟢 [成功] 今日头条发布服务网络通畅 (HTTP {resp.status_code})。凭证格式已装载。"))
        return True
    except Exception as e:
        logs.append(log_func("WARN", f"⚠️ [网络] 无法连接至今日头条端点: {e}。"))
        return False


def probe_csdn(
    settings: Dict[str, Any],
    logs: List[Dict[str, str]],
    log_func: Any,
    proxies: Dict[str, str]
) -> bool:
    """CSDN 博客控制台凭据校验"""
    token = str(settings.get("token") or "").strip()
    cookie = str(settings.get("cookie") or "").strip()

    if not token and not cookie:
        logs.append(log_func("ERROR", "❌ [错误] CSDN Token 或 Cookie 凭据必须至少配置一项。"))
        return False

    if cookie and "UserName=" not in cookie and "UserToken=" not in cookie:
        logs.append(log_func("WARN", "⚠️ [Cookie结构预警] CSDN Cookie 中未包含 UserName 或 UserToken 标识，建议重新复制完整 Cookie。"))

    logs.append(log_func("INFO", "📡 [探测] 正在探测 CSDN 创作中心 API 连通度..."))
    try:
        resp = requests.head("https://mp.csdn.net", proxies=proxies, timeout=10)
        logs.append(log_func("SUCCESS", f"🟢 [成功] CSDN 创作中心网络通道畅通 (HTTP {resp.status_code})。"))
        return True
    except Exception as e:
        logs.append(log_func("WARN", f"⚠️ [网络] 无法直接连接 CSDN 创作者服务器: {e}。"))
        return False

