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

def get_next_iter_number(history_dir):
    """从 .plenipes/history/ 物理扫描最大 Iter 编号，避免编号冲突"""
    max_num = 0
    if os.path.isdir(history_dir):
        for entry in os.listdir(history_dir):
            match = re.search(r'Iter[_-](\d+)', entry)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
            # 兼容旧版 AEL-Iter-NNN 格式
            match2 = re.search(r'AEL-Iter-(\d+)', entry)
            if match2:
                num = int(match2.group(1))
                if num > max_num:
                    max_num = num
            # 兼容旧版 TDR-Iter-NNN 格式
            match3 = re.search(r'TDR-Iter-(\d+)', entry)
            if match3:
                num = int(match3.group(1))
                if num > max_num:
                    max_num = num
    return max_num + 1

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
    history_dir = os.path.join(project_root, ".plenipes", "history")
    
    next_num = get_next_iter_number(history_dir)
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
    
    # ── 踩坑信号检测 (Lesson Signal Detection) ──
    lesson_signals = detect_lesson_signals(latest_brain, project_root)
    if lesson_signals:
        print("\n" + "=" * 50)
        print("🧠 [踩坑信号检测] 发现以下信号，可能需要沉淀教训：")
        for sig in lesson_signals:
            print(f"   → {sig}")
        print("=" * 50)
        print("📝 请确认是否需要在 evolution_records.md 中追加教训条目。")
        print("   如果确认无需追加，请在 commit message 中注明 [NO-LESSON]。")
    else:
        print("\n✅ [踩坑信号检测] 本次迭代未检测到典型踩坑信号，无需强制更新 evolution_records。")


def detect_lesson_signals(brain_dir, project_root):
    """扫描 walkthrough 内容和 git 历史，检测是否存在"应该写教训但没写"的信号"""
    import subprocess
    signals = []
    
    # ── 信号 1: walkthrough 中是否包含修复/问题关键词 ──
    walkthrough_path = os.path.join(brain_dir, "walkthrough.md")
    if os.path.exists(walkthrough_path):
        with open(walkthrough_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
        fix_keywords = ['修复', '修补', 'fix', 'bug', '缺陷', '故障', '踩坑', '问题', 'hotfix', 'revert', '回滚', '遗漏']
        hits = [kw for kw in fix_keywords if kw in content]
        if hits:
            signals.append(f"walkthrough.md 含修复信号关键词: {', '.join(hits[:5])}")
    
    # ── 信号 2: 最近 5 次 commit message 是否包含 fix/hotfix/revert ── 
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5", "--format=%s"],
            capture_output=True, text=True, check=True, cwd=project_root
        )
        fix_commits = []
        for msg in result.stdout.strip().split("\n"):
            if re.search(r'\bfix\b|\bhotfix\b|\brevert\b|\bbug\b', msg, re.IGNORECASE):
                fix_commits.append(msg[:60])
        if fix_commits:
            signals.append(f"最近提交含修复记录: {'; '.join(fix_commits[:3])}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # ── 信号 3: governance_audit.py 是否在本次暂存区中被修改（新增了检查项） ──
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, check=True, cwd=project_root
        )
        if "governance_audit.py" in result.stdout:
            signals.append("governance_audit.py 被修改（可能新增了检查项 → 意味着发现了系统性缺口）")
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # ── 过滤: 如果 evolution_records 今天已有新条目，则清空信号 ──
    if signals:
        evo_path = os.path.join(project_root, ".plenipes", "evolution_records.md")
        today = datetime.now().strftime("%Y-%m-%d")
        if os.path.exists(evo_path):
            with open(evo_path, 'r', encoding='utf-8') as f:
                evo_content = f.read()
            if today in evo_content:
                # 今天已经写过教训了，取消信号
                signals = []
    
    return signals


if __name__ == "__main__":
    main()
