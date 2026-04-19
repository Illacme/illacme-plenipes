# Implementation Plan - SSG 全路径兼容性增强 (Universal Egress)

本计划旨在通过增强 Egress 适配器和静态化引擎，使 Illacme-plenipes 引擎能够 100% 覆盖市面上所有主流（Astro, Docusaurus）及传统/非标（Hugo, Hexo, Nextra）SSG 框架。

## User Review Required

> [!IMPORTANT]
> - **配置项扩展**：我将在 `config.yaml` 的 `theme_options` 节点下增加 `metadata_format` 和 `shortcode_mappings` 节点。这不会破坏现有配置，但会提供更细粒度的控制。
> - **静态化性能**：引入“深度递归扁平化”算法。对于包含极深度嵌套组件（如 3 层以上 Tabs 嵌套）的文章，同步时间可能会略微增加（毫秒级同步变动）。

---

## Proposed Changes

### [逻辑增强 - Egress 适配层]

#### [MODIFY] [egress.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/adapters/egress.py)
- **Metadata Format**: 在 `adapt_metadata` 方法中引入日期格式化逻辑，支持 `strftime` 风格的占位符。
- **Custom Shortcodes**: 新增 `convert_shortcodes` 方法，根据配置中的正则字典执行二次翻译。
- **Strict Keys**: 支持将 metadata 中的 `true/false` 强制转化为目标框架要求的 `1/0` 或字符串。

### [架构升级 - 静态化管线]

#### [MODIFY] [staticizer.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/pipeline/staticizer.py)
- **Recursive Flattening**: 实现 `_process_nested_recursive` 逻辑，处理组件嵌套问题。
- **Enhanced Dataview**: 优化 Dataview 拦截器，支持通过 YAML 配置开启“源码预览模式”或“强制脱敏模式”。

### [配置更新 - 范例同步]

#### [MODIFY] [config.example.yaml](file:///Volumes/Notebook/omni-hub/illacme-plenipes/config.example.yaml)
- **Hugo/Hexo 专业模板**: 增加 `hugo_preset` 与 `hexo_preset` 的全量配置示例，包含专属的时间格式与 Frontmatter 映射。

---

## 验证计划

### 自动化测试
- 编写 Mock 任务，验证日期 `2026-04-19` 是否能根据配置正确输出为 `2026-04-19T10:00:00+08:00`。
- 构造嵌套组件字符串，验证其在一次逻辑扫描中是否能被全部解构。

### 手动核验
- 您可以尝试切换到一个对格式极其敏感的框架（如 Hugo），确认同步过程不再报 `Frontmatter Parsing Error`。
