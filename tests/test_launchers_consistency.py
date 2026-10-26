#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Launcher Ecosystem Consistency Tests
模块职责：断言多平台启动脚本（start.command, start.sh, start.bat, start.ps1, publish.sh）
在端口、Python环境探测、版本门禁、入口调用与安全标志上的一致性。
🛡️ [SOP-01 规范]：单文件行数严格 ≤ 300 行。
"""

import os
import re
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

LAUNCHER_FILES = {
    "command": os.path.join(ROOT_DIR, "start.command"),
    "sh": os.path.join(ROOT_DIR, "start.sh"),
    "bat": os.path.join(ROOT_DIR, "start.bat"),
    "ps1": os.path.join(ROOT_DIR, "start.ps1"),
}

PUBLISH_FILE = os.path.join(ROOT_DIR, "publish.sh")


def test_all_launchers_exist():
    """断言四大启动器与发布脚本物理存在于根目录"""
    for name, path in LAUNCHER_FILES.items():
        assert os.path.isfile(path), f"启动器脚本缺失: {name} -> {path}"
    assert os.path.isfile(PUBLISH_FILE), f"发布脚本缺失: {PUBLISH_FILE}"


def test_launchers_port_consistency():
    """断言所有启动器指向标准 API 端口 43212 (遵循 Rule #6)"""
    expected_port_str = "43212"
    for name, path in LAUNCHER_FILES.items():
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert expected_port_str in content, f"{name} 启动器中未包含标准端口 43212"
        # 绝不能误绑定到 43210 (单例锁) 或 8000
        assert "43210" not in content, f"{name} 启动器误写了单例锁端口 43210"


def test_launchers_python_version_guard():
    """断言所有启动器均包含 Python 3.10+ 版本检查门禁"""
    pattern = re.compile(r"sys\.version_info\s*>=\s*\(\s*3\s*,\s*10\s*\)")
    for name, path in LAUNCHER_FILES.items():
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert pattern.search(content), f"{name} 启动器未包含 sys.version_info >= (3, 10) 检查"


def test_launchers_virtualenv_priority():
    """断言所有启动器均优先检查 .venv 再检查 venv"""
    for name, path in LAUNCHER_FILES.items():
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        idx_dot_venv = content.find(".venv")
        idx_venv = content.find("venv")
        assert idx_dot_venv != -1, f"{name} 启动器未配置 .venv 探测"
        assert idx_venv != -1, f"{name} 启动器未配置 venv 探测"
        assert idx_dot_venv <= idx_venv, f"{name} 启动器未将 .venv 放在最高优先级"


def test_launchers_entrypoint_consistency():
    """断言所有启动脚本均调用统一主入口 plenipes.py，严禁遗留 bridge.py"""
    all_scripts = list(LAUNCHER_FILES.values()) + [PUBLISH_FILE]
    for script_path in all_scripts:
        with open(script_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "plenipes.py" in content, f"{os.path.basename(script_path)} 未调用 plenipes.py"
        assert "bridge.py" not in content, f"{os.path.basename(script_path)} 遗留了废弃的 bridge.py"


def test_launchers_pip_security_flag():
    """断言启动器中执行 pip install 时包含 --disable-pip-version-check (遵循 Rule #4)"""
    for name, path in LAUNCHER_FILES.items():
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if "pip install" in content:
            assert "--disable-pip-version-check" in content, (
                f"{name} 中的 pip install 未附加 --disable-pip-version-check"
            )


def test_unix_scripts_executable_permission():
    """断言 Unix/macOS 脚本具有可执行权限 (chmod +x)"""
    unix_scripts = [
        LAUNCHER_FILES["command"],
        LAUNCHER_FILES["sh"],
        PUBLISH_FILE,
    ]
    for script in unix_scripts:
        is_executable = os.access(script, os.X_OK)
        assert is_executable, f"脚本未设置执行权限 (X_OK): {os.path.basename(script)}"
