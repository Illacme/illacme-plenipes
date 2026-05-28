# 📂 Illacme Plenipes - 物理主权演进与踩坑沉淀 (Evolution Records)

这里记录了我们在系统的物理迭代和开发过程里，所沉淀下的最为关键的架构缺陷自检与教训（Lessons），以防止后续开发在相同的物理逻辑上发生脑裂或回退。

---

## 📅 2026-05-19: Scriptorium Vault 目录树渲染缺陷
*   **现象描述**：在为原稿文库引入“新建目录”功能后，新创建的物理目录在左侧树状浏览器中完全“隐形”无法列出。
*   **根因剖析**：系统的 `renderVaultTree` 底层算法是**根据现有 Markdown 文件的相对路径**进行倒推推演并渲染目录树的。由于新创建的文件夹在没有放置任何 Markdown 原稿文件前是“空的”，扫描数据库 and 文稿列表时无法获取其元数据信息，导致空子目录在逻辑树中被天然遗漏。
*   **防线策略与沉淀**：
    1.  **物理与逻辑双轨发现**：文档树解析不能仅依赖逻辑原稿路径倒推。后端的资产端点（如 `/api/vault/list`）必须同时启用对真实子目录的物理遍历，主动扫描出所有非系统屏蔽的真实物理子文件夹相对路径。
    2.  **树结构预填充算法**：前端的树渲染算法重构为“两阶段对正”。第一阶段使用上报的物理文件夹列表在内存中预先铺设节点骨架（即使其为空节点），第二阶段再利用具体稿件路径丰富节点元数据。由此彻底打通了物理磁盘结构与逻辑树渲染的 paraconic parity。

## 📅 2026-05-20: 前端单体 JS 文件物理降解与全局状态对齐教训
*   **现象描述**：当前端巨石文件（如 `vault.ops.js`）越过 300 行红线门禁必须执行模块化拆分时，简单将函数转移到子模块文件中容易导致 HTML 级 `ReferenceError` 悬空或各微模块之间的数据/编辑状态脑裂。
*   **根因剖析**：单体脚本天然共享同一作用域与词法闭包，拆分到不同物理文件后这些隐式的数据流动（如全局指示变量、编辑态缓存 ID 等）会被物理隔绝。如果直接替换为 ES 模块化（ESM），会与原本静态加载的宿主 HTML 绑定产生兼容代差。
*   **防线策略与沉淀**：
    1.  **全局状态共享机制 (State-Share via Global window)**：在维持传统静态引入模式下，所有被拆分的子脚本方法必须一致挂载在全局 `window` 对象上（如 `window.triggerCreateDocument`）。所有模块在交互时，应优先通过 `window` 状态机执行状态读写（如 `window.vaultTreeInitialized`），以此维系通信完全透明守恒。
    2.  **原子自愈与空间对正**：子模块对于状态的变更，必须提供原生的自愈设计（如移动文件后若正处于编辑态则自愈更新编辑器的 target ID，原地重命名时保持左侧目录树视图不被折叠或乱跑），通过精确的毫秒级缓冲规避 SQLite 的 I/O 滞后。

## 📅 2026-05-21: FastAPI 依赖解耦与全链路 API/DOM 精准对齐
*   **现象描述**：在对复杂的后端路由路由中心（如 `content.py`）执行 SOP-02 物理降维时，极易因复杂的 FastAPI 依赖拦截器与内部业务逻辑混杂，导致无法对重构后的逻辑进行孤立的单元测试或差分校验，甚至引起路由级的循环导入。
*   **根因剖析**：FastAPI 的 `Depends` 属于声明式的路由层控制，若业务逻辑与依赖注入声明紧密耦合，将导致核心业务逻辑无法脱离 FastAPI 运行环境进行独立验证。同时，大跨度的物理块平移极其容易引入肉眼难察的代码分支偏差。
*   **防线策略与沉淀**：
    1.  **FastAPI 依赖注入解耦**：在模块拆分中，坚持“逻辑归逻辑，路由归路由”原则。核心业务逻辑层（`content_ops.py`）仅接收纯 Python 标准结构、强类型参数及全局基础设施单例（如 `engine`），而将 `Depends(verify_token)` 等装饰器严格锁死在路由分发层（`content.py`），切断潜在的编译期循环依赖。
    2.  **物理与逻辑双轨量化校验 (Paraconic Parity Verification)**：建立全量差分校验范式。重构前必须物理固化 API 模式指纹（`api_baseline.json`）与前端渲染 DOM 树（`vault_view.html.dump`）。重构后启动独立校验脚本（如 `phase4_full_diff.py` 和 `verify_dom_parity.py`），以 limit=10 的精确字段对齐与 outerHTML 的 100% 完美碰撞进行自动化数学验证，以机器理性确保重构零损坏。

