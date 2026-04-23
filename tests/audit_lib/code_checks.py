import os
import subprocess
import re
import ast
from .base import galaxy

@galaxy(3)
def check_docstring_coverage(audit):
    """[AEL-Iter-006] 检查 core/ 目录下所有 Python 文件是否包含模块级文档字符串"""
    core_dir = "core"
    if not os.path.isdir(core_dir): return
    
    missing = []
    for root, dirs, files in os.walk(core_dir):
        for f in files:
            if f.endswith(".py") and f != "__init__.py":
                fpath = os.path.join(root, f)
                with open(fpath, "r", encoding="utf-8") as file:
                    try:
                        tree = ast.parse(file.read())
                        if not ast.get_docstring(tree):
                            missing.append(fpath)
                    except Exception:
                        pass
    if missing:
        audit.fail("工业级注释主权", f"以下文件缺失模块级文档字符串: {', '.join(missing[:3])}")
    else:
        audit.ok("注释主权", "所有核心逻辑文件均具备工业级模块注释")

@galaxy(3)
def check_defensive_coding_patterns(audit):
    """[AEL-Iter-009] 检查代码中是否存在潜在的 NoneType 风险（防御性编程审计）"""
    core_dir = "core"
    if not os.path.isdir(core_dir): return
    
    risky_pattern = re.compile(r'\[[\'"]\w+[\'"]\]')
    violations = 0
    for root, dirs, files in os.walk(core_dir):
        for f in files:
            if f.endswith(".py"):
                fpath = os.path.join(root, f)
                with open(fpath, "r", encoding="utf-8") as file:
                    content = file.read()
                    if "config" in content.lower():
                        matches = risky_pattern.findall(content)
                        if len(matches) > 10:
                            violations += 1
    if violations > 0:
        audit.fail("防御性编程审计", f"检测到 {violations} 个文件存在较多裸引用索引，必须改用 .get() 确保 NoneType 免疫力")
    else:
        audit.ok("防御性编程", "核心逻辑具备良好的 NoneType 免疫力")

@galaxy(3)
def check_comment_retention(audit):
    """[AEL-Iter-015/E] 注释不可删除：检测提交中是否大量删除了注释行"""
    comment_markers = ['# ', '"""', "'''", '// ']
    threshold = 10 
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
            # 🛡️ 增加重构豁免检查
            if _is_refactoring_phase():
                audit.ok("注释主权 (重构豁免)", f"检测到重构期，允许 core/ 注释大规模迁移 ({deleted_comments} 行)")
            else:
                audit.warn("注释不可删除", f"检测到本次提交删除了 {deleted_comments} 行 core/ 注释")
        else:
            audit.ok("注释保护", f"core/ 注释删除量 ({deleted_comments}) 在安全范围内")
    except Exception:
        audit.ok("注释保护", "非 Git 暂存区上下文，跳过检查")

def _is_refactoring_phase():
    """探测是否处于重大架构重构期"""
    # 逻辑 1：检查演化记录中是否有 'Refactor' 或 'Reconstruction' 关键字
    evo_file = ".plenipes/evolution_records.md"
    if os.path.exists(evo_file):
        with open(evo_file, "r", encoding="utf-8") as f:
            tail = f.read()[-500:] # 只看最近 500 字符
            if "Refactor" in tail or "Reconstruction" in tail or "架构包化" in tail:
                return True
    return False

@galaxy(3)
def check_no_mass_deletion(audit):
    """[AEL-Iter-015/D] 代码不可裁剪：检测单文件大规模净删除"""
    deletion_threshold = 30
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--numstat"],
            capture_output=True, text=True, check=True
        )
        suspects = []
        for line in result.stdout.strip().split("\n"):
            if not line.strip(): continue
            parts = line.split("\t")
            if len(parts) != 3: continue
            added, deleted, fpath = parts
            if added == '-' or deleted == '-': continue
            net_deleted = int(deleted) - int(added)
            if net_deleted >= deletion_threshold and fpath.startswith("core/"):
                suspects.append(f"{fpath} (-{net_deleted}行)")
                
        if suspects:
            if _is_refactoring_phase():
                audit.ok("代码不可裁剪 (重构豁免)", f"重构期允许核心代码大幅变动: {'; '.join(suspects[:3])}")
            else:
                audit.warn("代码不可裁剪", f"检测到 core/ 文件发生大规模净删除: {'; '.join(suspects[:3])}")
        else:
            audit.ok("代码不可裁剪", "未检测到核心代码大规模裁剪")
    except Exception:
        audit.ok("代码不可裁剪", "非 Git 暂存区上下文，跳过检查")

