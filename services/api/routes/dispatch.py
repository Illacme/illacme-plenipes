#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📡 [V68.0] Illacme Plenipes - Dispatch Hub API (Router Hub)
职责：仅定义资产分发状态控制路由契约，实体业务逻辑均委派至门面 dispatch_ops.py。
"""

from fastapi import APIRouter, Depends, HTTPException
from .system import verify_token
from core.runtime.engine_singleton import get_global_engine

# 引入中枢逻辑代理层
from services.api.logic.dispatch_ops import (
    get_dispatch_status_facade,
    toggle_lab_facade,
    trigger_re_dispatch_facade,
    destroy_artifact_facade,
    get_pending_syndication_facade
)

router = APIRouter()

@router.get("/api/vault/dispatch-status/{doc_id:path}", dependencies=[Depends(verify_token)])
async def get_dispatch_status(doc_id: str):
    """
    🛰️ 物理感应探针 (Sovereign Sensing)
    委派给 telemetry_ops 分片完成，扫描真实产物分布并还原算力、费用与节点状态。
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return get_dispatch_status_facade(engine, doc_id)

@router.post("/api/vault/toggle-lab", dependencies=[Depends(verify_token)])
async def toggle_lab():
    """
    🧪 实时预览引擎物理调度 (Physical Daemon Scheduling)
    委派给 daemon_ops 分片完成，在后台线程中拉起/关闭 DevServer。
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return toggle_lab_facade(engine)

@router.post("/api/vault/re-dispatch/{doc_id:path}", dependencies=[Depends(verify_token)])
async def trigger_re_dispatch(doc_id: str, req: dict):
    """
    ♻️ 主权调度中心：强制推入出版管线
    委派给 pipeline_ops 分片完成，提交任务至异步线程池。
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return trigger_re_dispatch_facade(engine, doc_id, req)

