# Illacme Plenipes 规则治理总索引 (SOP Index)

为了解决规则冲突、遗忘与碎片化问题，项目所有的活跃规则均统一收敛于 `.plenipes/SOP/` 目录。

## 📥 活跃规则列表 (Active Rules)

| 规则编号 | 规则名称 | 核心职责 | 状态 |
| :--- | :--- | :--- | :--- |
| **[SOP-00]** | [协作准则 (Collaboration)](file:///Volumes/Notebook/omni-hub/illacme-plenipes/.plenipes/SOP/00_COLLABORATION_RULES.md) | **硬性规则**：全中文思考/交互、强制子目录归档。 | **Active** |
| **[SOP-01]** | [系统主权 (Governance)](file:///Volumes/Notebook/omni-hub/illacme-plenipes/.plenipes/SOP/01_SYSTEM_GOVERNANCE.md) | **物理规则**：端口锁定、配置分层 (Local > Imprint > Base)。 | **Active** |
| **[SOP-02]** | [代码质量 (Engineering)](file:///Volumes/Notebook/omni-hub/illacme-plenipes/.plenipes/SOP/02_ENGINEERING_STANDARDS.md) | **技术规则**：Lint 修复标准、注释保留原则。 | **Draft** |

## 🛡️ 执行机制 (Enforcement)
1.  **开工必读**：AI 助理在接到复杂任务后的第一步思考必须是：“是否符合 SOP Index 中的相关规则？”。
2.  **废弃处理**：任何不再适用的旧规则文件必须移入 `.plenipes/history/deprecated_rules/`，不得残留在活跃目录。
3.  **冲突处理**：编号越小（SOP-00）优先级越高。如果 SOP-01 与 SOP-00 冲突，以 SOP-00 为准。

---
*更新日期：2026-05-12*
*治理负责人：Antigravity (AI)*
