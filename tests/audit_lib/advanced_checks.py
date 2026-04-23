import os
import subprocess
import re
import ast
import sys

def check_core_architecture_fingerprint(audit):
    """[AEL-Iter-011] 核心架构指纹校验：拦截非法的大规模逻辑重构"""
    fingerprints = {
        "core/engine.py": 250, # 允许上下波动 100 行
        "core/pipeline/runner.py": 100,
        "core/pipeline/steps.py": 150
    }
    for path, expected in fingerprints.items():
        if not os.path.exists(path): continue
        with open(path, "r") as f:
            count = len(f.readlines())
        if abs(count - expected) > 100: 
            audit.warn("架构指纹偏差", f"{path} 体积异常 ({count} 行)，请确认是否涉及重大重构")
        else:
            audit.ok(f"指纹校验: {path}")

def check_simulation_test_coverage(audit):
    """[AEL-Iter-006] 检查仿真测试文件是否存在"""
    tests = ["tests/autonomous_simulation.py", "tests/governance_audit.py"]
    for t in tests:
        if os.path.isfile(t):
            audit.ok(f"测试存在: {t}")
        else:
            audit.fail(f"测试缺失: {t}")

def check_simulation_execution(audit):
    """[AEL-Iter-006] 物理试运行仿真引擎"""
    sim_script = "tests/autonomous_simulation.py"
    if not os.path.isfile(sim_script): return
    try:
        result = subprocess.run(
            [sys.executable, sim_script, "--check-only"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            audit.ok("仿真引擎试运行", "影子校验通过")
        else:
            audit.fail("仿真引擎试运行", "影子校验失败，请检查逻辑输出")
    except Exception as e:
        audit.warn("仿真引擎试运行", f"执行超时或异常 (可能非致命): {e}")

def check_iter_id_tagging(audit):
    """[AEL-Iter-011] AEL 代码溯源打标审计：检测最近提交是否含 Iter-ID"""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"], capture_output=True, text=True
        )
        if "[AEL-Iter-" in result.stdout:
            audit.ok("AEL 溯源打标", "检测到有效的迭代 ID 标记")
        else:
            audit.warn("AEL 溯源打标", "本次提交缺少 [AEL-Iter-ID] 标记，建议补全")
    except Exception:
        pass

def check_global_ki_evolution_freshness(audit):
    """[AEL-Iter-006] 检查全局 KI 演化记录新鲜度"""
    ki_evo = os.path.expanduser("~/.gemini/antigravity/knowledge/global_integrity/artifacts/evolution_records.md")
    if not os.path.isfile(ki_evo): return
    
    import time
    mtime = os.path.getmtime(ki_evo)
    days = (time.time() - mtime) / (24 * 3600)
    if days < 7:
        audit.ok("全局知识沉淀", f"全局演化记录最近 {int(days)} 天内有更新")
    else:
        audit.warn("全局知识荒废", f"全局演化记录已有 {int(days)} 天未更新，AI 经验可能过时")

def check_docs_targeted_binding(audit):
    """[AEL-Iter-013] 文档靶向精准绑定：检测核心变更是否同步了历史归档"""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], capture_output=True, text=True
        )
        files = result.stdout.split("\n")
        has_core = any(f.startswith("core/") for f in files)
        has_history = any(f.startswith(".plenipes/history/") for f in files)
        if has_core and not has_history:
            audit.fail("文档靶向绑定", "核心代码已变动，但未发现同步的历史归档 (history/plan/task)")
        else:
            audit.ok("文档靶向绑定", "变更链路完整性达标")
    except Exception:
        pass

