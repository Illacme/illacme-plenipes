#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes - Physical Constants
职责：定义全域主权路径、文件名等底层物理常量，作为系统依赖的最底层。
🛡️ [V66.0] 基石模块：解除循环依赖的物理核心。
"""

import os

# 1. 目录结构常量
CONFIG_DIR = "configs"
METADATA_DIR = "metadata"
IMPRINT_DIR = "imprints"
THEMES_DIR = "themes"
DIST_DIR = "dist"
PROMPTS_TEMPLATES_DIR = "prompts_templates"
DIALECTS_DIR = "dialects"

# 2. 配置文件名常量
CONFIG_NAME = "config.yaml"
CONFIG_LOCAL_NAME = "config.local.yaml"
CONFIG_IMPRINT_NAME = "config.imprint.yaml"

# 3. 运行时常量
LOGS_DIR = "runtime/logs"
CACHE_DIR = "runtime/cache"
MAIN_LOG_NAME = "plenipes.log"

# 4. 方言与提示词常量
PROMPTS_NAME = "prompts.yaml"
DEFAULT_DIALECT_NAME = "default.yaml"
