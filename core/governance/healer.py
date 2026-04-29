"""
💊 自愈引擎 — 自动化资产修复与降级恢复。
基于审计结果自动执行缓存重建、断链修复与配置回滚。
"""
# -*- coding: utf-8 -*-
import glob
import re
from typing import List

class CodeHealer:
    """🚀 [V24.6] 物理代码自愈器"""
    
    @staticmethod
    def auto_heal_loggers() -> List[str]:
        """物理扫描并替换旧版 Logger (正则驱动)"""
        healed = []
        # 扫描核心与适配器目录
        for f in glob.glob("core/**/*.py", recursive=True) + glob.glob("adapters/**/*.py", recursive=True):
            if "tracing.py" in f or "doctor.py" in f or "__pycache__" in f: continue

            try:
                with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()

                modified = False
                # 1. 替换导入语句
                if "import logging" in content and "from core.utils.tracing import tlog" not in content:
                    content = content.replace("import logging", "import logging\nfrom core.utils.tracing import tlog")
                    modified = True

                # 2. 替换实例初始化
                pattern = re.compile(r'logger\s*=\s*logging\.getLogger\(.*?\)')
                if pattern.search(content):
                    content = pattern.sub("logger = tlog", content)
                    modified = True

                if modified:
                    with open(f, 'w', encoding='utf-8') as fp:
                        fp.write(content)
                    healed.append(f"🩹 [Auto-Healer] 已物理修复代码追踪点: {f}")
            except Exception: pass

        return healed
