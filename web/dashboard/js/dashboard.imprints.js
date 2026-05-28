/**
 * ⚙️ [V74.0] Illacme Plenipes Imprints Management Module (Hub Controller)
 * 职责：出版集团指挥中心、核心版图意志切换、物理隔离与一键注销。
 */

window.switchImprint = async (id) => {
    if (!id) return;
    addAudit(`🛰️ 正在申请版图切换: ${id}...`, "info");

    const res = await apiFetch('/api/imprints/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ imprint_id: id })
    });

    if (res && res.success) {
        addAudit(`🔄 [对正] 成功切换至版图: ${id}`, "success");
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
                      '• 版图限额: 1/1 (已满)<br>' +
                      '• 治理限制: 无法添加更多出版版图。<br><br>' +
                      '<span style="color:var(--accent-secondary)">💡 建议：升级至 [专业版] 以开启无限版图管理。</span>' +
                      '</div>',
                icon: 'warning',
                confirmButtonText: '了解',
                background: 'var(--card-bg)',
                color: 'var(--text-bright)',
                confirmButtonColor: 'var(--accent-primary)'
            });
        } else {
            alert("🛡️ [准入拦截]\n社区版限额 1 个版图，无法继续添加。");
        }
        return;
    }

    if (typeof showImprintWizard === 'function') {
        showImprintWizard();
    }
};

window.deleteImprint = async (id) => {
    // 🛡️ [安全底线拦截] 前端双重保护：严禁删除活动版图与默认版图，防范系统配置丢失雪崩
    const activeImprint = window.settingsData?._active_imprint || 'default';
    if (id === 'default' || id === activeImprint) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: '🛡️ 安全拦截',
                html: `<div style="text-align:left; font-size: 0.9rem; line-height: 1.6;">` +
                      `无法删除当前<b>正处于激活状态</b>（或默认）的版图：<b style="color:var(--accent-secondary)">${id}</b>。<br><br>` +
                      `💡 <b>自愈建议：</b><br>` +
                      `请先在左上角切换至其他可用版图，然后再对本版图执行注销或物理抹除。` +
                      `</div>`,
                icon: 'error',
                confirmButtonText: '了解',
                background: 'var(--card-bg)',
                color: 'var(--text-bright)',
                confirmButtonColor: 'var(--accent-primary)'
            });
        } else {
            alert(`🛡️ [安全拦截]\n无法删除当前处于激活状态（或默认）的版图 [${id}]！\n请先切换至其他可用版图后再行操作。`);
        }
        return;
    }

    if (!confirm(`🚨 危险操作！\n确认要物理抹除出版版图 [${id}] 吗？`)) return;

    const res = await apiFetch('/api/imprints/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: id })
    });

    if (res && res.success) {
        addAudit(`🗑️ 版图已撤销: ${id}`, "warning");
        loadSettings('imprints');
    }
};

/**
 * 🚀 [V75.6] 全域事件总线无感热重载 (Zero-Reload Hotswap)
 * 解决切换版图全页白屏重载的痛点，毫秒级无缝换脑
 */
window.hotswapActiveImprint = async (id) => {
    try {
        if (typeof showNotification === 'function') {
            showNotification(`🔄 正在快速切换至版图: ${id}...`, 'info');
        } else if (typeof addAudit === 'function') {
            addAudit(`🔄 正在执行零加载无感热重载至: ${id}...`, 'info');
        }

        // 0. 关闭可能处于打开状态的编辑器与元数据详情抽屉，防范跨版图物理误写
        if (typeof window.closeEditor === 'function') window.closeEditor();
        if (typeof window.closeVaultDrawer === 'function') window.closeVaultDrawer();
        
        // 1. 重新拉取全量系统设置与品牌元数据
        if (typeof loadSettings === 'function') {
            // 记住当前的设置 Tab
            const activeTab = document.querySelector('.s-tab.active');
            const targetTab = activeTab ? activeTab.dataset.cat : 'imprints';
            await loadSettings(targetTab);
        }
        
        // 2. 重新加载原稿文库及目录探索树
        if (typeof loadVault === 'function') {
            // 重置文库上下文状态，防范旧版图“幽灵活跃目录”污染新版图视图
            window.vaultActiveFolder = '';
            window.vaultCurrentQuery = '';
            window.vaultCurrentPage = 1;
            
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
            showNotification(`✅ 已无缝热重载至版图: ${id}`, 'success');
        } else if (typeof addAudit === 'function') {
            addAudit(`✅ 零加载热重载成功，版图: ${id}`, 'success');
        }
    } catch (err) {
        console.error("Hotswap failed, falling back to reload:", err);
        location.reload();
    }
};