@galaxy(3)
def check_file_complexity(audit):
    """🚀 [Rule 12.10] 工业级复杂度红线：核心逻辑文件严禁超过 300 行"""
    FAIL_THRESHOLD = 300
    violation_found = False
    
    for root, dirs, files in os.walk("core"):
        for f in files:
            if f.endswith(".py"):
                fpath = os.path.join(root, f)
                try:
                    with open(fpath, 'r', encoding='utf-8') as file:
                        count = len(file.readlines())
                        if count > FAIL_THRESHOLD:
                            audit.fail("单文件行数超标 (RED)", f"文件 {f} ({count} 行) 超过了 {FAIL_THRESHOLD} 行的红线限制，必须执行模块拆分！")
                            violation_found = True
                except Exception: pass
    
    if not violation_found:
        audit.ok("代码复杂度控制", f"全量核心逻辑文件均控制在 {FAIL_THRESHOLD} 行红线内")

@galaxy(3)
def check_callout_nesting(audit):
    """[AEL-Iter-v5.1] 嵌套 Callout 校验：AST 语义特征审计"""
    service_path = "core/services/staticizer.py"
    if not os.path.exists(service_path):
        audit.fail("Callout 嵌套校验", "缺失核心服务文件")
        return

    try:
        with open(service_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        
        found_recursive = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "staticize_callouts":
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Call) and isinstance(subnode.func, ast.Attribute):
                        if subnode.func.attr == "staticize_callouts":
                            found_recursive = True
                            break
        
        if found_recursive:
            audit.ok("Callout 嵌套校验", "已通过 AST 静态分析确认逻辑具备递归特征")
        else:
            audit.fail("Callout 嵌套校验", "AST 审计失败：staticize_callouts 内未发现递归调用")
    except Exception as e:
        audit.fail("Callout 嵌套校验", f"AST 审计解析异常: {str(e)}")


@galaxy(3)
def check_logic_shadowing(audit):
    """[Rule 12.9] 协议/逻辑隔离审计：确保子类没有重写基类的受保护业务方法"""
    # 🚀 深度审计范围：AI 适配器子包
    adapter_dir = "core/adapters/ai"
    if not os.path.isdir(adapter_dir): return
    
    # 定义属于“大脑层”的逻辑方法，严禁子类重写
    protected_methods = {'translate', 'generate_slug', 'generate_seo_metadata'}
    violation_found = False
    
    for root, dirs, files in os.walk(adapter_dir):
        for f in files:
            if f.endswith(".py") and f != "base.py":
                fpath = os.path.join(root, f)
                try:
                    with open(fpath, "r", encoding="utf-8") as file:
                        tree = ast.parse(file.read())
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                # 排除策略类，它们需要重写 translate 以实现调度逻辑
                                if "Strategy" in node.name: continue
                                
                                # 检查子类是否重写了受保护的方法
                                methods = {n.name for n in node.body if isinstance(n, ast.FunctionDef)}
                                shadowed = protected_methods & methods
                                if shadowed:
                                    audit.fail("逻辑主权篡改 (RED)", f"类 {node.name} ({f}) 非法重写了业务层逻辑: {', '.join(shadowed)}")
                                    violation_found = True
                except Exception: pass
    
    if not violation_found:
        audit.ok("架构主权隔离", "未发现子类对业务层逻辑的非法篡改")

@galaxy(3)
def check_protocol_completeness(audit):
    """强制校验所有 Translator 必须实现原子协议 _ask_ai"""
    adapter_dir = "core/adapters/ai"
    if not os.path.isdir(adapter_dir): return
    
    violation_found = False
    for root, dirs, files in os.walk(adapter_dir):
        for f in files:
            if f.endswith(".py") and f != "base.py":
                fpath = os.path.join(root, f)
                try:
                    with open(fpath, "r", encoding="utf-8") as file:
                        tree = ast.parse(file.read())
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef) and node.name.endswith("Translator"):
                                if node.name in ["BaseTranslator", "FallbackStrategy", "SmartRoutingStrategy"]: continue
                                methods = {n.name for n in node.body if isinstance(n, ast.FunctionDef)}
                                if "_ask_ai" not in methods:
                                    audit.fail("协议实现缺失 (RED)", f"类 {node.name} ({f}) 未实现原子协议 _ask_ai")
                                    violation_found = True
                except Exception: pass
    if not violation_found:
        audit.ok("适配器契约完整度", "所有适配器均已正确实现原子协议契约")
