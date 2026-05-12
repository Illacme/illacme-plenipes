# SOP-03: 前端工程标准 (Frontend Engineering Standards)

本准则定义了 Illacme Plenipes 前端**指挥中心 (Command Center)** 的物理架构与工程红线，旨在确保 **出版版图** 可视化的极致稳定、安全隔离与脱网可用性。

## 1. 物理行数红线 (Physical Line Limits)
- **JS/CSS 模块上限**：单文件逻辑行数建议控制在 **300 行**以内，严禁超过 **500 行**。
- **模板解耦**：禁止在 JS 中硬编码超过 20 行的 HTML 模板，必须将其提取至 `views/` 目录下的独立视图组件中。
- **职责分层**：文件必须按 `Logic` (业务逻辑)、`Render` (视图渲染)、`Style` (样式表现) 进行物理拆分，严禁创建巨型单体文件。

## 2. 资产本土化主权 (Asset Localization Sovereignty)
- **严禁外部引用**：禁止在代码中引用任何 CDN 或第三方远程 URL（包括但不限于 JS 库、CSS 框架、Google Fonts、远程图标、外部图片）。
- **物理下载强制令**：所有第三方资源必须物理下载并存放在 `core/api/static/vendor/` 目录下，并使用本地相对路径引用。
- **核心目的**：确保系统在内网、断网或极端环境（主权隔离）下依然能 100% 正常工作，杜绝第三方链路追踪、数据泄露与物理劫持。

## 3. 模块化与组件化 (Modularity)
- **命名空间保护**：所有全局单例必须挂载在 `window.plenipes` 命名空间下，严禁污染全局作用域以防止命名冲突。
- **CSS 治理**：通用样式收敛于 `css/components/`，视图特定样式存放于 `css/views/`。

## 4. 视觉主权锁定 (Visual Locking)
- **核心资产保护**：涉及项目身份标识（Banner、Logo、Sovereign OS Bar）的 CSS 布局与图片资产严禁在未授权情况下修改。

---
*优先级：高 (03)*
*更新日期：2026-05-12*
