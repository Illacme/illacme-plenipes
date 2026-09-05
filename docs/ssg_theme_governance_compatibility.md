# Illacme Plenipes 治理中心配置项与各类 SSG 主题兼容性深度穿透分析

## 1. 架构本质与 SSG 主题分类全景

在评估治理中心的各项配置在各 SSG 主题下的支持度之前，必须首先从工程底层厘清两类截然不同的主题运行机制：

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                Illacme Plenipes 核心编排引擎                            │
│                     (原稿扫描 · AI 翻译/SEO · 语法清洗 · 路由计算 · 资产归集)              │
└─────────────────────────────────────────┬──────────────────────────────────────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
     【类别 A：原生编译直出引擎】                      【类别 B/C：第三方生态框架适配器】
       (In-House Built-in)                             (Third-Party Ecosystem)
  • Sovereign (官方旗舰 Astro/原生)             • Docusaurus (React/Webpack)
  • Universal (轻量极速纯静态直出)                 • VitePress (Vue/Vite)
                                                • Starlight (Astro)
                                                • Nextra (Next.js/MDX)
                                                • Hugo (Go) / Hexo (Node)
  ┌───────────────────────────────┐             ┌───────────────────────────────┐
  │ • 系统掌控编译/渲染全生命周期   │             │ • 系统充当原稿与脚手架预处理机 │
  │ • 内置完整 AST 语法与双链解析 │             │ • 输出 Markdown/MDX 源码与配置│
  │ • HTML/CSS/DOM 级像素精准控制 │             │ • 交付给第三方打包器进行二次编译│
  │ • 100% 动态拓扑与跨级链接自愈 │             │ • Docusaurus/Starlight 原生组件│
  │ • 零第三方打包依赖，毫秒直出  │             │ • 拓扑图谱与出版合规已深度打通│
  └───────────────────────────────┘             └───────────────────────────────┘
