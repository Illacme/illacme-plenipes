/**
 * 🌍 [V75.5] Illacme Plenipes Localization - Category Tabs & Sub-Tab Routing Shard
 * 职责：语言翻译与内容治理二级 Sub-Tab 总控及分发路由 Sub-Tab 组合渲染入口与别名兼容。
 * 契约：严格遵守治理大宪章 Rule #3 (4个子标签) 与 Rule #3.1 (2个子标签) 规范。
 */

(function () {
    const locSubDescs = {
        localization: '💡 设置文章主出版语种（中文/英文）以及多语言分发的目标语种阵列。',
        block_rules: '💡 配置段落多段合并翻译、链接与跳转自动对齐，以及各类型正文内容的翻译流控规则。',
        glossary: '💡 维护品牌专有名词保护词库，AI 翻译前自动屏护，确保关键术语 100% 不被误译。',
        translation_style: '💡 设定大模型翻译输出的行文语气、专业风格基调与自定义 Prompt 微调。'
    };

    window.switchLocalizationGovSubTab = (subTab, btn) => {
        window.currentActiveSettingsSubCat = subTab;
        const container = document.getElementById('loc-gov-sub-tab-bar');
        if (container) {
            const btns = container.querySelectorAll('.sub-tab-btn');
            btns.forEach(b => {
                if (b.getAttribute('onclick') && b.getAttribute('onclick').includes(`'${subTab}'`)) {
                    b.classList.add('active');
                } else {
                    b.classList.remove('active');
                }
            });
        }

        const panels = ['localization', 'block_rules', 'translation_style', 'glossary'];
        panels.forEach(p => {
            const el = document.getElementById(`loc-panel-${p}`);
            if (el) el.style.display = (p === subTab) ? 'block' : 'none';
        });

        const descEl = document.getElementById('loc-gov-sub-tab-desc');
        if (descEl) descEl.innerHTML = locSubDescs[subTab] || '';

        const panelEl = document.getElementById(`loc-panel-${subTab}`);
        if (panelEl) {
            let html = '';
            if (subTab === 'localization' && typeof window.renderLocalizationCategory === 'function') {
                html = window.renderLocalizationCategory();
            } else if (subTab === 'block_rules' && typeof window.renderBlockRulesCategory === 'function') {
                html = window.renderBlockRulesCategory();
            } else if (subTab === 'translation_style' && typeof window.renderTranslationStyleCategory === 'function') {
                html = window.renderTranslationStyleCategory();
            } else if (subTab === 'glossary' && typeof window.renderGlossaryCategory === 'function') {
                html = window.renderGlossaryCategory();
            }
            panelEl.innerHTML = html;
        }

        if (typeof window.updateSaveButtonVisibility === 'function') {
            window.updateSaveButtonVisibility(subTab);
        }
    };

    window.renderLocalizationGovCategory = () => {
        const currentSub = window.currentActiveSettingsSubCat || 'localization';

        setTimeout(() => {
            const activeBtn = document.getElementById('loc-gov-sub-tab-bar')?.querySelector(`.sub-tab-btn[onclick*="${currentSub}"]`);
            if (typeof window.switchLocalizationGovSubTab === 'function') {
                window.switchLocalizationGovSubTab(currentSub, activeBtn);
            }
        }, 20);

        return `
            <div class="category-header-banner" style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px; padding: 18px 22px; background: rgba(0, 242, 255, 0.03); border: 1px solid var(--glass-border); border-radius: 12px; backdrop-filter: blur(10px);">
                <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <h2 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: var(--text-main); letter-spacing: 0.5px;">🌍 语言翻译与内容治理</h2>
                    </div>
                </div>

                <div class="sub-tab-navigation-bar" id="loc-gov-sub-tab-bar" style="display: flex; gap: 8px; margin-top: 10px; border-bottom: 1px solid var(--glass-border); padding-bottom: 10px;">
                    <button type="button" class="sub-tab-btn ${currentSub === 'localization' ? 'active' : ''}" onclick="window.switchLocalizationGovSubTab('localization', this)" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">🌍 语种矩阵</button>
                    <button type="button" class="sub-tab-btn ${currentSub === 'block_rules' ? 'active' : ''}" onclick="window.switchLocalizationGovSubTab('block_rules', this)" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">🧱 翻译规则</button>
                    <button type="button" class="sub-tab-btn ${currentSub === 'translation_style' ? 'active' : ''}" onclick="window.switchLocalizationGovSubTab('translation_style', this)" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">🗣️ 译文风格</button>
                    <button type="button" class="sub-tab-btn ${currentSub === 'glossary' ? 'active' : ''}" onclick="window.switchLocalizationGovSubTab('glossary', this)" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">📚 术语词库</button>
                </div>

                <div id="loc-gov-sub-tab-desc" style="font-size: 0.82rem; color: var(--text-muted); margin-top: 4px;">
                    ${locSubDescs[currentSub] || ''}
                </div>
            </div>

            <div id="loc-panel-localization" style="display: ${currentSub === 'localization' ? 'block' : 'none'};"></div>
            <div id="loc-panel-block_rules" style="display: ${currentSub === 'block_rules' ? 'block' : 'none'};"></div>
            <div id="loc-panel-translation_style" style="display: ${currentSub === 'translation_style' ? 'block' : 'none'};"></div>
            <div id="loc-panel-glossary" style="display: ${currentSub === 'glossary' ? 'block' : 'none'};"></div>
        `;
    };

    const routingSubDescs = {
        slug_settings: '💡 设定文章 URL Slug 生成规则（AI 智能推导短网址或文件名清洗）。',
        route_matrix: '💡 将本地特定文件夹路由至全新的逻辑出版路径，并指派专属前端模板与翻译风格。'
    };

    window.switchDisseminationRoutingSubTab = (subTab, btn) => {
        window.currentActiveSettingsSubCat = subTab;
        const container = document.getElementById('dissemination-routing-sub-tab-bar');
        if (container) {
            const btns = container.querySelectorAll('.sub-tab-btn');
            btns.forEach(b => {
                if (b.getAttribute('onclick') && b.getAttribute('onclick').includes(`'${subTab}'`)) {
                    b.classList.add('active');
                } else {
                    b.classList.remove('active');
                }
            });
        }

        const panels = ['slug_settings', 'route_matrix'];
        panels.forEach(p => {
            const el = document.getElementById(`routing-panel-${p}`);
            if (el) el.style.display = (p === subTab) ? 'block' : 'none';
        });

        const descEl = document.getElementById('dissemination-routing-sub-tab-desc');
        if (descEl) descEl.innerHTML = routingSubDescs[subTab] || '';

        const panelEl = document.getElementById(`routing-panel-${subTab}`);
        if (panelEl) {
            let html = '';
            if (subTab === 'slug_settings' && typeof window.renderSlugSettingsCategory === 'function') {
                html = window.renderSlugSettingsCategory();
            } else if (subTab === 'route_matrix' && typeof window.renderRouteMatrixCategory === 'function') {
                html = window.renderRouteMatrixCategory();
            }
            panelEl.innerHTML = html;
            if (subTab === 'route_matrix') {
                setTimeout(() => {
                    if (typeof window.updateAllLivePathBadges === 'function') {
                        window.updateAllLivePathBadges();
                    }
                }, 30);
            }
        }

        if (typeof window.updateSaveButtonVisibility === 'function') {
            window.updateSaveButtonVisibility(subTab);
        }
    };

    window.renderDisseminationRoutingCategory = () => {
        const currentSub = window.currentActiveSettingsSubCat || 'slug_settings';

        setTimeout(() => {
            const activeBtn = document.getElementById('dissemination-routing-sub-tab-bar')?.querySelector(`.sub-tab-btn[onclick*="${currentSub}"]`);
            if (typeof window.switchDisseminationRoutingSubTab === 'function') {
                window.switchDisseminationRoutingSubTab(currentSub, activeBtn);
            }
        }, 20);

        return `
            <div class="category-header-banner" style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px; padding: 18px 22px; background: rgba(0, 242, 255, 0.03); border: 1px solid var(--glass-border); border-radius: 12px; backdrop-filter: blur(10px);">
                <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <h2 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: var(--text-main); letter-spacing: 0.5px;">🧭 分发路由与网址路径</h2>
                    </div>
                </div>

                <div class="sub-tab-navigation-bar" id="dissemination-routing-sub-tab-bar" style="display: flex; gap: 8px; margin-top: 10px; border-bottom: 1px solid var(--glass-border); padding-bottom: 10px;">
                    <button type="button" class="sub-tab-btn ${currentSub === 'slug_settings' ? 'active' : ''}" onclick="window.switchDisseminationRoutingSubTab('slug_settings', this)" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">📝 网址路径</button>
                    <button type="button" class="sub-tab-btn ${currentSub === 'route_matrix' ? 'active' : ''}" onclick="window.switchDisseminationRoutingSubTab('route_matrix', this)" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">🧭 频道映射</button>
                </div>

                <div id="dissemination-routing-sub-tab-desc" style="font-size: 0.82rem; color: var(--text-muted); margin-top: 4px;">
                    ${routingSubDescs[currentSub] || ''}
                </div>
            </div>

            <div id="routing-panel-slug_settings" style="display: ${currentSub === 'slug_settings' ? 'block' : 'none'};"></div>
            <div id="routing-panel-route_matrix" style="display: ${currentSub === 'route_matrix' ? 'block' : 'none'};"></div>
        `;
    };

    // 🚀 向后兼容旧接口别名与智能双轨分发器
    window.renderI18nRoutingCategory = window.renderLocalizationGovCategory;
    window.switchI18nRoutingSubTab = (subTab, btn) => {
        if (['slug_settings', 'route_matrix'].includes(subTab) && typeof window.switchDisseminationRoutingSubTab === 'function') {
            return window.switchDisseminationRoutingSubTab(subTab, btn);
        }
        if (typeof window.switchLocalizationGovSubTab === 'function') {
            return window.switchLocalizationGovSubTab(subTab, btn);
        }
    };
})();
