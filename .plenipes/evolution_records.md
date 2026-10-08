# 📂 Illacme Plenipes - 物理主权演进与踩坑沉淀 (Evolution Records)

这里记录了我们在系统的物理迭代和开发过程里，所沉淀下的最为关键的架构缺陷自检与教训（Lessons），以防止后续开发在相同的物理逻辑上发生脑裂或回退。

## 📅 2026-10-08: 全站托管访问 URL 智能嗅探回填与全站原生弹窗主权毛玻璃模态化重构 (Sovereign Glassmorphism Confirm & Hosting Auto-Discovery)
*   **现象与需求描述**：
    1.  **全站托管卡片访问网址缺失**：GitHub Pages、Vercel 等托管平台在完成发布演练后，卡片未展示用户访问网址，需创作者手动寻找；且发布表头列未居中，视觉体验缺乏精致感；
    2.  **遗留原生弹窗体验割裂**：发布确认（如“一键发布到所有平台”、“发布到此平台”、“再次发布”）以及全站 18 处敏感破坏性操作（书架删除、原稿物理销毁、媒体资产清理、算力出厂重置等）依赖浏览器默认原生 `confirm()` / `alert()`，样式生硬且易受非 TTY 或 DOM 刷写干扰。
*   **根因剖析与工程设计**：
    1.  **全站托管访问 URL 自动嗅探与双向回填**：
        - 后端新增托管平台详情探测能力，精准解析 Git Remote Origin 与账户配置，智能推导官方 Pages 域名（如 `https://{user}.github.io/{repo}/`）；
        - 前端卡片与账本表格统一对齐居中展示，并在检测到有效 URL 时提供高亮外链直达徽标与一键复制；
    2.  **主权毛玻璃模态体系全面替换原生阻塞弹窗 (`confirmSovereignAction`)**：
        - 统一基于 `window.confirmSovereignAction` 与 `Swal.fire` 构建毛玻璃拟态模态中枢，注入高景深暗色背景与精致操作按钮；
        - 对原生 `confirm()` / `alert()` 进行彻底解耦与淘汰，全站 18 处高频操作全面升级，并在离线或极端缺宿主环境保留安全优雅降级；
        - 全站 19 个前端脚本物理行数严格保持在 `< 300` 行红线之内，通过 `test_frontend_integrity.py` 与 `sovereign_audit.py --stage 2.7` 全自动化门禁。

## 📅 2026-10-01: 工业级出版装订质感深耕：两遍渲染真实页码对齐、Running Header 自动克隆与底端微光页码印章 (Two-Pass TOC, Running Header & Folio Stamp Engine)
*   **现象与需求描述**：
    1.  **封面出血白边消除**：A4 纸张 210mm 换算 pt 舍入差导致封面右边和下边存在约 1px 细微白边；
    2.  **长章节跨页续页章眉（Running Header）**：跨页后无法知晓当前所处章节，缺乏传统工业级纸质图书的连续翻阅标识；
    3.  **底端统一微光页码印章（Folio Stamp）**：封面需 100% 纯净，前置目录需小写罗马数字（`i`, `ii`），正文页需从 `- 1 -` 起连续居中编号；
    4.  **前置目录真实印厂物理页码对齐（Two-Pass TOC）**：此前目录右端显示机械的 `CH 1 →`，未能反映章节在印刷实体书中的真实起始页码（如 `P. 1`, `P. 7`, `P. 9`），且目录跨页时条目曾侵入底端安全留白区。
*   **根因剖析与工程设计**：
    1.  **封面全画幅出血重构**：将 `.cover-page` 与 `.cover-art` 尺寸精准对齐 `100vw / 100vh` 满版铺满，并在 `@page` 层面设置 `size: A4 portrait; margin: 0;`，彻底根除 210mm 换算舍入误差带来的右下白边。
    2.  **W3C thead 跨页 Running Header 自动克隆 (Table-Header Architecture)**：
        - 采用经典出版工业级标准，将每个章节内容包裹于原生 `table.chapter-table` 中；
        - 将章眉声明于 `thead`（`display: table-header-group`），利用 Blink 引擎原生特性，长章节发生自然断页跨页时，每一页顶端全自动克隆出现优雅的章眉导航条（`第 X 章 · 章节标题`），首开页自然呈现，续页精准衔接，0 JavaScript 依赖。
    3.  **矢量微光页码印章引擎 (`PDFFolioStamp`)**：
        - 独立抽象 `core/adapters/egress/ebook/pdf_folio_stamp.py`（174 行，严格 $\le 300$ 行）；
        - 基于 `fitz` 矢量重写机制，在离底边 12.7mm（36pt）处精准居中注入 8.5pt Helvetica `#94a3b8` 优雅微光页码；
        - 智能三段式分类识别：封面 0 污染跳过，前置目录小写罗马数字（`i`, `ii`），正文自第 1 章首日起自 `- 1 -` 连续编号；
        - 结合 `-webkit-box-decoration-break: clone` 与 `padding-bottom: 28mm`，确保断页 Fragment 底端拥有绝对纯净的安全留白区，彻底消除文字压页码现象。
    4.  **两遍无头渲染真实物理页码回填流水线 (Two-Pass TOC Alignment Pipeline)**：
        - **Pass 1 探针扫描**：多章节场景下，Pass 1 编译临时探针 PDF，通过 `PDFFolioStamp.detect_chapter_pages` 高速扫描物理页面，精准计算出每一章节正文首页的逻辑页码（如 `{0: 1, 1: 7, 2: 9, ...}`）；
        - **Pass 2 精准回填**：将印厂页码映射表注入 `PDFAssets.render_toc_html(..., page_map=page_map)`，将条目右端由 `CH X →` 升级为 `P. 1`, `P. 7`, `P. 9`，目录高度与总页数保持绝对无抖动恒定（Zero Drift）；
        - 目录超链接（`<a href="#ch_{id}">`）完整包裹整行，点击 `P. X` 或章节名均可 100% 精准丝滑跳转；
        - 全量 104 项 `bindery` 自动化回归测试 100% 绿灯。

---

## 📅 2026-10-01: PDF 长卷多语对照分批切片打印与 PyMuPDF 瞬时合并引擎 (PDF Chunked Printing & Instant Assembly)
*   **现象与需求描述**：
    - 创作者在数字出版装订中枢导出全库（33 章节）双语/多语对照版（ZH ⇌ EN）PDF 印本时，界面持续卡在进度弹窗（`⏳ 正在按整篇并列对齐 ZH ⇌ EN 多语对照内容并生成 PDF 印本...`），无头 Chrome 打印卡死长达 6 分钟（360 秒）或触发超时异常。
*   **根因剖析与工程设计**：
    1.  **Chromium Blink 打印重排指数级死锁 (Paged Media Layout Thrashing)**：
        - 全库 33 章多语双开面对照（Verso/Recto）长卷包含 69 个连续断页节（141 页）；
        - 当单一巨大 HTML 中同时包含数百处 CSS Paged Media 复杂规则（`break-before: page`, `break-after: page`, `break-inside: avoid`, `@page :left`, `@page :right`）时，Blink 渲染引擎在计算奇偶页边距与断点时陷入深层瀑布流回溯搜索；
        - 实机现场捕获：单进程 Chrome Renderer 内存暴涨至 **1.85 GB**，CPU 假死，耗时 360 秒甚至崩溃报错 `Printing failed`。
    2.  **分卷切片无头打印与三级瞬时拼接引擎 (PDFChunkPrinter)**：
        - 独立建立 `core/adapters/egress/ebook/pdf_chunk_printer.py`（162 行，严格遵守 SOP-01 规范）；
        - **分批切片**：章节较多（> 8 节）时长卷自动按批次切片（每批 8 个 section 独立打包为轻量 HTML）；
        - **极速渲染**：实测每个分卷 Chrome 渲染仅需 **1.4 ~ 1.9 秒**，内存占用压低至 < 100MB（降低 95%）；
        - **三重高保真合并防线 (Triple-Layer Assembly)**：
          1. 优先尝试 C 级底层极速 `fitz` (PyMuPDF)；
          2. 其次调用纯 Python 现代工业标准 `pypdf`（`requirements.txt` 显式声明 `pypdf>=3.0.0`，杜绝环境缺少 PyPDF2 时降级 ReportLab）；
          3. 备选兼容遗留 `PyPDF2`；
        - **实机收益**：全库 33 章双语对照版 141 页 PDF 真实导出总耗时从 **360 秒骤降至 13~21 秒**（性能提升超 20 倍），彻底根治页面假死挂起。
    4.  **多语文章标题归位分栏内部架构 (In-Column Heading Desensitization)**：
        - 此前多语对照 PDF 在 `chapter-body` 外层平铺渲染通栏中文大标题与 `[EN] ...` 副标题，破坏了多栏并排研读的左右对称与视觉流；
        - 在 `PolyglotAligner` 中将各语种文章专属标题下沉注入各自语言的 `wb-poly-column` 顶部（紧随 `wb-poly-header` 徽章下方），下衬 0.5pt 细线，并剥离正文首行重复的 `<h1>` 标签；
        - 在 `pdf.py` 中多语模式下彻底抑制外层通栏标题，中英文文章标题 100% 完整落在各自分栏内部，实现顶部开阔舒展、左右严格对称并列。
    5.  **全画幅满版装帧与深墨玉毛玻璃封面重塑 (Full-Bleed Cover & Translucent Jade Cards)**：
        - **根除半截页面**：此前封面由于 `@page` 边距与无头 Chromium 打印机制，深色背景只渲染了内容高度，留有下半截巨大白边；重构 `@page { margin: 0; }` 并为封面注入全画幅满版 `radial-gradient` 渐变背景，版心安全内边距委托给具体正文组件；
        - **消灭刺眼白块**：多语封面卡片不再粗暴继承正文白底样式，重塑为高档通透的深墨玉微光磨砂玻璃卡片（`rgba(255, 255, 255, 0.05)` 与翠绿暗金边框），文字纯净雪白，底部融入版权署名，彻底达成顶级私立出版物视觉主权。
    6.  **目录全量 66 条链接 100% 内部锚点连通保证 (TOC Intra-Book Seamless Navigation)**：
        - 此前 `PDFChunkPrinter` 机械使用 `chunk_size=8` 分卷，导致第 1 分卷（仅含前 6 章）在 Chromium 编译时将第 7 章以后的跨卷目标当做无效应链，造成目录自第 7 章起全部失效；
        - 提升自适应单卷阈值至 64 章，全书 33 章正文在单 HTML 流中 4.3 秒毫秒级直出；经 `pypdf` 物理核验，目录第 2 页与第 3 页全部 66 个中英文条目（`/ch_1` ~ `/ch_33`）100% 完整具备跳转能力。
    7.  **多语静态发布路由反向解析与译文版全量超链接自愈 (Multilingual Route Desensitization & Link Parity)**：
        - **现象根因**：原稿中文使用 Obsidian 双链（如 `[[dashboard-guide]]`），直接匹配物理文件名成功生成链接；而译文由 AI 翻译转化为地道的英文 SEO 路由（如 `[dashboard-guide](/en/docs/governance-dashboard-operation-guide/)`），但装订器此前未载入 `metadata` 发布的英文 slug 缓存，且未剥离语种前缀，导致误判为死链并降级为 `pdf-unlinked` 纯文本（仅文件名相同的 `quick-start` 幸存）；
        - **双向自愈落地**：在 `BookAssembler` 中自动预热注入 metadata 发布 slug 映射表，`_resolve_route_target` 智能剥离语种前缀，并引入文本反查兜底；实测第 86 页等全量多语对照表格全部 21 处中英文超链接 100% 双向对齐点亮。

