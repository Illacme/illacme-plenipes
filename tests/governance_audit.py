#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Sovereign Governance Engine v5.4.1
🛡️ [Industrial] 五大星系治理引擎：动态注册与有序执行版
"""
import sys
import os
import importlib

# 确保能加载到 tests.audit_lib
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audit_lib.base import AuditResult, registry

def load_all_checks():
    """动态加载 audit_lib 下的所有审计模块以激活注册装饰器"""
    lib_path = os.path.join(os.path.dirname(__file__), "audit_lib")
    for f in os.listdir(lib_path):
        if f.endswith(".py") and f != "base.py":
            module_name = f"audit_lib.{f[:-3]}"
            importlib.import_module(module_name)

def main():
    print("🛡️  Illacme-plenipes 治理自审引擎 v5.4.1 (星系动态加载版)")
    print("自愈模式: " + ("开启" if "--fix" in sys.argv else "关闭"))
    print("=" * 60)

    # 1. 初始化审计上下文
    audit = AuditResult(auto_fix="--fix" in sys.argv)
    
    # 2. 动态发现所有审计项
    load_all_checks()
    
    # 3. 按照星系序列 (1-5) 执行有序审计
    for g_id in range(1, 6):
        registry.run_galaxy(g_id, audit)

    # 4. 输出最终判定结果
    success = audit.summary()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
