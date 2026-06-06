# 📜 Illacme-plenipes 更新日志 (CHANGELOG)

本文件记录了 Illacme-plenipes 引擎从初版至今的所有重大演进。

## [v6.4.0-Tower] - 2026-06-05
### 🚀 总编室控制塔可视化面板（阶段四）
- **实时指标 REST API 封装**：在 `services/api/routes/gov` 中实现了 `/api/governance/pulse` REST 端点及底层安全加载逻辑，强制进行了 API Token 验证与主权数据隔离。
- **前端可视化面板与导航实装**：在 dashboard 侧边导航实装“控制塔”选项卡，通过 Glassmorphism 样式与 CSS 发光投影呈现系统负载卡片及线程池队列进度。
- **高级 SVG 负载仪表盘**：重构了 CPU 和内存负载监测器，利用 CSS 过渡动画与 SVG 物理百分比圆环（stroke-dashoffset），实现顺滑的实时负载渲染。
- **进度条零值与卡顿自愈**：在 `HeartbeatService._gather_pulse` 中实现智能进度估算算法，将异步算力池（AI 推理池与资产处理池）的活跃和排队任务动态融入大盘进度计算中，彻底解决了单文档热更新在翻译阶段进度显示为 0，以及全量发布在 AI 收割阶段进度卡顿与置零的体验问题。
- **防御性生命周期管理**：在前端 `dashboard.tower.js` 控制器中增加了防泄漏逻辑，检测到离开当前视图或 DOM 不可见时自动销毁轮询，保障系统长时间运行无内存泄露。
- **测试套件覆盖**：新增 `tests/test_tower_visualization.py` API 集成测试，对路由连通性、身份验证过滤和 Pulse JSON schema 指标完整度做到了 100% 覆盖。

## [v6.3.0-SEO] - 2026-06-05
### 🚀 高阶 AI SEO 策略分流（出版模式优化）
- **SSG inject_seo 契约增强**：升级 `BaseSSGAdapter.inject_seo` 签名与功能，使其接收完整的 `seo_data` 字典并增量合并 OG 标签、Twitter Cards、Canonical 网址及 JSON-LD 等结构化数据至 Frontmatter 字段。
- **i18n_seo 交叉注入**：在 `BinderyDispatcher` 分发目标语种时，自动合并 `i18n_seo` 多语言翻译矩阵中的语言特定 SEO 属性，实现跨语言 SEO 差异化配置。
- **解耦优化**：将 SEO 注入细节委托给 `seo_helper.py` 处理，成功将 `base.py` 行数控制在 300 行红线内，完全符合 SOP 代码复杂度约束。
- **测试覆盖**：编写 `tests/test_seo_pipeline.py` 测试套件，100% 覆盖新签名向后兼容性与交叉合并注入逻辑。

## [v6.2.2-Refactor] - 2026-05-22
### 🚀 稿件流转加工流水线模块化物理拆分 (SOP-02 Pipeline Refactor)
- **步骤物理降解**：对大单体文件 `core/editorial/standard_steps.py` 实施 SOP-02 模块拆分协议，将其中的 6 大 PipelineStep 工序（读取与归一化、AST提纯、元数据指纹、AI SEO、隐私遮蔽、主权验证）原子搬迁到独立的子 Shards 中。
- **门面Facade中转**：将原 `standard_steps.py` 精简转型为桥接 Facade，物理行数由原本的 324 行极致压缩到 25 行，实现全向零形变无损向下兼容。
- **全息高保真对齐**：通过高保真逻辑基准 `standard_steps_logic_baseline.json` 物理证明拆分前后状态变换契约 100% 行为等价与零字节漂移。

## [v6.2.1-Parallel] - 2026-04-24
### 🚀 并行同步引擎加固 (Parallel Edition - Stage V6.1)
- **多级并行调度 [AEL-Iter-v6.2.1]**：引入 `Delta Block Parallelism`。在单文件同步内部启动块级并行翻译，结合语种级并发，实现全链路非阻塞同步。
- **工业级鲁棒性加固**：在 `BaseTranslator` 中集成指数退避重试机制。有效应对 429 流控与网络抖动。
- **深度响应审计**：针对 OpenAI/Ollama 适配器实现 400 错误深度日志捕获，强制记录 Response Body 以便排查本地推理格式问题。
- **元数据深度同步**：实现文章标题、标签（Tags）、分类（Categories）的自动化并行翻译与空值防御，确保多语言 SEO 完整性。

## [v6.0.1-Delta] - 2026-04-23
### 🚀 增量块引擎里程碑 (Delta Block Engine Milestones)
- **语义分片架构 (Stage V6)**：弃用落后的文件级同步，全面转向基于语义块（Block-Level）的增量管线。引入 `MarkdownBlockParser` 状态机实现 Callouts、Tabs、代码块的高精度切片。
- **影子块复用 (Zero-Token Reuse)**：建立 `BlockShadowCache` 物理复用层，实现跨文档、跨语种的块级翻译秒级检索，大幅降低 AI 算力成本。
- **账本指纹升级**：`MetadataManager` 新增块级指纹追踪，支持物理产物的细粒度审计与自愈。

### 🛡️ 安全与治理加固 (Security & Governance)
- **配置隔离 2.0**：实现 `configs/` 目录的“全量屏蔽 + 模板放行”策略，物理阻断 API Key 泄露风险。
- **治理监工补丁**：补全核心模块工业级 Docstrings，对齐 AEL 溯源协议。

## [v5.4.1-Sovereignty] - 2026-04-23
### 🚀 架构主权里程碑 (Sovereignty & Governance Milestones)
- **主权架构硬化**：实现业务逻辑（Base）与协议层（Adapter）的物理隔离。通过 `_ask_ai` 原子协议彻底解耦 AI 适配器。
- **治理星系 v5.4 重构**：自审引擎升级至“五大星系”调度架构，提供物理拓扑、点火冒烟、逻辑质量的全量审计（60/60 Pass）。
- **历史归档深度增强**：迭代文档（Plan/Task/Walkthrough）引入 3 迭代追溯机制，并实现双相内容深度校验。

### 🛡️ 硬约束增强 (Added Checks)
- **[Rule 12.10] 物理拓扑审计**：强制校验包结构（__init__.py）与静态导入链连通性。
- **[Rule 12.11] 冒烟点火协议**：提交前必须通过主入口点火测试，杜绝“无法启动”的代码入库。
- **[Rule 11.1] 复杂度红线升级**：将核心逻辑文件行数硬性限制在 **300 行** 范围内，强制重构。

### 🔧 修复 (Fixed)
- **逻辑丢失修复**：找回并重构了丢失的 AI Slug 生成与 SEO 提取逻辑，并建立了 AST 逻辑主权卫士进行监护。

## [v4.5-Refactor] - 2026-04-23
### Added
- [Structural Integrity] 引入栈式 Callout 解析器，取代脆弱的正则解析，完美支持多层嵌套。
### Changed
- [Architecture Consolidation] 将 Callout 渲染逻辑从 Egress Adapter 迁移至 Pipeline Staticizer 阶段。
### Fixed
- [Parsing] 修复了大规模嵌套 Callout 导致的结构损坏与语义丢失问题。

## [v4.4-Governance] - 2026-04-20
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
