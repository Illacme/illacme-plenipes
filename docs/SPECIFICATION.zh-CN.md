# 🛠️ Illacme-plenipes 项目技术规格书 (SPECIFICATION)

本文件详细定义了 Illacme-plenipes 引擎的核心架构、数据管线逻辑以及各项工业级设计准则，旨在为开发者提供深度的技术视图。

## 1. 核心架构总览 (High-Level Architecture)

Illacme-plenipes 采用 **“插件化适配器 + 线性同步管线”** 的解耦架构，核心组件分布如下：

*   **调度层 (Orchestrator & Daemon)**：负责环境初始化、多线程任务调度及文件系统实时监控。
*   **引擎层 (Engine)**：同步逻辑的“司令部”，负责装配 `SyncContext` 并在各个管线步骤间传递状态。
*   **管线层 (Pipeline)**：一套严谨的原子化加工步骤（Steps），负责处理从 Read 到 Route 的全量变换。
*   **适配层 (Adapters)**：
    *   **Ingress**：方言归一化（Obsidian/Logseq -> Standard Markdown）。
    *   **Egress**：物理出站适配（Markdown -> Docusaurus/Starlight UI 组件）。
    *   **AI Provider**：语义推理中枢（Token 级分片处理、增量 SEO 生成）。
*   **存储层 (Storage)**：
    *   **Ledger**：基于 Hash 的指纹账本，实现毫秒级增量判定。
    *   **Timeline**：创作审计时间轴，记录动作级历史。
    *   **Snapshot**：基于 `orjson` 的原子级物理落盘与灾备引擎。

## 2. 同步管线深度解析 (The Sync Pipeline)

每一篇文章在同步过程中都会经历以下 7 个核心阶段：

1.  **Read & Normalize**：读取源文件并注入元数据，处理 YAML Frontmatter 的物理合并。
2.  **Staticization**：将动态组件（如 Tabs, Dataview）转化为框架无关的静态 Markdown 语法。
3.  **AST & Purification**：通过抽象语法树清理非法标签、闭合 MDX 语法，并执行语义级资产提取。
4.  **Metadata & Hash**：计算内容指纹，通过 Ledger 判定是否需要触发 AI 任务或直接跳过。
5.  **AI Reasoning**：执行 Slug 生成、语义摘要提取及关键词矩阵构建。
6.  **Masking & Routing**：根据映射规则推导目标路径，并对敏感内容执行掩码隔离。
7.  **Egress Dispatch**：执行物理写盘，同时触发资产流水线（Asset Pipeline）进行 WebP 压缩与 Alt 补全。

## 3. 关键算法与设计模式

### 3.1 语义分片翻译 (Semantic Slicing)
针对超长文档，引擎利用 `tiktoken` 计算 Token 预算，结合 Markdown 标题层级执行贪心分片，确保 AI 翻译不丢失上下文。

### 3.2 影子资产自愈 (Shadow-Asset Recovery)
系统会自动在 `.illacme-shadow` 存储中间态 SEO 结果。当目标物理产物丢失但源文件指纹未变时，引擎能从影子资产中瞬间自愈，无需再次消耗 AI 算力。

### 3.3 声明式渲染与短代码转换 (Syntax-Driven Adaptation)
Egress 适配层通过正则表达式映射表（`shortcode_mappings`）实现从 Obsidian 方言到 SSG 私有语法（如 Hugo Shortcodes）的逻辑平移。这一设计彻底消灭了针对单一框架编写硬编码适配器的必要。

### 3.4 栈式组件解析 (Stack-based Staticization)
为了处理复杂的嵌套组件（如 Tabs 套 Tabs），静态化引擎采用了非正则的物理行扫描算法。通过栈（Stack）维护平衡匹配，确保复杂排版在降维过程中不丢失层级结构。

### 3.5 状态机信号分层 (State Machine Signal Isolation)
在处理核心管线中断逻辑时，引擎实行严格的双轨信号分离机制。性能级缓存命中（如源文件指纹未变更）必须抛出 `is_skipped` 信号，从而执行安全放行；而诸如安全拦截（空文件、关键格式错误）或人为阻断，则抛出 `is_aborted` 信号。这一区分确保了创作审计系统（Timeline）能够精准捕获物理截断与性能跳过，避免前端状态机的审计误报。

## 4. 扩展性原则

*   **新增语种**：在 `i18n_settings` 中配置 `targets` 阵列，无需修改核心代码。
*   **新增 SSG 框架**：在 `core/adapters/egress.py` 中实现新的 `SSGAdapter` 类，并在 `config.yaml` 的 `framework_adapters` 中定义 Callout 映射。
*   **新增方言**：在 `ingress_settings` 中注册自定义 Sanitizer，底层正则表达式会自动挂载至清理管线。
