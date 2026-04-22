#!/usr/bin/env python3
"""
🛡️ Illacme-plenipes 治理自审引擎 (Governance Self-Audit Engine)
================================================================
[AEL-Iter-006] 本脚本是 AI 智能体的"自省机制"。

运行时机：每轮迭代结束后、每次提交前，智能体必须执行本脚本。
自进化权：智能体在发现新的反模式时，必须主动向本脚本追加新的检查项。

用法：python3 tests/governance_audit.py
"""
import subprocess
import os
import sys
import json
import re

# ──────────────────────────────────────────────
# 🎨 输出格式化
# ──────────────────────────────────────────────
class AuditResult:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []

    def ok(self, name, detail=""):
        self.passed.append((name, detail))
        print(f"  ✅ {name}" + (f" — {detail}" if detail else ""))

    def fail(self, name, detail=""):
        self.failed.append((name, detail))
        print(f"  ❌ {name}" + (f" — {detail}" if detail else ""))

    def warn(self, name, detail=""):
        self.warnings.append((name, detail))
        print(f"  ⚠️  {name}" + (f" — {detail}" if detail else ""))

    def summary(self):
        total = len(self.passed) + len(self.failed) + len(self.warnings)
        print(f"\n{'='*60}")
        print(f"📊 自审结果: {len(self.passed)}/{total} 通过 | "
              f"{len(self.failed)} 失败 | {len(self.warnings)} 警告")
        if self.failed:
            print(f"\n🚨 以下问题必须在提交前修复：")
            for name, detail in self.failed:
                print(f"   → {name}: {detail}")
        if self.warnings:
            print(f"\n⚠️  以下问题建议尽快处理：")
            for name, detail in self.warnings:
                print(f"   → {name}: {detail}")
        print(f"{'='*60}")
        return len(self.failed) == 0


# ──────────────────────────────────────────────
# 🔍 审计检查项（智能体可自主追加新检查）
# ──────────────────────────────────────────────

def check_empty_history_dirs(audit):
    """[AEL-Iter-006] 检查 .plenipes/history/ 是否存在空目录"""
    history_path = ".plenipes/history"
    if not os.path.isdir(history_path):
        audit.fail("历史归档目录", f"{history_path} 不存在")
        return
    empty_dirs = []
    for entry in os.listdir(history_path):
        full = os.path.join(history_path, entry)
        if os.path.isdir(full) and not any(
            f for f in os.listdir(full) if not f.startswith('.')
        ):
            empty_dirs.append(entry)
    if empty_dirs:
        audit.fail("空历史目录", f"发现 {len(empty_dirs)} 个空目录: {', '.join(empty_dirs)}")
    else:
        audit.ok("历史归档完整性", "所有 history/ 子目录均包含归档文件")


def check_git_tracked_state_files(audit):
    """[AEL-Iter-006] 检查是否有本地状态文件被 Git 追踪"""
    forbidden_patterns = [
        ".plenipes/ledger.json",
        ".plenipes/plenipes_timeline.json",
        ".plenipes/timeline.md",
        ".plenipes/sentinel_health.json",
        ".illacme-shadow/",
    ]
    try:
        result = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True, check=True
        )
        tracked = result.stdout.strip().split("\n")
        violations = [f for f in tracked for p in forbidden_patterns if f.startswith(p)]
        if violations:
            audit.fail("Git 状态泄露", f"以下文件不应被追踪: {', '.join(violations)}")
        else:
            audit.ok("Git 卫生", "无本地状态文件泄露到版本控制")
    except subprocess.CalledProcessError:
        audit.warn("Git 检查", "无法执行 git ls-files")


def check_mandatory_files_exist(audit):
    """[AEL-Iter-006] 检查 Boot Chain 引用的必要文件是否物理存在"""
    mandatory = [
        ".plenipes/rules.md",
        ".plenipes/evolution_records.md",
        ".antigravityrules",
        "CHANGELOG.md",
    ]
    for f in mandatory:
        if os.path.isfile(f):
            audit.ok(f"文件存在: {f}")
        else:
            audit.fail(f"文件缺失: {f}", "Boot Chain 引用的文件不存在")