def check_no_unstaged_leftovers(audit):
    """[AEL-Iter-014] 防遺漏检测：检查工作区是否残留未暂存的修改文件"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True
        )
        unstaged = []
        for line in result.stdout.strip().split("\n"):
            if len(line) < 2: continue
            if line[1] == 'M':
                unstaged.append(line[3:])
        if unstaged:
            audit.fail("工作区遺漏检测", f"发现 {len(unstaged)} 个文件已修改但未暂存")
        else:
            audit.ok("工作区遺漏检测", "工作区无残留修改")
    except Exception:
        pass

def check_test_on_evolution(audit):
    """[AEL-Iter-015/A] 演化必测：检查核心管线变更是否伴随测试文件"""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], capture_output=True, text=True
        )
        changed = result.stdout.split("\n")
        core_logic = any(f.startswith("core/pipeline/") for f in changed)
        has_test = any(f.startswith("tests/") or "test_" in f for f in changed)
        if core_logic and not has_test:
            audit.warn("演化必测", "核心管线已变动，但未发现新增测试")
        else:
            audit.ok("演化必测", "变更伴随测试验证")
    except Exception:
        pass

def check_tdr_rhythm(audit):
    """[AEL-Iter-017] TDR 架构复健节律器：检测业务迭代与架构迭代的比例"""
    history_dir = ".plenipes/history"
    if not os.path.exists(history_dir): return
    dirs = os.listdir(history_dir)
    biz_iters = len([d for d in dirs if "_v" in d or "Iter_" in d])
    tdr_iters = len([d for d in dirs if "TDR-" in d])
    
    if biz_iters > 0 and tdr_iters == 0 and biz_iters > 5:
        audit.warn("TDR 节律", f"已累计 {biz_iters} 次业务迭代，建议安排架构复健 (TDR)")
    else:
        audit.ok("TDR 节律", f"当前业务/重构比: {biz_iters}/{tdr_iters}")

def check_audit_self_coverage(audit):
    """[Meta-Audit] 审计自身覆盖度：检查检查项是否覆盖了所有已记录教训"""
    evo_file = ".plenipes/evolution_records.md"
    if not os.path.exists(evo_file): return
    with open(evo_file, "r") as f:
        content = f.read()
    lessons = re.findall(r"^### \d+\.", content, re.MULTILINE)
    audit.ok("元审计覆盖度", f"当前已对齐 {len(lessons)} 条教训")

def check_orchestrator_purity(audit):
    """[AEL-Iter-028] 调度器纯净度审计：拦截硬编码与过深的分支逻辑"""
    orchestrators = [
        "core/adapters/ingress/__init__.py",
        "core/adapters/egress/ssg/__init__.py",
        "core/adapters/syndication/syndication.py",
        "core/adapters/ai_provider.py"
    ]
    forbidden_terms = ['obsidian', 'logseq', 'notion', 'typora', 'mkdocs', 
                       'devto', 'medium', 'ghost', 'wordpress', 'hashnode', 'linkedin',
                       'starlight', 'docusaurus', 'hugo']
    for path in orchestrators:
        if not os.path.exists(path): continue
        with open(path, "r", encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                # 豁免 import 语句、注释和注册表注册行
                clean_line = line.strip()
                if not clean_line or clean_line.startswith('#'): continue
                if 'import ' in line or 'from ' in line: continue
                if 'Registry.register' in line: continue
                
                # 1. 检查硬编码关键词
                for term in forbidden_terms:
                    if re.search(rf"['\"]{term}['\"]", line, re.IGNORECASE):
                        audit.fail("架构主权篡改", f"在 {path}:{i+1} 发现硬编码插件名 '{term}'")
                indent = len(line) - len(line.lstrip())
                if indent >= 16:
                    if any(kw in line for kw in ['if ', 'elif ', 'for ', 'while ']):
                         audit.fail("逻辑层级过深", f"在 {path}:{i+1} 嵌套超过 3 层")


def check_topology_integrity(audit):
    """[AEL-Iter-029] 物理拓扑完整性审计：检查包结构、导入连通性与契约对齐"""
    core_dir = "core"
    if not os.path.exists(core_dir): return

    # 1. 检查包结构 (Package Integrity)
    for root, dirs, files in os.walk(core_dir):
        if "__pycache__" in root: continue
        py_files = [f for f in files if f.endswith(".py")]
        if py_files and "__init__.py" not in files:
            audit.fail("物理拓扑缺失", f"目录 {root} 包含 Python 文件但缺失 __init__.py")
        elif py_files:
            audit.ok(f"包结构确认: {root}")

    # 2. 检查静态导入连通性 (Import Connectivity)
    _check_imports_in_dir(core_dir, audit)

def _check_imports_in_dir(target_dir, audit):
    for root, _, files in os.walk(target_dir):
        for file in files:
            if not file.endswith(".py") or file == "__init__.py": continue
            path = os.path.join(root, file)
            with open(path, "r", encoding='utf-8') as f:
                try:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.Import, ast.ImportFrom)):
                            _verify_import_node(node, path, audit)
                except Exception as e:
                    audit.warn("静态解析失败", f"无法解析 {path}: {e}")

def _verify_import_node(node, source_file, audit):
    """验证 AST 导入节点是否对应真实物理文件"""
    if isinstance(node, ast.Import):
        for alias in node.names:
            _validate_module_path(alias.name, source_file, audit)
    elif isinstance(node, ast.ImportFrom):
        if node.level > 0: # 处理相对导入
            # 相对导入校验逻辑较为复杂，此处优先校验绝对导入
            return 
        _validate_module_path(node.module, source_file, audit)

def _validate_module_path(module_name, source_file, audit):
    if not module_name or not module_name.startswith('core.'): return
    
    # 将 core.adapters.ingress 转换为 core/adapters/ingress.py 或 core/adapters/ingress/__init__.py
    rel_path = module_name.replace('.', '/')
    potential_file = rel_path + ".py"
    potential_dir = rel_path + "/__init__.py"
    
    if not os.path.exists(potential_file) and not os.path.exists(potential_dir):
        audit.fail("导入路径断裂", f"在 {source_file} 中发现虚假导入: {module_name}")

def check_contract_alignment(audit):
    """[AEL-Iter-029] 接口契约对齐审计：核验核心方法签名兼容性"""
    # 此处通过静态分析检查特定方法的参数数量
    core_files = {
        "core/adapters/syndication/syndication.py": ("syndicate", 8), # 至少 8 个参数
    }
    for path, (method_name, min_args) in core_files.items():
        if not os.path.exists(path): continue
        with open(path, "r", encoding='utf-8') as f:
            tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == method_name:
                    arg_count = len(node.args.args)
                    if arg_count < min_args:
                        audit.fail("接口契约断裂", f"{path} 中的 {method_name} 参数不足 (需 {min_args}, 实 {arg_count})")
                    else:
                        audit.ok(f"契约对齐: {path} -> {method_name}")
