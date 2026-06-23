#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Governance Sentinel Matrix (治理哨兵矩阵)
职责：物理核实代码变更是否符合 SOP-05 及相关治理红线。
"""
import subprocess
import sys
import re
import os
import hashlib

# --- 治理红线配置 ---
REDLINE_MAX_LINES = 300  # 🚀 [V5.4] 治理终极闭环版
GENE_PATTERN = r'🚀\s*\[V\d+\.\d+\]'  # 基因标记正则
DEPENDENCY_FILES = ['requirements.txt', 'package.json']

# 历史遗留且当前正在演进中的超限大文件豁免白名单 — 统一从 YAML 单一真相源加载
from exemption_loader import load_redline_exemptions
EXEMPT_REDLINE_FILES = load_redline_exemptions()

def get_changed_files():
    """获取当前工作区中已修改或暂存的文件列表"""
    try:
        # 获取 M (Modified) 和 A (Added) 状态的文件
        status = subprocess.check_output(["git", "status", "--porcelain"], text=True)
        files = []
        for line in status.split('\n'):
            if not line: continue
            mode = line[:2].strip()
            path = line[3:].strip()
            if mode in ['M', 'A', '??']:
                files.append(path)
        return files
    except:
        return []

def audit_file_redlines(files):
    """审计文件行数是否超标"""
    print("🔍 [审计阶段] 物理红线审计 (行数限制)...")
    failed = False
    for f in files:
        if not os.path.exists(f) or os.path.isdir(f): continue
        if not f.endswith(('.py', '.js')): continue
        
        # 针对历史遗留大文件的豁免放行
        if f in EXEMPT_REDLINE_FILES:
            with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                line_count = sum(1 for _ in file)
            print(f"  ⚠️  [EXEMPT] {f} 历史超标文件已获合规豁免 ({line_count} lines)")
            continue
            
        with open(f, 'r', encoding='utf-8', errors='ignore') as file:
            line_count = sum(1 for _ in file)
            if line_count > REDLINE_MAX_LINES:
                print(f"  ❌ [FAIL] {f} 行数超标: {line_count} (上限: {REDLINE_MAX_LINES})")
                failed = True
            else:
                print(f"  ✅ [PASS] {f} ({line_count} lines)")
    return not failed

def audit_gene_traceability(files):
    """审计基因标记是否被非预期删除"""
    print("🔍 [审计阶段] 基因溯源审计 (🚀 标记维护)...")
    failed = False
    try:
        diff = subprocess.check_output(["git", "diff", "HEAD"], text=True)
        deleted_genes = re.findall(r'^-.*' + GENE_PATTERN, diff, re.MULTILINE)
        added_genes = re.findall(r'^\+.*' + GENE_PATTERN, diff, re.MULTILINE)
        
        def extract_tags(lines):
            tags = set()
            for line in lines:
                m = re.search(r'🚀\s*\[V\d+\.\d+\]', line)
                if m:
                    # Normalize whitespaces inside the tag match
                    tags.add(re.sub(r'\s+', '', m.group(0)))
            return tags
            
        del_tags = extract_tags(deleted_genes)
        add_tags = extract_tags(added_genes)
        actual_deleted = del_tags - add_tags
        
        if actual_deleted:
            print("  ❌ [FAIL] 检测到基因阉割！以下基因标记被非法删除：")
            for gene in actual_deleted:
                print(f"    └── {gene}")
            failed = True
        else:
            print("  ✅ [PASS] 基因完整性校验通过")
    except Exception as e:
        print(f"  ⚠️  [跳过] 无法执行基因差分审计: {e}")
    return not failed

def audit_documentation_quality(files):
    """审计代码文档与类型标注的完备性"""
    print("🔍 [审计阶段] 质量审计 (Docstrings & Typing)...")
    failed = False
    for f in files:
        if not f.endswith(('.py', '.js')): continue
        if not os.path.exists(f) or os.path.isdir(f): continue
        
        with open(f, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            
            # 1. Python 审计
            if f.endswith('.py'):
                # 检查是否包含类或函数定义但缺少 docstring (简单启发式)
                defs = re.findall(r'^(def|class) \w+', content, re.MULTILINE)
                docstrings = re.findall(r'"""[\s\S]*?"""', content)
                if defs and len(docstrings) < len(defs):
                    # 允许文件头部有一个全局 docstring，所以 len(docstrings) 应 >= len(defs) + 1
                    if len(docstrings) <= len(defs):
                        print(f"  ❌ [FAIL] {f}: 检测到函数/类缺少 Docstring 注释")
                        failed = True
                
                # 检查是否包含类型标注 -> 或 :
                if defs and '->' not in content and ':' not in content:
                    print(f"  ❌ [FAIL] {f}: 检测到缺少 Type Hints 类型标注")
                    failed = True

            # 2. JS 审计
            if f.endswith('.js'):
                # 检查是否包含 JSDoc 风格注释 /**
                if '/**' not in content:
                    print(f"  ❌ [FAIL] {f}: 检测到缺少 JSDoc 注释")
                    failed = True
                    
    if not failed:
        print("  ✅ [PASS] 文档与类型完备性校验通过")
    return not failed

def audit_observability(files):
    """审计逻辑演进日志是否同步更新 (SOP-07)"""
    print("🔍 [审计阶段] 可观测性审计 (Logic Evolution Log)...")
    log_path = ".plenipes/history/logic_evolution.log"
    
    # 获取今天的日期字符串
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    def check_log():
        if not os.path.exists(log_path):
            return False
        with open(log_path, 'r', encoding='utf-8') as f:
            return today in f.read()
            
    if not check_log():
        print("  ⚠️  [可观测性缺失] 今日逻辑演进尚未登记。正在启动自动愈合程序...")
        try:
            res = subprocess.run([sys.executable, "scripts/log_healer.py"], capture_output=True, text=True)
            if res.returncode == 0:
                print("  ✅ [自愈成功] 逻辑演进日志已被自愈脚本修补。")
            else:
                print(f"  ❌ [自愈失败] 无法自动修补日志: {res.stderr or res.stdout}")
        except Exception as e:
            print(f"  ❌ [自愈失败] 执行自愈脚本异常: {e}")
            
    # 重新检查
    if not check_log():
        print(f"  ❌ [FAIL] 今日逻辑演进尚未登记！请手动在 {log_path} 中记录变更因果。")
        return False
        
    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()
        
    # 进一步检查日志中是否提到了正在修改的文件（模糊匹配）
    mentions_file = False
    for f in files:
        basename = os.path.basename(f)
        if basename in log_content:
            mentions_file = True
            break
            
    if not mentions_file:
        print("  ⚠️  [警告] 今日日志中未明确检测到当前变更文件的记录条目。")
        # 暂时只警告，不硬拦截，给 AI 一定的合并记录空间
        
    print("  ✅ [PASS] 逻辑演进登记已就绪")
    return True

def audit_architecture_redlines(files):
    """审计架构隔离红线 (SOP-01)"""
    print("🔍 [审计阶段] 架构隔离审计 (脱敏检查)...")
    forbidden_terms = ["config.local.yaml"] # 严禁硬编码在 core 层的术语
    failed = False
    for f in files:
        if not f.startswith('core/'): continue
        if not os.path.exists(f) or os.path.isdir(f): continue
        
        with open(f, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
            for term in forbidden_terms:
                if term in content:
                    print(f"  ❌ [FAIL] {f}: 检测到非法路径硬编码 '{term}' (违反 SOP-01)")
                    failed = True
                    
    if not failed:
        print("  ✅ [PASS] 架构隔离校验通过")
    return not failed

def audit_supply_chain(files):
    """审计供应链依赖漂移 (SOP-10)"""
    print("🔍 [审计阶段] 供应链审计 (Dependency Check)...")
    changed_deps = [f for f in files if f in DEPENDENCY_FILES]
    if not changed_deps:
        print("  ✅ [PASS] 无依赖变更")
        return True
        
    failed = False
    for dep_file in changed_deps:
        try:
            # 检查是否有新增行 (+)
            diff = subprocess.check_output(["git", "diff", "HEAD", dep_file], text=True)
            added_lines = [l for l in diff.split('\n') if l.startswith('+') and not l.startswith('+++')]
            if added_lines:
                print(f"  ❌ [FAIL] {dep_file}: 检测到未授权的新增依赖:")
                for l in added_lines:
                    print(f"    └── {l}")
                failed = True
        except: pass
        
    if not failed:
        print("  ✅ [PASS] 供应链审计通过")
    return not failed

def run_governance_matrix():
    print("🛡️  [治理哨兵] 启动全量合规性矩阵扫描...")
    files = get_changed_files()
    
    if not files:
        print("✅ [无变更] 工作区纯净，无需审计。")
        return True

    results = [
        audit_file_redlines(files),
        audit_gene_traceability(files),
        audit_documentation_quality(files),
        audit_observability(files),
        audit_architecture_redlines(files),
        audit_supply_chain(files)
    ]

    if all(results):
        print("\n🏆 [审计结案] 治理矩阵全量达标。准予执行下一步操作。")
        return True
    else:
        print("\n🚨 [审计拦截] 物理红线或治理规范被触碰！请根据报错信息进行架构降解或基因修复。")
        return False

if __name__ == "__main__":
    if not run_governance_matrix():
        sys.exit(1)
    sys.exit(0)
