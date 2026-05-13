# SOP-02: 逻辑演进与重构手册 (Transformation Manual)
版本: V10.2 | 状态: 激活 (Active)

本手册定义了系统在面临架构调整、大文件拆分及跨会话任务接力时的物理操作流程，确保系统演进过程中的逻辑连续性与稳定性。

---

## 目录
1. [代码精益重构与物理拆分 (原 SOP-04)](#1-代码精益重构与物理拆分)
2. [跨对话接力与状态继承 (原 SOP-08)](#2-跨对话接力与状态继承)
3. 稳定性加固场景 (占位/待补充)

---

## 1. 代码精益重构与物理拆分 (Original SOP-04)

本准则定义了当文件物理行数超过红线时的标准化拆分流程。

### 1.1 物理红线管控 (The Red Line)
- **300 行 (Warning)**：AI 必须主动提醒并建立“治理预警”，在 implementation_plan 中明确拆分路径。
- **500 行 (Hard Limit)**：**强制执行物理拆分**。严禁在超过 500 行的文件中新增任何非修复性逻辑。

### 1.2 工业重构六大铁律 (The Six Iron Rules)
1. **逻辑等价指纹 (Logic Fingerprinting)**：重构前必须针对目标模块生成“逻辑指纹”。重构后的逻辑链路必须通过 `diff` 验证，副作用与原始指纹 **100% 吻合**。
2. **单一真理源 (Single Source of Truth)**：拆分出的原子模块必须是该逻辑状态的“物理唯一居所”。
3. **循环引用熔断 (Circular Dependency Break)**：物理拆分严禁导致循环导入。
4. **版本痕迹全量保留 (Heritage Preservation)**：搬迁代码必须携带所有历史基因（🚀 [Vxx.x]）。
5. **物理落盘二次校验 (Physical Integrity Check)**：确认所有导出函数签名与原文件 **绝对对齐**。
6. **单体拆分约束 (Single-Unit Constraint)**：**严禁同时对多个大文件执行拆分**。只有当前文件完成全流程量化校验并确认 Stable 后，方可启动下一个治理目标。

### 1.3 标准化施工流 (Implementation Workflow)
#### 第一阶段：视觉与逻辑存证 (Evidence Capture)
- **物理截图存证**：使用 `browser_subagent` 遍历**所有相关子菜单**。
- **DOM 指纹备份**：导出关键容器的 `outerHTML` 并保存为 `.html.dump`。
- **API 模式审计**：执行 `curl` 导出 `api_baseline.json`；识别所有依赖该接口的硬编码字段。
- **逻辑分支映射**：在 `implementation_plan.md` 中建立“逻辑迁移清单”。

#### 第二阶段：微步原子搬迁 (Micro-Atomic Migration)
- **分步执行**：必须按“逻辑块”执行搬迁。
- **即时点火**：每迁移一个块，立即更新 Hub 文件并重启服务。

#### 第三阶段：枢纽重建与校验循环 (Hub & Verification Loop)
- 原文件重构后退化为“路由调度中心”。

#### 第四阶段：量化校验 (Verification & Parity)
- **API Schema 差分 (Mandatory)**：新响应与 `api_baseline.json` 进行全量 `diff`。
- **视觉巡检比对 (Visual Parity)**：对比 `current` 与 `baseline` 截图，确保 100% 渲染一致。
- **功能闭环审计**：点击-响应测试，确保控制台无 `ReferenceError`。

### 1.4 熔断回滚与硬终止协议
- **失败即刻回滚**：一旦校验失败，立即物理回滚至上一个 Checkpoint。严禁在线修补。
- **二次失败硬终止**：若替代策略再次失败，必须立即停止操作并提交“技术攻坚报告”。

---

## 2. 跨对话接力与状态继承 (Original SOP-08)

本章节旨在消除“对话衰老”导致的逻辑退化，保持任务物理状态的连续性。

### 2.1 退出快照 (Exit Snapshot) 触发条件
当满足手动挂起、上下文溢出或手术中断时，必须生成或更新 `.plenipes/SESSION_SNAPSHOT.md`。

### 2.2 快照内容规范
`SESSION_SNAPSHOT.md` 必须包含：`Baseline_Hash`, `Dirty_Hash`, `Current_Task`, `Pending_Logic`, `Next_Step`。

### 2.3 继承审计流程 (Inheritance Audit)
1. **核实身份**：比对 `Dirty_Hash` 与物理 `git diff`。
2. **声明主权**：发送继承意志声明。
3. **跳过预检**：使用 `pre_flight_check.py --resume`。

---
*执行准则：意图可以中断，但状态必须永恒。*
