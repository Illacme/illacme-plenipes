#!/usr/bin/env python3
import os

history_dir = ".plenipes/history"

for root, dirs, files in os.walk(history_dir):
    if root == history_dir:
        for d in dirs:
            if d.startswith("2026-"):
                dir_path = os.path.join(root, d)
                dir_files = [f for f in os.listdir(dir_path) if not f.startswith(".")]
                
                # Check for plans
                has_plan = "plan.md" in dir_files or "implementation_plan.md" in dir_files
                # Check for tasks
                has_task = "task.md" in dir_files
                # Check for walkthrough/acceptance
                has_walk = "walkthrough.md" in dir_files or "acceptance.md" in dir_files
                
                if not has_plan:
                    with open(os.path.join(dir_path, "plan.md"), "w") as f:
                        f.write(f"# 溯源补全规划\n\n此文件为系统自动回填的规划占位符，因为早期演化 {d} 缺失规划沉淀。\n")
                if not has_task:
                    with open(os.path.join(dir_path, "task.md"), "w") as f:
                        f.write(f"- [x] 溯源补全任务 (System Auto-Fill for {d})\n")
                if not has_walk:
                    with open(os.path.join(dir_path, "walkthrough.md"), "w") as f:
                        f.write(f"# 溯源复盘总结\n\n此文件为系统自动回填的总结占位符。\n")
