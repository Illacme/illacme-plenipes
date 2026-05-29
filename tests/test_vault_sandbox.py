#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil
import pytest
from core.adapters.ai.tools.vault_tools import ReadDocumentTool, WriteDocumentTool, SearchVaultTool, get_secure_vault_path

def test_get_secure_vault_path():
    """验证安全文库工作路径的动态获取与自愈兜底"""
    path = get_secure_vault_path()
    assert os.path.isabs(path)
    assert os.path.exists(path) or path.endswith("vault")

def test_vault_tools_sandboxing():
    """
    🛡️ [安全沙箱锁定单元测试]：
    验证 ReadDocumentTool 和 WriteDocumentTool 在面对各种越界（目录穿越）调用时，
    是否能够 100% 触发 os.path.commonpath 熔断拦截，并拒绝越界读写。
    """
    read_tool = ReadDocumentTool()
    write_tool = WriteDocumentTool()
    
    # 模拟工作路径
    vault_path = get_secure_vault_path()
    
    # 1. 尝试越界读取敏感路径（相对路径穿越逃逸）
    malicious_rel_path = "../../../etc/passwd"
    read_rel_result = read_tool.execute(malicious_rel_path)
    assert "Error: Path traversal detected." in read_rel_result
    assert "Access denied" in read_rel_result

    # 2. 尝试越界读取绝对路径（系统根路径逃逸）
    malicious_abs_path = "/etc/passwd"
    read_abs_result = read_tool.execute(malicious_abs_path)
    assert "Error: Path traversal detected." in read_abs_result
    assert "Access denied" in read_abs_result

    # 3. 尝试越界覆盖写入敏感文件
    write_rel_result = write_tool.execute(malicious_rel_path, "malicious payload")
    assert "Error: Path traversal detected." in write_rel_result
    assert "Access denied" in write_rel_result

    write_abs_result = write_tool.execute(malicious_abs_path, "malicious payload")
    assert "Error: Path traversal detected." in write_abs_result
    assert "Access denied" in write_abs_result

    # 4. 验证正常读写操作（在沙箱内部）
    test_file_path = "Docs/sandbox_test_file.md"
    test_content = "# Test Sandbox\nThis file is safely inside the vault sandbox."
    
    # 正常写入
    write_ok = write_tool.execute(test_file_path, test_content)
    assert "Successfully wrote" in write_ok
    
    # 正常读取
    read_ok = read_tool.execute(test_file_path)
    assert read_ok == test_content
    
    # 清理测试写入的正常文件
    full_test_file = os.path.join(vault_path, test_file_path)
    if os.path.exists(full_test_file):
        os.remove(full_test_file)
