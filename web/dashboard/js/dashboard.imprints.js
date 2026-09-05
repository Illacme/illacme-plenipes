/**
 * ⚙️ [V74.0] Illacme Plenipes Imprints Management Module (Hub Controller)
 * 职责：出版集团指挥中心、核心品牌意志切换、物理隔离与一键注销。
 * 遵循 SOP-02 模块拆分协议，各功能板块已微步物理迁入对应专用分片。
 */

// 💡 [SOP-02 拆分分片拓扑]
// 1. 生命周期与热重载 -> js/imprints/imprints_shards/imprints.lifecycle.js
// 2. 向导表单与路径拾取 -> js/imprints/imprints_shards/imprints.wizard.form.js
// 3. 算力环境与模型探活 -> js/imprints/imprints_shards/imprints.wizard.compute.js
// 4. 算力分发配置与摘要 -> js/imprints/imprints_shards/imprints.wizard.config.js
// 5. 步骤校验与向导流转 -> js/imprints/imprints_shards/imprints.wizard.flow.js
// 6. 异步创建与网络提交 -> js/imprints/imprints_shards/imprints.wizard.submit.js
// 7. 成功模态框与就绪页 -> js/imprints/imprints_shards/imprints.wizard.modal.js

window.addNewImprint = async () => {
    if (typeof window.checkSettingsDirtyAndConfirm === 'function') {
        const proceed = await window.checkSettingsDirtyAndConfirm();
        if (!proceed) return;
    }

    const isLicensed = window.settingsData?._is_licensed || false;
    const currentCount = window.settingsData?._imprints?.length || 0;

    if (!isLicensed && currentCount >= 2) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: '🛡️ 准入拦截',
                html: '<div style="text-align:left; font-size: 0.9rem; line-height: 1.6;">' +
                      '您当前处于 <b>免费社区版</b>。<br><br>' +
                      '• 品牌限额: 2/2 (已含 1 个默认品牌 + 1 个自定义品牌)<br>' +
                      '• 治理限制: 社区版最多允许创建 1 个自定义出版品牌。<br><br>' +
                      '<span style="color:var(--accent-secondary)">💡 建议：升级至 [高级专业版] 以解锁多品牌管理。</span>' +
                      '</div>',
                icon: 'warning',
                confirmButtonText: '了解',
                background: 'var(--card-bg)',
                color: 'var(--text-bright)',
                confirmButtonColor: 'var(--accent-primary)'
            });
        } else {
            alert("🛡️ [准入拦截]\n免费社区版限额 2 个品牌 (1 个默认 + 1 个自定义)，无法继续添加。");
        }
        return;
    }

    if (typeof window.showImprintWizard === 'function') {
        window.showImprintWizard();
    }
};

// 🏛️ 向后兼容命名空间代理桥接
window.ImprintsHub = {
    switch: (id) => typeof window.switchImprint === 'function' && window.switchImprint(id),
    delete: (id) => typeof window.deleteImprint === 'function' && window.deleteImprint(id),
    hotswap: (id) => typeof window.hotswapActiveImprint === 'function' && window.hotswapActiveImprint(id),
    add: () => typeof window.addNewImprint === 'function' && window.addNewImprint()
};
