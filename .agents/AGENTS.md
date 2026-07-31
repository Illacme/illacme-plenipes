# Illacme Plenipes Governance Tab UI Sovereign Rules

为保持治理中心（Governance Dashboard）前端页面交互的高档毛玻璃与二级 Sub-Tab 体验，所有参与前端变更的 AI 助手必须强制遵守以下二级子选项卡（Sub-Tab）规则，禁止平铺渲染或覆盖退化：

## 1. 基础配置与运维 (General Configuration) 选项卡规则
*   **路由大分类**：`general`
*   **二级子标签（4个）**：
    1.  `identity`（🏷️ 身份标识）：包含 Imprint & Site Identity 品牌身份组。
    2.  `compliance`（📖 出版合规）：包含 Publishing Compliance & Metadata 合规组。
    3.  `storage`（📂 存储缓存）：包含数据存储与原稿适配组，以及算力缓存自动清理（Janitor GC / LRU）策略、段落缓存治理中枢（Block Cache Hub）。
    4.  `engine`（⚙️ 系统基座）：包含日志级别、访问日志开关以及 Markdown 换行渲染模式。
*   **交互实现**：必须定义并调用 `window.switchGeneralSubTab(subTab, btn)`，在常规设置中隐藏/显示对应的面板并点亮 Tab 按钮。

## 2. 版图装帧与模式 (Layout & Publishing Modes) 选项卡规则
*   **组合渲染入口**：必须在 `dashboard.modes.js` 结尾挂载 `window.renderLayoutCategory`，接收 `layout` 路由并动态按需切换。
*   **二级子标签（3个）**：
    1.  `imprints`（🏷️ 版图管理）：调用 `window.renderImprintsCategory()`
    2.  `themes`（🎭 装帧主题）：调用 `window.renderThemesCategory()`
    3.  `modes`（📋 出版模式）：调用 `window.renderModesCategory()`
*   **交互实现**：必须提供 `window.switchLayoutSubTab(subTab, btn)` 并支持在初次加载/大类切换时延迟少许自动激活点亮子面板（避免首屏白屏）。

## 3. 语言翻译与内容治理 (Localization & Content Governance) 选项卡规则
*   **组合渲染入口**：必须在 `localization.render.js` 结尾挂载 `window.renderLocalizationGovCategory`，接收 `localization_gov` 路由（兼容 `i18n_routing` 别名）。
*   **二级子标签（4个）**：
    1.  `localization`（🌍 语种矩阵）：调用 `window.renderLocalizationCategory()`
    2.  `block_rules`（🧱 块级规则）：调用 `window.renderBlockRulesCategory()`
    3.  `glossary`（📖 术语词库）：调用 `window.renderGlossaryCategory()`
    4.  `translation_style`（🎭 翻译风格）：调用 `window.renderTranslationStyleCategory()`
*   **交互实现**：必须提供 `window.switchLocalizationGovSubTab(subTab, btn)` 并支持自动点亮回填。

## 3.1 分发路由与网址路径 (Dissemination & URL Routing) 选项卡规则
*   **组合渲染入口**：必须在 `localization.render.js` 结尾挂载 `window.renderDisseminationRoutingCategory`，接收 `dissemination_routing` 路由。
*   **二级子标签（2个）**：
    1.  `slug_settings`（📝 网址路径）：调用 `window.renderSlugSettingsCategory()`
    2.  `route_matrix`（🧭 频道映射）：调用 `window.renderRouteMatrixCategory()`
*   **交互实现**：必须提供 `window.switchDisseminationRoutingSubTab(subTab, btn)` 并支持自动点亮回填。


