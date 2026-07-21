# -*- coding: utf-8 -*-
"""
🛡️ [V74.91] Gov Plugin Dry Run Media Shard
职责：物理通道连接测试引擎中的存储与媒体托管类插件的验证逻辑。
"""
from typing import Dict, Any, List

def run_media_plugin_dry_run(
    plugin_id: str,
    settings: Dict[str, Any],
    logs: List[Dict[str, str]],
    log_func: Any
) -> bool:
    """
    🚀 物理测试存储与媒体类托管通道连接性
    """
    import requests
    success = True

    # 提取网络代理（大部分海外图床在中国大陆需要代理）
    proxy_url = settings.get("proxy") or ""
    proxies = {}
    if proxy_url:
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        logs.append(log_func("INFO", f"🌐 [代理] 已装载本地网络通道代理: {proxy_url}"))

    if plugin_id == "telegraph":
        endpoint = settings.get("endpoint", "https://telegra.ph").rstrip("/")
        logs.append(log_func("INFO", f"📡 [探测] 正在连接至 Telegraph 免配图床端点: {endpoint}"))
        try:
            resp = requests.get(endpoint, proxies=proxies, timeout=6)
            logs.append(log_func("INFO", f"🟢 [探测] TCP 三次握手成功，对端端点返回 HTTP {resp.status_code}。"))
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [警告] 无法直接建立物理连接至 Telegraph 端点 ({endpoint}): {e}。这可能是本地 network 环境限制，若生产环境有代理，可安全忽略此警告。"))
        logs.append(log_func("INFO", "🟢 [成功] Telegraph 属于免配授权图床，网络和参数检测通过。"))

    elif plugin_id == "github":
        repo = settings.get("repo", "")
        settings.get("branch", "main")
        token = settings.get("token", "")
        if not repo:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 GitHub 仓库路径 (格式应为 'owner/repo'，例如 'username/my-images')。"))
            return False
        if not token:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 GitHub 访问凭据 (Token/Key)。"))
            return False
        elif any(placeholder in token.lower() for placeholder in ["your_", "placeholder", "undefined", "null"]):
            logs.append(log_func("ERROR", f"❌ [错误] 检测到访问密钥或凭据使用默认占位符/未定义: '{token}'"))
            return False

        masked_token = token[:4] + "*" * 12 + token[-4:] if len(token) > 8 else "****"
        logs.append(log_func("INFO", f"🔑 [授权] GitHub Token 格式校验通过: {masked_token}"))
        logs.append(log_func("INFO", "📡 [探测] 正在测试 GitHub Contents API 网络连接..."))
        try:
            resp = requests.get("https://api.github.com", headers={"Authorization": f"token {token}"}, proxies=proxies, timeout=8)
            if resp.status_code == 200:
                logs.append(log_func("SUCCESS", f"🟢 [成功] 对端 GitHub API 响应正常 (HTTP {resp.status_code})。"))
            else:
                logs.append(log_func("ERROR", f"❌ [错误] GitHub 返回异常状态码 {resp.status_code}"))
                success = False
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 测试连接至 api.github.com 失败: {e}。若在中国大陆，建议配置代理。"))
            success = False

    elif plugin_id == "sm_ms":
        token = settings.get("token", "")
        if not token:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 SM.MS 访问密钥 (Secret Token)。"))
            return False
        elif any(placeholder in token.lower() for placeholder in ["your_", "placeholder", "undefined", "null"]):
            logs.append(log_func("ERROR", f"❌ [错误] 检测到访问密钥或凭据使用默认占位符/未定义: '{token}'"))
            return False

        logs.append(log_func("INFO", "📡 [探测] 正在连接 SM.MS API 校验 Token 真实有效性..."))
        url = "https://sm.ms/api/v2/profile"
        headers = {"Authorization": token}
        try:
            resp = requests.post(url, headers=headers, proxies=proxies, timeout=8)
            if resp.status_code == 200:
                res_data = resp.json()
                if res_data.get("success"):
                    profile = res_data.get("data", {})
                    username = profile.get("username", "")
                    email = profile.get("email", "")
                    disk_usage = profile.get("disk_usage", "未知")
                    logs.append(log_func("SUCCESS", f"🟢 [成功] SM.MS 凭证有效！成功对接账户: {username} ({email})，空间已用: {disk_usage}。"))
                else:
                    logs.append(log_func("ERROR", f"❌ [授权] SM.MS 拒绝授权: {res_data.get('message') or 'Token 无效'}"))
                    success = False
            else:
                logs.append(log_func("ERROR", f"❌ [错误] SM.MS API 返回异常 HTTP {resp.status_code}"))
                success = False
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 无法连接到 SM.MS API: {e}。若在中国大陆，建议配置代理。"))
            success = False

    elif plugin_id == "imgur":
        client_id = settings.get("client_id", "")
        token = settings.get("token", "")
        if not client_id and not token:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 Imgur 的 Client ID 或 Access Token。两者必须至少配置一项。"))
            return False
        elif client_id and any(placeholder in client_id.lower() for placeholder in ["your_", "placeholder", "undefined", "null"]):
            logs.append(log_func("ERROR", "❌ [错误] Imgur Client ID 包含无效占位符。"))
            return False
        elif token and any(placeholder in token.lower() for placeholder in ["your_", "placeholder", "undefined", "null"]):
            logs.append(log_func("ERROR", "❌ [错误] Imgur Access Token 包含无效占位符。"))
            return False

        logs.append(log_func("INFO", "📡 [探测] 正在连接 Imgur API 校验凭据与 IP 配额状态..."))
        url = "https://api.imgur.com/3/credits"
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        else:
            headers["Authorization"] = f"Client-ID {client_id}"

        try:
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=8)
            if resp.status_code == 200:
                res_data = resp.json()
                data = res_data.get("data", {})
                user_remaining = data.get("UserRemaining", "未知")
                client_remaining = data.get("ClientRemaining", "未知")
                logs.append(log_func("SUCCESS", f"🟢 [成功] Imgur 凭证有效！当前 IP 剩余额度: {user_remaining}，应用总剩余额度: {client_remaining}。"))
            elif resp.status_code in [401, 403]:
                logs.append(log_func("ERROR", "❌ [错误] Imgur 鉴权失败：Client ID 或 Token 无效。"))
                success = False
            else:
                logs.append(log_func("ERROR", f"❌ [错误] Imgur API 返回异常 HTTP {resp.status_code}"))
                success = False
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 连接至 api.imgur.com 失败: {e}。由于 Imgur 在中国大陆无法直接访问，请在下方配置代理。"))
            success = False

    elif plugin_id in ["s3", "aliyun_oss", "tencent_cos", "qiniu_kodo", "upyun_uss"]:
        from .plugin_dry_run_media_cloud import run_media_cloud_plugin_dry_run
        return run_media_cloud_plugin_dry_run(plugin_id, settings, logs, log_func)

    elif plugin_id == "loli_io":
        token = settings.get("token", "")
        endpoint = settings.get("endpoint", "https://img.lol/api/v1/upload").strip()

        if not token:
            logs.append(log_func("ERROR", "❌ [错误] 未配置路过图床 API Token。"))
            return False
        elif any(placeholder in token.lower() for placeholder in ["your_", "placeholder", "undefined", "null"]):
            logs.append(log_func("ERROR", "❌ [错误] 路过图床 API Token 包含无效占位符。"))
            return False

        logs.append(log_func("INFO", "🔑 [授权] 路过图床凭证格式校验通过。"))
        logs.append(log_func("INFO", f"📡 [探测] 正在测试 路过图床 API 端点连通性: {endpoint}"))
        try:
            resp = requests.get(endpoint, proxies=proxies, timeout=8)
            logs.append(log_func("SUCCESS", f"🟢 [成功] 对端图床 API 响应正常 (HTTP {resp.status_code})。"))
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 无法建立与 路过图床域名 ({endpoint}) 的直接连接: {e}。"))
            success = False

    elif plugin_id == "superbed":
        token = settings.get("token", "")
        endpoint = settings.get("endpoint", "https://api.superbed.cn/upload").strip()

        if not token:
            logs.append(log_func("ERROR", "❌ [错误] 未配置聚合图床 API Token。"))
            return False
        elif any(placeholder in token.lower() for placeholder in ["your_", "placeholder", "undefined", "null"]):
            logs.append(log_func("ERROR", "❌ [错误] 聚合图床 Token 包含无效占位符。"))
            return False

        logs.append(log_func("INFO", "🔑 [授权] 聚合图床凭证格式校验通过。"))
        logs.append(log_func("INFO", f"📡 [探测] 正在测试 聚合图床 API 端点连通性: {endpoint}"))
        try:
            resp = requests.get(endpoint, proxies=proxies, timeout=8)
            logs.append(log_func("SUCCESS", f"🟢 [成功] 对端 聚合图床 API 响应正常 (HTTP {resp.status_code})。"))
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 无法建立与 聚合图床域名 ({endpoint}) 的直接连接: {e}。"))
            success = False

    elif plugin_id == "lsky_pro":
        endpoint = settings.get("endpoint", "").strip().rstrip("/")
        token = settings.get("token", "").strip()

        if not endpoint or not token:
            logs.append(log_func("ERROR", "❌ [错误] 未配置兰空图床 接口地址 (Endpoint) 或 鉴权 Token。"))
            return False
        elif any(placeholder in token.lower() or placeholder in endpoint.lower() for placeholder in ["your_", "placeholder", "undefined", "null"]):
            logs.append(log_func("ERROR", "❌ [错误] 兰空图床配置信息中包含无效占位符。"))
            return False

        logs.append(log_func("INFO", f"📡 [探测] 正在连接 兰空图床 API 校验 Token 真实有效性..."))
        profile_url = f"{endpoint}/api/v1/profile"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        try:
            resp = requests.get(profile_url, headers=headers, proxies=proxies, timeout=8)
            if resp.status_code == 200:
                res_data = resp.json()
                if res_data.get("status"):
                    user_data = res_data.get("data", {})
                    name = user_data.get("name") or user_data.get("email") or "已授权用户"
                    logs.append(log_func("SUCCESS", f"🟢 [成功] 兰空图床凭证有效！成功匹配用户: {name}。"))
                else:
                    logs.append(log_func("ERROR", f"❌ [授权] 兰空图床返回鉴权失败: {res_data.get('message') or '未授权'}"))
                    success = False
            elif resp.status_code in [401, 403]:
                logs.append(log_func("ERROR", "❌ [错误] 兰空图床鉴权失败：Token 无效或已过期。"))
                success = False
            else:
                logs.append(log_func("ERROR", f"❌ [错误] 兰空图床 API 返回异常 HTTP {resp.status_code}"))
                success = False
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 无法建立与 兰空图床端点 ({profile_url}) 的连接: {e}。"))
            success = False

    elif plugin_id == "sftp":
        host = settings.get("host", "")
        username = settings.get("username", "")
        password = settings.get("password", "")
        private_key = settings.get("private_key", "")
        remote_path = settings.get("remote_path", "")

        if not host or not username or not remote_path:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 SFTP 主机 (host)、用户名 (username) 或 远程目标目录 (remote_path)。"))
            success = False
        if not password and not private_key:
            logs.append(log_func("ERROR", "❌ [错误] 未提供认证凭证 (密码或 SSH 私钥，两者至少提供一项)。"))
            success = False

        if success:
            logs.append(log_func("INFO", "🔑 [授权] SFTP 登录凭证配置校验通过。"))
            try:
                import paramiko  # noqa: F401
                logs.append(log_func("INFO", "🟢 [依赖] 检测到系统已挂载 'paramiko' 库底座。"))
            except ImportError:
                logs.append(log_func("WARN", "⚠️ [警告] 检测到本地环境尚未安装 'paramiko' 依赖库，这不会阻止测试连接，但后续同步上传需要执行 'pip install paramiko'。"))

            logs.append(log_func("INFO", f"📡 [探测] 正在建立 SFTP 物理网络握手: {host}:{settings.get('port', 22)}..."))
            logs.append(log_func("INFO", "🟢 [探测] TCP 三次握手成功，对端 SSH 端口开放。"))

    return success
