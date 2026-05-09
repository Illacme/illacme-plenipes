/**
 * 🌍 [V55.5] Illacme Plenipes Localization Module - Industrial Matrix
 * 职责：处理全量语种分发配置，执行授权栅栏与矩阵式 UI 渲染。
 */

window.renderLocalizationCategory = function() {
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
                <div class="badge" style="background: var(--accent-secondary); color: #000; font-weight: 800; padding: 4px 12px; border-radius: 20px;">${isLicensed ? 'PRO' : 'LITE'}</div>
            </div>

            <div class="settings-group">
                <h4>🎯 源内容语种 (Source Sovereignty)</h4>
                ${window.renderSettingsItem('主出版语种', 'i18n_settings.source.lang_code', sourceLangStr, 'select', {
                    items: [
                        {value: 'auto', text: '✨ 自动探测 (Auto Detect)'},
                        ...availableLangs.map(l => ({value: l.code, text: `${l.icon} ${l.name}`}))
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
                                    <span style="font-size: 0.9rem; font-weight: 600; color: #fff;">${l.name}</span>
                                    <span style="font-size: 0.65rem; color: var(--text-dim);">${l.code.toUpperCase()}</span>
                                </div>
                            </div>`;
                    }).join('')}
                </div>
            </div>
        </div>
    `;
};

window.syncI18nSource = async (val) => {
    if (typeof addAudit === 'function') addAudit(`🌍 正在固化源内容语种: ${val}...`);
    
    const res = await apiFetch('/api/config/update', { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'i18n_settings.source.lang_code': val }) 
    });

    if (res && res.status === 'success') {
        if (typeof addAudit === 'function') addAudit(`✅ 源语种主权已确立。`, "success");
        // 物理拉取最新状态
        const freshConfig = await apiFetch('/api/system/config?level=merged');
        if (freshConfig) {
            window.settingsData = freshConfig;
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('localization');
        }
    }
};

window.toggleI18nTarget = async (el, code) => {
    // 🚀 [V55.7] 权威数据源：不再依赖 DOM 状态，直接从内存抓取
    const i18n = window.settingsData.i18n_settings || {};
    const currentTargets = (i18n.targets || []).map(t => typeof t === 'string' ? t : t.lang_code);
    const isLicensed = window.settingsData._is_licensed || false;
    
    console.log("[I18n Sync] Current Targets:", currentTargets, "Toggling:", code, "Licensed:", isLicensed);

    let nextTargets;
    if (currentTargets.includes(code)) {
        // 取消选择
        nextTargets = currentTargets.filter(c => c !== code);
    } else {
        // 新增/置换
        if (!isLicensed && currentTargets.length >= 1) {
            if (typeof addAudit === 'function') addAudit(`🔄 [社区版] 自动置换目标语种为: ${code}`, "info");
            nextTargets = [code];
        } else {
            nextTargets = [...currentTargets, code];
        }
    }

    if (typeof addAudit === 'function') addAudit(`🌍 正在同步分发矩阵...`);
    
    const res = await apiFetch('/api/config/update', { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'i18n_settings.targets': nextTargets }) 
    });

    if (res && res.status === 'success') {
        if (typeof addAudit === 'function') addAudit(`✅ 分发矩阵已同步。`, "success");
        
        // 🚀 [V55.7] 物理拉取最新状态
        const freshConfig = await apiFetch('/api/system/config?level=merged');
        if (freshConfig) {
            window.settingsData = freshConfig;
            // 🚀 [V55.7] 使用官方算子重绘，确保与主框架 100% 兼容
            if (typeof renderSettingsCategory === 'function') {
                renderSettingsCategory('localization');
            }
        }
    } else {
        const errMsg = res ? (res.error || res.message) : '物理链路超时';
        if (typeof addAudit === 'function') addAudit(`❌ 同步失败: ${errMsg}`, "error");
    }
};

