#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes - Test suite for log_healer.py (逻辑演进日志自愈脚本测试)
"""
import os
import re
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from datetime import datetime

from scripts.log_healer import (
    get_staged_files,
    parse_metadata,
    parse_log_entry,
    heal_log
)

def test_get_staged_files():
    """测试获取已暂存或已修改的文件列表"""
    # Mock subprocess.run
    with patch("subprocess.run") as mock_run, patch("os.path.exists", return_value=True):
        # 1. 模拟有暂存文件
        mock_run.return_value = MagicMock(returncode=0, stdout="core/logic/ai/rate_limit_shield.py\ntests/test_log_healer.py\n")
        staged = get_staged_files()
        assert len(staged) == 2
        assert "core/logic/ai/rate_limit_shield.py" in staged
        
        # 2. 模拟无暂存，回退到工作区改动
        # 第一次调用返回空，第二次调用返回工作区改动
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=""),
            MagicMock(returncode=0, stdout="core/logic/sitemap_engine.py\n")
        ]
        staged_fallback = get_staged_files()
        assert len(staged_fallback) == 1
        assert "core/logic/sitemap_engine.py" in staged_fallback

def test_parse_metadata():
    """测试从模拟 walkthrough.md 提取并清洗元数据"""
    temp_dir = tempfile.mkdtemp()
    try:
        walkthrough_content = (
            "# Walkthrough - P1, P2 & P3 Iterative Summary\n\n"
            "一些前导说明文字，不属于 Rationale\n\n"
            "---\n\n"
            "## 🚨 P1: SQLite 并发与锁保护 (安全性保障)\n\n"
            "为了彻底解决多协程并发对 SQLite 的死锁锁死隐患，本阶段引入了互斥锁。\n\n"
            "### 变更细节\n"
            "- **并发隔离重构**：修改了 [audit_ledger.py](file:///path/to/audit_ledger.py)，实现了重入锁。\n"
            "- **测试套件扩容**：新建了并发测试 [test_ledger_concurrency.py](file:///path/to/test_ledger_concurrency.py)。\n\n"
            "## 🧪 验证结果\n\n"
            "- pytest 单元测试 280 个用例全部通过。\n"
            "- sovereign_audit.py 审计无违规。\n"
        )
        
        walkthrough_path = os.path.join(temp_dir, "walkthrough.md")
        with open(walkthrough_path, "w", encoding="utf-8") as f:
            f.write(walkthrough_content)
            
        staged_files = ["core/governance/audit_ledger.py", "tests/test_ledger_concurrency.py"]
        title, actions, rationale, evidence = parse_metadata(temp_dir, staged_files)
        
        assert title == "P1, P2 & P3 Iterative Summary"
        assert len(actions) == 2
        # 检查是否成功清洗了绝对路径 file:/// 链接
        assert actions[0] == "1. **并发隔离重构**：修改了 audit_ledger.py，实现了重入锁。"
        assert actions[1] == "2. **测试套件扩容**：新建了并发测试 test_ledger_concurrency.py。"
        
        assert "为了彻底解决多协程并发对 SQLite 的死锁锁死隐患" in rationale
        assert "pytest 单元测试 280 个用例全部通过" in evidence
        assert "sovereign_audit.py 审计无违规" in evidence
    finally:
        shutil.rmtree(temp_dir)

def test_parse_log_entry():
    """测试从单条演进日志中精确反解字段"""
    entry_text = (
        "## [2026-06-23] 智能网关限流 / 并发防护 (SOP-01 & SOP-02)\n"
        "- **ACTION**:\n"
        "  1. 重构了连接池隔离。\n"
        "  2. 新增了滑动窗口限流核心。\n"
        "- **RATIONALE**: 解决瞬时超限 429 崩溃隐患。\n"
        "- **IMPACT**: core/logic/ai/rate_limit_shield.py, tests/test_rate_limit_governance.py\n"
        "- **EVIDENCE**: 单元测试 8 passed 绿灯。\n"
    )
    title, actions, rationale, impact, evidence = parse_log_entry(entry_text)
    
    assert title == "智能网关限流 / 并发防护"
    assert len(actions) == 2
    assert actions[0] == "重构了连接池隔离。"
    assert actions[1] == "新增了滑动窗口限流核心。"
    assert rationale == "解决瞬时超限 429 崩溃隐患。"
    assert len(impact) == 2
    assert "core/logic/ai/rate_limit_shield.py" in impact
    assert evidence == "单元测试 8 passed 绿灯。"

def test_heal_log_integration():
    """测试日志原地回写与今日同日合并功能"""
    temp_dir = tempfile.mkdtemp()
    try:
        log_file = os.path.join(temp_dir, "logic_evolution.log")
        
        # 1. 模拟初始空文件或未创建状态的第一次写入
        title1 = "首次大版本迭代"
        actions1 = ["1. 新建了 app.py 入口。"]
        rationale1 = "建立服务主流程。"
        evidence1 = "手动验证通过。"
        staged1 = ["app.py"]
        
        # Mock log_path 指向临时测试文件
        with patch("scripts.log_healer.os.path.exists", return_value=True), \
             patch("scripts.log_healer.open", create=True) as mock_open:
            
            # 使用临时文件测试真实的读写
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("# Header\n\n---\n")
                
            # 执行 heal_log
            # 我们通过改写 log_path 变量来测试实际写入
            # 由于 heal_log 中写死了 log_path = ".plenipes/history/logic_evolution.log"，
            # 我们可以在测试中直接 mock 该方法里的本地变量或局部路径。
            # 为了能够对物理文件进行读写，我们直接在 heal_log 内部对文件进行 mock 代理
            # 或者干脆用 patch 包装 open 以读写本地文件：
            
            # 定义一个真实的本地读写 proxy
            def open_file_proxy(path, mode="r", *args, **kwargs):
                return open(log_file, mode, *args, **kwargs)
                
            with patch("scripts.log_healer.open", side_effect=open_file_proxy):
                # 写入第一条（今天）
                heal_log(title1, actions1, rationale1, evidence1, staged1)
                
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                today_str = datetime.now().strftime("%Y-%m-%d")
                assert today_str in content
                assert title1 in content
                assert "app.py" in content
                
                # 2. 模拟第二次同日自愈合并
                title2 = "第二阶段微调"
                actions2 = ["2. 优化了 app.py 的路由配置。"]
                rationale2 = "补充性能配置。"
                evidence2 = "pytest regression passed。"
                staged2 = ["app.py", "config.py"]
                
                heal_log(title2, actions2, rationale2, evidence2, staged2)
                
                with open(log_file, "r", encoding="utf-8") as f:
                    merged_content = f.read()
                    
                # 校验是否合并成功
                assert today_str in merged_content
                # 标题是否合并
                assert "首次大版本迭代 / 第二阶段微调" in merged_content
                # 动作是否合并去重
                assert "1. 新建了 app.py 入口。" in merged_content
                assert "2. 优化了 app.py 的路由配置。" in merged_content
                # Rationale 拼接
                assert "建立服务主流程。 补充性能配置。" in merged_content
                # Impact 去重合并
                assert "app.py, config.py" in merged_content
                # Evidence 拼接
                assert "手动验证通过。 pytest regression passed。" in merged_content
    finally:
        shutil.rmtree(temp_dir)

def test_sentinel_matrix_auto_heal():
    """验证治理哨兵 sentinel_matrix.py 遇到缺失日志时自动触发自愈并放行"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("sentinel_matrix", ".plenipes/tools/sentinel_matrix.py")
    sentinel_matrix = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sentinel_matrix)
    audit_observability = sentinel_matrix.audit_observability
    
    # 模拟今天有和没有日志的情况，以及 log_healer 的调用
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", create=True) as mock_open, \
         patch("subprocess.run") as mock_run:
        
        # 1. 第一次调用 check_log() 返回今天不存在，在自愈后第二次返回存在
        # 模拟 read 结果：第一次不含今日日期，第二次包含今日日期
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        mock_file = MagicMock()
        mock_file.read.side_effect = [
            "Old entry\n",           # check_log() #1
            f"## [{today_str}] ...",   # check_log() #2
            f"## [{today_str}] ...",   # 校验 mentions 读内容
        ]
        mock_open.return_value.__enter__.return_value = mock_file
        
        # 模拟 log_healer.py 执行成功
        mock_run.return_value = MagicMock(returncode=0, stdout="Success")
        
        # 执行审计，验证它应当能顺利自愈并返回 True
        staged_files = ["core/logic/ai/rate_limit_shield.py"]
        passed = audit_observability(staged_files)
        
        assert passed is True
        mock_run.assert_called_once()
        # 校验它调用的是 scripts/log_healer.py
        cmd_args = mock_run.call_args[0][0]
        assert "scripts/log_healer.py" in cmd_args

