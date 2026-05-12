# SOP-01: 系统主权与物理治理 (Sovereignty & Governance)

本准则定义了 Illacme Plenipes 引擎的物理边界、受保护资产与品牌身份。

## 1. 品牌主权 (Brand Sovereignty)
系统已进化为“全球私人出版社”体系。在任何日志、注释或 UI 中必须使用出版术语：
- **Manuscripts (原稿)**：指代源 Markdown 库。
- **The Archive (档案库)**：指代数据存储根目录。
- **The Press (印刷机)**：指代 SSG 渲染引擎及源码。
- **The Bookstore (书店)**：指代最终发布的产物目录。
- **禁忌**：严禁使用旧称 *Omni-Hub*。

## 2. 物理资产与端口锁定
- **Banner 锁定**：`core/ui/handlers/status_handlers.py` 视觉资产严禁修改。
- **端口锁定**：43210-43213 端口物理锁定。

## 3. 语法敬畏 (Syntax Integrity)
- **YAML 守卫**：严禁破坏 Frontmatter 的 YAML 缩进与类型。
- **组件隔离**：处理包含 `<Card>`, `<Tabs>` 的 MDX/JSX 文件时，严禁误伤大括号 `{}` 和标签闭合。
- **黑盒豁免**：严禁在任何文本清洗操作中处理 `[[STB_MASK_n]]` 类占位符。

## 4. 配置分层 (Local > Imprint > Base)
必须严格遵守 `config.local.yaml` 的最高优先级。

---
*优先级：高 (01)*
