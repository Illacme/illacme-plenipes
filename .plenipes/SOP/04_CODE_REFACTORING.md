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
- **物理截图存证**：使用 `browser_subagent` 遍历**所有相关子菜单**，截图并存入 `.plenipes/history/refactoring/snapshots/[YYYYMMDD_TASK]/baseline/`。
- **DOM 指纹备份**：导出关键容器的 `outerHTML` 并保存为 `.html.dump`。
- **API 模式审计 (New)**：
  - **JSON 存证**：执行 `curl -s http://localhost:43212/api/xxx > api_baseline.json`。
  - **依赖搜索**：对 `core/api/static/js/` 执行全局 `grep`，识别所有依赖该接口的硬编码字段（ID/Category/Status）。
- **逻辑分支映射**：在 `implementation_plan.md` 中枚举原代码的所有逻辑分支，建立“逻辑迁移清单”。

### 第二阶段：微步原子搬迁 (Micro-Atomic Migration)
- **分步执行**：必须按“逻辑块”执行搬迁。
- **即时点火**：每迁移一个块，立即更新 Hub 文件并重启服务。
- **分支勾选**：每完成一个分支，必须在任务清单中勾选标记。

### 第三阶段：枢纽重建与校验循环 (Hub & Verification Loop)
- 原文件重构后退化为“路由调度中心”。
- 每步搬迁后，执行物理 Checkpoint。

### 第四阶段：量化校验 (Verification & Parity)
- **API Schema 差分 (Mandatory)**：
  - 执行 `curl` 获取新响应，与 `api_baseline.json` 进行全量 `diff`。
  - 校验 JSON 嵌套层级与键名是否 100% 对正。
- **视觉巡检比对 (Visual Parity)**：
  - 使用 `browser_subagent` 遍历**所有子菜单**截图，存入 `.../current/` 目录。
  - 必须将 `current` 截图与 `baseline` 截图进行逐一肉眼或像素级比对，确保渲染内容完整性。
- **功能闭环审计**：
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

## 9. 深度复盘经验固化 (V26.0 - 治理 API 与逻辑完整性准则)

> [!IMPORTANT]
> **基于 V26.0 治理路由拆分导致 API 格式崩溃与逻辑截断的惨痛教训：** 禁止在未对齐前端 Response Schema 的情况下修改后端响应结构。

### I. 响应模式 JSON 级对正 (Response Schema Parity)
- **要求**：重构 API 接口时，必须强制比对原始接口与新接口的 JSON 结构层级（如：数组 `[]` vs 对象 `{"data": []}`）。
- **校验**：必须使用 `curl` 导出重构前后的响应报文，执行 `diff` 审计，确保数据包装逻辑 100% 一致。

### II. 前端硬编码依赖审计 (Frontend Hardcoded Dependency Audit)
- **要求**：在修改任何 API 返回的 `id`、`category` 或 `status` 字段前，必须强制对 `core/api/static/js/` 目录执行全局 `grep`。
- **目标**：识别前端是否存在针对特定字符串的 `if/else` 逻辑或过滤逻辑（如：`category === 'hosting'`），确保后端返回的 ID 指纹与前端逻辑硬映射。

### III. 逻辑树全路径覆盖校验 (Logic Tree Coverage)
- **要求**：拆分代码块时，禁止进行“感官式迁移”。必须在 `implementation_plan.md` 中枚举原代码块的所有逻辑分支（如：插件矩阵的 9 大分类）。
- **动作**：迁移完成后，必须逐一勾选确认：**[x] 逻辑路径已闭环**。严禁出现因忽略长尾逻辑导致的“UI 空白”事故。

### IV. 动态发现与静态注册双重审计 (Discovery & Registry Parity)
- **要求**：涉及“插件/组件枚举”逻辑时，必须确保新代码不仅涵盖“已激活实例”，还必须涵盖“全局注册表 (Registry)”。
- **校验**：重构后必须验证 UI 能够正确显示“未启用但可配置”的组件，防止系统配置能力丢失。

