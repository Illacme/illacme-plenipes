# SOP-03: 视觉主权与资产手册 (UI/UX & Assets Manual)
版本: V10.2 | 状态: 激活 (Active)

本手册定义了 Illacme Plenipes 指挥中心的物理架构、视觉资产保护及供应链安全红线，确保系统在极端环境下的可用性与主权隔离。

---

## 目录
1. [前端工程标准 (原 SOP-03)](#1-前端工程标准)
2. [供应链主权与依赖审计 (原 SOP-10)](#2-供应链主权与依赖审计)

---

## 1. 前端工程标准 (Original SOP-03)

本章节定义了指挥中心的物理架构与工程红线。

### 1.1 物理行数红线 (Physical Line Limits)
- **JS/CSS 模块上限**：单文件逻辑行数建议控制在 **300 行**以内，严禁超过 **500 行**。
- **模板解耦**：禁止在 JS 中硬编码超过 20 行的 HTML 模板，必须将其提取至 `views/` 目录下的独立视图组件中。
- **职责分层**：文件必须按 `Logic` (业务逻辑)、`Render` (视图渲染)、`Style` (样式表现) 进行物理拆分。

### 1.2 资产本土化主权 (Asset Localization Sovereignty)
- **严禁外部引用**：禁止在代码中引用任何 CDN 或第三方远程 URL（包括 JS 库、CSS 框架、图标等）。
- **物理下载强制令**：所有第三方资源必须物理下载并存放在 `core/api/static/vendor/` 目录下，并使用本地相对路径引用。
- **核心目的**：确保脱网可用，杜绝第三方劫持。

### 1.3 模块化与视觉锁定
- **命名空间保护**：所有全局单例挂载在 `window.plenipes` 下。
- **视觉主权锁定**：涉及项目身份标识（Banner、Logo、Sovereign OS Bar）的资产严禁擅自修改。

---

## 2. 供应链主权与依赖审计 (Original SOP-10)

本章节旨在物理拦截“依赖膨胀”与“供应链投毒”。

### 2.1 依赖白名单准则
1. **禁止静默安装**：AI 助手严禁在未获得批准的情况下新增任何第三方库。
2. **审计要求**：
   - 必须记录新增库的理由、版本号及许可证。
   - 优先使用项目原生库。

### 2.2 物理门禁 (Physical Gating)
- `sentinel_matrix.py` 会自动扫描依赖变更。若无对应审计记录，**立即拦截提交**。

---

## 3. 工业级视觉审美硬指标 (Industrial Aesthetic Standards)

本章节定义了项目的物理美学边界，AI 助手必须以此作为 UI 优化的最高准则。

### 3.1 物理网格与对齐 (Grid & Alignment)
1. **8px 步进系统**：所有间距（Gap）、填充（Padding）、边距（Margin）必须是 8 的倍数（特殊细微调整允许 4px）。
2. **视觉对齐优先**：在处理图标与文字对齐时，优先使用 `Optical Center`（视觉中心）而非简单的 `vertical-align: middle`。
3. **响应式断点**：强制适配 `375px` (Mobile), `768px` (Tablet), `1280px` (Laptop), `1920px` (Desktop)。

### 3.2 色彩与材质主权 (Color & Material)
1. **变量锁定**：严禁使用任何硬编码色值。必须使用 `index.css` 中定义的 CSS Variables。
2. **材质感 (Glassmorphism)**：核心看板组件必须遵循“玻璃拟态”规范：
   - `backdrop-filter: blur(12px) saturate(180%)`
   - `background: rgba(var(--bg-rgb), 0.7)`
   - `border: 1px solid rgba(255, 255, 255, 0.1)`
3. **层级阴影**：统一使用柔和的扩散阴影，严禁使用高对比度的生硬阴影。

### 3.3 动效语言 (Motion Language)
1. **高级曲线**：禁止使用默认的 `linear` 或 `ease`。强制使用 `cubic-bezier(0.4, 0, 0.2, 1)` (Swift Out) 或 `cubic-bezier(0, 0, 0.2, 1)` (Deceleration)。
2. **时长规范**：
   - 微交互（Hover/Active）：100ms - 150ms。
   - 页面切换/展开：250ms - 350ms。

---
*执行准则：代码是骨架，审美是主权。*
