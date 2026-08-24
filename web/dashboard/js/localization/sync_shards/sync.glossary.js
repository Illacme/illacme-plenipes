/**
 * 🌍 [V55.5] Illacme Plenipes Localization Sync - Glossary Shard
 * 职责：专有名词保护术语增删、多语种 Tab 切换、以及一键清空语种词库弹窗交互。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
 */

// 🚀 [V75.0] 新增专有名词保护词 (适配多语种对准)
window.addGlossaryItem = async () => {
    const srcInput = document.getElementById('glossary-src-input');
    const dstInput = document.getElementById('glossary-dst-input');
    if (!srcInput || !dstInput) return;

    const src = srcInput.value.trim();
    const dst = dstInput.value.trim();

    if (!src || !dst) {
        if (typeof showNotification === 'function') {
            showNotification('⚠️ 原稿词汇与保护译词均不能为空', 'warning');
        } else {
            alert('⚠️ 原稿词汇与保护译词均不能为空');
        }
        return;
    }

    const currentLang = window.currentGlossaryLang || 'en';
    const gov = window.settingsData?.translation?.governance || {};
    const glossary = { ...(gov.glossary || {}) };

    if (!glossary[currentLang]) {
        glossary[currentLang] = {};
    } else {
        glossary[currentLang] = { ...glossary[currentLang] };
    }
    glossary[currentLang][src] = dst;

    if (typeof window.syncTranslationGovernanceField === 'function') {
        await window.syncTranslationGovernanceField('translation.governance.glossary', glossary, true);
    }

    srcInput.value = '';
    dstInput.value = '';
};

// 🚀 [V75.0] 删除专有名词保护词 (适配多语种对准)
window.removeGlossaryItem = async (src) => {
    const currentLang = window.currentGlossaryLang || 'en';
    const gov = window.settingsData?.translation?.governance || {};
    const glossary = { ...(gov.glossary || {}) };

    if (glossary[currentLang]) {
        glossary[currentLang] = { ...glossary[currentLang] };
        delete glossary[currentLang][src];
    }

    if (typeof window.syncTranslationGovernanceField === 'function') {
        await window.syncTranslationGovernanceField('translation.governance.glossary', glossary, true);
    }
};

// 🚀 [V75.5] 切换专有名词术语编辑的语种 Tab
window.switchGlossaryLang = (code) => {
    window.currentGlossaryLang = code;
    window.currentGlossarySearchQuery = "";
    window.currentGlossaryPage = 1;
    const panelEl = document.getElementById('loc-panel-glossary');
    if (panelEl && typeof window.renderGlossaryCategory === 'function') {
        panelEl.innerHTML = window.renderGlossaryCategory();
    } else if (typeof renderSettingsCategory === 'function') {
        renderSettingsCategory('glossary');
    }
};

// 🚀 [V75.6] 一键清空当前选定语种下的所有名词防护术语
window.clearGlossaryCurrentLang = async () => {
    if (typeof Swal === 'undefined') return;
    const currentLang = window.currentGlossaryLang || 'en';
    const result = await Swal.fire({
        title: '🧹 确认清空术语表？',
        text: `确定要彻底清空当前语种 [${currentLang.toUpperCase()}] 下的所有专有名词防护术语吗？此操作无法撤销。`,
        icon: 'warning',
        showCancelButton: true,
        background: 'hsla(236, 37%, 8%, 0.95)',
        color: 'var(--text-bright, #ffffff)',
        confirmButtonText: '💥 确定清空',
        cancelButtonText: '❌ 取消',
        customClass: {
            popup: 'glass-panel',
            confirmButton: 'danger-btn glow-btn',
            cancelButton: 'primary-btn'
        }
    });

    if (result.isConfirmed) {
        const gov = window.settingsData?.translation?.governance || {};
        const glossary = { ...(gov.glossary || {}) };
        glossary[currentLang] = {};

        if (typeof addAudit === 'function') addAudit(`🧹 正在清空 [${currentLang.toUpperCase()}] 的防护术语表...`);
        if (typeof window.syncTranslationGovernanceField === 'function') {
            await window.syncTranslationGovernanceField('translation.governance.glossary', glossary);
        }
        window.currentGlossaryPage = 1;
        if (typeof window.refreshGlossaryUI === 'function') {
            window.refreshGlossaryUI();
        }

        Swal.fire({
            title: '🎉 已清空',
            text: `当前语种 [${currentLang.toUpperCase()}] 的保护词表已成功清空！`,
            icon: 'success',
            background: 'hsla(236, 37%, 8%, 0.95)',
            color: 'var(--text-bright, #ffffff)',
            timer: 1500,
            showConfirmButton: false
        });
    }
};
