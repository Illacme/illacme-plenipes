# 同步管线与状态一致性规约

## 1. 概述
Illacme-plenipes 采用流水线（Pipeline）架构处理文档。为了确保“增量同步”的准确性，管线必须保证在执行决策（是否跳过）之前，能够获取到纯净、未受当前周期干扰的历史状态。

---

## 2. 状态隔离机制 (State Isolation)

### 2.1 启动前快照协议 (Pre-Sync Snapshot)
*   **设计原则**：在 `sync_document` 方法进入管线第一步之前，必须对账本（Ledger）中的旧数据执行“冷备份”，存入 `_old_info_cache`。
*   **背景原因**：防止管线中途的元数据更新步骤（如 `MetadataAndHashStep`）修改了账本，导致后续的同步检测逻辑误判为“已完成”。

### 2.2 确定性哈希计算
*   **公式**：`CurrentHash = MD5(ProcessedFrontmatter + BodyContent)`。
*   **应用**：该哈希值作为判定文件级跳过的唯一真理。

---

## 3. 典型技术坑位 (Lessons Learned)

### 3.1 案例分析：哈希覆盖导致的“虚假跳过”
*   **现象**：修改文件内容后，引擎依然报告 `🔄 [指纹匹配跳过]`。
*   **根因**：`MetadataAndHashStep` 在管线中途将新哈希写入了账本，而后续的 `engine.py` 逻辑直接从账本读取了最新哈希进行对比，导致“自己和自己比”永远相等。
*   **修复方案**：引入 `_old_info_cache`，强制所有跳过决策必须基于“同步开始前”的镜像状态。

---

### 4.2 元数据深度对齐 (Metadata Alignment)
*   **适用对象**：`title`, `tags`, `categories`。
*   **处理模式**：批量原子化翻译（Batch Atomic Translation）。
*   **价值**：确保分类体系在全语种下保持语义一致性，提升 SEO 权重。

## 5. 管线生命周期 (Lifecycle)
1.  **Initialize**: 提取旧哈希，准备 `SyncContext`。
2.  **Normalize**: 读取并抹平编辑器方言。
3.  **Purify**: 剥离技术噪声，准备 AI 输入。
4.  **Audit**: 计算当前哈希，检查是否可以跳过。
5.  **Transform (Delta)**: 启动块级增量翻译（Delta Block Engine）。
6.  **Align (Metadata)**: [V6.1] 执行标题与标签的深度语义对齐。
7.  **Distribute**: 向物理影子库与前端分发。
8.  **Finalize**: 将新哈希写入账本。

---
*文档签署人：Antigravity AI*
*签署日期：2026-04-23*
