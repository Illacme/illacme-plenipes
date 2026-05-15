# SOP-01: 全局工程准则 (Core Engineering Manual)
版本: V10.2 | 状态: 激活 (Active)

本手册是 Illacme Plenipes 系统的底层工程法典，定义了所有开发行为的“基石规范”。

---

## 目录
1. [交互与协作准则 (原 SOP-00)](#1-交互与协作准则)
2. [系统治理与系统主权 (原 SOP-01)](#2-系统治理与系统主权)
3. [工程标准与质量标准 (原 SOP-02)](#3-工程标准与质量标准)
4. [逻辑契约与 API 设计 (原 SOP-09)](#4-逻辑契约与-api-设计)

---

## 1. 交互与协作准则 (Original SOP-00)

本章节定义了 AI 助理与用户交互及处理现有代码时的基本行为底线。

### 1.1 语言与交互 (Language Sovereignty)
- **全中文流转**：思考过程（Thought Block）、对话、草稿（Scratchpad）、文档必须全部使用中文。
- **任务描述对正**：在调用任何具备 `Task`, `Description` 或 `Summary` 字段的自动化工具时，禁止使用英文。必须将其翻译为严谨的中文指令。
- **思考链拦截**：任何涉及逻辑推演、方案对比或进度记录的思考片段，严禁出现非中文的段落化呈现。
- **术语对正**：所有英文技术术语在思考过程中必须紧随中文解释，主体逻辑链必须 100% 中文。

### 1.2 工程诊断与故障溯源 (Engineering Diagnostics)
- **拒绝推卸责任**：当自动化工具（如 browser_subagent）访问失败时，禁止直接判定为“环境限制”。
- **强制诊断路径**：
    1. **进程自检**：物理检查目标程序是否正在运行 (`ps -ef | grep`)。
    2. **监听审计**：物理检查端口监听状态 (`lsof -i`)。
    3. **日志溯源**：检查应用日志是否存在崩溃或配置报错。
- **结果闭环**：只有在确认程序健康运行且端口开放的情况下，方可讨论网络隔离或环境限制问题。

### 1.3 契约锁死与代码诚信 (Contract Integrity)
- **禁止精简 (No-Pruning)**：严禁擅自删除或“重写简化”现有逻辑。
- **逻辑全貌审计 (Mandatory Pre-Audit)**：在修改/迁移任何核心逻辑块前，AI **必须**先通过 `cat` 或 `grep` 打印出该逻辑块的 **“全量字段与逻辑清单”**。
- **总量守恒原则**：任何搬迁任务必须在 Plan 中确认所有字段已 100% 映射至目标位置。严禁以“优化”为名丢弃任何一行有效代码。
- **注释保留**：100% 保留原有注释，包括历史基因标签 `🚀 [Vxx.x]`。

### 1.4 Git 卫生与归档契约
- **原子化提交 (Atomic Transaction)**：功能变更、SOP 文档修订及 `.plenipes/history/` 归档必须在同一个 Git 事务中提交。严禁分批提交导致审计引擎死锁。
- **防止残留 (No Leftovers)**：严禁手选文件提交（如 `git add file1`），必须确保工作区（Worktree）干净，且所有变更已对齐。
- **子目录归档**：历史记录必须以 `history/YYYY-MM-DD_任务描述/` 目录形式存在。

### 1.5 静默失效与验证主权 (Silent Failure Governance)
- **拒绝消极验证**：AI 助手禁止以“未发现报错日志”作为任务成功的判定标准。
- **正向证明原则**：验证阶段必须提供“预期业务效果已达成”的积极证据（如：回填值已显示、数据已落盘、字段 1:1 对齐）。
- **交互级嗅探**：对于前端重构，必须通过 `browser_console` 或 `audit_list` 确认关键逻辑路径（如切换 Provider 后的回填）已被物理激活。任何未经验证的“静默路径”均视为重构失败。

---

## 2. 系统治理与系统主权 (Original SOP-01)

本章节定义了 Illacme Plenipes 引擎的物理边界、受保护资产与品牌身份。

### 2.1 系统身份与隐喻 (Core Identity)
- **定位**：“全球私人出版社 (Global Private Press)”。
- **副标题**：“您的全球出版发行指挥中心 (Your Global Publishing & Distribution Command Center)”。
- **UI 核心隐喻**：Dashboard 必须作为“指挥中心”进行迭代，每一个交互都应具备“指挥”与“掌控”的即时感。
- **出版版图 (Publishing Map)**：指代系统中所有 **Imprint (品牌)** 的集合，代表了出版社的全球疆域。

### 2.2 核心术语与流程映射 (Terminology)
为了确保 AI 助理与指挥官的语义高度对齐，强制执行以下术语体系：

#### A. 创作阶段 (Ideation & Drafting)
- **The Scriptorium (创作中心)**：指代 AI 创作入口，由指挥官下达指令，AI 负责起草、润色并将想法固化为原稿。

#### B. 出版阶段 (Content Production)
- **Manuscript Vault (原稿文库)**：指代源 Markdown 库或内容资产，是系统主权的根基。
- **The Galley (排版文库)**：指代 SSG 内部的原始文档目录（src），是稿件进入装帧前加工、校样的“工作室”。
- **Compute (算力中心)**：负责“出版”的核心动力，涵盖内容生成与 AI 翻译流水线。
- **The Bindery (装帧中心)**：指代 SSG 渲染引擎（如 Hugo/Jekyll）。它负责将排版文库 (The Galley) 中的内容，通过预设的主题模板物理固化为出版成品。
- **The Publication (出版成品)**：由装帧中心产出的静态产物 (Dist)，是发行的物理对象。

#### C. 发行阶段 (Global Distribution)
- **The Matrix (发行矩阵)**：全球多平台、多语种的自动化部署网络基座。
- **The Dispatch (发行调度)**：将“出版成品”推向矩阵的瞬时动作，由指挥中心统一调配。
- **The Channels (发行渠道)**：具体的触达终端（如 GitHub, Netlify, Social Media 等）。

#### D. 统筹与主权 (Sovereignty)
- **Command Center (指挥中心)**：即 Dashboard，统筹“出版”与“发行”双重操作的物理载体。
- **Imprint (品牌)**：指代**独立出版项目**。它是系统逻辑运行与资源隔离的最高物理边界，是划定“出版版图”的最小主权单元。
    - *理解要点*：增加一个 Imprint 即代表“扩大出版疆域”。

### 2.3 术语主权红线 (Terminological Redlines)
- **硬性禁令**：
    - 严禁使用旧称 *Omni-Hub*。
    - **严禁使用英文单词 `Brand` 或 `Branding`**。技术层必须统一使用 `Imprint` 或 `Imprinting`。
    - **严禁使用中文单词“印记”**。UI 与对话层必须统一使用 **“品牌”**。
- **映射契约**：
    - **英文/技术域**：`Imprint` 优先。
    - **中文/用户域**：**“品牌”** 优先。

### 2.4 物理资产与安全锁定
- **Banner 锁定**：`core/ui/handlers/status_handlers.py` 的 ASCII 视觉资产严禁 AI 擅自修改。
    - *详见知识库*: `Status Handlers Banner Sovereignty Lock`
- **端口锁定**：43210-43213 端口物理锁定，严禁改动以避让冲突。
- **配置分层**：严格遵守 `config.local.yaml` > `config.yaml` 的主权优先级。

### 2.5 工程诚信 (Engineering Integrity)
- **语法敬畏**：严禁破坏 YAML Frontmatter 结构与组件标签（如 `<Card>`, `<Tabs>`）。
- **黑盒豁免**：严禁在文本清洗操作中处理 `[[STB_MASK_n]]` 类占位符。

### 2.6 架构隔离红线 (Architectural Isolation)
> [!CAUTION]
> **严禁“逻辑寄生”。核心引擎层 (core/) 必须保持纯净，严禁硬编码任何特定品牌或本地环境的物理路径。**

1. **环境脱敏**：严禁在 `core/` 目录下出现 `config.local.yaml` 或特定 Imprint ID 的硬编码字符串。
2. **上下文路由**：所有运行时配置必须通过 `gov/context.py` 或 `engine.config` 进行动态注入。
3. **物理拦截**：`sentinel_matrix.py` 将自动扫描核心层代码，检测是否存在路径泄露。

### 2.7 AI 控制器 Session 准入协议 (SOP-INIT)
> [!CAUTION]
> **本协议定义了 AI 在新 Session 启动时的强制自检行为。**

#### I. 启动即扫描 (Scan on Boot)
- **硬执行**：在任何新对话窗口的第一轮任务中，AI **必须**主动执行 `list_dir` 确认 `.plenipes/SOP` 目录的完整性。
- **关联挂载**：AI 必须读取 `RULES_INDEX.md`，并将其中的核心红线作为当前对话的“宪法”底座。

#### II. 准入声明 (Mandatory Declaration)
- **硬执行**：在第一个任务开始前，AI 必须向用户声明：“已成功挂载项目 SOP 规则集 (Vxx.x)，治理哨兵协议已点火。”

#### III. 认知持久化责任 (Persistence Responsibility)
- **要求**：禁止以“新窗口、不记得”为由规避既定规范。所有已存证的 SOP 均视为物理法律，AI 负有主动搜寻并遵守的终身责任。

---

## 3. 工程标准与质量标准 (Original SOP-02)

本章节定义了代码开发过程中的技术契约与物理约束。

### 3.1 物理写保护 (Writing Protection)
- **禁止盲写**：除非新建文件，否则严禁在未读取既有文件内容的情况下进行全量覆盖。必须先 `view_file` 确认后再修改。
- **最小侵入**：优先使用 `replace_file_content` 执行原子化修改，严禁不必要的全文件重写。

### 3.2 配置与元数据契约
- **配置主权层级**：所有配置修改必须明确其归属。凡涉及 **品牌 (Imprint)** 的特定逻辑，严禁污染全局 Base 配置，必须在品牌独立的 `config.yaml` 中进行闭环。
- **YAML 类型保护**：在 `config.yaml` 中修改版本号或 ID 时，必须显式加双引号 `" "`，防止解析器将其识别为 float 或 int。
- **插件元数据**：适配器类必须包含 `PLUGIN_ID`, `DISPLAY_NAME`, `DESCRIPTION`。

### 3.3 架构隔离
- **逻辑影子拦截 (Logic Shadowing)**：子类适配器仅允许实现 `_ask_ai` 等原子接口，严禁重写基类（BaseTranslator）的业务流程方法。

### 3.4 仿真验证 (Simulation Gating)
- **零回归保证**：修改 Egress 逻辑前必须执行物理仿真。

### 3.5 物理规模约束 (Physical Scale Constraints)
- **300 行红线**：所有后端模块 (.py) 与前端模块 (.js) 必须严格遵守 300 行物理行数限制。
- **强制重构**：当单文件超过 300 行时，必须通过“委托模式 (Delegation)”或“子插件化”进行物理拆分。
- **初衷**：确保每个治理单元的逻辑是可审计、可快速理解且低耦合的。

### 3.6 代码主权文档 (Documentation Sovereignty)
> [!CAUTION]
> **严禁“裸奔”代码。没有任何注释或类型标注的代码被视为无效资产。**

1. **Python 文档标准**：
   - 所有的 `class` 和 `def` 必须包含 `""" """` 风格的 Docstring，且必须使用中文描述。
   - 必须使用 `Type Hints` 进行参数 and 返回值的类型标注。
2. **Javascript 文档标准**：
   - 关键函数必须包含 `/** */` 风格的 JSDoc 注释。
3. **物理拦截**：上述标准由 `.plenipes/tools/sentinel_matrix.py` 进行物理审计。审计不通过严禁提交。

---

## 4. 逻辑契约与 API 设计 (Original SOP-09)

本章节旨在物理消除重构带来的业务逻辑 Regression。当修改核心算法、复杂业务规则或关键数据转换逻辑时，强制执行。

### 4.1 影子快照 (Shadow Snapshot) 准则
在对任何被标记为“核心逻辑”的函数进行重构前，AI 必须执行以下动作：
1. **捕获现状**：使用 `.plenipes/tools/logic_shadow.py --capture` 运行目标函数，并自动生成包含 I/O 对的 `.shadow` 文件。
2. **定义覆盖范围**：快照必须包含至少 5 组典型输入及所有已知的边界条件（Edge Cases）。

### 4.2 逻辑锁定与校验 (Locking & Verification)
重构完成后，AI 必须：
1. **运行对比**：执行 `.plenipes/tools/logic_shadow.py --verify`。
2. **100% 匹配要求**：除非重构的本意就是改变业务逻辑（需在 `logic_evolution.log` 中明确登记），否则输出必须与快照 100% 字符级对齐。

### 4.3 物理拦截
`sentinel_matrix.py` 将检查：
- 变更集中是否包含核心逻辑函数。
- 如果包含，是否已生成并验证了对应的 `.shadow` 报告。

---

## 5. 物理拓扑与运行契约 (Physical Topology & Operations)

本章节定义了系统在物理机上的运行形态，AI 助理必须确保任何重构不破坏这些物理契约。

### 5.1 物理启停命令 (Sovereign Commands)
| 场景 | 命令 | 物理行为 |
| :--- | :--- | :--- |
| **标准模式启动** | `python plenipes.py` | 启动 API 服务、同步引擎及文件守护 (Watchdog)。 |
| **启动向导模式** | `python plenipes.py --wizard` | 启动 Web 安装向导，用于初始化出版品牌 (Imprints)。 |
| **纯算力模式** | `python plenipes.py --headless` | 禁用控制台 Rich 视觉组件，仅以 JSON/Text 流输出。 |
| **紧急下线** | `python plenipes.py --shutdown` | 向运行中的 API 发送关机信号，安全导出账本快照。 |
| **状态回滚** | `python plenipes.py --rollback` | 将物理资产与数据库回滚至上一个同步点。 |

### 5.2 全量端口分配矩阵 (Port Matrix)
| 端口 | 职能定义 | 物理协议 | 约束说明 |
| :--- | :--- | :--- | :--- |
| **43210** | **单例互斥锁** | TCP/LOCK | 严禁占用，否则引擎将因“检测到多实例”物理熔断。 |
| **43211** | **版图配置向导** | HTTP/HTML | 对应 `--wizard` 模式，负责新版图的视觉化初始化。 |
| **43212** | **主权 API 门户** | REST/WS | 指挥中心主入口。重构路由时严禁导致 404。 |
| **43213** | **预览服务容器** | HTTP/STATIC | 负责 `target_base` 目录的物理预览呈现。 |
| **动态** | **算力心跳感知** | UDP/ICMP | 用于 ComponentMonitor 探测局域网内其他出版节点。 |

### 5.3 核心模块职责图谱 (Architecture Landscape)
- **`core/runtime/`**: **动力系统**。负责工厂装配、单例锁定、同步策略及生命周期守护。
- **`core/api/`**: **指挥系统**。承载 RESTful 路由、WebSocket 实时链路及 UI 静态资源。
- **`core/editorial/`**: **生产系统**。负责 Markdown AST 解析、资产流水线及出版物分发。
- **`core/governance/`**: **法务系统**。负责审计 (Audit)、健康扫描 (Doctor)、秘密管理及账本计量。
- **`core/ingress/`**: **采编系统**。负责 Notion/Obsidian/Local 等不同源稿渠道的接入适配。
- **`core/adapters/`**: **外设系统**。负责与大模型 (AI)、SSG 工具 (Docusaurus/Starlight) 的物理对接。

---
*代码可以变美，但灵魂必须保持一致。*
