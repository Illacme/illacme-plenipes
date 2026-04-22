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

def check_history_artifacts_completeness(audit):
    """[AEL-Iter-012] 检查 .plenipes/history/ 历史迭代的三相基因完备性"""
    history_path = ".plenipes/history"
    if not os.path.isdir(history_path):
        audit.fail("历史归档目录", f"{history_path} 不存在")
        return
    
    incomplete_dirs = []
    for entry in os.listdir(history_path):
        full = os.path.join(history_path, entry)
        if os.path.isdir(full) and entry.startswith("2026-"):
            files = os.listdir(full)
            has_plan = "plan.md" in files or "implementation_plan.md" in files
            has_task = "task.md" in files
            has_walk = "walkthrough.md" in files or "acceptance.md" in files
            
            if not (has_plan and has_task and has_walk):
                incomplete_dirs.append(entry)
                
    if incomplete_dirs:
        audit.fail("历史迭代矩阵不完整", f"发现 {len(incomplete_dirs)} 个迭代目录缺少 plan/task/walkthrough 三相文件: {', '.join(incomplete_dirs[:3])}...")
    else:
        audit.ok("历史归档完整性", "所有 history/ 迭代目录均已严格沉淀三相规划基因")


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


def check_iter_id_tagging(audit):
    """[AEL-Iter-013/P1] 代码溯源打标：检查 core/ 下变更的 Python 文件是否包含 [AEL-Iter-] 标记"""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
            capture_output=True, text=True, check=True
        )
        changed_py = [
            f for f in result.stdout.strip().split("\n")
            if f.startswith("core/") and f.endswith(".py") and f.strip()
        ]
        if not changed_py:
            audit.ok("代码溯源打标", "本次提交无 core/ Python 文件变更，跳过检查")
            return

        untagged = []
        for fpath in changed_py:
            diff_result = subprocess.run(
                ["git", "diff", "--cached", "-U0", "--", fpath],
                capture_output=True, text=True, check=True
            )
            added_lines = [l for l in diff_result.stdout.split("\n") if l.startswith("+") and not l.startswith("+++")]
            has_tag = any("[AEL-Iter-" in line or "[Iter-" in line for line in added_lines)
            if not has_tag and added_lines:
                untagged.append(os.path.basename(fpath))

        if untagged:
            audit.fail("代码溯源打标",
                       f"{len(untagged)} 个 core/ 文件缺少 [AEL-Iter-ID] 溯源标记: {', '.join(untagged[:5])}")
        else:
            audit.ok("代码溯源打标", f"全部 {len(changed_py)} 个变更文件均已打标")
    except subprocess.CalledProcessError:
        audit.ok("代码溯源打标", "非 Git 暂存区上下文，跳过检查")


def check_core_architecture_fingerprint(audit):
    """[AEL-Iter-013/P2] 核心架构指纹保护：检查关键类/函数是否物理存在于代码中"""
    sacred_signatures = {
        "core/engine.py": ["TimelineManager"],
        "core/pipeline/steps.py": ["MaskingAndRoutingStep", "ContextualImageAltStep"],
        "core/adapters/ingress.py": ["InputAdapter"],
        "core/egress_dispatcher.py": ["EgressDispatcher", "unmask_fn"],
        "core/config.py": ["ConfigManager"],
    }
    missing = []
    for fpath, signatures in sacred_signatures.items():
        if not os.path.isfile(fpath):
            missing.append(f"{fpath} (文件缺失)")
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        for sig in signatures:
            if sig not in content:
                missing.append(f"{fpath}::{sig}")

    if missing:
        audit.fail("核心架构指纹",
                   f"以下神圣签名从代码中消失: {', '.join(missing[:5])}")
    else:
        total_sigs = sum(len(v) for v in sacred_signatures.values())
        audit.ok("核心架构指纹", f"全部 {total_sigs} 个神圣签名均物理存在")


def check_defensive_coding_patterns(audit):
    """[AEL-Iter-013/P3] 防御性编程：检测 core/ 中高危的裸索引访问模式"""
    dangerous_patterns = [
        (re.compile(r'config\[["\']'), "config 裸索引"),
        (re.compile(r'os\.environ\[["\']'), "os.environ 裸索引"),
    ]
    safe_marker = "# SAFE-INDEX"
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
                        if safe_marker in line:
                            continue
                        for pat, label in dangerous_patterns:
                            if pat.search(line):
                                violations.append(f"{fpath}:{i} ({label})")
            except Exception:
                pass

    if violations:
        audit.warn("防御性编程",
                   f"发现 {len(violations)} 处高危裸索引 (应使用 .get()): {', '.join(violations[:5])}")
    else:
        audit.ok("防御性编程", "core/ 代码未发现高危裸索引访问模式")


