# 实施方案 - Project Sovereignty (v5.1) 第二阶段：哨兵闭环 (Sentinel Closure)

本方案旨在通过治理审计引擎的硬性拦截，强制实现开发过程的“闭环自愈”。

## 核心目标
1.  **物理拦截偷懒**：审计引擎将自动检查 `task.md` 的核销情况，未勾选的任务将导致审计失败。
2.  **强制架构契约**：使用 AST 分析确保流水线工序不再违规使用正则，必须通过服务层。
3.  **深度复盘约束**：强制要求 `walkthrough.md` 包含高质量的偏差分析。

## 拟议变更

### 1. 治理审计升级 (The Sentinel)

#### [MODIFY] [governance_audit.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/tests/governance_audit.py)
- **新增 `check_task_completion_status`**：解析任务清单，拦截未完成项。
- **新增 `check_walkthrough_depth`**：验证复盘内容的质量与字数。
- **升级 `check_callout_nesting`**：改为通过 AST 静态分析，增强检测的逻辑严密性。

### 2. 演化记录同步

#### [MODIFY] [.plenipes/ROADMAP.md](file:///Volumes/Notebook/omni-hub/illacme-plenipes/.plenipes/ROADMAP.md)
- 更新里程碑状态，标记 v5.1 启动。

## 验证计划
- 运行 `python3 tests/governance_audit.py` 进行自我约束测试。
- 在 `task.md` 中故意留下未完成项，测试拦截效果。
