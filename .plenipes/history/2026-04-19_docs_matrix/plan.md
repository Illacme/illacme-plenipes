# 活化文档系统矩阵 (Docs Matrix) 实施方案

## 背景与目标
随着 V33 时代高精度切片以及并发框架的引入，功能的断崖式膨胀导致单体 `README.md` 已无法承载引擎所有的环境变量与使用边界。为保持工业级项目的清晰度，须建立“活化文档机制 (Living Documentation Matrix)”。

## 实施策略
1. **拆解三维视界**：
   - `docs/SPECIFICATION.zh-CN.md` (面向协同者)：沉淀同步管线概念、算法设计（Shadow，Staticization）与协议规范。
   - `docs/REFERENCE.zh-CN.md` (面向配置环境)：收拢所有字典配置、命令行参数 `CLI` 与日志阈值。
   - `docs/MANUAL.zh-CN.md` (面向内容创作者)：提供开箱即用的工作流（Watchdog 保存即发布）、避坑排雷与灾备复原指南。
2. **制度约束**：在随后引入的 `.plenipes/rules.md` 中加入 "Living Documentation Mandate" 红线，规定未来凡涉及到核心类的底层修改，必须以更新上述文档作为验收结束的标志。
