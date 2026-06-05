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

window.translationStyles = {
    professional: {
        name: "💼 商务专业 (Professional)",
        badge: "商用",
        desc: "正式、严谨，采用严密的行业术语，适用于商业报告、官方规范与业务文档。",
        translate: "You are a professional translator. Translate the following Markdown content from {source_lang} to {target_lang}. Keep all Markdown syntax, frontmatter keys, and LaTeX formulas intact. Use formal tone and professional vocabulary. Do not add any explanations.",
        title: "You are a professional editor. Translate and polish the following title into {target_lang}. Keep it concise, formal, and professional. Output ONLY the title.",
        meta: "You are a professional editor. Translate and polish the provided metadata into {target_lang} using formal terminology. Output ONLY the result."
    },
    casual: {
        name: "💬 活泼随性 (Casual)",
        badge: "日常",
        desc: "口语化、自然亲切，注重本地读者的日常表达，适用于个人随笔、博客分享与社媒文案。",
        translate: "You are a friendly translator. Translate the following Markdown content from {source_lang} to {target_lang} in a natural, conversational tone. Keep all Markdown syntax and frontmatter intact. Do not add any explanations.",
        title: "You are a creative editor. Translate the following title into {target_lang} in a catchy, natural, and conversational way. Output ONLY the title.",
        meta: "You are a creative editor. Translate the provided metadata into {target_lang} using natural, modern language. Output ONLY the result."
    },
    literal: {
        name: "🔍 精准直译 (Literal)",
        badge: "直译",
        desc: "结构对称、忠于原文，尽可能保留句型与字面对应，适用于学术条约及比对校验场景。",
        translate: "You are a precise translator. Translate the following Markdown content from {source_lang} to {target_lang} literally, preserving the original structure and word choice as much as possible. Keep all Markdown syntax intact. Do not add any explanations.",
        title: "You are a precise translator. Translate the following title into {target_lang} as literally as possible. Output ONLY the title.",
        meta: "You are a precise translator. Translate the provided metadata into {target_lang} literally. Output ONLY the result."
    },
    academic: {
        name: "🎓 学术客观 (Academic)",
        badge: "学术",
        desc: "客观严谨、使用被动语态与书面学术用词，完美保留 LaTeX 复杂公式与文献脚注。",
        translate: "You are an academic translator. Translate the following Markdown research paper from {source_lang} to {target_lang}. Use formal academic style, precise terminology, and objective tone. Maintain all LaTeX mathematical environments, footnotes, citations, and Markdown markup intact. Do not alter the formatting.",
        title: "You are a scholarly editor. Translate the following paper title into {target_lang} with high academic accuracy. Output ONLY the title.",
        meta: "You are a scholarly editor. Translate the following metadata into {target_lang} using academic terminology. Output ONLY the result."
    },
    technical: {
        name: "💻 技术极客 (Technical)",
        badge: "技术",
        desc: "面向开发者与工程师，保留通用技术名词不予硬译，完美对齐行内代码与代码块结构。",
        translate: "You are a technical translator specializing in computer science. Translate the following developer documentation from {source_lang} to {target_lang}. Keep industry standard terms (e.g., 'API', 'Docker', 'GIL') in English. Keep all code blocks, inline code, and formatting strictly unchanged.",
        title: "You are a technical writer. Translate the following technical article title into {target_lang}, retaining essential technical terms in English. Output ONLY the title.",
        meta: "You are a technical writer. Translate the following metadata into {target_lang}, preserving standard technology terms. Output ONLY the result."
    },
    literary: {
        name: "🎭 文学唯美 (Literary)",
        badge: "信达雅",
        desc: "意境重于字词、行文优雅且追求文学感官，适用于散文随笔、故事创作与诗歌小说。",
        translate: "You are a literary translator. Translate the following prose from {source_lang} to {target_lang} with an emphasis on tone, style, and flow. Capture the emotional resonance and elegance of the original text. Maintain all Markdown formatting. Avoid literal translation where a more elegant expression exists.",
        title: "You are a literary editor. Translate the following title into {target_lang} with poetic beauty. Output ONLY the title.",
        meta: "You are a literary editor. Translate the following metadata into {target_lang} with high literary elegance. Output ONLY the result."
    }
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
    const ts = prompts.translate_system || '';

    // 智能反向推导当前属于哪个风格预设
    let activeStyleKey = 'custom';
    for (const [key, tpl] of Object.entries(window.translationStyles)) {
        if (tpl.translate === ts) {
            activeStyleKey = key;
            break;
        }
    }
    if (!ts && !prompts.title_system && !prompts.metadata_system) {
        activeStyleKey = 'professional'; // 默认值
    }

    const currentStyle = window.translationStyles[activeStyleKey] || {
        badge: "自定义",
        desc: "正在使用专属于该品牌的个性化翻译 Prompt 模板。",
        translate: ts,
        title: prompts.title_system || '',
        meta: prompts.metadata_system || ''
    };

    return `
        <div class="full-width">
            <div class="section-header"><h3>🎭 全域翻译风格 (Universal Style)</h3></div>
            <p style="color: var(--text-dim); font-size: 0.85rem; margin-bottom: 1.5rem;">设定当前品牌在全球化分发中所采用的语感模板，强制对正全量算力输出。</p>
            
            <div class="settings-grid">
                <div class="settings-group">
                    <h4>🌐 风格预设 (Preset Templates)</h4>
                    <div style="display: flex; gap: 15px; align-items: center; margin-bottom: 15px;">
                        <select id="style-selector" class="setting-input" onchange="window.updateStylePreview(this.value)" style="flex: 1; min-height: 38px;">
                            ${Object.entries(window.translationStyles).map(([key, tpl]) => `
                                <option value="${key}" ${key === activeStyleKey ? 'selected' : ''}>${tpl.name}</option>
                            `).join('')}
                            <option value="custom" ${activeStyleKey === 'custom' ? 'selected' : ''}>✍️ 自定义风格 (Custom Prompt)</option>
                        </select>
                        <button class="primary-btn" onclick="applyTranslationStyle()" style="white-space: nowrap; min-height: 38px; display: flex; align-items: center; gap: 6px;">
                            <span>⚡</span> 应用此风格
                        </button>
                    </div>
                    
                    <!-- 风格详情卡片描述区 -->
                    <div id="style-description-box" style="padding: 12px 16px; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; background: rgba(var(--bg-rgb), 0.2); font-size: 0.8rem; line-height: 1.5; color: var(--text-normal); margin-bottom: 20px; display: flex; align-items: center; gap: 12px; transition: all 0.3s ease;">
                        <span style="background: var(--accent-secondary, #00f2ff); color: var(--bg-solid, #000); padding: 2px 6px; border-radius: 4px; font-weight: 800; font-size: 0.7rem;">${currentStyle.badge}</span>
                        <p style="margin: 0; font-weight: 500;">${currentStyle.desc}</p>
                    </div>

                    <!-- Prompt 编辑与展示区 (等宽字体、高对比底色与外框，上下依次垂直排列：标题 -> 正文 -> 元数据) -->
                    <div class="prompt-wrapper" style="display: flex; flex-direction: column; gap: 15px; margin-top: 15px;">
                        <!-- 1. 标题翻译 Prompt -->
                        <div style="display: flex; flex-direction: column; gap: 6px;">
                            <span style="font-size: 0.75rem; font-weight: 600; color: var(--text-bright, #ffffff); opacity: 0.85; display: flex; align-items: center; gap: 6px;">
                                📌 标题翻译 Prompt 模板 (Title)
                            </span>
                            <textarea id="prompt-preview-title" oninput="window.checkStyleMatch()" 
                                      onfocus="if(!this.hasAttribute('readonly')) { this.style.borderColor='var(--accent-primary)'; this.style.boxShadow='0 0 10px rgba(var(--accent-primary-rgb), 0.3)'; }" 
                                      onblur="if(!this.hasAttribute('readonly')) { this.style.borderColor='rgba(var(--accent-primary-rgb), 0.25)'; this.style.boxShadow='none'; } else { this.style.borderColor='var(--glass-border)'; }"
                                      ${activeStyleKey !== 'custom' ? 'readonly' : ''}
                                      style="width: 100%; box-sizing: border-box; font-family: 'Fira Code', Consolas, Monaco, monospace; font-size: 0.72rem; padding: 12px 16px; 
                                             background: ${activeStyleKey === 'custom' ? 'var(--bg-agent-input)' : 'rgba(var(--bg-modal-solid-rgb, 13, 14, 28), 0.5)'}; 
                                             border: ${activeStyleKey === 'custom' ? '1.5px solid rgba(var(--accent-primary-rgb), 0.25)' : '1px solid var(--glass-border)'}; 
                                             border-radius: 8px; color: var(--text-bright, #ffffff); min-height: 60px; resize: vertical; line-height: 1.5; outline: none; transition: all 0.2s ease;
                                             cursor: ${activeStyleKey === 'custom' ? 'text' : 'default'};">${currentStyle.title || ''}</textarea>
                        </div>

                        <!-- 2. 正文翻译 Prompt -->
                        <div style="display: flex; flex-direction: column; gap: 6px;">
                            <span style="font-size: 0.75rem; font-weight: 600; color: var(--text-bright, #ffffff); opacity: 0.85; display: flex; align-items: center; gap: 6px;">
                                📄 正文翻译 Prompt 模板 (Markdown Content)
                            </span>
                            <textarea id="prompt-preview-translate" oninput="window.checkStyleMatch()" 
                                      onfocus="if(!this.hasAttribute('readonly')) { this.style.borderColor='var(--accent-primary)'; this.style.boxShadow='0 0 10px rgba(var(--accent-primary-rgb), 0.3)'; }" 
                                      onblur="if(!this.hasAttribute('readonly')) { this.style.borderColor='rgba(var(--accent-primary-rgb), 0.25)'; this.style.boxShadow='none'; } else { this.style.borderColor='var(--glass-border)'; }"
                                      ${activeStyleKey !== 'custom' ? 'readonly' : ''}
                                      style="width: 100%; box-sizing: border-box; font-family: 'Fira Code', Consolas, Monaco, monospace; font-size: 0.72rem; padding: 12px 16px; 
                                             background: ${activeStyleKey === 'custom' ? 'var(--bg-agent-input)' : 'rgba(var(--bg-modal-solid-rgb, 13, 14, 28), 0.5)'}; 
                                             border: ${activeStyleKey === 'custom' ? '1.5px solid rgba(var(--accent-primary-rgb), 0.25)' : '1px solid var(--glass-border)'}; 
                                             border-radius: 8px; color: var(--text-bright, #ffffff); min-height: 80px; resize: vertical; line-height: 1.5; outline: none; transition: all 0.2s ease;
                                             cursor: ${activeStyleKey === 'custom' ? 'text' : 'default'};">${currentStyle.translate || ''}</textarea>
                        </div>

                        <!-- 3. 网页元数据 Prompt -->
                        <div style="display: flex; flex-direction: column; gap: 6px;">
                            <span style="font-size: 0.75rem; font-weight: 600; color: var(--text-bright, #ffffff); opacity: 0.85; display: flex; align-items: center; gap: 6px;">
                                🏷️ 网页元数据 Prompt 模板 (Metadata)
                            </span>
                            <textarea id="prompt-preview-meta" oninput="window.checkStyleMatch()" 
                                      onfocus="if(!this.hasAttribute('readonly')) { this.style.borderColor='var(--accent-primary)'; this.style.boxShadow='0 0 10px rgba(var(--accent-primary-rgb), 0.3)'; }" 
                                      onblur="if(!this.hasAttribute('readonly')) { this.style.borderColor='rgba(var(--accent-primary-rgb), 0.25)'; this.style.boxShadow='none'; } else { this.style.borderColor='var(--glass-border)'; }"
                                      ${activeStyleKey !== 'custom' ? 'readonly' : ''}
                                      style="width: 100%; box-sizing: border-box; font-family: 'Fira Code', Consolas, Monaco, monospace; font-size: 0.72rem; padding: 12px 16px; 
                                             background: ${activeStyleKey === 'custom' ? 'var(--bg-agent-input)' : 'rgba(var(--bg-modal-solid-rgb, 13, 14, 28), 0.5)'}; 
                                             border: ${activeStyleKey === 'custom' ? '1.5px solid rgba(var(--accent-primary-rgb), 0.25)' : '1px solid var(--glass-border)'}; 
                                             border-radius: 8px; color: var(--text-bright, #ffffff); min-height: 60px; resize: vertical; line-height: 1.5; outline: none; transition: all 0.2s ease;
                                             cursor: ${activeStyleKey === 'custom' ? 'text' : 'default'};">${currentStyle.meta || ''}</textarea>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
};