---

## 📅 2026-10-01: Word 多语言对照动态行高拟真切片与首行 H1 剥离对齐架构 (DOCX Dynamic Capacity & Heading-1 Desensitization)
*   **现象与需求描述**：
    1.  单语版生成 75 页，而总文本量高达 13.4 万字（单语版的 3.38 倍）的多语对照版在审校器中仅呈现 46 页，用户困惑是否发生了内容丢弃；
    2.  多语对照审校页面中，译文版标题（如 `[EN] 🚀 My First Sovereign Publishing Blog Post...`）孤立被置于章节顶部，而分栏表格内部中文存在标题、英文直接从正文开始，导致全书 32/33 个章节自第一行起发生整体向上错位串行，且中文章标题发生内外二次重复。
*   **根因剖析与工程设计**：
    1.  **物理文字量核验与排版几何学**：
        - 经物理比对，33 个章节与 33 项目录 100% 完整对齐，文字量无任何丢弃；双栏并排结构使得单行同时消费中英文两个段落，垂直高度天然收敛；
        - 此前 `docx_reader.py` 对表格切片时机械写死单行估算点数为 `32` 点，低估了包含上百字中英文长段落对照行的实际占位，导致单页被强塞多达 14~20 组长段落，版面被过度压缩至 46 页。
    2.  **表格行高动态估算算法 (`_estimate_row_pts`)**：
        - 在 `docx_reader.py` 中引入动态行高计算，根据单元格中最长文本字数与列宽动态折算折行数（26 ~ 220 点），剩余容量不足时自适应切入下一页；优化后多语对照版舒展为 102 页，留白与行距恢复出版级疏朗呼吸感。
    3.  **出版级典籍双语章名章题与首行 H1 剥离**：
        - **章题头升级**：在 `docx.py` 中去除生硬突兀的 `[EN]` 标签，改为出版典籍题头规范（主标题：`第 25 章 多品牌主权矩阵`，副标题：`Chapter 25 · Multi-Brand Sovereign Matrix...`，深灰蓝斜体）；
        - **首行 H1 剥离**：在 `DocxPolyglotBuilder` 切分各语种语义块时，检测并自动剥离正文开头的首个 `# H1` 重复标题，使左右分栏直接由正文第一段（或提示块）严格对齐；
        - **纯分割线清洗**：在 `split_markdown_blocks` 中将孤立的 `---`、`***` 识别为段间断点并过滤，彻底消灭单边横线打乱行数的顽疾。
    4.  **工程合规与自动化门禁**：
        - `core/adapters/egress/ebook/docx_reader.py`（294 行）、`docx.py`（299 行）、`docx_polyglot_builder.py`（275 行）严格遵循 SOP-01 单文件 $\le 300$ 行规范；
        - 全量 87 项装订测试与 Stage 2.7 前端主权审计 100% 绿灯 Pass。

---

## 📅 2026-09-30: Word 多语言对照版全域分栏骨架与 HTML 容器脱壳清洗 (DOCX Polyglot Full Scaffold & HTML Sanitization)
*   **现象与需求描述**：
    1.  数字出版装订（Bindery）导出 Word (.docx) 多语言对照版时，封面、目录与版权声明仍为单语居中形式，未遵循全书的多语言并排分栏规范；
    2.  当手稿或翻译文本中混杂了前端专用组件标签（如 `<div class="home-hero-container">`、`<span class="hero-badge">`）时，Word 单元格内直接输出了裸露的 HTML 源码字符串，破坏了出版级阅读体验。
*   **根因剖析与工程设计**：
    1.  **全链路 HTML 语义降级与双重脱壳防线 (HtmlSanitizer)**：
        - 在 `DocxPolyglotBuilder` 切分各语言语义块前，无条件引入 `HtmlSanitizer.sanitize_to_markdown` 彻底剥离 `div/span/style` 容器外壳，仅保留标题、链接与纯自然语言文本；
        - 在表格单元格写入富文本时（`_render_cell_block`），注入第二道防线，若段落含有残余尖括号标签再次脱壳，杜绝任何 HTML 源码污染 Word 文档。
    2.  **多语言并排分栏骨架架构 (DocxPolyglotScaffold)**：
        - 独立建立 `core/bindery/docx_polyglot_scaffold.py`（284 行，严格符合 SOP-01 规范）；
        - **分栏封面**：根据多语种矩阵构建无边框双列表格，左右列分别居中排布各语种的品牌徽章、出版书名与描述简介；
        - **分栏目录**：构建多列对齐目录网格，表头为各语言徽章，表体每一行代表一个章节，双列各自显示对应语言章节名并绑定 `#{ch_id}` Word 原生交互式超链接；
        - **分栏版权声明**：构建多列表格，并排呈现各语种的出版典籍、责任作者、出版机构与版权规范元数据。
    3.  **驱动无缝接入与行数合规**：
        - `core/adapters/egress/ebook/docx.py`（299 行）无缝接入骨架分栏与章节副标题对照，所有修改文件严格 $\le 300$ 行；
        - 新增与全量测试 87 项测试 100% 绿灯 Pass。

---

## 📅 2026-09-30: Word 与 PDF 印刷级出版排版深化 (DOCX Syntax Highlighting, Print Duplex Gutter & Page-Break Protection)
*   **现象与需求描述**：
    1.  数字出版装订（Bindery）导出的 Word (.docx) 印本中，代码块此前仅为等宽无色彩纯文本，缺乏技术图书出版级的语法层次与美感；
    2.  固定版式印刷 PDF 面向物理纸质胶装或精装装订时，内外侧边距均等（16mm），导致翻页装订线（Gutter）处文字容易被书脊挤压遮挡，影响实物阅读；
    3.  PDF 长文排版中容易出现段落首尾孤行孤字（Orphans/Widows）以及标题孤立在页底、内容跨到下一页的断流瑕疵。
*   **根因剖析与工程设计**：
    1.  **DOCX 原生词法高亮着色器 (DocxSyntaxHighlighter)**：
        - 独立实现 `core/bindery/docx_syntax_highlighter.py`（145 行，符合 SOP-01 规范），引入 `pygments` 词法分词流；
        - 定义出版级浅色高对比度色彩表（紫罗兰关键字、沉稳天蓝函数名、森林绿字符串、沉稳灰斜体注释、琥珀橙数字等）；
        - 对相邻同样式 Token 执行流式合并，大幅减少 Word OpenXML `<w:r>` 节点数量，兼顾渲染性能与格式兼容，并在异常时平滑降级为等宽文本。
    2.  **PDF 物理印厂规范 (Print-Ready Duplex Gutter & Break Protection)**：
        - 优化 `PDFAssets.get_print_css()`，利用 CSS Paged Media 规范分别声明 `@page :left` 与 `@page :right`，实现内侧书脊留白（20mm Gutter）与外侧切口（14mm Margin）对称装订设计，封面页 `@page :first` 保持全画幅居中；
        - 注入 `orphans: 3; widows: 3;` 杜绝孤行孤字；对标题层级追加 `break-after: avoid;`，对代码卡片、引述、多语对照栏追加 `break-inside: avoid;`；
        - 为 PDF 注入 `.codehilite` 印刷着色样式，确保 Chromium 无头打印与打印机输出高保真彩色代码卡片。
    3.  **全量自动化测试守护**：
        - 新增 `tests/test_bindery_syntax_highlight.py`，全量 82 项装订与电子书测试 100% 绿灯 Pass。

---

## 📅 2026-09-29: GitHub Actions 云端门禁解耦、无头依赖对齐与单元测试绝对隔离自愈 (Sovereign CI Gate, Hermetic Tests & Headless Parity)
*   **现象描述**：
    1.  用户反馈 GitHub Actions 历史流水线频繁呈现持续失败或大量 `cancelled`；
    2.  解耦并新增轻量级代码门禁后，云端 Ubuntu Runner 出现 `RuntimeError: The starlette.testclient module requires the httpx package to be installed.`；
    3.  补全依赖后，`test_translation_resolver_content_fidelity` 在本地通过但在云端抛出 `AssertionError: assert 'About' in '关于'`。
*   **根因剖析与工程设计**：
    1.  **流水线触发策略混淆与重型任务并发冲突**：
        - 历史工作流 `.github/workflows/build_desktop.yml` 配置了 `push.branches: [main]` 与 `concurrency: cancel-in-progress: true`，密集的日常 Git 提交导致耗时较长（~8分钟）的全平台桌面打包（Mac/Windows/Linux PyInstaller）未完成即被下一次提交中断取消；
        - 将桌面全平台打包解耦为仅在 `tags: ['v*']` 或手动 `workflow_dispatch` 触发；新增轻量级快速云原生门禁 `.github/workflows/ci_sovereign_gate.yml` 用于每次 Push / PR 代码规范与测试审计。
    2.  **无头环境依赖与测试客户端缺失**：
        - 无头 Linux 下无浏览器环境与图形栈，PDF 无头渲染依赖 `reportlab>=3.6.0`；
        - FastAPI 的 `TestClient` (基于 Starlette) 强依赖 `httpx`，将 `httpx>=0.24.0` 补充至 `requirements.txt` 与 CI 依赖清单。
    3.  **单元测试依赖未版本化构建产物的环境污染隐患 (Hermetic Testing Rule)**：
        - 发现 `imprints/` 目录属于 `.gitignore` 排除范围，云端全新 Clone 容器中 `imprints/` 为空；
        - 原测试用例直接依赖本地残留的 `imprints/` 目录中已编译的手稿提取译文，缺少自包含性；
        - 重构 `TranslationResolver.resolve_chapter()` 引入 `base_dir` 可选入参，单测改造为使用 `tmp_path` 构造纯净沙箱手稿进行隔离验证，彻底消除环境依赖；
        - 云端流水线全量 106 项装帧测试与 Ruff Lint 100% 绿灯 Pass（耗时缩短至 20 秒）。

---

