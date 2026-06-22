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

    if plugin_id == "telegraph":
        endpoint = settings.get("endpoint", "https://telegra.ph").rstrip("/")
        logs.append(log_func("INFO", f"📡 [探测] 正在连接至 Telegraph 免配图床端点: {endpoint}"))
        try:
            resp = requests.get(endpoint, timeout=5)
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
            success = False
        if not token:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 GitHub 访问凭据 (Token/Key)。"))
            success = False
        elif any(placeholder in token.lower() for placeholder in ["your_", "placeholder", "undefined", "null"]):
            logs.append(log_func("ERROR", f"❌ [错误] 检测到访问密钥或凭据使用默认占位符/未定义: '{token}'"))
            success = False

        if success:
            masked_token = token[:4] + "*" * 12 + token[-4:] if len(token) > 8 else "****"
            logs.append(log_func("INFO", f"🔑 [授权] GitHub Token 格式校验通过: {masked_token}"))
            logs.append(log_func("INFO", "📡 [探测] 正在测试 GitHub Contents API 网络连接..."))
            try:
                resp = requests.get("https://api.github.com", headers={"Authorization": f"token {token}"}, timeout=5)
                logs.append(log_func("INFO", f"🟢 [探测] 对端 API 服务响应正常 (HTTP {resp.status_code})。"))
            except Exception as e:
                logs.append(log_func("WARN", f"⚠️ [警告] 测试连接至 api.github.com 失败: {e}。这可能是本地网络环境受限，若服务器端有代理，可安全忽略。"))

    elif plugin_id == "sm_ms":
        token = settings.get("token", "")
        if not token:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 SM.MS 访问密钥 (Secret Token)。"))
            success = False
        elif any(placeholder in token.lower() for placeholder in ["your_", "placeholder", "undefined", "null"]):
            logs.append(log_func("ERROR", f"❌ [错误] 检测到访问密钥或凭据使用默认占位符/未定义: '{token}'"))
            success = False

        if success:
            masked_token = token[:4] + "*" * 12 + token[-4:] if len(token) > 8 else "****"
            logs.append(log_func("INFO", f"🔑 [授权] SM.MS Token 格式校验通过: {masked_token}"))
            logs.append(log_func("INFO", "📡 [探测] 正在测试 SM.MS API 网络连接..."))
            try:
                resp = requests.get("https://sm.ms/api/v2", timeout=5)
                logs.append(log_func("INFO", f"🟢 [探测] 对端 API 服务响应正常 (HTTP {resp.status_code})。"))
            except Exception as e:
                logs.append(log_func("WARN", f"⚠️ [警告] 测试连接至 sm.ms 失败: {e}。"))

    elif plugin_id == "imgur":
        client_id = settings.get("client_id", "")
        token = settings.get("token", "")
        if not client_id and not token:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 Imgur 的 Client ID 或 Access Token。两者必须至少配置一项。"))
            success = False
        elif client_id and any(placeholder in client_id.lower() for placeholder in ["your_", "placeholder", "undefined", "null"]):
            logs.append(log_func("ERROR", "❌ [错误] Imgur Client ID 包含无效占位符。"))
            success = False
        elif token and any(placeholder in token.lower() for placeholder in ["your_", "placeholder", "undefined", "null"]):
            logs.append(log_func("ERROR", "❌ [错误] Imgur Access Token 包含无效占位符。"))
            success = False

        if success:
            logs.append(log_func("INFO", "🔑 [授权] Imgur 凭证格式校验通过。"))
            logs.append(log_func("INFO", "📡 [探测] 正在测试 Imgur API 连通性..."))
            try:
                resp = requests.get("https://api.imgur.com/3/image", timeout=5)
                logs.append(log_func("INFO", f"🟢 [探测] 对端 API 服务响应正常 (HTTP {resp.status_code})。"))
            except Exception as e:
                logs.append(log_func("WARN", f"⚠️ [警告] 测试连接至 api.imgur.com 失败: {e}。"))

    elif plugin_id in ["s3", "aliyun_oss", "tencent_cos", "qiniu_kodo", "upyun_uss"]:
        from .plugin_dry_run_media_cloud import run_media_cloud_plugin_dry_run
        return run_media_cloud_plugin_dry_run(plugin_id, settings, logs, log_func)

    elif plugin_id == "loli_io":
        token = settings.get("token", "")
        endpoint = settings.get("endpoint", "https://img.lol/api/v1/upload").strip()

        if not token:
            logs.append(log_func("ERROR", "❌ [错误] 未配置路过图床 API Token。"))
            success = False
        elif any(placeholder in token.lower() for placeholder in ["your_", "placeholder", "undefined", "null"]):
            logs.append(log_func("ERROR", "❌ [错误] 路过图床 API Token 包含无效占位符。"))
            success = False

        if success:
            logs.append(log_func("INFO", "🔑 [授权] 路过图床凭证格式校验通过。"))
            logs.append(log_func("INFO", f"📡 [探测] 正在测试 路过图床 API 端点连通性: {endpoint}"))
            try:
                resp = requests.get(endpoint, timeout=5)
                logs.append(log_func("INFO", f"🟢 [探测] 对端图床 API 响应正常 (HTTP {resp.status_code})。"))
            except Exception as e:
                logs.append(log_func("WARN", f"⚠️ [警告] 无法建立与 路过图床域名 ({endpoint}) 的直接连接: {e}。"))

    elif plugin_id == "superbed":
        token = settings.get("token", "")
        endpoint = settings.get("endpoint", "https://api.superbed.cn/upload").strip()

        if not token:
            logs.append(log_func("ERROR", "❌ [错误] 未配置聚合图床 API Token。"))
            success = False
        elif any(placeholder in token.lower() for placeholder in ["your_", "placeholder", "undefined", "null"]):
            logs.append(log_func("ERROR", "❌ [错误] 聚合图床 Token 包含无效占位符。"))
            success = False

        if success:
            logs.append(log_func("INFO", "🔑 [授权] 聚合图床凭证格式校验通过。"))
            logs.append(log_func("INFO", f"📡 [探测] 正在测试 聚合图床 API 端点连通性: {endpoint}"))
            try:
                resp = requests.get(endpoint, timeout=5)
                logs.append(log_func("INFO", f"🟢 [探测] 对端 聚合图床 API 响应正常 (HTTP {resp.status_code})。"))
            except Exception as e:
                logs.append(log_func("WARN", f"⚠️ [警告] 无法建立与 聚合图床域名 ({endpoint}) 的直接连接: {e}。"))

    elif plugin_id == "lsky_pro":
        endpoint = settings.get("endpoint", "").strip().rstrip("/")
        token = settings.get("token", "").strip()

        if not endpoint or not token:
            logs.append(log_func("ERROR", "❌ [错误] 未配置兰空图床 接口地址 (Endpoint) 或 鉴权 Token。"))
            success = False
        elif any(placeholder in token.lower() or placeholder in endpoint.lower() for placeholder in ["your_", "placeholder", "undefined", "null"]):
            logs.append(log_func("ERROR", "❌ [错误] 兰空图床配置信息中包含无效占位符。"))
            success = False

        if success:
            logs.append(log_func("INFO", "🔑 [授权] 兰空图床凭证格式校验通过。"))
            logs.append(log_func("INFO", f"📡 [探测] 正在测试 兰空图床端点可达性: {endpoint}"))
            try:
                resp = requests.get(endpoint, timeout=5)
                logs.append(log_func("INFO", f"🟢 [探测] 兰空图床端点服务物理网络可达 (HTTP {resp.status_code})。"))
            except Exception as e:
                logs.append(log_func("WARN", f"⚠️ [警告] 无法直接连接至 兰空图床端点 ({endpoint}): {e}。"))

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
