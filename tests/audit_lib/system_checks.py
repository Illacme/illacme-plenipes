import os
import subprocess
import re
import sys

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
    except Exception:
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
    project_keywords = ["illacme", "plenipes", ".plenipes"]
    violations = []
    for root, dirs, files in os.walk(ki_base):
        for fname in files:
            if not fname.endswith(".md"): continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                for kw in project_keywords:
                    if kw.lower() in content:
                        violations.append(f"{fname} 包含 '{kw}'")
                        break
            except Exception: pass
    if violations:
        audit.warn("全局 KI 项目污染", f"全局文件含项目关键词: {'; '.join(violations)}")
    else:
        audit.ok("全局 KI 纯净度", "全局知识库未发现当前项目特定关键词")

def check_gitignore_coverage(audit):
    """[AEL-Iter-006] 检查 .gitignore 是否覆盖了所有关键状态路径"""
    gitignore = ".gitignore"
    if not os.path.isfile(gitignore):
        audit.fail(".gitignore 缺失")
        return
    required = [".plenipes/*.json", ".plenipes/*.log", ".illacme-shadow/"]
    with open(gitignore, "r") as f:
        content = f.read()
    missing = [p for p in required if p not in content]
    if missing:
        audit.warn(".gitignore 覆盖不足", f"建议添加: {', '.join(missing)}")
    else:
        audit.ok(".gitignore 覆盖度", "所有已知状态文件均已被屏蔽")

def check_boot_chain_integrity(audit):
    """[AEL-Iter-006] 检查 .antigravityrules 的加载完整性"""
    boot_file = ".antigravityrules"
    if not os.path.isfile(boot_file): return
    with open(boot_file, "r") as f:
        content = f.read()
    checks = {
        "强制读取指令": "view_file",
        "rules.md 引用": ".plenipes/rules.md",
        "evolution_records 引用": ".plenipes/evolution_records.md",
        "稳定性硬约束": "Rule 11.1"
    }
    for name, pattern in checks.items():
        if pattern in content:
            audit.ok(f"Boot Chain: {name}")
        else:
            audit.fail(f"Boot Chain 损坏: {name}", f"缺失 {pattern}")

def check_no_placeholder_patterns(audit):
    """[AEL-Iter-006] 检查代码中是否存在待办占位符（如 FIXME, TODO, [ ]）"""
    forbidden = ["TODO", "FIXME", "[ ]"]
    violations = []
    for root, dirs, files in os.walk("core"):
        for f in files:
            if f.endswith(".py"):
                fpath = os.path.join(root, f)
                with open(fpath, "r", encoding="utf-8") as file:
                    for i, line in enumerate(file, 1):
                        for p in forbidden:
                            if p in line:
                                violations.append(f"{f}:{i} ({p})")
                                break
    if violations:
        audit.warn("零占位符协议", f"核心代码包含占位符: {'; '.join(violations[:3])}")
    else:
        audit.ok("零占位符协议", "核心代码无占位符标记残留")

def check_simulation_hook_exists(audit):
    """[AEL-Iter-006] 检查仿真钩子物理存在性"""
    hook_path = "core/engine.py"
    if not os.path.isfile(hook_path): return
    with open(hook_path, "r") as f:
        content = f.read()
    if "verify_docs_sync_hook" in content:
        audit.ok("防爆钩子治理", "verify_docs_sync_hook 物理存在且完好")
    else:
        audit.fail("防爆钩子缺失", "engine.py 中未发现仿真校验钩子")

def check_precommit_hook_exists(audit):
    """[AEL-Iter-006] 检查 .git/hooks/pre-commit 是否已安装并指向治理脚本"""
    hook = ".git/hooks/pre-commit"
    if not os.path.isfile(hook):
        audit.warn("Pre-commit Hook 缺失", "建议安装以确保本地治理闭环")
        return
    with open(hook, "r") as f:
        content = f.read()
    if "governance_audit.py" in content:
        audit.ok("Pre-commit Hook", "已安装且指向 governance_audit.py")
    else:
        audit.warn("Pre-commit Hook 异常", "已安装但未调用治理审计脚本")