def check_global_ki_evolution_freshness(audit):
    """[AEL-Iter-013/P4] 全局知识反哺：检查全局 KI 进化记录是否保持活跃"""
    import time
    evo_global = os.path.expanduser(
        "~/.gemini/antigravity/knowledge/global_integrity/artifacts/evolution_records.md"
    )
    if not os.path.isfile(evo_global):
        audit.warn("全局知识反哺", f"全局进化记录不存在: {evo_global}")
        return
    mtime = os.path.getmtime(evo_global)
    age_days = (time.time() - mtime) / 86400
    if age_days > 7:
        audit.warn("全局知识反哺",
                   f"全局 KI evolution_records.md 已 {int(age_days)} 天未更新，跨项目教训可能正在流失")
    else:
        audit.ok("全局知识反哺", f"全局 KI 进化记录在 {int(age_days)} 天内有更新")


def check_docs_targeted_binding(audit):
    """[AEL-Iter-013/P5] 文档靶向绑定：检查代码域变更是否命中对应文档域"""
    domain_map = {
        "core/config.py": ["docs/REFERENCE.zh-CN.md", "CHANGELOG.md"],
        "core/pipeline/": ["docs/SPECIFICATION.zh-CN.md", "CHANGELOG.md"],
        "plenipes.py": ["docs/MANUAL.zh-CN.md", "CHANGELOG.md"],
    }
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, check=True
        )
        changed = set(result.stdout.strip().split("\n"))
        if not changed or changed == {""}:
            audit.ok("文档靶向绑定", "无暂存区变更，跳过检查")
            return

        violations = []
        for code_domain, doc_targets in domain_map.items():
            domain_hit = any(f.startswith(code_domain) for f in changed)
            if domain_hit:
                doc_hit = any(d in changed for d in doc_targets)
                if not doc_hit:
                    violations.append(f"{code_domain} → 应更新 {' 或 '.join(doc_targets)}")

        if violations:
            audit.warn("文档靶向绑定",
                       f"代码域变更未命中对应文档: {'; '.join(violations)}")
        else:
            audit.ok("文档靶向绑定", "代码域与文档域映射一致")
    except subprocess.CalledProcessError:
        audit.ok("文档靶向绑定", "非 Git 暂存区上下文，跳过检查")


