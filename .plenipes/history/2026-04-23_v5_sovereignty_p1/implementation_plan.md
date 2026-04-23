# 实施方案 - Project Sovereignty (v5.0) 第一阶段：逻辑服务化重构

本方案旨在将 `StaticizerStep` 中的核心静态化逻辑剥离至独立的 `StaticizerService`。这是实现高级自进化能力与自愈闭环的物理前提。

## 用户审核要点

> [!IMPORTANT]
> 本次重构改变了流水线工序 (Steps) 之间的交互模式。工序将不再通过扫描流水线来查找其他工序，而是统一通过中心化的“服务注册表”获取能力。这是向模块化、可测试架构迈出的关键一步。

## 拟议变更

### 1. 核心服务层 (Core Service Layer)

#### [NEW] [staticizer.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/services/staticizer.py)
- 创建 `StaticizerService` 类。
- 迁移原 `StaticizerStep` 中的 `_staticize_callouts`、`_staticize_tabs` 和 `_staticize_dataview` 方法。
- 完善文档注释，并嵌入 `[AEL-Iter-ID]` 溯源标识。

### 2. 流水线基建 (Pipeline Infrastructure)

#### [MODIFY] [context.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/pipeline/context.py)
- 为 `SyncContext` 添加 `services` 属性（初始化为容器对象或字典）。

#### [MODIFY] [engine.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/engine.py)
- 在 `IllacmeEngine.__init__` 中实例化 `StaticizerService`。
- 在 `sync_document` 初始化阶段，将服务实例注入到 `SyncContext` 中。

### 3. 流水线工序 (Pipeline Steps)

#### [MODIFY] [staticizer.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/pipeline/staticizer.py)
- 重构 `StaticizerStep`，使其完全委托 `ctx.services.staticizer` 执行逻辑。
- 仅保留 `Step` 作为流水线兼容的薄包装。
- 物理删除类内部的 `_staticize_...` 私有方法。

#### [MODIFY] [steps.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/pipeline/steps.py)
- 更新 `ASTAndPurifyStep`，直接调用 `ctx.services.staticizer.staticize_callouts`。
- **彻底消除** 遍历 `ctx.pipeline.steps` 的查找逻辑。

## 验证计划

### 自动化测试
- 执行 `python3 tests/governance_audit.py`：确保 35 项治理检查全部通过。
- 执行 `python3 tests/autonomous_simulation.py`：验证重构后的逻辑依然能生成正确的 SSG 资产。

### 手动校验
- 验证测试 Markdown 文件中的嵌套 Callout 是否渲染正常。
- 验证 ````tabs```` 语法是否仍能正确转换为 `:::tabs`。
