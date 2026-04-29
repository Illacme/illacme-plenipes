#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Ingress Plugin - Local File Source
职责：负责从本地文件系统读取原始数据。
"""
import os
from typing import Iterator
from core.ingress.base import BaseSource

class LocalFileSource(BaseSource):
    """🚀 [V16.0] 本地文件系统数据源"""
    
    def __init__(self, root_path: str):
        self.root_path = os.path.abspath(root_path)

    def list_files(self) -> Iterator[str]:
        """递归遍历本地目录，返回相对路径"""
        for root, _, files in os.walk(self.root_path):
            for file in files:
                abs_path = os.path.join(root, file)
                yield os.path.relpath(abs_path, self.root_path)

    def read_content(self, rel_path: str) -> str:
        abs_path = os.path.join(self.root_path, rel_path)
        with open(abs_path, 'r', encoding='utf-8') as f:
            return f.read()

    def get_mtime(self, rel_path: str) -> float:
        abs_path = os.path.join(self.root_path, rel_path)
        return os.path.getmtime(abs_path)
