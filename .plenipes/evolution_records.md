# 🧬 Illacme-plenipes 项目进化记录 (Project Evolution Records)

本文件记录 Illacme-plenipes 引擎开发过程中的专属技术踩坑与架构进化。通用 AI 行为纪律请查阅全局 KI 中的 `evolution_records.md`。

## 📅 2026-04-18/19 进化点

### 1. [逻辑防御] 状态机信号分层 (State Machine Signal Isolation)
- **背景**：系统中存在性能跳过（指纹一致）与安全拦截（空文/草稿）两种中止逻辑，原系统混用 `is_aborted` 信号导致统计数据全量误报为"拦截"。
- **进化结论**：
    - **强制分层**：必须通过 `is_skipped` (性能跳过) 与 `is_aborted` (规则拦截) 进行双轨上报。
    - **显示反馈**：在 Summary Dashboard 中必须精确区分 ✅、🔄、🛑 三种物理状态。
- **Action**: 处理管线跳过逻辑时，禁止直接 Abort，必须先显式标记 Skip。

### 2. [新特性] 创作实时审计 (Real-time Audit Capability)
- **需求驱动**：用户需要对"本地保存 -> 系统响应"的整个过程有物理追溯能力。
- **进化结论**：
    - **时空追溯**：实现了 `plenipes_timeline.json` 与 `timeline.md` 的异步持久化。
    - **状态闭环**：审计必须覆盖从 Watchdog 捕获动作到 Pipeline 输出结果的全生命周期。
- **Action**: 未来新增监听事件时，必须同步在 `on_*` 钩子中植入 `timeline` 记录点。

### 3. [跨框架] 声明式 Egress 适配 (Declarative Egress GGP)
- **痛点回顾**：不同 SSG 的日期格式、短代码（Shortcode）各不相同，硬编码适配器导致工程臃肿。
- **进化结论**：
    - **正则映射表**：引入 `shortcode_mappings` 与 `datetime_format`，将"逻辑适配"下沉至"配置定义"。
    - **栈式静态化**：在处理嵌套 Tabs 时，必须使用平衡栈（Stack）而非正则表达式，以确保 100% 结构保真。
- **Action**: 所有出站适配逻辑应优先查找 `shortcode_mappings` 全局配置。

### 4. [自愈性] 哨兵监护与主动检测 (Guardian Sentinel)
- **需求驱动**：单纯的同步无法保证代码质量的长效稳定性。
- **进化结论**：
    - **主动纠偏**：通过 Sentinel + Ruff 实现静默期的代码自愈（Auto-Fix），消灭代码坏味道。
    - **测试驱动**：建立 AEL v2 协议，将"功能实现"与"单元测试"进行物理绑定（TDE）。
- **Action**: 哨兵审计报告必须作为 AEL 迭代归档的必要附件。

## 📅 2026-04-22 进化点

### 5. [Git 卫生] 本地状态泄露防线 (Git Hygiene)
- **故障回顾**：`ledger.json`、`plenipes_timeline.json` 等引擎运行时状态文件被 Git 追踪，导致仓库膨胀且存在隐私泄露风险。
- **进化结论**：
    - **精准切割**：`.plenipes/history/` 和 `rules.md` 必须提交（项目基因）；`ledger.json`、`timeline.*`、`sentinel_health.json` 和 `.illacme-shadow/` 必须屏蔽（本地状态）。
    - **追踪树清洗**：仅修改 `.gitignore` 不够，已被追踪的文件必须用 `git rm --cached` 物理摘除。
- **Action**: 新增运行时状态文件时，第一时间检查 `.gitignore` 是否已覆盖。

### 6. [AEL 治理] 防爆钩子与文档耦合 (Simulation Hook Governance)
- **故障回顾**：历史归档目录出现空文件夹，文档更新长期滞后于代码变更。
- **进化结论**：
    - **Git 防爆钩子**：`autonomous_simulation.py` 中的 `verify_docs_sync_hook` 强制要求每次代码变更同步更新 `docs/` 或 `CHANGELOG.md`，且在 `.plenipes/history/` 下新增归档。
    - **规则元进化**：`rules.md` 第九章授权 AI 在实战中主动修改规则本身，通过"修宪"实现事前预防而非事后惩罚。
- **Action**: 每次提交前运行 `autonomous_simulation.py`，确保防爆钩子放行。
