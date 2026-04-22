# 📜 Illacme-plenipes 更新日志 (CHANGELOG)

本文件记录了 Illacme-plenipes 引擎从初版至今的所有重大演进。

## [v4.4-Governance] - 2026-04-23
### 🚀 全自动治理框架里程碑 (Major Governance Milestones)
- **治理引擎升级至 v4.4**：自审清单扩展至 28 项硬约束检查，实现全链路自治。
- **踩坑自闭环 (Self-Healing Lessons)**：
  - 新增“信号探测仪”：自动扫描修复模式（fix/bug/error）并强制要求沉淀教训。
  - **Guard 绑定协议**：物理校验 `evolution_records.md` 中的每一条教训是否都关联了有效的治理检查函数。
- **架构复健节律 (TDR Rhythm)**：引入业务迭代计数器，强制每 5-8 次特性开发后必须进行一次架构解耦迭代。
- **全 IDE 基因对齐**：同步发布 `.cursorrules`, `.continuerules`, `.windsurfrules`, `.github/copilot-instructions.md`，实现跨平台 AI 行为一致性。

### 🛡️ 硬约束增强 (Added Checks)
- **[AEL-Iter-014/v4.2] 物理防裁剪**：新增 `check_no_mass_deletion` 与 `check_comment_retention`，严禁 AI 大规模裁剪代码或删除注释。
- **[AEL-Iter-014/v4.2] 遗漏探测**：新增 `check_no_unstaged_leftovers`，物理阻断“部分暂存”导致的提交不全。
- **[AEL-Iter-015/v4.2] 演化必测**：核心逻辑变更强制附带物理测试代码。

### 🔧 基础设施优化 (Fixed)
- **收割机自愈**：重构 `harvest.py` 为物理编号扫描模式，彻底解决高频迭代下的迭代号（Iter_NNN）冲突。
- **教训双轨沉淀**：确立全局/项目双层教训存款机制，防止“工程失忆”。

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
- **feat(governance)**: Injected Boot Sequence Reflex (BSR) into .antigravityrules, .cursorrules, and global KI protocols. AI agents are now forced to physically read rules on first turn.
- **feat(governance)**: Split evolution_records.md into global (universal) and project-specific (illacme) layers with dual read/write mandates.
- **feat(governance)**: Created governance_audit.py self-audit engine with 7 automated checks. AI now has autonomous inspection capability.
# hook test
- **feat(governance)**: Added setup-hooks.sh for hook portability; 2 new audit checks (hook existence, runtime artifact detection).
- **feat(governance)**: Governance audit v2.0 complete — 16 checks, zero gaps. All self-evolution mechanisms sealed.
- **feat(governance)**: Upgrade to v3.0 (Dynamic Engine) with  checks, integrating actual simulation sandbox run directly into commit process.
- **fix(core)**: Resurrect Alt-Text image processor and restore Metadata API to eliminate sandbox runtime crash.
- **fix(sentinel)**: Add robust sandbox error handling (fallback on missing Ruff / directory missing).
