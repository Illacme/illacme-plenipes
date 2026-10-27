#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 自动化发版说明生成器 (ReleaseNotesBuilder) 门禁测试
断言场景：
1. 提交记录智能提取与分类映射正确性 (去技术黑话)
2. 全平台下载速查表格链接有效性与中英双语结构完备性
3. 文件自动生成与防覆盖机制
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from desktop.release_notes_builder import ReleaseNotesBuilder


def test_release_notes_builder_categorization():
    """测试将技术 Commit 准确映射为创作者板块"""
    builder = ReleaseNotesBuilder(version="1.8.1", repo_root=REPO_ROOT)
    test_commits = [
        "feat(ui): 全面适配温润白天浅色模式视觉风格",
        "feat(bindery): 增强 Word 原生公式与高清封面导出",
        "feat(wechat): 自动将超链接转换为文末参考文献脚注",
        "fix(desktop): 修复 Windows 托盘图标偶发残留异常",
        "perf(core): 优化版本检测与弹窗秒开体验",
    ]

    cats = builder.categorize_commits(test_commits)
    assert "ui" in cats
    assert "bindery" in cats
    assert "syndication" in cats
    assert "fix" in cats
    assert "perf" in cats


def test_release_notes_builder_markdown_structure():
    """测试生成的 Markdown 符合创作者友好的发版文档标准规范"""
    builder = ReleaseNotesBuilder(version="1.8.1", repo_root=REPO_ROOT)
    md = builder.render_markdown()

    # 1. 断言中文版关键章节
    assert "# 🏛️ Illacme Plenipes v1.8.1 官方发版说明" in md
    assert "📦 官方客户端下载（免配环境，解压或双击即用）" in md
    assert "Illacme-Plenipes-macOS.dmg" in md
    assert "Illacme-Plenipes-Windows-x64-Setup.exe" in md
    assert "🛡️ 首次打开遇到安全提示？3 秒快速放行" in md
    assert "双击修复无法打开.command" in md
    assert "🏛️ 创作者主权初心" in md

    # 2. 断言英文版关键章节
    assert "# 🏛️ Illacme Plenipes v1.8.1 Official Release Notes (English)" in md
    assert "Official Desktop Downloads (Zero-Config, Plug & Play)" in md
    assert "The Creator Sovereignty Pledge" in md


def test_release_notes_builder_file_generation(tmp_path):
    """测试写入物理文件与防覆盖机制"""
    builder = ReleaseNotesBuilder(version="1.8.2", repo_root=REPO_ROOT)
    target = tmp_path / "v1.8.2.md"

    # 第一次正常生成
    res1 = builder.generate_file(target_path=target, force=False)
    assert res1.exists()
    content = res1.read_text(encoding="utf-8")
    assert "v1.8.2" in content

    # 第二次非强制写入应当跳过，不报错
    res2 = builder.generate_file(target_path=target, force=False)
    assert res2 == target
