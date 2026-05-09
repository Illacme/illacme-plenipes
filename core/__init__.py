#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Sovereign Gateway & Version Hub
职责：内核语义网关与全局真理源。负责映射物理目录至产品主权概念，并管理全域版本号。
🛡️ [V50.3]：主权语义映射层 + 全局版本控制器。
"""

import sys
from . import ingress as intake
from . import bindery as egress
from . import archives as archives
from . import editorial as editorial
from . import logic as engine

# 🚀 [V50.3] 全局版本真理源
__version__ = "50.3"
__edition__ = "Industrial-Sovereignty (工业主权版)"
__status__ = "Production-Ready"

# 🚀 [V35.2] 动态挂载语义别名至 sys.modules，支持 import core.intake 这种写法
sys.modules['core.intake'] = intake
sys.modules['core.egress'] = egress
sys.modules['core.archives'] = archives
sys.modules['core.editorial'] = editorial
sys.modules['core.engine'] = engine

__all__ = ['intake', 'egress', 'archives', 'editorial', 'engine', '__version__', '__edition__', '__status__']
