/**
 * 🌍 [V75.5] Illacme Plenipes Localization Rendering Module
 * 职责：全球分发矩阵多语种阵列 HTML 面板拼装、总控开关与级联隐藏渲染、Lite/Pro 授权旗帜渲染。
 * 包含：翻译高级治理（超链接自愈、块级翻译规则矩阵、多语种对照表）的可视化面板。
 */

window.renderLocalizationCategory = function () {
    const i18n = window.settingsData.i18n_settings || {};
    const mode = window.settingsData.governance?.publishing_mode || 'basic';
    const isGlobal = mode === 'global';
    const isEnabled = isGlobal ? (i18n.enabled !== false) : false; // 默认为 true，但非 global 模式强制为 false
    const sourceLangStr = i18n.source?.lang_code || 'auto';
    const targets = (i18n.targets || []).map(t => typeof t === 'string' ? t : t.lang_code);
    const isLicensed = window.settingsData._is_licensed || false;

    // 🚀 [V75.0] 高级翻译治理局部变量
    const gov = window.settingsData.translation?.governance || {};
    const lg = gov.link_governance || {};
    const blockRules = gov.block_rules || {};
    const glossary = gov.glossary || {};

    const blockTypes = {
        header: { name: '📌 标题块 (Header)', desc: 'Markdown 中的各级标题。' },
        paragraph: { name: '📄 正文段落 (Paragraph)', desc: 'Markdown 中的一般段落文本。' },
        table: { name: '📊 表格内容 (Table)', desc: 'Markdown 中的数据表格。' },
        callout: { name: '💡 提示卡片 (Callout)', desc: '各种高亮提示框（如 > [!NOTE] ）。' },
        code: { name: '💻 代码块 (Code Block)', desc: 'Markdown 代码围栏块。' },
        html: { name: '🌐 HTML 块', desc: 'Markdown 中嵌入的原生 HTML 元素。' },
        comment: { name: '💬 行内/块级注释', desc: '原稿中以特定语法标记的草稿/Todo 注释。' }
    };

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

    // 🚀 [V57.4] 完美支持授权限制：如果是非授权社区版，强力规整只激活前 1 个选中的语种卡片，其余在界面上自愈为锁定态
    const activeTargets = (!isLicensed && targets.length > 1) ? [targets[0]] : targets;
    const availableLangs = window.availableLangs || [];

    // 🚀 [V75.5] 确立当前术语对照表编辑的目标语种 Tab
    const activeTargetsForTabs = activeTargets;
    if (!window.currentGlossaryLang) {
        window.currentGlossaryLang = activeTargetsForTabs.length > 0 ? activeTargetsForTabs[0] : 'en';
    } else if (!activeTargetsForTabs.includes(window.currentGlossaryLang) && activeTargetsForTabs.length > 0) {
        window.currentGlossaryLang = activeTargetsForTabs[0];
    }
    const glossaryForCurrentLang = glossary[window.currentGlossaryLang] || {};

    // 🚀 [V57.4] 渲染物理多语言总开关
    let descriptionText = '控制多语言与全域 AI 翻译的开关。关闭后，发布流水线将挂起所有 AI 翻译作业，仅发布源原稿。';
    if (!isGlobal) {
        const modeText = mode === 'basic' ? '基础模式 (Basic)' : '增强模式 (Enhanced)';
        descriptionText = `⚠️ <b>由于当前印记处于 ${modeText}，多语言翻译总控已锁定关闭</b>。在此模式下，系统将自动透传原稿内容至多语言路径，无须执行多语言翻译矩阵。若要启用完整的 AI 多语言翻译，请在印记设置中切换为“全球出版模式 (Global)”。`;
    }

    const enabledSwitchHtml = window.renderSettingsItem(
        '多语言翻译矩阵', 
        'i18n_settings.enabled', 
        isEnabled, 
        'checkbox', 
        {
            onchange: 'window.syncI18nEnabled(this.checked)',
            description: descriptionText,
            disabled: !isGlobal
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
            
            <!-- 4. 目标分发阵列与高级翻译治理（仅当 isEnabled 为开启时才渲染显示） -->
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

                <div id="translation-governance-group" style="margin-top: 3rem; border-top: 1px dashed var(--glass-border); padding-top: 2.5rem;">
                    <div class="section-header"><h3>🛡️ 翻译高级治理 (Advanced Translation Governance)</h3></div>
                    <p class="section-desc" style="margin-bottom: 20px;">配置 Markdown 各模块在 AI 编译过程中的块级分流动作、词汇隔离保护与超链接自愈策略。</p>

                    <!-- A. 超链接治理卡片 -->
                    <div class="settings-group" style="margin-bottom: 2rem; display: flex; flex-direction: column; gap: 10px;">
                        <h4 style="color: var(--accent-secondary); margin-bottom: 5px; font-size: 0.95rem; font-family: 'JetBrains Mono', monospace;">🔗 链接与锚点对准 (Link & Anchor Resolution)</h4>
                        ${window.renderSettingsItem('翻译链接标题 (Translate Link Labels)', 'translation.governance.link_governance.translate_labels', lg.translate_labels ?? true, 'checkbox', {
                            onchange: "window.syncTranslationGovernanceField('translation.governance.link_governance.translate_labels', this.checked)",
                            description: '是否自动将超链接 Markdown 文本的中文标题部分通过 AI 翻译为目标语种。'
                        })}
                        ${window.renderSettingsItem('翻译哈希锚点 (Translate Anchor Hashes)', 'translation.governance.link_governance.translate_anchors', lg.translate_anchors ?? true, 'checkbox', {
                            onchange: "window.syncTranslationGovernanceField('translation.governance.link_governance.translate_anchors', this.checked)",
                            description: '开启后，AI 将自动翻译锚点文本并按规范清洗为小写连字符格式（如 #1-安装与准备 -> #1-install-and-prepare），用于 SSG 框架页内精准定位自愈。'
                        })}
                        ${window.renderSettingsItem('内链多语言路径自愈 (Auto-Localize Internal Links)', 'translation.governance.link_governance.auto_localize_internal_links', lg.auto_localize_internal_links ?? true, 'checkbox', {
                            onchange: "window.syncTranslationGovernanceField('translation.governance.link_governance.auto_localize_internal_links', this.checked)",
                            description: '开启后，对于类似 ./getting-started.html 的本站内部链接，系统将自动映射检测是否有对应语种的副本，并自动转换前缀为目标语言目录，防止跳转错位。'
                        })}
                        ${window.renderSettingsItem('外部超链接掩码模式', 'translation.governance.link_governance.external_links_mask_mode', lg.external_links_mask_mode || 'url_only', 'select', {
                            items: [
                                { value: 'url_only', text: '🔒 仅保护 URL (url_only)' },
                                { value: 'all', text: '🔒 完整保护链接 (all)' },
                                { value: 'none', text: '🔓 不执行保护 (none)' }
                            ],
                            onchange: "window.syncTranslationGovernanceField('translation.governance.link_governance.external_links_mask_mode', this.value)",
                            description: '配置外部超链接在发送给大模型时的遮蔽脱敏策略。推荐使用 url_only，在防止大模型篡改 URL 的同时允许翻译链接文字。'
                        })}
                    </div>

                    <!-- B. 块行为流控卡片 -->
                    <div class="settings-group" style="margin-bottom: 2.5rem;">
                        <h4 style="color: var(--accent-secondary); margin-bottom: 5px; font-size: 0.95rem; font-family: 'JetBrains Mono', monospace;">🧱 块级分流规则矩阵 (Block-Level Dispatch Rules)</h4>
                        <p class="section-desc" style="margin-bottom: 15px;">通过对 Markdown 不同的切片语义块类型指定独立 Action，实现精准的行文级流控。</p>
                        <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 15px;">
                            ${Object.entries(blockTypes).map(([key, info]) => {
                                const rule = blockRules[key] || {};
                                const action = rule.action || (key === 'code' || key === 'html' || key === 'comment' ? 'bypass' : 'translate');
                                const overrideVal = rule.prompt_override || '';
                                const isChecked = !!overrideVal;
                                const presets = blockPresets[key] || [];
                                return `
                                <div class="glass-panel" style="padding: 16px 20px; border-radius: 8px; border: 1px solid var(--glass-border); display: flex; justify-content: space-between; align-items: center; gap: 15px;">
                                    <div style="flex: 1; min-width: 0;">
                                        <div style="font-weight: 700; font-size: 0.88rem; color: var(--text-bright, #fff);">${info.name}</div>
                                        <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 2px; line-height: 1.4; word-break: break-word;">${info.desc}</div>
                                    </div>
                                    <div style="display: flex; align-items: center; gap: 12px; flex-shrink: 0;">
                                        <select class="setting-input" style="min-width: 180px; min-height: 32px; font-size: 0.78rem; border-radius: 6px;" 
                                                onchange="window.handleBlockActionChange('${key}', this.value)">
                                            <option value="translate" ${action === 'translate' ? 'selected' : ''}>🌐 AI 翻译该块内容</option>
                                            <option value="bypass" ${action === 'bypass' ? 'selected' : ''}>⏩ 原样跳过 (Bypass)</option>
                                            <option value="strip" ${action === 'strip' ? 'selected' : ''}>🗑️ 物理抹除 (Strip)</option>
                                            <option value="parse_comments_only" ${action === 'parse_comments_only' ? 'selected' : ''}>💬 仅提取并翻译注释</option>
                                        </select>
                                        ${(action === 'translate' || action === 'parse_comments_only') ? `
                                            <label style="font-size: 0.78rem; color: var(--text-bright, #fff); display: flex; align-items: center; gap: 6px; cursor: pointer; user-select: none; margin-left: 8px;">
                                                <input type="checkbox" id="checkbox-override-${key}" ${overrideVal ? 'checked' : ''} 
                                                       onchange="window.handleOverrideToggle('${key}', this.checked)"
                                                       style="accent-color: var(--accent-secondary); width: 15px; height: 15px; cursor: pointer;">
                                                ✍️ 提示词微调
                                            </label>
                                        ` : ''}
                                    </div>
                                </div>
                                
                                <!-- 提示词微调抽屉 -->
                                <div id="override-drawer-${key}" style="display: ${overrideVal ? 'block' : 'none'}; border-top: 1px dashed rgba(255,255,255,0.05); padding: 12px; margin-top: -8px; background: rgba(0,0,0,0.08); border-radius: 0 0 8px 8px; margin-bottom: 8px;">
                                    <div id="override-input-area-${key}" style="margin-top: 0px;">
                                        <textarea class="setting-input" id="textarea-override-${key}" style="width: 100%; min-height: 55px; font-family: monospace; font-size: 0.72rem; padding: 8px; box-sizing: border-box; border-radius: 6px; outline: none; background: rgba(0,0,0,0.25);" 
                                                  placeholder="例如：保持口语化，不要过分生硬；或者：专有术语翻译成学术名称。"
                                                  onchange="window.handleOverrideChange('${key}', this.value)">${overrideVal}</textarea>
                                        
                                        ${presets.length > 0 ? `
                                            <div style="margin-top: 8px; display: flex; flex-direction: column; gap: 4px;">
                                                <span style="font-size: 0.65rem; color: var(--text-dim);">💡 点击推荐预设快速填入并保存：</span>
                                                <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                                                    ${presets.map(p => `
                                                        <span class="preset-tag" 
                                                              style="font-size: 0.65rem; padding: 2px 8px; background: rgba(255,255,255,0.04); border: 1px solid var(--glass-border); border-radius: 12px; cursor: pointer; color: var(--accent-primary); transition: all 0.2s;"
                                                              onmouseover="this.style.background='rgba(0, 242, 255, 0.08)'; this.style.borderColor='var(--accent-primary)';"
                                                              onmouseout="this.style.background='rgba(255, 255, 255, 0.04)'; this.style.borderColor='var(--glass-border)';"
                                                              onclick="window.applyOverridePreset('${key}', '${p.value.replace(/'/g, "\\'")}')"
                                                              title="${p.value}">
                                                            ${p.text}
                                                        </span>
                                                    `).join('')}
                                                </div>
                                            </div>
                                        ` : ''}
                                    </div>
                                </div>
                                `;
                            }).join('')}
                        </div>
                    </div>

                    <!-- C. 专有名词与术语表 -->
                    <div class="settings-group" style="margin-bottom: 2rem;">
                        <h4 style="color: var(--accent-secondary); margin-bottom: 5px; font-size: 0.95rem; font-family: 'JetBrains Mono', monospace;">🎯 术语与专有名词屏护对照表 (Glossary Protection)</h4>
                        <p class="section-desc" style="margin-bottom: 15px;">在此添加专属于您品牌的专有名词（如系统名称、特色名词）。系统在 AI 翻译前将对其进行物理隔离屏护，大模型翻译还原后自动无损重填，确保 100% 不发生脑补 and 错译。</p>
                        
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
                        </div>

                        <!-- 术语列表显示 -->
                        <div class="glossary-container" style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 15px; max-height: 250px; overflow-y: auto;">
                            ${Object.keys(glossaryForCurrentLang).length === 0 ? `
                                <div style="padding: 15px; text-align: center; color: var(--text-dim); background: rgba(0,0,0,0.1); border-radius: 8px; font-size: 0.8rem; border: 1px dashed var(--glass-border);">
                                    尚未在当前语种 [${window.currentGlossaryLang.toUpperCase()}] 下添加任何防护术语。在下方输入并添加。
                                </div>
                            ` : `
                                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 10px;">
                                    ${Object.entries(glossaryForCurrentLang).map(([src, dst]) => `
                                        <div class="glass-panel" style="padding: 8px 12px; border-radius: 6px; border: 1px solid var(--glass-border); display: flex; justify-content: space-between; align-items: center; background: rgba(0,242,255,0.02);">
                                            <div style="font-size: 0.8rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 200px;">
                                                <span style="color: var(--text-bright, #fff); font-weight: 600;">${src}</span>
                                                <span style="color: var(--text-dim); margin: 0 4px;">➡️</span>
                                                <span style="color: var(--accent-secondary);">${dst}</span>
                                            </div>
                                            <span style="cursor: pointer; color: #ff6b6b; font-size: 0.9rem; padding: 2px 6px; transition: opacity 0.2s;" 
                                                  onclick="window.removeGlossaryItem('${src.replace(/'/g, "\\'")}')" title="删除该保护词">🗑️</span>
                                        </div>
                                    `).join('')}
                                </div>
                            `}
                        </div>

                        <!-- 术语新增表单 -->
                        <div style="display: flex; gap: 10px; align-items: center; background: rgba(255,255,255,0.02); padding: 12px; border-radius: 8px; border: 1px solid var(--glass-border);">
                            <input type="text" id="glossary-src-input" class="setting-input" style="flex: 1; min-height: 32px; font-size: 0.8rem; border-radius: 6px;" placeholder="原稿词汇 (例如: 物理主权)">
                            <div style="color: var(--text-dim); font-size: 0.9rem;">➡️</div>
                            <input type="text" id="glossary-dst-input" class="setting-input" style="flex: 1; min-height: 32px; font-size: 0.8rem; border-radius: 6px;" placeholder="保护译词 (${window.currentGlossaryLang.toUpperCase()} 目标翻译词)">
                            <button class="primary-btn glow-btn" style="padding: 0 15px; height: 32px; font-size: 0.8rem; white-space: nowrap; border-radius: 6px;" onclick="window.addGlossaryItem()">＋ 添加保护词</button>
                        </div>
                    </div>
                </div>
            ` : ''}
        </div>
    `;
};
