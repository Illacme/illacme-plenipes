# 治理补丁计划：5 大规则盲区物理化 (Rule Hardening Roadmap)

将写在 Markdown 宪法中的"软规则"逐一翻译成 CPU 级别的"硬约束"。

## 补丁顺序与理据

| 优先级 | 补丁名称 | 对应宪法 | 风险等级 | 复杂度 |
|:---:|---|---|:---:|:---:|
| P1 | AEL-Iter-ID 代码溯源打标 | Rule VIII + Global VIII | 🔴 致命 | ⭐ 低 |
| P2 | 核心架构结构指纹保护 | Rule I, II, III | 🔴 致命 | ⭐⭐ 中 |
| P3 | 防御性编程静态拦截 | Rule IV | 🟡 高危 | ⭐⭐ 中 |
| P4 | 全局 KI 知识反哺强制 | Global V, X | 🟡 高危 | ⭐ 低 |
| P5 | 文档靶向精准绑定 | Rule V | 🟢 中危 | ⭐⭐⭐ 高 |

---

## P1: AEL-Iter-ID 代码溯源打标 🏷️

> **宪法依据**: Rule VIII "意图溯源" + Global Protocol VIII "Traceable Intent"
> **当前状态**: ❌ 完全没有物理检测

这是**最致命的盲区**。没有它，我写的所有代码都是"孤儿代码"——无法追溯到任何一次迭代记录。一旦未来出现 Bug，连"这行代码是哪次迭代引入的"都查不到。

### 实施方案

#### [MODIFY] [governance_audit.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/tests/governance_audit.py)

新增 `check_iter_id_tagging(audit)` 函数：
- 通过 `git diff HEAD --cached` 获取本次提交中变更的 `.py` 文件
- 对每个变更文件，检查新增行（`+` 开头）中是否包含 `[AEL-Iter-` 或 `[Iter-` 标记
- 如果有 Python 文件被修改但没有任何溯源标记，触发 `audit.fail()`

> [!NOTE]
> 排除列表：`tests/`、`scripts/` 目录下的工具脚本不强制要求打标，只对 `core/` 下的业务代码强制执行。

---

## P2: 核心架构结构指纹保护 🏛️

> **宪法依据**: Rule I "旗舰配置保护" + Rule II "核心架构保护" + Rule III "服务连续性"
> **当前状态**: ❌ 完全没有物理检测

如果我在某次修改中因为幻觉删除了 `TimelineManager`、砍掉了 `config.yaml` 的核心 `framework_adapters` 节点、或者移除了 `InputAdapter`，现有的门禁对此毫无感知。

### 实施方案

#### [MODIFY] [governance_audit.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/tests/governance_audit.py)

新增 `check_core_architecture_fingerprint(audit)` 函数：
- 维护一份"神圣签名列表"（Sacred Signatures），包含必须永远存在于代码中的关键类名/函数名：
  - `core/engine.py`: `TimelineManager`
  - `core/pipeline/steps.py`: `InputAdapter`, `MaskingAndRoutingStep`, `ContextualImageAltStep`
  - `core/egress_dispatcher.py`: `EgressDispatcher`, `unmask_fn`
  - `core/config.py`: `ConfigManager`
- 对每个签名，直接用 `grep` 检查对应文件中是否物理包含该标识符
- 任何签名消失 → `audit.fail("核心架构指纹缺失")`

---

## P3: 防御性编程静态拦截 🛡️

> **宪法依据**: Rule IV "NoneType Immunity"
> **当前状态**: ❌ 完全没有物理检测

如果我写了 `config["key"]` 而不是 `config.get("key")`，现在的系统会无感放行，但运行时遇到缺失键就会直接 `KeyError` 崩溃。

### 实施方案

#### [MODIFY] [governance_audit.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/tests/governance_audit.py)

新增 `check_defensive_coding_patterns(audit)` 函数：
- 扫描 `core/` 目录下所有 `.py` 文件
- 用正则检测高危模式：
  - `config\[["']` — 对 config 对象的裸索引访问（应使用 `.get()`）
  - `os\.environ\[["']` — 对环境变量的裸索引访问（应使用 `.get()`）
- 排除已有 `try/except` 包裹的上下文（简化处理：按行检测，允许白名单注释 `# SAFE-INDEX` 豁免）
- 发现未豁免的裸索引 → `audit.warn()`（首期为警告，稳定后升级为 fail）

---

## P4: 全局 KI 知识反哺强制 🧠

> **宪法依据**: Global Protocol V + X "Post-Session Deposit"
> **当前状态**: ❌ 完全没有物理检测

我经常在迭代完成后只更新了项目本地的 `evolution_records.md`，却忘了把跨项目通用的教训同步到全局 KI 知识库。这导致当你切换到其他项目时，那些教训就"死"了。

### 实施方案

#### [MODIFY] [governance_audit.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/tests/governance_audit.py)

新增 `check_global_ki_evolution_freshness(audit)` 函数：
- 读取全局 KI 进化记录：`~/.gemini/antigravity/knowledge/global_integrity/artifacts/evolution_records.md`
- 检查其最后修改时间是否在 **7 天以内**
- 超过 7 天未更新 → `audit.warn("全局知识反哺滞后")`

> [!NOTE]
> 此项设为 `warn` 而非 `fail`，因为不是每次微小迭代都会产生跨项目通用教训。但连续 7 天不更新则说明知识沉淀链条断裂。

---

## P5: 文档靶向精准绑定 📎

> **宪法依据**: Rule V "活化文档同步协议"
> **当前状态**: 🟡 粗粒度检测（只看 docs/ 是否有任何变更）

目前的检测逻辑是"改了 core/ → 只要 docs/ 下有任何变更就放行"。这无法防范我改了配置中心却去改了一篇不相关的文档来蒙混过关。

### 实施方案

#### [MODIFY] [governance_audit.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/tests/governance_audit.py)

升级现有的 `check_docs_update_quality(audit)` 函数：
- 建立"代码域 → 文档域"映射表：
  - `core/config.py` 变更 → 必须触及 `docs/REFERENCE.zh-CN.md`
  - `core/pipeline/` 变更 → 必须触及 `docs/SPECIFICATION.zh-CN.md`
  - `plenipes.py` (CLI) 变更 → 必须触及 `docs/MANUAL.zh-CN.md`
- 通过 `git diff --cached --name-only` 获取变更文件列表
- 如果代码域命中但对应文档域未命中 → `audit.warn()`（首期为警告）

---

## 执行策略

每个补丁按照标准 AEL 流程执行：
1. 编写检查函数并注入 `governance_audit.py`
2. 执行 `python3 tests/governance_audit.py` 验证
3. 使用 `harvest.py` 收割归档
4. 物理 `git commit` 触发防爆钩子全量验证

> [!IMPORTANT]
> 完成全部 5 个补丁后，治理引擎将从 v3.0 升级为 **v4.0**，检查项从 17 项扩展至 **22 项**，版本号和计数器需同步更新。

## 验证策略

### 自动验证
- 每个补丁完成后执行 `python3 tests/governance_audit.py`
- 最终执行 `git commit` 触发 pre-commit hook 全量验证

### 对抗测试
- P1: 故意提交一个不带 `[AEL-Iter-ID]` 的 core/ 文件修改，确认被拦截
- P2: 临时删除一个核心类名，确认指纹检测报警
