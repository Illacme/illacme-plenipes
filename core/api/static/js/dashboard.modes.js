/**
 * 📋 [V57.0] Illacme Plenipes Publishing Modes Module
 * 职责：出版模式管理、SEO 策略选择与算力就绪检查。
 */

window.renderModesCategory = () => {
    const currentMode = window.settingsData.governance?.publishing_mode || 'basic';
    const currentStrategy = window.settingsData.governance?.seo_strategy || 'heuristic';

    const modeDefinitions = [
        { id: 'global', icon: '🌍', title: '全球矩阵', subtitle: 'Global Matrix', desc: '全量 AI：多语种翻译 + 跨语种 SEO 投喂。', strategies: [{ id: 'ai_sync', name: 'AI 翻译同步', desc: 'SEO 元信息 1:1 精准翻译' }, { id: 'ai_localized', name: 'AI 本地化策略', desc: '按语种搜索习性差异化' }] },
        { id: 'enhanced', icon: '🛰️', title: '智能增强', subtitle: 'Enhanced Publishing', desc: 'AI 参与 SEO 优化但不翻译，专注母语流量增长。', strategies: [{ id: 'ai_alignment', name: 'AI 算法对齐', desc: '优化标题点击率' }, { id: 'ai_authority', name: 'AI 实体增强', desc: '提取知识实体' }] },
        { id: 'basic', icon: '📜', title: '基础出版', subtitle: 'Basic Publishing', desc: '无 AI 介入，纯物理规则引擎。适合离线创作、私密写作。', strategies: [{ id: 'heuristic', name: '结构化提取', desc: '从 H1 和首段物理抓取 SEO' }, { id: 'protocol', name: '全维协议工程', desc: '生成 JSON-LD / Open Graph' }] }
    ];

    return `
        <div class="full-width">
            <div class="section-header"><h3>📋 出版模式 (Publishing Modes)</h3></div>
            <p class="section-desc">选择您的内容加工深度。所有模式均遵守元数据优先原则。</p>
            
            <div class="card-gallery">
                ${modeDefinitions.map(m => {
                    const isActive = m.id === currentMode;
                    return `
                        <div class="identity-card mode-card ${isActive ? 'active' : ''}" onclick="switchPublishingMode('${m.id}')">
                            <div class="card-header">
                                <div class="card-icon">${m.icon}</div>
                                <div class="card-body">
                                    <h4>${m.title}</h4>
                                    <span class="subtitle">${m.subtitle}</span>
                                </div>
                                ${isActive ? '<div class="badge active">ACTIVE</div>' : ''}
                            </div>
                            <p class="mode-desc">${m.desc}</p>
                            
                            <div class="strategy-list">
                                <span class="strategy-label">SEO 增强方式</span>
                                ${m.strategies.map(s => {
                                    const isStratActive = isActive && s.id === currentStrategy;
                                    return `
                                        <div class="strategy-item ${isStratActive ? 'active' : ''}" 
                                             onclick="event.stopPropagation(); switchSeoStrategy('${m.id}', '${s.id}')">
                                            <div class="radio-indicator">
                                                <div class="radio-inner"></div>
                                            </div>
                                            <div class="strategy-info">
                                                <div class="strategy-name">${s.name}</div>
                                                <div class="strategy-desc">${s.desc}</div>
                                            </div>
                                        </div>`;
                                }).join('')}
                            </div>
                        </div>`;
                }).join('')}
            </div>
        </div>
    `;
};

window.switchPublishingMode = async (mode) => {
    if (mode !== 'basic' && typeof checkAIReadiness === 'function' && !checkAIReadiness()) {
        if (typeof addAudit === 'function') addAudit(`🛑 无法切换至 ${mode.toUpperCase()} 模式：未配置 AI 算力`, "error");
        return;
    }
    if (typeof addAudit === 'function') addAudit(`📋 正在切换出版模式至: ${mode.toUpperCase()}...`);
    const res = await apiFetch('/api/config/update', { method: 'POST', body: JSON.stringify({ 'governance.publishing_mode': mode }) });
    if (res && res.status === 'success') {
        window.settingsData.governance.publishing_mode = mode;
        if (typeof renderSettingsCategory === 'function') renderSettingsCategory('modes');
        if (typeof addAudit === 'function') addAudit(`✅ 出版模式已切换至 [${mode.toUpperCase()}]`, "success");
    }
};

window.switchSeoStrategy = async (mode, strategy) => {
    if (typeof addAudit === 'function') addAudit(`🎯 正在切换 SEO 策略至: ${strategy}...`);
    const res = await apiFetch('/api/config/update', { 
        method: 'POST', 
        body: JSON.stringify({ 'governance.publishing_mode': mode, 'governance.seo_strategy': strategy }) 
    });
    if (res && res.status === 'success') {
        window.settingsData.governance.seo_strategy = strategy;
        if (typeof renderSettingsCategory === 'function') renderSettingsCategory('modes');
        if (typeof addAudit === 'function') addAudit(`✅ SEO 策略已切换至 [${strategy}]`, "success");
    }
};

window.checkAIReadiness = () => {
    const nodes = window.settingsData?.translation?.compute_nodes || {};
    return Object.keys(nodes).length > 0;
};