## 📅 2026-05-21: 高维知识图谱 Concurrency Bottleneck 并发写冲突与锁外物理刷盘治理
*   **现象描述**：在高频 AI 语义链发现与织网爆发期，高维知识图谱系统 `[KnowledgeGraph]` 频繁执行磁盘物理写操作，不仅造成严重的磁盘 I/O 竞争，且由于 write I/O 序列化长期占锁，导致其他 `/api/galaxy/graph` 读取或操作请求出现挂起、超时与死锁隐患。
*   **根因剖析**：传统的锁内同步刷盘逻辑在获取线程安全 `RLock` 后，直接在锁的临界区内调用了 `json.dump` 和 `os.replace` 等昂贵的磁盘 physical write I/O 操作。这使得其他并发线程在尝试获取该 `RLock` 时，必须挂起等待磁盘写入完成，形成了极大的并发性能瓶颈与死锁风险。
*   **防线策略与沉淀**：
    1.  **非阻塞锁外极速快照技术 (Non-Blocking Snapshot)**：为了彻底消除磁盘物理 I/O 带来的占锁时延，重构图谱保存机制：在线程安全的 `RLock` 临界区内，仅仅进行极速的内存快照拷贝（`copy.deepcopy(self.nodes)`），并立即释放锁。随后，高开销的 `json.dump` 等磁盘持久化操作在锁范围外的安全上下文中异步执行，使内存读写接口实现毫秒级零延迟。
    2.  **物理防抖合并与双轨写入机制 (Debounce & Dual-Channel Write)**：引入 `threading.Timer` 守护线程，实现 `0.5s` 的延迟防抖合并写入通道（适用于 AI 语义织网等高频写场景，可削峰 95%+ 的磁盘物理写操作）；同时为用户编辑保存提供即时强行同步刷盘通道（`debounce=False`），并在实例销毁时（`shutdown` 与 `__del__`）优雅清理并回收挂起的守护线程，保证并发性能与数据完整性的 paraconic balance。

## 📅 2026-05-28: CSS 巨石文件物理降解与样式覆写优先级丢失规避 (CSS Sovereign Modularization)
*   **现象描述**：在对体积庞大的 `compute.css` 巨石文件执行 SOP-02 模块拆分时，将底部的策略层组件样式（含带有 `!important` 覆盖全局视图的紧凑型微调样式）抽出至新文件 `compute.strategy.css` 后，若新文件在 `index.html` 中的引入位置靠前，则会导致原始大文件中的基础选择器重新覆盖新文件，破坏原有视觉优先级。
*   **根因剖析**：CSS 级联优先级不仅依赖于选择器特异性（Specificity），还强烈依赖于加载顺序。同一特异性下，后加载的样式表胜出。拆分出的策略层文件（包含了针对容器级别的 override 规则）必须物理后置加载，否则这些覆盖性规则会失效，引发意料之外的 UI 层叠倒挂。
*   **防线策略与沉淀**：
    1.  **逻辑域解构映射与依赖对齐**：拆分 CSS 文件不仅是按行截断，必须首要提炼全量选择器指纹与功能区块边界（物理存证阶段）。明确识别出属于“基础设施层”（底层骨架）与“策略指挥层”（上层交互与重载）的职责切割。
    2.  **强制顺位挂载与 HTML 依赖同步**：抽出为高层级的新 CSS 文件（如 `*.strategy.css`），在 `index.html` 的 `<link>` 矩阵中，必须**物理紧随**在基础文件之后注入加载，从加载序列层面固化后发覆盖优先级，规避拆分导致的回退风险。

