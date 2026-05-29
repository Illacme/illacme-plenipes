import os
import json
from typing import Dict, Any

from core.adapters.ai.tool_protocol import IllacmeTool
# 假设我们可以通过全局对象获取 vault 实例。为了不引入循环依赖，我们采用动态获取策略。
# 系统一般将核心引擎实例挂载在某处，这里先用最基础的文件系统操作，后续可以对齐到 Archives/Ledger 引擎

class ReadDocumentTool(IllacmeTool):
    """
    🏢 [V75.0] 读取原稿库中的文档内容
    """
    name = "read_document"
    description = "Read the full markdown content of a specified document in the vault by its relative path."
    
    @classmethod
    def get_parameters_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "relative_path": {
                    "type": "string",
                    "description": "The relative path of the markdown file within the vault. Example: 'ProjectX/README.md'"
                }
            },
            "required": ["relative_path"]
        }

    def execute(self, relative_path: str) -> str:
        try:
            # 简化版：直接从全局配置取 vault 路径
            from core.config.settings import Settings
            settings = Settings()
            vault_path = settings.get("vault_path", "./vault")
            
            full_path = os.path.join(vault_path, relative_path)
            
            # 安全检查：防止目录穿越
            if not os.path.abspath(full_path).startswith(os.path.abspath(vault_path)):
                return "Error: Path traversal detected. Access denied."
                
            if not os.path.exists(full_path):
                return f"Error: File '{relative_path}' not found."
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"

class SearchVaultTool(IllacmeTool):
    """
    🏢 [V75.0] 在原稿库中搜索关键字
    """
    name = "search_vault"
    description = "Search for a specific keyword across all markdown documents in the vault. Returns a list of matching file paths."
    
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
            from core.config.settings import Settings
            settings = Settings()
            vault_path = settings.get("vault_path", "./vault")
            
            matches = []
            for root, dirs, files in os.walk(vault_path):
                # 排除系统目录
                if '.plenipes' in root or '.git' in root:
                    continue
                for file in files:
                    if file.endswith('.md'):
                        full_path = os.path.join(root, file)
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
    🏢 [V75.0] 覆盖写入原稿库中的文档
    """
    name = "write_document"
    description = "Write or overwrite markdown content to a specific file path in the vault. Will create directories if they don't exist."
    
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
            from core.config.settings import Settings
            settings = Settings()
            vault_path = settings.get("vault_path", "./vault")
            
            full_path = os.path.join(vault_path, relative_path)
            
            # 安全检查
            if not os.path.abspath(full_path).startswith(os.path.abspath(vault_path)):
                return "Error: Path traversal detected. Access denied."
                
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return f"Successfully wrote {len(content)} characters to '{relative_path}'."
        except Exception as e:
            return f"Error writing file: {str(e)}"