def check_global_ki_no_project_keywords(audit):
    """[AEL-Iter-006] 检查全局 KI 文件是否包含项目特有关键词"""
    ki_base = os.path.expanduser("~/.gemini/antigravity/knowledge")
    if not os.path.isdir(ki_base):
        audit.warn("全局 KI 检查", f"KI 目录不存在: {ki_base}")
        return
    # 项目特有词汇（新项目启动时应追加到此列表）
    project_keywords = ["illacme", "plenipes", ".plenipes"]
    violations = []
    for root, dirs, files in os.walk(ki_base):
        for fname in files:
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                for kw in project_keywords:
                    if kw.lower() in content:
                        violations.append(f"{fname} 包含 '{kw}'")
                        break
            except Exception:
                pass
    if violations:
        audit.warn("全局 KI 项目污染", f"全局文件含项目关键词: {'; '.join(violations)}")
    else:
        audit.ok("全局 KI 纯净度", "全局文件不含项目特有关键词")


def check_gitignore_coverage(audit):
    """[AEL-Iter-006] 检查 .gitignore 是否覆盖了已知的状态文件模式"""
    if not os.path.isfile(".gitignore"):
        audit.fail(".gitignore 缺失", "项目根目录不存在 .gitignore")
        return
    with open(".gitignore", "r", encoding="utf-8") as f:
        content = f.read()
    required_patterns = [
        ".plenipes/ledger.json",
        ".plenipes/sentinel_health.json",
        ".illacme-shadow/",
    ]
    missing = [p for p in required_patterns if p not in content]
    if missing:
        audit.fail(".gitignore 覆盖缺口", f"缺少屏蔽规则: {', '.join(missing)}")
    else:
        audit.ok(".gitignore 覆盖度", "所有已知状态文件均已被屏蔽")


def check_evolution_records_freshness(audit):
    """[AEL-Iter-006] 检查项目进化记录是否包含近期条目"""
    evo_file = ".plenipes/evolution_records.md"
    if not os.path.isfile(evo_file):
        audit.fail("项目进化记录", f"{evo_file} 不存在")
        return
    with open(evo_file, "r", encoding="utf-8") as f:
        content = f.read()
    # 检查是否有日期标题
    dates = re.findall(r"## 📅 (\d{4}-\d{2}-\d{2})", content)
    if dates:
        latest = max(dates)
        audit.ok("项目进化记录", f"最近更新日期: {latest}")
    else:
        audit.warn("项目进化记录", "未找到任何带日期的进化条目")


def check_boot_chain_integrity(audit):
    """[AEL-Iter-006] 检查 .antigravityrules 是否包含强制读取指令"""
    rules_file = ".antigravityrules"
    if not os.path.isfile(rules_file):
        audit.warn("Boot Chain", ".antigravityrules 不存在")
        return
    with open(rules_file, "r", encoding="utf-8") as f:
        content = f.read()
    checks = {
        "view_file": "强制读取指令 (view_file)",
        "rules.md": "rules.md 引用",
        "evolution_records": "evolution_records 引用",
    }
    for keyword, label in checks.items():
        if keyword in content:
            audit.ok(f"Boot Chain: {label}")
        else:
            audit.fail(f"Boot Chain: {label}", f".antigravityrules 缺少 '{keyword}' 关键引用")


def check_no_placeholder_patterns(audit):
    """[全局#1] 零占位符协议：检查核心代码中是否残留占位符标记"""
    placeholder_patterns = [
        r"#\s*\.\.\.\s*(existing|skip|rest|remaining)",
        r"#\s*\.\.\.\s*省略",
        r"//\s*\.\.\.\s*(existing|skip)",
    ]
    violations = []
    for root, dirs, files in os.walk("core"):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fname in files:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        for pat in placeholder_patterns:
                            if re.search(pat, line, re.IGNORECASE):
                                violations.append(f"{fpath}:{i}")
            except Exception:
                pass
    if violations:
        audit.fail("零占位符协议", f"发现 {len(violations)} 处占位符: {', '.join(violations[:5])}")
    else:
        audit.ok("零占位符协议", "核心代码无占位符标记残留")


def check_docstring_coverage(audit):
    """[全局#2] 工业级注释主权：检查核心 Python 文件是否包含模块级文档"""
    missing = []
    for root, dirs, files in os.walk("core"):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for fname in files:
            if not fname.endswith(".py") or fname == "__init__.py":
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read(500)  # 只需读头部
                if '"""' not in content and "'''" not in content:
                    missing.append(fpath)
            except Exception:
                pass
    if missing:
        audit.warn("工业级注释主权", f"{len(missing)} 个核心文件缺少模块文档: {', '.join(missing[:5])}")
    else:
        audit.ok("工业级注释主权", "所有核心 Python 文件均包含模块级文档")


