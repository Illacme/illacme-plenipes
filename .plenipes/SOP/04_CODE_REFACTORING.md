# SOP-04: 代码精益重构与全栈物理拆分准则 (Industrial Grade Refactoring)

本准则定义了当文件物理行数超过 [SOP-03] 规定红线时的标准化拆分流程。其核心目的在于通过“物理降解”消除 AI 助手处理大文件时的认知负荷，确保系统在极速迭代中保持架构透明度与功能稳定性。

## 1. 物理红线管控 (The Red Line)
- **300 行 (Warning)**：AI 必须主动提醒并建立“治理预警”，在 implementation_plan 中明确拆分路径。
- **500 行 (Hard Limit)**：**强制执行物理拆分**。严禁在超过 500 行的文件中新增任何非修复性逻辑。

## 2. 工业重构六大铁律 (The Six Iron Rules)

### I. 逻辑等价指纹 (Logic Fingerprinting)
- **准则**：重构前必须针对目标模块生成“逻辑指纹”。
- **校验**：重构后的逻辑链路必须通过 `diff` 验证，副作用与原始指纹 **100% 吻合**。

### II. 单一真理源 (Single Source of Truth)
- **准则**：拆分出的原子模块必须是该逻辑状态的“物理唯一居所”。

### III. 循环引用熔断 (Circular Dependency Break)
- **准则**：物理拆分严禁导致循环导入。

### IV. 版本痕迹全量保留 (Heritage Preservation)
- **准则**：搬迁代码必须携带所有历史基因（🚀 [Vxx.x]）。

### V. 物理落盘二次校验 (Physical Integrity Check)
- **准则**：确认所有导出函数签名与原文件 **绝对对齐**。

### VI. 单体拆分约束 (Single-Unit Constraint)
- **准则**：**严禁同时对多个大文件执行拆分**。
- **校验**：每一次治理行动的物理边界必须锁定在**单个文件**内。只有当前文件完成全流程量化校验并确认 Stable 后，方可启动下一个治理目标。

## 3. 标准化施工流 (Implementation Workflow - Atomic Incremental)

### 第一阶段：视觉与逻辑存证 (Evidence Capture)
- **物理截图存证**：`.plenipes/history/refactoring/snapshots/[YYYYMMDD]/` 记录 Baseline。
- **DOM 指纹备份**：导出关键容器的 `outerHTML` 并保存为 `.html.dump`。
- **逻辑基准备份**：记录后端路由的 `response_baseline.json`。

### 第二阶段：微步原子搬迁 (Micro-Atomic Migration)
- **分步执行**：禁止一次性搬迁全量代码。必须按“逻辑块”或“函数组”执行增量搬迁。
- **即时点火**：每迁移一个逻辑块，必须立即更新枢纽文件（Hub）并执行一次最小化运行测试。

### 第三阶段：枢纽重建与校验循环 (Hub & Verification Loop)
- 原文件重构后退化为“路由调度中心”。
- 每一步搬迁后，必须比对关键指纹。若校验通过，则执行物理 Checkpoint。

### 第四阶段：量化校验 (Verification & Parity)
- **视觉像素比对 (Visual Diff)**：
  - 重构后截图与 Baseline 执行像素级叠图，偏离度必须为 0%。
  - 重点核对：间距 (Padding/Margin)、颜色值 (HEX/RGBA)、阴影深度。
- **DOM 指纹对齐 (DOM Alignment)**：
  - 校验 `document.querySelectorAll('*').length` 变化。
  - 确认所有交互元素的 ID 与 Class 属性无变动。
- **功能闭环审计 (Functional Matrix)**：
  - **点击-响应测试**：每一个按钮必须触发原有的 API 动作或 UI 状态切换。
  - **异常审计**：控制台 (Console) 严禁出现新的 `ReferenceError` 或 `404`。

## 4. 熔断回滚与硬终止协议 (Fallback & Escalation Protocol)

> [!IMPORTANT]
> **本协议高于一切执行指令。当重构过程偏离基准时，自动触发物理熔断。**

### I. 失败即刻回滚 (Immediate Rollback)
- 一旦任何原子步进导致校验失败（视觉偏离、逻辑报错、指纹不符），AI 必须立即放弃当前修改，**物理回滚至上一个验证通过的 Checkpoint**。
- 严禁在失败的基础上执行“在线修补 (Hotfixing)”，必须确保回滚后的基准环境绝对纯净。

