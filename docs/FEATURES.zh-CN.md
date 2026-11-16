# 🌟 Illacme Plenipes 核心特性宪章 (Core Features Charter)

本文件定义了 **Illacme Plenipes · 出版发行工作台** 的核心功能目标与设计哲学，是所有架构演进与功能迭代的最高准则。

---

## 🚀 十二项核心能力

### 1. 本土创作，全球传播
创作者只需在 **原稿文库 (Vault)** 中维护单一本土语言 Markdown 文档，引擎全自动完成多语种衍生、全媒介封包与全球化分发。

### 2. 极致的 Markdown 与 Obsidian 兼容性
不限制文库方言，原生兼容标准 Markdown、LaTeX 数学公式、Callout 语法以及 Obsidian/Logseq `[[双链]]` 语法。

### 3. 全链路 AI 算力适配与段落缓存
支持 OpenAI、Gemini、Claude、DeepSeek 等云端大模型以及 Ollama / LM Studio 本地离线模型，配合段落级指纹缓存（Block Cache）降低重复翻译成本。

### 4. 语义化多语翻译与人工校对锁
通过大模型分片/分段翻译维持长文上下文一致，并提供人工校对锁定表（`translation_reviews`），保护创作者精修译文不被后续全站构建覆盖。

### 5. 多主题静态站装帧与一键托管
支持 Sovereign、Universal、Docusaurus、Starlight、Nextra、VitePress 等多种装帧主题，并一键部署至 GitHub Pages、Cloudflare Pages、Vercel、Netlify 等托管平台。

### 6. 多语数字装订与品牌隔离书架
内嵌 **BookAssembler** 装订中枢，支持一键导出多语平行对照 **WebBook**、**EPUB 3**、**印刷级 PDF** 与 **可编辑公式 DOCX**，并按出版品牌物理隔离输出目录。

### 7. 双人伴读播客与 RSS 2.0 发行
内置双人对话剧本提炼、TTS 合成与 BGM 自适应闪避混音引擎，自动生成章节时间轴、`podcast-feed.xml` 与网页/电子书内嵌播放器，支持 R2 / S3 / OSS / COS CDN 转储。

### 8. 多画幅封面工坊与视觉资产图库
内置 **Cover Studio** 与 `ImageHub`，支持 `16:9`、`2.35:1`（微信首图）、`3:4`（小红书）、`1:1` 安全区自适应预览，并按品牌隔离封面缓存。

### 9. 30+ 社媒矩阵同步与死信自愈
自动完成跨平台排版清洗、外链转脚注与图片转存，提供可追踪的分发账本与死信队列重试/AI 诊断机制。

### 10. 3D 知识星谱与拓扑联动
自动构建文档实体、摘要与双链关系图谱，原稿创建、移动或销毁时实时同步图谱节点与入边引用。

### 11. 多品牌主权治理 (Multi-Imprint)
支持在单一工作台中并行管理多个独立 **出版品牌 (Imprint)**，各自隔离文库路径、装帧主题、语种矩阵、书架与封面资产。

### 12. 出版主编智能体与开放 MCP 协议
内置 **Sovereign Copilot**（14 项出版自治工具、持久化多轮记忆、HITL 审批与写前快照回滚），并通过 `/api/agent/mcp/rpc` 暴露完整 MCP（`Tools` / `Resources` / `Prompts`）能力。

---

> [!IMPORTANT]
> **设计哲学：让创作者回归创作本身。**
> 任何功能迭代如果增加了创作者的操作负担，或破坏了 Markdown 与本地数据的开放主权，均应被视为违背本宪章。
