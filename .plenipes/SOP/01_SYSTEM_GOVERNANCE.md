# SOP-01: 品牌主权与系统治理 (Imprint & Governance)

本准则定义了 Illacme Plenipes 引擎的物理边界、受保护资产与品牌身份。

## 1. 系统身份与隐喻 (Core Identity)
- **定位**：“全球私人出版社 (Global Private Press)”。
- **副标题**：“您的全球出版发行指挥中心 (Your Global Publishing & Distribution Command Center)”。
- **UI 核心隐喻**：Dashboard 必须作为“指挥中心”进行迭代，每一个交互都应具备“指挥”与“掌控”的即时感。
- **出版版图 (Publishing Map)**：指代系统中所有 **Imprint (品牌)** 的集合，代表了出版社的全球疆域。

## 2. 核心术语与流程映射 (Terminology)
为了确保 AI 助理与指挥官的语义高度对齐，强制执行以下术语体系：

### A. 创作阶段 (Ideation & Drafting)
- **The Scriptorium (创作中心)**：指代 AI 创作入口，由指挥官下达指令，AI 负责起草、润色并将想法固化为原稿。

### B. 出版阶段 (Content Production)
- **Manuscript Vault (原稿文库)**：指代源 Markdown 库或内容资产，是系统主权的根基。
- **The Galley (排版文库)**：指代 SSG 内部的原始文档目录（src），是稿件进入装帧前加工、校样的“工作室”。
- **Compute (算力中心)**：负责“出版”的核心能力，涵盖内容生成、AI 翻译流水线及 **装帧 (SSG) 渲染**。
- **The Publication (出版成品)**：算力中心产出的静态产物 (Dist)，是发行的物理对象。

### C. 发行阶段 (Global Distribution)
- **The Matrix (发行矩阵)**：全球多平台、多语种的自动化部署网络基座。
- **The Dispatch (发行调度)**：将“出版成品”推向矩阵的瞬时动作，由指挥中心统一调配。
- **The Channels (发行渠道)**：具体的触达终端（如 GitHub, Netlify, Social Media 等）。

### D. 统筹与主权 (Sovereignty)
- **Command Center (指挥中心)**：即 Dashboard，统筹“出版”与“发行”双重操作的物理载体。
- **Imprint (品牌)**：指代**独立出版项目**。它是系统逻辑运行与资源隔离的最高物理边界，是划定“出版版图”的最小主权单元。
    - *理解要点*：增加一个 Imprint 即代表“扩大出版疆域”。

## 3. 术语主权红线 (Terminological Redlines)
- **硬性禁令**：
    - 严禁使用旧称 *Omni-Hub*。
    - **严禁使用英文单词 `Brand` 或 `Branding`**。技术层必须统一使用 `Imprint` 或 `Imprinting`。
    - **严禁使用中文单词“印记”**。UI 与对话层必须统一使用 **“品牌”**。
- **映射契约**：
    - **英文/技术域**：`Imprint` 优先。
    - **中文/用户域**：**“品牌”** 优先。

## 4. 物理资产与安全锁定
- **Banner 锁定**：`core/ui/handlers/status_handlers.py` 的 ASCII 视觉资产严禁 AI 擅自修改。
- **端口锁定**：43210-43213 端口物理锁定，严禁改动以避让冲突。
- **配置分层**：严格遵守 `config.local.yaml` > `config.yaml` 的主权优先级。

## 5. 工程诚信 (Engineering Integrity)
- **语法敬畏**：严禁破坏 YAML Frontmatter 结构与组件标签（如 `<Card>`, `<Tabs>`）。
- **黑盒豁免**：严禁在文本清洗操作中处理 `[[STB_MASK_n]]` 类占位符。

---
*更新日期：2026-05-12*
*执行负责人：Antigravity (AI)*
*优先级：最高 (01)*
