# 📝 Illacme-plenipes：面向 Markdown 创作者的极致灵活性指南

对于 Markdown 用户而言，Illacme-plenipes 不仅仅是一个同步工具，它是一个**具备语义感知能力的内容进化引擎**。以下从四个维度深度解析本项目的灵活性：

---

## 1. 语义化原子同步 (Semantic Atomicity)
**“只翻译你修改的那段话”**

传统的同步工具通常是“全量替换”，这在 AI 翻译场景下会导致大量 Token 浪费，甚至因 AI 响应的不确定性导致未修改部分的格式发生微小偏移。
- **Delta Block Engine**：引擎通过 `MarkdownBlockParser` 将你的文件拆解为段落、代码块、引用块、列表等独立单元。
- **指纹级缓存**：只有当你真正修改了某个块的内容时，引擎才会请求 AI 进行翻译。这意味着你可以放心地进行“微调”，而不用担心影响全文。

## 2. 复杂容器的深度兼容 (Rich Container Support)
**“保护你的 Docusaurus / Starlight 魔法”**

Markdown 的力量在于其扩展。Illacme-plenipes 针对现代 SSG（静态网站生成器）进行了专项优化：
- **容器感知**：支持 `:::tip` / `:::info` 等自定义容器（Custom Containers）以及 `> [!NOTE]` 等 Callouts。引擎会自动识别这些容器的边界，翻译内部文本，同时**绝对保证**外部容器标记的物理结构不被破坏。
- **代码块禁区**：所有 ``` 代码块都会被自动标记为“禁区”，引擎会提取其中的语言标签并保护代码逻辑，防止 AI 误伤代码缩进或语法。

## 3. 元数据的主权掌控 (Metadata & Frontmatter)
**“SEO 自动化，但不失控”**

Frontmatter 是 Markdown 的灵魂，我们给予了用户最高的配置权限：
- **深度元数据对齐**：标题、标签、分类等元数据可以随正文同步翻译，且支持“空值保护”——如果 AI 翻译失败，会保留原值以防止页面 Meta 信息丢失。
- **Slug 自动进化**：支持基于标题自动生成 SEO 友好的 Slug。如果你对 AI 生成的 Slug 不满意，可以直接手动指定，引擎会优先尊重用户的物理输入。

## 4. 多端适配的路由矩阵 (Routing Matrix)
**“一套内容，全域分发”**

你的 Markdown 文件不必被束缚在单一的目录结构中：
- **路径重映射**：通过 `config.yaml` 中的 `route_matrix`，你可以灵活定义 Ingress（入站）与 Egress（出站）的对应关系。
- **多 SSG 适配**：支持针对 Docusaurus、Starlight 等不同框架的路径习惯。例如，同一份文档可以同步为 Docusaurus 的侧边栏结构，也可以同步为 Starlight 的扁平路由。

## 5. 极致透明的 AI 协作 (Transparent AI Logic)
**“你才是主编，AI 是助理”**
- **自定义 Prompts**：你可以针对翻译、SEO 提取、Slug 生成等不同环节自定义系统提示词，精准控制 AI 的语气和风格。
- **无推理模式 (No-Reasoning)**：引擎强制过滤 AI 的思维链（如 `<think>` 标签），确保产物纯净，直接可用，无需人工二次清洗。

---

> [!TIP]
> **灵活性核心哲学**：Illacme-plenipes 的目标是让创作者**专注写作**。你只需要在本地用你最喜欢的编辑器（Obsidian, VS Code 等）写好一份中文 Markdown，剩下的多语言分发、SEO 优化、路径转换，全部交给引擎自动完成。
