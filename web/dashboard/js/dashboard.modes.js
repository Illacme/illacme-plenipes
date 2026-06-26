/**
 * 📋 [V57.0] Illacme Plenipes Publishing Modes Module
 * 职责：出版模式管理、SEO 策略选择与算力就绪检查。
 */

window.renderModesCategory = () => {
    const currentMode = window.settingsData.governance?.publishing_mode || 'basic';
    const currentStrategy = window.settingsData.governance?.seo_strategy || 'heuristic';

    // 🚀 [V74.96] 预热初始化记忆：若配置已加载有效策略，同步记录进本地 localStorage 缓存
    if (window.settingsData.governance?.seo_strategy) {
        localStorage.setItem(`illacme_plenipes_last_strategy_for_${currentMode}`, currentStrategy);
    }

    const enableAi = window.settingsData.translation?.enable_ai !== false;
    const i18nEnabled = window.settingsData.i18n_settings?.enabled !== false;

    const modeDefinitions = [
        { 
            id: 'global', 
            icon: '🌍', 
            title: '全球多语言分发', 
            subtitle: 'Global Distribution Mode', 
            desc: 'AI 全量介入：源语言写作后，自动为您同步翻译生成多语种版本，并自动适配各国搜索习惯。', 
            strategies: [
                { id: 'ai_sync', name: 'AI 翻译同步', desc: '将原稿 SEO 标题和元信息 1:1 进行精准语义翻译。' }, 
                { id: 'ai_localized', name: 'AI 区域搜索对齐', desc: '根据目标语种地区的搜索习惯与文化差异，智能生成更符合当地检索习性的元数据。' }
            ] 
        },
        { 
            id: 'enhanced', 
            icon: '🛰️', 
            title: '智能母语增强', 
            subtitle: 'Enhanced Native Mode', 
            desc: 'AI 参与单语种 SEO 调优，仅优化母语网站结构与流量，不进行跨语言翻译。', 
            strategies: [
                { id: 'ai_alignment', name: 'AI 标题与点击率调优', desc: '优化标题与网页描述（CTR），使文章更具点击吸引力。' }, 
                { id: 'ai_authority', name: 'AI 核心概念标记', desc: '自动提取并标记文章中的知识实体，提升搜索引擎对内容专业度的权威识别。' }
            ] 
        },
        { 
            id: 'basic', 
            icon: '📜', 
            title: '基础物理出版', 
            subtitle: 'Basic Rule Mode', 
            desc: '完全无 AI 参与，只根据网站预设的物理规则运转。适合不需要多语言、无算力配置或高度保密的离线创作。', 
            strategies: [
                { id: 'heuristic', name: '结构化提取', desc: '根据固定规则从 H1 标题和文章正文首段中物理抓取生成 SEO 信息。' }, 
                { id: 'protocol', name: '社交与检索协议增强', desc: '自动生成 JSON-LD 结构化数据与 Open Graph 社交分享卡片协议。' }
            ] 
        }
    ];
    
    // 🚀 [V74.96] 置顶机制：将当前激活的出版模式移动到模式列表最顶部显示
    const activeIndex = modeDefinitions.findIndex(m => m.id === currentMode);
    if (activeIndex > 0) {
        const [activeMode] = modeDefinitions.splice(activeIndex, 1);
        modeDefinitions.unshift(activeMode);
    }

    return `
        <div class="full-width">
            <div class="section-header"><h3>📋 出版模式 (Publishing Modes)</h3></div>
            <p class="section-desc" style="margin-bottom: 20px;">选择您的内容加工深度。所有模式均遵守元数据优先原则。</p>
            
            <!-- 🧭 极简出版决策指南 -->
            <div class="glass-panel" style="padding: 16px 20px; border-radius: 12px; border: 1px dashed rgba(0, 242, 255, 0.2); background: rgba(0, 242, 255, 0.02); margin-bottom: 25px; display: flex; flex-direction: column; gap: 10px;">
                <h5 style="color: #00f2ff; margin: 0; font-size: 0.85rem; font-weight: 700; letter-spacing: 0.5px; display: flex; align-items: center; gap: 6px;">
                    🧭 如何选择适合您的出版模式？
                </h5>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; font-size: 0.78rem; line-height: 1.5; color: var(--text-normal);">
                    <div style="border-right: 1px solid rgba(255, 255, 255, 0.05); padding-right: 15px;">
                        <span style="color: var(--text-bright, #fff); font-weight: 600; display: block; margin-bottom: 4px;">🌍 全球多语言分发</span>
                        适合有<b>海外/跨国流量需求</b>。写完后 AI 自动帮您全量翻译成多国语种并对齐海外搜索习惯（需配置算力网关）。
                    </div>
                    <div style="border-right: 1px solid rgba(255, 255, 255, 0.05); padding-right: 15px;">
                        <span style="color: var(--text-bright, #fff); font-weight: 600; display: block; margin-bottom: 4px;">🛰️ 智能母语增强</span>
                        适合<b>仅写单语（母语）但想冲高点击率</b>。不翻译，仅让 AI 帮您润色标题、提取实体优化本土检索（需配置算力网关）。
                    </div>
                    <div>
                        <span style="color: var(--text-bright, #fff); font-weight: 600; display: block; margin-bottom: 4px;">📜 基础物理出版</span>
                        适合<b>离线写作、高度隐私</b>，或无 AI 算力。完全不调用 AI 接口，只通过程序物理规则抓取首段和 H1，零算力成本。
                    </div>
                </div>
            </div>

            <div class="card-gallery">
                ${modeDefinitions.map(m => {
                    const isActive = m.id === currentMode;
                    const isDisabled = (m.id === 'global' && (!enableAi || !i18nEnabled)) || (m.id === 'enhanced' && !enableAi);
                    let disabledReason = '';
                    if (m.id === 'global') {
                        if (!enableAi) disabledReason = '🔒 未开启 AI 算力总控';
                        else if (!i18nEnabled) disabledReason = '🔒 未开启多语言翻译矩阵';
                    } else if (m.id === 'enhanced' && !enableAi) {
                        disabledReason = '🔒 未开启 AI 算力总控';
                    }

                    return `
                        <div class="identity-card mode-card ${isActive ? 'active' : ''} ${isDisabled ? 'disabled' : ''}" 
                             style="${isDisabled ? 'opacity: 0.5; cursor: not-allowed; pointer-events: none;' : ''}"
                             onclick="${isDisabled ? '' : `switchPublishingMode('${m.id}')`}">
                            <div class="card-header">
                                <div class="card-icon">${m.icon}</div>
                                <div class="card-body">
                                    <h4>${m.title}</h4>
                                    <span class="subtitle">${m.subtitle}</span>
                                </div>
                                ${isActive ? '<div class="badge active">ACTIVE</div>' : ''}
                                ${isDisabled ? `<div class="badge error" style="background: rgba(255, 68, 68, 0.15); color: #ff4444; border: 1px solid rgba(255, 68, 68, 0.3); font-size: 0.65rem; padding: 4px 8px;">${disabledReason}</div>` : ''}
                            </div>
                            <p class="mode-desc">${m.desc}</p>
                            
                            <div class="strategy-list" style="${isDisabled ? 'pointer-events: none;' : ''}">
                                <span class="strategy-label">SEO 增强方式</span>
                                ${m.strategies.map(s => {
                                    const isStratActive = isActive && s.id === currentStrategy;
                                    return `
                                        <div class="strategy-item ${isStratActive ? 'active' : ''}" 
                                             style="${isDisabled ? 'cursor: not-allowed;' : ''}"
                                             onclick="event.stopPropagation(); ${isDisabled ? '' : `switchSeoStrategy('${m.id}', '${s.id}')`}">
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
    if (typeof window.checkSettingsDirtyAndConfirm === 'function') {
        const proceed = await window.checkSettingsDirtyAndConfirm();
        if (!proceed) {
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('modes');
            return;
        }
    }

    const enableAi = window.settingsData.translation?.enable_ai !== false;
    const i18nEnabled = window.settingsData.i18n_settings?.enabled !== false;

    if (mode === 'global' && (!enableAi || !i18nEnabled)) {
        const reason = !enableAi ? '未开启 AI 算力总控' : '未开启多语言翻译矩阵';
        if (typeof addAudit === 'function') addAudit(`🛑 无法切换至 全球多语言分发 模式：${reason}`, "error");
        if (typeof showNotification === 'function') showNotification(`🔒 无法选择全球多语言分发：${reason}`, 'error');
        return;
    }
    if (mode === 'enhanced' && !enableAi) {
        if (typeof addAudit === 'function') addAudit(`🛑 无法切换至 智能母语增强 模式：未开启 AI 算力总控`, "error");
        if (typeof showNotification === 'function') showNotification(`🔒 无法选择智能母语增强：未开启 AI 算力总控`, 'error');
        return;
    }

    if (mode !== 'basic' && typeof checkAIReadiness === 'function' && !checkAIReadiness()) {
        if (typeof addAudit === 'function') addAudit(`🛑 无法切换至 ${mode.toUpperCase()} 模式：未配置 AI 算力`, "error");
        return;
    }
    const defaultStrategies = {
        'global': 'ai_sync',
        'enhanced': 'ai_alignment',
        'basic': 'heuristic'
    };
    
    // 🚀 [V74.96] 记忆机制：优先从 localStorage 提取用户上一次在该模式选定的策略，若无则使用兜底默认
    const lastStrategyKey = `illacme_plenipes_last_strategy_for_${mode}`;
    const defaultStrategy = localStorage.getItem(lastStrategyKey) || defaultStrategies[mode] || 'heuristic';
    
    if (typeof addAudit === 'function') addAudit(`📋 正在切换出版模式至: ${mode.toUpperCase()}...`);
    const res = await apiFetch('/api/config/update', { 
        method: 'POST', 
        body: JSON.stringify({ 
            'governance.publishing_mode': mode,
            'governance.seo_strategy': defaultStrategy
        }) 
    });
    if (res && res.status === 'success') {
        // 智能在本地缓存中再次固化这次的选择
        localStorage.setItem(lastStrategyKey, defaultStrategy);
        
        window.settingsData = { ...window.settingsData, ...res.active_config };
        if (typeof renderSettingsCategory === 'function') renderSettingsCategory('modes');
        
        // 🚀 刷新左侧治理边栏感知状态，隐藏/显示 Intelligence 模块
        if (typeof window.refreshGovernanceContext === 'function') {
            window.refreshGovernanceContext();
        }

        // 🚀 交互自愈：切换模式后自动平滑滚动置顶，确保列表首个可见
        const container = document.querySelector('.view-panel.active .tab-content-area');
        if (container) {
            container.scrollTo({ top: 0, behavior: 'smooth' });
        }
        
        if (typeof addAudit === 'function') addAudit(`✅ 出版模式已切换至 [${mode.toUpperCase()}]，启用 [${defaultStrategy}] 策略`, "success");
        if (window.Swal) {
            window.Swal.fire({
                title: '💡 出版模式切换提示',
                text: '出版模式已成功切换。为了让本地译文缓存和文件完全对正，强烈建议您在下一次同步时勾选“强制重构/清除缓存”选项重新发布。',
                icon: 'info',
                background: 'rgba(20, 20, 25, 0.95)',
                color: '#fff',
                confirmButtonColor: 'var(--accent-primary)',
                confirmButtonText: '确定'
            });
        }
    }
};

window.switchSeoStrategy = async (mode, strategy) => {
    if (typeof window.checkSettingsDirtyAndConfirm === 'function') {
        const proceed = await window.checkSettingsDirtyAndConfirm();
        if (!proceed) {
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('modes');
            return;
        }
    }

    const enableAi = window.settingsData.translation?.enable_ai !== false;
    const i18nEnabled = window.settingsData.i18n_settings?.enabled !== false;

    if (mode === 'global' && (!enableAi || !i18nEnabled)) {
        return;
    }
    if (mode === 'enhanced' && !enableAi) {
        return;
    }

    if (typeof addAudit === 'function') addAudit(`🎯 正在切换 SEO 策略至: ${strategy}...`);
    const res = await apiFetch('/api/config/update', { 
        method: 'POST', 
        body: JSON.stringify({ 'governance.publishing_mode': mode, 'governance.seo_strategy': strategy }) 
    });
    if (res && res.status === 'success') {
        // 🚀 [V74.96] 记忆机制：手动切换策略成功后，立刻持久化记录至本地 localStorage 缓存
        const lastStrategyKey = `illacme_plenipes_last_strategy_for_${mode}`;
        localStorage.setItem(lastStrategyKey, strategy);

        window.settingsData = { ...window.settingsData, ...res.active_config };
        if (typeof renderSettingsCategory === 'function') renderSettingsCategory('modes');
        
        // 🚀 刷新左侧治理边栏感知状态，隐藏/显示 Intelligence 模块
        if (typeof window.refreshGovernanceContext === 'function') {
            window.refreshGovernanceContext();
        }

        // 🚀 交互自愈：切换策略后自动平滑滚动置顶
        const container = document.querySelector('.view-panel.active .tab-content-area');
        if (container) {
            container.scrollTo({ top: 0, behavior: 'smooth' });
        }
        
        if (typeof addAudit === 'function') addAudit(`✅ SEO 策略已切换至 [${strategy}]`, "success");
    }
};

window.checkAIReadiness = () => {
    const nodes = window.settingsData?.translation?.compute_nodes || {};
    return Object.keys(nodes).length > 0;
};
