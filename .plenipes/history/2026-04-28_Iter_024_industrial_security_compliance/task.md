# Task List - Phase 2 架构合规重构

## 1. Governance - Doctor Service 重构 (348 -> <300)
- [x] 创建 `core/governance/checks/` 目录与子模块
- [x] 迁移 Infrastructure 检查逻辑 -> `checks/infra.py`
- [x] 迁移 Ledger & Metadata 检查逻辑 -> `checks/ledger.py`
- [x] 迁移 Contract & Plugin 检查逻辑 -> `checks/plugins.py`
- [x] 迁移 Auto-Heal 正则逻辑 -> `core/governance/healer.py`
- [x] 更新 `doctor.py` 委托调用并完成瘦身

## 2. UI - Terminal UI 重构 (486 -> <300)
- [x] 创建 `core/ui/handlers/` 目录与子模块
- [x] 迁移 基础状态处理 (Banner, Progress) -> `handlers/status_handlers.py`
- [x] 迁移 审计与诊断报告处理 -> `handlers/audit_handlers.py`
- [x] 迁移 汇总与性能看板处理 -> `handlers/summary_handlers.py`
- [x] 迁移 向导逻辑 -> `core/ui/wizard.py`
- [x] 更新 `terminal.py` 订阅中枢并完成瘦身

## 3. API - Server 路由模块化 (372 -> <300)
- [x] 创建 `core/api/routes/` 目录与子模块
- [x] 提取 系统路由 (Health, Stats, Shutdown) -> `routes/system.py`
- [x] 提取 内容路由 (Ledger, Search, Galaxy) -> `routes/content.py`
- [x] 提取 治理路由 (Logs, Billing, Workspaces) -> `routes/governance.py`
- [x] 更新 `server.py` 使用 `include_router` 并完成瘦身

## 4. Storage & Utils 补尾 (312/307 -> <300)
- [x] 提取 SQL 静态语句 -> `core/storage/sql_statements.py`
- [x] 拆分 Common Utils -> `utils/text.py`, `utils/io.py`
- [x] 更新引用并验证

## 5. 验收与回归
- [x] 全量文件行数审计 (Red-line Scan)
- [x] 运行集成测试验证业务闭环
- [x] 验证 API Swagger 文档完整性