## 📅 2026-09-29: 多语言对照装帧中枢、按卷直达跳转、极速翻页缓冲队列与移动端响应式闭环 (Polyglot Concordance Bindery, Responsive Matrix & Focus Glow)
*   **现象描述**：
    1.  数字出版装帧（Bindery）多语平行对照（Polyglot Concordance / Matrix）此前在长篇大作（如 33 章节的中-英-日大型对照典籍）中，页脚跳转输入框按全书折算绝对线性百分比换算，导致读者输入“3”意在直达“第 3 卷”，却被换算跳转至“第 1 卷第 3 子页”，造成强烈的心理预期割裂；
    2.  卷内多语子页动画横滑滑动周期约 260ms，当读者极速连击键盘方向键、滚轮或翻页热区时，由于处于动画保护期，后续按键被静默抛弃，产生明显卡顿吞键感；
    3.  移动端与窄屏设备下（≤ 900px），多语顶栏控制条原样式被粗暴隐藏，导致移动端读者完全无法感知或切换语种；且在翻页模式（Paginated）下小屏粗暴纵向堆叠导致主语下方的对照语被视口截断彻底不可见；
    4.  多栏对照排版在跨语种阅读时，左右视线频繁游移寻找对应段落带来严重的视觉疲劳，缺乏段落级联动对齐指示。
*   **根因剖析与工程设计**：
    1.  **卷号优先心理预期对齐与自适应输入控制 (Volume-First Quick Jump)**：
        - 在 `epub_reader_pager_js.py` 中新增 `wb-concordance` 模式自适应感知，智能识别提取 `第 X 卷` 与 `共 Y 卷`，将输入框占位符切换为 `卷`，总量后缀动态切换为 `/ Y 卷`；
        - 在 `epub_reader_polyglot_js.py` 实现 `handlePolyglotGoToPage()`，优先遍历章节卡片精准按 `meta.chapterNum` 匹配，瞬时直达目标卷首屏；
    2.  **极速翻页缓冲防丢帧队列 (Pending Flip Queue)**：
        - 引入轻量级缓冲标记 `pendingFlip`，在动画进行中捕获新的翻页意图并在 140ms 动画收敛后自动补发，彻底消除丢帧与吞键感；
        - 强化前置触底与触顶边界探测，在到达卷首/卷末边界时严格放行给外层阅读器的跨卷翻页控制；
    3.  **移动端与窄屏多语对照自适应 (Responsive Concordance)**：
        - 废除顶栏暴力隐藏，在 `epub_reader_polyglot_css.py` 中针对小屏将控制条转换为极简紧凑药丸胶囊（Compact Capsule），隐藏次要文本标签仅保留国旗与语种简写；
        - 在翻页模式下移动端严格保持 `flex-direction: row` 双列/多列并排，通过 `clamp()` 动态微调字号与间距，彻底消除纵向溢出截断；在卷轴模式下支持紧凑纵向堆叠卡片流；
    4.  **跨语种段落级高亮微光联动与对齐聚焦 (Concordance Para Glow)**：
        - 物理独立拆分 `epub_reader_polyglot_sync_js.py`，自动为各语种栏的块级子元素注入同级索引 `data-para-idx="N"`；
        - 点击任一语言栏的段落时，对应语种段落瞬时激活 `.wb-para-active` 翠绿柔光微发光，在窄屏卷轴模式下自动联动平滑滚入视口，极大降低双面对照阅读疲劳；
    5.  **版权页多语国际化与全量主权回归**：
        - 完善版权页（Colophon）多语言术语字典，严格遵循 SOP-01 规范（所有新改文件均 ≤ 300 行）；
        - 全量 106 项装帧与电子书测试 100% 绿灯 Pass，主权审计 Stage 2.7 前端完整性 100% 闭环。

---

## 📅 2026-09-25: 移动端全协议扫码穿透自愈中枢、插件免密试运行与全域主权审计合规清零 (Mobile QR Tunnel Mesh, Plugin Dry-Run & Sovereignty Clean-Up)
*   **现象描述**：
    1.  数字装订（Bindery）生成的 WebBook 移动端阅览存在局域网 IP 不可达或跨网段隔离（如手机走蜂窝流量、电脑在公司内网）的痛点，传统方案配置 ngrok / cloudflare tunnel 门槛高，需用户配置复杂的 Token 或预装二进制客户端；
    2.  移动端小屏设备扫码预览时，顶部工具栏与操作按钮在不同分辨率下存在横向滚动穿透与视觉截断问题；
    3.  分发渠道插件在品牌层与全局层存在配置脱节，插件测试运行缺乏对公网与免密平台的一键化校验防护；
    4.  系统累积了新增的底层穿透模块，尚未在架构指纹基线中登记，部分 CSS 样式存在硬编码颜色，全域审计脚本存在警告。
*   **根因剖析与工程设计**：
    1.  **移动端全协议穿透网格矩阵 (Tunnel Mesh Engine)**：
        - 架构设计了通用穿透基类 `core/adapters/tunnel/base.py`，统一多驱动生命周期与状态回调契约；
        - 引入零依赖纯 SSH 原生驱动 `pinggy.py` 作为首选默认公网通道，配合免密模式 `cloudflare.py`、`localhost_run.py`、`serveo.py` 以及专用客户端驱动 `cpolar`、`frp`、`ngrok`、`tailscale`；
        - 实现 `core/bindery/tunnel_diagnostic.py` 诊断中枢，支持多网卡嗅探、单驱动瞬时拨测、双通道自动降级与开箱即用状态判断。
    2.  **前端扫码弹窗全息诊断与移动端响应式适配**：
        - 新增 `vault.bindery.qr_diagnostic.js` 与 `bindery.qr_diagnostic.css`，支持「局域网直接连接」与「公网隧道穿透」双模切换，展示驱动连通性脉冲呼吸灯与开箱即用徽章；
        - 彻底解决移动端小屏横向溢出，对顶栏控制栏引入弹性收缩与流式布局，保证高精度阅读体验。
    3.  **插件免密试运行与品牌激活主权**：
        - 实现 `plugin_dry_run.py` 试运行沙箱，支持前置语法与连通性验证；
        - 对齐品牌层免密授权与全局配置感知，消除假密钥误报。
    4.  **全域合规审计大清零 (Sovereignty Clean-Up)**：
        - 物理更新 `.plenipes/governance/structure.baseline`，全量对齐 479 个系统架构文件，架构越权清零；
        - 样式变量 100% Token 化，修复 `bindery.qr_diagnostic.css` 与 `modals.base.css` 的硬编码色值；
        - 所有模块严格遵循 SOP-01（≤ 300 行）；
        - 全量 853 项自动化冒烟单测 100% 绿灯闭环。

---

## 📅 2026-09-19: 全站前端模块工业级物理重构宪章落地与 SOP-01 超限大盘彻底清零 (Frontend Architecture Refactoring & Zero Oversize Limit)
*   **现象描述**：
    1.  随着 Illacme Plenipes 数字主权系统多语种、全域分发、图谱工作台、建站向导等复杂业务演进，前端代码库中累计出现 21 个物理文件超过 SOP-01 规约中的单文件 ≤ 300 行硬指标；
    2.  超限文件不仅包含 301~390 行的微超限模块，还存在 `modals.js` (649行)、`plugins.render.pod.js` (467行)、`route.slug.sandbox.js` (466行)、`core.terminal.js` (456行)、`route.render.js` (429行) 等多个巨型中枢组件；
    3.  巨型单文件承载多重混合职责（DOM 模版声明、网络交互、状态机联动、物理拖拽算力动画），导致局部修改极易引发隐蔽回归，维护难度急剧攀升。
*   **根因剖析与重构架构设计 (SOP-01 / SOP-02 工业重构六大铁律)**：
    1.  **自底向上三梯队渐进式物理拆分战略**：
        - **第一梯队（微超限 9 个文件）**：物理抽离 `platforms.publishers_domestic.js`、`platforms.notifications.events.js`、`vault.drawer.cards.js`、`system.save.js` 等，迅速实现微超限闪电清零；
        - **第二梯队（次微超限 6 个文件）**：物理抽离 `route.i18n_ai.js`、`plugins.render.status.js`、`plugins.render.loader.js`、`core.descriptions.js` 等高频交互模块；
        - **第三梯队（400+ 行巨型中枢 6 个文件）**：
          * `plugins.render.cards.js` (403行 ➔ 196行)：拆出 `plugins.brand_activation.js`；
          * `route.render.js` (429行 ➔ 256行)：拆出 `route.slug_render.js` (186行)；
          * `core.terminal.js` (456行 ➔ 257行)：拆出 `core.deploy_summary.js` (213行)；
          * `route.slug.sandbox.js` (466行 ➔ 237行)：拆出 `route.slug_actions.js` (259行)；
          * `plugins.render.pod.js` (467行 ➔ 282行)：拆出 `plugins.render.badges.js` (136行) 与 `plugins.render.physics.js` (78行)；
          * `ui/modals.js` (649行 ➔ 181行)：拆出 `modals.system.js` (181行)、`modals.wizard_step3.js` (226行) 与 `modals.wizard_success.js` (89行)。
    2.  **契约兼容与零破坏性保障**：
        - 拆分遵循“母本纯粹中枢 + 子分片能力下沉”的拓扑设计，严格保留原有所有全局公共 API、函数签名、DOM 容器 ID 与 class 选择器；
        - 在 `modals.js` 与 `modals.wizard_step3.js` 之间通过防守式全局挂载与动态安全检测聚合子分片 HTML，杜绝跨文件依赖裂解。
    3.  **全量拓扑注册与自动化沙箱门禁**：
        - 在 `web/dashboard/index.html` 中严格按拓扑依赖顺位注册所有新分片，达成 **0 漏引、0 孤儿**（Rule 14）；
        - 在 `tests/test_frontend_integrity.py` 扩充 CRITICAL_MODULES 列表，实现静态编译与拓扑全覆盖；
        - 在 `tests/test_frontend_render_integrity.py` 补充 Node.js 沙箱真实执行与核心 DOM 节点拓扑断言（Rule 7）；
        - 修缮 `tests/test_imprint_wizard_e2e_flow.py`，支持向导分片聚合断言与 6 大装帧主题完整性校验。
*   **物理验证与量化成果**：
    - **全站超限大盘清零**：全站 244 个前端 JS 文件，超过 300 行的文件数从 **21 个彻底归零（0 个）**，100% 达成 SOP-01 规范；
    - **V8 语法静态编译**：全站所有分片通过 `node -c` 检查，0 语法错误；
    - **主权工程大审计**：`scripts/sovereign_audit.py` 全阶段大审计完全通过，自动化冒烟测试 **714 passed (exit code 0)**。

---

## 📅 2026-09-14: 社交媒体全渠道分发封面公网闭环与智能防呆演进 (Syndication Cover Hosting & Preflight Guard)
*   **现象描述**：
    1.  微信公众号分发时，若封面为设计中心生成的本地资产路径（`/api/design/assets/covers/gen_xxx.jpg`），因路径未穿透至文库根目录导致获取为空，静默降级为 900x383 默认黑底科技边框卡片；
    2.  Dev.to、Hashnode、B站专栏、今日头条等渠道强依赖公网绝对 HTTP/HTTPS 图片 URL，若用户使用本地封面，因缺少图床转存导致外部平台无法展示头图或报错；
    3.  创作者在分发抽屉中无法直观获知哪些渠道强依赖封面，且在未设置封面时缺乏前置防呆提示与一键补全通道。
