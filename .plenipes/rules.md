# Illacme-plenipes 项目治理宪章 (V6.0)
# 🛡️ 架构主权与 AI 开发硬约束

本宪章是 Illacme-plenipes 引擎的最高开发准则，旨在通过硬性的逻辑约束和物理审计，确保 AI 在自主迭代过程中不偏离架构初衷。

---

## 第零层：核心红线 (The Absolute Red Lines)
**违反以下任何一条，均视为治理失败，必须立即回滚。**

1. **[R0.1] 语言主权 (Language Sovereignty)**：
   - 所有用户交互、过程文档（Plan/Task/Walkthrough）必须全量使用 **中文**。
   - 配置文件中的 `commentary` 必须详尽且为中文。

2. **[R0.2] 逻辑剪枝禁令 (No Pruning)**：
   - 严禁在未完成逻辑迁移的前提下删除任何核心类方法。
   - 严禁简化现有的正则表达式（尤其是 Ingress 掩码逻辑）或脱敏算法。

3. **[R0.3] 复杂度红线 (300 Lines Policy)**：
   - 禁止任何单个 Python 逻辑文件超过 **300 行**。
   - 触线即强制重构，禁止通过增加注释来逃避该约束。

---

## 第一层：架构与物理约束 (Architecture & Physics)

4. **[R1.1] 物理拓扑完整性**：
   - 所有 Python 目录必须包含 `__init__.py`。
   - 静态导入链必须通过 100% 连通性扫描，严禁循环引用。

5. **[R1.2] 逻辑主权隔离协议 (Logical Sovereignty Isolation)**：
   - **适配器层 (core/adapters, adapters/)**：职责仅限于协议翻译、物理连接管理及厂商特定的载荷封装（Payload Wrapping）。严禁在适配器内编写业务状态机或审计策略。
   - **核心中枢层 (core/logic, core/governance, core/pipeline, core/services)**：承担所有业务决策、全量审计、任务调度及管线流转职责。
   - **调用准则**：必须遵循 `核心层 -> 适配器层` 的单向调用。禁止适配器层引用任何核心逻辑组件，以确保插件化的纯粹性，防止架构“脑裂”。

6. **[R1.3] NoneType 免疫防御**：
   - 所有配置查找和 API 响应处理必须使用防御性 `dict.get()`。
   - 强制执行显式类型转换（如 `int(val or 0)`），严禁出现裸取导致的 `TypeError`。

7. **[R1.4] 冒烟点火令**：
   - 任何代码提交前，必须在子进程中成功执行 `python3 plenipes.py --dry-run`。
   - 确保系统具备 100% 可启动性，严禁提交无法运行的代码。

8. **[R1.5] API 控制面隔离协议**：
   - `core/api` 是外部交互的唯一合法平面。严禁在核心逻辑层（Logic/Engine）中直接处理 HTTP/Socket 协议。
   - 必须通过 `Bridge` (如 `core/api/bridge.py`) 实现事件外溢，保持引擎核心的纯净与无状态性。

---

## 第二层：工程生命周期 (AEL - Automated Engineering Lifecycle)

9. **[R2.1] 基因沉淀 (Genetic Archiving)**：
   - 每一个重大功能增量，必须在 `.plenipes/history/` 下建立独立文件夹。
   - 必须同步存放该版本的 `implementation_plan.md`, `task.md` 和 `walkthrough.md`。

10. **[R2.2] 仿真优先 (Simulation-First)**：
    - 凡涉及出站管线（Egress）或分发引擎的重构，必须先在 `tests/` 中通过仿真校验。

11. **[R2.3] 意图溯源 (Traceable Intent)**：
    - 所有 AI 生成或大幅修改的代码块必须包含 `[AEL-Iter-ID]` 或 `[Sovereignty]` 标签，方便追溯演进上下文。

---

## 第三层：服务连续性与质量 (Service & Quality)

12. **[R3.1] 纲领性配置保留**：
    - `config.yaml` 必须保持 V34.5+ 的结构复杂度。
    - 严禁擅自合并 `framework_adapters` 与 `theme_options` 节点。

13. **[R3.2] 审计时间线一致性**：
    - 严禁精简 `TimelineManager` 或 `daemon.py` 中的审计钩子。
    - 必须保留全量的同步轨迹记录。

