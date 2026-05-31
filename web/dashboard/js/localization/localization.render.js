/**
 * 🌍 [V55.5] Illacme Plenipes Localization Rendering Module
 * 职责：全球分发矩阵多语种阵列 HTML 面板拼装、Lite/Pro 授权旗帜渲染、以及全域翻译语感风格 Prompt 模板与方言矩阵网格渲染。
 */

window.renderLocalizationCategory = function () {
    const i18n = window.settingsData.i18n_settings || {};
    const sourceLangStr = i18n.source?.lang_code || 'auto';
    const targets = (i18n.targets || []).map(t => typeof t === 'string' ? t : t.lang_code);
    const isLicensed = window.settingsData._is_licensed || false;

    const availableLangs = window.availableLangs || [];

    return `
        <div class="full-width">
            <div class="section-header"><h3>🌍 全球分发矩阵 (Global Matrix)</h3></div>
            <p class="section-desc">配置全域内容的物理分发语种映射。每一项激活的语种都将触发一次算力原子的物理加工。</p>
            
            <div class="license-banner">
                <div class="license-info">
                    <h4>授权等级: ${isLicensed ? '主权专业版' : '社区标准版'}</h4>
                    <p>${isLicensed ? '已解锁无限语种并行分发矩阵。' : '当前限制 1 个目标语种，升级专业版解锁全球全量分发。'}</p>
                </div>
                <div class="badge" style="background: var(--accent-secondary); color: var(--bg-solid, #000000); font-weight: 800; padding: 4px 12px; border-radius: 20px;">${isLicensed ? 'PRO' : 'LITE'}</div>
            </div>

            <div class="settings-group">
                <h4>🎯 源内容语种 (Source Sovereignty)</h4>
                ${window.renderSettingsItem('主出版语种', 'i18n_settings.source.lang_code', sourceLangStr, 'select', {
        items: [
            { value: 'auto', text: '✨ 自动探测 (Auto Detect)' },
            ...availableLangs.map(l => ({ value: l.code, text: `${l.icon} ${l.name}` }))
        ],
        onchange: 'syncI18nSource(this.value)'
    })}
            </div>

            <div style="margin-top: 2.5rem;">
                <div class="section-header"><h4>🛰️ 目标分发阵列 (Target Dissemination)</h4></div>
                <div class="lang-matrix">
                    ${availableLangs
            .filter(l => sourceLangStr === 'auto' || l.code !== sourceLangStr)
            .map(l => {
                const isSelected = targets.includes(l.code);
                const isLocked = !isLicensed && !isSelected && targets.length >= 1;
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
        </div>
    `;
};

window.renderTranslationStyleCategory = () => {
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
