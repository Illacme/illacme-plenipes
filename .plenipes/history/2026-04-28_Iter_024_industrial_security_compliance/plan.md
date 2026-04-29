# Implementation Plan - Dashboard 2.0: Intelligence Panorama

本计划旨在将 Omni-Hub 的监控界面从“工程仪表盘”升级为“智源全景中心”，通过 3D 可视化与现代设计语言提升产品溢价感。

## User Review Required

> [!IMPORTANT]
> 1. **技术栈选择**: 采用原生 HTML5 + CSS3 (Vanilla) + 3D-Force-Graph (CDN) 实现，确保轻量且无环境依赖。
> 2. **视觉风格**: 强制启用深色模式 (Deep Dark) 与玻璃拟态 (Glassmorphism) 风格。
> 3. **实时性**: 利用现有的 `/api/stats` 与 `/api/galaxy/graph` 接口，结合 `setInterval` 实现伪实时同步。

## Proposed Changes

### 1. 视觉系统重塑 (CSS Design System)
#### [MODIFY] [dashboard.css](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/api/static/dashboard.css)
*   引入 Google Fonts (Outfit / JetBrains Mono)。
*   定义全局 CSS 变量（极光紫、主权蓝、预警红）。
*   实现 `.glass-card` 组件与平滑过渡动画。

### 2. 3D 知识银河实现 (Frontend Logic)
#### [MODIFY] [dashboard.js](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/api/static/dashboard.js)
*   集成 `3d-force-graph` 库。
*   实现节点的语义聚类显示：
    *   AI 节点（紫光）。
    *   用户定义节点（金光）。
    *   关联强度（光晕亮度）。
*   添加节点点击交互：展示摘要与关联列表。

### 3. 结构化布局更新 (HTML Structure)
#### [MODIFY] [index.html](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/api/static/index.html)
*   重构网格布局：
    *   **左侧**: 引擎脉冲 (Pulse) 与算力 ROI。
    *   **中央**: 3D 知识银河容器。
    *   **右侧**: 实时审计流水与诊断简报。

### 4. 品牌资产增强
#### [NEW] [logo_v2.png](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/api/static/logo_v2.png)
*   利用 `generate_image` 生成具有科幻质感的 Omni-Hub V2 标识。

## Verification Plan

### Manual Verification
*   **浏览器兼容性**: 在 Chrome/Safari 中验证 3D 渲染帧率。
*   **交互验证**: 点击图谱节点，确认右侧侧边栏能正确弹出详细信息。
*   **自适应测试**: 验证在不同分辨率下的布局伸缩性。
