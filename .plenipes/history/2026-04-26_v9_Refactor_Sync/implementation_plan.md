# [2026-04-26] 零触架构包化重构计划

## 目标
将单体逻辑拆分为标准的 Python 包结构，引入插件自发现机制，提升系统可扩展性。

## 方案
1. 拆分 `ai_provider.py` 到 `core/adapters/ai/`。
2. 拆分 `ingress/` 到 `core/adapters/ingress/`。
3. 引入 `plugin_loader.py` 实现自发现加载。
4. 迁移所有核心逻辑到 `core/` 下的对应包中。
