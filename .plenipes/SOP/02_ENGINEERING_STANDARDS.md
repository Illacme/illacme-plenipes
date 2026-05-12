# SOP-02: 工程研发与质量标准 (Engineering Standards)

本准则定义了代码开发过程中的技术契约。

## 1. 物理写保护 (Writing Protection)
- **禁止盲写**：除非新建文件，否则严禁在未读取既有文件内容的情况下进行全量覆盖。必须先 `view_file` 确认后再修改。
- **最小侵入**：优先使用 `replace_file_content` 执行原子化修改，严禁不必要的全文件重写。

## 2. 配置与元数据契约
- **YAML 类型保护**：在 `config.yaml` 中修改版本号或 ID 时，必须显式加双引号 `" "`，防止解析器将其识别为 float 或 int。
- **插件元数据**：适配器类必须包含 `PLUGIN_ID`, `DISPLAY_NAME`, `DESCRIPTION`。

## 3. 架构隔离
- **逻辑影子拦截 (Logic Shadowing)**：子类适配器仅允许实现 `_ask_ai` 等原子接口，严禁重写基类（BaseTranslator）的业务流程方法。

## 4. 仿真验证 (Simulation Gating)
- **零回归保证**：修改 Egress 逻辑前必须执行物理仿真。

---
*优先级：中 (02)*
