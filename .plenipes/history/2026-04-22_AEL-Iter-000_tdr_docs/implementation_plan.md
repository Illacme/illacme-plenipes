# TDR (技术债清还)：活化文档回填与强熔断机制建立 (Living Documentation Sync & Hook)

解决在 V33.7 与 V34.5 迭代中遗留的“代码超前、文档掉队”漏洞，物理补全架构文档，并在模拟自愈场中设立 Git 级别的钩子以阻断未来的掉队行为。

## Proposed Changes

### 1. 架构核心规范修补 (Documentation TDR)

通过补充漏掉的底层机制，使得业务文档真正对齐当前的旗舰版引擎逻辑。

#### [MODIFY] [docs/SPECIFICATION.zh-CN.md]
- **变更点**：在“同步管线深度解析”或“关键算法”章节新增 `3.5 状态机信号分层 (State Machine Signal Isolation)`。
- **内容**：物理阐述 `is_skipped` (无哈希变动跳过) 与 `is_aborted` (触发规则拦截) 的双轨机制逻辑。声明引擎必须如何处理这两种不同状态以防止 Timeline 审计误报。

### 2. 模拟防爆场增强 (Autonomy Matrix Guard)

为 `autonomous_simulation.py` 补充物理防御机制，将其打造成全自动迭代中真正的“最后防线”。

#### [MODIFY] [tests/autonomous_simulation.py]
- **变更点**：新增一个装饰器或前置验证函数 `verify_docs_sync_hook()`。
- **验证逻辑**：在执行核心模拟测试前，利用 `subprocess` 调用并解析 `git status --porcelain` 或 `git diff`。
- **熔断条件**：如果检测到暂存区/工作区对 `core/` 下的核心管线代码有修改，但对 `docs/` 目录**没有任何改动**，那么该文件会直接触发 `AssertionError: [Living Documentation Mandate] Core logic modified without syncing docs/` 并强行阻断测试。（此举将直接阻断作为主体智能体的我提交报告）。

## 反馈请求 (User Review Required)

> [!WARNING]
> **Git 钩子的严格度确认**：
> `autonomous_simulation.py` 中新加的 Git 校验可能会在你的开发早期（还没来得及写文档的时候）导致本地运行直接报错。此校验主要用于约束未来的全自动 AI 迭代，是否需要为该校验提供一个 `--skip-doc-check` 的手动逃生阀门，以方便你个人的本地单步调试？

## Verification Plan

### Automated Tests
1. 执行 `python3 tests/autonomous_simulation.py`，观察系统正常通过。
2. 物理触碰 `core/config.py`（例如加个空格），再次执行模拟测试，预期触发 `AssertionError`。
3. 同步物理触碰 `docs/SPECIFICATION.zh-CN.md`，再次执行测试，预期恢复通过（绿灯）。此机制验证文档掉队漏洞被永久封死。