*   **根因剖析与工程设计**：
    1.  **分发装载层路径穿透与自愈支持**：
        - 在 `pipeline_syndicate_loader.py` 中为原稿 Frontmatter 注入 `doc_dir`、`file_path` 和 `vault_root`，解决下游驱动本地寻址盲区；
        - 在 `wechat_uploader.py` 中接入 `vault_root` 与 JIT 自愈恢复器 `serve_cover_asset_or_heal`，彻底打通微信永久素材 `thumb_media_id` 上传链路；
    2.  **全渠道封面公网转存防线 (`upload_cover`)**：
        - 在 `core/syndication/uploader.py` 新增 `upload_cover()`，自动探测物理封面文件并委托系统已启用的图床插件（Cloudflare R2, ImgBB, Catbox, S3 等）或独立站 CDN 映射为公网直链；
        - 在 `core/syndication/hub.py` 分发前置阶段自动将 `metadata["cover"]` 转存并回填；并在 `devto.py` 中注入 `payload["article"]["main_image"]`；
    3.  **全渠道封面需求辨识徽标与前置智能防呆**：
        - 在 `syndicate.cards.js` 中为渠道卡片注入珊瑚红「🖼️ 必配封面」与天青蓝「🖼️ 推荐题图」高辨识度徽标与完整浮动 Tooltip；
        - 在 `syndicate.dispatch.js` 增加 `showCoverPreflightModal` 前置防呆守卫，检测到勾选必配平台且无封面时优雅弹窗，支持「一键 AI 意境生图并继续分发」；
    4.  **社交即时审查 (Live Preview) 信息流大图模拟**：
        - 在 `syndicate.preview.js` 顶部动态渲染高保真社交卡片流（微信 2.35:1 消息卡片、小红书 1:1 瀑布流卡片），实现所见即所得。
*   **物理验证与实机门禁**：
    - 所有修改文件严格遵守 SOP-01（`uploader.py` 191 行、`devto.py` 196 行、`cards.js` 222 行、`dispatch.js` 297 行、`preview.js` 293 行）；
    - `pytest tests/test_wechat*.py` 与 `test_frontend_integrity.py` 100% 通过；
    - 无头浏览器双层实机验收，卡片徽标与真机审查完美闭环。

---

## 📅 2026-09-09: 线上站点全球边缘健康度雷达 (Live Health & Latency Radar) 架构落地
*   **现象描述**：
    1.  全域发布向 Vercel、GitHub Pages 等 CDN 渠道投递后，终端看板仅输出静态 URL 文本，创作者无法实时感知站点在全球边缘节点的健康状态、HTTP 状态码及 RTT 往返时延（ms）；
    2.  境内网络在直接发起探测请求时容易受网络波动影响出现假性超时，需要自动感知本地代理加速通道；
    3.  部分静态 CDN 边缘服务器出于安全策略对 `HEAD` 请求返回 405 Method Not Allowed，若缺乏自愈机制会导致误报；
    4.  终端日志中的 URL 偶尔附带括号（如 `(实例: https://...app)`），若直接捕获会导致末尾标点混入链接引发 404。
*   **根因剖析与工程设计**：
    1.  **后端并发雷达探测端点与协议适配**：
        - 拆分独立治理分片 `services/api/routes/gov/actions_shards/health_radar_ops.py`；
        - 在 `services/api/routes/gov/actions.py` 注册 `POST /api/governance/health-radar` 端点；
        - 实现 `_resolve_effective_proxy()` 嗅探机制，支持从环境变量与本地常用加速端口（10809/7890/1080）自动挂载代理；
        - 采用 `ThreadPoolExecutor` 高性能异步并发，对所有上线渠道 URL 并行发起探测；
        - 优先发送零带宽开销的 `HEAD` 轻量请求，遇到 405/403 自动降级为流式 `GET`（仅读 Headers 即断开），根绝误报；
        - 基于 `Server`、`Via`、`x-vercel-id`、`x-github-request-id` 等响应头，毫秒级指纹比对出 CDN 供应商名称。
    2.  **前端终端全息徽章与交互联动**：
        - 在 `web/dashboard/js/core/core.terminal.js` 的 `renderDeploymentSummaryCard()` 中，为每个上线成功的渠道卡片注入 `.health-radar-badge`；
        - 终端弹窗渲染后自动延迟 200ms 点火探测，动态回填如 `⚡ 956ms · HTTP 200 (GitHub Pages)`，支持异常时呈现 `⚠️ 异常 · HTTP 502`；
        - 在看板操作栏增加 `⚡ 刷新测速` 按钮，赋予创作者随时一键重新打测速包的能力；
        - 重构 URL 提取正则，强制剔除末尾闭合字符 `/[),.;!?:\]]+$/`，根治 URL 尾随符号污染。
    3.  **样式适配与高质感视觉**：
        - 补充 `web/dashboard/css/themes/theme.light.overrides.css` 亮色主题高对比度样式，兼顾暗色毛玻璃与亮色高清晰度。
    4.  **自动化守护与门禁**：
        - 接入 `tests/test_health_radar.py` 自动化测试套件（单测、厂商指纹匹配、批量并发）；
        - 通过 `pytest tests/test_frontend_integrity.py` 与 Node.js 真实运行沙箱校验，满足 Rule 7 与 Rule 11 物理铁律。

## 📅 2026-09-07: 文章正文顶部出版级全息装帧元数据栏通用引擎跨主题实装 (Article Header & Reading Telemetry)
*   **现象描述**：
    1.  读者阅读文章时缺乏对正文字数、预计阅读时长、修订版本的直观感知；
    2.  双语/多语种矩阵中，读者在进入特定语言页面时无法快速感知并一键穿梭切换至同一手稿的其他语言版本；
    3.  各 SSG 主题（Nextra、Docusaurus、Starlight 等）渲染机制各异，且存在异步竞态导致重复挂载或样式割裂的风险。
*   **根因剖析与工程设计**：
    1.  在 `core/bindery/garden_exporter.py` 中强化手稿语义图谱，导出手稿摘要与全局路由映射；
    2.  设计零依赖跨主题通用引擎 `article-telemetry-core.js`：
        - ⏱️ 智能统计 CJK 汉字与西文字词，精准计算预计阅读时间；
        - 📅 自动解析修订日期与版本时间戳；
        - 🌐 基于全局路由图谱自动嗅探同源 Slug 的多语种版本，生成高亮激活与穿梭链接胶囊；
        - 🛡️ 设计双重锁与单例幂等清理机制（`data-telemetry-mounted` / `data-telemetry-mounting` + 插入前 `oldBars.forEach(b => b.remove())`），根绝异步竞态与 SPA 路由二次加载重复注入。
    3.  各主题原生挂载与 1:1 版图同步：
        - Nextra：在 `components/LinkedMentions.jsx` 中按路由与语言状态动态挂载；
        - Docusaurus：在 `clientModules/routeGuard.js` 与 `DocItem/Footer/index.js` 中挂载；
        - Starlight：在 `CustomFooter.astro` 内联脚本中以动态 import 挂载（严格保持 ≤ 300 行）。
*   **物理验证与实机验收凭证**：
    - V8 静态编译 (`node -c`) 与 `pytest tests/test_frontend_integrity.py`、`python scripts/sovereign_audit.py` 538 项测试 100% 通过；
    - 逐个拉起 Nextra、Docusaurus、Starlight 实机服务（43213），浏览器无头 subagent 截取实机快照，断言元素计数严格为 1，多语种胶囊与阅读指标真实可用。

---

## 📅 2026-09-06: 知识图谱升级版图全局单例与 Nextra 配置平滑适配 (Knowledge Graph Singleton & Nextra Parity)
*   **现象描述**：
    1.  本地发布时用户切换装帧主题（如从 `sovereign` 首次切至 `nextra`），系统重新调用了大模型进行语义分析（NER & Gist 提取），且静态服务器访问根目录时暴露了 `Directory listing for /`；
    2.  Nextra DevServer 启动时抛出 `TypeError: require(...) is not a function at Object.<anonymous> (next.config.js:1:37)` 导致预览服务异常退出。
*   **根因剖析**：
    1.  知识图谱此前按主题物理隔离存储在 `imprints/{imprint}/metadata/themes/{theme}/knowledge_graph_{theme}.json`，与排版主题错误耦合；首次切至新主题时账本为空，导致系统误判为新内容而触发重复大模型语义提取；
    2.  Nextra 母本安装了最新的 4.x/React 19 尝鲜版本，其与 Nextra 2.x 的 `theme.config.js` 配置规范产生代差（4.x 废弃了 `withNextra({ theme: ... })` 的参数格式且为 ESM/CJS 混编导出）。
*   **防线策略与沉淀**：
    1.  **知识图谱提升为版图级全局单例 (`get_knowledge_graph_path`)**：
        - 在 `core/config/config_models.py` 中新增 `get_knowledge_graph_path()`，统一将知识图谱锚定至 `metadata/core/knowledge_graph.json`；
        - 在 `core/runtime/assemblers/component_assembler.py` 中统一组装全局单例；
        - 在 `core/logic/knowledge/knowledge_migrator.py` 中实现向前兼容物理自愈迁移：全局账本为空时自动聚合所有历史旧主题的图谱数据，彻底消除切换主题时的重复大模型开销。
    2.  **Nextra 生产级现代配置平滑适配**：
        - 锁定稳定成熟的 `nextra@^2.13.4`、`nextra-theme-docs@^2.13.4`、`next@^14.2.5`、`react@^18.3.1` 黄金组合；
        - 在 `themes/nextra/next.config.js` 中使用 `const nextra = _nextra.default || _nextra;` 进行防御性解构，确保 CJS/ESM 混编环境下 100% 稳健启动。
    3.  **全域主权门禁 494 项测试 100% 绿灯准予提交**：
        - `core/logic/knowledge/knowledge_graph.py` 严格收敛在 297 行（严格低于 300 行红线）；
        - `scripts/sovereign_audit.py` 全部 8 项治理阶段全绿通过。

---

## 📅 2026-09-06: Nextra 与 VitePress 独立单页 Clean URL 与多语言前缀自愈 (SSG Nav & Options Parity)
*   **现象描述**：在异构 SSG 架构下，独立单页（如 `about.md`）在 Nextra 与 VitePress 中由于路由合成器未细分单页与频道，导航链接被附加了末尾斜杠（`/about/`），导致静态托管服务寻找不存在的 `about/index.html` 目录并触发 301/302 重定向甚至 404；且多语言矩阵下单页链接丢失语种前缀（如跳回默认语言 `/about`），同时 Nextra 的 `i18n` 与 VitePress 的 `locales` 未能与 `route_matrix` 的多语言导航结构完成自动化热编译水合。
*   **根因剖析**：
    1.  `SSGNavSynthesizer` 早期仅对通用频道执行 `/{prefix}/` 的目录级拼接，未对单页槽位（`slot in ("pages", "page")` 或特定单页 prefix 如 `about`、`terms`、`privacy`）做 Clean URL 无斜杠特化；
    2.  多语言循环 `nav_links_i18n` 中未统一将目标语言前缀（如 `/en`、`/ja`）与 Clean URL 规则做闭包统一计算；
    3.  `SSGThemeCompiler` 编译输出时缺乏对 Nextra `i18n` (包含 `defaultLocale` 和 `locales` 列表) 及 VitePress `locales` 树结构的自动化生成与注入。
