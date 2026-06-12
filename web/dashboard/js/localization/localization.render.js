/**
 * 🌍 [V57.4 → I5-Refactor] Illacme Plenipes Localization Rendering Module
 * 职责：全球分发矩阵多语种阵列 HTML 面板拼装、总控开关与级联隐藏渲染、Lite/Pro 授权旗帜渲染。
 *
 * [SOP-02 §1 拆分记录]
 *   - window.translationStyles        → localization.style.js
 *   - window.renderTranslationStyleCategory → localization.style.js
 * 本文件现专注于"翻译阵列"面板渲染（renderLocalizationCategory）。
 */

window.renderLocalizationCategory = function () {
    const i18n = window.settingsData.i18n_settings || {};
    const isEnabled = i18n.enabled !== false; // 默认为 true
    const sourceLangStr = i18n.source?.lang_code || 'auto';
    const targets = (i18n.targets || []).map(t => typeof t === 'string' ? t : t.lang_code);
    const isLicensed = window.settingsData._is_licensed || false;

    // 🚀 [V57.4] 完美支持授权限制：如果是非授权社区版，强力规整只激活前 1 个选中的语种卡片，其余在界面上自愈为锁定态
    const activeTargets = (!isLicensed && targets.length > 1) ? [targets[0]] : targets;

    const availableLangs = window.availableLangs || [];

    // 🚀 [V57.4] 渲染物理多语言总开关
    const enabledSwitchHtml = window.renderSettingsItem(
        '多语言翻译矩阵', 
        'i18n_settings.enabled', 
        isEnabled, 
        'checkbox', 
        {
            onchange: 'window.syncI18nEnabled(this.checked)',
            description: '控制多语言与全域 AI 翻译的开关。关闭后，发布流水线将挂起所有 AI 翻译作业，仅发布源原稿。'
        }
    );

    return `
        <div class="full-width">
            <div class="section-header"><h3>🌍 全球分发矩阵 (Global Matrix)</h3></div>
            <p class="section-desc">配置全域内容的物理分发语种映射。每一项激活的语种都将触发一次算力原子的物理加工。</p>
            
            <!-- 1. 授权等级模块（最顶部） -->
            <div class="license-banner" style="margin-bottom: 1.5rem;">
                <div class="license-info">
                    <h4>授权等级: ${isLicensed ? '主权专业版' : '社区标准版'}</h4>
                    <p>${isLicensed ? '已解锁无限语种并行分发矩阵。' : '当前限制 1 个目标语种，升级专业版解锁全球全量分发。'}</p>
                </div>
                <div class="badge" style="background: var(--accent-secondary); color: var(--bg-solid, #000000); font-weight: 800; padding: 4px 12px; border-radius: 20px;">${isLicensed ? 'PRO' : 'LITE'}</div>
            </div>

            <!-- 2. 源内容语种（上移并常驻，不受开关控制） -->
            <div class="settings-group" style="margin-bottom: 2rem;">
                <h4>🎯 源内容语种 (Source Sovereignty)</h4>
                ${window.renderSettingsItem('主出版语种', 'i18n_settings.source.lang_code', sourceLangStr, 'select', {
                    items: [
                        { value: 'auto', text: '✨ 自动探测 (Auto Detect)' },
                        ...availableLangs.map(l => ({ value: l.code, text: `${l.icon} ${l.name}` }))
                    ],
                    onchange: 'syncI18nSource(this.value)'
                })}
                ${window.renderSettingsItem('主语言路径前缀强制化', 'i18n_settings.force_source_prefix', i18n.force_source_prefix || false, 'checkbox', {
                    onchange: 'window.syncI18nForcePrefix(this.checked)',
                    description: '决定主语言（如中文）在发布后是否拥有独立的路径前缀（如 /zh/）。开启后，所有语种将拥有完全对称的路径结构。'
                })}
            </div>

            <!-- 3. 多语言翻译矩阵开关总控闸 -->
            <div id="i18n-enable-control-group" class="settings-group" style="margin-bottom: 2rem;">
                ${enabledSwitchHtml}
            </div>
            
            <!-- 4. 目标分发阵列（仅当 isEnabled 为开启时才渲染显示） -->
            ${isEnabled ? `
                <div id="target-dissemination-group" style="margin-top: 2.5rem;">
                    <div class="section-header">
                        <h4>🛰️ 目标分发阵列 (Target Dissemination)</h4>
                    </div>
                    <div class="lang-matrix">
                        ${availableLangs
                            .filter(l => sourceLangStr === 'auto' || l.code !== sourceLangStr)
                            .map(l => {
                                const isSelected = activeTargets.includes(l.code);
                                const isLocked = !isLicensed && !isSelected && activeTargets.length >= 1;
                                return `
                                            <div class="lang-card ${isSelected ? 'active' : ''} ${isLocked ? 'locked' : ''}" 
                                                 onclick="window.toggleI18nTarget(this, '${l.code}')">
                                                <span style="font-size: 1.5rem;">${l.icon}</span>
                                                <div style="display: flex; flex-direction: column; gap: 2px;">
                                                    <span style="font-size: 0.9rem; font-weight: 600; color: var(--text-bright, #ffffff);">${l.name}</span>
                                                    <span style="font-size: 0.65rem; color: var(--text-dim);">${l.code.toUpperCase()}</span>
                                                </div>
                                            </div>`;
                            }).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
};
