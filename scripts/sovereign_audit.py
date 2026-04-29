#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Sovereign Audit Integration (主权审计集成)
职责：执行符合 V24.6 工业架构的“全链路”安全与主权审计。
"""
import sys
import os
import subprocess

# 确保能导入 core 包
sys.path.insert(0, os.getcwd())

def run_step(name, command_list):
    print(f"🚀 [审计阶段] {name}...")
    try:
        result = subprocess.run(command_list, check=True, capture_output=True, text=True)
        print(f"  └── ✅ {name} 通过")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  └── ❌ {name} 失败！")
        if e.stdout: print(f"      Stdout:\n{e.stdout}")
        if e.stderr: print(f"      Stderr:\n{e.stderr}")
        return False
    except FileNotFoundError as e:
        print(f"  └── ⚠️  跳过 {name}: 未找到工具 ({e})")
        return True

def main():
    success = True
    
    # 1. 核心合规性审计 (GitHub 出海红线)
    print("🚀 [审计阶段] GitHub 安全合规性审计...")
    try:
        from core.governance.contract_guard import ContractGuard
        compliance_violations = ContractGuard.verify_repository_compliance()
        if compliance_violations:
            for v in compliance_violations: print(f"  └── {v}")
            if any("❌" in v for v in compliance_violations):
                success = False
        else:
            print("  └── ✅ GitHub 安全合规性审计通过")
    except Exception as e:
        print(f"  └── ❌ 合规审计执行异常: {e}")
        success = False

    # 2. 物理主权红线审计 (300行约束)
    print("🚀 [审计阶段] 物理主权红线审计 (300行限制)...")
    try:
        limit_violations = []
        # 允许豁免的文件列表 (V24.6 工业级组件)
        EXEMPT_FILES = [
            "core/ui/handlers/status_handlers.py",
            "core/config/config.py",
            "core/runtime/engine_factory.py",
            "core/editorial/asset_pipeline.py"
        ]
        
        for root, dirs, files in os.walk('core'):
            for file in files:
                if file.endswith('.py'):
                    p = os.path.join(root, file).replace('\\', '/')
                    with open(p, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                    if lines > 300 and p not in EXEMPT_FILES:
                        limit_violations.append(f"❌ [主权越线] {p} 超过 300 行 (当前: {lines})")
                    elif lines > 300:
                        print(f"  └── ⚠️ [豁免组件] {p} (当前: {lines})")
        
        if limit_violations:
            for v in limit_violations: print(f"  └── {v}")
            success = False
        else:
            print("  └── ✅ 物理主权红线审计通过")
    except Exception as e:
        print(f"  └── ❌ 红线审计异常: {e}")
        success = False

    # 2.5 Banner UI 主权锁定审计
    print("🚀 [审计阶段] Banner UI 主权锁定审计...")
    try:
        # 检查 status_handlers.py 是否被修改
        staged_files = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).splitlines()
        if "core/ui/handlers/status_handlers.py" in staged_files:
            if os.environ.get("ALLOW_BANNER_EDIT") == "1":
                print("  └── ⚠️ [UI主权特权] 检测到 ALLOW_BANNER_EDIT=1 环境变量，允许授权修改 Banner 视觉资产。")
            else:
                print("  └── ❌ [UI主权拦截] core/ui/handlers/status_handlers.py 已被标记为 Read-Only Visual Asset。")
                print("         为保护 V48.2 极致对称物理排版，严禁常规修改！")
                print("         如确需授权修改，请在提交时附加变量，例如： ALLOW_BANNER_EDIT=1 git commit -m '...'")
                success = False
        else:
            print("  └── ✅ UI 主权锁定审计通过 (Banner 未被非法篡改)")
    except Exception as e:
        # 如果未在 git 仓库中或命令失败，静默放行或打印警告
        print(f"  └── ⚠️ UI主权审计跳过 (Git 检测异常: {e})")

    # 3. 核心规范审计 (Ruff Linting)
    # 豁免 status_handlers.py 以保护 V48.2 Banner 亚像素级物理空格不被清理
    if not run_step("核心引擎规范审计", ["ruff", "check", "core/", "--extend-exclude", "core/ui/handlers/status_handlers.py"]):
        success = False

    # 4. 回归测试 (Smoke Tests)
    # V48.2 升级：覆盖全新的 Ingress 与 Web Wizard 测试套件
    if not run_step("自动化冒烟测试", ["pytest", "tests/", "--maxfail=1"]):
        success = False

    if not success:
        print("\n🛑 [主权审计拦截] 提交的代码未通过 V24.6 工业治理审计，请修复后再提交！")
        sys.exit(1)
    else:
        print("\n✨ [主权审计完成] 恭喜！代码符合 V24.6 工业主权规范，准予提交。")
        sys.exit(0)

if __name__ == "__main__":
    main()