### II. 策略寻优 (Strategy Pivot)
- 回滚后，AI 需重新分析失败原因，并提出**替代拆分方案**（如调整注入顺序、隔离依赖等）。
- 替代策略必须在 implementation_plan 中重新向用户报备。

### III. 二次失败硬终止 (Hard Stop)
- 若替代策略在同一逻辑点再次触发校验失败，AI 必须**立即停止一切重构操作**。
- AI 需整理失败的物理证据（日志、截图、差分），向用户提交“技术攻坚报告”，并等待用户明确指示。

## 5. 核心技术避坑准则 (Technical Pitfalls)

### I. 路径解析基准化 (Path Normalization)
- **风险**：子模块相对路径失效。
- **对策**：拆分后涉及文件系统的操作必须使用**全局绝对路径**。

### II. 底层状态下沉 (State Sinking)
- **风险**：循环引用。
- **对策**：全局单例及其 Getter/Setter 必须物理下沉至**无依赖的 Singleton 模块**。

### III. 参数解析权限分层 (Argparse Layering)
- **风险**：CLI 参数定义与逻辑脱节。
- **对策**：入口枢纽保留参数定义权，子模块保留处理权。

## 6. 重构事故规避铁律 (Anti-Regression Iron Rules)

> [!CAUTION]
> **严禁在未审计 HTML/CSS 支撑环境的情况下，直接对前端逻辑执行物理分拆。**

### I. 物理锚点预设 (Anchor Pre-flight)
- **对策**：在分拆 JS 前，必须在 `index.html` 或 `views.js` 中**预先静态化**所有 ID 锚点。

### II. 样式与效果保障 (Style Integrity)
- **对策**：重构后的 HTML 结构嵌套深度必须与原版 **100% 保持一致**。

### III. 资源加载时序对正 (Sequence Alignment)
- **对策**：遵循：**基础工具 -> 原子分片 -> 逻辑枢纽** 的加载顺序。

### IV. 内容级像素复原验证 (Content-Level Parity)
- **对策**：必须强制校验：`document.getElementById(KEY_ID).children.length > 0` 且关键容器可见。

## 7. 治理审计 (Audit)
- 每次重构必须在 `EVOLUTION_HISTORY.md` 中记录“拆分映射表”与“视觉比对报告路径”。

## 8. 深度复盘经验固化 (Lessons Learned Enforcement - V24.0)

> [!IMPORTANT]
> **基于 V24.0 重构失败的血泪教训：** 禁止在未识别 JS 全局依赖的情况下执行“细胞级”拆分。

### I. 全局依赖矩阵审计 (Global Dependency Audit)
- **要求**：在拆分任何前端 JS 文件前，必须先在 `implementation_plan.md` 中列出该文件涉及的所有 `window` 全局变量及跨文件调用函数。
- **目标**：确保拆分后的模块挂载顺序（Order of Injection）与依赖链 100% 匹配。

### II. 强制浏览器 UI 自动化校验 (Mandatory Browser Verification)
- **要求**：涉及 `dashboard.js` 相关族群的重构，必须在 `task.md` 中包含“子代理 UI 巡检”步骤。
- **动作**：调用 `browser_subagent` 模拟用户点击核心 Tab（如算力中心、插件矩阵），并截取 Console Log 以确认无 `ReferenceError`。

### III. 禁止“在线补丁” (No Hotfixes Policy)
- **要求**：重构后的 UI 如果出现“局部失效”（如某个按钮不弹窗），严禁在原子分片内进行逻辑微调。
- **动作**：必须执行 **物理回退 (git restore)**，重新分析依赖关系后再启动新一轮实验。

### IV. GitHub 前置提交锁定 (GitHub Commit Lock)
- **要求**：在执行任何拆分操作（SOP-04）前，必须确认当前工作区已 100% 提交并推送至 GitHub 仓库。
- **目标**：确保在发生不可预知的物理损坏或逻辑坍塌时，具备 100% 的云端恢复能力。

### V. 强制存档总结报告 (Mandatory Post-Refactor Report)
- **要求**：拆分任务结束时，无论成功还是失败（触发回滚），AI 必须强制输出一份详细的总结报告进行存档。
- **位置**：存放在 `.plenipes/history/refactoring/refactor_summary_[YYYYMMDD].md`。

---
*修订日期：2026-05-12*
*执行负责人：Antigravity (AI Controller)*
*优先级：S 级 (不可逾越)*
