#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Pre-Flight Sovereignty Check (重构起飞前检查)
职责：在启动大规模代码手术前，物理核实工作区是否 100% 纯净且已锁定 GitHub。
"""
import subprocess
import sys
import os
import hashlib

def get_dirty_hash():
    """生成当前未提交变更的哈希值"""
    try:
        diff = subprocess.check_output(["git", "diff"], text=False)
        untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], text=False)
        # 合并 diff 和未追踪文件名作为哈希输入
        hasher = hashlib.sha256()
        hasher.update(diff)
        hasher.update(untracked)
        return hasher.hexdigest()
    except:
        return None

def check_workspace_purity(resume_mode=False):
    print(f"🛡️  [起飞前检查] 正在核实工作区主权状态 (模式: {'继承/接力' if resume_mode else '纯净/常规'})...")
    
    # 0. 治理工具完整性校验 (V5.1)
    sentinel_path = ".plenipes/tools/sentinel_matrix.py"
    if not os.path.exists(sentinel_path):
        print(f"❌ [治理中断] 未找到治理哨兵工具: {sentinel_path}")
        print("🚨 [指令] 请先恢复治理基建！")
        return False
    
    try:
        # 1. 检查是否有未暂存或未提交的修改
        status = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
        lines = [line for line in status.split('\n') if line and "themes/universal" not in line]
        
        if lines:
            if resume_mode:
                snapshot_path = ".plenipes/SESSION_SNAPSHOT.md"
                if os.path.exists(snapshot_path):
                    with open(snapshot_path, "r") as f:
                        content = f.read()
                        current_hash = get_dirty_hash()
                        if current_hash and current_hash in content:
                            print("⏩ [继承] 检测到有效的会话快照，主权意志已接力，准予继续。")
                            return True
                    print("❌ [拦截] 虽然开启了接力模式，但工作区现状与快照不符！")
                else:
                    print("❌ [拦截] 未找到 SESSION_SNAPSHOT.md，无法执行接力。")
            
            print("❌ [拦截] 检测到工作区存在未提交的物理变更：")
            for line in lines:
                print(f"  └── {line}")
            print("\n🚨 [治理指令] 请先执行 git commit & push，或使用 --resume 恢复合法快照！")
            return False
        
        # 2. 检查本地与远程是否同步
        subprocess.run(["git", "fetch"], check=True, capture_output=True)
        local_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        remote_hash = subprocess.check_output(["git", "rev-parse", "@{u}"], text=True).strip()
        
        if local_hash != remote_hash:
            print("❌ [拦截] 本地分支与远程 origin/main 不对正！")
            return False
            
        print("✅ [准予起飞] 工作区 100% 纯净，可以启动新任务。")
        return True
        
    except Exception as e:
        print(f"⚠️  [检查异常] 无法验证状态: {e}")
        return False

if __name__ == "__main__":
    resume = "--resume" in sys.argv
    if not check_workspace_purity(resume_mode=resume):
        sys.exit(1)
    sys.exit(0)
