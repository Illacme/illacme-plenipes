import os
import re
from .base import galaxy

@galaxy(5)
def check_history_artifacts_completeness(audit):
    """[AEL-Iter-012] 检查 .plenipes/history/ 历史迭代的三相基因完备性"""
    history_path = ".plenipes/history"
    if not os.path.isdir(history_path):
        audit.fail("历史归档目录", f"{history_path} 不存在")
        return
    
    incomplete_dirs = []
    for entry in os.listdir(history_path):
        full = os.path.join(history_path, entry)
        if os.path.isdir(full) and entry.startswith("2026-"):
            files = os.listdir(full)
            has_plan = "plan.md" in files or "implementation_plan.md" in files
            has_task = "task.md" in files
            has_walk = "walkthrough.md" in files or "acceptance.md" in files
            
            if not (has_plan and has_task and has_walk):
                incomplete_dirs.append(entry)
                
    if incomplete_dirs:
        audit.fail("历史迭代矩阵不完整", f"发现 {len(incomplete_dirs)} 个迭代目录缺少 plan/task/walkthrough 三相文件: {', '.join(incomplete_dirs[:3])}...")
    else:
        audit.ok("历史归档完整性", "所有 history/ 迭代目录均已严格沉淀三相规划基因")

@galaxy(5)
def check_evolution_records_freshness(audit):
    """[AEL-Iter-006] 检查 evolution_records.md 是否在最近 24 小时内有更新"""
    evo_file = ".plenipes/evolution_records.md"
    if not os.path.isfile(evo_file):
        audit.fail("进化记录缺失", f"{evo_file} 不存在")
        return
    
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    with open(evo_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if today in content:
            audit.ok("项目进化记录", f"最近更新日期: {today}")
        else:
            audit.warn("项目进化记录", "今日尚未沉淀演化记录")

@galaxy(5)
def check_history_language_sovereignty(audit):
    """[AEL-Iter-v5.0] 过程文档语言主权审计：确保 Plan/Task/Walkthrough 使用中文"""
    history_dir = ".plenipes/history"
    if not os.path.exists(history_dir):
        return
    dirs = sorted([d for d in os.listdir(history_dir) if os.path.isdir(os.path.join(history_dir, d))], reverse=True)
    if not dirs:
        return
    
    latest_dir = os.path.join(history_dir, dirs[0])
    files = ["implementation_plan.md", "task.md", "walkthrough.md"]
    violations = []
    for f_name in files:
        f_path = os.path.join(latest_dir, f_name)
        if os.path.exists(f_path):
            try:
                with open(f_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not re.search(r'[\u4e00-\u9fa5]', content):
                        violations.append(f_name)
            except Exception:
                pass
                
    if violations:
        audit.fail("过程文档语言主权", f"迭代目录 {dirs[0]} 中的以下文件缺少中文内容: {', '.join(violations)}")
    else:
        audit.ok("过程文档语言主权", f"迭代目录 {dirs[0]} 已对齐中文语言主权")

@galaxy(5)
def check_task_completion_status(audit):
    """[AEL-Iter-v5.0] 任务核销闭环审计：检查最近 3 个迭代的任务清单是否已全部核销"""
    history_dir = ".plenipes/history"
    if not os.path.exists(history_dir):
        return
    dirs = sorted([d for d in os.listdir(history_dir) if os.path.isdir(os.path.join(history_dir, d))], reverse=True)
    if not dirs:
        return
    
    # 追溯最近 3 个迭代的任务核销情况
    for i in range(min(3, len(dirs))):
        dir_name = dirs[i]
        task_file = os.path.join(history_dir, dir_name, "task.md")
        
        if not os.path.exists(task_file):
            audit.warn("任务核销审计", f"迭代 {dir_name} 缺失 task.md")
            continue
            
        with open(task_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pending = re.findall(r'- \[ \]', content)
        if pending:
            audit.fail("任务核销审计", f"迭代 {dir_name} 中存在 {len(pending)} 个未完成任务")
        else:
            # 只在最新的迭代输出 OK 信号，避免日志爆炸
            if i == 0:
                audit.ok("任务核销审计", f"迭代 {dir_name} 任务清单已 100% 核销")

@galaxy(5)
def check_history_docs_depth(audit):
    """[Sentinel] 迭代文档深度审计：拦截敷衍了事的计划与验收记录。"""
    history_dir = ".plenipes/history"
    if not os.path.exists(history_dir):
        return

    dirs = sorted([d for d in os.listdir(history_dir) if os.path.isdir(os.path.join(history_dir, d))], reverse=True)
    if not dirs:
        return
    
    # 审计最近 3 个迭代，防止通过“闪击提交”绕过深度检查
    for i in range(min(3, len(dirs))):
        target_dir = os.path.join(history_dir, dirs[i])
        
        # 1. 审计计划深度 (Plan)
        plan_files = ["implementation_plan.md", "plan.md"]
        _check_single_doc_depth(target_dir, plan_files, "规划深度审计", 400, audit, dirs[i])
        
        # 2. 审计验收深度 (Walkthrough)
        walk_files = ["walkthrough.md", "acceptance.md"]
        _check_single_doc_depth(target_dir, walk_files, "验收深度审计", 300, audit, dirs[i])

def _check_single_doc_depth(target_dir, filenames, label, min_len, audit, dir_name):
    found_file = None
    for f in filenames:
        path = os.path.join(target_dir, f)
        if os.path.exists(path):
            found_file = path
            break
    
    if not found_file:
        audit.warn(label, f"迭代 {dir_name} 缺失 {filenames[0]}")
        return

    with open(found_file, "r", encoding="utf-8") as f:
        content = f.read()
        # 排除 Markdown 标题和元数据，计算净内容长度
        clean_content = re.sub(r'#.*|---.*---|`.*`|\n', '', content, flags=re.DOTALL)
        
        if len(content) < min_len:
            audit.fail(label, f"{dir_name}/{os.path.basename(found_file)} 内容过短 (当前 {len(content)} 字)，疑似敷衍占位。")
        else:
            # 只在最新的迭代输出 OK 信号，避免日志爆炸
            if dir_name == sorted(os.listdir(".plenipes/history"), reverse=True)[0]:
                audit.ok(label, f"迭代 {dir_name} {os.path.basename(found_file)} 深度达标 ({len(content)} 字符)")

@galaxy(5)
def check_roadmap_freshness(audit):
    """[AEL-Iter-010] 检查 ROADMAP.md 是否在最近 3 天内有更新"""
    roadmap_file = ".plenipes/ROADMAP.md"
    if not os.path.isfile(roadmap_file):
        audit.ok("ROADMAP 检查", "跳过（非强制文件）")
        return
        
    import time
    mtime = os.path.getmtime(roadmap_file)
    days_diff = (time.time() - mtime) / (24 * 3600)
    if days_diff < 3:
        audit.ok("ROADMAP 新鲜度", f".plenipes/ROADMAP.md 最近 {int(days_diff)} 天内有更新")
    else:
        audit.warn("ROADMAP 建议更新", f".plenipes/ROADMAP.md 已有 {int(days_diff)} 天未更新")

@galaxy(5)
def check_config_reference_alignment(audit):
    """[Industrial] 配置-参考手册对齐审计：确保所有配置项在 REFERENCE.md 中均有定义"""
    config_file = "core/config.py"
    ref_file = "docs/REFERENCE.zh-CN.md"
    
    if not os.path.exists(config_file) or not os.path.exists(ref_file):
        return

    # 1. 提取 config.py 中的配置键名 (简单正则匹配，覆盖大部分字段)
    with open(config_file, 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    # 匹配 self.key = value 风格的定义
    keys = re.findall(r'self\.([a-z0-9_]+)\s*=', config_content)
    # 过滤掉一些私有变量
    keys = [k for k in set(keys) if not k.startswith('_') and len(k) > 3]
    
    # 2. 检查 REFERENCE.md
    with open(ref_file, 'r', encoding='utf-8') as f:
        ref_content = f.read()
    
    missing = [k for k in keys if k not in ref_content]
    
    # 排除一些已知的无需文档化的变量
    ignore_keys = ['config', 'trans_cfg', 'logger', 'timeout']
    missing = [k for k in missing if k not in ignore_keys]
    
    if missing:
        audit.warn("配置参考对齐", f"以下配置项在 REFERENCE.md 中缺失文档定义: {', '.join(missing)}")
    else:
        audit.ok("配置参考对齐", "REFERENCE.md 已覆盖所有核心配置项定义")
