# TDR 迭代：技术债修复

- [x] 恢复底层的 Alt-Text 并网逻辑
  - [x] 提取并应用 `git stash` 上的业务层代码修改。
  - [x] 确保 `MetadataManager` 成功注册对应的图像缓存 API 方法。
  - [x] 确保 `MaskingAndRoutingStep` 与原图像处理方法正确交接替换。
- [/] 修复自主隔离沙盒环境崩塌问题
  - [ ] 修改 `autonomous_simulation.py` 以于临时隔离区创建 `.plenipes` 目。
  - [ ] 修改 `core/storage/sentinel.py` 以包涵化解在沙盒无头态无 `Ruff` 的崩溃处理。
- [ ] 全域验证试运行
  - [ ] 自主触发 `tests/autonomous_simulation.py` 通过。
  - [ ] 自触发 `tests/governance_audit.py` 返回全节点验证。
  - [ ] 生成提交并触发 Pre-Commit Hook 的最高层动态阻截锁以彻底完成演化。