*   **防线策略与沉淀**：
    1.  **路径合成闭包化 (`_calc_target_path`)**：在 `SSGNavSynthesizer` 中统一提取单页识别与 Clean URL 运算逻辑，对 `is_clean_url` 环境下单页输出精准的 `/{lang}/{prefix}`（严禁末尾斜杠），目录频道输出 `/{lang}/{prefix}/`；并加入 SOP-08 防御性解包（`isinstance(routes, list)`）。
    2.  **异构 SSG Options 动态编译水合**：在 `SSGThemeCompiler` 中原生实现 `nextra`（输出标准 `i18n` 与 `defaultLocale`）和 `vitepress`（输出带有 `root` 与各语种 link 的 `locales`）的编译逻辑，确保两款引擎可直接消费 `theme.options.json`。
    3.  **穿透测试与全域主权门禁 100% 覆盖**：在 `tests/test_universal_navigation.py` 中新增 `test_nextra_and_vitepress_standalone_page_and_i18n_parity` 完整断言，494 项全域主权测试与代码红线全部 100% 绿灯。

---

## 📅 2026-09-06: Sovereign 主题适配器大文件物理拆分与治理豁免消减 (SOP-02 Modularization)
*   **现象描述**：`themes/sovereign/adapters/sovereign_helpers.py` 物理行数历史膨胀至 717 行，严重突破 300 行警戒线及 500 行强制重构硬红线，长期处于 `.plenipes/governance/exemptions.yaml` 豁免白名单中，违背精益架构主权。
*   **根因剖析**：早期的 `sovereign_helpers.py` 作为“万能辅助模块”，承担了树状侧边栏测绘、案例多视图自适应转换、语言切换器动态装配、主导航渲染、上下篇分页计算以及主模版注入等多重异质职责，导致职责混杂与单体过大。
*   **防线策略与沉淀**：
    1.  **全功能微模块解耦 (Fine-Grained Shards)**：严格按照单一职责原则拆分为 4 个高度聚焦的子模块：
        - `sovereign_sidebar.py` (155 行)：专注于树状侧边栏测绘、标题物理提取与活跃状态标记；
        - `sovereign_showcase.py` (76 行)：专注于案例展厅双视图（网格卡片/紧凑列表）自适应重塑；
        - `sovereign_switcher.py` (122 行)：专注于多语言切换器动态装配与 hreflang 智能计算；
        - `sovereign_nav_builder.py` (259 行)：专注于主导航三模态渲染、上一篇/下一篇链接查找与 Canonical URL 计算；
    2.  **对外公开契约零破坏 (100% Re-export Hub)**：`sovereign_helpers.py` 收敛为协调中枢（283 行），通过 `__all__` 完整 re-export 所有既有函数签名，确保各 SSG 调度层与单元测试完全无感调用。
    3.  **终结技术债与豁免归零**：每个分片文件严格控制在 300 行以内，成功从 `.plenipes/governance/exemptions.yaml` 中永久移出，全量 493 项自动化测试及主权审计门禁 100% 绿灯准予提交。

---

## 📅 2026-09-02: 全球 50 语种前台组件视图与国际化架构解耦重构 (View I18N Matrix)
*   **现象描述**：博客与案例展厅等前台页面的视图切换按钮（如时间轴、卡片、列表）在早期实现中，使用了硬编码的语言分支判断（仅判断 zh/en/ja），导致在切换到西、法、俄、德、阿、韩等其他数十种主流语种时无法呈现地道母语，违背了商业级多语言出版产品的设计标准。
*   **根因剖析**：未将前台组件与视图的交互词汇纳入系统级国际化标准字典；业务层代码（SSG 归档器、主题模板辅助器）越权承担了语言分支逻辑。
*   **防线策略与沉淀**：
    1.  **50 语种全局视图矩阵（VIEW_I18N_MATRIX）**：在 `ssg_slot_matrix.py` 中 100% 对齐系统 `SUPPORTED_MATRIX` 50 大语种规范，统一建立 `timeline`、`cards`、`list`、`all`、`read_more` 等组件级词汇矩阵。
    2.  **通用级联解析器（get_i18n_view_label）与主题 UI 字典无缝打通**：通过精确匹配 -> 语族前缀 -> 英文降级的级联算法，让 `get_ui_i18n(lang)` 自动覆盖全量 50 语种。
    3.  **业务代码 0 语言硬编码**：彻底移除所有页面渲染层中的 `if lang == 'zh'` 分支，全面改用动态矩阵查询，实现真正可扩展的商业级全语种自适应。

---

## 📅 2026-09-01: 频道路由矩阵（Route Matrix）单篇文件与分组选择器交互重构
*   **现象描述**：频道映射配置中，文库来源下拉框只列出物理目录，无法点选单篇稿件（如 `about.md`）；且一旦创作者切为“自定义输入”后，界面单向锁定无法切回下拉列表；同时缺少最终三模态产物路径推演。
*   **根因剖析**：底层扫描器（`scanner.py`）天然支持单篇文件与目录双轨匹配，但前端装配数据时仅注入了 `_directories`，未消费 `_vault_files` 稿件列表；且自定义模式下没有保留恢复 `<select>` 渲染的逆向控制句柄。
*   **防线策略与沉淀**：
    1.  **分组选择器（Grouped Selector）**：在 `<select>` 中通过 `<optgroup>` 明确区隔「📁 专题目录（整栏映射）」与「📄 单篇稿件（独立单页）」，并在自定义输入框右侧附加 `🔄` 逆向恢复按钮，消除单向死穴。
    2.  **三级意图自动联动与三模态实时推演**：点选单篇文件自动联动切换模板为 `📄 独立页面 (pages)` 并填充去除后缀的路径与文档标题；在网页路径下方实时渲染推演徽标（如 `👉 产物: /about.html`），消除创作者盲猜成本。

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

## [算力网关革命] Tool Use 函数调用大一统协议实现
- **时间**: 2026-05-29 00:37:57
- **目标**: `core/adapters/ai/` 与 `adapters/compute/openai.py`
- **执行内容**:
  1. 新建了 `core/adapters/ai/tool_protocol.py`，定义了跨平台的 `IllacmeTool` 和 `ToolCallEvent`。
  2. 升级了 `PayloadManager.prepare_payload`，正式支持大模型的多轮 `messages` 注入和 `tools` 字典组装。
  3. 彻底重构了 `OpenAICompatibleTranslator._ask_ai`。现在它不仅能发送工具契约给模型，更能精准拦截模型返回的 `tool_calls`，并将其翻译为标准的 Python 对象阵列反馈给系统，成功打破了大模型“只能聊文本”的禁锢。
- **验证**: 通过物理脱机测试脚本 (`test_tool_use.py`) 验证了序列化流向，结构完美。

## 📅 2026-05-29: CSS 加载顺序导致的高度坍塌与伪元素绝对定位引起的滚动条爆炸
*   **现象描述**：
    1. 左侧边栏本应可以上下滚动，却被强行截断无法滚动。
    2. 下拉菜单和原稿文库的内部文件列表下方，凭空出现了极其巨大的空白可滚动区域（超长滚动条）。
*   **根因剖析**：
    1. **层叠优先级与加载顺序倒挂**：我们在拆分出的 `glass.layout.css` 里给 `.sidebar` 赋予了 `overflow-y: auto;`。然而由于之后引入了具有动画特效的 `dashboard.animations.css`，为了防止玻璃光泽溢出，在其中为 `.glass-panel` 加了 `overflow: hidden;`。由于 `.sidebar` 和 `.glass-panel` 的 CSS 特异性完全相同（皆为类选择器，0,1,0），导致后加载的 `overflow: hidden` 赢得了级联冲突，硬生生屏蔽了侧边栏的滚动。
    2. **伪元素撑爆绝对定位与 Scroll 容器交互漏洞**：`dashboard.animations.css` 中的光泽动画是通过 `::after` 伪元素并设置 `width: 200%; height: 200%; position: absolute;` 实现的。当带有该伪元素的容器（如下拉菜单和文库列表）被强行施加 `overflow-y: auto` 时，原本隐藏的 200% 高度绝对定位元素被浏览器纳入了“可滚动计算范围”，从而导致容器内向下延展出长达本体 1.5 倍的空白滚动幽灵区域。
*   **防线策略与沉淀**：
    1. **真实浏览器 DOM / CSS 抓取倒逼验证**：不要仅仅靠“肉眼”和“经验”阅读样式。前端重构必须将 Playwright / Puppeteer 的 Computed Style 提取程序（或人工开发者工具审查）纳入核心验证循环，让机器输出最终应用的实际 `overflow` 状态，而不是凭借脑图臆想。
    2. **滚动容器与绝对定位伪元素的物理隔离**：绝对禁止在拥有 `overflow-y: auto` 的滚动容器本体上施加超出 100% 尺寸 of 绝对定位伪元素特效。此类全局特效要么被 `display: none !important;` 针对性剔除，要么将其挂载在只带 `overflow: hidden;` 的独立父级外壳 DOM 上进行物理隔离。
    3. **提权防卫机制**：针对核心布局骨架（如 Sidebars），在面对多模块 CSS 加载乱序的潜在风险时，应果断通过增设 ID 选择器或 `!important` 建立护城河，防御后期特效库的无意识全局覆盖。

## 📅 2026-06-06: 单元测试中 MockEngine 缺失核心属性与解包结构不一致导致的任务级脑裂
*   **现象描述**：在进行 AI 容错热接力机制（Fault Tolerance）开发后，针对其编写的单元测试在 Mock 阶段发生 AttributeError（由于 MockEngine 缺少 `meta` 和 `dispatcher` 等核心环境属性）及 ValueError（解包结果与 `dispatch_targets` 返回的字典结构冲突）。
*   **根因剖析**：
    1.  **复杂依赖链条的局部 Mock 盲区**：在编写 `dispatch_ops.py` 时引入了新版本的属性与分发控制流（例如在 `as_completed` 循环中使用了 `engine.meta.is_watch_mode` 和 `engine.dispatcher.dispatch`）。然而，针对该模块测试构造的 `MockEngine` 和 `MockContext` 未能前瞻性对齐这些在后续生命周期中调用的系统组件，导致 Mock 调用崩塌。
    2.  **契约定义与测试解包断言脱节**：`dispatch_targets` 最终返回的是 `target_results` 字典，包含了每个语种的健康状况和 SEO 数据（格式为 `{"en": {"health": bool, "seo": dict}}`），而测试中仍采用了旧版 5 元组解包（`code, body, target_fm...`），破坏了返回值契约一致性。
