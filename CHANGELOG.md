# 📜 Illacme-plenipes 更新日志 (CHANGELOG)

本文件记录了 Illacme-plenipes 引擎从初版至今的所有重大演进。

## [v34.5-Flagship] - 2026-04-19

### 🚀 新增 (Added)
- **创作审计时间轴 (Audit Timeline)**：实时记录本地 FSEvents 与管线同步结果。
- **治理规则固化**：引入 `.antigravityrules` 限制自动化工具对代码完整性的篡改。
- **二层治理体系**：实现全局 KI 协议与局部 Repo 规则的分层管控。

### 🔧 修复 (Fixed)
- **代码精简事故**：修复了因占位符模式导致的 `engine.py` 核心变量丢失。
- **状态机误报**：解耦 `is_skipped` 与 `is_aborted` 信号，修复同步统计错误。

### 📝 文档 (Documentation)
- **活化文档系统**：实现 `SPECIFICATION`, `REFERENCE`, `MANUAL` 的全量自动化维护。

## [v33.7] - 2026-04-18

### 🚀 新增 (Added)
- **高精度分片引擎**：接入 `tiktoken` 实现 Token 级 Markdown 语义翻译分片。
- **影子资产引擎**：引入 `.illacme-shadow` 支持无 Token 消耗的物理自愈。

## [v16.0] - 2026-04-17

### 🔄 变更 (Changed)
- **配置一致性重构**：将所有零散配置项收拢至统一的 `Configuration` 强类型对象。

## [v13.0] - 旧版基准

- 实现基础的 Watchdog 监听与 Docusaurus 适配器。
- **chore(governance)**: Upgraded .gitignore to fully block V34.5+ local artifacts like ledger and timeline, ensuring a clean git tree.
- **feat(governance)**: Enacted Rule Meta-Evolution in rules.md. Agent is now explicitly authorized to amend governance rules proactively based on battle lessons to prevent recurrent assertion failures.
