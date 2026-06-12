/**
 * ⚙️ [V57.0] Illacme Plenipes System & Governance Module
 * 职责：系统设置、基础信息管理与安全审计。
 * 注：装帧主题、出版模式、翻译风格与治理准入逻辑已拆分至独立模块。
 */

window.switchToSettingsTab = (catName) => {
    const tab = document.querySelector(`.s-tab[data-cat="${catName}"]`);
    if (tab) tab.click();
};

// 1. 系统设置加载器
window.loadSettings = async (targetCat = 'general') => {
    // 🚀 [V55.21] 物理状态先行：在异步加载前先对正侧边栏标签状态
    document.querySelectorAll('.s-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.cat === targetCat);
        tab.onclick = () => {
            document.querySelectorAll('.s-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            renderSettingsCategory(tab.dataset.cat);
            if (tab.dataset.cat === 'general' && typeof window.refreshCacheStats === 'function') {
                window.refreshCacheStats();
            }
            const c = document.querySelector('.view-panel.active .tab-content-area');
            if (c) c.scrollTop = 0;
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
    if (targetCat === 'general' && typeof window.refreshCacheStats === 'function') {
        window.refreshCacheStats();
    }
};

// 🚀 [V57.3] 动态更新设置选项卡的多语言状态信标与锁标识
window.updateSettingsTabsStatus = () => {
    const isEnabled = window.settingsData?.i18n_settings?.enabled !== false;
    document.querySelectorAll('.s-tab').forEach(tab => {
        if (tab.dataset.cat === 'localization') {
            tab.innerHTML = isEnabled ? '<span class="tab-icon">🌍</span> 翻译阵列' : '<span class="tab-icon" style="opacity: 0.5;">🌍</span> <span style="opacity: 0.7;">翻译阵列 (已关闭)</span>';
        }
        if (tab.dataset.cat === 'translation_style') {
            tab.innerHTML = isEnabled ? '<span class="tab-icon">🎭</span> 翻译风格' : '<span class="tab-icon" style="opacity: 0.5;">🔒</span> <span style="color: var(--text-dim); text-decoration: line-through; opacity: 0.65;">翻译风格</span>';
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
        case 'slug_settings':
            html = typeof renderSlugSettingsCategory === 'function' ? renderSlugSettingsCategory() : '<div class="empty-state">模块加载中...</div>';
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

    if (window._shouldScrollToTopAfterThemeSwitch) {
        window._shouldScrollToTopAfterThemeSwitch = false;
        setTimeout(() => {
            const container = document.querySelector('.view-panel.active .tab-content-area');
            if (container) {
                container.scrollTop = 0;
                container.scrollTo({ top: 0, behavior: 'smooth' });
            }
            window.scrollTo({ top: 0, behavior: 'smooth' });
            document.documentElement.scrollTop = 0;
            document.body.scrollTop = 0;
        }, 80);
    }
    
    // 🚀 [V55.8] 核心能见度治理：统一管理不需要显示“全局保存”按钮的页面
    const saveBtn = document.getElementById('btn-save-settings');
    if (saveBtn) {
        const noSaveTabs = ['imprints', 'modes', 'localization', 'guardrails'];
        saveBtn.style.display = noSaveTabs.includes(cat) ? 'none' : 'flex';
    }
};

// 2. 配置保存
window.saveAllSettings = async () => {
    addAudit("💾 正在打包全量主权配置快照...");
    
    // 🚚 [BlockCache] 检测缓存分级或目录变更
    let migrateCache = false;
    if (window.initialSettingsState) {
        try {
            const initialObj = JSON.parse(window.initialSettingsState);
            const oldShardLevels = initialObj['block_cache_shard_levels'];
            const newShardLevels = window.settingsData.block_cache_shard_levels;
            const oldCacheDir = initialObj['block_cache_dir'];
            const newCacheDir = window.settingsData.block_cache_dir;

            const levelsChanged = oldShardLevels !== undefined && oldShardLevels !== newShardLevels;
            const dirChanged = oldCacheDir !== undefined && oldCacheDir !== newCacheDir;

            if (levelsChanged || dirChanged) {
                if (typeof Swal !== 'undefined') {
                    const result = await Swal.fire({
                        title: '⚠️ 检测到缓存配置变更',
                        html: `您已修改段落缓存配置：<br>` +
                              (levelsChanged ? `• 目录分级: <b>${oldShardLevels}级</b> ➡️ <b>${newShardLevels}级</b><br>` : '') +
                              (dirChanged ? `• 存储目录: <b>${oldCacheDir || '默认'}</b> ➡️ <b>${newCacheDir || '默认'}</b><br>` : '') +
                              `<br>为了避免已有翻译缓存失效导致重复请求大模型，建议对已有缓存进行物理迁移。是否执行迁移？`,
                        icon: 'warning',
                        showCancelButton: true,
                        showDenyButton: true,
                        background: 'hsla(236, 37%, 8%, 0.95)',
                        color: 'var(--text-bright, #ffffff)',
                        confirmButtonText: '🚚 迁移并保存 (推荐)',
                        denyButtonText: '⚙️ 仅保存配置',
                        cancelButtonText: '❌ 取消',
                        customClass: {
                            popup: 'glass-panel',
                            confirmButton: 'primary-btn glow-btn',
                            denyButton: 'secondary-btn',
                            cancelButton: 'danger-btn'
                        }
                    });
                    
                    if (result.isDismissed) {
                        addAudit("❌ 已取消保存配置。", 'info');
                        return;
                    }
                    if (result.isConfirmed) {
                        migrateCache = true;
                    }
                } else {
                    migrateCache = confirm("⚠️ 检测到段落缓存配置变更。是否在保存的同时物理迁移已有缓存文件？\n\n【确定】：迁移并保存\n【取消】：仅保存配置（原缓存会失效）");
                }
            }
        } catch (err) {
            console.error('[BlockCache] 预检变更异常:', err);
        }
    }

    const full = window.flattenObject(window.settingsData), payload = {};
    Object.keys(full).forEach(k => {
        if (!k.split('.').some(p => p.startsWith('_'))) payload[k] = full[k];
    });
    
    const url = `/api/config/update?migrate_cache=${migrateCache}`;
    const res = await apiFetch(url, {
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
                if (activeTab.dataset.cat === 'general' && typeof window.refreshCacheStats === 'function') {
                    window.refreshCacheStats();
                }
            }
            // 🚀 [V74.9] 全域对正：即时刷新侧边栏上下文
            if (typeof refreshGovernanceContext === 'function') {
                await refreshGovernanceContext();
            }
            if (window.SovereignAgent && typeof window.SovereignAgent.initModelCapabilities === 'function') {
                window.SovereignAgent.initModelCapabilities();
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
                    ${renderSettingsItem('段落缓存存储目录', 'block_cache_dir', data.block_cache_dir || '', 'text', {
                        placeholder: '默认为空（自愈退避至项目根目录下的隐藏目录 .plenipes/blocks/）',
                        description: '跨版图共享段落缓存物理存储根目录。支持自定义重定向以实现在任意版图和任意 SSG 主题之间共用。'
                    })}
                    ${renderSettingsItem('段落缓存目录分级', 'block_cache_shard_levels', data.block_cache_shard_levels ?? 0, 'select', {
                        items: [
                            {value: 0, text: '📂 不分级 (如 blocks/lang/style/hash.txt)'},
                            {value: 1, text: '📂 一级前缀分流 (如 blocks/lang/style/ab/hash.txt)'},
                            {value: 2, text: '📂 二级前缀分流 (如 blocks/lang/style/ab/cd/hash.txt)'},
                            {value: 3, text: '📂 三级前缀分流 (如 blocks/lang/style/ab/cd/ef/hash.txt)'}
                        ],
                        onchange: `window.updateConfigField('block_cache_shard_levels', parseInt(this.value))`,
                        description: '通过分切段落原文哈希前缀的字符数进行多级目录分流，避免单个目录包含海量碎片文件导致的 IO 性能下降。'
                    })}
                </div>
            </div>

            <div class="settings-group mt-large">
                <h4>🧰 段落缓存治理中枢 (Block Cache Hub)</h4>
                <p class="section-desc" style="font-size: 0.8rem; opacity: 0.85; margin-bottom: 12px;">实时盘点和管理跨版图共享段落翻译缓存的占用状态并执行搬移和清理。</p>
                <div class="settings-grid" style="grid-template-columns: 1fr 1fr; gap: 20px; background: rgba(255,255,255,0.02); padding: 15px; border-radius: 6px; border: 1px dashed rgba(255,255,255,0.08);">
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                        <div style="font-size: 0.85rem; opacity: 0.75;">缓存状态盘点：</div>
                        <div style="font-size: 0.95rem; font-weight: bold; color: var(--accent, #00ff88);" id="cache-stats-count">正在统计...</div>
                        <div style="font-size: 0.95rem; font-weight: bold; color: var(--accent, #00ff88);" id="cache-stats-size">正在统计...</div>
                    </div>
                    <div style="display: flex; flex-direction: column; justify-content: center; gap: 10px;">
                        <div style="display: flex; gap: 10px;">
                            <button type="button" class="primary-btn glow-btn" onclick="window.manualMigrateCache()" style="padding: 6px 14px; font-size: 0.75rem; height: 32px; line-height: 14px;">🚚 物理分级迁移</button>
                            <button type="button" class="danger-btn" onclick="window.clearBlockCacheAll()" style="padding: 6px 14px; font-size: 0.75rem; height: 32px; line-height: 14px;">🗑️ 清空所有缓存</button>
                        </div>
                    </div>
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
                        description: '是否记录每一次网页 and API 访问（包含心跳请求）。建议关闭以防终端频繁被 stats 心跳刷屏。'
                    })}
                    ${renderSettingsItem('AI 并发排队超时 (秒)', 'system.resilience.ai_semaphore_timeout', data.system?.resilience?.ai_semaphore_timeout ?? 3600, 'number', {
                        description: '翻译在高并发且算力满载时，在本地队列中等待获取执行资源的最长等待秒数。如果任务在队列中积压超时将抛出 AI_SEMAPHORE_TIMEOUT，建议设置为 3600 秒以上以防任务被提前取消。'
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
    
    setTimeout(() => {
        if (typeof window.loadAndRenderConfigAudit === 'function') {
            window.loadAndRenderConfigAudit();
        }
    }, 50);

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

            <div id="config-audit-topology-container" class="mt-large"></div>
        </div>
    `;
}

window.refreshCacheStats = async () => {
    const elCount = document.getElementById('cache-stats-count');
    const elSize = document.getElementById('cache-stats-size');
    if (!elCount || !elSize) return;
    
    elCount.innerText = '正在统计...';
    elSize.innerText = '正在统计...';
    
    try {
        const stats = await apiFetch('/api/system/cache/stats');
        if (stats) {
            elCount.innerText = (stats.file_count || 0) + ' 个缓存段落';
            const sizeMB = ((stats.size_bytes || 0) / (1024 * 1024)).toFixed(2);
            elSize.innerText = sizeMB + ' MB';
        }
    } catch (err) {
        elCount.innerText = '获取失败';
        elSize.innerText = '获取失败';
        console.error('获取缓存统计失败:', err);
    }
};

window.manualMigrateCache = async () => {
    if (typeof Swal === 'undefined') return;
    
    const initialObj = window.initialSettingsState ? JSON.parse(window.initialSettingsState) : {};
    const oldShardLevels = initialObj['block_cache_shard_levels'] ?? 1;
    const newShardLevels = window.settingsData.block_cache_shard_levels ?? 1;
    const oldCacheDir = initialObj['block_cache_dir'] ?? null;
    const newCacheDir = window.settingsData.block_cache_dir ?? null;

    const result = await Swal.fire({
        title: '🚚 手动触发段落缓存物理迁移',
        html: `系统将根据当前的配置状态，将缓存从旧分级搬移到新分级中：<br><br>` +
              `• 旧配置：<b>${oldCacheDir || '默认'}</b> (L<b>${oldShardLevels}</b>)<br>` +
              `• 新配置：<b>${newCacheDir || '默认'}</b> (L<b>${newShardLevels}</b>)<br><br>` +
              `此操作将立即执行，请确认是否继续？`,
        icon: 'info',
        showCancelButton: true,
        background: 'hsla(236, 37%, 8%, 0.95)',
        color: 'var(--text-bright, #ffffff)',
        confirmButtonText: '立即迁移',
        cancelButtonText: '取消',
        customClass: {
            popup: 'glass-panel',
            confirmButton: 'primary-btn glow-btn',
            cancelButton: 'danger-btn'
        }
    });
    
    if (result.isConfirmed) {
        addAudit("🚚 正在手动触发段落缓存迁移任务...");
        const res = await apiFetch('/api/governance/cache/migrate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                old_levels: oldShardLevels,
                new_levels: newShardLevels,
                old_dir: oldCacheDir,
                new_dir: newCacheDir
            })
        });
        if (res && res.status === 'success') {
            Swal.fire({
                toast: true,
                position: 'top-end',
                icon: 'success',
                title: '缓存迁移完成',
                showConfirmButton: false,
                timer: 3000
            });
            addAudit("✅ 段落缓存物理迁移已成功完成。", 'success');
            await window.refreshCacheStats();
        } else {
            Swal.fire('迁移失败', res ? res.message : '未知原因', 'error');
        }
    }
};

window.clearBlockCacheAll = async () => {
    if (typeof Swal === 'undefined') return;
    
    const result = await Swal.fire({
        title: '🗑️ 危险：清空段落缓存',
        text: '确定要物理删除所有翻译后的段落缓存文件吗？这会导致下一次翻译时，所有段落均需重新请求大模型进行翻译！',
        icon: 'warning',
        showCancelButton: true,
        background: 'hsla(236, 37%, 8%, 0.95)',
        color: 'var(--text-bright, #ffffff)',
        confirmButtonText: '💥 确定清空 (不保留备份)',
        cancelButtonText: '取消',
        customClass: {
            popup: 'glass-panel',
            confirmButton: 'danger-btn glow-btn',
            cancelButton: 'primary-btn'
        }
    });
    
    if (result.isConfirmed) {
        addAudit("🗑️ 正在清空段落翻译缓存...");
        const res = await apiFetch('/api/governance/cache/clear', { method: 'POST' });
        if (res && res.status === 'success') {
            Swal.fire({
                toast: true,
                position: 'top-end',
                icon: 'success',
                title: '段落缓存已成功清空',
                showConfirmButton: false,
                timer: 3000
            });
            addAudit("✅ 全量段落翻译缓存已被安全物理移除。", 'success');
            await window.refreshCacheStats();
        } else {
            Swal.fire('清理失败', res ? res.message : '未知原因', 'error');
        }
    }
};
