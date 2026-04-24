# AI 算力节点适配与自愈策略

## 1. 概述
Illacme-plenipes 的 AI 适配层旨在屏蔽不同算力供应商（DeepSeek, Gemini, LM Studio, Ollama）的接口差异，并在不稳定的网络或资源环境下提供工业级的容错能力。

---

## 2. 连通性工程 (Connectivity Engineering)

### 2.1 本地回环优化
*   **规约**：在连接 LM Studio 或 Ollama 等本地实例时，**禁止使用 `localhost`**，必须显式指定 `127.0.0.1`。
*   **原理**：规避 Python `requests` 库在某些 OS 环境下的 DNS 解析延迟，并防止错误的代理流量注入。

### 2.2 终结点智能修正 (Endpoint Normalization)
*   适配器会自动检测 `base_url` 完整性。若检测到 OpenAI 兼容接口缺失 `/chat/completions` 或 `/completions` 后缀，引擎将执行物理补全，确保请求始终命中正确的 REST API。

---

## 3. 容错与自愈 (Resilience & Self-healing)

### 3.1 级联超时继承 (Timeout Hierarchy)
为了应对本地模型加载或大规模并发导致的 Read Timeout，系统采用三层超时保护机制：
1.  **节点级超时**：在 `ai_providers.yaml` 中为特定算力节点定义。
2.  **全局超时**：在 `config.yaml` 的 `translation` 模块中统一定义。
3.  **熔断默认值**：当上述均缺失时，强制执行 60s 工业级熔断。

### 3.2 节点切换策略 (Fallback)
*   **触发条件**：当主算力节点（Primary Node）发生 `Connection Error`, `Rate Limit (429)` 或 `Read Timeout` 时。
*   **行为**：系统将自动切换至备用节点（Fallback Node）。若主节点为本地模型，建议备用节点指向稳定云端（如 DeepSeek）。

---

## 4. 最佳实践：本地实测配置建议
在本地开发调试阶段，为了保证稳定性，建议执行以下配置：
*   `llm_concurrency: 1` (防止显存溢出)
*   `api_timeout: 300.0` (应对大模型首字延迟)
*   `max_retries: 0` (方便第一时间捕获错误堆栈)

---
*文档签署人：Antigravity AI*
*签署日期：2026-04-23*
