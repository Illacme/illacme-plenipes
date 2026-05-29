import os
import json
from typing import Dict, Any

from core.adapters.ai.tool_protocol import IllacmeTool

def get_secure_vault_path() -> str:
    """
    🏢 动态获取当前版图的原稿文库（Vault）的物理路径，作为 AI 模块的默认安全沙箱工作目录
    """
    from core.runtime.engine_singleton import get_global_engine
    engine = get_global_engine()
    if engine and hasattr(engine, 'config') and getattr(engine.config, 'vault_root', None):
        return os.path.abspath(engine.config.vault_root)
    return os.path.abspath("./vault")

class ReadDocumentTool(IllacmeTool):
    """
    🏢 [V75.0] 读取原稿库中的文档内容（防越界审计安全沙箱版）
    """
    name = "read_document"
    description = "Read the full markdown content of a specified document in the vault by its relative path. Use this tool immediately when the user asks to read, open, view, print, or get the contents of a specific file."
    
    def __init__(self):
        super().__init__(
            name=self.name,
            description=self.description,
            parameters=self.get_parameters_schema()
        )
    
    @classmethod
    def get_parameters_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "relative_path": {
                    "type": "string",
                    "description": "The relative path of the markdown file within the vault. Example: 'Index/Showcase.md' or 'Docs/getting-started.md'"
                }
            },
            "required": ["relative_path"]
        }

    def execute(self, relative_path: str) -> str:
        try:
            vault_path = get_secure_vault_path()
            
            # 尝试直接拼接与规范化绝对路径
            full_path = os.path.abspath(os.path.join(vault_path, relative_path))
            
            # 🌟 [自愈自适应路径定位]：若直接路径不存在，尝试在文稿库中进行模糊与子目录智能搜索匹配
            if not os.path.exists(full_path):
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
                            # 确保候选路径安全地处于沙箱根目录内
                            if os.path.commonpath([vault_path]) == os.path.commonpath([vault_path, cand_path]):
                                candidates.append(cand_path)
                
                if len(candidates) == 1:
                    full_path = candidates[0]
                    relative_path = os.path.relpath(full_path, vault_path)
                elif len(candidates) > 1:
                    rel_cands = [os.path.relpath(c, vault_path) for c in candidates]
                    return f"Error: Multiple matching files found: {', '.join(rel_cands)}. Please specify the exact relative path."
            
            # 🛡️ 安全沙箱锁定检查：使用 os.path.commonpath 防止任何穿越逃逸
            if os.path.commonpath([vault_path]) != os.path.commonpath([vault_path, full_path]):
                return "Error: Path traversal detected. Access denied outside the secure manuscript vault."
                
            if not os.path.exists(full_path):
                return f"Error: File '{relative_path}' not found."
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"

class SearchVaultTool(IllacmeTool):
    """
    🏢 [V75.0] 在原稿库中搜索关键字（锁定在安全沙箱内）
    """
    name = "search_vault"
    description = "Search for a specific keyword across all markdown documents in the vault. Returns a list of matching file paths. Do NOT use this tool if the user explicitly wants to read, view, or open a specific document; use read_document instead."
    
    def __init__(self):
        super().__init__(
            name=self.name,
            description=self.description,
            parameters=self.get_parameters_schema()
        )
    
    @classmethod
    def get_parameters_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "The search term or keyword to look for."
                }
            },
            "required": ["keyword"]
        }

    def execute(self, keyword: str) -> str:
        try:
            vault_path = get_secure_vault_path()
            matches = []
            for root, dirs, files in os.walk(vault_path):
                # 排除系统目录
                if '.plenipes' in root or '.git' in root:
                    continue
                for file in files:
                    if file.endswith('.md'):
                        full_path = os.path.abspath(os.path.join(root, file))
                        # 🛡️ 安全沙箱锁定检查
                        if os.path.commonpath([vault_path]) != os.path.commonpath([vault_path, full_path]):
                            continue
                        try:
                            with open(full_path, 'r', encoding='utf-8') as f:
                                if keyword.lower() in f.read().lower():
                                    rel_path = os.path.relpath(full_path, vault_path)
                                    matches.append(rel_path)
                        except:
                            pass
                            
            if not matches:
                return f"No documents found containing the keyword '{keyword}'."
            return "Found matching documents:\n" + "\n".join(matches)
        except Exception as e:
            return f"Error searching vault: {str(e)}"

class WriteDocumentTool(IllacmeTool):
    """
    🏢 [V75.0] 覆盖写入原稿库中的文档（防越界审计安全沙箱版）
    """
    name = "write_document"
    description = "Write or overwrite markdown content to a specific file path in the vault. Will create directories if they don't exist."
    
    def __init__(self):
        super().__init__(
            name=self.name,
            description=self.description,
            parameters=self.get_parameters_schema()
        )
    
    @classmethod
    def get_parameters_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "relative_path": {
                    "type": "string",
                    "description": "The relative path to save the file as. Example: 'ProjectX/NewFile.md'"
                },
                "content": {
                    "type": "string",
                    "description": "The full markdown content to write into the file."
                }
            },
            "required": ["relative_path", "content"]
        }

    def execute(self, relative_path: str, content: str) -> str:
        try:
            vault_path = get_secure_vault_path()
            full_path = os.path.abspath(os.path.join(vault_path, relative_path))
            
            # 🛡️ 安全沙箱锁定检查：使用 os.path.commonpath 严禁写越界
            if os.path.commonpath([vault_path]) != os.path.commonpath([vault_path, full_path]):
                return "Error: Path traversal detected. Access denied outside the secure manuscript vault."
                
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote {len(content)} characters to '{relative_path}'."
        except Exception as e:
            return f"Error writing file: {str(e)}"