```

---

## 2. 各核心配置大类在各类 SSG 下的支持情况穿透分析

### 2.1 分发路由与网址路径 (Dissemination & URL Routing)

#### ① 网址路径组织形态 (`slug_dir_mode`: `nested` / `flat` / `prefix`)
*   **原生主题 (Sovereign / Universal)**：**🟢 100% 原生支持**
    *   **底层物理逻辑**：由 `core/editorial/router.py` 驱动落盘，同时原生主题在渲染阶段拥有 `syntax_resolver.py` 与 `_resolve_content_links`，能根据当前选定的 `slug_dir_mode`，动态计算所有页面间相互引用的相对路径并重写超链接。
    *   无论是平铺至根目录的 `flat`、拼接连字符的 `prefix`，还是保持文件夹层级的 `nested`，原生主题均可保证**内链 100% 互通、0 坏链、0 404**。
*   **第三方框架 (Docusaurus / VitePress / Starlight / Nextra / Hugo / Hexo)**：**🟡 推荐使用 `nested`；`flat`/`prefix` 受限于框架规范**
    *   **底层物理逻辑**：第三方框架全部采用**“基于文件系统的路由（File-based Routing）”**。它们的侧边栏菜单（Sidebar）、面包屑导航、多语言切分，深度依赖源码磁盘目录树（如 `docs/tech/guide.md`）。
    *   **架构边界**：
        1.  **Docusaurus / Starlight**：虽然可以通过 Frontmatter 中的 `slug:` 字段自定义访问 URL，但其物理源码文件仍建议保持嵌套目录结构，否则侧边栏层级自动生成逻辑会完全退化为扁平列表。
        2.  **VitePress / Nextra**：**官方压根不支持 Frontmatter `slug` 别名覆盖**，它们的 URL 路径与物理 `.md` 文件的磁盘相对路径强制 1:1 绑定。若在 Illacme 中强行开启 `flat`，物理源码全部落盘在根目录，将导致 VitePress 的侧边栏无法分层，且多语言目录结构崩塌。
    *   **落地方案**：治理中心前端已明确标注：第三方框架推荐锁定为<b>【📂 目录树复刻 (nested)】</b>。

#### ② 基础命名法则 (`slug_mode`: `ai` / `filename`)
*   **原生主题**：**🟢 100% 支持**（AI 语义生成精炼英文短网址，或物理文件名安全清洗）。
*   **第三方框架**：**🟢 100% 支持**（上游在生成目标文件时已完成文件名与 Frontmatter slug 的转换，第三方打包器直接消费生成后的文件名）。

#### ③ 频道映射矩阵 (`route_matrix`)
*   **原生主题**：**🟢 100% 支持**（文件夹精确映射为 `docs`、`blog`、`showcase` 等频道，并渲染对应的频道模板与列表页）。
*   **第三方框架**：**🟡 依靠 Feature Slots 槽位映射**
    *   第三方框架通过各自适配器中声明的 `get_feature_slots()`（如 Hugo 的 `content/blog`，Docusaurus 的 `blog`，Hexo 的 `source/_posts`）将特定频道的稿件投递到框架规定的专属目录。如果创作者在治理中心自定义了非常规频道名，第三方框架可能需要手动增配对应的脚手架路由。

#### ④ 独立单页与 Clean URL 坍缩治理 (Slot Pages & Anti-Nesting Shield)
*   **全引擎全矩阵支持**：**🟢 100% 规则对齐与物理测试闭环**（经 `tests/test_slot_pages_full_matrix.py` 严格验证）。
    *   **8 大主流引擎单页落盘契约**：根单页（如 `about.md`、`terms.md` 等）根据框架规范投递至专用槽位：
        *   Starlight: `src/content/docs/about.md`（多语：`src/content/docs/{lang}/about.md`）
        *   Docusaurus: `src/pages/about.md`（多语：`i18n/{lang}/docusaurus-plugin-content-pages/about.md`）
        *   VitePress / Universal: `about.md`（多语：`{lang}/about.md`）
        *   Nextra: `pages/about.md`（多语：`pages/{lang}/about.md`）
        *   Hugo / Sovereign: `content/about.md`（多语：`content/{lang}/about.md`）
        *   Hexo: `source/about.md`（多语：`source/{lang}/about.md`）
    *   **同名单页 Clean URL 自动坍缩折叠**：`RouteManager` 具备智能坍缩算法，当单页的频道前缀与 Slug 相同（如 `channel="about", slug="about"`）时，自动折叠为单级 Clean URL（如 `/about`、`/en/about`），**彻底消灭 `/about/about` 这类套娃路径**。
    *   **根目录双重套娃拦截网 (Anti-Nesting Shield)**：当脚手架 Base Path（如 `content`、`source`）与文档自身前缀重叠时，系统自动识别并剥离首级冗余，严防生成 `content/content/about.md` 或 `source/source/about.md`。
    *   **跨层级根单页双链解析**：无论在根目录还是深层文档中，引用 `[[about|关于我们]]` 均能精准计算相对路径或 Clean URL 自愈。

#### ⑤ 独立单页跨引擎寻址与 Base URI 规避偏移标准 (Base URI Parity & Anti-Drift Guard)
*   **各引擎架构差异与关键分水岭**：
    *   **现代前端生态应用（Starlight / Docusaurus / Nextra）**：
        *   运行于现代前端打包管线之上，路由基于框架的虚拟 Clean URLs（如 `/about`、`/en/about`），浏览器的 Base URI 恒定锚定在根域 `/`。
        *   无论处于何种单页，浏览器端正文的相对链接和顶栏导航链接均受 SPA 路由器或绝对虚拟路径统一接管，**天生免疫相对目录层级偏移**。
    *   **原生极速直出引擎（Sovereign / Universal）**：
        *   输出纯静态 `.html` 物理文件，全站 CSS/JS 资源引用、正文跨文档引用、顶栏导航菜单**深度依赖静态相对路径**（`./` 或 `../`），具有零外部打包依赖、零运行时服务开销的极致轻量优势。
        *   **死穴与 Base URI 漂移陷阱**：
            *   物理落盘上，单页生成在站点根目录（如 `dist/about.html`，多语言为 `dist/en/about.html`），磁盘根本不存在 `about/index.html` 实体文件。
            *   若导航合成器或模版引擎将独立单页误视作频道专区（如 `docs/`、`blog/`），拼装出目录型链接 `<a href="./about/index.html">`；
            *   当创作者或访客点击该链接后，浏览器地址栏将停留在 `http://domain/about/index.html`（或 `http://domain/about/`）。
            *   此时，**浏览器的基准路径（Base URI）被浏览器强制提升并锁定到了 `/about/` 目录下**！
            *   由此产生灾难性的“连锁漂移”：页面内部所有正常的相对路径（如快速入门 `./docs/quick-start.html`、返回首页 `./index.html`、以及再次点击关于我们 `./about.html`），都会被浏览器按 `/about/` 进行拼接，分别解析为 `/about/docs/quick-start.html` 和 `/about/about.html`，不仅所有内链瞬间 404，且连续点击关于我们时会产生 `/about/about/about/...` 的**无限递归套娃死循环**。
