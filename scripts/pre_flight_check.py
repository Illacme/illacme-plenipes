#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Pre-Flight Sovereignty Check (重构起飞前检查)
职责：在启动大规模代码手术前，物理核实工作区是否 100% 纯净且已锁定 GitHub。
"""
import subprocess
import sys

def check_workspace_purity():
    print("🛡️  [起飞前检查] 正在核实工作区主权状态...")
    
    try:
        # 1. 检查是否有未暂存或未提交的修改
        status = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
        
        # 排除 themes/universal 等已知的 untracked submodule 干扰
        lines = [line for line in status.split('\n') if line and "themes/universal" not in line]
        
        if lines:
            print("❌ [拦截] 检测到工作区存在未提交的物理变更：")
            for line in lines:
                print(f"  └── {line}")
            print("\n🚨 [治理指令] 请先执行 git commit & push，锁定当前基准后再启动新任务！")
            return False
        
        # 2. 检查本地与远程是否同步
        subprocess.run(["git", "fetch"], check=True, capture_output=True)
        local_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        remote_hash = subprocess.check_output(["git", "rev-parse", "@{u}"], text=True).strip()
        
        if local_hash != remote_hash:
            print(f"❌ [拦截] 本地分支与远程 origin/main 不对正！")
            print(f"  └── Local:  {local_hash[:7]}")
            print(f"  └── Remote: {remote_hash[:7]}")
            print("\n🚨 [治理指令] 请先执行 git push，确保云端资产已锁定！")
            return False
            
        print("✅ [准予起飞] 工作区 100% 纯净，GitHub 已同步，可以启动重构手术。")
        return True
        
    except Exception as e:
        print(f"⚠️  [检查异常] 无法验证 Git 状态: {e}")
        return False

if __name__ == "__main__":
    if not check_workspace_purity():
        sys.exit(1)
    sys.exit(0)