## 10. 主权拦截与防偷懒硬红线 (Anti-Pruning & AI Sabotage Interception)

> [!CAUTION]
> **本章节旨在物理拦截 AI 的“习惯性跳步”与“擅自简化”行为。违反本章任何一条，用户有权立即终止当前会话。**

### I. 证据先行原则 (Evidence-First Approval)
- **硬拦截**：在启动第二阶段（原子搬迁）之前，AI **必须**在对话框中主动展示第一阶段生成的 `api_baseline.json` 核心片段和 `baseline` 截图路径。
- **授权点**：必须获得用户明确回复“准予搬迁”后，方可执行物理文件操作。

### II. 逻辑搬迁“总量守恒”定律 (Logic Conservation)
- **要求**：在 `implementation_plan.md` 中必须明确：`[原函数名] | [原行数] -> [新文件路径]`。
- **校验**：搬迁后，目标文件的有效逻辑行数必须与原逻辑块 **严格对应**。严禁以“优化”或“清理”为名删减任何一行代码（包括注释）。

### III. 强制二次 Grep 逻辑确认 (Post-Migration Grep)
- **动作**：迁移完成后，必须再次对原 Hub 文件执行 `grep` 搜索已迁移的关键词。
- **拦截点**：如果 Hub 文件中仍残留未被委派的旧逻辑，或新文件中丢失了原有的 `🚀 [Vxx.x]` 基因标记，判定为重构失败，强制触发回滚。

### IV. 视觉比对“零容忍”差异报告 (Zero-Tolerance Visual Report)
- **动作**：在第四阶段，AI 必须生成一份比对表格，列出：`子菜单 | Baseline 截图 ID | Current 截图 ID | 比对结论`。
- **硬要求**：只要有一个子菜单的 UI 元素位置发生 > 1px 的偏移，或数据内容减少，必须在报告中红字标注，并主动提请用户裁决是否触发回滚。

## 11. 逻辑全貌审计与原子交互链对正 (Logic Map & Interaction Parity - V27.0)

> [!IMPORTANT]
> **本章节旨在彻底杜绝“功能性逻辑丢失”。任何涉及 JS 拆分的任务，必须强制通过逻辑全貌审计。**

### I. 建立逻辑全貌图谱 (Logic Map Mapping)
- **要求**：在重构计划阶段，AI 必须深度阅读原文件，并总结出所有的 **“原子交互链 (Interaction Chains)”**。
- **格式**：在 `implementation_plan.md` 中以表格形式列出：
  | 交互动作 (Trigger) | 核心处理逻辑 (Handler) | 预期物理效果 (Effect) | 状态 (State) |
  | :--- | :--- | :--- | :--- |
  | 选择协议下拉项 | `selectProvider()` | 自动回填 `swal-input-url` | [ ] 已对正 |
  | 点击“感应”按钮 | `discoverModels()` | 异步填充 `asset-discovery-menu` | [ ] 已对正 |

### II. 原子搬迁“基因不丢失”校验 (No-Loss Gene Check)
- **硬准则**：在拆分 JS 代码块时，禁止仅仅迁移“看起来有用”的代码。
- **校验点**：必须对原文件中的 `onclick`, `oninput`, `addEventListener` 等事件绑定点执行 **[物理点名]**。
- **目标**：确保在重构后的 Hub 文件中，每一个被移除的行，都能在分片文件中找到 **1:1 的逻辑等价物**。

### III. 物理契约对正 (Contract Parity)
- **要求**：如果后端 API 字段发生了变化（如 ID 命名规范化），必须在重构 JS 时同步更新所有关联的硬编码字符串。
- **拦截点**：禁止出现“后端改了 ID，前端还在搜旧 ID”导致的逻辑断层。

---
*修订日期：2026-05-13*
*执行负责人：Antigravity (AI Controller)*
*核心红线：严禁在未建立逻辑图谱的情况下启动大文件拆分。*