*   **Illacme 全链路三大物理防御铁律**：
    1.  **铁律 1（导航合成器单页排他规范）**：
        *   物理文件：`core/adapters/egress/ssg/base_shards/ssg_nav_synthesizer.py`
        *   在非 clean-url 模式下，`SSGNavSynthesizer` 显式侦测 `is_standalone_page = (slot in ("pages", "page") or prefix in ("about", "terms", ...))`，强制输出 `/{prefix}.html`（如 `/about.html`），绝不生成目录型伪路径 `/{prefix}/`。
    2.  **铁律 2（模版组装器单页相对路径对齐）**：
        *   物理文件：`themes/sovereign/adapters/sovereign_helpers.py`
        *   在 `apply_template` 组装顶部主导航时，严格将单页槽位与常见独立单页排除在 `/index.html` 规则之外，强制生成 `{root_path}{nav_lang_prefix}{u_slug}.html`。在根目录渲染 `about.html` 时输出 `<a href="./about.html" class="active">`，确保浏览器地址栏始终稳定停留在根目录，Base URI 0 偏移。
    3.  **铁律 3（开发预览服务器 302 客户端纠偏防卫）**：
        *   物理文件：`core/utils/dev_server.py` (`SovereignHandler.do_GET`)
        *   **递归路径自动折叠**：当拦截到形如 `/about/about/...` 的重复连续路径段时，利用正则折叠并通过 **HTTP 302 Found** 客户端重定向跳回单级路径；
        *   **虚拟单页目录拦截重定向**：若请求 `/about/index.html` 或 `/about/` 且物理磁盘无该子目录索引，但父级磁盘存在同名实体单页 `about.html` 时，**严禁静默 200 返回父级内容**（静默 200 无法校正浏览器地址栏），必须向浏览器发送 **HTTP 302** 重定向到 `/about.html`，从网络协议层强制纠偏浏览器 Base URI。

---

### 2.2 语言翻译与内容治理 (Localization & Content Governance)

#### ① 多语言矩阵 (`i18n_settings`: `source.lang_code`, `targets`, `force_source_prefix`)
*   **原生主题 (Sovereign / Universal)**：**🟢 100% 原生支持**
    *   原生主题自带多语言动态切换下拉菜单、母语/译文无缝跳转。`force_source_prefix`（源语言是否强制带 `/zh/` 前缀）可自由开启或关闭，路由树完全自适应。
*   **第三方框架**：**🟡 框架自身的多语言方案各异，依赖适配器脚手架生成**
    *   **Docusaurus**：采用官方 `i18n` 机制，多语言内容存放于 `i18n/{lang}/...` 目录下，并自动同步 `docusaurus.config.js` 的 `i18n.locales`；
    *   **VitePress**：采用目录分流（如 `/zh/`、`/en/`），自动在 `.vitepress/config.mts` 中声明 `locales` 对象；
    *   **Starlight**：在 `astro.config.mjs` 中声明 `locales`，文档存放于 `src/content/docs/{lang}/`；
    *   **Nextra**：依赖 Next.js 的 `i18n` 路由或子目录 pages；
    *   **Hugo**：依赖 `languages.{lang}` 与多语子目录；
    *   **Hexo**：Hexo 原生多语言较弱，通常依赖第三方国际化插件或独立子目录。
    *   **结论**：Illacme 能够将翻译后的多语言 Markdown 准确投递到第三方框架对应的语言槽位，多语言切换器 UI 样式由框架自身决定。

#### ② 翻译规则与保护 (`block_rules` / `translation_style` / `glossary`)
*   **全主题通用**：**🟢 100% 深度支持**
    *   翻译、代码块锁定、数学公式保护、术语词库替换，全部发生在**上游的 Markdown 编译与 LLM 推理阶段**（`core/editorial/steps/translation.py`），下游 SSG 适配器只负责接收清洗完成后的成稿，因此所有主题对翻译质量与规则保护的表现完全一致。

