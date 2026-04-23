#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes 治理自审引擎 v5.4 (五大星系架构版)
🛡️ [AEL-Iter-2026.04.23.TOPOLOGY_P1]
职责：Runner 程序，遵循“先物理，后逻辑，先静态，后动态”的原则调度审计。
"""

import os
import sys
import ast

# 🚀 [Stability] 确保能找到同目录下的 audit_lib
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from audit_lib.base import AuditResult, AutoHealer
from audit_lib.history_checks import *
from audit_lib.code_checks import *
from audit_lib.system_checks import *
from audit_lib.advanced_checks import *

# ──────────────────────────────────────────────
# 🚀 元审计：自检逻辑
# ──────────────────────────────────────────────

def meta_self_check():
    """🚀 [Rule 11.3] 元审计：在运行业务审计前，先确保脚本自身无语法错误或重复定义"""
    script_path = __file__
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source)
        
        # 检查重复的函数名
        func_names = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
        duplicates = set([x for x in func_names if func_names.count(x) > 1])
        if duplicates:
            print(f"❌ [META-FAILURE] 治理脚本自身存在重复函数定义: {duplicates}")
            sys.exit(1)
            
    except SyntaxError as e:
        print(f"❌ [META-FAILURE] 治理脚本自身存在语法错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"⚠️ [META-WARNING] 元审计执行异常: {e}")

# ──────────────────────────────────────────────
# 🚀 主执行入口
# ──────────────────────────────────────────────

def main():
    meta_self_check()
    auto_fix = "--fix" in sys.argv
    audit = AuditResult(auto_fix=auto_fix)
    
    print(f"\n🛡️  Illacme-plenipes 治理自审引擎 v5.4 (五大星系架构版)")
    print(f"自愈模式: {'开启' if auto_fix else '关闭'}")
    print("=" * 60)

    # 自动切换到项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)

    # --- 1. 物理拓扑审计 (Topology Checks) ---
    # 核心原则：先看零件齐不齐，位置对不对
    print("\n🏗️ [1/5] 物理拓扑审计 (Topology Checks)...")
    check_topology_integrity(audit)
    check_contract_alignment(audit)
    check_boot_chain_integrity(audit)
    check_mandatory_files_exist(audit)

    # --- 2. 系统与环境审计 (System Checks) ---
    # 核心原则：看外部环境是否纯净
    print("\n📂 [2/5] 系统与环境审计 (System Checks)...")
    check_git_tracked_state_files(audit)
    check_gitignore_coverage(audit)
    check_global_ki_no_project_keywords(audit)
    check_untracked_runtime_artifacts(audit)
    check_no_placeholder_patterns(audit)
    check_simulation_hook_exists(audit)
    check_precommit_hook_exists(audit)
    check_config_sovereignty(audit)

    # --- 3. 代码质量与逻辑审计 (Code Checks) ---
    # 核心原则：核验代码基因是否符合工业标准
    print("\n📝 [3/5] 代码质量与逻辑审计 (Code Checks)...")
    check_orchestrator_purity(audit)
    check_docstring_coverage(audit)
    check_defensive_coding_patterns(audit)
    check_comment_retention(audit)
    check_no_mass_deletion(audit)
    check_file_complexity(audit)
    check_callout_nesting(audit)
    check_logic_shadowing(audit)
    check_protocol_completeness(audit)

    # --- 4. 动态仿真与点火审计 (Execution Checks) ---
    # 核心原则：真实运行程序，核验点火连通性
    print("\n🚀 [4/5] 动态仿真与点火审计 (Execution Checks)...")
    check_main_entry_smoke_test(audit)
    check_simulation_test_coverage(audit)
    check_simulation_execution(audit)
    check_core_architecture_fingerprint(audit)

    # --- 5. 历史归档与合规审计 (Governance Checks) ---
    # 核心原则：确保存档完整，基因可溯
    print("\n📜 [5/5] 历史归档与合规审计 (Governance Checks)...")
    check_history_artifacts_completeness(audit)
    check_evolution_records_freshness(audit)
    check_global_ki_evolution_freshness(audit)
    check_history_language_sovereignty(audit)
    check_task_completion_status(audit)
    check_roadmap_freshness(audit)
    check_iter_id_tagging(audit)
    check_docs_targeted_binding(audit)
    check_no_unstaged_leftovers(audit)
    check_test_on_evolution(audit)
    check_tdr_rhythm(audit)
    check_audit_self_coverage(audit)
    check_history_docs_depth(audit)

    success = audit.summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
