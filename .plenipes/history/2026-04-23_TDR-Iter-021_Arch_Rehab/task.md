# 任务清单 - TDR-Iter-021: 架构复健与复杂度降熵

## 🏗️ 架构瘦身 (File Splitting)
- [x] 创建 `core/engine_factory.py` 并迁移 `Engine.__init__` 逻辑
- [x] 重构 `core/engine.py` 接入工厂类，移除冗余初始化代码
- [x] 验证 `engine.py` 行数降至 300 行以下

## 🛡️ 稳固性加固 (Safety Hardening)
- [x] 全局搜索并修复 `config[...]` 裸引用，改用 `.get()`
- [x] 修复 `egress_dispatcher.py` 中的 NoneType 风险点
- [x] 修复 `config.py` 中的配置注入风险点

## 🧹 环境卫生 (Hygiene Cleanup)
- [x] 更新 `.gitignore` 屏蔽规则
- [x] 物理清理全库 `__pycache__` 产物
- [x] 暂存所有变更并准备提交

## 🏁 验收与同步
- [x] 运行 `governance_audit.py` 验证复健效果
- [x] 更新 `SPECIFICATION.zh-CN.md` 文档
- [x] 完成 TDR 深度复盘