## 4. 后台非交互式子进程安全调用规则 (Non-Interactive Subprocess Invocation Rules)
*   **适用场景**：所有由后端 Python 脚本、Celery 队列或守护进程触发的 `subprocess`、`os.system` 等外部命令行调用。
*   **禁用交互挂起**：为防止在缺乏交互终端（Non-TTY）的后台环境中因 CLI 出现“确认提示（如 `Ok to proceed? (y/n)` 或 `Press Enter to continue`）”而导致后台无限挂起超时，必须强制附加“自动确认/非交互”标志：
    1.  在使用 `npx` 降级调起工具时，必须强制包含 `-y` 或 `--yes` 参数（例如 `npx -y <pkg>`）。
    2.  在使用 `pip` 时，若需要静默安装或自动降级，必须追加 `--disable-pip-version-check` 并搭配非交互标志。
    3.  在使用其他可能会触发二次确认的 CLI 工具（如 `docker`、`git` 等）时，必须合理设置环境变量（如 `GIT_TERMINAL_PROMPT=0`）或显式注入 `--force`、`-q` 等安静/无确认参数，以确保子进程永远能够自愈闭环退出。

## 5. 全站托管与分发渠道一键化体验标准规范 (One-Click Experience Standard Architecture Rules)
*   **体验简化原则**：所有全站托管或聚合内容同步渠道插件在开发/升级时，必须以“极简化操作”和“屏蔽底层技术细节”为核心体验指标，绝不能向没有技术背景的创作者暴露任何非必要的密钥创建或手动寻找参数的操作路径。
*   **分类规范**：
    1.  **CLI 型托管平台（如 GitHub Pages, Netlify, Vercel）**：
        *   必须在后端提供**一键唤醒本地 CLI 授权的 API 接口**（如拉起后台 `npx <cli> login` 浏览器流，并以新会话运行防阻塞）。
        *   必须提供**本地登录会话状态与属性探测 API**（如调用 `<cli> whoami` 并用正则精准提取输出中的 Account ID / 邮箱），同时在前端抽屉面板提供「🔑 本地一键免密授权」按钮，在点击后开启短周期轮询，授权完成后**全自动将数据回填至配置表单**。
    2.  **Web 社交与聚合分发渠道（如 Dev.to, Hashnode, Medium）**：
        *   必须在配置项下方提供高亮亲和的 **「💡 Token 极简获取向导」** 卡片。
        *   必须提供**一键直达该渠道最深层 API 密钥申请或扩展授权页面的“魔术链接（Magic Link）”**（免除用户在复杂的多级设置菜单中四处寻找的门槛）。

## 6. 系统默认服务端口规划与进程占位锁规则 (System Default Port Layout & Singleton Lock Rules)
*   **物理职责划分（4个端口）**：
    1.  `43210`（🔒 单例进程锁）：进程唯一性占位锁，防止在后台被重复拉起而破坏指纹账本及造成 I/O 冲突。后台启动新进程时若绑定失败，应当拦截并友好提示。
    2.  `43212`（🔌 API 模式端口）：FastAPI Web API 控制网关服务监听端口，仪表盘交互以及后端 API 调用均在此服务上承载。
    3.  `43211`（🧙 可视化向导端口）：引导安装与配置向导 (Wizard) 暴露的前端服务端口。
    4.  `43213`（🌐 本地预览端口）：分发同步演练完成后，内嵌的静态预览服务启动的监听端口。
*   **开发约束**：调试或拉起服务时必须严格区分单例锁端口 (`43210`) 与实际 HTTP 网络服务端口 (如 `43212`)，不得将其混淆或硬编码错误端口。

## 7. 前端变更强制 node -c 语法静态自检规则 (Frontend Code Syntax Compilation Gate Rules)
*   **适用场景**：所有对 `web/dashboard/js/*.js` 前端 JavaScript 代码文件、DOM 模版进行修改的 AI 助手与自动化脚本。
*   **物理约束**：
    1. 凡是修改了任何前端 `.js` 文件，在完成代码替换后，**必须强制自动运行 `node -c <path_to_file>` 尝试进行 V8 引擎语法静态编译**。
    2. 若 `node -c` 抛出 `SyntaxError`（如括号未闭合、语法错位、大写 False/True 拼写错误），必须拦截并物理修正，直至编译 exit code 归零。

