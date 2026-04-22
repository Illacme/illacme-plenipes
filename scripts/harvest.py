#!/usr/bin/env python3
import os
import sys
import glob
import shutil
import re
from datetime import datetime

def get_latest_brain_dir():
    brain_root = os.path.expanduser("~/.gemini/antigravity/brain")
    if not os.path.exists(brain_root):
        print(f"Error: Could not find Antigravity brain dir at {brain_root}")
        sys.exit(1)
    
    subdirs = [os.path.join(brain_root, d) for d in os.listdir(brain_root) if os.path.isdir(os.path.join(brain_root, d))]
    if not subdirs:
        print(f"Error: No subdirectories found in {brain_root}")
        sys.exit(1)
        
    latest_dir = max(subdirs, key=os.path.getmtime)
    return latest_dir

def get_next_record_number(records_file):
    if not os.path.exists(records_file):
        return 1
    with open(records_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    matches = re.findall(r'### (\d+)\.', content)
    if not matches:
        return 1
    return max([int(m) for m in matches]) + 1

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text)
    return text.strip('_')

def main():
    if len(sys.argv) < 2:
        print("Usage: python harvest.py \"Task Title or Description\"")
        sys.exit(1)
        
    task_title = sys.argv[1]
    task_slug = slugify(task_title)
    if not task_slug:
        task_slug = "unknown_task"
        
    # Get physical artifacts
    latest_brain = get_latest_brain_dir()
    artifacts = [
        ("implementation_plan.md", "plan.md"),
        ("task.md", "task.md"),
        ("walkthrough.md", "walkthrough.md")
    ]
    
    # Calculate Iteration
    today = datetime.now().strftime("%Y-%m-%d")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    records_file = os.path.join(project_root, ".plenipes", "evolution_records.md")
    
    next_num = get_next_record_number(records_file)
    iter_str = f"{next_num:03d}"
    
    target_dir_name = f"{today}_Iter_{iter_str}_{task_slug}"
    target_dir = os.path.join(project_root, ".plenipes", "history", target_dir_name)
    
    # Copy files
    os.makedirs(target_dir, exist_ok=True)
    files_copied = 0
    for src_name, dst_name in artifacts:
        src_path = os.path.join(latest_brain, src_name)
        if os.path.exists(src_path):
            dst_path = os.path.join(target_dir, dst_name)
            shutil.copy2(src_path, dst_path)
            # Add to git
            os.system(f"git add {dst_path}")
            print(f"✅ Harvested: {dst_name}")
            files_copied += 1
            
    if files_copied == 0:
        print("❌ No artifacts found to harvest.")
        sys.exit(1)
        
    # Inject Evolution Records
    print(f"\n📂 Created Iteration Folder: {target_dir_name}")
    print("\n⚠️  Remember to add your evolution record manually in .plenipes/evolution_records.md!")
    print(f"Suggested snippet:\n\n### {next_num}. [{task_title}] \n- **背景**：...\n- **进化结论**：\n    - \n- **Action**: \n")

if __name__ == "__main__":
    main()
