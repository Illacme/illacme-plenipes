# SOP-09: 逻辑契约与零风险重构协议 (Logic Contract & Shadow Testing)

> [!IMPORTANT]
> **本协议旨在物理消除重构带来的业务逻辑 Regression。当修改核心算法、复杂业务规则或关键数据转换逻辑时，强制执行。**

## 1. 影子快照 (Shadow Snapshot) 准则
在对任何被标记为“核心逻辑”的函数进行重构前，AI 必须执行以下动作：
1. **捕获现状**：使用 `.plenipes/tools/logic_shadow.py --capture` 运行目标函数，并自动生成包含 I/O 对的 `.shadow` 文件。
2. **定义覆盖范围**：快照必须包含至少 5 组典型输入及所有已知的边界条件（Edge Cases）。

## 2. 逻辑锁定与校验 (Locking & Verification)
重构完成后，AI 必须：
1. **运行对比**：执行 `.plenipes/tools/logic_shadow.py --verify`。
2. **100% 匹配要求**：除非重构的本意就是改变业务逻辑（需在 `logic_evolution.log` 中明确登记），否则输出必须与快照 100% 字符级对齐。

## 3. 物理拦截
`sentinel_matrix.py` 将检查：
- 变更集中是否包含核心逻辑函数。
- 如果包含，是否已生成并验证了对应的 `.shadow` 报告。

---
*修订日期：2026-05-13*
*执行准则：代码可以变美，但灵魂必须保持一致。*
