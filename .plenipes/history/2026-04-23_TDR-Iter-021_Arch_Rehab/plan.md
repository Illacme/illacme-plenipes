# 实施方案 - TDR-Iter-021: 架构复健与复杂度降熵

## 1. 背景与目标
根据 v5.3 治理审计结果，项目已触发 TDR (架构复健) 阈值。本迭代的目标是处理技术债务，将核心文件压回 300 行健康黄线以内，并提升整体代码的防御性水平。

## 2. 核心修复任务

### 2.1 复杂度降熵：拆解 `engine.py` (425行 -> <300行)
- **[NEW] `core/engine_factory.py`**：迁移 `Engine` 类的初始化逻辑、组件挂载（Sentinel, Timeline, Staticizer 等）以及路径校验逻辑。
- **[MODIFY] `core/engine.py`**：保留核心管线调度逻辑，通过工厂类完成实例化。

### 2.2 防御性加固：消除 NoneType 风险
- 针对审计标记 of 5 个文件，将 `config['key']` 或 `s_fm['key']` 模式统一替换为 `config.get('key', default)`。
- 重点覆盖：`egress_dispatcher.py`, `config.py`, `engine.py`。

### 2.3 环境卫生清理
- **[MODIFY] `.gitignore`**：补全 `.plenipes/*.json` 和 `.plenipes/*.log` 的屏蔽规则。
- **物理清理**：递归删除全库的 `__pycache__` 和 `.pyc` 编译产物。

### 2.4 文档同步
- 更新 `docs/SPECIFICATION.zh-CN.md`，同步 v5.3 的模块化审计架构说明。

## 3. 拟修改文件

### [CORE]
#### [MODIFY] [engine.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/engine.py)
#### [NEW] [engine_factory.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/engine_factory.py)
#### [MODIFY] [config.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/config.py)
#### [MODIFY] [egress_dispatcher.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/egress_dispatcher.py)

### [GOVERNANCE]
#### [MODIFY] [.gitignore](file:///Volumes/Notebook/omni-hub/illacme-plenipes/.gitignore)

## 4. 验证方案
- 运行 `python3 tests/governance_audit.py`。
- **预期结果**：
    - `文件复杂度黄线` 预警项中 `engine.py` 消失。
    - `防御性编程审计` 通过。
    - `Git 状态泄露` 通过。

## 5. 待确认问题
- 是否需要同时拆解 `egress_dispatcher.py`？
- **建议**：本次优先处理最核心的 `engine.py`，保持迭代原子性。
