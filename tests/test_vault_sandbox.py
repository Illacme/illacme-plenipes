#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil
from core.adapters.ai.tools.vault_tools import ReadDocumentTool, WriteDocumentTool, get_secure_vault_path

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
    
    # 5. 验证自愈路径定位功能（模糊/不完整相对路径读取）
    read_healed_1 = read_tool.execute("sandbox_test_file")
    assert read_healed_1 == test_content
    
    read_healed_2 = read_tool.execute("sandbox_test_file.md")
    assert read_healed_2 == test_content
    
    # 清理测试写入的正常文件
    full_test_file = os.path.join(vault_path, test_file_path)
    if os.path.exists(full_test_file):
        os.remove(full_test_file)


def test_vault_service_functions():
    """
    🏢 独立校验 vault_service 核心模块的单元健壮性
    """
    from core.adapters.ai.tools.vault_service import verify_sandbox_path, fuzzy_match_document, get_secure_vault_path
    
    vault_path = get_secure_vault_path()
    
    # 1. 验证 verify_sandbox_path
    assert verify_sandbox_path(vault_path, os.path.join(vault_path, "Docs/test.md")) is True
    assert verify_sandbox_path(vault_path, "/etc/passwd") is False
    assert verify_sandbox_path(vault_path, "../etc/passwd") is False
    
    # 2. 验证 fuzzy_match_document - 正常匹配和自愈
    test_sub_dir = os.path.join(vault_path, "SubTest")
    os.makedirs(test_sub_dir, exist_ok=True)
    test_file_path = os.path.join(test_sub_dir, "unique_filename_test.md")
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("hello")
        
    try:
        # A. 直接路径存在时的直通匹配
        f_path, r_path, err = fuzzy_match_document(vault_path, "SubTest/unique_filename_test.md")
        assert err is None
        assert f_path == test_file_path
        assert r_path == "SubTest/unique_filename_test.md"
        
        # B. 路径不存在且只有一个同名文件时的自愈智能路径校正
        f_path_2, r_path_2, err_2 = fuzzy_match_document(vault_path, "unique_filename_test")
        assert err_2 is None
        assert f_path_2 == test_file_path
        assert r_path_2 == "SubTest/unique_filename_test.md"
        
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        if os.path.exists(test_sub_dir):
            shutil.rmtree(test_sub_dir)
