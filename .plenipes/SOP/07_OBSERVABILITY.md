# SOP-07: 日志与全链路可观测性标准 (Observability Standards)

> [!IMPORTANT]
> **本标准定义了代码资产的“可监控”等级。严禁编写无法被外部审计感知的“黑盒逻辑”。任何静默失效均被视为开发缺陷。**

## 1. 强制性日志指纹 (Mandatory Fingerprints)
代码中任何涉及 **外部契约 (API/IO/User Input/Logic Pivot)** 的操作，必须包含以下物理日志指纹：

### A. 后端物理审计 (tlog)
- **入口审计**：接收到 API 请求或 CLI 指令时，必须记录关键 ID 指纹。
- **同步审计**：在执行配置修改、内存赋值 (`setattr`) 或物理落盘前，必须输出 `📝 [内存同步]` 或 `💾 [物理固化]` 标签。
- **异常穿透**：严禁静默捕获异常。所有 `try-except` 必须输出 `tlog.error`。

### B. 前端交互审计 (addAudit)
- **链路达标指纹**：API 数据到达并被解析后，必须输出 `✅ [数据流达]` 记录。
- **交互联动指纹**：在复杂的 UI 联动逻辑中（如：选择 Provider 自动填 URL、Model Discovery 感应），必须输出 `📡 [联动对正]` 指纹，清晰描述“从哪来，到哪去”。

## 2. 契约自校验指纹 (Contract Enforcement)
- **防御性纠偏**：如果逻辑层检测到字段缺失（如 `undefined` 或 `null`），必须主动调用 `addAudit` 触发 **[RED_ALERT]** 提示，而非静默终止。

## 3. 验证准则 (Validation)
- AI 助理在验证阶段，必须通过 `browser_console` 或后台日志流，**物理证明**上述指纹已被真实触发。禁止仅凭 UI 视觉猜测功能状态。

## 4. 调试视野强制令 (Mandatory Debug Mode)
- **启动环境对正**：在开发迭代与验证阶段，必须显式开启调试模式：
  `python3 plenipes.py --api --log-level DEBUG`
- **严禁“盲飞”**：AI 助手禁止在 `INFO` 级别下声称功能验证通过。必须在验证 Thought 环节中捕获并分析 `[DEBUG]` 级别的逻辑分叉指纹。
- **控制台主权**：前端验证必须通过 `get_browser_console_logs` 同步检查。如果控制台出现任何被 UI 遮盖的 `undefined` 或逻辑警告，视为验证不通过。

---
*修订日期：2026-05-13*
*执行准则：无日志，不交付；无指纹，不通过。*