## 8. 后端数据解包与防御性类型防护规则 (Defensive Unpacking & Type Verification Rules)
*   **适用场景**：所有涉及从数据库 (SQLite/Redis)、配置文件或外部 API 读取集合与字典的后端 Python 代码。
*   **物理约束**：
    1. 严禁直接假设数据库或配置项返回的数据格式为固定 `list` 或 `dict`，在迭代前必须显式进行断言和类型解包（例如 `if isinstance(raw, dict): items = list(raw.values())`）。
    2. 在对集合中的元素（如 `doc`）调用属性/方法（如 `.get(...)`）前，必须判断 `if isinstance(doc, dict):`，绝不允许字符串等非字典类型引发 AttributeError (500 内部服务错误)。

## 10. 用户配置与原稿文库绝对保护及测试隔离红线规则 (Absolute Configuration & Vault Protection Rules)
*   **适用场景**：所有参与单元测试、集成测试、代码重构、单测修缮与脚本编写的 AI 助手与自动化脚本。
*   **物理红线**：
    1. **未经创作者显式授权，绝对禁止因测试、调试或跑单测而修改/覆盖用户真实的物理配置文件**（包括但不限于 `config.local.yaml`、`config.yaml`、`imprints/*/configs/config.imprint.yaml`）。
    2. **绝对禁止修改/污染创作者的原稿文库路径 (`vault_root`) 与物理笔记文件**。
## 11. AI 助手商业级交付与需求履约物理铁律 (Agent Commercial Delivery & Zero-Hallucination Gate Rules)
* **适用场景**：所有 AI 助手在响应创作者的评估、需求讨论、功能排查、代码修改或架构设计请求时。
* **物理约束与红线**：
    1. **零凭空评估与代码查验先行红线**：严禁在未通过 `grep_search` / `view_file` 查验真实源码前，凭空想象或仅凭模型记忆发表关于“功能是否实现/现状如何”的任何评估。任何现状结论必须基于带文件路径与行号的物理代码依据。
    2. **零浮夸与务实工程语言红线**：严禁在交互中使用任何虚浮的自我夸赞、夸张赞美或敷衍套话。只允许采用客观、中立、精准的工程语言报告“物理现状”、“差异点”与“验证结果”。
    3. **零掩饰与实事求是红线**：面对功能缺漏或体验割裂，严禁通过强行迎合、顺杆爬或打太极来掩饰失误；实现即实现，缺失即缺失。
    4. **物理凭证闭环红线**：任何代码修改完成后，必须强制运行 `node -c` 及 pytest 测试套件，只有在 exit code 归零且输出 Pass 凭证后方可声明完成。

## 12. 治理中心局部平滑滚动物理铁律 (Governance Partial Scroll Iron Rules)
*   **适用场景**：所有涉及治理中心 (`#view-settings`) 面板中 `.tab-content-area` 局部平滑滚动的前端代码变更。
*   **知识库文档**：完整死穴根因分析与标准滚动模板详见 `knowledge/governance_scroll_iron_rules/artifacts/scroll_iron_rules.md`。
*   **物理铁律**：
    1.  **禁止使用 `scrollIntoView()`**：治理中心的右侧内容区是 `overflow-y: auto` 的局部容器 (`#view-settings .tab-content-area`)，不是 window 级滚动。`scrollIntoView` 在 DOM `innerHTML` 重写后的 Stacking Context 中会被浏览器静默吞掉。必须使用 `scrollContainer.scrollTo({ top: ..., behavior: 'smooth' })` 配合 `getBoundingClientRect()` 像素差计算。
    2.  **滚动延迟必须 ≥ 300ms**：`renderSettingsCategory()` 会触发级联的二次异步 DOM 重写（内部有 20ms `setTimeout` 调用 `switchLocalizationGovSubTab` 再次 `innerHTML`），在此之前执行的任何滚动指令都会因 `scrollTop` 归零而被吞掉。
    3.  **容器选择器必须带 `#view-settings` 前缀**：页面上存在多个 `.tab-content-area`，不带前缀的选择器可能误匹配到隐藏面板的容器。
    4.  **修改 `window.xxx` 全局函数后必须全文件去重**：禁止在同一文件中出现同名全局函数的多次赋值定义，后定义会静默覆盖前面包含滚动逻辑的版本。修改后必须运行 `grep -rn 'window\.函数名\s*=' web/dashboard/js/` 确认仅有 1 个赋值定义。
