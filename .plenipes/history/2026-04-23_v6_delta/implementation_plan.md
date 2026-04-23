# [AEL-Iter-v6.0.1] Stage V6: Delta Block Engine (增量块引擎)

## 1. 目标描述 (Goal)
将 Illacme-plenipes 的同步颗粒度从 **“文件级”** 进化到 **“语义块级 (Semantic Block-level)”**。通过精准识别文档内部的变动块，仅对修改部分执行 AI 翻译，从而大幅降低 Token 消耗并提升长文处理并发度。

## 2. 核心架构设计 (Architecture)

### 2.1 语义切片算法 (Semantic Slicing)
- **输入**: 原始 Markdown 字符串。
- **解析**: 使用基于行扫描与状态机（而非正则）的解析器，识别出以下原子块：
    - 标题 (Headers)
    - 段落 (Paragraphs)
    - 列表项 (List Items)
    - 代码块 (Fenced Code Blocks)
    - 容器块 (Callouts, Tabs, Details) - 支持嵌套。
- **输出**: 一个 `BlockList` 对象，每个 `Block` 包含 `id (index)`, `content`, `type`, `fingerprint (MD5)`。

### 2.2 块级指纹系统 (Block Fingerprinting)
- **账本更新**: 在 `.plenipes/ledger.json` 中，原有的 `files` 节点下新增 `blocks` 映射。
- **比对逻辑**:
    - 如果 `file_hash` 发生变化，进入块级对比。
    - 逐一比对 `Block.fingerprint`。
    - 标记状态：`UNCHANGED` (指纹匹配), `MODIFIED` (内容变动), `NEW` (新增块), `DELETED` (旧块删除)。

### 2.3 抢占式并发调度 (Preemptive Scheduling)
- **任务化**: 每一个 `MODIFIED` 或 `NEW` 的块被视为一个独立的 `Task`。
- **全局信号量**: 所有文件的 `Task` 共用 `llm_concurrency` 信号量。
- **结果重组**: 使用 `TaskID` 维护块在原文中的物理位置，确保翻译完成后按序回填。

## 3. 拟修改模块 (Proposed Changes)

### 📂 core/logic/
#### [NEW] block_parser.py
实现 `MarkdownBlockParser` 类。负责将文本切片为具备语义边界的块。

### 📂 core/storage/
#### [MODIFY] ledger.py
升级 `LedgerManager` 以支持 `blocks` 节点的存储与查询。

### 📂 core/pipeline/
#### [MODIFY] runner.py
重构同步管线，插入块级对比逻辑，并实现 `Block-level Parallel Dispatching`。

### 📂 core/adapters/ai/
#### [MODIFY] base.py
确保 `BaseTranslator` 能够接收 `Block` 对象作为输入并处理局部翻译。

## 4. 验证计划 (Verification)

### 自动化测试
- **语义切片测试**: 验证嵌套 Callout 是否会被切碎。
- **增量更新测试**: 修改长文中的一个词，验证是否只触发了 1 次 AI 调用。
- **并发压力测试**: 将 `llm_concurrency` 设为 5，观察长文块是否并行执行。

### 物理审计
- **Galaxy Dimension 3 & 4**: 验证重构后的代码是否依然符合主权隔离与复杂度红线。
