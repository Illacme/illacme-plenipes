# 📜 Illacme Plenipes 出版社技术协议与商业共识 (Consensus Protocol)
## 品牌方案 C 与 V48.3 架构定型版 (Final Consensus)

> **核心宪制**：Illacme Plenipes 是一套服务于“全球私人出版社”的主权操作系统，其核心底座为“您的主权化全球出版发行中心”。

---

## 1. 品牌与主权占位 (Branding & Sovereignty)
*   **品牌定位**：全球私人出版社 (Global Private Press)。
*   **功能定位**：您的主权化全球出版发行中心 (Sovereign Global Publishing & Distribution Center)。
*   **主权原则**：数据不漂移、算力本地化、物理强隔离、资产可审计。

## 2. 疆域与资产隔离 (Territory & Isolation)
*   **疆域实体 (Territory)**：[原 Workspace] 每个疆域是一个独立的出版经营实体，拥有私有的配置、账本、索引与时间轴。
*   **全主题感知隔离**：[V48.3] 疆域内的核心资产（`meta.db`, `vectors.json`, `pulse.json`）必须支持 **“主题化物理隔离”**。切换主题即切换物理存储路径，确保不同装帧风格下的数据不发生污染。
*   **零硬编码协议**：严禁在核心代码中硬化任何物理路径。所有路径必须通过 `engine.paths` 协议从疆域根目录动态派生。

## 3. 授权与准入治理 (License & Governance)
*   **权益逻辑**：
    - **社区版**：单一疆域，单一语种，基础分发。
    - **授权版 (Sovereign)**：无限疆域，全量语种矩阵，子目录切片映射，主题物理隔离。
*   **凭据安全**：严禁明文存储 Credential。必须实装 `SecretSentinel` 机制，确保存储主权不因配置文件外泄而沦陷。

## 4. 运行环境与装帧 (Runtime & Bindery)
*   **环境隔离 (EnvironmentContainer)**：为防止不同 SSG 适配器版本冲突，系统支持为特定疆域锁定独立的工具链环境。
*   **装帧自愈**：启用新主题时，系统应自动执行物理资产搬运与 i18n 拓扑构建。

## 5. 分发事务与一致性 (Egress & Consistency)
*   **原子化分发**：多渠道分发（S3, Webhook, GitHub）必须遵循事务契约。部分失败时，必须在账本中标记 `PARTIAL_SUCCESS`。
*   **净化审计 (Janitor)**：物理抹除操作必须记录在“主权净化日志”中，确保物理疆域的变动可追溯。

## 6. 项目主权语义映射 (Sovereign Mapping)
为了确保品牌、文档与代码的一致性，系统采用以下映射标准：
*   **Intake**：进稿/收割。
*   **Egress**：分发/出稿。
*   **Territory**：疆域（出版经营实体）。
*   **Pulse**：脉搏（实时治理体征）。
*   **Timeline**：时间轴（主权经营历史）。

---
**总编辑确认**：____________________
**执行审计**：Antigravity (AEL-Iter-V48.3)
**日期**：2026-04-30
