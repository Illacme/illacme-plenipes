/**
 * 🌍 [V57.4] Illacme Plenipes Localization Rendering Module
 * 职责：全球分发矩阵多语种阵列 HTML 面板拼装、总控开关与级联隐藏渲染、Lite/Pro 授权旗帜渲染、以及未启用时的警示面板渲染。
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

window.renderTranslationStyleCategory = () => {
    const i18n = window.settingsData.i18n_settings || {};
    const isEnabled = i18n.enabled !== false; // 默认为 true

    // 🚀 [V57.3] 若引擎未激活，物理拦截并展示设计感强烈的提示面板
    if (!isEnabled) {
        return `
            <div class="full-width">
                <div class="section-header"><h3>🎭 全域翻译风格 (Universal Style)</h3></div>
                <div class="glass-panel" style="padding: 40px 30px; text-align: center; color: var(--text-dim); display: flex; flex-direction: column; align-items: center; gap: 15px; border-radius: 12px; background: rgba(255, 255, 255, 0.02); border: 1px dashed var(--glass-border);">
                    <span style="font-size: 3.5rem; filter: drop-shadow(0 0 10px rgba(0, 242, 255, 0.15));">🌍</span>
                    <h4 style="color: var(--text-bright, #ffffff); margin: 0; font-size: 1.2rem; font-weight: 700; letter-spacing: 0.5px;">多语言翻译引擎未启用</h4>
                    <p style="font-size: 0.85rem; max-width: 420px; line-height: 1.6; margin: 0; color: var(--text-dim);">
                        当前品牌的多语言翻译矩阵已关闭。在此状态下无法调整翻译风格。如需微调 Prompt 模板，请先前往 <strong>🌍 翻译阵列</strong> 开启多语言总开关。
                    </p>
                </div>
            </div>
        `;
    }

    const prompts = window.settingsData.translation?.prompts || {};

    return `
        <div class="full-width">
            <div class="section-header"><h3>🎭 全域翻译风格 (Universal Style)</h3></div>
            <p style="color: var(--text-dim); font-size: 0.85rem; margin-bottom: 1.5rem;">设定当前品牌在全球化分发中所采用的语感模板，强制对正全量算力输出。</p>
            
            <div class="settings-grid">
                <div class="settings-group">
                    <h4>🌐 风格预设 (Preset Templates)</h4>
                    <div style="display: flex; gap: 15px; align-items: center; margin-bottom: 10px;">
                        <select id="style-selector" class="setting-input">
                            <option value="professional">商务专业 (Professional) - 正式、严谨</option>
                            <option value="casual">活泼随性 (Casual) - 自然、口语</option>
                            <option value="literal">精准直译 (Literal) - 忠实、结构</option>
                        </select>
                        <button class="primary-btn" onclick="applyTranslationStyle()" style="white-space: nowrap;">⚡ 应用</button>
                    </div>
                    
                    <div class="prompt-container">
                        <div class="prompt-box" id="prompt-preview-translate">
                            ${prompts.translate_system || '正在提取物理 Prompt...'}
                        </div>
                        <div class="settings-grid" style="grid-template-columns: 1fr 1fr; gap: 15px;">
                            <div class="prompt-box" id="prompt-preview-title">
                                标题: ${prompts.title_system || 'Default'}
                            </div>
                            <div class="prompt-box" id="prompt-preview-meta">
                                元数据: ${prompts.metadata_system || 'Default'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
};
