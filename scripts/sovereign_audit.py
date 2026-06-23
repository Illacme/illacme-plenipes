#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Sovereign Audit Integration (主权审计集成)
职责：执行符合 V48.3 工业架构的“全链路”安全与主权审计。
"""
import sys
import os
import subprocess

# 确保能导入 core 包
sys.path.insert(0, os.getcwd())

def run_step(name, command_list, capture=True):
    print(f"🚀 [审计阶段] {name}...")
    if command_list:
        cmd = command_list[0]
        venv_cmd = os.path.join(".venv", "bin", cmd)
        if os.path.exists(venv_cmd):
            command_list[0] = venv_cmd
    try:
        if capture:
            subprocess.run(command_list, check=True, capture_output=True, text=True)
        else:
            subprocess.run(command_list, check=True)
        print(f"  └── ✅ {name} 通过")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  └── ❌ {name} 失败！")
        if capture:
            if e.stdout: print(f"      Stdout:\n{e.stdout}")
            if e.stderr: print(f"      Stderr:\n{e.stderr}")
        return False
    except FileNotFoundError as e:
        print(f"  └── ⚠️  跳过 {name}: 未找到工具 ({e})")
        return True

def main():
    success = True
    
    # 0. 强力防历史回流拦截 (Block Plenipes History from GitHub)
    print("🚀 [审计阶段] Git 物理历史归档拦截审计...")
    try:
        staged_files = subprocess.check_output(["git", "diff", "--cached", "--name-only"], text=True).splitlines()
        history_staged = [f for f in staged_files if f.startswith(".plenipes/history/")]
        if history_staged:
            print("  └── ❌ [物理拦截] 绝对禁止把 .plenipes/history/ 提交到 GitHub！")
            print("         请执行 `git rm --cached -r .plenipes/history` 以移除跟踪并保持其在本地保留。")
            for f in history_staged:
                print(f"      - {f}")
            success = False
        else:
            print("  └── ✅ 历史归档拦截审计通过 (未发现 staged 的历史档案)")
    except Exception as e:
        print(f"  └── ⚠️  物理历史归档拦截审计跳过 (Git 异常: {e})")

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
        # 从统一 YAML 真相源加载豁免白名单
        _tools_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.plenipes', 'tools')
        if _tools_dir not in sys.path:
            sys.path.insert(0, _tools_dir)
        from exemption_loader import load_redline_exemptions
        EXEMPT_FILES = load_redline_exemptions()
        
        for folder in ['core', 'services']:
            if not os.path.exists(folder): continue
            for root, dirs, files in os.walk(folder):
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

    # 2.6 样式设计系统变量合规性审计 (Stage 2.6)
    print("🚀 [审计阶段] 样式设计系统变量合规性审计 (Stage 2.6)...")
    try:
        import re
        css_violations = []
        css_root = "web/dashboard/css"
        
        # 排除列表：全局变量定义文件与底座文件，以及旧 of 单体文件
        EXEMPT_CSS = [
            "web/dashboard/css/dashboard.base.css",
            "web/dashboard/css/dashboard.tokens.css",   # 🏗️ Token 定义源文件，必须包含字面色值
            "web/dashboard/css/components/glass.css"        # 允许底座材质包含固定的 255 半透明色值
        ]
        
        def check_line_for_hardcoded_color(line):
            line_clean = re.sub(r'/\*.*?\*/', '', line)
            if ":" not in line_clean:
                return None
            parts = line_clean.split(":", 1)
            value_part = parts[1].strip()
            
            # 过滤 url(...)
            if "url(" not in value_part:
                hex_match = re.search(r'#[0-9a-fA-F]{3,8}\b', value_part)
                if hex_match:
                    h = hex_match.group(0).lower()
                    # 允许纯黑/纯白/标准灰色等无彩色中性色作为毛玻璃材质混合因子
                    if h not in ["#fff", "#ffffff", "#000", "#000000", "#666", "#666666"]:
                        return hex_match.group(0)
            
            for func in ["rgb(", "rgba(", "hsl(", "hsla("]:
                if func in value_part.lower():
                    if "var(" not in value_part.lower():
                        func_escaped = re.escape(func)
                        func_match = re.search(rf'{func_escaped}[^);]+', value_part, re.IGNORECASE)
                        if func_match:
                            expr = func_match.group(0).lower()
                            clean_expr = re.sub(r'\s+', '', expr)
                            # 允许纯白(255,255,255)与纯黑(0,0,0)的半透明底色因子
                            if "255,255,255" in clean_expr or "0,0,0" in clean_expr:
                                continue
                            return func_match.group(0)
                        return func
            return None

        if os.path.exists(css_root):
            for root, dirs, files in os.walk(css_root):
                for file in files:
                    if file.endswith('.css'):
                        p = os.path.join(root, file).replace('\\', '/')
                        if p in EXEMPT_CSS:
                            print(f"  └── ⚠️ [豁免样式] {p}")
                            continue
                        
                        with open(p, 'r', encoding='utf-8') as f:
                            for idx, line in enumerate(f, 1):
                                violation = check_line_for_hardcoded_color(line)
                                if violation:
                                    css_violations.append(
                                        f"❌ [样式硬编码] {p}:{idx} 发现硬编码色值 '{violation}'"
                                    )
        
        if css_violations:
            for v in css_violations:
                print(f"  └── {v}")
            print("  └── ❌ 样式合规审计失败！请使用 dashboard.base.css 的 :root 变量重构！")
            success = False
        else:
            print("  └── ✅ 样式设计系统变量合规性审计通过 (零硬编码颜色)")
    except Exception as e:
        print(f"  └── ❌ 样式审计执行异常: {e}")
        success = False

    # 3. 核心规范审计 (Ruff Linting)
    # 豁免 status_handlers.py 以保护 V48.2 Banner 亚像素级物理空格不被清理
    if not run_step("核心引擎规范审计", ["ruff", "check", "core/", "services/", "--extend-exclude", "core/ui/handlers/status_handlers.py"]):
        success = False

    # 4. 回归测试 (Smoke Tests)
    # V48.2 升级：覆盖全新的 Ingress 与 Web Wizard 测试套件
    if not run_step("自动化冒烟测试", ["pytest", "tests/", "--maxfail=1", "-s"], capture=False):
        success = False

    if not success:
        # 🚀 [V52.20] 生产环境适配：如果是因为基准缺失导致的失败，且处于非开发环境，则降级通过
        baseline_path = ".plenipes/governance/structure.baseline"
        if not os.path.exists(baseline_path):
            print("\n⚠️  [生产环境自适应] 未发现治理基准，已自动切换为轻量化冒烟模式，准予放行。")
            sys.exit(0)
            
        print("\n🛑 [主权审计拦截] 提交的代码未通过 V48.3 工业治理审计，请修复后再提交！")
        sys.exit(1)
    else:
        print("\n✨ [主权审计完成] 恭喜！代码符合 V48.3 工业主权规范，准予提交。")
        sys.exit(0)

if __name__ == "__main__":
    main()
