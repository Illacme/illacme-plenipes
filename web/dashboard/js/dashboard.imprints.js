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
        
        // 🚀 [V75.6] 全域事件总线无感热重载 (Zero-Reload Hotswap)
        if (typeof window.hotswapActiveImprint === 'function') {
            await window.hotswapActiveImprint(id);
        } else {
            setTimeout(() => {
                location.reload();
            }, 800);
        }
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

/**
 * 🚀 [V75.6] 全域事件总线无感热重载 (Zero-Reload Hotswap)
 * 解决切换事业部全页白屏重载的痛点，毫秒级无缝换脑
 */
window.hotswapActiveImprint = async (id) => {
    try {
        if (typeof showNotification === 'function') {
            showNotification(`🔄 正在快速切换至版图事业部: ${id}...`, 'info');
        } else if (typeof addAudit === 'function') {
            addAudit(`🔄 正在执行零加载无感热重载至: ${id}...`, 'info');
        }
        
        // 1. 重新拉取全量系统设置与品牌元数据
        if (typeof loadSettings === 'function') {
            // 记住当前的设置 Tab
            const activeTab = document.querySelector('.s-tab.active');
            const targetTab = activeTab ? activeTab.dataset.cat : 'imprints';
            await loadSettings(targetTab);
        }
        
        // 2. 重新加载原稿文库及目录探索树
        if (typeof loadVault === 'function') {
            window.vaultTreeInitialized = false; // 强制重构目录树
            await loadVault();
        }
        
        // 3. 刷新全量生命体征与审计上下文
        if (typeof refreshGovernanceContext === 'function') {
            await refreshGovernanceContext();
        }
        
        // 4. 重建全息星系宇宙 (如果是 Overview 面板且 3D 库存在)
        if (window.currentView === 'overview' && typeof refreshGalaxy === 'function') {
            refreshGalaxy();
        }
        
        // 5. 交互徽章特制霓虹微光脉冲
        const badge = document.getElementById('active-imprint-name');
        if (badge) {
            badge.classList.add('pulse-success');
            setTimeout(() => badge.classList.remove('pulse-success'), 1500);
        }
        
        if (typeof showNotification === 'function') {
            showNotification(`✅ 已无缝热重载至事业部: ${id}`, 'success');
        } else if (typeof addAudit === 'function') {
            addAudit(`✅ 零加载热重载成功，版图: ${id}`, 'success');
        }
    } catch (err) {
        console.error("Hotswap failed, falling back to reload:", err);
        location.reload();
    }
};
