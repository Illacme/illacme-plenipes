# 任务清单 - Project Sovereignty (v5.1) 第二阶段：哨兵闭环

## 🏗️ 治理引擎加固
- [x] 在 `governance_audit.py` 中实现 `check_task_completion_status` (自动核销检查)
- [x] 在 `governance_audit.py` 中实现 `check_walkthrough_depth` (强制深度复盘)
- [x] 升级 `check_callout_nesting` 为 AST 模式 (逻辑指纹校验)

## 🧪 演化验证
- [x] 故意触发审计失败，验证“反偷懒”拦截有效性
- [x] 完成 v5.1 闭环验收并同步演化记录
