/**
 * 🌍 [V75.5] Illacme Plenipes Localization - Glossary Rendering & Pagination Shard
 * 职责：专有名词保护术语词库面板、语种 Tab 切换、分页渲染与搜索过滤控制。
 */

(function () {
    window.renderGlossaryCategory = function () {
        const gov = window.settingsData?.translation?.governance || {};
        const glossary = gov.glossary || {};
        const targets = (window.settingsData?.i18n_settings?.targets || []).map(t => typeof t === 'string' ? t : t.lang_code);
        const isLicensed = window.settingsData?._is_licensed || false;
        const activeTargets = (!isLicensed && targets.length > 1) ? [targets[0]] : targets;
        const availableLangs = window.availableLangs || [];
        const activeTargetsForTabs = activeTargets;

        if (!window.currentGlossaryLang) {
            window.currentGlossaryLang = activeTargetsForTabs.length > 0 ? activeTargetsForTabs[0] : 'en';
        }

        return `
            <div class="full-width">
                <div class="settings-group" style="margin-bottom: 2rem;">
                    <!-- 🚀 [V75.5] 语种 Tab 切换选择栏 -->
                    <div class="lang-tabs" style="display: flex; gap: 8px; align-items: center; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 12px; flex-wrap: wrap;">
                        <span style="font-size: 0.75rem; color: var(--text-dim); margin-right: 6px;">编辑语种对照表:</span>
                        ${activeTargetsForTabs.length > 0 ? activeTargetsForTabs.map(code => {
            const isTabActive = code === window.currentGlossaryLang;
            const langObj = availableLangs.find(l => l.code === code) || { name: code.toUpperCase(), icon: '🌐' };
            return `
                                <button type="button" class="mini-btn ${isTabActive ? 'active glow-btn' : ''}" 
                                        style="padding: 6px 12px; font-size: 0.72rem; border-radius: 20px; border: 1px solid ${isTabActive ? 'var(--accent-secondary)' : 'var(--glass-border)'}; cursor: pointer; height: 26px; line-height: 14px;"
                                        onclick="window.switchGlossaryLang('${code}')">
                                    ${langObj.icon} ${langObj.name}
                                </button>
                            `;
        }).join('') : `
                            <button type="button" class="mini-btn active glow-btn" style="padding: 6px 12px; font-size: 0.72rem; border-radius: 20px; border: 1px solid var(--accent-secondary); cursor: default; height: 26px; line-height: 14px;">
                                🇬🇧 English (EN)
                            </button>
                        `}
                        ${!isLicensed ? `
                            <span class="community-edition-badge" style="font-size: 0.68rem; color: #fbbf24; background: rgba(251, 191, 36, 0.1); border: 1px solid rgba(251, 191, 36, 0.25); padding: 2px 8px; border-radius: 10px; font-weight: 500; margin-left: auto; white-space: nowrap;">
                                🌱 免费社区版：单语种术语库
                            </span>
                        ` : ''}
                    </div>

                    <!-- 🔍 检索与操作控制栏 -->
                    <div style="display: flex; gap: 10px; margin-bottom: 12px; align-items: center; justify-content: space-between; flex-wrap: wrap;">
                        <div style="position: relative; flex: 1; min-width: 200px; max-width: 320px;">
                            <input type="text" id="glossary-search-input" class="setting-input" 
                                   style="width: 100%; min-height: 28px; font-size: 0.75rem; border-radius: 6px; padding: 4px 10px 4px 10px; box-sizing: border-box;" 
                                   placeholder="🔍 过滤保护词条..." value="${window.currentGlossarySearchQuery || ''}"
                                   oninput="window.onGlossarySearch(this.value)">
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <button type="button" class="mini-btn glow-btn" 
                                    style="padding: 4px 12px; font-size: 0.72rem; border-radius: 6px; border: 1px solid var(--accent-secondary); cursor: pointer; height: 28px; line-height: 18px;"
                                    onclick="window.openGlossaryImportModal()">
                                📄 批量导入 (CSV/JSON/粘贴)
                            </button>
                            <button type="button" class="mini-btn danger-btn" 
                                    style="padding: 4px 12px; font-size: 0.72rem; border-radius: 6px; border: 1px solid #ff6b6b; cursor: pointer; height: 28px; line-height: 18px; color: #ff6b6b; background: rgba(255, 107, 107, 0.05);"
                                    onclick="window.clearGlossaryCurrentLang()">
                                🧹 一键清空
                            </button>
                        </div>
                    </div>

                    <!-- 术语列表显示局部容器 -->
                    <div class="glossary-container" id="glossary-display-wrapper" style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 15px; min-height: 80px; max-height: 250px; overflow-y: auto;">
                        ${window.renderGlossaryListHtml()}
                    </div>

                    <!-- 术语新增表单 -->
                    <div style="display: flex; gap: 10px; align-items: center; background: rgba(255,255,255,0.02); padding: 12px; border-radius: 8px; border: 1px solid var(--glass-border);">
                        <input type="text" id="glossary-src-input" class="setting-input" style="flex: 1; min-height: 32px; font-size: 0.8rem; border-radius: 6px;" placeholder="原稿词汇 (例如: 物理主权)">
                        <div style="color: var(--text-dim); font-size: 0.9rem;">➡️</div>
                        <input type="text" id="glossary-dst-input" class="setting-input" style="flex: 1; min-height: 32px; font-size: 0.8rem; border-radius: 6px;" placeholder="保护译词 (${(window.currentGlossaryLang || 'en').toUpperCase()} 目标翻译词)">
                        <button class="primary-btn glow-btn" style="padding: 0 15px; height: 32px; font-size: 0.8rem; white-space: nowrap; border-radius: 6px;" onclick="window.addGlossaryItem()">＋ 添加保护词</button>
                    </div>
                </div>
            </div>
        `;
    };

    window.renderGlossaryListHtml = () => {
        const gov = window.settingsData?.translation?.governance || {};
        const glossary = gov.glossary || {};
        const glossaryForCurrentLang = glossary[window.currentGlossaryLang] || {};

        let entries = Object.entries(glossaryForCurrentLang);
        const q = (window.currentGlossarySearchQuery || '').toLowerCase().trim();
        if (q) {
            entries = entries.filter(([src, dst]) => src.toLowerCase().includes(q) || dst.toLowerCase().includes(q));
        }

        const itemsPerPage = 8;
        const totalEntries = entries.length;
        const totalPages = Math.ceil(totalEntries / itemsPerPage) || 1;

        if (window.currentGlossaryPage > totalPages) window.currentGlossaryPage = totalPages;
        if (window.currentGlossaryPage < 1) window.currentGlossaryPage = 1;

        const startIdx = (window.currentGlossaryPage - 1) * itemsPerPage;
        const paginatedEntries = entries.slice(startIdx, startIdx + itemsPerPage);

        let listHtml = "";
        if (paginatedEntries.length === 0) {
            listHtml = `
                <div style="padding: 15px; text-align: center; color: var(--text-dim); background: rgba(0,0,0,0.1); border-radius: 8px; font-size: 0.8rem; border: 1px dashed var(--glass-border);">
                    ${q ? '未检索到匹配的保护词条。' : `尚未在当前语种 [${(window.currentGlossaryLang || 'en').toUpperCase()}] 下添加任何防护术语。`}
                </div>
            `;
        } else {
            listHtml = `
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 10px;">
                    ${paginatedEntries.map(([src, dst]) => `
                        <div class="glass-panel" style="padding: 8px 12px; border-radius: 6px; border: 1px solid var(--glass-border); display: flex; justify-content: space-between; align-items: center; background: rgba(0,242,255,0.02); height: 38px; box-sizing: border-box;">
                            <div style="font-size: 0.8rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 200px;" title="${src} ➡️ ${dst}">
                                <span style="color: var(--text-bright, #fff); font-weight: 600;">${src}</span>
                                <span style="color: var(--text-dim); margin: 0 4px;">➡️</span>
                                <span style="color: var(--accent-secondary);">${dst}</span>
                            </div>
                            <span style="cursor: pointer; color: #ff6b6b; font-size: 0.9rem; padding: 2px 6px; transition: opacity 0.2s;" 
                                  onclick="window.removeGlossaryItem('${src.replace(/'/g, "\\'")}')" title="删除该保护词">🗑️</span>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        let paginationHtml = "";
        if (totalPages > 1) {
            paginationHtml = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.05); font-size: 0.75rem; color: var(--text-dim);">
                    <div>共 <b>${totalEntries}</b> 条词项</div>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <button type="button" class="mini-btn" style="padding: 2px 8px; font-size: 0.7rem; border-radius: 4px; cursor: pointer; border: 1px solid var(--glass-border);" 
                                ${window.currentGlossaryPage === 1 ? 'disabled style="opacity:0.4; cursor:default;"' : `onclick="window.changeGlossaryPage(-1)"`}>上一页</button>
                        <span>${window.currentGlossaryPage} / ${totalPages} 页</span>
                        <button type="button" class="mini-btn" style="padding: 2px 8px; font-size: 0.7rem; border-radius: 4px; cursor: pointer; border: 1px solid var(--glass-border);" 
                                ${window.currentGlossaryPage === totalPages ? 'disabled style="opacity:0.4; cursor:default;"' : `onclick="window.changeGlossaryPage(1)"`}>下一页</button>
                    </div>
                </div>
            `;
        } else if (totalEntries > 0) {
            paginationHtml = `
                <div style="margin-top: 10px; font-size: 0.7rem; color: var(--text-dim); text-align: right;">共 <b>${totalEntries}</b> 条词项</div>
            `;
        }

        return listHtml + paginationHtml;
    };

    window.refreshGlossaryUI = () => {
        const container = document.getElementById('glossary-display-wrapper');
        if (container && typeof window.renderGlossaryListHtml === 'function') {
            container.innerHTML = window.renderGlossaryListHtml();
        }
    };

    window.changeGlossaryPage = (dir) => {
        window.currentGlossaryPage += dir;
        if (typeof window.refreshGlossaryUI === 'function') {
            window.refreshGlossaryUI();
        }
    };

    window.onGlossarySearch = (query) => {
        window.currentGlossarySearchQuery = query;
        window.currentGlossaryPage = 1;
        if (typeof window.refreshGlossaryUI === 'function') {
            window.refreshGlossaryUI();
        }
    };
})();
