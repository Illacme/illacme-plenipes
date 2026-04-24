# SSG 适配器架构与 SEO 注入协议

## 1. 设计目标
本架构旨在解决不同静态网站生成器 (SSG) 之间元数据结构、语义块语法和 SEO 规范的不一致问题。通过引入适配器层，引擎核心保持“框架中立 (Framework Agnostic)”，确保了极强的可扩展性。

---

## 2. 核心接口规约 (Adapter Protocol)

### 2.1 元数据适配 (`adapt_metadata`)
*   **职责**：将通用的文档元数据（日期、作者）转换为框架特定的字段。
*   **示例**：Docusaurus 使用 `last_update: {date: ...}`，而 Starlight 可能使用 `lastUpdated: ...`。

### 2.2 SEO 注入 (`inject_seo`)
*   **职责**：定义 AI 生成的 SEO 描述和关键词如何进入 Frontmatter。
*   **逻辑**：
    *   **Docusaurus**: 直接注入顶层 `description` 和 `keywords`。
    *   **Starlight/Astro**: 优先保证 `description` 的准确性，并根据主题配置映射 `keywords`。
    *   **Next.js (Metadata API)**: 可选支持将数据封装在 `metadata` 对象内。

---

## 3. 渲染适配 (Block Rendering)

### 3.1 Callout/Admonition 转换
适配器负责将通用的 Callout 类型转换为目标框架的语法：
*   **Docusaurus**: `:::tip{Title}`
*   **Starlight**: `:::tip [Title]`

---

## 4. 扩展指南
新增 SSG 支持只需以下三步：
1.  在 `core/adapters/egress/ssg/` 下新建 `{framework}.py`。
2.  继承 `BaseSSGAdapter` 并实现相关接口。
3.  在 `registry.py` 中注册该适配器标识。

---
*文档签署人：Antigravity AI*
*签署日期：2026-04-23*
