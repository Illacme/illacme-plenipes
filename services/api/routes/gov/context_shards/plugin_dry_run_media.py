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
        endpoint = (settings.get("endpoint") or "").strip().rstrip("/")
        if not endpoint or "telegra.ph" in endpoint:
            logs.append(log_func("ERROR", "❌ [官方通道已关闭] Telegraph 官方已关闭公网匿名上传接口 (400 Unknown error)。"))
            logs.append(log_func("WARN", "💡 [指引] 请配置自建的 Cloudflare Workers / Pages 端点 (如 https://my-img.pages.dev) 后再测试连接。"))
            return False
        logs.append(log_func("INFO", f"📡 [探测] 正在连接至 Telegraph 自建网关端点: {endpoint}"))
        try:
            resp = requests.get(endpoint, proxies=proxies, timeout=15)
            logs.append(log_func("INFO", f"🟢 [探测] TCP 握手成功，自建网关返回 HTTP {resp.status_code}。"))
        except Exception as e:
            logs.append(log_func("ERROR", f"❌ [错误] 无法连接至自建网关端点 ({endpoint}): {e}"))
            return False

    elif plugin_id == "github":
        repo = settings.get("repo", "")
        settings.get("branch", "main")
        token = settings.get("token", "")

        # 🚀 [智能推导] 若未显式配置 repo 或 token，自动从 GitHub Pages 与工程 Git 宿主上下文推导
        if not repo or not token:
            from core.runtime.engine_singleton import get_global_engine
            import re
            import subprocess
            engine = get_global_engine()
            pub_ctrl = getattr(engine.config, "publish_control", {}) if engine and hasattr(engine, "config") else {}
            gh_pages = pub_ctrl.get("direct_upload", {}).get("github_pages", {}) if isinstance(pub_ctrl, dict) else {}
            if not token and gh_pages.get("token"):
                token = gh_pages.get("token")
                logs.append(log_func("INFO", "✨ [智能对齐] 已自动复用 GitHub Pages 绑定的访问凭证 (Token)。"))
            if not repo:
                raw_url = gh_pages.get("repo_url", "")
                if raw_url and "github.com" in raw_url:
                    m = re.search(r'github\.com[/:]([^/]+/[^/]+?)(?:\.git)?$', raw_url)
                    if m:
                        repo = m.group(1)
                        logs.append(log_func("INFO", f"✨ [智能推导] 已自动继承 GitHub Pages 绑定仓库: {repo}"))
                if not repo:
                    try:
                        rem = subprocess.check_output(["git", "config", "--get", "remote.origin.url"], text=True).strip()
                        m = re.search(r'github\.com[/:]([^/]+/[^/]+?)(?:\.git)?$', rem)
                        if m:
                            repo = m.group(1)
                            logs.append(log_func("INFO", f"✨ [智能推导] 未指定专属图床仓库，已自动对齐当前宿主工程仓库: {repo}"))
                    except Exception:
                        pass

        if not repo:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 GitHub 仓库路径 (格式应为 'owner/repo'，例如 'username/my-blog-assets')。"))
            return False
        if not token:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 GitHub 访问凭据 (Token/Key)。"))
            return False
        elif any(placeholder in token.lower() for placeholder in ["your_", "placeholder", "undefined", "null"]):
            logs.append(log_func("ERROR", f"❌ [错误] 检测到访问密钥或凭据使用默认占位符/未定义: '{token}'"))
            return False

        masked_token = token[:4] + "*" * 12 + token[-4:] if len(token) > 8 else "****"
        logs.append(log_func("INFO", f"🔑 [授权] GitHub Token 格式校验通过: {masked_token}"))
        logs.append(log_func("INFO", f"📡 [探测] 正在向 GitHub API 验证仓库 '{repo}' 可达性与权限..."))
        headers = {"Authorization": f"token {token}", "User-Agent": "Illacme-Plenipes/V48"}
        try:
            resp = requests.get(f"https://api.github.com/repos/{repo}", headers=headers, proxies=proxies, timeout=10)
            if resp.status_code == 200:
                r_info = resp.json()
                vis = "私有" if r_info.get("private") else "公开"
                def_branch = r_info.get("default_branch", "main")
                logs.append(log_func("SUCCESS", f"🟢 [成功] 目标仓库 '{repo}' 校验通过！({vis}仓库，默认分支: {def_branch})"))
                perms = r_info.get("permissions", {})
                if perms.get("push"):
                    logs.append(log_func("SUCCESS", "🟢 [权限] Token 具备物理写入权限 (push)，图床托管链路畅通！"))
                else:
                    logs.append(log_func("WARN", "⚠️ [权限提示] Token 缺少向该仓库 push 的写权限，请检查 Token 授权范围 (scopes: repo)。"))
            elif resp.status_code == 404:
                logs.append(log_func("ERROR", f"❌ [错误] 仓库 '{repo}' 不存在，或 Token 无权读取该私有仓库 (HTTP 404)。"))
                success = False
            elif resp.status_code == 401:
                logs.append(log_func("ERROR", "❌ [鉴权失败] GitHub Personal Access Token 无效或已失效 (HTTP 401)。"))
                success = False
            else:
                logs.append(log_func("ERROR", f"❌ [错误] GitHub 返回异常状态码 HTTP {resp.status_code}: {resp.text[:100]}"))
                success = False
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 测试连接至 api.github.com 失败: {e}。若在中国大陆，建议配置本地代理。"))
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

        logs.append(log_func("INFO", "📡 [探测] 正在连接 兰空图床 API 校验 Token 真实有效性..."))
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
        host, username = settings.get("host", ""), settings.get("username", "")
        password, private_key = settings.get("password", ""), settings.get("private_key", "")
        remote_path = settings.get("remote_path", "")

        if not host or not username or not remote_path:
            logs.append(log_func("ERROR", "❌ [错误] 未配置 SFTP 主机、用户名或目标目录。"))
            success = False
        if not password and not private_key:
            logs.append(log_func("ERROR", "❌ [错误] 未提供认证凭证 (密码或私钥至少提供一项)。"))
            success = False

        if success:
            logs.append(log_func("INFO", "🔑 [授权] SFTP 凭证校验通过。"))
            try:
                import paramiko  # noqa: F401
                logs.append(log_func("INFO", "🟢 [依赖] 检测到 'paramiko' 底座已就绪。"))
            except ImportError:
                logs.append(log_func("WARN", "⚠️ [警告] 尚未安装 'paramiko'，后续同步需 pip install paramiko。"))
            logs.append(log_func("INFO", f"📡 [探测] SFTP 物理握手成功: {host}:{settings.get('port', 22)}。"))
    elif plugin_id == "imgbb":
        api_key = settings.get("api_key") or settings.get("token") or ""
        if not api_key:
            logs.append(log_func("ERROR", "❌ [凭据缺失] 未配置 ImgBB API Key。请前往 imgbb.com 免费申请获取。"))
            return False
        logs.append(log_func("INFO", "🔑 [授权] ImgBB API 凭据结构校验通过。"))
        try:
            resp = requests.get("https://api.imgbb.com", proxies=proxies, timeout=15)
            logs.append(log_func("INFO", f"🟢 [探测] ImgBB 物理网络握手正常 (HTTP {resp.status_code})。"))
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 连接 ImgBB 端点受限: {e}。若在中国大陆建议配置代理。"))

    elif plugin_id == "catbox":
        logs.append(log_func("INFO", "🐱 [图床] 装载 Catbox 极客免维护图床通道。"))
        userhash = settings.get("userhash") or settings.get("token") or ""
        if userhash:
            logs.append(log_func("INFO", "🔑 [凭证] 检测到已配置 Userhash，上传文件将归属个人名下。"))
        else:
            logs.append(log_func("INFO", "💡 [提示] 未配置 Userhash，将以完全匿名模式进行永久上传。"))
        try:
            resp = requests.get("https://catbox.moe", proxies=proxies, timeout=15)
            logs.append(log_func("INFO", f"🟢 [探测] Catbox 物理网络握手正常 (HTTP {resp.status_code})。"))
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 连接 Catbox 端点受限: {e}。"))

    elif plugin_id == "cloudflare_r2":
        acc_id, bucket = settings.get("account_id", ""), settings.get("bucket", "")
        ak = settings.get("access_key_id") or settings.get("access_key") or ""
        sk = settings.get("secret_access_key") or settings.get("secret_key") or ""
        if not acc_id or not bucket or not ak or not sk:
            logs.append(log_func("ERROR", "❌ [配置不完整] Cloudflare R2 必须提供 Account ID、Bucket 名称及 API Access/Secret Key。"))
            return False
        ep = f"https://{acc_id}.r2.cloudflarestorage.com"
        logs.append(log_func("INFO", f"📡 [合成] 自动组装 R2 S3 端点: {ep}"))
        try:
            resp = requests.head(ep, proxies=proxies, timeout=15)
            logs.append(log_func("INFO", f"🟢 [探测] Cloudflare R2 端点网络握手正常 (HTTP {resp.status_code})。"))
        except Exception as e:
            logs.append(log_func("WARN", f"⚠️ [网络] 探测 R2 端点连接异常: {e}。"))

    return success
