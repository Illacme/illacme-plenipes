import os
from typing import Dict, Any

from core.adapters.ai.tool_protocol import IllacmeTool
from core.adapters.ai.tools.vault_service import (
    get_secure_vault_path,
    verify_sandbox_path,
    fuzzy_match_document
)

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
            
            # 🌟 智能平移：调用公共沙箱服务层的模糊自愈路径定位算法
            full_path, resolved_rel, err_msg = fuzzy_match_document(vault_path, relative_path)
            if err_msg:
                return err_msg
                
            if not full_path:
                # 若完全找不到，需首先校验入参的沙箱安全性以阻断恶意逃逸，再行报错
                raw_path = os.path.abspath(os.path.join(vault_path, relative_path))
                if not verify_sandbox_path(vault_path, raw_path):
                    return "Error: Path traversal detected. Access denied outside the secure manuscript vault."
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
                        # 🛡️ 智能平移：安全沙箱物理边界校验，防止逃逸穿越
                        if not verify_sandbox_path(vault_path, full_path):
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
    description = "Write or overwrite markdown content to a specific file path in the vault. WARNING: NEVER use this tool to modify, edit, or append to an existing file that is longer than 30 lines, as it will easily exceed the output token limit and trigger truncation. You MUST use patch_document for modifying existing files instead."
    
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
            
            # 🛡️ 智能平移：调用公共服务层，防逃逸安全越界沙箱检查
            if not verify_sandbox_path(vault_path, full_path):
                return "Error: Path traversal detected. Access denied outside the secure manuscript vault."
                
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote {len(content)} characters to '{relative_path}'."
        except Exception as e:
            return f"Error writing file: {str(e)}"

class PatchDocumentTool(IllacmeTool):
    """
    🏢 [V75.0] 微创增量修改原稿库中的文档（防越界审计安全沙箱及 Token 节约版）
    """
    name = "patch_document"
    description = "Apply a search-and-replace patch to a specific document in the vault. You MUST prioritize using this tool instead of write_document whenever you are modifying, editing, or appending to any existing file, in order to prevent output truncation, preserve token space, and guarantee write safety."
    
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
                },
                "search_content": {
                    "type": "string",
                    "description": "The exact block of text in the original file to be replaced. MUST match the original text exactly, including whitespace and line breaks."
                },
                "replace_content": {
                    "type": "string",
                    "description": "The new block of text to replace the search_content."
                }
            },
            "required": ["relative_path", "search_content", "replace_content"]
        }

    def execute(self, relative_path: str, search_content: str, replace_content: str) -> str:
        try:
            vault_path = get_secure_vault_path()
            
            # 🌟 智能平移：调用公共沙箱服务层的模糊自愈路径定位算法
            full_path, resolved_rel, err_msg = fuzzy_match_document(vault_path, relative_path)
            if err_msg:
                return err_msg
                
            if not full_path:
                # 若完全找不到，需首先校验入参的沙箱安全性以阻断恶意逃逸，再行报错
                raw_path = os.path.abspath(os.path.join(vault_path, relative_path))
                if not verify_sandbox_path(vault_path, raw_path):
                    return "Error: Path traversal detected. Access denied outside the secure manuscript vault."
                return f"Error: File '{relative_path}' not found."
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if not search_content:
                return "Error: 'search_content' cannot be empty. If you want to overwrite the entire file, use write_document."
                
            occurrences = content.count(search_content)
            if occurrences == 0:
                return "Error: 'search_content' not found in the document. Please ensure it matches the original text exactly (including indentation and line breaks)."
            elif occurrences > 1:
                return "Error: 'search_content' matches multiple blocks in the document. Please provide more surrounding lines of context to make it unique."
                
            new_content = content.replace(search_content, replace_content, 1)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            return f"Successfully patched '{resolved_rel}'. Replaced {len(search_content)} characters with {len(replace_content)} characters."
        except Exception as e:
            return f"Error patching file: {str(e)}"