#### ③ 全球 50 种语言前台核心视图本地化矩阵 (`VIEW_I18N_MATRIX`)
*   **全引擎全矩阵支持**：**🟢 100% 矩阵覆盖与零硬编码解耦**（经 `tests/test_i18n_view_matrix.py` 验证）。
    *   在 `core/adapters/egress/ssg/base_shards/ssg_slot_matrix.py` 中内置了覆盖全球 50 种语言的核心交互词条（`timeline`、`cards`、`list`、`all`、`read_more` 等）。
    *   原生主题与第三方适配器统一通过 `get_i18n_view_label(key, lang)` 动态级联获取地道母语翻译，彻底消除了前台视图切换中的硬编码中英文字符串。

---

### 2.3 出版合规与品牌标识 (Compliance & Identity)

#### ① 出版合规 (`icp_license`, `police_license`, `cc_license`)
*   **原生主题 (Sovereign / Universal)**：**🟢 100% 原生支持**
    *   Sovereign 与 Universal 的页脚组件（Footer）深度集成了中国出版合规槽位：自动展示工信部 ICP 备案号（直链工信部官网）、公安网安备图标及备案号、知识共享许可（CC-BY-NC-SA 4.0）徽标与协议详情链接。
*   **Starlight (Astro)**：**🟢 官方原生级插槽组件支持**
    *   Illacme 在 `themes/starlight/src/components/CustomFooter.astro` 中提供了深度定制的页脚组件，构建时自动读取 `theme.options.json`：
        1.  工信部 ICP 备案号（带 📜 徽标直链 `https://beian.miit.gov.cn/`）；
        2.  公安网安备专用矢量警徽 SVG 图标及备案号（直链 `http://www.beian.gov.cn/`）；
        3.  知识共享许可协议（带 ⚖️ 徽标与详情链接）；
        4.  全域版权声明及 Powered by 署名行；
        5.  完全适配 Starlight 深浅主题切换与移动端响应式排版，创作者**开箱即用，无需手动覆盖组件**。
*   **其他第三方框架 (Docusaurus / VitePress / Nextra / Hugo / Hexo)**：**🟡 降级注入到 Footer 版权字符串**
    *   这些框架原生未预留备案号与警徽插槽。Illacme 会将备案号与版权信息格式化后注入配置文件的版权字段（如 `themeConfig.footer.copyright`）。如需公安警徽图标或独立卡片排版，需通过框架自身的组件覆盖（如 Docusaurus Swizzle）定制。

#### ② 品牌与站点身份 (`site_title`, `site_tagline`, `logo`, `favicon`)
*   **原生主题**：**🟢 100% 原生支持**（顶部导航栏、元数据 `<head>`、OpenGraph 社交卡片自动完整装配）。
*   **第三方框架**：**🟢 100% 支持**（适配器在生成框架配置文件时，自动将这些字段回填至各框架的配置对象中，如 Docusaurus 的 `title`/`tagline`/`favicon`，VitePress 的 `title`/`description`）。

---

### 2.4 原稿语法与 Markdown 扩展 (Markdown & Extended Syntax)

#### ① Obsidian 专有双链 (`[[target|alias]]`) 与相对超链接自愈
*   **原生主题**：**🟢 原生 AST 级解析**（自动计算目标文件绝对/相对映射，自适应 `slug_dir_mode` 重写为真实 HTML 链接）。
*   **第三方框架**：**🟢 通过 `normalize_markdown_content` 100% 自愈转化**
    *   基类 `BaseSSGAdapter.normalize_markdown_content` 已为全部 6 种第三方框架（经 `tests/test_ssg_adapters_link_healing.py` 验证）注入标准流水线：
        1.  **Obsidian 双链清洗**：将 `[[target|alias]]` 精准转化为 `[alias](./target.md)` 或 Clean URL；
        2.  **后缀自愈**：将正文中的 `.html` 相对链接自愈修正为 `.md`，保证 SPA 路由无缝跳转；
        3.  **🛡️ CommonMark 陷阱防御**：自动将带有 4+ 空格缩进的 HTML 标签行顶格处理，防止其在空行后被 Remark/CommonMark 误识别为缩进代码块（`<pre><code>`）。

