# 大模型参数兼容性与算力载荷清洗规约 (LLM Parameter Compatibility Protocols)

## 1. 背景与防线设计宗旨
在混合算力架构中，各类云端和本地大模型（如 OpenAI 官方 `o1`/`o3-mini`、DeepSeek-R1 系列、LM Studio 自建端、SiliconFlow 等第三方托管）由于协议实现细节不同，其对入参存在许多非标和强制排他约束。
若不对入参请求进行统一拦截、智能对准与剔除，部分平台将直接抛出 **HTTP 400 Bad Request** 错误。

为了在产品层面做到各层级无缝兼容，本项目特设立以 `PayloadManager.align_and_clean_payload` 为中枢的 **终极参数洗涤网关 (Ultimate Parameter Alignment Gateway)**，在同步对话 (`openai.py`) 和流式评估 (`tool_runner.py`) 两个原子级调用入口强制闭环拦截。

---

## 2. 各类大模型参数特征调研矩阵

| 大模型/托管平台 | reasoning_effort 支持情况 | temperature 约束 | max_tokens 与 max_completion_tokens | system 角色支持情况 |
| :--- | :--- | :--- | :--- | :--- |
| **OpenAI o1 / o3-mini** | 支持 `"low"`, `"medium"`, `"high"` | ❌ 不支持 (强制只能为 `1.0` 或不传，传其他值报 400) | ❌ 废弃 `max_tokens`，必须使用 `max_completion_tokens` | 较新模型支持 `developer` 角色；老版本（如 `o1-mini`）完全不支持 system 消息，必须降级为 `user` 角色 |
| **LM Studio (本地推理)** | 仅支持 `"none"`, `"minimal"`, `"low"`, `"medium"`, `"high"`, `"xhigh"`。传入 `"on"`/`"off"` 会直接报 400 Client Error。开启时自动规整为用户分档值或 `"medium"`，关闭时自动规整为 `"none"`。 | ✅ 正常支持 | ❌ 不支持 `max_completion_tokens`，必须使用 `max_tokens` | ✅ 正常支持 |
| **SiliconFlow (硅基流动)** | ❌ 不支持，思维链使用 `thinking_budget` (整数) | ✅ 正常支持 | ❌ 不支持 `max_completion_tokens` | ✅ 正常支持 |
| **Together AI / OpenRouter** | 仅支持特殊包装：`"reasoning": {"enabled": bool, "effort": str}` | ✅ 正常支持 | ❌ 不支持 `max_completion_tokens`，必须使用 `max_tokens` | ✅ 正常支持 |
| **Ollama** | ❌ 不支持，思维链使用 `"think"` / `"thinking"` (布尔值) | ✅ 正常支持 | ❌ 不支持 `max_completion_tokens`，必须使用 `max_tokens` | ✅ 正常支持 |
| **其他通用模型 (如 GPT-4o, Claude 等)** | ❌ 不支持任何推理相关参数，传入直接报错 400 | ✅ 正常支持 | ❌ 不支持 `max_completion_tokens`，必须使用 `max_tokens` | ✅ 正常支持 |

---

## 3. 本项目全层级物理兼容与降级策略

### 3.1 核心洗涤拦截算法 (`align_and_clean_payload`)
该算法集中集成在 `core/adapters/ai/payload_manager.py` 中，执行五大层级的过滤与自动纠正：

1. **OpenAI 推理大模型精细清洗**：
   - 当检测到模型为 OpenAI `o1`/`o3` 系列时，自动物理删除 `temperature` 参数。
   - 自动将 `max_tokens` 参数重命名为 `max_completion_tokens`。
   - 针对 `o1-mini` / `o1-preview` 早期模型，自动将 `system` 角色消息安全改写为 `user` 角色消息以防报错；对较新模型改写为 `developer` 角色消息。
   
2. **常规大模型向下兼容映射**：
   - 自动将 `max_completion_tokens` 安全回退并重命名为 `max_tokens`，防止非推理模型或第三方兼容网关报错 `400`。
   
3. **推理思维链参数精准对准**：
   - 统一清洗并剥离所有非标思维链参数（如 `enable_thinking`, `think`, `thinking_budget`, `reasoning_effort` 等）。
   - **LM Studio 节点**：将 `reasoning_effort` 对正为 `"on"` 或 `"off"`，并同步注入 `enable_thinking`、`think` 和 `thinking_budget` 以支持 Qwen 本地思考。
   - **SiliconFlow 节点**：仅注入 `thinking_budget`。
   - **Ollama 节点**：仅注入 `think` 和 `thinking`。
   - **OpenRouter/Together 节点**：重组为特殊嵌套结构。
   - **通用非官方推理节点**：在检测到推理名（如 `r1`）时，只注入 `think`/`thinking_budget`，拒绝盲目注入 `reasoning_effort`。

---

## 4. 后续演进与硬性工程红线

> [!IMPORTANT]
> **开发硬性工程红线**：
> 1. **严禁在调用 LLM 时手动拼装 `reasoning_effort` 或 `max_completion_tokens` 等参数**。所有请求载荷必须统一调用 `PayloadManager.align_and_clean_payload` 进行洗涤过滤。
> 2. 新增或修改任何大模型算力通道（如新接入 Claude-3.7 等），必须将参数特性优先登记在清洗网关中，确保入参在发送给底层物理网关前完成彻底的安全脱毒与规格兼容。
