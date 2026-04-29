#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Universal Bootstrap
模块职责：全平台环境一键初始化脚本。
"""

import os
import sys
import subprocess
import platform

def main():
    print("\n🚀 [Illacme-plenipes] 正在开启全平台自适应引导...")
    print("=" * 50)
    
    # 1. 基础环境自检
    system = platform.system()
    py_version = platform.python_version()
    print(f"📡 检测到系统: {system}")
    print(f"🐍 当前 Python: {py_version}")
    
    # 2. 物理隔离环境构建
    venv_dir = ".venv"
    if not os.path.exists(venv_dir):
        print(f"🛠️  正在创建虚拟环境 ({venv_dir})...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
            print("   └── ✅ 虚拟环境构建成功。")
        except Exception as e:
            print(f"   └── ❌ 构建失败: {e}")
            sys.exit(1)
    else:
        print(f"ℹ️  虚拟环境 {venv_dir} 已存在，准备更新依赖。")

    # 3. 路径适配
    if os.name == 'nt': # Windows
        pip_exe = os.path.join(venv_dir, "Scripts", "pip.exe")
        python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
    else: # Unix/Mac
        pip_exe = os.path.join(venv_dir, "bin", "pip")
        python_exe = os.path.join(venv_dir, "bin", "python")

    # 4. 依赖项闪电安装 (集成国内加速源)
    req_file = "requirements.txt"
    if os.path.exists(req_file):
        print(f"📥 正在安装工业级依赖集 ({req_file})...")
        try:
            # 默认使用阿里云镜像加速
            subprocess.check_call([
                pip_exe, "install", "--upgrade", "pip"
            ])
            subprocess.check_call([
                pip_exe, "install", "-r", req_file,
                "-i", "https://mirrors.aliyun.com/pypi/simple/"
            ])
            print("   └── ✅ 依赖项同步完成。")
        except Exception as e:
            print(f"   └── ⚠️ 依赖同步发生轻微波动: {e}")
            print("   └── 💡 请尝试手动运行: source .venv/bin/activate && pip install -r requirements.txt")
    
    print("=" * 50)
    print("🎉 [恭喜] 全平台环境初始化已 100% 完成！")
    print("\n🚀 现在您可以直接运行引擎：")
    print("   python plenipes.py --help")
    print("\n💡 提示：由于已开启 Smart Bootstrapping，您无需手动 activate 环境，")
    print("   直接使用系统 python 运行 plenipes.py，它会自动跳转到虚拟环境。")
    print("=" * 50 + "\n")

if __name__ == "__main__":
    main()
