# Illacme Plenipes 规则治理总索引 (SOP Index)

为了解决规则冲突、遗忘与碎片化问题，项目所有的活跃规则均统一收敛于 `.plenipes/SOP/` 目录。

## 📥 活跃规则列表 (Active Rules)

| 规则编号 | 规则名称 | 核心职责 | 状态 |
| :--- | :--- | :--- | :--- |
| **[SOP-00]** | [协作准则 (Collaboration)](file:///Volumes/Notebook/omni-hub/illacme-plenipes/.plenipes/SOP/00_COLLABORATION_RULES.md) | **硬性规则**：全中文思考/交互、强制子目录归档。 | **Active** |
| **[SOP-01]** | [品牌主权与系统治理 (Imprint & Governance)](file:///Volumes/Notebook/omni-hub/illacme-plenipes/.plenipes/SOP/01_SYSTEM_GOVERNANCE.md) | **品牌与版图**：身份定位、出版发行流水线隐喻、术语主权（禁用 Brand）、独立项目疆域。 | **Active** |
| **[SOP-02]** | [代码质量 (Engineering)](file:///Volumes/Notebook/omni-hub/illacme-plenipes/.plenipes/SOP/02_ENGINEERING_STANDARDS.md) | **技术规则**：Lint 修复标准、注释保留原则。 | **Draft** |
| **[SOP-03]** | [前端工程标准 (Frontend Engineering Standards)](file:///Volumes/Notebook/omni-hub/illacme-plenipes/.plenipes/SOP/03_FRONTEND_ENGINEERING.md) | **技术规则**：300行物理红线、资产本土化强制令。 | **Active** |
| **[SOP-04]** | [代码精益重构与物理拆分准则 (Code Refactoring)](file:///Volumes/Notebook/omni-hub/illacme-plenipes/.plenipes/SOP/04_CODE_REFACTORING.md) | **重构规则**：标准化拆分流程、像素级还原保障机制、500行强制重构令。 | **Active** |
| **[SOP-05]** | [治理哨兵协议 (Sentinel Protocol)](file:///Volumes/Notebook/omni-hub/illacme-plenipes/.plenipes/SOP/05_SENTINEL_PROTOCOL.md) | **AI 自省规则**：强制性存证、API 对正审计、物理红线熔断机制。 | **Active** |
| **[SOP-06]** | [故障处理与回滚协议 (Fault Tolerance)](file:///Volumes/Notebook/omni-hub/illacme-plenipes/.plenipes/SOP/06_FAULT_TOLERANCE.md) | **止损规则**：功能倒退即刻回滚、故障分析报告。 | **Active** |
| **[SOP-07]** | [日志与可观测性标准 (Observability)](file:///Volumes/Notebook/omni-hub/illacme-plenipes/.plenipes/SOP/07_OBSERVABILITY.md) | **监控规则**：强制性后端 tlog 与前端 addAudit 指纹审计。 | **Active** |

## 🛡️ 执行机制 (Enforcement)
1.  **开工必读**：AI 助理在接到任务后的第一步思考必须是：“是否符合 SOP Index 中的相关规则？”。
2.  **契约锁死**：根据 SOP-00，任何重构前必须先通过 Thought 审计物理列出全量字段。
3.  **强制指纹**：根据 SOP-07，所有新注入逻辑必须具备可被审计的日志指纹。
4.  **失败回滚**：根据 SOP-06，任何功能回归必须触发物理复位。

---
*法典版本：V52.20_Sovereign_Hardening*
*更新日期：2026-05-13*
*治理负责人：Antigravity (AI Controller)*
