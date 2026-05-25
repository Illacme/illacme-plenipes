# -*- coding: utf-8 -*-
"""
🛡️ 前向兼容导入垫片 (Bridge Shim)
职责：将旧有的 core.ui.web.wizard_server 路径的导入透明转发至服务层，保障系统的业务稳定与平滑过渡。
"""
from services.wizard.wizard_server import app, start_wizard_server
