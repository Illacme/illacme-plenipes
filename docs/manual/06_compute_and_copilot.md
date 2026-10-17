# 🧠 06. 算力底座与自主智能体 (Compute & Sovereign Copilot)

### 功能概述
**算力中心** 为系统提供强劲的模型推理能力，涵盖全域大模型接入、延迟监控、故障自动降级策略，以及常驻工作台的 **Sovereign Copilot** 自主出版助手。

---

### 核心功能与操作

#### 1. 全域 AI 算力适配器 (25+ 提供商)
*   **主流云端大模型**：
    *   OpenAI (GPT-4o, o1, o3-mini)
    *   Google Gemini (Gemini 2.5 Flash, 3.8 Flash, Pro)
    *   Anthropic (Claude 3.5 Sonnet)
    *   DeepSeek (DeepSeek V3, R1)
    *   国内大模型：SiliconFlow、Qianfan、Dashscope、Zhipu 等。
*   **本地私有化算力 (Zero-Data Leakage)**：
    *   Ollama、LM Studio、LocalAI（完全断网即可执行高质量翻译）。

#### 2. 网关故障自愈与动态降级 (Failover)
*   支持设定**主选算力池**与**备用降级算力池**。
*   当遭遇官方 API 限流（429 Too Many Requests）或网络超时时，系统毫秒级平滑切换到备选模型，确保大批量全站翻译不中断。

#### 3. Sovereign Copilot 与人类审查 (HITL) 门禁
*   工作台右侧常驻智能对话面板，支持随时唤醒/收起（快捷键 `]`）。
*   **人类审查闭环 (Human-in-the-Loop)**：
    *   当 Copilot 需要执行敏感指令（如修改系统物理配置、推送全网发布或应用系统补丁）时，会强制生成确认卡片；
    *   **创作者点击批准**后才物理写盘，并提供 **一键撤销/回滚 (Rollback)** 机制，确保人机协作绝对安全。