def check_untracked_runtime_artifacts(audit):
    """[AEL-Iter-006] 检查是否存在未追踪且未被忽略的运行时产物"""
    forbidden_exts = [".pyc", ".log", ".tmp", ".bak"]
    found = []
    for root, dirs, files in os.walk("."):
        if ".git" in root or "venv" in root or "__pycache__" in root: continue
        for f in files:
            if any(f.endswith(ext) for ext in forbidden_exts):
                fpath = os.path.join(root, f)
                # 🛡️ 询问 Git：这个文件是被忽略的吗？
                try:
                    result = subprocess.run(
                        ["git", "check-ignore", "-q", fpath],
                        capture_output=False, text=False
                    )
                    if result.returncode != 0: # 返回非 0 表示未被忽略
                        found.append(f)
                except Exception:
                    found.append(f)
    if found:
        audit.warn("运行时产物检测", f"发现未追踪且未忽略文件: {', '.join(found[:5])}")
    else:
        audit.ok("运行时产物检测", "工作区纯净，无异常产物")

def check_main_entry_smoke_test(audit):
    """[AEL-Iter-029] 主入口冒烟测试：强制执行 plenipes.py --dry-run 核验点火连通性"""
    entry_script = "plenipes.py"
    if not os.path.isfile(entry_script):
        audit.fail("主入口缺失", f"未发现 {entry_script}")
        return

    try:
        # 执行 dry-run，限制运行时间并捕获输出
        result = subprocess.run(
            [sys.executable, entry_script, "--dry-run"],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode == 0:
            audit.ok("主入口冒烟测试", "点火成功，全量服务初始化正常")
        else:
            # 提取关键错误信息
            error_msg = result.stderr.split("\n")[-2:] if result.stderr else "未知错误"
            audit.fail("主入口点火失败", f"Dry-run 返回非零码，关键报错: {error_msg}")
    except subprocess.TimeoutExpired:
        audit.warn("主入口点火超时", "Dry-run 执行超过 20 秒，可能存在死循环或网络阻塞")
    except Exception as e:
        audit.fail("主入口点火异常", f"执行过程崩溃: {e}")

def check_config_sovereignty(audit):
    """[Rule 12.7] 配置文件主权审计：监控 config.yaml 的规模稳定性，防止盲目修剪"""
    config_file = "config.yaml"
    if not os.path.isfile(config_file): return
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            count = len(lines)
            comment_count = sum(1 for line in lines if line.strip().startswith("#"))
            
        # 物理质量基准：由于已启用 Rule 11.5 分片协议，主文件行数允许下降，但仍需监控
        if count < 100:
            audit.fail("配置文件主权 (RED)", f"config.yaml 规模异常缩小 ({count} 行)，疑似发生盲目内容修剪")
        elif comment_count < 30: # 主文件保留核心引导注释
            audit.warn("配置文档主权", f"检测到 config.yaml 引导注释密度较低 ({comment_count} 行)")
        else:
            audit.ok("配置文件主权", f"config.yaml 已适配分片协议 ({count} 行)，文档引导密度达标")
            
        # 扩展审计：检查子模块文件的完整性
        configs_dir = "configs"
        if os.path.isdir(configs_dir):
            for f in os.listdir(configs_dir):
                if f.endswith(".yaml"):
                    fpath = os.path.join(configs_dir, f)
                    with open(fpath, "r", encoding="utf-8") as sub_f:
                        sub_lines = sub_f.readlines()
                        sub_comments = sum(1 for l in sub_lines if l.strip().startswith("#"))
                        if sub_comments < 5:
                            audit.warn("分片文档缺失", f"配置分片 {f} 缺失工业级注释说明")
    except Exception:
        pass