#### ② Callout / 警告块语法 (`> [!NOTE]` / `> [!WARNING]`)
*   **原生主题**：**🟢 原生毛玻璃 Callout 卡片渲染**（支持 13 种常见类型，自适应暗黑/高亮模式与微动画）。
*   **第三方框架**：**🟢 各适配器深度语义转译**
    *   `DocusaurusAdapter`：转译为 Docusaurus 官方 Admonitions（`:::note` / `:::warning` / `:::danger`）；
    *   `VitepressAdapter`：转译为 VitePress 原生容器（`::: info` / `::: warning` / `::: danger`）；
    *   `StarlightAdapter`：转译为 Astro Starlight `<Aside type="...">` 组件；
    *   `NextraAdapter`：转译为 React MDX 组件 `<Callout type="...">` 并自动引入组件；
    *   `HugoAdapter`：转译为 Hugo Shortcode `{{% notice note %}}`；
    *   `HexoAdapter`：转译为 Hexo Tag Plugins `{% note info %}`。

#### ③ 软回车硬换行 (`markdown_break`: `hard` / `soft`)
*   **原生主题**：**🟢 原生支持**（`hard` 模式下回车即为换行，完全对齐 Obsidian 体验）。
*   **第三方框架**：**🟡 依赖框架内置 Markdown 引擎配置**（需框架开启 `breaks: true`，例如 VitePress 在 config 中配置 `markdown.breaks = true`）。

---

### 2.5 全站托管与渠道分发 (Hosting & Syndication)

*   **静态站点托管平台 (GitHub Pages / Cloudflare Pages / Vercel / Netlify / Render / Zeabur / Railway)**：
    *   **原生 Universal**：**🟢 体验最轻量**。无需 Node.js 环境，纯 HTML 静态产物直接上传即可秒级上线。
    *   **原生 Sovereign**：**🟢 标准静态输出**。构建输出 `dist/`，任何静态托管均可直接挂载。
    *   **第三方框架**：**🟡 依赖云端构建器或本地 Node.js 预编译**。托管平台必须具备 Node.js/Go 构建环境以执行 `npm run build` 或 `hugo --minify`。
*   **社交平台同步 (微信公众号 / 知乎 / 掘金 / Medium / Dev.to / Ghost 等)**：
    *   **全主题通用**：**🟢 100% 独立解耦**。社交平台同步是由 Illacme 的 Egress 渠道插件直接读取已排版/已翻译的 Markdown 内容推送到对端 API，与本地采用何种前端 SSG 主题没有任何耦合。

---

### 2.6 数字花园关系图谱与拓扑分析 (Knowledge Graph & Topology)

*   **原生主题 (Sovereign / Universal)**：**🟢 100% 原生全息图谱支持**
    *   内置 D3.js 力导向图谱，支持全屏展开、节点拖拽、反向链接（Backlinks）漫游、缩放与聚类分析。
*   **Docusaurus & Starlight (Astro)**：**🟢 官方原生组件级深度集成**
    *   **拓扑核心引擎下沉**：由 `shared/topology-core.js` 统一驱动，本地化捆绑 `d3.v7.min.js`，**0 外链 CDN 依赖**。
    *   **构建期拓扑数据同步**：`core/bindery/garden_exporter.py` 在发布期自动导出全息反链关系并写入站点的 `public/graph.json`。
    *   **专用原生组件**：
        *   Starlight: `themes/starlight/src/components/TopologyCanvas.astro`（Web Component 封装，集成 View Transitions 监听与右侧栏尺寸自适应）；
        *   Docusaurus: `themes/docusaurus/src/components/TopologyCanvas.jsx`（React `BrowserOnly` 封装，集成侧边栏与活动路径高亮）。
    *   **多语言动态切流**：根据当前页面访问的语言前缀（如 `/en/`、`/ja/`、默认母语），前台图谱组件自动过滤并呈现对应语种的节点子图。
    *   **深浅色主题双向响应**：自动监听宿主框架的暗黑模式切换（Starlight `data-theme`、Docusaurus `html[data-theme]`），实时无缝重绘制图谱配色。
