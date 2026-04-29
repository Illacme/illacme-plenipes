#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme Plenipes Core - Sovereign Gateway
职责：内核语义网关。负责映射物理目录至产品主权概念。
🛡️ [V35.2]：主权语义映射层。
"""

import sys
from . import ingress as intake
from . import bindery as egress
from . import archives as archives
from . import editorial as editorial
from . import logic as engine

# 🚀 [V35.2] 动态挂载语义别名至 sys.modules，支持 import core.intake 这种写法
sys.modules['core.intake'] = intake
sys.modules['core.egress'] = egress
sys.modules['core.archives'] = archives
sys.modules['core.editorial'] = editorial
sys.modules['core.engine'] = engine

__all__ = ['intake', 'egress', 'archives', 'editorial', 'engine']
