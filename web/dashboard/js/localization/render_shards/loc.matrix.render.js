/**
 * 🌍 [V75.5] Illacme Plenipes Localization - Matrix & Target Dissemination Shard
 * 职责：源内容语种、路径拓扑演算预览、多语言总控闸与目标分发阵列卡片渲染。
 */

(function () {
    const blockPresets = {
        header: [
            { text: '保持极其简练', value: 'Keep headings extremely concise, capitalize word initials, and avoid full sentences.' },
            { text: '动宾短语导向', value: 'Use action-oriented verb-object phrases where appropriate for guide titles.' },
            { text: '保留技术缩写', value: 'Retain specific technical abbreviations untranslated, capitalize word initials.' }
        ],
        paragraph: [
            { text: '保持自然流畅', value: 'Ensure natural readability and flow, preferring native idiomatic expressions over literal translation.' },
            { text: '学术严谨风格', value: 'Use formal, academic, and rigorous terminology suitable for official documentation.' },
            { text: '通俗口语化', value: 'Translate in an easy-to-understand, colloquial, and friendly tone.' }
        ],
        table: [
            { text: '单元格紧凑精简', value: 'Keep translation extremely compact and concise to fit within table cells, avoiding long wrapping sentences.' },
            { text: '直译保留对齐', value: 'Translate cell items literally, ensuring strict alignment with established technical definitions.' }
        ],
        callout: [
            { text: '专业亲切语气', value: 'Use an engaging, professional, and friendly tone for alerts and highlights.' },
            { text: '严肃警告语气', value: 'Maintain a strict, clear, and warning tone appropriate for caution or error panels.' }
        ],
        code: [
            { text: '仅译注释，保留代码', value: 'Translate only code comments and strings. Do not modify any code syntax, API endpoints, or variable names.' }
        ],
        html: [
            { text: '仅译内文，保留属性', value: 'Only translate the inner text of HTML tags. Do not modify tag names or attributes (such as class, id, href).' }
        ],
        comment: [
            { text: '工作流日志风', value: 'Translate TODOs and draft comments into a simple, professional work-log style.' }
        ]
    };

    // 挂载至全局以便在 sync 模块中读取
    window.blockPresets = blockPresets;

    window.renderLocalizationCategory = function () {
        if (window.currentGlossarySearchQuery === undefined) window.currentGlossarySearchQuery = "";
        if (window.currentGlossaryPage === undefined) window.currentGlossaryPage = 1;

        const i18n = window.settingsData?.i18n_settings || {};
        const mode = window.settingsData?.governance?.publishing_mode || 'basic';
        const isGlobal = mode === 'global';
        const isEnabled = isGlobal ? (i18n.enabled !== false) : false; // 默认为 true，但非 global 模式强制为 false
        const sourceLangStr = i18n.source?.lang_code || 'auto';
        const targets = (i18n.targets || []).map(t => typeof t === 'string' ? t : t.lang_code);
        const isLicensed = window.settingsData?._is_licensed || false;

        // 🚀 [V57.4] 完美支持授权限制：如果是非授权社区版，强力规整只激活前 1 个选中的语种卡片，其余在界面上自愈为锁定态
        const activeTargets = (!isLicensed && targets.length > 1) ? [targets[0]] : targets;
        const availableLangs = window.availableLangs || [];

        // 🚀 [V75.7] 物理多语言总开关：解开模式死锁，根据 enable_ai 进行智能准入
        const enableAi = window.settingsData?.translation?.enable_ai !== false;
        let descriptionText = '';
        if (!enableAi) {
            descriptionText = '🔒 <b>未开启 AI 算力总控，多语言翻译矩阵处于离线关闭状态</b>（模式：基础物理出版 Basic）。';
        } else if (isGlobal) {
            descriptionText = '⚡ <b>多语言翻译矩阵已激活</b>。系统将使用 AI 将您的原稿翻译并分发至多国语言路径（模式：全球出版模式 Global）。';
        } else {
            descriptionText = '💡 <b>多语言翻译矩阵目前已关闭</b>。系统仅在母语下执行 AI SEO 与智能润色，原稿内容自动透传至多语言路径（模式：智能母语增强 Enhanced）。点击开启将自动切换至全球出版模式。';
        }

        const renderItem = window.renderSettingsItem || (() => '');
        const enabledSwitchHtml = renderItem(
            '多语言翻译矩阵',
            'i18n_settings.enabled',
            i18n.enabled !== false && isGlobal,
            'checkbox',
            {
                onchange: 'window.syncI18nEnabled(this.checked)',
                description: descriptionText,
                disabled: !enableAi
            }
        );

        return `
            <div class="full-width">
                <!-- 1. 源内容语种（上移并常驻，不受开关控制） -->
                <div class="settings-group" style="margin-bottom: 2rem;">
                    <h4>🎯 源内容语种 (Source Sovereignty)</h4>
                    ${renderItem('主出版语种', 'i18n_settings.source.lang_code', sourceLangStr, 'select', {
            items: [
                { value: 'auto', text: '✨ 自动探测 (Auto Detect)' },
                ...availableLangs.map(l => ({ value: l.code, text: `${l.icon} ${l.name}` }))
            ],
            onchange: 'syncI18nSource(this.value)'
        })}
                    ${renderItem('主语言路径前缀强制化', 'i18n_settings.force_source_prefix', i18n.force_source_prefix || false, 'checkbox', {
            onchange: 'window.syncI18nForcePrefix(this.checked)',
            description: '决定主语言（如中文）在发布后是否拥有独立的路径前缀（如 /zh/）。开启后所有语种完全对称；关闭后主语言直接落盘至站点根路径。'
        })}
                    <div class="path-simulator-box" id="path-simulator-preview">
                        <div class="sim-label">🗺️ 物理拓扑演算预览 (Path Topology Simulator)</div>
                        <div style="display: flex; flex-direction: column; gap: 4px; margin-top: 4px;">
                            <div>• <b>主出版语言</b>: <span class="sim-url" id="sim-url-source">${i18n.force_source_prefix ? '/zh/docs/quick-start.html' : '/docs/quick-start.html (根目录扁平化)'}</span></div>
                            <div>• <b>多语言目标</b>: <span class="sim-url" id="sim-url-target">/en/docs/quick-start.html</span></div>
                        </div>
                        <div class="sim-note">💡 提示：更改此配置会改变全站物理 URL 拓扑。保存后需执行<b>「⚡ 开始发布」</b>重新编译生成静态网页与全局索引。</div>
                    </div>
                </div>

                <!-- 3. 多语言翻译矩阵开关总控闸 -->
                <div id="i18n-enable-control-group" class="settings-group" style="margin-bottom: 2rem;">
                    ${enabledSwitchHtml}
                </div>
                
                <!-- 4. 目标分发阵列与高级翻译治理（仅当 isEnabled 为开启时才渲染显示） -->
                ${isEnabled ? `
                    <div id="target-dissemination-group" style="margin-top: 1.8rem;">
                        <div class="section-header" style="display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 8px; flex-wrap: wrap;">
                            <h4 style="margin: 0; font-size: 0.95rem;">🛰️ 目标分发阵列 (Target Dissemination)</h4>
                            ${!isLicensed ? `
                                <span class="community-edition-badge" style="font-size: 0.68rem; color: #fbbf24; background: rgba(251, 191, 36, 0.1); border: 1px solid rgba(251, 191, 36, 0.25); padding: 2px 8px; border-radius: 10px; font-weight: 500; display: inline-flex; align-items: center; gap: 4px; white-space: nowrap;">
                                    🌱 免费社区版：仅限 1 个目标语种
                                </span>
                            ` : ''}
                        </div>
                        <div class="lang-matrix">
                            ${availableLangs
                    .filter(l => sourceLangStr === 'auto' || l.code !== sourceLangStr)
                    .map(l => {
                        const isSelected = activeTargets.includes(l.code);
                        const isLocked = !isLicensed && !isSelected && activeTargets.length >= 1;
                        const cardTitle = isLocked ? '点击一键置换为此语种' : '';
                        return `
                                                <div class="lang-card ${isSelected ? 'active' : ''} ${isLocked ? 'locked' : ''}" 
                                                     ${cardTitle ? `title="${cardTitle}"` : ''}
                                                     onclick="window.toggleI18nTarget(this, '${l.code}')">
                                                    <span style="font-size: 1.15rem; line-height: 1;">${l.icon}</span>
                                                    <div style="display: flex; flex-direction: column; gap: 1px; align-items: center;">
                                                        <span style="font-size: 0.78rem; font-weight: 600; color: var(--text-bright, #ffffff); line-height: 1.2;">${l.name}</span>
                                                        <span style="font-size: 0.6rem; color: var(--text-dim); line-height: 1;">${l.code.toUpperCase()}</span>
                                                    </div>
                                                </div>`;
                    }).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    };
})();