*   **其他框架 (VitePress / Nextra / Hugo / Hexo)**：**🟡 具备底层数据，需接入前端挂载点**
    *   底层均会自动生成 `public/graph.json`，但默认模版未集成侧边栏 D3 挂载组件，需创作者引入对应框架的组件挂载。

---

### 2.7 博客流与展示页面自治契约 (Autonomous Blog & Custom Synthesis)

*   **生命周期分流与自治机制 (`has_autonomous_blog_engine`)**：**🟢 架构解耦**
    *   在 `core/adapters/egress/ssg/base.py` 中建立了 `has_autonomous_blog_engine()` 契约：
        *   当主题具备自治博客合成器时（如 Sovereign 或自定义扩展），通用生命周期插件自动避让，绝不执行外部通用 HTML 覆盖；
        *   对于纯第三方文档型框架，系统则按 Feature Slots 规则投递标准的 Markdown 博客文章与单页源码。

---

## 3. 各 SSG 主题能力支持矩阵一览表

| 治理中心配置与能力维度 | Sovereign (官方旗舰) | Universal (极速通用) | Starlight (Astro) | Docusaurus (React) | VitePress (Vue) | Nextra (Next.js) | Hugo (Go) | Hexo (Node) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **运行时外部依赖** | 纯 Python/Astro | **0 外部依赖 (纯 Python)** | Node.js | Node.js | Node.js | Node.js | Go | Node.js |
| **网址组织形态: nested (目录树)** | 🟢 完美 | 🟢 完美 | 🟢 完美 (推荐) | 🟢 完美 (推荐) | 🟢 完美 (推荐) | 🟢 完美 (推荐) | 🟢 完美 (推荐) | 🟢 完美 (推荐) |
| **网址组织形态: flat (极简根目录)** | 🟢 完美 (自愈内链) | 🟢 完美 (自愈内链) | 🟡 需依赖 Frontmatter | 🟡 扁平化侧边栏退化 | 🔴 不支持 (破坏路由) | 🔴 不支持 (破坏路由) | 🟡 需自定义重定向 | 🟡 侧边栏退化 |
| **网址组织形态: prefix (智能前缀)** | 🟢 完美 (自愈内链) | 🟢 完美 (自愈内链) | 🟡 需 Frontmatter slug | 🟡 连字符路径显示 | 🔴 不支持 (破坏层级) | 🔴 不支持 (破坏层级) | 🟡 需自定义 | 🟡 侧边栏退化 |
| **独立单页 (Slot Pages) 落盘契约** | 🟢 content/about.md | 🟢 about.md | 🟢 src/content/docs/ | 🟢 src/pages/about.md | 🟢 about.md | 🟢 pages/about.md | 🟢 content/about.md | 🟢 source/about.md |
| **同名单页 Clean URL 自动坍缩** | 🟢 消除 /about/about | 🟢 消除 /about/about | 🟢 消除 /about/about | 🟢 消除 /about/about | 🟢 消除 /about/about | 🟢 消除 /about/about | 🟢 消除 /about/about | 🟢 消除 /about/about |
| **独立单页 Base URI 漂移防御与 302 自愈** | **🟢 物理相对根路径对齐 + 302 折叠重定向** | 🟢 物理相对根路径对齐 (./about.html) | 🟢 框架接管 (Clean URL /about) | 🟢 框架接管 (Clean URL /about) | 🟢 物理对齐 (about.html) | 🟢 框架接管 (/about) | 🟢 目录直出 (/about/) | 🟢 目录直出 (/about/) |
| **Slug 命名法则 (AI / 文件名)** | 🟢 完美 | 🟢 完美 | 🟢 完美 | 🟢 完美 | 🟢 完美 | 🟢 完美 | 🟢 完美 | 🟢 完美 |
| **Obsidian 双链与相对链接自愈** | 🟢 原生 AST 转换 | 🟢 原生 AST 转换 | 🟢 自动清洗为 .md | 🟢 自动清洗为 .md | 🟢 自动清洗为 .md | 🟢 自动清洗为 .md | 🟢 自动清洗为 .md | 🟢 自动清洗为 .md |
| **CommonMark 4空格缩进代码陷阱防御** | 🟢 格式化防护 | 🟢 格式化防护 | 🟢 格式化防护 | 🟢 格式化防护 | 🟢 格式化防护 | 🟢 格式化防护 | 🟢 格式化防护 | 🟢 格式化防护 |
| **Callout 语法转译** | 🟢 原生毛玻璃卡片 | 🟢 原生毛玻璃卡片 | 🟢 `<Aside>` 组件 | 🟢 `:::note` 规范 | 🟢 `::: info` 规范 | 🟢 `<Callout>` MDX | 🟢 Shortcode | 🟢 Tag Plugins |
| **数字花园动态拓扑图谱 (Graph View)** | 🟢 原生力导向图 | 🟢 原生力导向图 | 🟢 原生 Astro 组件 | 🟢 原生 React 组件 | 🟡 产出 graph.json | 🟡 产出 graph.json | 🟡 产出 graph.json | 🟡 产出 graph.json |
| **多语言矩阵与切换** | 🟢 原生沉浸式切换 | 🟢 原生沉浸式切换 | 🟡 Starlight locales | 🟡 Docusaurus i18n | 🟡 VitePress locales | 🟡 Nextra i18n | 🟡 Hugo 多语 | 🔴 插件支持较弱 |
| **50 语种核心交互标签矩阵** | 🟢 100% 覆盖 | 🟢 100% 覆盖 | 🟢 100% 覆盖 | 🟢 100% 覆盖 | 🟢 100% 覆盖 | 🟢 100% 覆盖 | 🟢 100% 覆盖 | 🟢 100% 覆盖 |
| **出版合规 (ICP/公网安备/CC)** | 🟢 专属页脚卡片槽位 | 🟢 专属页脚卡片槽位 | **🟢 官方定制页脚组件** | 🟡 注入 Copyright 文本 | 🟡 注入 Copyright 文本 | 🟡 注入 Copyright 文本 | 🟡 注入版权行 | 🟡 注入版权行 |
| **博客列表/自治合成器** | 🟢 自治合成流 | 🟢 支持 (紧凑/卡片) | 🔴 框架官方固定版式 | 🔴 框架官方固定版式 | 🔴 框架官方固定版式 | 🔴 需手写 React 组件 | 🟡 依赖外部主题 | 🟡 依赖外部主题 |
| **全息搜索 (Search)** | 🟢 内置纯前端全文检索 | 🟢 内置纯前端全文检索 | 🟡 Pagefind / 原生 | 🟡 Algolia / 本地插件 | 🟡 Minisearch | 🟡 FlexSearch | 🟡 Fuse.js | 🟡 LocalSearch |

