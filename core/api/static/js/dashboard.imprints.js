/**
 * ⚙️ [V74.0] Illacme Plenipes Imprints Management Module (Hub Controller)
 * 职责：出版集团指挥中心、核心事业部意志切换、物理隔离与一键注销。
 */

window.switchImprint = async (id) => {
    if (!id) return;
    addAudit(`🛰️ 正在申请事业部切换: ${id}...`, "info");

    const res = await apiFetch('/api/imprints/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ imprint_id: id })
    });

    if (res && res.success) {
        addAudit(`🔄 [对正] 成功切换至事业部: ${id}`, "success");
        if (typeof renderImprintDropdown === 'function') renderImprintDropdown();
        
        // 🚀 [V74.15] 全域主权对正：品牌切换是重量级上下文切换，强制刷新以确保所有视图与后端引擎同步
        setTimeout(() => {
            location.reload();
        }, 800);
    } else {
        addAudit(`🚨 切换失败: ${res ? res.error : '物理链路异常'}`, "error");
    }
};

window.addNewImprint = async () => {
    const isLicensed = window.settingsData?._is_licensed || false;
    const currentCount = window.settingsData?._imprints?.length || 0;

    if (!isLicensed && currentCount >= 1) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: '🛡️ 准入拦截',
                html: '<div style="text-align:left; font-size: 0.9rem; line-height: 1.6;">' +
                      '您当前处于 <b>社区标准版</b>。<br><br>' +
                      '• 事业部限额: 1/1 (已满)<br>' +
                      '• 治理限制: 无法添加更多出版事业部。<br><br>' +
                      '<span style="color:var(--accent-secondary)">💡 建议：升级至 [专业版] 以开启无限事业部管理。</span>' +
                      '</div>',
                icon: 'warning',
                confirmButtonText: '了解',
                background: 'var(--card-bg)',
                color: 'var(--text-bright)',
                confirmButtonColor: 'var(--accent-primary)'
            });
        } else {
            alert("🛡️ [准入拦截]\n社区版限额 1 个事业部，无法继续添加。");
        }
        return;
    }

    if (typeof showImprintWizard === 'function') {
        showImprintWizard();
    }
};

window.deleteImprint = async (id) => {
    if (!confirm(`🚨 危险操作！\n确认要物理抹除出版事业部 [${id}] 吗？`)) return;

    const res = await apiFetch('/api/imprints/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: id })
    });

    if (res && res.success) {
        addAudit(`🗑️ 事业部已撤销: ${id}`, "warning");
        loadSettings('imprints');
    }
};
