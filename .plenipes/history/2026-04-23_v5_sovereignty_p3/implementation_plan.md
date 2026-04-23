# 契约化主权与逻辑隔离架构演进 (Contractual Sovereignty & Logic Isolation)

本方案旨在通过“物理隔离”业务逻辑与协议适配，建立一套永不退化的工业级 AI 适配器框架。

## User Review Required

> [!IMPORTANT]
> **架构断裂式重构**：我将把所有适配器（OpenAI, Gemini 等）的 `translate` / `slug` 逻辑收回到基类。未来任何适配器只需实现一个 `_ask_ai` 原子方法。
> **审计红线升级**：如果我在未来任何一次编辑中尝试在子类中重载（Override）这些受保护的方法，审计将直接 **RED (FAIL)**。

## Proposed Changes

### 1. 基类契约化 (Base Contractualization)

#### [MODIFY] [ai_base.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/adapters/ai_base.py)
- 引入 `abc.ABC` 和 `@abstractmethod`。
- **逻辑下沉**：将 `translate` / `generate_slug` / `generate_seo_metadata` 的具体实现（Prompt 组装、JSON 解析、数据清洗）全部移入 `BaseTranslator`。
- **定义原子协议**：`@abstractmethod def _ask_ai(self, system_prompt, user_content) -> str`。

### 2. 适配器脱壳 (Adapter Decoupling)

#### [MODIFY] [ai_openai.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/adapters/ai_openai.py)
- 移除 `OpenAICompatibleTranslator` 中所有业务方法。
- 实现纯净的 `_ask_ai`（仅处理 OpenAI HTTP 请求）。
- `DeepSeekR1Translator` 仅重写 `_ask_ai` 以处理流式推理。

#### [MODIFY] [ai_specialized.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/adapters/ai_specialized.py)
- 同步重构为纯净协议适配器模式。

### 3. 治理审计升级 (Governance Upgrade)

#### [MODIFY] [code_checks.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/tests/audit_lib/code_checks.py)
- **[NEW] `check_logic_shadowing`**：使用 AST 检查所有子类。如果发现子类定义了基类中已有的逻辑方法（如 `generate_slug`），则判定为“越权篡改”并报错。
- **[NEW] `check_protocol_completeness`**：强制检查是否实现了 `_ask_ai`。

#### [MODIFY] [rules.md](file:///Volumes/Notebook/omni-hub/illacme-plenipes/.plenipes/rules.md)
- **[Rule 12.9] 逻辑主权隔离协议**：明确定义逻辑层与协议层的物理界限。

## Verification Plan

### Automated Tests
- `python3 tests/governance_audit.py`：验证逻辑隔离审计通过。
- `python3 tests/autonomous_simulation.py`：验证 AI 功能在重构后依然全量可用。
 
