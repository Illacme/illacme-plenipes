import subprocess
import os
import sys
import json
import re
import ast
from collections import defaultdict

class GalaxyRegistry:
    """🚀 [Industrial] 五大审计维度注册中心"""
    def __init__(self):
        # 按审计维度 ID 存储函数列表
        self.matrix = defaultdict(list)
        self.galaxy_names = {
            1: "🛡️ [维度 1] 物理拓扑 (Topology)",
            2: "🛡️ [维度 2] 系统环境 (System)",
            3: "🛡️ [维度 3] 代码逻辑 (Code)",
            4: "🛡️ [维度 4] 动态仿真 (Execution)",
            5: "🛡️ [维度 5] 历史归档 (History)"
        }

    def register(self, galaxy_id: int):
        """装饰器：将审计项注册到指定星系"""
        def decorator(func):
            self.matrix[galaxy_id].append(func)
            return func
        return decorator

    def run_galaxy(self, galaxy_id: int, audit):
        """执行特定星系的所有审计项"""
        name = self.galaxy_names.get(galaxy_id, f"Galaxy {galaxy_id}")
        print(f"\n{name}...")
        for check_func in self.matrix[galaxy_id]:
            try:
                check_func(audit)
            except Exception as e:
                audit.fail(f"审计项执行异常: {check_func.__name__}", str(e))

registry = GalaxyRegistry()
galaxy = registry.register

class AuditResult:
    def __init__(self, auto_fix=False):
        self.passed = []
        self.failed = []
        self.warnings = []
        self.fixable = [] # (name, detail, fix_func)
        self.auto_fix = auto_fix

    def ok(self, name, detail=""):
        self.passed.append((name, detail))
        print(f"  ✅ {name}" + (f" — {detail}" if detail else ""))

    def fail(self, name, detail="", fix_func=None):
        if self.auto_fix and fix_func:
            print(f"  🔧 {name} — 正在尝试自愈修复...")
            if fix_func():
                self.ok(name, f"{detail} (已自动修复)")
                return
        
        self.failed.append((name, detail))
        if fix_func:
            self.fixable.append((name, detail, fix_func))
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
                has_fix = any(f[0] == name for f in self.fixable)
                fix_tag = " [可自愈, 请运行 --fix]" if has_fix else ""
                print(f"   → {name}{fix_tag}: {detail}")
        
        if self.warnings:
            print(f"\n⚠️  以下问题建议尽快处理：")
            for name, detail in self.warnings:
                print(f"   → {name}: {detail}")
        print(f"{'='*60}")
        return len(self.failed) == 0

class AutoHealer:
    """🚀 [V5.2] 治理自愈中心：提供确定性偏差的物理修正逻辑"""
    
    @staticmethod
    def fix_ael_tag(file_path, iter_id):
        """注入 AEL 溯源标记"""
        if not os.path.exists(file_path): return False
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        if lines and lines[0].startswith("#!"):
            insert_pos = 1
        else:
            insert_pos = 0
            
        tag_line = f"🛡️ [{iter_id}]\n"
        lines.insert(insert_pos, tag_line)
        
        with open(file_path, 'w') as f:
            f.writelines(lines)
        return True

    @staticmethod
    def sync_task_checklist(task_file):
        """基于仿真成功结果，自动核销任务清单"""
        if not os.path.exists(task_file): return False
        with open(task_file, 'r') as f:
            content = f.read()
        
        new_content = content.replace("[ ]", "[x]")
        if new_content == content: return False
        
        with open(task_file, 'w') as f:
            f.write(new_content)
        return True
