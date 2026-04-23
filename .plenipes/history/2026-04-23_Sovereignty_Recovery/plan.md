# 架构主权复苏与核心逻辑加固 (Sovereignty Recovery & Logic Hardening)

由于之前的过度修剪，导致 `Translator` 的核心方法丢失，且配置项未全量暴露。本计划旨在找回丢失逻辑，并建立“物理级”的逻辑防线。

## User Review Required

> [!IMPORTANT]
> **逻辑防线建立**：我将引入 `Mandatory Method Guard`。如果未来任何一次编辑导致 `BaseTranslator` 或其子类缺失 `translate`、`generate_slug`、`generate_seo_metadata` 之一，治理审计将直接 **RED (Fail)** 并强行中断。

## Proposed Changes

### 1. 逻辑复健 (Core Logic Recovery)

#### [MODIFY] [ai_base.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/adapters/ai_base.py)
- 在 `BaseTranslator` 中重新定义 `generate_slug` 和 `generate_seo_metadata` 的基类存根。

#### [MODIFY] [ai_openai.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/adapters/ai_openai.py)
- 物理找回并实现 `generate_slug` 与 `generate_seo_metadata`。
- 将 System Prompt 改为从 `trans_cfg.custom_prompts` 中读取，支持动态覆盖。

### 2. 配置主权扩容 (Config Expansion)

#### [MODIFY] [configs/ai_providers.yaml](file:///Volumes/Notebook/omni-hub/illacme-plenipes/configs/ai_providers.yaml)
- 为每个节点增加 `proxy` 配置项示例。

#### [MODIFY] [config.yaml](file:///Volumes/Notebook/omni-hub/illacme-plenipes/config.yaml)
- 增加 `translation: custom_prompts` 节点。
- 增加 `translation: global_proxy` 节点。
- 增加 `system: watchdog_settings` 与 `ai_context_purification: strip_jsx_tags`。

### 3. 治理引擎加固 (Governance Hardening)

#### [MODIFY] [code_checks.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/tests/audit_lib/code_checks.py)
- **[NEW] `check_mandatory_logic`**：使用 `ast` 静态分析 `core/adapters/` 目录。
- 强制要求所有 `BaseTranslator` 的实现类必须具备完整的 3 个核心方法。

#### [MODIFY] [rules.md](file:///Volumes/Notebook/omni-hub/illacme-plenipes/.plenipes/rules.md)
- **[NEW] [Rule 12.8] 核心函数主权防护**：严禁在未迁移逻辑的前提下删除核心类方法。

## Verification Plan

### Automated Tests
- 运行 `python3 tests/governance_audit.py`：确保新增的 `Mandatory Method Guard` 通过。
- 运行 `python3 tests/autonomous_simulation.py`：验证 AI Slug 生成逻辑是否恢复正常。

### Manual Verification
- 检查 `config.yaml` 及其分片，确认新增的 `proxy` 和 `prompts` 节点已生效。
