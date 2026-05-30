#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚙️ Illacme Plenipes - Human-In-The-Loop (HITL) Session Manager
作为人类在环会话全局管理器的“物理唯一真理源”，实现全局 AI 挂起等待、授权决策逻辑与状态解耦。(V77.10)
"""

# 全局活跃的 HITL 会话缓存真理源，存放挂起会话的事件与决策状态
active_hitl_sessions = {}
