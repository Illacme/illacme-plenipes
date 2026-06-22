#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes SFTP Publisher Plugin
🚀 [V1.0]：通过 SFTP 协议将静态站点资产物理同步至远程自建 Web 服务器（如 Nginx、Apache）。
"""

import os
import io
from typing import Dict, Any, List, Optional
from core.adapters.egress.publishers.base import BasePublisher, PublisherRegistry
from core.utils.tracing import tlog


def _mkdir_recursive(sftp, remote_directory: str):
    """
    递归创建 SFTP 远程目录以匹配本地结构
    """
    path = remote_directory.replace("\\", "/")
    parts = path.split("/")
    current = ""
    for part in parts:
        if not part:
            current += "/"
            continue
        if current and not current.endswith("/"):
            current += "/"
        current += part
        try:
            sftp.stat(current)
        except IOError:
            try:
                sftp.mkdir(current)
            except Exception as e:
                # 兼容并发冲突或根目录检查
                tlog.warning(f"⚠️ 无法创建远程目录 '{current}': {e}")


def _load_private_key(key_data: str, passphrase: Optional[str] = None):
    """
    从私钥文本或私钥路径加载 SSH 私钥
    """
    import paramiko
    errors = []
    # 尝试多种算法类
    for key_cls in [paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey, paramiko.DSSKey]:
        try:
            if "-----BEGIN" in key_data:
                return key_cls.from_private_key(io.StringIO(key_data), password=passphrase)
            elif os.path.exists(key_data):
                return key_cls.from_private_key_file(key_data, password=passphrase)
        except Exception as e:
            errors.append(f"{key_cls.__name__}: {e}")
            continue
    raise ValueError(f"无法解析的私钥。校验异常: {'; '.join(errors)}")


@PublisherRegistry.register("sftp")
class SftpPublisher(BasePublisher):
    PLUGIN_ID = "sftp"
    DISPLAY_NAME = "SFTP / SSH"
    VERSION = "V1.0"
    DESCRIPTION = "通过 SFTP 安全地将静态资产同步到自建或租赁的服务器根目录中。"

    def __init__(self, config: Dict[str, Any], sys_config: Dict[str, Any] = None):
        super().__init__(config, sys_config)
        self.host = config.get("host", "").strip()
        self.port = int(config.get("port", 22) or 22)
        self.username = config.get("username", "").strip()
        self.password = config.get("password", "")
        self.private_key = config.get("private_key", "").strip()
        self.passphrase = config.get("passphrase", "") or None
        self.remote_path = config.get("remote_path", "").strip()
        self.public_url = config.get("public_url", "").rstrip("/")

    def push(self, bundle_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        validation_errors = self.validate_config()
        if validation_errors:
            return {"status": "skipped", "message": f"SFTP 配置不完整: {'; '.join(validation_errors)}"}

        if not os.path.isdir(bundle_path):
            return {"status": "error", "message": f"Bundle path 不存在: {bundle_path}"}

        try:
            import paramiko
        except ImportError:
            tlog.error("❌ [SFTP] paramiko 未安装，无法执行 SFTP 上传。请运行: pip install paramiko")
            return {"status": "error", "message": "paramiko 未安装，请运行 pip install paramiko"}

        tlog.info(f"🚀 [SFTP] 正在连接至 SSH 服务器 '{self.host}:{self.port}'...")

        ssh = None
        sftp = None
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 建立 SSH 认证通道
            connect_kwargs = {
                "hostname": self.host,
                "port": self.port,
                "username": self.username,
                "timeout": 15
            }

            if self.private_key:
                pkey = _load_private_key(self.private_key, self.passphrase)
                connect_kwargs["pkey"] = pkey
            elif self.password:
                connect_kwargs["password"] = self.password
            else:
                return {"status": "error", "message": "未配置 SFTP 登录密码或 SSH 私钥，无法认证。"}

            ssh.connect(**connect_kwargs)
            sftp = ssh.open_sftp()

            # 确保远程目标根目录存在
            _mkdir_recursive(sftp, self.remote_path)

            file_count = 0
            error_count = 0

            for root, dirs, files in os.walk(bundle_path):
                dirs[:] = [d for d in dirs if not d.startswith(".")]

                for file in files:
                    if file.startswith("."):
                        continue

                    local_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_path, bundle_path)
                    
                    # 相对路径转为 Unix SFTP 目标路径
                    sftp_rel = relative_path.replace("\\", "/")
                    remote_file_path = f"{self.remote_path}/{sftp_rel}".replace("//", "/")

                    # 在上传前确保父文件夹存在
                    remote_parent_dir = os.path.dirname(remote_file_path)
                    _mkdir_recursive(sftp, remote_parent_dir)

                    try:
                        sftp.put(local_path, remote_file_path)
                        file_count += 1
                    except Exception as upload_err:
                        tlog.warning(f"⚠️ [SFTP] 传输失败 ({sftp_rel}): {upload_err}")
                        error_count += 1

            if error_count > 0:
                tlog.warning(f"⚠️ [SFTP] 部分同步完成: {file_count} 成功，{error_count} 失败。")
                return {
                    "status": "partial",
                    "files": file_count,
                    "errors": error_count,
                    "host": self.host,
                }

            tlog.info(f"✅ [SFTP] 目录全量同步成功！共 {file_count} 个文件 → 服务器: {self.host}")
            return {
                "status": "success",
                "files": file_count,
                "host": self.host,
                "url": self.get_deploy_url(),
            }

        except Exception as e:
            tlog.error(f"❌ [SFTP] 连接或传输异常: {e}")
            return {"status": "error", "message": str(e)}

        finally:
            if sftp:
                sftp.close()
            if ssh:
                ssh.close()

    def is_healthy(self) -> bool:
        if not self.host or not self.username or not self.remote_path:
            return False
        if not self.password and not self.private_key:
            return False

        try:
            import paramiko
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            connect_kwargs = {
                "hostname": self.host,
                "port": self.port,
                "username": self.username,
                "timeout": 5
            }
            if self.private_key:
                pkey = _load_private_key(self.private_key, self.passphrase)
                connect_kwargs["pkey"] = pkey
            else:
                connect_kwargs["password"] = self.password

            ssh.connect(**connect_kwargs)
            sftp = ssh.open_sftp()
            # 简单 stat 一下 remote_path
            sftp.stat(self.remote_path)
            sftp.close()
            ssh.close()
            return True
        except Exception:
            return False

    def validate_config(self) -> List[str]:
        errors: List[str] = []
        if not self.host:
            errors.append("缺少必填配置: host")
        if not self.username:
            errors.append("缺少必填配置: username")
        if not self.remote_path:
            errors.append("缺少必填配置: remote_path")
        if not self.password and not self.private_key:
            errors.append("缺少登录认证凭证 (密码 password 与 私钥 private_key 二选一)")
        return errors

    def get_deploy_url(self) -> Optional[str]:
        if self.public_url:
            return self.public_url
        return None