14. **[R3.3] 资产管线硬约束**：
    - 保持对图片资产的 WebP 压缩与 Alt 标签生成的严格类型检查，严禁跳过元数据审计。

15. **[R3.4] 持久化原子性约束**：
    - 鉴于系统引入了 SQLite (core/storage/)，所有涉及索引更新的操作必须确保原子性。
    - 在多线程环境下必须使用互斥锁保护元数据账本，防止索引脑裂。

16. **[R3.5] 影子库主权隔离**：
    - 影子库（Shadow Vault）是唯一合法的渲染预处理区。同步引擎严禁在任何情况下直接修改 `vault` (源目录) 中的原始 Markdown 文件。

---

## 第四层：治理自审 (Self-Audit)

---
14. **[R4.1] 每轮必审 (Post-Iteration Audit)**：
    - 迭代结束后、提交前，必须执行 `python3 tests/governance_audit.py`。
    - 审计项必须 **0 失败** 准入。

15. **[R4.2] 活化文档同步**：
    - 核心逻辑变更后，必须同步更新 `docs/SPECIFICATION.zh-CN.md`。
    - 在 `CHANGELOG.md` 中留下带有时间戳的物理变更记录。

---

## 第五层：全球私人出版社：品牌与意象 (Global Private Press Protocol)

16. **[R5.1] 品牌主权一致性 (Branding Sovereignty)**：
    - 官方名称：唯一指定为 **Illacme Plenipes**。严禁在代码注释、日志或文档中使用 *Omni-Hub*。
    - 品牌口号：**Illacme Plenipes: 您的全球私人出版社 (Your Global Private Press)**。

17. **[R5.2] 核心意象术语映射表 (Term Mapping)**：
    在编写日志、变量名或文档时，必须遵循以下“出版社”隐喻：
    - **Manuscripts (原稿库)**：对应源内容仓库（Markdown Vault）。
    - **The Archive (档案馆)**：对应 `.plenipes/` 数据根目录。
    - **The Registry (注册簿)**：对应 SQLite 元数据账本（Ledger/DB）。
    - **The Shadows (影子库)**：对应内容缓存目录（Shadow Cache）。
    - **The Press (印刷工场)**：对应 SSG 的 `src` 处理目录。
    - **The Bookstore (全球书店)**：对应最终发布的 `dist` 静态站。
    - **Syndication (联合供稿)**：对应第三方分发插件（Publishers）。
    - **The Newsroom (总编室)**：对应 Dashboard 与控制台入口。

18. **[R5.3] 职能化身份注入 (Functional Roles)**：
    - 将 **AI 模型** 视为：**特约翻译官 (Translators)** 或 **首席文案 (Copywriters)**。
    - 将 **Sentinel** 视为：**首席校对 (Chief Proofreaders)**。
    - 将 **Engine** 视为：**总编辑 (Editor-in-Chief)**。

19. **[R5.4] 全自动出版流水线环节映射 (Pipeline Stages)**：
    在开发 Pipeline Steps 时，必须对齐以下业务阶段：
    - **Submission (收稿)**：对应 Ingress/Read 阶段，主编进行初稿指纹核对。
    - **Purification (净化)**：对应 Purify 阶段，去除杂质，准备进入审校流。
    - **Editorial Review (编辑审校)**：对应 Audit/Metadata 阶段，核验版权（哈希）与合规性。
    - **Global Translation (全球编译)**：对应 AI 翻译阶段，特约翻译官进行多语种重塑。
    - **Typesetting (排版打样)**：对应 Slug/SEO 生成，设计美观的 URL 与检索标签。
    - **Imprinting/Pressing (付印)**：对应 Egress 到 `src` 的过程，将样稿转化为印刷印张。
    - **Release (发行/上架)**：对应 SSG Build 到 `dist` 的终态，新书正式摆上全球书架。
    - **Syndication (播发)**：对应第三方分发，向通讯社和分销商进行联合供稿。

20. **[R5.5] 交互语境防御 (UX Tone)**：
    - 所有的 CLI 日志和 UI 文案应具备“出版仪式感”。例如：使用“正在打磨样张”代替“正在同步文件”，使用“注册簿已更新”代替“数据库已保存”。

