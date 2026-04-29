#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Env Loader
模块职责：负责从 .env 文件加载环境变量。
"""

import os
from core.utils.tracing import tlog

def load_dotenv(dotenv_path=".env"):
    """极简 .env 加载实现，不依赖第三方库"""
    if not os.path.exists(dotenv_path):
        return

    try:
        with open(dotenv_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")

                    if key not in os.environ:
                        os.environ[key] = value
        tlog.debug(f"🔑 [环境引擎] 已从 {dotenv_path} 加载本地秘密。")
    except Exception as e:
        tlog.warning(f"⚠️ [环境引擎] 加载 .env 失败: {e}")