@router.delete("/api/vault/destroy/{doc_id:path}", dependencies=[Depends(verify_token)])
async def destroy_artifact(doc_id: str):
    """
    🗑️ 物理销毁逻辑：抹除磁盘资产及其所有出版产物，并在账本中彻底注销
    委派给 pipeline_ops 分片完成，自愈清理多级空目录。
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return destroy_artifact_facade(engine, doc_id)

@router.get("/api/vault/pending-syndication", dependencies=[Depends(verify_token)])
async def get_pending_syndication():
    """
    📡 获取待同步至社交渠道的稿件信息（用于前端同步自愈引导）
    """
    engine = get_global_engine()
    if not engine:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    return get_pending_syndication_facade(engine)

@router.post("/api/plugins/cloudflare/oauth-login", dependencies=[Depends(verify_token)])
async def cloudflare_oauth_login():
    """
    🔑 本地免密一键授权：后台异步拉起 wrangler login 浏览器窗口
    """
    import subprocess
    try:
        subprocess.Popen(
            ["npx", "-y", "wrangler", "login"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        return {"success": True, "message": "已拉起您的系统浏览器，请在浏览器中完成 Cloudflare 账户授权。"}
    except Exception as e:
        return {"success": False, "message": f"拉起浏览器失败: {e}"}

@router.get("/api/plugins/cloudflare/oauth-status", dependencies=[Depends(verify_token)])
async def cloudflare_oauth_status():
    """
    📡 探测本地 wrangler 会话登录状态、Account ID 与 Pages 项目列表
    """
    import subprocess
    import re
    import json
    try:
        # 1. 探测基本账户状态
        result = subprocess.run(
            ["npx", "-y", "wrangler", "whoami"],
            capture_output=True,
            text=True,
            timeout=8
        )
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        combined = stdout + "\n" + stderr
        
        account_id_match = re.search(r"Account ID:\s*([a-fA-F0-9]{32})", combined)
        account_name_match = re.search(r"Account Name:\s*([^\n\r]+)", combined)
        email_match = re.search(r"logged in as\s*([^\s\n\r]+)", combined)
        
        if account_id_match:
            # 2. 已登录状态下，尝试静默探测 Pages 项目列表
            projects = []
            try:
                proj_res = subprocess.run(
                    ["npx", "-y", "wrangler", "pages", "project", "list", "--json"],
                    capture_output=True,
                    text=True,
                    timeout=8
                )
                if proj_res.returncode == 0:
                    proj_data = json.loads(proj_res.stdout or "[]")
                    if isinstance(proj_data, list):
                        for proj in proj_data:
                            if isinstance(proj, dict) and "name" in proj:
                                prod_branch = "production"
                                if "production_branch" in proj:
                                    prod_branch = proj["production_branch"]
                                elif "source" in proj and isinstance(proj["source"], dict):
                                    config = proj["source"].get("config", {})
                                    if isinstance(config, dict):
                                        prod_branch = config.get("production_branch", "production")
                                projects.append({
                                    "name": proj["name"],
                                    "branch": prod_branch
                                })
            except Exception:
                pass

            return {
                "logged_in": True,
                "account_id": account_id_match.group(1),
                "account_name": account_name_match.group(1).strip() if account_name_match else "默认账户",
                "email": email_match.group(1).strip() if email_match else "",
                "projects": projects
            }
        else:
            if "You are logged in" in combined:
                return {
                    "logged_in": True,
                    "message": "检测到本地会话已登录，但未能在输出中识别到 Account ID"
                }
            return {
                "logged_in": False,
                "message": "未检测到有效的 wrangler 登录会话"
            }
    except Exception as e:
        return {"logged_in": False, "message": f"探测登录状态发生异常: {e}"}

@router.post("/api/plugins/netlify/oauth-login", dependencies=[Depends(verify_token)])
async def netlify_oauth_login():
    """
    🔑 本地免密一键授权：后台异步拉起 netlify login 浏览器窗口
    """
    import subprocess
    try:
        subprocess.Popen(
            ["npx", "-y", "netlify-cli", "login"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        return {"success": True, "message": "已拉起您的系统浏览器，请在浏览器中完成 Netlify 账户授权。"}
    except Exception as e:
        return {"success": False, "message": f"拉起浏览器失败: {e}"}

@router.get("/api/plugins/netlify/oauth-status", dependencies=[Depends(verify_token)])
async def netlify_oauth_status():
    """
    📡 探测本地 netlify 会话登录状态与 Token
    """
    import os
    import json
    config_path = os.path.expanduser("~/.config/netlify/config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 支持老的及新的 Netlify CLI 会话格式
            access_token = data.get("access_token")
            user_info = data.get("users", {}).get("default", {})
            if access_token or user_info:
                return {
                    "logged_in": True,
                    "username": user_info.get("name") or "已授权 Netlify 账户",
                    "email": user_info.get("email") or "",
                    "token": access_token or ""
                }
        except Exception:
            pass
    return {"logged_in": False, "message": "未检测到本地有效的 Netlify 登录会话，请先点击登录授权"}

@router.post("/api/plugins/vercel/oauth-login", dependencies=[Depends(verify_token)])
async def vercel_oauth_login():
    """
    🔑 本地免密一键授权：后台异步拉起 vercel login 验证
    """
    import subprocess
    try:
        # vercel login 调起后需要用户在终端与浏览器交互，强制注入 -y
        subprocess.Popen(
            ["npx", "-y", "vercel", "login"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        return {"success": True, "message": "已拉起您的系统浏览器，请完成 Vercel 邮箱或第三方授权。"}
    except Exception as e:
        return {"success": False, "message": f"拉起浏览器失败: {e}"}

@router.get("/api/plugins/vercel/oauth-status", dependencies=[Depends(verify_token)])
async def vercel_oauth_status():
    """
    📡 探测本地 vercel 会话登录状态与 Token
    """
    import os
    import json
    config_path = os.path.expanduser("~/.config/vercel/auth.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            token = data.get("token")
            if token:
                return {
                    "logged_in": True,
                    "username": data.get("username") or "已授权 Vercel 账户",
                    "token": token
                }
        except Exception:
            pass
    return {"logged_in": False, "message": "未检测到本地有效的 Vercel 登录会话，请先点击登录授权"}

@router.get("/api/plugins/github/ssh-status", dependencies=[Depends(verify_token)])
async def github_ssh_status():
    """
    📡 探测本地机器与 GitHub 的 SSH 密钥连通状态 (用于免 Token 部署引导)
    """
    import subprocess
    import re
    try:
        # 探测 ssh 是否畅通 (不使用严格主机校验以防挂起)
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=4", "-o", "StrictHostKeyChecking=no", "-T", "git@github.com"],
            capture_output=True,
            text=True,
            timeout=5
        )
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        combined = stdout + "\n" + stderr
        
        # GitHub 成功时的握手文本是 "Hi <username>! You've successfully authenticated..."
        match = re.search(r"Hi\s+([^\s!]+)!\s+You've\s+successfully\s+authenticated", combined)
        if match:
            return {
                "ssh_ok": True,
                "username": match.group(1),
                "message": f"探测到本地 SSH 密钥与 GitHub 连通极佳，您可以使用 SSH 地址免密克隆与发布！"
            }
    except Exception:
        pass
    return {"ssh_ok": False, "message": "未能连接到 GitHub SSH 服务，建议填入访问令牌 (Token)"}

@router.post("/api/plugins/firebase/oauth-login", dependencies=[Depends(verify_token)])
async def firebase_oauth_login():
    """
    🔑 本地免密一键授权：后台异步拉起 firebase login 验证
    """
    import subprocess
    try:
        # firebase login 需要开启浏览器进行交互，使用 npx -y 启动
        subprocess.Popen(
            ["npx", "-y", "firebase-tools", "login"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        return {"success": True, "message": "已拉起您的系统浏览器，请完成 Firebase CLI 授权登录。"}
    except Exception as e:
        return {"success": False, "message": f"拉起 Firebase 登录失败: {e}"}

@router.get("/api/plugins/firebase/oauth-status", dependencies=[Depends(verify_token)])
async def firebase_oauth_status():
    """
    📡 探测本地 firebase 会话登录状态与 Token
    """
    import os
    import json
    config_path = os.path.expanduser("~/.config/configstore/firebase-tools.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            tokens = data.get("tokens", {})
            # firebase-tools 存储的主 Token 通常是 refresh_token
            token = tokens.get("refresh_token") or tokens.get("active")
            user_info = data.get("user", {})
            if token:
                return {
                    "logged_in": True,
                    "username": user_info.get("email") or "已授权 Firebase 账户",
                    "token": token
                }
        except Exception:
            pass
    return {"logged_in": False, "message": "未检测到本地有效的 Firebase 登录会话，请先点击登录授权"}

@router.get("/api/plugins/aws/credentials-status", dependencies=[Depends(verify_token)])
async def aws_credentials_status():
    """
    📡 探测本地 AWS 凭据配置 (~/.aws/credentials 与 config)
    """
    import os
    import configparser
    creds_path = os.path.expanduser("~/.aws/credentials")
    config_path = os.path.expanduser("~/.aws/config")
    
    result = {
        "logged_in": False,
        "access_key": "",
        "secret_key": "",
        "region": ""
    }
    
    if not os.path.exists(creds_path):
        return result
        
    try:
        parser = configparser.ConfigParser()
        parser.read(creds_path, encoding='utf-8')
        section = "default"
        if not parser.has_section(section) and parser.sections():
            section = parser.sections()[0]
            
        if parser.has_section(section):
            result["access_key"] = parser.get(section, "aws_access_key_id", fallback="") or parser.get(section, "access_key", fallback="")
            result["secret_key"] = parser.get(section, "aws_secret_access_key", fallback="") or parser.get(section, "secret_key", fallback="")
            if result["access_key"] and result["secret_key"]:
                result["logged_in"] = True
                
        if os.path.exists(config_path):
            cfg_parser = configparser.ConfigParser()
            cfg_parser.read(config_path, encoding='utf-8')
            cfg_section = "default"
            if not cfg_parser.has_section(cfg_section) and cfg_parser.sections():
                cfg_section = cfg_parser.sections()[0]
            if cfg_parser.has_section(cfg_section):
                result["region"] = cfg_parser.get(cfg_section, "region", fallback="")
    except Exception:
        pass
        
    return result

@router.get("/api/plugins/sftp/ssh-status", dependencies=[Depends(verify_token)])
async def sftp_ssh_status():
    """
    📡 探测本地 ~/.ssh 目录下的常用 SSH 私钥文件物理路径
    """
    import os
    ssh_dir = os.path.expanduser("~/.ssh")
    possible_keys = ["id_ed25519", "id_rsa", "id_ecdsa"]
    
    for key_name in possible_keys:
        key_path = os.path.join(ssh_dir, key_name)
        if os.path.exists(key_path):
            return {
                "success": True,
                "private_key_path": key_path,
                "key_name": key_name
            }
            
    return {
        "success": False,
        "message": "在 ~/.ssh/ 目录下未感应到 id_ed25519 或 id_rsa 等常用 SSH 私钥文件"
    }

@router.get("/api/plugins/gitee/git-status", dependencies=[Depends(verify_token)])
async def gitee_git_status():
    """
    📡 调用本地 git-credential 助手探测 Gitee 凭证
    """
    import subprocess
    try:
        proc = subprocess.Popen(
            ["git", "credential", "fill"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, _ = proc.communicate(input="protocol=https\nhost=gitee.com\n\n", timeout=4)
        
        username = ""
        password = ""
        for line in stdout.splitlines():
            if line.startswith("username="):
                username = line.split("=", 1)[1]
            elif line.startswith("password="):
                password = line.split("=", 1)[1]
                
        if username and password:
            return {
                "success": True,
                "username": username,
                "password": password
            }
    except Exception:
        pass
        
    return {
        "success": False,
        "message": "未能通过 git-credential 助手提取到 Gitee 凭据"
    }

@router.get("/api/plugins/docker/auth-status", dependencies=[Depends(verify_token)])
async def docker_auth_status():
    """
    📡 探测并解密本地 Docker 登录凭据 (~/.docker/config.json)
    """
    import os
    import json
    import base64
    config_path = os.path.expanduser("~/.docker/config.json")
    
    if not os.path.exists(config_path):
        return {"success": False, "message": "未检测到本地 ~/.docker/config.json 文件"}
        
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        auths = data.get("auths", {})
        targets = ["https://index.docker.io/v1/", "registry.hub.docker.com", "index.docker.io"]
        
        auth_str = ""
        for t in targets:
            if t in auths and auths[t].get("auth"):
                auth_str = auths[t]["auth"]
                break
        if not auth_str and auths:
            for k, v in auths.items():
                if v.get("auth"):
                    auth_str = v["auth"]
                    break
                    
        if auth_str:
            decoded = base64.b64decode(auth_str).decode("utf-8")
            if ":" in decoded:
                user, pwd = decoded.split(":", 1)
                return {
                    "success": True,
                    "username": user,
                    "password": pwd
                }
    except Exception:
        pass
        
    return {"success": False, "message": "未能在 ~/.docker/config.json 中找到有效的已登录认证凭据"}


@router.post("/api/system/sensing/git", dependencies=[Depends(verify_token)])
async def sensing_git_credentials():
    """
    🔑 零配置环境感应：拉取本地系统的 Git user.name 与 user.email
    """
    import subprocess
    name = ""
    email = ""
    try:
        res_name = subprocess.run(
            ["git", "config", "--global", "user.name"],
            capture_output=True,
            text=True,
            timeout=3
        )
        if res_name.returncode == 0:
            name = res_name.stdout.strip()

        res_email = subprocess.run(
            ["git", "config", "--global", "user.email"],
            capture_output=True,
            text=True,
            timeout=3
        )
        if res_email.returncode == 0:
            email = res_email.stdout.strip()

        return {
            "success": True,
            "name": name,
            "email": email,
            "message": f"已自动感知本地 Git 用户: {name or '未设置'} <{email or '未设置'}>"
        }
    except Exception as e:
        return {"success": False, "message": f"拉取 Git 凭据异常: {e}"}

