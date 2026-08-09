/**
 * ⚙️ [V74.0] Illacme Plenipes Imprints Management Module (Hub Controller)
 * 职责：出版集团指挥中心、核心版图意志切换、物理隔离与一键注销。
 */

window.switchImprint = async (id) => {
    if (!id) return;

    if (typeof window.checkSettingsDirtyAndConfirm === 'function') {
        const proceed = await window.checkSettingsDirtyAndConfirm();
        if (!proceed) {
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('imprints');
            const selectEl = document.getElementById('imprint-select');
            if (selectEl) {
                selectEl.value = window.settingsData._active_imprint || 'default';
            }
            return;
        }
    }

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
                      '• 版图限额: 2/2 (已含 1 个默认版图 + 1 个自定义版图)<br>' +
                      '• 治理限制: 社区版最多允许创建 1 个自定义出版版图。<br><br>' +
                      '<span style="color:var(--accent-secondary)">💡 建议：升级至 [高级专业版] 以解锁多版图管理。</span>' +
                      '</div>',
                icon: 'warning',
                confirmButtonText: '了解',
                background: 'var(--card-bg)',
                color: 'var(--text-bright)',
                confirmButtonColor: 'var(--accent-primary)'
            });
        } else {
            alert("🛡️ [准入拦截]\n免费社区版限额 2 个版图 (1 个默认 + 1 个自定义)，无法继续添加。");
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
        if (window.Swal) {
            await window.Swal.fire({
                title: '🛡️ 安全拦截',
                html: `<div style="text-align:left; font-size: 0.88rem; line-height: 1.6;">无法物理抹除当前<b>处于激活状态</b>（或默认）的出版版图：<b style="color:var(--accent-secondary, #00f2fe);">${id}</b>。<br><br>💡 <b>建议：</b>请先在左上角或下方卡片中切换至其他可用版图后再行抹除。</div>`,
                icon: 'error',
                confirmButtonText: '我知道了',
                confirmButtonColor: 'var(--accent-primary, #7c3aed)',
                background: 'var(--bg-solid, #0f111a)',
                color: 'var(--text-bright, #ffffff)'
            });
        } else {
            alert(`🛡️ [安全拦截]\n无法删除当前处于激活状态（或默认）的版图 [${id}]！\n请先切换至其他可用版图后再行操作。`);
        }
        return;
    }

    if (typeof window.checkSettingsDirtyAndConfirm === 'function') {
        const proceed = await window.checkSettingsDirtyAndConfirm();
        if (!proceed) return;
    }

    // 🛡️ [物理安全防线 2] SweetAlert2 霸权防闪退确认框
    if (window.Swal) {
        const res = await window.Swal.fire({
            title: '🚨 确认物理抹除出版版图',
            html: `<div style="text-align:left; font-size: 0.88rem; line-height: 1.6;">您确定要彻底物理抹除出版版图 <b style="color:#ff4444;">[${id}]</b> 吗？<br><br>⚠️ <b>后果提示</b>：该版图下的独立样式、配置及专有产物元数据将被销毁，此物理操作不可撤销！</div>`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: '🔥 确认物理抹除',
            cancelButtonText: '取消',
            confirmButtonColor: '#ef4444',
            cancelButtonColor: '#64748b',
            background: 'var(--bg-solid, #0f111a)',
            color: 'var(--text-bright, #ffffff)'
        });
        if (!res.isConfirmed) return;
    } else {
        if (!confirm(`🚨 危险操作！\n确认要物理抹除出版版图 [${id}] 吗？`)) return;
    }

    const res = await apiFetch('/api/imprints/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: id })
    });

    if (res && res.success) {
        if (typeof addAudit === 'function') addAudit(`🗑️ 版图已物理抹除: ${id}`, "warning");
        if (typeof window.loadSettings === 'function') window.loadSettings('imprints');
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
            const targetTab = window.currentActiveSettingsSubCat || 'imprints';
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
        
        // 5. 🚀 [V100.7] 全域视图条件热刷新 (根据用户当前停留在的视图面板同步更新数据)
        if (window.currentView === 'compute' && typeof window.loadComputeCenter === 'function') {
            await window.loadComputeCenter();
        } else if (window.currentView === 'plugins' && typeof window.loadPlugins === 'function') {
            await window.loadPlugins();
        } else if (window.currentView === 'tower' && typeof window.loadTowerCenter === 'function') {
            window.loadTowerCenter();
        } else if (window.currentView === 'analytics' && typeof window.loadAnalyticsCenter === 'function') {
            window.loadAnalyticsCenter();
        }
        
        // 6. 交互徽章特制霓虹微光脉冲
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
