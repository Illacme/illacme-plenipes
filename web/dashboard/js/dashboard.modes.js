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

    const currentModeDef = modeDefinitions.find(m => m.id === currentMode) || modeDefinitions[2];

    return `
        <div class="full-width fade-in">
            <!-- 📋 首屏核心业务：出版模式3列横向并排对比矩阵 (位置绝对稳定，空间记忆永不跳跃) -->
            <div class="modes-grid" style="margin-top: 2px;">
                ${modeDefinitions.map(m => {
                    const isActive = m.id === currentMode;
                    const isDisabled = (m.id !== 'basic' && !enableAi);
                    const disabledReason = (m.id !== 'basic' && !enableAi) ? '🔒 未开启 AI 算力总控' : '';

                    return `<div class="identity-card mode-card ${isActive ? 'active' : ''} ${isDisabled ? 'disabled' : ''}" style="position: relative; ${isDisabled ? 'opacity: 0.5; cursor: not-allowed; pointer-events: none;' : ''}" onclick="${isDisabled ? '' : `switchPublishingMode('${m.id}')`}">
                            ${isActive ? '<div class="mode-active-ribbon" style="position: absolute; top: 18px; right: 18px; background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: #ffffff; font-weight: 800; font-size: 0.68rem; padding: 4px 10px; border-radius: 6px; box-shadow: 0 4px 14px rgba(5, 150, 105, 0.45); display: flex; align-items: center; gap: 5px; letter-spacing: 0.3px; backdrop-filter: blur(8px);"><span>👑</span> <span>当前生效模式</span></div>' : ''}
                            ${isDisabled ? `<div class="badge error" style="position: absolute; top: 18px; right: 18px; background: rgba(255, 68, 68, 0.15); color: #ff4444; border: 1px solid rgba(255, 68, 68, 0.3); font-size: 0.62rem; padding: 3px 6px; border-radius: 6px;">${disabledReason}</div>` : ''}
                            <div class="card-header">
                                <div class="card-icon">${m.icon}</div>
                                <div class="card-body"><h4 style="margin: 0 0 2px 0;">${m.title}</h4><span class="subtitle">${m.subtitle}</span></div>
                            </div>
                            <p class="mode-desc">${m.desc}</p>
                            <div class="strategy-list" style="${isDisabled ? 'pointer-events: none;' : ''}">
                                <span class="strategy-label">SEO 增强方式</span>
                                ${m.strategies.map(s => {
                                    const isStratActive = isActive && s.id === currentStrategy;
                                    return `<div class="strategy-item ${isStratActive ? 'active' : ''}" style="${isDisabled ? 'cursor: not-allowed;' : ''}" onclick="event.stopPropagation(); ${isDisabled ? '' : `switchSeoStrategy('${m.id}', '${s.id}')`}">
                                            <div class="radio-indicator"><div class="radio-inner"></div></div>
                                            <div class="strategy-info"><div class="strategy-name">${s.name}</div><div class="strategy-desc">${s.desc}</div></div>
                                        </div>`;
                                }).join('')}
                            </div>
                        </div>`;
                }).join('')}
            </div>

            <!-- 🧭 底部精炼知识卡：如何选择适合您的出版模式 -->
            <div class="glass-panel" style="padding: 16px 20px; border-radius: 12px; border-left: 4px solid var(--accent-secondary); background: rgba(0, 242, 255, 0.02); margin-top: 25px; display: flex; flex-direction: column; gap: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h5 style="color: var(--accent-secondary); margin: 0; font-size: 0.88rem; font-weight: 700; letter-spacing: 0.5px; display: flex; align-items: center; gap: 6px;">🧭 如何选择适合您的出版模式？</h5>
                    <span style="font-size: 0.72rem; color: var(--text-dim);">可根据文稿类型与目标读者随时一键切换</span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; font-size: 0.76rem; line-height: 1.5; color: var(--text-normal);">
                    <div style="background: rgba(255, 255, 255, 0.02); padding: 10px 14px; border-radius: 8px; border: 1px solid var(--glass-border);">
                        <span style="color: var(--text-bright, #fff); font-weight: 600; display: block; margin-bottom: 4px;">🌍 全球多语言分发</span>
                        适合有<b>海外/跨国读者群与多语流量需求</b>。写完后 AI 自动帮您全量翻译成多国语种并优化各地区 SEO（需配置算力网关）。
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.02); padding: 10px 14px; border-radius: 8px; border: 1px solid var(--glass-border);">
                        <span style="color: var(--text-bright, #fff); font-weight: 600; display: block; margin-bottom: 4px;">🛰️ 智能母语增强</span>
                        适合<b>仅写作单语（母语）但希望最大化曝光与点击率</b>。不进行多语翻译，由 AI 针对母语润色标题与知识实体（需配置算力网关）。
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.02); padding: 10px 14px; border-radius: 8px; border: 1px solid var(--glass-border);">
                        <span style="color: var(--text-bright, #fff); font-weight: 600; display: block; margin-bottom: 4px;">📜 基础物理出版</span>
                        适合<b>离线写作、极简轻量或对内容隐私有极高要求</b>的场景。完全零 AI 算力调用，基于纯固定规则静态生成。
                    </div>
                </div>
            </div>
        </div>`;
};
// 🚀 [模式切换控制器解耦] 出版模式与 SEO 策略切换控制器已抽离至 modes_shards/modes.controller.js 供给

