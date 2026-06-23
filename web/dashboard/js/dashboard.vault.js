/**
 * 📂 [V55.0] Illacme Plenipes Vault & Editor Component Hub
 * 职责：稿件仓库加载调度、分发矩阵遥测，对外进行逻辑控制。
 * 🛡️ [V75.2 Decoupled] 模块化重构：Obsidian 目录树、Markdown 编辑器及磁盘 Ops 已分离至 vault 子目录原子文件中。
 * 🛡️ [V88.0 Split] 物理拆分：列表+分页逻辑迁移至 vault/vault.list.js，Drawer+遥测+重调度迁移至 vault/vault.drawer.js。
 *    本文件退化为状态矩阵声明中心 (Hub)。
 */

// 1. 状态矩阵
window.currentDocId = null;
window.activeDocId = null;
window.vaultSearchTimeout = null;
window.vaultCurrentPage = 1;
window.vaultCurrentQuery = '';
window.vaultPageSize = 20;
window.vaultActiveFolder = '';
window.vaultTreeInitialized = false;
window.vaultTotalItems = 0;