*   **防线策略与沉淀**：
    1.  **单元测试与实际流出物理对齐**：编写 Mock 测试时，不能仅模拟所改动方法入参的浅表属性，必须细致梳理被测试函数在其调用层链路上的所有下游对象引用（如 `engine.dispatcher` 等分发器）。若有下游调用，必须完整提供 Mock 接口或 MagicMock，并从下游被调用方的 `call_args` 或参数列表中断言业务层流出的数据。
    2.  **契约校验一贯性**：修改函数的返回值结构后，必须立即对齐所有单元测试的断言解包结构。在测试中优先使用字典或命名元组获取键值，避免脆弱的多元素顺序解包带来的运行时 ValueError。

## 📅 2026-06-06: 单元测试中 WebSocket 接收无数据时阻塞挂起与 TestClient 缺乏 timeout 参数支持
*   **现象描述**：在编写 `test_telemetry_resilience.py` 测试时，尝试调用 `websocket.receive_json()` 验证在无离线消息重放时的场景，导致测试线程无限期挂起阻塞；随后向 `receive_json(timeout=0.1)` 传递超时参数时，遭到 Pyrefly 的类型/签名不符警告。
*   **根因剖析**：
    1.  **TestClient 同步接收阻塞设计**：FastAPI / Starlette 提供的 `WebSocketTestSession` 在测试线程中以同步模拟 ASGI 管道，其 `receive_json` 底层如果没有接收到任何事件消息，其事件队列的 `get` 逻辑会同步永久挂起，直至外围被强行终止。
    2.  **签名契约约束**：Starlette 测试会话的 `receive_json` 等方法的包装层在某些定义中并未直接暴露出 `timeout` 参数，强行传递会导致签名校验错误。
*   **防线策略与沉淀**：
    1.  **使用 anyio 外围超时防护**：测试任何“不应收到消息”或“在网络断开时不再接收新数据”的空值边界时，决不能依赖空读阻塞，必须使用 `anyio.fail_after(delay)` 保护上下文块来优雅包覆可能阻塞的 socket 操作，从而在超时时抛出 `TimeoutError` 进行断言捕获。
    2.  **契约与 Lint 优先对齐**：避免向没有明确类型参数声明的底层模拟类（如 `WebSocketTestSession`）传递多余的控制参数，通过外部通用的协程/超时管理器代替特定类的私有控制参数，保持测试套件的整洁与高兼容。

## 📅 2026-06-06: 大媒体资产懒加载掏空构建后差分合并时导致历史快照误删的数据溃决与物理行数红线应对
*   **现象描述**：在实现增量编译端媒体大资产掏空隐藏进行编译剪枝时，由于 SSG 编译器在 build 时未感知媒体大文件导致最终 `site_dir` 中缺少该资产。在最后执行目录差分物理合并时，快照目录中已存在的大文件被判定为已删除的“孤儿文件”而被直接删除，发生快照数据丢失。同时，向接近 300 行限界的文件添加逻辑极易触发 pre-commit hook 的行数门禁拦截。
*   **根因剖析**：
    1.  **输入与输出的编译侧脑裂**：编译器编译时跳过的大文件，必须在编译完成后回填到生成的目标目录 `site_dir` 中，使目标目录状态恢复 100% 对齐。如果省略回填，差分对齐逻辑（例如 `_incremental_copy_tree` 的孤儿清理机制）会误将其识别为已从源端删除的“孤儿”而将其从快照中移除。
    2.  **物理行数设计硬上限超标**：向老旧高频修改文件（如 `github_pages.py` 的 292 行）中无节制添加代码会导致行数直接崩塌超标。
*   **防线策略与沉淀**：
    1.  **掏空必须对应回填防线**：在装帧端实施非 Markdown 物理资产掏空隐藏进行编译剪枝时，编译结束后必须**立刻且物理强制**将这些被隐藏的资产增量回填（复制）至编译输出目录 `site_dir` 中，然后再调用差分合并目录算法，阻止孤儿清理机制误删大文件快照。
    2. **行数超标清剿协议**：添加核心算法逻辑前必须预估物理行数基础。若文件接近限界，严禁无节制增补，必须首先清剿非业务层的大段静态注释、冗长文档说明及空行，释出至少 10% 的物理行数空余额度，以规避提交层面的拦截并维系架构纯度。

## 📅 2026-06-08: 单元测试中 MagicMock 与 MockEngine 引起的数据类型及序列化异常脑裂
*   **现象描述**：在运行测试套件 `pytest` 时，`test_ai_hot_failover_and_retry` 与 `test_bindery_dispatcher_i18n_seo_cross_injection` 因 Mock 对象的不合理评估而抛出 `TypeError` 和 `RepresenterError` 崩溃。
*   **根因剖析**：
    1.  **Mock 链式返回导致比对崩塌**：测试环境中的 `engine.config.translation` 是一个未定制属性的 `MagicMock`，调用其属性会动态产生新的 `MagicMock`，这使得 `getattr(..., 1)` 无法退避到默认值 `1`，进而导致其与 `int` (例如 `<= 1`) 比较时报类型错误。
    2.  **Truthy Mock 的隐式溢出与污染**：`self.meta` 如果是 `MagicMock`，其返回的子属性如 `_lang_meta.get("reviewed_desc")` 仍会是 Truthy 的 Mock 对象。系统未对从 `self.meta` 中获取的值进行强类型字典（`dict`）和非 Mock 对象防御，导致 Mock 对象被误注入 Frontmatter 元数据并直接传递给 `yaml.dump`，引发序列化不可表示错误。
*   **防线策略与沉淀**：
    1.  **配置与对象读取的强类型硬防线**：在获取如并发、配额、文档快照字典等非文本属性时，必须在读取处对对象或其属性进行显式的类型安全判断（如 `isinstance(val, (int, float))` 或 `isinstance(val, dict)`）并对 `type(val).__name__` 进行防卫，阻断空值或 Mock 对象的链式透传。
    2.  **API/Mock 调用的存在性感知防线**：对外部环境对象（如 `engine.meta`）进行调用前，不仅要使用 `hasattr(engine, "meta")` 进行一层防护，还必须检查目标调用方法本身是否存在（如 `hasattr(engine.meta, "get_doc_info")`），消除单元测试中伪造的对象因缺少对应属性方法而引发的 `AttributeError` 崩溃。

## 📅 2026-06-08: 前端校对工作台打字防丢交互与无感增量 DOM 更新
*   **现象描述**：在为人工校对抽屉工作台（Review Drawer）引入脏态（未保存修改）高亮交互时，若在用户每次在输入框打字触发 `oninput` 时都重新渲染整个工作台页面，会导致打字输入焦点（Input Focus）瞬间丢失，页面卡顿且无法连续打字。同时，关闭抽屉时若不进行脏态检测，极易因用户误触丢弃已录入的校对成果。
*   **根因剖析**：
    1.  **全局重新渲染导致 DOM 树重建**：常规的前端刷新策略（如重新调用 `_reviewRenderBody()`）会卸载并重建整个编辑面板 DOM 节点。由于原 input / textarea 物理节点被替换，浏览器的激活焦点与光标位置会瞬间被丢弃，导致无法正常输入。
    2.  **快照缓存未同步覆盖导致脏态恒定**：人工校对锁在保存成功后，只更新了服务端状态和 `human_approved` 标志，但未在本地内存中将最新的修改（`state.edits[lc]`）同步覆盖至缓存快照（`state.data.langs[lc]`），使得保存操作结束后，系统再次比对二者时仍会误判为“脏态”。
*   **防线策略与沉淀**：
    1.  **增量式 DOM 更新与聚焦保护 (Incremental DOM Updates)**：禁止在实时打字（`oninput`）交互中采用全量刷新。对于 Tab 上的黄色圆点 `●`、状态栏的 `⚠️ 未保存修改` 标识、以及保存按钮的阴影发光边框，必须使用 `insertAdjacentHTML` 或直接控制 style 等增量 DOM 修改手段，精准插入/删除对应标记，完美维系 input 的焦点连续性。
    2.  **内存状态同步覆盖防线**：在成功执行“保存并锁定”的 API 交互后，内存中的原始数据快照必须与当前 edits 状态执行深拷贝对正，将 `paragraphs`、`title`、`desc` 完备同步并清空段落的 `_edited` 临时标志。此时可安全触发全量 `_reviewRender()` 重置界面状态，彻底消除伪脏态问题。
    3.  **多语种脏态独立捕获与防丢失拦截**：拦截抽屉关闭事件，在 `window.closeTranslationReview` 挂载全局防丢拦截。遍历所有已加载的语种，只要有一个存在 `_isReviewDirty(lc)` 返回 `true`，必须弹出 `confirm` 提示拦截误触；若用户切换 Tab，脏态可被独立并保留。

## 📅 2026-06-08: 知识图谱增量更新、内存逆向索引与 NLP Cache Guard
*   **现象描述**：知识图谱深度语义挖掘在处理大型语料库时耗时极长（需调用大模型 API 提取实体和摘要），且织网阶段采用 `[:100]` 的硬采样导致大量共享实体关联被遗漏。
*   **根因剖析**：
    1.  **无状态 AI 重复提取**：文档即使哈希未变（即内容无修改），每次增量构建时仍会再次触发 NLPAdapter 深度分析，造成严重的 API 资源浪费与时间卡顿。
    2.  **织网效率低下**：基于实体的强关联（SHARED_ENTITY）依靠双重遍历，为了防止在大型图谱中发生性能抖动而引入了 `[:100]` 硬编码，丧失了全局织网的完备性。
*   **防线策略与沉淀**：
    1.  **NLP Cache Guard 防线**：在 `SemanticLinkerStep` 中引入基于 `source_hash` 的增量比对机制。如果当前文档的哈希匹配且缓存中有完备 of `entities` 与 `gist` 节点，则自动短路并跳过高开销的 AI 提取，复用现有图谱数据。
    2.  **内存逆向索引优化 (Memory-based Inverted Index)**：在 `KnowledgeGraph` 内存中增量维护一个以实体为 Key、以 `doc_id` 集合为 Value 的反向索引 `entity_inverted_index`。检索共享实体时通过 $O(M)$ 级别的极速检索规避 $O(N)$ 遍历，安全移除 `[:100]` 的硬限制，达成 100% 无遗漏的全局逻辑织网。

## 📅 2026-06-08: 多语言并发调度隔离控制与救援线程增殖防御限流
*   **现象描述**：在高并发大批量笔记分发时，系统后台的临时翻译线程和嵌套自愈救援线程会无节制增多，可能在大批量任务堆积且 API 响应慢时发生死锁，造成进度条卡死或引擎 OOM 崩溃。
*   **根因剖析**：
    1.  **局部线程池失控**：多语言并发分发在 `dispatch_ops.py` 中物理创建了临时的 `ThreadPoolExecutor`，这打破了全局 `ai_executor` 和流程池 `global_executor` 的统一配额限流约束。
    2.  **死锁自愈机制无上限**：嵌套任务提交时触发的救援机制 `OrchestratorRescue` 缺乏数量防护，在极高频嵌套和拥堵下会无节制物理派生出上百个救援线程，引发资源枯竭。
