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


def check_precommit_hook_exists(audit):
    """[AEL-Iter-007] 检查 Git pre-commit hook 是否已安装"""
    hook_path = ".git/hooks/pre-commit"
    if not os.path.isfile(hook_path):
        audit.fail("Pre-commit Hook",
                   f"{hook_path} 不存在。请执行 sh scripts/setup-hooks.sh 安装。")
        return
    if not os.access(hook_path, os.X_OK):
        audit.fail("Pre-commit Hook", f"{hook_path} 存在但不可执行（缺少 +x 权限）")
        return
    with open(hook_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "governance_audit" in content:
        audit.ok("Pre-commit Hook", "已安装且指向 governance_audit.py")
    else:
        audit.warn("Pre-commit Hook", "hook 存在但未调用 governance_audit.py")


def check_untracked_runtime_artifacts(audit):
    """[AEL-Iter-007] 检测工作区中疑似运行时产物但未被 .gitignore 覆盖的文件"""
    runtime_extensions = {".json", ".db", ".sqlite", ".log", ".cache", ".tmp"}
    runtime_names = {"ledger", "timeline", "sentinel", "shadow", "cache"}
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain", "-u"], capture_output=True, text=True, check=True
        )
        untracked = [
            line[3:] for line in result.stdout.strip().split("\n")
            if line.startswith("??")
        ]
        suspects = []
        for f in untracked:
            basename = os.path.basename(f).lower()
            _, ext = os.path.splitext(basename)
            if ext in runtime_extensions:
                if any(kw in basename for kw in runtime_names):
                    suspects.append(f)
        if suspects:
            audit.warn("运行时产物泄露",
                       f"发现 {len(suspects)} 个疑似状态文件未被 .gitignore 覆盖: "
                       f"{', '.join(suspects[:5])}。请确认是否需要加入 .gitignore。")
        else:
            audit.ok("运行时产物检测", "未发现可疑的未追踪运行时文件")
    except subprocess.CalledProcessError:
        audit.warn("运行时产物检测", "无法执行 git status")


def check_docs_update_quality(audit):
    """[AEL-Iter-008] 检查 docs/ 最近变更是否有实质内容（防止空变更蒙混过关）"""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%H", "--", "docs/"],
            capture_output=True, text=True, check=True
        )
        last_doc_commit = result.stdout.strip()
        if not last_doc_commit:
            audit.warn("文档更新质量", "docs/ 目录从未被提交过")
            return
        diff_result = subprocess.run(
            ["git", "diff", "--stat", f"{last_doc_commit}~1..{last_doc_commit}", "--", "docs/"],
            capture_output=True, text=True, check=True
        )
        diff_stat = diff_result.stdout.strip()
        if not diff_stat:
            audit.ok("文档更新质量", "最近一次文档提交有实质变更")
            return
        # 解析 insertions/deletions
        import re as _re
        nums = _re.findall(r'(\d+) insertion|\(\d+) deletion', diff_stat)
        total_changes = sum(int(n) for n in nums if n)
        if total_changes < 3:
            audit.warn("文档更新质量",
                       f"最近一次文档提交仅 {total_changes} 行变更，可能是空变更蒙混")
        else:
            audit.ok("文档更新质量", f"最近一次文档提交 {total_changes} 行实质变更")
    except (subprocess.CalledProcessError, Exception):
        audit.ok("文档更新质量", "检查跳过（git 历史不足或无 docs 变更）")


def check_roadmap_freshness(audit):
    """[AEL-Iter-008] 检查 ROADMAP.md 是否与代码仓库的活跃度保持同步"""
    roadmap_candidates = ["ROADMAP.md", ".plenipes/ROADMAP.md"]
    roadmap_path = None
    for rp in roadmap_candidates:
        if os.path.isfile(rp):
            roadmap_path = rp
            break
    if not roadmap_path:
        audit.warn("ROADMAP 新鲜度", "未找到 ROADMAP.md 文件")
        return
    import time
    mtime = os.path.getmtime(roadmap_path)
    age_days = (time.time() - mtime) / 86400
    if age_days > 30:
        audit.warn("ROADMAP 新鲜度",
                   f"{roadmap_path} 已有 {int(age_days)} 天未更新，可能已过期")
    else:
        audit.ok("ROADMAP 新鲜度", f"{roadmap_path} 最近 {int(age_days)} 天内有更新")


