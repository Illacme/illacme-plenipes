#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Ingress Plugin - Git Repository Source
职责：负责从 Git 仓库拉取并读取数据。
🛡️ [V16.0] 原生同步：支持直接翻译 Git 分支内容。
"""
from typing import Iterator
from core.ingress.base import BaseSource

class GitRepositorySource(BaseSource):
    """🚀 [V16.0] Git 仓库数据源 (占位实现)"""
    
    def __init__(self, repo_url: str, branch: str = "main"):
        self.repo_url = repo_url
        self.branch = branch

    def list_files(self) -> Iterator[str]:
        # [Sovereignty] GitPython 集成已在路线图中，暂回退至空迭代以保持管线纯净
        return iter([])

    def read_content(self, rel_path: str) -> str:
        return ""

    def get_mtime(self, rel_path: str) -> float:
        return 0.0
