# -*- coding: utf-8 -*-
"""
📡 Dispatch Hub API Shard - Platform OAuth Routes (CLI 托管平台免密授权与探针分片)
职责：承载 Cloudflare Pages, Netlify, Vercel, Firebase CLI 的一键授权登录唤醒与本地会话探针。
"""

import os
import re
import json
import subprocess
from fastapi import APIRouter, Depends
from ..system import verify_token

router = APIRouter()

@router.post("/api/plugins/cloudflare/oauth-login", dependencies=[Depends(verify_token)])
async def cloudflare_oauth_login():
    """
    🔑 本地免密一键授权：后台异步拉起 wrangler login 浏览器窗口
    """
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

@router.post("/api/plugins/firebase/oauth-login", dependencies=[Depends(verify_token)])
async def firebase_oauth_login():
    """
    🔑 本地免密一键授权：后台异步拉起 firebase login 验证
    """
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