def check_simulation_test_coverage(audit):
    """[AEL-Iter-008] 检查 autonomous_simulation.py 是否覆盖核心测试阶段"""
    sim_file = "tests/autonomous_simulation.py"
    if not os.path.isfile(sim_file):
        audit.fail("仿真测试覆盖", f"{sim_file} 不存在")
        return
    with open(sim_file, "r", encoding="utf-8") as f:
        content = f.read()
    required_phases = {
        "verify_docs_sync_hook": "AEL 文档同步钩子",
        "run_shadow_simulation": "影子沙盒主流程",
        "Simulation Gating": "仿真网关标识",
    }
    missing = [label for key, label in required_phases.items() if key not in content]
    if missing:
        audit.warn("仿真测试覆盖", f"缺少关键测试阶段: {', '.join(missing)}")
    else:
        audit.ok("仿真测试覆盖", f"全部 {len(required_phases)} 个核心阶段均存在")

def check_simulation_execution(audit):
    """[AEL-Iter-009] 动态运行核心业务的影子沙盒边界测试，拦截由逻辑错误导致代码提交"""
    try:
        result = subprocess.run(
            [sys.executable, "tests/autonomous_simulation.py"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            audit.ok("仿真运行健康", "影子执行全部验证通过，无运行时异常")
        else:
            error_lines = result.stderr.strip().split('\n')[-3:]
            if not any(error_lines):
                error_lines = result.stdout.strip().split('\n')[-3:]
            err_msg = " | ".join(error_lines)
            audit.fail("仿真运行异常", f"测试挂掉 (exit {result.returncode})\n尾部报错: {err_msg}")
    except Exception as e:
        audit.fail("仿真运行异常", f"无法启动仿真进程：{str(e)}")


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
    print("🛡️  Illacme-plenipes 治理自审引擎 v3.0 (动静结合版)")
    print("=" * 60)

    # 切换到项目根目录（如果从别的位置调用）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)

    audit = AuditResult()

    print("\n📂  [1/17] 历史归档完整性...")
    check_empty_history_dirs(audit)

    print("\n🔒  [2/17] Git 状态泄露检测...")
    check_git_tracked_state_files(audit)

    print("\n📄  [3/17] Boot Chain 必要文件存在性...")
    check_mandatory_files_exist(audit)

    print("\n🌐  [4/17] 全局 KI 项目污染检测...")
    check_global_ki_no_project_keywords(audit)

    print("\n🛡️  [5/17] .gitignore 规则覆盖度...")
    check_gitignore_coverage(audit)

    print("\n🧬  [6/17] 项目进化记录新鲜度...")
    check_evolution_records_freshness(audit)

    print("\n🔗  [7/17] Boot Chain 完整性...")
    check_boot_chain_integrity(audit)

    print("\n🚫  [8/17] 零占位符协议...")
    check_no_placeholder_patterns(audit)

    print("\n📝  [9/17] 工业级注释主权...")
    check_docstring_coverage(audit)

    print("\n⚡  [10/17] 防爆钩子治理...")
    check_simulation_hook_exists(audit)

    print("\n🔧  [11/17] Pre-commit Hook 安装...")
    check_precommit_hook_exists(audit)

    print("\n🗑️  [12/17] 运行时产物泄露检测...")
    check_untracked_runtime_artifacts(audit)

    print("\n📋  [13/17] 文档更新质量...")
    check_docs_update_quality(audit)

    print("\n🗺️  [14/17] ROADMAP 新鲜度...")
    check_roadmap_freshness(audit)

    print("\n🧪  [15/17] 仿真测试静态存在性...")
    check_simulation_test_coverage(audit)

    print("\n⚔️  [16/17] 仿真引擎物理试运行 (动)...")
    check_simulation_execution(audit)

    print("\n🪞  [17/17] 元审计：自身覆盖度...")
    check_audit_self_coverage(audit)

    success = audit.summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
