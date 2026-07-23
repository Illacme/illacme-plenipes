# -*- coding: utf-8 -*-
"""
📡 Dispatch Hub API Shard - Sensing Routes (环境与系统凭据静默感应分片)
职责：承载 GitHub SSH, AWS, SFTP, Gitee, Docker 凭据及 Git 零配置感知探针。
"""

import os
import re
import json
import base64
import configparser
import subprocess
from fastapi import APIRouter, Depends
from ..system import verify_token

router = APIRouter()

@router.get("/api/plugins/github/ssh-status", dependencies=[Depends(verify_token)])
async def github_ssh_status():
    """
    📡 探测本地机器与 GitHub 的 SSH 密钥连通状态 (用于免 Token 部署引导)
    """
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
                "message": "探测到本地 SSH 密钥与 GitHub 连通极佳，您可以使用 SSH 地址免密克隆与发布！"
            }
    except Exception:
        pass
    return {"ssh_ok": False, "message": "未能连接到 GitHub SSH 服务，建议填入访问令牌 (Token)"}

@router.get("/api/plugins/aws/credentials-status", dependencies=[Depends(verify_token)])
async def aws_credentials_status():
    """
    📡 探测本地 AWS 凭据配置 (~/.aws/credentials 与 config)
    """
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
        return {"success": False, "message": f"拉起 Git 凭据异常: {e}"}