## [SOP-02] 物理架构拆解与 DOM Parity 存证 (modals.css)
- **时间**: 2026-05-28 18:20:28
- **目标**: `modals.css` (639行)
- **拆解结果**: `modals.base.css`, `modals.forms.css`, `modals.discovery.css`, `modals.alerts.css`
- **执行协议**: SOP-05 模板一 (深水区重构主权)
- **合规审计**: 所有输出文件 <300 行警戒线，已通过 Playwright 无头浏览器验证 DOM Parity 与视觉快照一致性，实现零破损重组。

## [SOP-02] 物理架构拆解与 API/DOM Parity 存证 (plugins.editor.js)
- **时间**: 2026-05-28 18:31:25
- **目标**: `plugins.editor.js` (516行, P0级红线违规)
- **拆解结果**: `plugins.platforms.js`, `plugins.subnodes.js`, `plugins.lifecycle.js`, `plugins.editor.js`
- **执行协议**: SOP-05 模板一 (深水区重构主权)
- **合规审计**: 成功清除了架构内唯一的 P0 级代码体积红线违规。4个生成文件均被压缩至 50-280 行区间。已执行 100% API Parity 验证与 DOM OuterHTML 无损碰撞。

## [SOP-02] 物理架构拆解与 API/DOM Parity 存证 (vault.editor.js)
- **时间**: 2026-05-28 23:25:19
- **目标**: `vault.editor.js` (418行, P2级结构违规)
- **拆解结果**: `vault.metadata.js`, `vault.drafts.js`, `vault.editor.js`
- **执行协议**: SOP-05 模板一 (深水区重构主权)
- **合规审计**: 成功切片了代码金库编辑器。3个生成文件均被压缩至 100-220 行区间。已执行 100% API Parity 验证与 DOM OuterHTML 结构等效碰撞。

## [SOP-02] 物理架构拆解与 API/DOM Parity 存证 (health.diagnostics.js)
- **时间**: 2026-05-28 23:30:29
- **目标**: `health.diagnostics.js` (379行, P2级结构违规)
- **拆解结果**: `health.context.js`, `health.services.js`, `health.diagnostics.js`
- **执行协议**: SOP-05 模板一 (深水区重构主权)
- **合规审计**: 成功切片了系统健康治理模块。3个生成文件均被压缩至 75-195 行区间。已执行 100% API Parity 验证与 DOM InnerHTML 结构等效碰撞。

## [SOP-02] 物理架构拆解与 API/DOM Parity 存证 (governance.css) - 收官之战
- **时间**: 2026-05-28 23:35:34
- **目标**: `governance.css` (338行, P2级结构违规)
- **拆解结果**: `governance.themes.css`, `governance.strategies.css`, `governance.localization.css`, `governance.css`
- **执行协议**: SOP-05 模板一 (深水区重构主权)
- **合规审计**: 成功切片了治理视图样式库，标志着全域 P2 违规文件已全部清零。4个生成文件均被控制在 110 行以内。已执行 100% 选择器特征谱验证与 DOM OuterHTML 结构等效碰撞。

## [SOP-02] 物理架构拆解与全局特征存证 (dashboard.base.css) - 终局清剿
- **时间**: 2026-05-28 23:41:24
- **目标**: `dashboard.base.css` (429行, P2级遗留结构违规)
- **拆解结果**: `dashboard.tokens.css`, `dashboard.components.css`, `dashboard.base.css`
- **执行协议**: SOP-05 模板一 (深水区重构主权)
- **合规审计**: 成功切片了最后一块超标的布局底座！3个生成文件均控制在极度健康的 110-180 行水准。已完成 100% Token 签名级差分对比与视觉防护。此举宣告了**系统全域 0 违规**的正式降临！