*   **防线策略与沉淀**：
    1.  **全局隔离算力委托防线**：废止局部物理创建 `ThreadPoolExecutor` 的方式，将多语言翻译任务全部委托并提交至全局专职隔离的 `ai_executor` 中。这一方面实现了流程控制与算力消耗的物理隔离，另一方面使得翻译的瞬时连接数完全受制于全局 `ai_workers` 红线，彻底遏制了无序并发。
    2.  **自愈救援工人数上限防御 (Rescue Throttle)**：在 `OrchestratedExecutor` 提交入口增加救援线程的数量校验。若当前已存在的救援线程数已达到 `max(4, self.max_workers // 2)` 门槛，则拦截并拒绝生成新线程，改为在原池退避，从而守住系统的线程和内存底线。

## 📅 2026-06-08: Wikilinks 双链索引增量构建与物理 I/O 短路优化
*   **现象描述**：文库同步结束时执行的双链自愈扫描在海量笔记场景下耗时极长，每次哪怕仅更新单篇文档，也会引发全量文档的重新扫描与正则解析。
*   **根因剖析**：
    1.  **物理大 I/O 阻塞读取**：在 `VaultIndexer.build_indexes` 中，没有对缓存有效性进行前置的短路阻断，导致不管 `mtime` 是否一致，都会强行对每篇文档调用 `source.read_content` 磁盘大 I/O 读取，以及 `LanguageSentinel.detect_language` 重复进行语种探测。
    2.  **账本注册属性被过滤丢弃**：由于元数据管理器（`MetadataManager`）在 `register_document` 的硬编码字典中拦截并过滤掉了 `mtime`, `links`, `detected_lang`, `size`, `tags` 等非表内置字段，导致这部分关系元数据缓存无法持久化进 SQLite 的 `metadata_json` 中，缓存名存实亡。
*   **防线策略与沉淀**：
    1.  **缓存回写与持久化通路**：在 [ledger.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/archives/ledger.py) 中补齐了这 5 个关键的元数据缓存属性，打通其通过 SQLite 账本的读取和写入通路，建立了牢固的双链与语种缓存底座。
    2.  **双链极速增量短路通道**：在 [vault_indexer.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/editorial/vault_indexer.py) 中在磁盘读取前增加缓存存在性判定。只要文件的 `mtime` 未更改，则直接短路读取和语种探测操作，从账本中还原 `links` 和元数据组装成 `link_graph`，避免 90%+ 的重复大 I/O 与 NLP 计算耗时；同时，只在缓存失效时退避回物理读取解析，并在分析完成后自动回写。

## 📅 2026-06-08: 多渠道发行（Syndication）持久化异步重试队列
*   **现象描述**：多平台分发由于网络抖动或第三方 API 限制失败后，分发直接终止且无重试机制，应用重启后也丢失了分发失败的任务，降低了整个同步矩阵的稳定性。
*   **根因剖析**：
    1.  **分发失败零重试**：`ContentSyndicator` 在调用插件分发时，只在 `try-except` 中使用 `tlog.error` 记录日志，任务没有排队，网络波动时分发直接断裂。
    2.  **不可重入锁死锁**：在补充同步状态持久化（`register_syndication`）时，错误地在加锁的方法中嵌套调用了同样使用 `with self.lock:` 互斥锁的 `register_document`。因为 `threading.Lock` 是不可重入锁，这会百分之百触发运行时死锁，使分发线程在重试成功时卡死。
*   **防线策略与沉淀**：
    1.  **SQLite 持久化重试队列**：在数据库引入 `syndication_queue` 实体表。失败任务自动落盘排队，并将重试逻辑提交至全局 `global_executor` 以 `TaskPriority.SYNDICATION` 优先级并发异步调度，并在每次同步分发时自愈式拉起 pending 任务。
    2.  **指数级退避与限额保护**：每次重试失败时累加 `retry_count`，并利用 `(2 ** retry_count) * 10` 秒进行指数退避。达到 `max_retries = 3` 阈值后，自动转为 `FAILED` 并移出重试池，形成工业级容错环。
    3.  **嵌套锁剥离解死锁**：将 `register_syndication` 方法外的 `self.lock` 保护层物理剥离，完全交由内层 `register_document` 专职处理互斥独占写，彻底消除了重入造成的锁挂起隐患。

## 📅 2026-06-09: 翻译校对抽屉内间距、Pre 标签平台差异及 pre-wrap 模板字符串空白溢出治理
*   **现象描述**：在译文校对工作台的抽屉页面中，原文/译文正文段落以及原文描述（Source Description）等内容前后出现大量物理换行与大空白，非常占据页面空间。
*   **根因剖析**：
    1. **多余外边距与内边距累积**：每一个段落块 `.review-para-block` 具有过大的 `padding: 10px 14px`，且原文段落和原文描述具有 `margin-bottom: 12px`，在段落数较多时缝隙巨大。
    2. **Pre 标签浏览器差异**：正文原使用 `<pre>` 承载，虽然重置了 margin，但 `<pre>` 底层仍会受浏览器 User Agent 样式表默认字间距、行高等行内排版预设的潜在干扰，在跨平台呈现时高度不一致。
    3. **ES6 模板字符串的 Pre-wrap 换行与缩进吞噬漏洞（核心教训）**：原文段落、译文段落、以及原文描述容器在样式上均使用了 `white-space: pre-wrap;`。然而在 JS 拼装 HTML 时，将模板字符串写成多行形式（包含为了代码美观而加入的换行符与缩进空格），例如：
       ```javascript
       `<div class="pre-wrap-container">
           ${content}
        </div>`
       ```
       这些包裹在容器内部、用来表示 HTML 层次关系的换行与缩进空格，会被 `pre-wrap` 引擎强制识别为“实际的文本内容换行和空格”，从而在页面上渲染出巨大的多余空白。
*   **防线策略与沉淀**：
    1. **布局紧凑度微调**：将段落块 padding 压缩为 `6px 12px`，原文 `margin-bottom` 减半为 `6px`，收紧排版结构。
    2. **替换容器标签为 Div**：将文本段落的包裹容器统一重构为等效但没有浏览器排版怪癖的 `<div>`，维持 `white-space: pre-wrap; word-break: break-word;` 确保原有格式正确。
    3. **pre-wrap 模板字符串单行防漏规约**：在任何带有 `white-space: pre-wrap` 或 `white-space: pre` 的 CSS 容器中，JS 的模板字符串拼接必须**物理上扁平为单行写死**，严禁在模板字符串的 DOM 标签夹缝中留有任何换行符或缩进空格。例如必须严格写为：
       ```javascript
       `<div class="pre-wrap-container">${content}</div>`
       ```
       通过代码级别的物理单行强制杜绝多余空白渲染。

## 📅 2026-06-11: 本地推理大模型思维链溢出截断、占位符死循环与参数错位路由治理
*   **现象描述**：用户执行 Markdown 原稿的“强制重新发布”翻译时，后台任务挂起或翻译正文显示空，且本地推理服务器（LM Studio / Ollama）资源高负载下，同步任务进度被 ResourceGuard 挂起。
*   **根因剖析**：
    1.  **思维链空间挤占**: 本地推理模型在翻译前输出上千 token 的思考过程，若请求的 `max_tokens` 设置偏低（如 2048）或在 `audit_payload_logic` 审计中拦截 2048，直接导致正文在生成前被物理截断。
    2.  **空白块推理循环**: 仅包含 `__B_MASK_n__` 等无任何有效字母数字的空 Mask 块被发送给 LLM，导致模型陷入自我推理的无限循环，引发死锁或 API 400 Bad Request。
    3.  **计算节点配置错位**: 系统在 `PayloadManager` 中错误地从 `ComputeNode` （仅负责 IP/URL 等网络参数）中读取 `max_tokens` 和 `temperature`，使具体品牌的 `trans_cfg` 策略被完全忽略，回退至全局不适配的默认值。
*   **防线策略与沉淀**：
    1.  **纯 MASK 块直接旁路 (Pure Mask Bypass)**：翻译块内通过正则 `\w` 预检，凡是不含任何字母数字的纯占位符与标点块，直接短路（Bypass）LLM，100% 物理还原占位符文本，防止本地节点思考崩溃。
    2.  **思维链输出大扩容与安全放宽**: 强制为 `is_lmstudio` 等本地推理端请求配置 >=4096 的 `max_tokens`，且动态调整审计拦截线至 4096，保障思维链与译文同时完备吐出。
    3.  **参数策略与节点实体彻底解耦**: 规范化路由机制，禁止直接从 `ComputeNode` 中获取策略参数，一切翻译调用参数必须从 `trans_cfg` 闭环加载。

## 📅 2026-06-11: 译文校对工作台细化“按需生成指定语种译文”参数路由与交互优化
*   **现象描述**：用户在译文校对工作台已存在部分语种译文的情况下，点击“重新生成 AI 译文”按钮会强制重新生成全部目标语种的译文。这不仅造成大量不必要的 LLM 算力 Token 损耗，且在网络波动或本地模型并发处理多语种翻译时大幅增加了等待时间。
*   **根因剖析**：
    1. **参数控制流缺失**：后端路由 `/api/publish/trigger` 接口仅接受 paths 参数而无法接收指定语种列表，多线程并发分发任务时无法传递语种选择，使得同步引擎一律对配置的目标语种进行全量翻译。
    2. **按钮交互粗糙**：前端空状态只有一个全量生成按钮，而在已生成部分语种后，左下角的重新生成也是全局性质，缺少精细化控制。
*   **防线策略与沉淀**：
    1. **全链路语种透传 (Targeted Parameter Routing)**：在 `/api/publish/trigger` -> `start_asynchronous_sync` -> `sync_document` -> `FingerprintSyncStrategy.execute` -> `AIScheduler.dispatch_targets` 全链路上支持 `target_langs` 参数过滤。
    2. **精准调度过滤**：在多语言分发核心算子中对 targets 集合进行匹配过滤，当且仅当传入 `target_langs` 时执行 `[t for t in targets if t.lang_code in target_langs]` 过滤，既保留了单语种按需生成的能力，又向下兼容了原生的全量发布链路。
    3. **前端双态精细交互**：空状态时并排渲染“🚀 仅生成当前语种译文”与“🌍 生成所有目标语种译文”双按钮，已有译文时改写为“🔄 只重新生成当前语种译文”，极大提升用户操作针对性。

