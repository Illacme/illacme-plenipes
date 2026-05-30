import os
from typing import Tuple, Optional

def get_secure_vault_path() -> str:
    """
    🏢 动态获取当前版图的原稿文库（Vault）的物理路径，作为 AI 模块的默认安全沙箱工作目录
    """
    from core.runtime.engine_singleton import get_global_engine
    engine = get_global_engine()
    if engine and hasattr(engine, 'config') and getattr(engine.config, 'vault_root', None):
        return os.path.abspath(engine.config.vault_root)
    return os.path.abspath("./vault")

def verify_sandbox_path(vault_path: str, target_path: str) -> bool:
    """
    🛡️ 安全沙箱锁定检查：使用 os.path.commonpath 防止任何穿越逃逸。
    确保目标绝对路径绝对限制在 secure vault_path 的子树分支中。
    """
    try:
        abs_vault = os.path.abspath(vault_path)
        abs_target = os.path.abspath(target_path)
        return os.path.commonpath([abs_vault]) == os.path.commonpath([abs_vault, abs_target])
    except Exception:
        return False

def fuzzy_match_document(vault_path: str, relative_path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    🌟 [自愈自适应路径定位]：若直接路径不存在，尝试在文稿库中进行模糊与子目录智能搜索匹配。
    参数:
        vault_path: 文稿库绝对路径
        relative_path: 待定位的相对路径或文件名
    返回:
        (matched_full_path, matched_relative_path, error_message)
        - 定位成功: 返回 (绝对路径, 规范化相对路径, None)
        - 定位失败（越界/逃逸）: 返回 (None, None, "Error: Path traversal detected...")
        - 定位失败（找到多个）: 返回 (None, None, "Error: Multiple matching files...")
        - 找不到匹配: 返回 (None, None, None)
    """
    try:
        # 1. 尝试直接拼接绝对路径
        full_path = os.path.abspath(os.path.join(vault_path, relative_path))
        
        # 如果文件直接存在，优先校验其沙箱安全性并直通返回
        if os.path.exists(full_path):
            if verify_sandbox_path(vault_path, full_path):
                return full_path, relative_path, None
            return None, None, "Error: Path traversal detected. Access denied outside the secure manuscript vault."
            
        # 2. 尝试执行模糊自愈定位与子目录智能搜索
        norm_rel = relative_path.replace("\\", "/").strip("/")
        filename = os.path.basename(norm_rel)
        if not filename.endswith('.md') and '.' not in filename:
            filename += '.md'
            
        candidates = []
        for root, dirs, files in os.walk(vault_path):
            if '.plenipes' in root or '.git' in root:
                continue
            for file in files:
                if file.lower() == filename.lower() or file.lower() == norm_rel.lower():
                    cand_path = os.path.abspath(os.path.join(root, file))
                    if verify_sandbox_path(vault_path, cand_path):
                        candidates.append(cand_path)
                        
        if len(candidates) == 1:
            matched_full = candidates[0]
            matched_rel = os.path.relpath(matched_full, vault_path)
            return matched_full, matched_rel, None
        elif len(candidates) > 1:
            rel_cands = [os.path.relpath(c, vault_path) for c in candidates]
            return None, None, f"Error: Multiple matching files found: {', '.join(rel_cands)}. Please specify the exact relative path."
            
        return None, None, None
    except Exception as e:
        return None, None, f"Error in path resolution: {str(e)}"
