# SOP-05: 治理哨兵协议 (AI Sentinel & Compliance Matrix)

> [!IMPORTANT]
> **本协议定义了 AI 助手在执行任务时的强制性自省流程。任何违反本协议的行为都将被视为“系统性风险”。本协议高于一切业务指令。**

## 1. 任务准入审计 (Pre-flight Audit)
在生成任何 Implementation Plan 之前，AI 必须在 Thought 环节回答以下“灵魂三问”：
1. **物理红线**：目标文件当前行数是多少？是否触及 300/500 行物理极限？
2. **快照先行 (Snapshot-First)**：是否已执行 `.plenipes/tools/api_parity.py --capture` 捕获了修改前的 API 响应基准？
3. **基因扫描**：是否已在 Thought 中物理列出目标代码块的全量字段清单，以锁死逻辑契约？
4. **依赖对正**：是否已执行全局 `grep` 确认前端/后端字段的物理耦合深度？

## 2. 强制存证标识 (Evidence Tags)
在回复用户时，必须使用以下标签进行状态标记，作为“任务完成”的物理证据：
- `[EVIDENCE: BASELINE]`：列出原始状态的存证路径（截图 ID / JSON 备份路径）。
- `[EVIDENCE: PARITY]`：展示重构前后的 Diff 对比结果（使用 `.plenipes/tools/api_parity.py` 生成）。
- `[EVIDENCE: PERSISTENCE]`：展示物理落盘的证据（如 `cat` 或 `yaml_verify` 结果）。

## 3. 治理优先级与熔断 (Governance Priority)
- **拒绝执行**：如果用户要求在 >500 行文件中新增复杂逻辑，AI **必须**首先建议执行“物理降解”。
- **失败熔断**：一旦物理校验（如落盘失败、Schema 偏离）出现报错，禁止在错误基础上执行“在线修补 (Hotfixing)”，必须立即物理回滚并提交风险分析。

## 4. 复盘自检模版 (Post-flight Checklist)
任务结束前，AI 必须完成以下自检：
- [ ] **基因溯源**：所有 `🚀 [Vxx.x]` 基因标记是否完整保留？
- [ ] **契约对正**：API JSON 结构是否与 Baseline 100% 对齐（包括键名、层级、空值处理）？
- [ ] **像素级比对**：UI 是否存在非预期的偏移或功能缺失？
- [ ] **物理闭环**：数据是否已进入正确的治理层级（Local / Imprint / Global）？

## 5. 物理哨兵强制执行 (Hard Enforcement)

> [!CAUTION]
> **本章节定义了物理拦截规则。任何试图绕过物理哨兵的行为都将被视为对系统主权的恶意破坏。**

1. **法定校验器**：`.plenipes/tools/sentinel_matrix.py` 是唯一的法定治理校验工具。
2. **强制运行时机**：
   - 在生成任何 `Implementation Plan` 之前（空转审计）。
   - 在执行 `git commit` 之前（最终门禁）。
3. **失败处置 (Disposal on Fail)**：
   - 如果 **[红线审计]** 失败：必须立即进行“手术拆解”，将大文件拆分为多个符合 <500 行规范的子模块。禁止申请豁免。
   - 如果 **[基因溯源]** 失败：必须回滚变更，或者在 Thought 中提供严密的逻辑论证，说明为何该基因已失效，并获得用户的手动确认。
4. **自动化拦截**：在后续版本中，`sentinel_matrix.py` 将被集成到 Git Pre-commit Hook 中。

---
*修订日期：2026-05-13*
*生效范围：全栈迭代与重构任务*
