/**
 * ⚙️ [V57.0] Illacme Plenipes System & Governance Module
 * 职责：系统设置、基础信息管理与安全审计。
 * 注：装帧主题、出版模式、翻译风格与治理准入逻辑已拆分至独立模块。
 */

// 1. 系统设置加载器
window.loadSettings = async () => {
    const formEl = document.getElementById('settings-form');
    if (formEl) formEl.innerHTML = '<div class="loading">正在拉取全量主权配置与治理元数据...</div>';

    const res = await apiFetch('/api/system/config');
    const imprints = await apiFetch('/api/imprints');
    if (!res) return;

    window.settingsData = res.config || res;
    window.governanceRules = res.governance_rules || res._governance_rules;
    window.settingsData._imprints = imprints ? imprints.imprints : [];
    window.settingsData._active_imprint = imprints ? imprints.active : 'default';
    window.settingsData._is_licensed = res._is_licensed || false;

    const stats = await apiFetch('/api/imprints/stats');
    window.settingsData._imprint_stats = stats || {};

    renderSettingsCategory('general');

    document.querySelectorAll('.s-tab').forEach(tab => {
        tab.onclick = () => {
            document.querySelectorAll('.s-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            renderSettingsCategory(tab.dataset.cat);
            const container = document.querySelector('.tab-content-area');
            if (container) container.scrollTop = 0;
        };
    });
};

window.renderSettingsCategory = (cat) => {
    const formEl = document.getElementById('settings-form');
    if (!formEl) return;

    let html = '';
    switch (cat) {
        case 'general':
            html = renderGeneralCategory();
            break;
        case 'modes':
            html = typeof renderModesCategory === 'function' ? renderModesCategory() : '<div class="empty-state">模块加载中...</div>';
            break;
        case 'imprints':
            html = typeof renderImprintsCategory === 'function' ? renderImprintsCategory() : '<div class="empty-state">模块加载中...</div>';
            break;
        case 'themes':
            html = typeof renderThemesCategory === 'function' ? renderThemesCategory() : '<div class="empty-state">模块加载中...</div>';
            break;
        case 'localization':
            html = typeof renderLocalizationCategory === 'function' ? renderLocalizationCategory() : '<div class="empty-state">模块加载中...</div>';
            break;
        case 'guardrails':
            html = typeof renderGuardrailsCategory === 'function' ? renderGuardrailsCategory() : '<div class="empty-state">模块加载中...</div>';
            break;
        case 'translation_style':
            html = typeof renderTranslationStyleCategory === 'function' ? renderTranslationStyleCategory() : '<div class="empty-state">模块加载中...</div>';
            break;
        case 'compute_strategy':
            if (typeof renderComputeStrategy === 'function') {
                html = renderComputeStrategy(window.settingsData);
            }
            break;
        case 'security':
            html = renderSecurityCategory();
            break;
    }

    formEl.innerHTML = html;
    
    // 🚀 [V55.8] 核心能见度治理：统一管理不需要显示“全局保存”按钮的页面
    const saveBtn = document.getElementById('btn-save-settings');
    if (saveBtn) {
        const noSaveTabs = ['imprints', 'modes', 'translation_style', 'localization', 'guardrails'];
        saveBtn.style.display = noSaveTabs.includes(cat) ? 'none' : 'flex';
    }
};

// 2. 配置保存
window.saveAllSettings = async () => {
    addAudit("💾 正在打包全量主权配置快照...");
    
    const fullConfig = window.flattenObject(window.settingsData);
    const payload = {};
    
    Object.keys(fullConfig).forEach(key => {
        if (!key.split('.').some(part => part.startsWith('_'))) {
            payload[key] = fullConfig[key];
        }
    });

    const res = await apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res && res.status === 'success') {
        addAudit("✅ 全量主权配置已固化至物理磁盘。", 'success');
        if (res.active_config) {
            window.settingsData = { ...window.settingsData, ...res.active_config };
            const activeTab = document.querySelector('.s-tab.active');
            if (activeTab && typeof renderSettingsCategory === 'function') {
                renderSettingsCategory(activeTab.dataset.cat);
            }
        }
    } else {
        addAudit(`❌ 配置固化失败: ${res ? res.error : '未知故障'}`, 'error');
    }
};

// 3. 基础信息渲染
function renderGeneralCategory() {
    const data = window.settingsData;
    return `
        <div class="full-width">
            <div class="section-header"><h3>ℹ️ 基础信息 (General Information)</h3></div>
            <p class="section-desc">管理当前出版版图的核心身份标识与全域元数据。</p>
            
            <div class="settings-grid">
                <div class="settings-group">
                    <h4>🏛️ 版图身份 (Imprint Identity)</h4>
                    ${renderSettingsItem('版图展示名称', 'imprint_name', data.imprint_name || '')}
                    ${renderSettingsItem('版图描述', 'imprint_description', data.imprint_description || '')}
                </div>
 
                <div class="settings-group">
                    <h4>📡 出版元数据 (Publishing Metadata)</h4>
                    ${renderSettingsItem('主站点 URL', 'site_url', data.site_url || '')}
                    ${renderSettingsItem('默认作者署名', 'frontmatter_defaults.author', data.frontmatter_defaults?.author || '')}
                    ${renderSettingsItem('全域版权声明', 'frontmatter_defaults.copyright', data.frontmatter_defaults?.copyright || '© 2024 All Rights Reserved')}
                    ${renderSettingsItem('出版许可证 (License)', 'frontmatter_defaults.license', data.frontmatter_defaults?.license || 'CC BY-NC-SA 4.0')}
                </div>
            </div>
 
            <div class="settings-group mt-large">
                <h4>🧱 物理拓扑结构 (Physical Topology)</h4>
                <div class="settings-grid">
                    ${renderSettingsItem('原稿仓库路径', 'vault_root', data.vault_root || '', 'text', {readonly: true})}
                    ${renderSettingsItem('强制原稿子目录', 'i18n_settings.force_source_prefix', data.i18n_settings?.force_source_prefix || false, 'checkbox')}
                    ${renderSettingsItem('系统底座版本', 'version', data.version || 'V24.0', 'text', {readonly: true})}
                </div>
            </div>
        </div>
    `;
}
 
// 4. 安全审计渲染
function renderSecurityCategory() {
    const sys = window.settingsData?.system || {};
    const gov = window.settingsData?.governance || {};
    const rg = gov.resource_guard || { cpu_threshold: 85 };
    
    return `
        <div class="full-width">
            <div class="section-header"><h3>🛡️ 安全审计 (Security & Compliance)</h3></div>
            <p class="section-desc">配置系统安全底座与物理审计策略。</p>
            
            <div class="settings-grid">
                ${renderSettingsItem('API 访问令牌 (Token)', 'system.api_token', sys.api_token || '', 'password', {placeholder: '保持为空则不启用认证'})}
                ${renderSettingsItem('日志输出级别', 'system.log_level', sys.log_level || 'INFO', 'select', {
                    items: [
                        {value: 'DEBUG', text: 'DEBUG (全量输出)'},
                        {value: 'INFO', text: 'INFO (常规运行)'},
                        {value: 'WARNING', text: 'WARNING (仅告警)'},
                        {value: 'ERROR', text: 'ERROR (仅异常)'}
                    ]
                })}
                ${renderSettingsItem('启用资产安全审计', 'system.enable_asset_audit', sys.enable_asset_audit ?? true, 'checkbox')}
                ${renderSettingsItem('资源负载红线 (%)', 'governance.resource_guard.cpu_threshold', rg.cpu_threshold, 'number')}
            </div>
        </div>
    `;
}