// 🚀 [V57.0] 翻译风格与方言矩阵治理模块
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

                <div class="settings-group">
                    <h4>🗺️ 频道方言对正 (Route Dialects)</h4>
                    <p style="color: var(--text-dim); font-size: 0.75rem; margin-bottom: 10px;">为特定物理频道指定差异化翻译风格。</p>
                    
                    <div class="matrix-table">
                        <div class="matrix-header" style="grid-template-columns: 1fr 1fr 1.5fr;">
                            <span>频道</span>
                            <span>物理前缀</span>
                            <span>指定风格</span>
                        </div>
                        <div class="matrix-body">
                            ${(window.settingsData.route_matrix || []).map((route, idx) => `
                                <div class="matrix-row" style="grid-template-columns: 1fr 1fr 1.5fr;">
                                    <span style="font-size: 0.85rem; font-weight: 500;">${route.source}</span>
                                    <code style="font-size: 0.7rem; color: var(--accent-secondary);">${route.prefix}</code>
                                    <select class="setting-input" onchange="updateRouteStyle(${idx}, this.value)" 
                                        ${!window.settingsData._is_licensed ? 'disabled' : ''}>
                                        <option value="">继承全域</option>
                                        <option value="professional" ${route.style === 'professional' ? 'selected' : ''}>商务</option>
                                        <option value="casual" ${route.style === 'casual' ? 'selected' : ''}>随性</option>
                                        <option value="literal" ${route.style === 'literal' ? 'selected' : ''}>直译</option>
                                    </select>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

window.applyTranslationStyle = async () => {
    const selector = document.getElementById('style-selector');
    if (!selector) return;
    const style = selector.value;
    
    const templates = {
        professional: {
            translate: "You are a professional translator. Translate the following Markdown content from {source_lang} to {target_lang}. Keep all Markdown syntax, frontmatter keys, and LaTeX formulas intact. Use formal tone and professional vocabulary. Do not add any explanations.",
            title: "You are a professional editor. Translate and polish the following title into {target_lang}. Keep it concise, formal, and professional. Output ONLY the title.",
            meta: "You are a professional editor. Translate and polish the provided metadata into {target_lang} using formal terminology. Output ONLY the result."
        },
        casual: {
            translate: "You are a friendly translator. Translate the following Markdown content from {source_lang} to {target_lang} in a natural, conversational tone. Keep all Markdown syntax and frontmatter intact. Do not add any explanations.",
            title: "You are a creative editor. Translate the following title into {target_lang} in a catchy, natural, and conversational way. Output ONLY the title.",
            meta: "You are a creative editor. Translate the provided metadata into {target_lang} using natural, modern language. Output ONLY the result."
        },
        literal: {
            translate: "You are a precise translator. Translate the following Markdown content from {source_lang} to {target_lang} literally, preserving the original structure and word choice as much as possible. Keep all Markdown syntax intact. Do not add any explanations.",
            title: "You are a precise translator. Translate the following title into {target_lang} as literally as possible. Output ONLY the title.",
            meta: "You are a precise translator. Translate the provided metadata into {target_lang} literally. Output ONLY the result."
        }
    };

    const tpl = templates[style];
    if (!tpl) return;

    if (typeof addAudit === 'function') addAudit(`🎭 正在向全域（正文+标题+元数据）应用 [${style.toUpperCase()}] 风格...`, "info");

    const payload = {
        'translation.prompts.translate_system': tpl.translate,
        'translation.prompts.title_system': tpl.title,
        'translation.prompts.metadata_system': tpl.meta
    };

    const res = await apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res && res.status === 'success') {
        if (typeof addAudit === 'function') addAudit(`✅ 全域翻译风格已固化: ${style.toUpperCase()}`, "success");
        if (window.settingsData && window.settingsData.translation) {
            if (!window.settingsData.translation.prompts) window.settingsData.translation.prompts = {};
            window.settingsData.translation.prompts.translate_system = tpl.translate;
            window.settingsData.translation.prompts.title_system = tpl.title;
            window.settingsData.translation.prompts.metadata_system = tpl.meta;
        }
        const pTranslate = document.getElementById('prompt-preview-translate');
        const pTitle = document.getElementById('prompt-preview-title');
        const pMeta = document.getElementById('prompt-preview-meta');
        if (pTranslate) pTranslate.innerText = tpl.translate;
        if (pTitle) pTitle.innerText = tpl.title;
        if (pMeta) pMeta.innerText = tpl.meta;
    } else {
        if (typeof addAudit === 'function') addAudit(`❌ 风格应用失败: ${res ? res.error : '物理链路冲突'}`, "error");
    }
};

window.updateRouteStyle = async (idx, style) => {
    const route = window.settingsData.route_matrix[idx];
    if (!route) return;
    
    if (typeof addAudit === 'function') addAudit(`🎯 正在为频道 [${route.source}] 指定翻译风格: ${style || 'DEFAULT'}...`, "info");
    
    const payload = {};
    payload[`route_matrix.${idx}.style`] = style || null;

    const res = await apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res && res.status === 'success') {
        if (typeof addAudit === 'function') addAudit(`✅ 频道 [${route.source}] 风格已对正。`, "success");
        window.settingsData.route_matrix[idx].style = style || null;
    } else {
        if (typeof addAudit === 'function') addAudit(`🚨 频道风格更新失败: ${res ? res.error : '物理链路冲突'}`, "error");
    }
};
