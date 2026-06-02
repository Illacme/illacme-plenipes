/**
 * ⚙️ [V57.0] Illacme Plenipes System & Governance Module
 * 职责：系统设置、基础信息管理与安全审计。
 * 注：装帧主题、出版模式、翻译风格与治理准入逻辑已拆分至独立模块。
 */

// 1. 系统设置加载器
window.loadSettings = async (targetCat = 'general') => {
    // 🚀 [V55.21] 物理状态先行：在异步加载前先对正侧边栏标签状态
    document.querySelectorAll('.s-tab').forEach(tab => {
        if (tab.dataset.cat === targetCat) tab.classList.add('active');
        else tab.classList.remove('active');
        
        tab.onclick = () => {
            document.querySelectorAll('.s-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            renderSettingsCategory(tab.dataset.cat);
            const container = document.querySelector('.tab-content-area');
            if (container) container.scrollTop = 0;
        };
    });

    const formEl = document.getElementById('settings-form');
    if (formEl) formEl.innerHTML = '<div class="loading">正在拉取全量主权配置与治理元数据...</div>';

    const res = await apiFetch('/api/system/config');
    const imprints = await apiFetch('/api/imprints');
    const slotsRes = await apiFetch('/api/system/theme/slots');
    const vaultRes = await apiFetch('/api/vault/list');
    if (!res) return;

    window.settingsData = res.config || res;
    window.governanceRules = res.governance_rules || res._governance_rules;
    window.settingsData._imprints = imprints ? imprints.imprints : [];
    window.settingsData._active_imprint = imprints ? imprints.active : 'default';
    window.settingsData._is_licensed = res._is_licensed || false;
    window.settingsData._theme_slots = (slotsRes && slotsRes.slots) ? slotsRes.slots : {};
    window.settingsData._directories = (vaultRes && vaultRes.directories) ? vaultRes.directories : [];

    const stats = await apiFetch('/api/imprints/stats');
    window.settingsData._imprint_stats = stats || {};

    // 🚀 [V57.1] 初始化基准状态快照，用于脏检查
    if (typeof window.getCleanConfig === 'function') {
        window.initialSettingsState = window.getCleanConfig(window.settingsData);
        if (typeof window.checkSettingsDirty === 'function') {
            window.checkSettingsDirty();
        }
    }

    // 🚀 [V57.3] 动态同步刷新侧边栏子项多语言指示器与锁定锁
    if (typeof window.updateSettingsTabsStatus === 'function') {
        window.updateSettingsTabsStatus();
    }

    renderSettingsCategory(targetCat);
};

// 🚀 [V57.3] 动态更新设置选项卡的多语言状态信标与锁标识
window.updateSettingsTabsStatus = () => {
    const i18n = window.settingsData?.i18n_settings || {};
    const isEnabled = i18n.enabled !== false;
    
    document.querySelectorAll('.s-tab').forEach(tab => {
        if (tab.dataset.cat === 'localization') {
            tab.innerHTML = isEnabled 
                ? '<span class="tab-icon">🌍</span> 翻译阵列' 
                : '<span class="tab-icon" style="opacity: 0.5;">🌍</span> <span style="opacity: 0.7;">翻译阵列 (已关闭)</span>';
        }
        if (tab.dataset.cat === 'translation_style') {
            tab.innerHTML = isEnabled 
                ? '<span class="tab-icon">🎭</span> 翻译风格' 
                : '<span class="tab-icon" style="opacity: 0.5;">🔒</span> <span style="color: var(--text-dim); text-decoration: line-through; opacity: 0.65;">翻译风格</span>';
        }
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
        case 'route_matrix':
            html = typeof renderRouteMatrixCategory === 'function' ? renderRouteMatrixCategory() : '<div class="empty-state">模块加载中...</div>';
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
        const noSaveTabs = ['imprints', 'modes', 'translation_style', 'localization', 'guardrails', 'route_matrix'];
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
        addAudit("✅ 全局主权配置已成功保存并即刻生效。", 'success');
        if (res.active_config) {
            window.settingsData = { ...window.settingsData, ...res.active_config };
            
            // 🚀 [V57.1] 同步新的基准状态并重置按钮
            if (typeof window.getCleanConfig === 'function') {
                window.initialSettingsState = window.getCleanConfig(window.settingsData);
                if (typeof window.checkSettingsDirty === 'function') {
                    window.checkSettingsDirty();
                }
            }

            const activeTab = document.querySelector('.s-tab.active');
            if (activeTab && typeof renderSettingsCategory === 'function') {
                renderSettingsCategory(activeTab.dataset.cat);
            }
            // 🚀 [V74.9] 全域对正：即时刷新侧边栏上下文
            if (typeof refreshGovernanceContext === 'function') {
                await refreshGovernanceContext();
            }
        }
    } else {
        addAudit(`❌ 配置保存失败: ${res ? res.error : '未知故障'}`, 'error');
    }
};

// 3. 基础信息渲染
function renderGeneralCategory() {
    const data = window.settingsData;
    return `
        <div class="full-width">
            <div class="section-header"><h3>ℹ️ 基础信息 (General Information)</h3></div>
            <p class="section-desc">管理当前出版版图的核心身份标识与全域元数据。</p>
            
            <div class="settings-group">
                <h4>🏷️ 品牌与站点身份 (Brand & Site Identity)</h4>
                <div class="settings-grid">
                    ${renderSettingsItem('版图展示名称', 'imprint_name', data.imprint_name || '')}
                    ${renderSettingsItem('版图描述', 'imprint_description', data.imprint_description || '')}
                    ${renderSettingsItem('全局站点名称', 'site_name', data.site_name || '', 'text', {placeholder: '未填则自愈 fallback 为版图展示名称'})}
                    ${renderSettingsItem('全局站点描述', 'site_description', data.site_description || '', 'text', {placeholder: '未填则自愈 fallback 为版图描述'})}
                    ${renderSettingsItem('全局品牌 Logo 路径', 'logo_path', data.logo_path || '', 'text', {placeholder: '例如: /static/logo.png'})}
                    ${renderSettingsItem('全局 Favicon 图标路径', 'favicon_path', data.favicon_path || '', 'text', {placeholder: '例如: /static/favicon.ico'})}
                </div>
            </div>

            <div class="settings-group mt-large">
                <h4>📖 出版合规与元数据 (Publishing Compliance & Metadata)</h4>
                <div class="settings-grid">
                    ${renderSettingsItem('主站点 URL', 'site_url', data.site_url || '')}
                    ${renderSettingsItem('默认作者署名', 'frontmatter_defaults.author', data.frontmatter_defaults?.author || '')}
                    ${renderSettingsItem('全域版权声明', 'frontmatter_defaults.copyright', data.frontmatter_defaults?.copyright || '© 2024 All Rights Reserved')}
                    ${renderSettingsItem('出版许可证 (License)', 'frontmatter_defaults.license', data.frontmatter_defaults?.license || 'CC BY-NC-SA 4.0')}
                </div>
            </div>

            <div class="settings-group mt-large">
                <h4>📂 数据存储与原稿适配 (Storage & Dialect Adaptation)</h4>
                <div class="settings-grid">
                    ${renderSettingsItem('原稿文库路径', 'vault_root', data.vault_root || '', 'static', {
                        description: '🔒 物理主权路径在版图确立后不可变。如需迁移资产领土，请新建版图。'
                    })}
                    ${renderSettingsItem('首选解析协议', 'ingress_settings.active_dialects', data.ingress_settings?.active_dialects?.[0] || 'auto', 'select', {
                        items: [
                            {value: 'auto', text: '✨ 自动感应 (Auto-Sensing)'},
                            {value: 'obsidian', text: 'Obsidian Connector'},
                            {value: 'logseq', text: 'Logseq Adapter'},
                            {value: 'notion', text: 'Notion Sync'},
                            {value: 'typora', text: 'Typora Dialect'},
                            {value: 'mkdocs', text: 'MkDocs Standard'}
                        ],
                        onchange: `window.updateConfigField('ingress_settings.active_dialects', [this.value])`,
                        description: '定义系统如何识别原稿格式。选择“自动感应”将根据文件特征物理识别；选择特定协议则执行主权强制解析。'
                    })}
                </div>
            </div>

            <div class="settings-group mt-large">
                <h4>⚙️ 系统基座与遥测运维 (Engine Base & Telemetry)</h4>
                <div class="settings-grid">
                    ${renderSettingsItem('系统底座版本', 'version', data.version || 'V24.0', 'text', {readonly: true})}
                    ${renderSettingsItem('系统日志级别', 'system.log_level', data.system?.log_level || 'INFO', 'select', {
                        items: [
                            {value: 'DEBUG', text: 'DEBUG (全量输出)'},
                            {value: 'INFO', text: 'INFO (常规运行)'},
                            {value: 'WARNING', text: 'WARNING (仅告警)'},
                            {value: 'ERROR', text: 'ERROR (仅异常)'}
                        ],
                        description: '控制服务器后端在终端输出的日志详细程度。建议使用 WARNING 级别以保持静音。'
                    })}
                    ${renderSettingsItem('启用 HTTP 访问日志', 'system.access_log', data.system?.access_log ?? true, 'checkbox', {
                        description: '是否记录每一次网页和 API 访问（包含心跳请求）。建议关闭以防终端频繁被 stats 心跳刷屏。'
                    })}
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
