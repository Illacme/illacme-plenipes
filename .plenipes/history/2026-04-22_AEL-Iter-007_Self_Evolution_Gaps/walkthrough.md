# 自进化缺口修补验收

## 修补内容
1. 创建 `scripts/setup-hooks.sh`：pre-commit hook 可移植到任一新环境。
2. 新增审计 #11 `check_precommit_hook_exists`：检测 hook 是否安装。
3. 新增审计 #12 `check_untracked_runtime_artifacts`：自动发现疑似状态文件。
4. 审计引擎升级至 v1.2，共 13 项检查。
