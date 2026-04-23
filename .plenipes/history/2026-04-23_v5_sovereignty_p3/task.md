# Task List: Sovereign Engine Hardening (AEL-Iter-v5.4)

- [x] **Phase 1: Logic Hub & Line Count Enforcer**
    - [x] 创建 `ai_logic_hub.py` 并下沉 Prompt 组装逻辑
    - [x] 重构 `BaseTranslator` 实现逻辑隔离
    - [x] 强制约束 `core/` 核心文件控制在 300 行红线内
- [x] **Phase 2: 物理主权审计 (Topology & Entry)**
    - [x] 实现 `check_topology_integrity` (包结构与 Import 连通性)
    - [x] 实现 `check_main_entry_smoke_test` (主程序冒烟测试)
    - [x] 确立 `syndicate()` 方法签名契约审计
- [x] **Phase 3: 治理星系重排 (Scheduling Optimization)**
    - [x] 将审计流程重组为“五大星系”架构 (物理 -> 系统 -> 代码 -> 仿真 -> 历史)
    - [x] 优化失败诊断路径，优先暴露物理层断裂
- [x] **Phase 4: 历史主权加固 (History Deep Audit)**
    - [x] 升级 `check_history_docs_depth` 实现“计划/验收”双相追溯
    - [x] 将任务核销审计扩展至最近 3 个迭代周期
- [x] **Phase 5: 最终验收 (Verification)**
    - [x] 运行全量 `governance_audit.py` (60/60 Pass)
    - [x] 执行 GitHub 交付推送