def check_no_unstaged_leftovers(audit):
    """[AEL-Iter-014] 防遺漏检测：检查工作区是否残留未暂存的修改文件"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
        )
        unstaged = []
        for line in result.stdout.strip().split("\n"):
            if len(line) < 2:
                continue
            # git porcelain: index char + worktree char + space + path
            # ' M' = modified but not staged; 'MM' = staged AND has additional unstaged edits
            index_char = line[0]
            worktree_char = line[1]
            path = line[3:]
            # Detect unstaged modifications to tracked files
            if worktree_char == 'M':
                unstaged.append(path)

        if unstaged:
            audit.fail("工作区遺漏检测",
                       f"发现 {len(unstaged)} 个文件已修改但未纳入暂存区 (git add): {', '.join(unstaged[:5])}")
        else:
            audit.ok("工作区遺漏检测", "工作区无残留的未暂存修改")
    except subprocess.CalledProcessError:
        audit.warn("工作区遺漏检测", "无法执行 git status")


def check_test_on_evolution(audit):
    """[AEL-Iter-015/A] 演化必测：检查核心管线变更是否伴随测试文件"""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
            capture_output=True, text=True, check=True
        )
        changed = result.stdout.strip().split("\n")
        
        core_logic_hit = any(
            f.startswith("core/pipeline/") or f.startswith("core/adapters/")
            for f in changed if f.strip()
        )
        
        if not core_logic_hit:
            audit.ok("演化必测", "本次提交未触及核心管线，跳过检查")
            return
            
        has_test = any(
            f.startswith("tests/") or
            "test_" in os.path.basename(f) or
            f.startswith(".plenipes/history/")
            for f in changed if f.strip()
        )
        
        if not has_test:
            audit.warn("演化必测",
                       "检测到 core/pipeline 或 core/adapters 变更，但未发现伴随的测试文件或历史归档")
        else:
            audit.ok("演化必测", "核心管线变更已伴随测试/归档文件")
    except subprocess.CalledProcessError:
        audit.ok("演化必测", "非 Git 暂存区上下文，跳过检查")


def check_no_mass_deletion(audit):
    """[AEL-Iter-015/D] 代码不可裁剪：检测单文件大规模净删除"""
    deletion_threshold = 30  # 单文件净删除行数超过此值则报警
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--numstat"],
            capture_output=True, text=True, check=True
        )
        suspects = []
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) != 3:
                continue
            added, deleted, fpath = parts
            if added == '-' or deleted == '-':  # binary file
                continue
            net_deleted = int(deleted) - int(added)
            if net_deleted >= deletion_threshold and fpath.startswith("core/"):
                suspects.append(f"{fpath} (-{net_deleted}行)")
                
        if suspects:
            audit.warn("代码不可裁剪",
                       f"检测到 {len(suspects)} 个 core/ 文件发生大规模净删除: {'; '.join(suspects[:3])}")
        else:
            audit.ok("代码不可裁剪", "未检测到 core/ 文件的大规模代码裁剪")
    except subprocess.CalledProcessError:
        audit.ok("代码不可裁剪", "非 Git 暂存区上下文，跳过检查")


def check_comment_retention(audit):
    """[AEL-Iter-015/E] 注释不可删除：检测提交中是否大量删除了注释行"""
    comment_markers = ['# ', '"""', "'''", '// ']
    threshold = 10  # 删除超过 10 行注释则报警
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "-U0"],
            capture_output=True, text=True, check=True
        )
        deleted_comments = 0
        current_file = ""
        for line in result.stdout.split("\n"):
            if line.startswith("--- a/") or line.startswith("+++ b/"):
                if line.startswith("+++ b/"):
                    current_file = line[6:]
            elif line.startswith("-") and not line.startswith("---"):
                stripped = line[1:].strip()
                if current_file.startswith("core/") and any(stripped.startswith(m) for m in comment_markers):
                    deleted_comments += 1
                    
        if deleted_comments >= threshold:
            audit.warn("注释不可删除",
                       f"检测到本次提交删除了 {deleted_comments} 行 core/ 注释，请确认是否经过用户授权")
        else:
            audit.ok("注释保护", f"core/ 注释删除量 ({deleted_comments}) 在安全阈值内")
    except subprocess.CalledProcessError:
        audit.ok("注释保护", "非 Git 暂存区上下文，跳过检查")


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
    print("\n🛡️  Illacme-plenipes 治理自审引擎 v4.2 (全域硬约束 + 防裁剪版)")
    print("=" * 60)

    # 切换到项目根目录（如果从别的位置调用）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)

    audit = AuditResult()

    print("\n📂  [1/26] 历史归档完整性...")
    check_history_artifacts_completeness(audit)

    print("\n🔒  [2/26] Git 状态泄露检测...")
    check_git_tracked_state_files(audit)

    print("\n📄  [3/26] Boot Chain 必要文件存在性...")
    check_mandatory_files_exist(audit)

    print("\n🌐  [4/26] 全局 KI 项目污染检测...")
    check_global_ki_no_project_keywords(audit)

    print("\n🛡️  [5/26] .gitignore 规则覆盖度...")
    check_gitignore_coverage(audit)

    print("\n🧬  [6/26] 项目进化记录新鲜度...")
    check_evolution_records_freshness(audit)

    print("\n🔗  [7/26] Boot Chain 完整性...")
    check_boot_chain_integrity(audit)

    print("\n🚫  [8/26] 零占位符协议...")
    check_no_placeholder_patterns(audit)

    print("\n📝  [9/26] 工业级注释主权...")
    check_docstring_coverage(audit)

    print("\n⚡  [10/26] 防爆钩子治理...")
    check_simulation_hook_exists(audit)

    print("\n🔧  [11/26] Pre-commit Hook 安装...")
    check_precommit_hook_exists(audit)

    print("\n🗑️  [12/26] 运行时产物泄露检测...")
    check_untracked_runtime_artifacts(audit)

    print("\n📋  [13/26] 文档更新质量...")
    check_docs_update_quality(audit)

    print("\n🗺️  [14/26] ROADMAP 新鲜度...")
    check_roadmap_freshness(audit)

    print("\n🧪  [15/26] 仿真测试静态存在性...")
    check_simulation_test_coverage(audit)

    print("\n⚔️  [16/26] 仿真引擎物理试运行 (动)...")
    check_simulation_execution(audit)

    print("\n🏷️  [17/26] AEL 代码溯源打标...")
    check_iter_id_tagging(audit)

    print("\n🏛️  [18/26] 核心架构指纹保护...")
    check_core_architecture_fingerprint(audit)

    print("\n🔐  [19/26] 防御性编程静态拦截...")
    check_defensive_coding_patterns(audit)

    print("\n🧠  [20/26] 全局知识反哺新鲜度...")
    check_global_ki_evolution_freshness(audit)

    print("\n📎  [21/26] 文档靶向精准绑定...")
    check_docs_targeted_binding(audit)

    print("\n🚨  [22/26] 工作区遺漏检测...")
    check_no_unstaged_leftovers(audit)

    print("\n🧪  [23/26] 演化必测...")
    check_test_on_evolution(audit)

    print("\n✂️  [24/26] 代码不可裁剪...")
    check_no_mass_deletion(audit)

    print("\n💬  [25/26] 注释不可删除...")
    check_comment_retention(audit)

    print("\n🪞  [26/26] 元审计：自身覆盖度...")
    check_audit_self_coverage(audit)

    success = audit.summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
