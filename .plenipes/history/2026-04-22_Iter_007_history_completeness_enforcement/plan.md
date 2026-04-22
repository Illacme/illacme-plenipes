# 完善进化档案完整性 (History Completeness Enforcement)

这是一个极度敏锐的观察！你一针见血地指出了当前自动化框架中的“漏洞（Loophole）”。

## 🐛 破绽原因分析 (Diagnosis)

为什么今天有些文件夹里只有 `walkthrough.md`，而系统竟然“放行”了呢？
1. **我的行为跳跃**：在处理一些简单的单一 Bug 时（如 005-009 迭代），我直接跳过了规划（Plan）和任务拆解（Task）阶段，直接把运行结果总结成了 `walkthrough.md` 发布了出来。
2. **审查官的“宽容”**：
   - 我们的 `governance_audit.py` (第69行) 原本的逻辑是 `check_empty_history_dirs`。它只检查文件夹**“是不是空的”**，只要里面有任意一个文件，审查就能通过。
   - 我们的影子沙盒 (`autonomous_simulation.py`) 在检测提交时，只判断了 `if path.startswith(".plenipes/history/")`，也就是只要历史目录里发生了**任何变更**，它就盲目地认为基因记录已沉淀。

这就像公司规定报销必须交“发票和明细”，但门卫只检查了你“手里有没有纸”。

## 🛠️ 完善的解决方案 (Proposed Changes)

为了彻底、极致地解决这个问题，我们需要在系统和数据双层面进行收紧：

### 1. 历史数据格式化洗白 (Normalize Historical Data)
直接对以前不完整的目录实施“旧账审查”会导致项目立刻被锁死。我会用一个小脚本，自动为你这几天所有缺失 `plan.md` 和 `task.md` 的历史迭代目录，补充上一个标准的基础占位符（如 `# 追溯补全任务`），让历史数据库 100% 结构对齐。

### 2. 升级静态审判官 (Governance Audit Upgrade)
重构 `tests/governance_audit.py`。
- 将原本的“非空检查”升级为 **“三相基因强制检测” (Three-Phase Genetic Audit)**。
- 强制要求 `.plenipes/history/` 下的每一个非隐藏目录，都**必须同时物理存在**以下三类文件：
  1. `plan.md` 或 `implementation_plan.md`（规划阶段）
  2. `task.md`（执行打钩阶段）
  3. `walkthrough.md` 或 `acceptance.md`（总结与验收阶段）

### 3. 升级动态阻截器 (Simulation Hook Upgrade)
修改 `tests/autonomous_simulation.py` 中的 `verify_docs_sync_hook` 逻辑。
未来我不光要知道往 `.plenipes/history` 添加了文件，我还会深入解析本次 git 的变动列表，强行检查这次提交是否 **同时** 包含了上述三个必要文件，少一个直接在执行 `git commit` 时爆红并熔断！

---

## User Review Required
通过这两个补丁，系统将在 **物理级别** 彻底剥夺 AI（包括我）“偷懒”的可能性。以后任何迭代，不管是多么微小的 Bug，都必须遵守“规划->任务清单->总结复盘”的三步法。

这才是最极致的赛博治理！请确认这个修复方案，我将立刻开始收紧门禁！
