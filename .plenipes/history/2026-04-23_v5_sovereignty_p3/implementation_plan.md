# 实施方案 - Project Sovereignty (v5.2) 第三阶段：自愈闭环

本方案旨在实现治理审计的“自动化修复”，减少人工干预，提升系统进化的自主性。

## 核心目标
1.  **实现 AutoHealer 框架**：支持审计项的一键自动纠偏。
2.  **增量仿真优化**：提升影子校验速度，仅针对变更文件。
3.  **自主演化审计**：审计引擎具备根据代码逻辑自动勾选任务清单的能力。

## 拟议变更

### 1. 治理引擎升级

#### [MODIFY] [governance_audit.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/tests/governance_audit.py)
- 定义 `AutoHealer` 接口，为关键检查项（如 AEL 标记、任务勾选、文件 hygiene）提供修复逻辑。
- 引入 `--fix` 参数。

### 2. 增量仿真加速

#### [MODIFY] [tests/autonomous_simulation.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/tests/autonomous_simulation.py)
- 通过 `git diff --name-only` 过滤待测试文件，避免全量扫描带来的耗时。

## 验证计划
- 运行 `python3 tests/governance_audit.py --fix` 验证自愈效果。
- 观察仿真耗时是否显著下降。