def check_simulation_hook_exists(audit):
    """[项目#6] 防爆钩子治理：检查 autonomous_simulation.py 中防爆钩子函数是否存在"""
    sim_file = "tests/autonomous_simulation.py"
    if not os.path.isfile(sim_file):
        audit.fail("防爆钩子", f"{sim_file} 不存在")
        return
    with open(sim_file, "r", encoding="utf-8") as f:
        content = f.read()
    required_hooks = ["verify_docs_sync_hook"]
    missing = [h for h in required_hooks if h not in content]
    if missing:
        audit.fail("防爆钩子", f"缺少关键钩子函数: {', '.join(missing)}")
    else:
        audit.ok("防爆钩子治理", "verify_docs_sync_hook 物理存在且完好")

def check_audit_self_coverage(audit):
    """[AEL-Iter-006] 元审计：检查本脚本的检查项是否覆盖了全部进化记录中的教训"""
    total_evo_count = 0

    # ── 1. 统计项目进化记录条目 ──
    evo_project = ".plenipes/evolution_records.md"
    if os.path.isfile(evo_project):
        with open(evo_project, "r", encoding="utf-8") as f:
            entries = re.findall(r"^### \d+\.", f.read(), re.MULTILINE)
        total_evo_count += len(entries)

    # ── 2. 统计全局进化记录条目 ──
    evo_global = os.path.expanduser(
        "~/.gemini/antigravity/knowledge/global_integrity/artifacts/evolution_records.md"
    )
    if os.path.isfile(evo_global):
        with open(evo_global, "r", encoding="utf-8") as f:
            entries = re.findall(r"^### \d+\.", f.read(), re.MULTILINE)
        total_evo_count += len(entries)

    # ── 3. 统计本脚本中的 check_ 函数数量 ──
    script_path = os.path.abspath(__file__)
    with open(script_path, "r", encoding="utf-8") as f:
        script_content = f.read()
    check_funcs = re.findall(r"^def (check_\w+)\(audit\):", script_content, re.MULTILINE)
    check_count = len(check_funcs)

    if check_count >= total_evo_count:
        audit.ok("元审计覆盖度",
                 f"审计检查项 ({check_count}) ≥ 进化记录总条目 ({total_evo_count}，项目+全局)")
    else:
        gap = total_evo_count - check_count
        audit.warn("元审计覆盖度",
                   f"进化记录共 {total_evo_count} 条教训（项目+全局），"
                   f"但审计仅有 {check_count} 项检查，差 {gap} 项。"
                   f"请为新教训追加对应的 check_ 函数。")


# ──────────────────────────────────────────────
# 🚀 主执行入口
# ──────────────────────────────────────────────

def main():
    print("🛡️  Illacme-plenipes 治理自审引擎 v1.1")
    print("=" * 60)

    # 切换到项目根目录（如果从别的位置调用）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)

    audit = AuditResult()

    print("\n📂  [1/11] 历史归档完整性...")
    check_empty_history_dirs(audit)

    print("\n🔒  [2/11] Git 状态泄露检测...")
    check_git_tracked_state_files(audit)

    print("\n📄  [3/11] Boot Chain 必要文件存在性...")
    check_mandatory_files_exist(audit)

    print("\n🌐  [4/11] 全局 KI 项目污染检测...")
    check_global_ki_no_project_keywords(audit)

    print("\n🛡️  [5/11] .gitignore 规则覆盖度...")
    check_gitignore_coverage(audit)

    print("\n🧬  [6/11] 项目进化记录新鲜度...")
    check_evolution_records_freshness(audit)

    print("\n🔗  [7/11] Boot Chain 完整性...")
    check_boot_chain_integrity(audit)

    print("\n🚫  [8/11] 零占位符协议...")
    check_no_placeholder_patterns(audit)

    print("\n📝  [9/11] 工业级注释主权...")
    check_docstring_coverage(audit)

    print("\n⚡  [10/11] 防爆钩子治理...")
    check_simulation_hook_exists(audit)

    print("\n🪞  [11/11] 元审计：自身覆盖度...")
    check_audit_self_coverage(audit)

    success = audit.summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