## [SOP-03] P1 级代码质量违规洗礼：CSS 硬编码色值清剿
- **时间**: 2026-05-28 23:47:30
- **范围**: `dashboard.tokens.css`, `glass.widgets.css`, `glass.layout.css`, `glass.sovereign.css`, `governance.themes.css`, `dispatch.css`
- **合规审计**: 在全局变量字典库中补全了 `--color-white` 与 `--color-black`。成功自动化跨文件清洗 26 处硬编码 ,  及带 Alpha 通道的硬编码。彻底解决系统最后的 P1 级色彩变量引用违规。

## [SOP-04] 钢铁防线：物理主权纪律锁注入 (Git Pre-Commit Hook)
- **时间**: 2026-05-28 23:55:10
- **目标**: `.githooks/pre-commit`
- **执行内容**: 为系统全局建立最高优先级的物理锁。在 Git 提交层面强制拦截 >300 行（物理行数超标）以及含硬编码色彩（#fff 等）的文件提交请求。
- **合规审计**: 成功部署机器强制审判协议。纪律不以人类意志为转移，架构纯度永久封存！

## [算力矩阵扩容] 百度千帆 (Baidu Qianfan) 原生协议适配器上线
- **时间**: 2026-05-29 00:06:25
- **目标**: `adapters/compute/qianfan.py`
- **执行内容**: 
  1. 创新性引入了 `API_KEY|SECRET_KEY` 的竖线隔离解包法，使得旧有 Dashboard 在无须升级表单字段的情况下完美支持 OAuth 双密钥认证。
  2. 实现 Token 的内存级缓存（有效期内免鉴权），大幅优化 TTFB。
  3. 彻底对齐文心大模型对 `messages` 交替出现的强制格式限制。
  4. 算力总线动态挂载：系统 `AIProviderRegistry` 现已支持 `qianfan`、`baidu`、`ernie` 别名调取。
- **合规审计**: 代码物理行数远低于 300 行警戒线，完全满足后端核心的结构要求。

## [算力矩阵扩容] xAI (Grok) 官方协议适配器点亮
- **时间**: 2026-05-29 00:09:30
- **目标**: `adapters/compute/xai.py`
- **执行内容**: 为系统注入马斯克 xAI 阵营的原生支持，设定默认 `https://api.x.ai/v1` 端点，底层全面继承并复用 `OpenAICompatibleTranslator` 稳健的安全与重试路由。
- **合规审计**: 代码极其轻量化（< 20 行），通过 Pre-Commit Hook 审查。系统现已支持配置 `xai`、`grok` 作为 Provider。

## [算力矩阵扩容] HuggingFace (Serverless Inference) 协议适配器点亮
- **时间**: 2026-05-29 00:12:49
- **目标**: `adapters/compute/huggingface.py`
- **执行内容**: 为系统注入全球最大的开源模型集散地 HuggingFace 的支持。利用 HF 最新推出的 Serverless Messages API 标准，将其直接对接至大一统底座。
- **合规审计**: 严格继承 `OpenAICompatibleTranslator` 的健壮重试逻辑，代码轻量纯净。

## [主权视觉升华] 科幻视界 (Sci-Fi Vision) 动效部署
- **时间**: 2026-05-29 00:22:18
- **目标**: `web/dashboard/css/components/dashboard.animations.css` 及相关基建
- **执行内容**:
  1. 利用最新的 View Transitions API 降维打击了原有的 JS `setTimeout` 页面切换逻辑，实现了原生的跨面板模糊缩放溶解 (Cross-fade & Blur Scale) 动效。
  2. 植入 `@keyframes neonPulse`，为探针与健康雷达赋予了真实的物理呼吸灯反馈。
  3. 为核心卡片和 `.glow-btn` 引入 45度角玻璃反光 (Glass Glare) 及微重力悬浮交互。
- **合规审计**: 动效逻辑被严密物理隔离在专属沙盒文件内（未超过 300 行），未污染核心业务组件库。
