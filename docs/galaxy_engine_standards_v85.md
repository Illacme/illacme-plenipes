# Illacme Plenipes 3D 星系知识图谱：工业实现标准 (V85.0)

## 1. 核心架构：离线主权协议
该图谱完全遵循“零网络依赖”准则，是数字主权架构的核心体现。

- **单一引擎闭环**：弃用所有散装插件（OrbitControls, CSS2DRenderer 等），全面整合至 `3d-force-graph@1.80.0` UMD 本地包。
- **环境隔离**：物理移除 `THREE` 全局命名空间引用，避免库冲突。
- **缓存控制**：通过资源 URL 动态版本号（如 `?v=85.0`）强制浏览器进行物理级刷新。

## 2. 视觉美学：实验室级工业风
对标 vasturiano 官网首页，强调高密度数据感与精密感。

### 2.1 节点：能量核心 (Energy Cores)
- **动态呼吸 (Kinetic Pulse)**：通过全局定时器微调 `nodeRelSize` (4.5 ↔ 5.3)，赋予静态图谱以生命节律。
- **高保真材质**：使用高饱和度 emissive 颜色模拟金属光泽。

### 2.2 连线：星际激光网络
- **极细对标**：线条宽度限制在 `0.8` 以下，配合 `0.15` 低透明度，营造深邃感。
- **粒子律动**：显著增加 `linkDirectionalParticles` 密度，模拟数据包在神经网格中的流动。

### 2.3 UI 框架：Glassmorphism 2.0
- **网格矩阵 (Grid Matrix)**：面板背景注入 `30px` 径向点状网格。
- **极客几何**：统一使用 `12px` 硬核圆角。

## 3. 核心实现代码快照

### 3.1 实例化 (Standard Initialization)
```javascript
const graph = new ForceGraph3D(elem)
    .backgroundColor('rgba(0,0,0,0)')
    .nodeRelSize(5)
    .nodeColor(node => node.group === 'imprint' ? '#a34cff' : '#00f2ff')
    .nodeLabel(node => `<div class="galaxy-label">...</div>`)
    .linkDirectionalParticles(3);
```

### 3.2 动态巡航与能量脉冲
```javascript
// 🌪️ 开启自动旋转
graph.controls().autoRotate = true;
graph.controls().autoRotateSpeed = 0.4;

// 🧪 呼吸逻辑 (呼吸频率: 0.05rad)
let angle = 0;
setInterval(() => {
    angle += 0.05;
    const pulse = 4.5 + Math.sin(angle) * 0.8;
    graph.nodeRelSize(pulse); 
}, 100);
```

## 4. 样式覆写标准 (CSS Matrix)
```css
/* 强制覆盖原生 Tooltip 呈现全息感 */
.scene-tooltip {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}

/* Glassmorphism 2.0 变量定义 */
:root {
    --matrix-grid: radial-gradient(circle, rgba(0, 242, 255, 0.05) 1px, transparent 1px);
}
```

---
**核准版本**：V85.0  
**状态**：100% 离线主权，视觉对标完成。