## 📅 2026-06-11: 目标语种 Frontmatter 中 SEO 描述与关键词的翻译与对齐治理
*   **现象描述**：目标语种（译文）文档的 Frontmatter 中，`description`（描述）与 `keywords`（关键词）未被翻译，直接保留了源文档（中文）的原始内容。
*   **根因剖析**：
    1. **流向断裂**：AI SEO 处理器在第一阶段生成的各语种 `seo_data` （如 `i18n_seo` 下的 description 与 keywords）没有被反向注入到多语言分发核心算子的 `target_fm` 中，导致两阶段数据脱节。
    2. **缺少兜底机制**：若没有配置或执行 AI SEO 处理器，调度器仅对正文、标题、Tags、Category 进行翻译，没有对 Description 和 Keywords 执行兜底翻译处理，导致它们直接拷贝了中文原稿内容落盘。
*   **防线策略与沉淀**：
    1. **双层防护机制 (Injection + Fallback)**：
       - **优先注入层**：多语言分发算子优先读取 `seo_data.i18n_seo.{lang_code}` 中的 description 与 keywords 并注入 `target_fm`。
       - **翻译兜底层**：在 `is_dry_run=False` 阶段，若 `target_fm` 中对应的字段仍等于源语种中文原值，则主动触发翻译网关 `translate_metadata` 进行物理翻译。
    2. **元数据多类型支持**：针对 `keywords` 的多样性设计了强类型检测，完美支持列表（`list`）和单字符串两种格式。对于列表格式下的每一个关键词分块调用 `translate_metadata` 进行翻译，最后合并回填。
    3. **避免重复翻译**：通过值比对（检测字段是否已被修改），凡是被 AI SEO 成功注入覆盖的字段，会自动绕过翻译兜底，以节约 API 调用开销并加快发布速度。

## 📅 2026-06-11: 多语言分发调度核心与出版模式联动对齐治理
*   **现象描述**：即使品牌配置的出版模式为 `basic`（基础物理出版）或 `enhanced`（智能母语增强），多语言分发核心（`dispatch_ops.py`）在配置有 i18n 目标语言时，仍会尝试通过 AI 翻译管线去调用大模型对其它语种进行内容翻译。这不仅严重违反了“完全无 AI 参与”与“禁用翻译管线”的业务规范，且在无算力挂载时会导致后台大量报错或挂起。
*   **根因剖析**：
    1. **模式判定盲区**：`AISchedulerDispatchOps.dispatch_targets` 只检查了 `engine.i18n.enabled` 等开关，并没有检测或感知全局的 `publishing_mode`，使得非全球分发模式下翻译动作完全失控。
*   **防线策略与沉淀**：
    1. **模式与管线物理联动防线 (Publishing Mode Guard)**：在 `process_target` 开始解析和分配算力任务前，主动引入 `publishing_mode` 的强逻辑预检。若处于 `basic` 或 `enhanced` 模式下，直接物理切断跨语言翻译管线。
    2. **自适应主权透传与拷贝**：在绕过翻译时，自动返回源文档的正文及 Frontmatter 的深拷贝（主权透传），转为物理拷贝分发，确保在维持多语言目录结构物理一致性的同时，不产生任何 AI 调用。

## 📅 2026-06-12: 出版模式自愈降级与段落级缓存续传自愈治理
*   **现象描述**：当关闭多语言翻译矩阵或算力中心/无可用节点时，若未合理设置出版模式，可能引发系统空转调用、测试挂起或 API 状态与磁盘 YAML 数据偏离。此外，段落级翻译缓存断件续传测试在特定 Mock 条件下会因为 `force_sync=True` 的设置冲突，导致无法命中缓存而重复翻译。
*   **根因剖析**：
    1. **缺乏联动校验防御**：在 `Configuration` 校验层未对出版模式与算力节点就绪状态、翻译矩阵启用状态进行联动防御。如果配置处于冲突状态，后端与 API 会产生脑裂。
    2. **API 落盘与内存偏离**：当 API 收到更新配置请求时，虽然触发了检验和默认降级，但降级后的值未能同步回写到磁盘 YAML 与内存的 `engine.config` 实例中。
    3. **缓存强同步短路冲突**：在 `dispatch_ops.py` 中，错误地将 `cached_content = None if force_sync else ...` 设置为在 `force_sync` 为 True 时完全绕过段落翻译块缓存。这导致在测试（或日常强制同步）中，即使本意只是强制写出文件、但期待命中已缓存的段落翻译时，依然重复发起了 AI 翻译，使得断点续传缓存统计失败。
*   **防线策略与沉淀**：
    1. **后置模型联动校验 (Post-model Validator)**：在 `Configuration` 中新增 `@model_validator(mode='after')` 统一校验：
       - 当多语言开关关闭且出版模式为全球 `global` 时，自愈降级为增强 `enhanced`，并自动将 SEO 策略对准为 `ai_alignment`；
       - 当 AI 算力未就绪（`enable_ai=False` 或无任何启用节点、无有效 `api_key`）时，强制将出版模式降级为 `basic`，SEO 策略对准为 `heuristic`。
    2. **API 状态自愈与持久化回写**：在 `/api/config/update` 中对更新后的 config 执行全量验证。一旦发生校验降级，自愈机制会自动将更改的值反向更新到持久化字典并写回 YAML 文件及内存，保持完全一致性。
    3. **强制发布与段落级缓存解耦**：将 `force_sync` 仅限定在“文档级/文件级”是否重新同步落盘，而允许段落块级别继续在 `dispatch_ops.py` 中完美匹配并读取 `block_cache` 以免造成 LLM 算力浪费和测试失败。

## 📅 2026-09-05: Sovereign 原生主题独立单页导航基准路径漂移修复与 DevServer 递归 302 防卫
*   **现象描述**：访问 Sovereign 主题下的独立单页（如“关于我们” `about.md`，槽位 `pages`）时，顶部导航栏的“关于我们”链接错误生成为 `./about/index.html`。当创作者点击后，浏览器进入虚拟目录 `/about/index.html`，导致浏览器的 Base URI 被下移一级到 `/about/`，使得页面内所有相对超链接（如 `./docs/quick-start.html`、`./about.html`）全部偏移，引发正文内链 404，且连续点击关于我们时陷入 `/about/about/about/...` 的无限递归套娃死循环。
*   **根因剖析**：
    1. **SSG 导航合成器槽位判断盲区**：`core/adapters/egress/ssg/base_shards/ssg_nav_synthesizer.py` 在非 clean-url 模式下将所有未带扩展名的项统一推导为目录路径（`target_path = f"/{prefix}/"`），未能识别独立单页（`pages` 槽位）不需要带尾斜杠。
    2. **模版相对链接盲目拼装 index.html**：`themes/sovereign/adapters/sovereign_helpers.py` 的 `apply_template` 在组装顶部主导航相对路径时，未排除单页槽位，直接将带有尾随斜杠的单页按频道规则拼接为 `{root_path}{nav_lang_prefix}{u_clean}/index.html`。
    3. **本地开发预览服务静默映射缺陷**：`core/utils/dev_server.py` 的 `SovereignHandler.translate_path` 对不存在的虚拟路径 `/about/index.html` 采用静默 200 返回根目录 `about.html` 内容，导致浏览器地址栏未同步纠偏，使得相对路径基准继续错位。
*   **防线策略与沉淀**：
    1. **SSGNavSynthesizer 单页排他规范**：显式增加 `is_standalone_page = (slot in ("pages", "page") or prefix in ("about", "terms", "privacy", "disclaimer", "contact"))` 判断，强制输出 `/{prefix}.html`（如 `/about.html`）。
    2. **SovereignHelpers 模版相对路径对齐**：在 `apply_template` 识别单页槽位，强制生成 `{root_path}{nav_lang_prefix}{u_slug}.html`（根目录直接输出 `<a href="./about.html" class="active">`），杜绝输出伪目录 `/index.html`，彻底稳定浏览器 Base URI。
    3. **SovereignHandler 302 客户端协议纠偏防卫**：在 `core/utils/dev_server.py` 中实现 `do_GET` 拦截器：
       - 正则折叠连续重复的套娃路径（如 `/about/about/...`），发送 HTTP 302 重定向；
       - 请求虚拟子目录索引（如 `/about/index.html`）且物理磁盘不存在该目录、但父级存在实体单页 `about.html` 时，发送 HTTP 302 重定向至规范单页地址 `about.html`，从网络层强制矫正浏览器 Base URI。
    4. **防御性类型解包加固**：遵循 Rule 8，在 `sovereign_helpers.py` 中对 `adapter.get_custom_options()` 及 `footer_copyright` 进行防御性类型转换，防止非字典或 MagicMock 对象引发 `TypeError`。

## 📅 2026-09-09: 全域发布推送统计与访问看板打通 (Sovereign Deployment Summary Hub)
*   **现象描述**：全域发布（分发）流程执行完毕后，控制台仅输出冗长的日志流与基础的 `同步流水线执行完毕` 文本提示。创作者无法直观知晓本次同步了哪些渠道、各渠道成功/失败状态，更无法直接获取或点击线上已上线的真实访问网址，导致发布后的“最后一公里”体验割裂。
*   **根因剖析**：
    1. **分发结果未结构化汇总**：`core/bindery/deployment_manager.py` 在推送完成后仅返回原始布尔值字典，未根据各 Publisher 凭证与品牌配置推导并组织各渠道的线上公网访问 URL。
    2. **前端终端缺乏成果卡片交互**：`web/dashboard/js/core/core.terminal.js` 中虽然有日志输出，但未对 URL 进行自动超链接解析，且弹窗 Footer 在发布完成后仅有置灰的关闭按钮，未点亮核心访问行动点。
*   **防线策略与沉淀**：
    1. **全域推送智能汇总与 URL 推导 (Deployment Summary Builder)**：
       - 在 `deployment_manager.py` 的 `deploy_all()` 结尾组装结构化 `summary` 载荷（包含成功/失败渠道计数、各渠道线上 URL、官方主站标识与错误原因）；
       - 智能推导官方主站与镜像 URL（如 GitHub Pages `https://{owner}.github.io/{repo}/`、Vercel `https://{project}.vercel.app/` 等）；
       - 通过事件总线广播 `DEPLOY_SUMMARY` 并在 ASCII 终端日志中输出对齐看板。
    2. **状态驻留与治理 API (`GET /api/governance/deployment-summary`)**：
       - 在 `core/services/post_sync.py` 与引擎中驻留 `last_deployment_results`，并在治理路由提供专用调阅接口，防止长连接丢失或刷新后数据丢失。
    3. **前端高质感成果看板与主站高光行动点 (`renderDeploymentSummaryCard`)**：
       - `core.terminal.js` 自动将日志流中的所有公网 URL 转为带安全属性 (`target="_blank" rel="noopener noreferrer"`) 的高亮点击链接；
       - 弹窗输出流末尾渲染「🎉 全域发布圆满完成 · 站点已上线」毛玻璃看板，区分「🏠 官方主站」与「🔄 容灾镜像」，提供各渠道专属「打开浏览 ↗」按钮及「📋 复制全部链接」功能；
       - 弹窗底部操作栏点亮翡翠绿色核心 CTA 按钮「🌐 立即访问线上主站 ↗」，点击直达官方主站。

