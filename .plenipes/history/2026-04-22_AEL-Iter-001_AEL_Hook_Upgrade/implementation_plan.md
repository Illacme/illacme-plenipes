# 全自动演化矩阵约束升级计划 (AEL & TDR Matrix Governance)

为了彻底根治 AI 在自主迭代过程中的“只敲代码，不写历史”的惯性弊病，我们需要对 `tests/autonomous_simulation.py` 中的 Git 熔断器进行二次扩容，将其升级为“全矩阵文档约束”。

## Proposed Changes

### [MODIFY] [tests/autonomous_simulation.py]

重构现有的 `verify_docs_sync_hook`，引入以下两个强制层级的逻辑断言：

#### 1. 活化文档强制蔓延 (Living Documentation Expansion)
- **触发条件**：只要修改了 `core/` 源代码或 `plenipes.py`。
- **通行条件**：除了 `docs/` 目录外，如果系统检测到 `CHANGELOG.md` 或 `.plenipes/ROADMAP.md` 发生了改变，也视为“架构文档已更新”并放行。这兼顾了功能较小、仅需更新 Changelog 的场景。
  
#### 2. 纪传体归档绝对红线 (Genetic Archiving Absolute Redline)
- **触发条件**：只要 Git 检测到项目内有**任何形式的代码或文档物理修改**（`any_modified = True`），即代表这发生了一次 AI 迭代。
- **通行条件**：暂存区/工作区内必须检测到以 `.plenipes/history/` 开头的新增路径。
- **熔断拦截**：如果被我“遗忘”，则直接抛出 `AssertionError: [AEL Protocol Mandate] 检测到代码库发生物理变更，但未在 .plenipes/history/ 下沉淀本次迭代！`

## User Review Required

> [!WARNING]
> **本地开发颗粒度边界**
> 一旦这个红线实装，意味着甚至连你自己在本地改个错别字想偷偷 `git commit` 时，如果你运行了这个模拟仿真脚本，它都会逼着你在 `.plenipes/history/` 里建个文件夹。
> 我保留了 `ILLACME_SKIP_DOC_CHECK=TRUE` 的环境变量逃生阀，请确认这种“绝对严苛的代码洁癖”是否符合你的期望？如果同意，接下来我将自动接手并强迫我自己执行它！

## Verification Plan

### Automated Tests
1. 通过 `touch scratch/test.txt` 模拟一次无关痛痒的代码变更。
2. 运行 `tests/autonomous_simulation.py`，因为没有在 `history` 建档，预期必然触发 `[AEL Protocol Mandate]` 的 AssertionError 报错。
3. 手动 `mkdir .plenipes/history/test_mock`，再次运行，预期通过拦截，绿灯放行。
