# Git 卫生治理方案：精准切割本地态与架构基建 (Git Hygiene)

## 背景
随着 V34.5 状态机 (Timeline 和 Ledger) 的建立，大量的操作流水和缓存文件（如 `.plenipes/ledger.json`）堆积在项目根目录与子目录中。这些文件由于带有极强的物理机器主观色彩，若进入 Git 版本树将导致代码库无端膨胀，并引发无穷尽的 Merge 冲突。

## 实施路径
1. **重构 `.gitignore`**：在末尾追加 `Zone 7`，专门用于屏蔽 `illacme-plenipes` 新时代独有的本地状态文件，主要包含：
   - 所有的 `.plenipes/*.json` 账本与健康探测结果。
   - `timeline.md` 审计流水日志。
   - `.illacme-shadow/` AIGC 算力缓存目录。
2. **清除既有隐患**：由于部分环境账本在早期缺乏规范控制时早已被 Git 抓取并缓存，必须通过物理清除指令 `git rm --cached` 将它们硬性抽离出现有的追踪网。
3. **保留金字招牌**：确立隔离边界，严禁将全量 `.plenipes` 目录一刀切。必须强制留存并上传项目的 ADR（`history/` 演化池）、系统宪法（`rules.md`）以及项目愿景图（`ROADMAP.md`）。