window.renderLayoutCategory = () => {
    const isLicensed = window.settingsData?._is_licensed || false;
    const layoutSubDescs = {
        imprints: `💡 查看与管理旗下所有独立出版品牌，支持一键切换当前激活的品牌。${!isLicensed ? '<span class="community-edition-badge" style="font-size: 0.68rem; color: #fbbf24; background: rgba(251, 191, 36, 0.1); border: 1px solid rgba(251, 191, 36, 0.25); padding: 2px 8px; border-radius: 10px; font-weight: 500; margin-left: 8px; white-space: nowrap;">🌱 免费社区版：支持 1 个自定义品牌</span>' : ''}`,
        themes: '💡 为当前出版品牌选用匹配的现代前端视觉装帧主题。',
        modes: '💡 调节加工深度与出版模式（基础出版 / 全球出版 / 智能母语增强）。',
        image_policy: '💡 为当前出版品牌配置自动化封面供给、视觉画幅与图像生成策略。'
    };

    if (!window.switchLayoutSubTab) {
        window.switchLayoutSubTab = (subTab, btn) => {
            window.currentActiveSettingsSubCat = subTab;
            const container = document.getElementById('layout-sub-tab-bar');
            if (container) container.querySelectorAll('.sub-tab-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            else if (typeof event !== 'undefined' && event.currentTarget) event.currentTarget.classList.add('active');

            const panels = ['imprints', 'themes', 'modes', 'image_policy'];
            panels.forEach(p => {
                const el = document.getElementById(`layout-panel-${p}`);
                if (el) el.style.display = (p === subTab) ? 'block' : 'none';
            });

            const descEl = document.getElementById('layout-sub-tab-desc');
            if (descEl) descEl.innerHTML = layoutSubDescs[subTab] || '';

            // 🎯 [V82.0] 同排右对齐状态指示微标：利用 Tab 栏右侧空白，完全 0 额外垂直占高
            window.updateLayoutStatusBadge = (targetSub) => {
                const badgeEl = document.getElementById('layout-header-status-badge');
                if (!badgeEl) return;
                const sub = targetSub || window.currentActiveSettingsSubCat;
                if (sub === 'imprints') {
                    const activeId = window.settingsData?._active_imprint;
                    const imprints = window.settingsData?._imprints || [];
                    const cur = imprints.find(i => i.id === activeId);
                    const imprintName = cur ? (cur.name || cur.id) : (activeId || '默认品牌');
                    badgeEl.innerHTML = `<div style="font-size: 0.72rem; padding: 3px 10px; background: rgba(var(--neon-cyan-rgb), 0.08); border: 1px solid var(--neon-cyan-30); border-radius: 16px; color: var(--accent-secondary); display: flex; align-items: center; gap: 5px;"><span>🚩 当前品牌：</span><b style="color: var(--text-bright); font-weight: 700;">${imprintName}</b></div>`;
                } else if (sub === 'themes') {
                    const activeTheme = window.settingsData?.active_theme || 'default';
                    const themeName = typeof window.getThemeDisplayName === 'function' ? window.getThemeDisplayName(activeTheme) : activeTheme;
                    badgeEl.innerHTML = `<div style="font-size: 0.72rem; padding: 3px 10px; background: rgba(var(--neon-cyan-rgb), 0.08); border: 1px solid var(--neon-cyan-30); border-radius: 16px; color: var(--accent-secondary); display: flex; align-items: center; gap: 5px;"><span>👑 当前主题：</span><b style="color: var(--text-bright); font-weight: 700;">${themeName}</b></div>`;
                } else if (sub === 'modes') {
                    const currentMode = window.settingsData?.governance?.publishing_mode || 'basic';
                    const modeMap = { global: '🌍 全球多语言分发', enhanced: '🛰️ 智能母语增强', basic: '📜 基础物理出版' };
                    badgeEl.innerHTML = `<div style="font-size: 0.72rem; padding: 3px 10px; background: rgba(var(--neon-cyan-rgb), 0.08); border: 1px solid var(--neon-cyan-30); border-radius: 16px; color: var(--accent-secondary); display: flex; align-items: center; gap: 5px;"><span>👑 当前模式：</span><b style="color: var(--text-bright); font-weight: 700;">${modeMap[currentMode] || '📜 基础物理出版'}</b></div>`;
                } else if (sub === 'image_policy') {
                    const policy = window.settingsData?.image_policy || {};
                    const stratId = policy.default_strategy || 'auto';
                    const stratNames = { auto: '⚡ 智能阶梯自愈', og_card: '💻 动态 OG 技术卡片', brand_presets: '🎨 品牌母本图库轮巡', minimal_badge: '🏷️ 极简首字文字徽章', unsplash: '📷 Unsplash 免版权摄影', ai_generator: '🔮 AI 智能文生图' };
                    badgeEl.innerHTML = `<div style="font-size: 0.72rem; padding: 3px 10px; background: rgba(var(--neon-cyan-rgb), 0.08); border: 1px solid var(--neon-cyan-30); border-radius: 16px; color: var(--accent-secondary); display: flex; align-items: center; gap: 5px;"><span>🖼️ 当前策略：</span><b style="color: var(--text-bright); font-weight: 700;">${stratNames[stratId] || stratId}</b></div>`;
                } else {
                    badgeEl.innerHTML = '';
                }
            };
            window.updateLayoutStatusBadge(subTab);

            // 渲染对应的子页面
            const panelEl = document.getElementById(`layout-panel-${subTab}`);
            if (panelEl) {
                let html = '';
                if (subTab === 'imprints' && typeof window.renderImprintsCategory === 'function') html = window.renderImprintsCategory();
                else if (subTab === 'themes' && typeof window.renderThemesCategory === 'function') html = window.renderThemesCategory();
                else if (subTab === 'modes' && typeof window.renderModesCategory === 'function') html = window.renderModesCategory();
                else if (subTab === 'image_policy' && typeof window.renderImagePolicyCategory === 'function') html = window.renderImagePolicyCategory();
                panelEl.innerHTML = html;
            }
            if (typeof window.updateSaveButtonVisibility === 'function') window.updateSaveButtonVisibility(subTab);
        };
    }
    const currentSub = window.currentActiveSettingsSubCat || 'imprints';
    setTimeout(() => {
        const activeBtn = document.querySelector(`#layout-sub-tab-bar .sub-tab-btn[onclick*="${currentSub}"]`);
        if (typeof window.switchLayoutSubTab === 'function') window.switchLayoutSubTab(currentSub, activeBtn);
    }, 20);

    return `
        <div class="category-header-banner" style="display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; padding: 12px 18px; background: rgba(0, 242, 255, 0.03); border: 1px solid var(--glass-border); border-radius: 12px; backdrop-filter: blur(10px);">
            <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <h2 style="margin: 0; font-size: 1.18rem; font-weight: 800; color: var(--text-main); letter-spacing: 0.5px;">🎨 品牌装帧与模式</h2>
                </div>
            </div>

            <div class="sub-tab-navigation-bar" id="layout-sub-tab-bar" style="display: flex; gap: 8px; margin-top: 4px; border-bottom: 1px solid var(--glass-border); padding-bottom: 8px; flex-wrap: wrap;">
                <button type="button" class="sub-tab-btn ${currentSub === 'imprints' ? 'active' : ''}" onclick="window.switchLayoutSubTab('imprints', this)" style="padding: 5px 13px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">🚩 品牌管理</button>
                <button type="button" class="sub-tab-btn ${currentSub === 'themes' ? 'active' : ''}" onclick="window.switchLayoutSubTab('themes', this)" style="padding: 5px 13px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">🎨 装帧主题</button>
                <button type="button" class="sub-tab-btn ${currentSub === 'modes' ? 'active' : ''}" onclick="window.switchLayoutSubTab('modes', this)" style="padding: 5px 13px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">📋 出版模式</button>
                <button type="button" class="sub-tab-btn ${currentSub === 'image_policy' ? 'active' : ''}" onclick="window.switchLayoutSubTab('image_policy', this)" style="padding: 5px 13px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">🖼️ 图像策略</button>
            </div>

            <!-- 💡 功能说明在左，当前激活模式在右 (左右对齐，认知顺畅，0 额外垂直占高) -->
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-top: 4px; min-height: 24px; flex-wrap: wrap;">
                <div id="layout-sub-tab-desc" style="font-size: 0.8rem; color: var(--text-muted); flex: 1; min-width: 240px;">
                    ${layoutSubDescs[currentSub] || ''}
                </div>
                <div id="layout-header-status-badge" style="display: flex; align-items: center; flex-shrink: 0;"></div>
            </div>
        </div>

            <div id="layout-panel-imprints" style="display: ${currentSub === 'imprints' ? 'block' : 'none'};"></div>
            <div id="layout-panel-themes" style="display: ${currentSub === 'themes' ? 'block' : 'none'};"></div>
            <div id="layout-panel-modes" style="display: ${currentSub === 'modes' ? 'block' : 'none'};"></div>
            <div id="layout-panel-image_policy" style="display: ${currentSub === 'image_policy' ? 'block' : 'none'};"></div>
        </div>`;
};