---

## 4. 总结与创作者选型准则

1.  **推荐首选原生直出主题 (`Universal` 或 `Sovereign`) 的场景**：
    *   希望**开箱即用、完全免除 Node.js / npm 庞大环境与编译依赖**（Universal 零外部依赖秒级直出）；
    *   需要使用【极简根目录（`flat`）】或【智能 SEO 前缀（`prefix`）】这类高级 URL 压缩形态；
    *   独立单页（如 `about.md`）享有严密的相对根路径对齐与 DevServer 302 客户端重定向防卫，**Base URI 0 漂移，内链 100% 互通**；
    *   需要最深度集成的中国出版合规卡片与 Obsidian 沉浸式毛玻璃视觉交互；
    *   追求毫秒级构建、极小产物体积以及原生的 Obsidian 双链与视觉体验。
2.  **选用生态框架旗舰级适配 (`Starlight` / `Docusaurus`) 的场景**：
    *   希望在享受 React / Astro 现代前端技术栈与丰富生态插件的同时，兼得 Illacme 的核心出版资产；
    *   **Starlight 深度适配**：享有专属定制的出版合规页脚（ICP + 公安网安备 SVG 警徽直链 + CC 协议）与 D3 原生动态知识图谱；
    *   **Docusaurus 深度适配**：享有原生 React 侧边栏动态知识图谱与全自动 i18n 语言包投递；
    *   网址组织形态请锁定在<b>【📂 目录树复刻 (nested)】</b>，独立单页与双向链接均已实现 Clean URL 自动坍缩与 100% 自动愈合。
3.  **选用其他框架 (`VitePress` / `Nextra` / `Hugo` / `Hexo`) 的场景**：
    *   团队已有极高定制度的专属工程脚手架与设计资产；
    *   Illacme 在上游完成 AI 翻译、SEO 优化、双链与 Callout 语法转译、以及独立单页投递，完美充当框架的工业级预处理引擎。
