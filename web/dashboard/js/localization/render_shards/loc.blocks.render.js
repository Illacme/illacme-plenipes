/**
 * 🌍 [V75.5] Illacme Plenipes Localization - Block Rules & Links Governance Shard
 * 职责：多段合并翻译中枢、链接与跳转对准、各类型正文块规则与提示词微调抽屉渲染。
 */

(function () {
    window.renderBlockRulesCategory = function () {
        const gov = window.settingsData?.translation?.governance || {};
        const lg = gov.link_governance || {};
        const bg = gov.batch_translation || {};
        const blockRules = gov.block_rules || {};
        const blockTypes = {
            header: { name: '📌 标题 (Header)', desc: 'Markdown 各级大纲标题。' },
            paragraph: { name: '📄 正文段落 (Paragraph)', desc: '普通正文段落文本。' },
            table: { name: '📊 表格内容 (Table)', desc: '数据表格及表头表尾。' },
            callout: { name: '💡 提示框 (Callout)', desc: 'Note、Tip、Warning 等高亮提示卡片。' },
            code: { name: '💻 代码块 (Code Block)', desc: '代码围栏块（默认原样跳过不翻译）。' },
            html: { name: '🌐 HTML 标签 (HTML Block)', desc: '正文中嵌入的原生 HTML 元素。' },
            comment: { name: '💬 原稿注释 (Comments)', desc: '文稿中的草稿、TODO 或备注注释。' }
        };
        const blockPresets = window.blockPresets || {};
        const renderItem = window.renderSettingsItem || (() => '');

        return `
            <div class="full-width">
                <!-- 🚀 多段合并翻译中枢 -->
                <div class="settings-group" style="margin-bottom: 2rem; display: flex; flex-direction: column; gap: 10px;">
                    <h4 style="color: var(--accent-secondary); margin-bottom: 5px; font-size: 0.95rem; font-family: 'JetBrains Mono', monospace;">🚀 多段合并翻译 (Batch Translation)</h4>
                    <p class="section-desc" style="margin-bottom: 10px;">将相邻段落合并为单次请求发给 AI，大幅加快整篇翻译速度、降低 API 调用开销与限流概率，同时让 AI 联系上下文翻译得更连贯。</p>
                    ${renderItem('启用多段合并翻译 (Enable Batch Translation)', 'translation.governance.batch_translation.enabled', bg.enabled ?? true, 'checkbox', {
            onchange: "window.syncTranslationGovernanceField('translation.governance.batch_translation.enabled', this.checked)",
            description: '开启后系统将自动合并相邻段落发起请求，大幅提升全文翻译速度与行文连贯性。关闭则逐段独立翻译。'
        })}
                    ${renderItem('单次最多合并段落数 (Max Paragraphs per Batch)', 'translation.governance.batch_translation.max_batch_paras', bg.max_batch_paras ?? 8, 'number', {
            min: 1, max: 30, step: 1, unit: '段',
            onchange: "window.syncTranslationGovernanceField('translation.governance.batch_translation.max_batch_paras', parseInt(this.value, 10))",
            description: '每个批次最多合并的物理段落数量（推荐 6~10 段）。'
        })}
                    ${renderItem('单次最大合并字数 (Max Chars per Batch)', 'translation.governance.batch_translation.max_batch_chars', bg.max_batch_chars ?? 1500, 'number', {
            min: 200, max: 10000, step: 100, unit: '字',
            onchange: "window.syncTranslationGovernanceField('translation.governance.batch_translation.max_batch_chars', parseInt(this.value, 10))",
            description: '单次合并请求的最大字数上限。针对中文原稿推荐 1500 字，英文等拉丁语系会自动按 2 倍放宽。'
        })}
                    ${renderItem('根据模型大小自动调整单次字数 (Model Tier Adaptive Scaling)', 'translation.governance.batch_translation.model_tier_adaptive', bg.model_tier_adaptive ?? true, 'checkbox', {
            onchange: "window.syncTranslationGovernanceField('translation.governance.batch_translation.model_tier_adaptive', this.checked)",
            description: '根据当前使用的模型智能调节。如果使用本地小模型（如 7B/8B），系统会自动降低单次合并量（如 3 段 / 600 字），防止小模型遗漏内容或产生幻觉。'
        })}
                    ${renderItem('局部异常时仅重试失败段落 (Smart Rescue & Retry)', 'translation.governance.batch_translation.fallback_on_error', bg.fallback_on_error ?? true, 'checkbox', {
            onchange: "window.syncTranslationGovernanceField('translation.governance.batch_translation.fallback_on_error', this.checked)",
            description: '若大模型在合并翻译中漏掉了某一段或格式破损，系统会保留已翻译成功的段落，仅对出错段落单独重试，避免整批重跑浪费额度。'
        })}
                </div>

                <!-- A. 链接与跳转对准 -->
                <div class="settings-group" style="margin-bottom: 2rem; display: flex; flex-direction: column; gap: 10px;">
                    <h4 style="color: var(--accent-secondary); margin-bottom: 5px; font-size: 0.95rem; font-family: 'JetBrains Mono', monospace;">🔗 链接与跳转对准 (Link & Anchor Resolution)</h4>
                    ${renderItem('翻译链接标题 (Translate Link Labels)', 'translation.governance.link_governance.translate_labels', lg.translate_labels ?? true, 'checkbox', {
            onchange: "window.syncTranslationGovernanceField('translation.governance.link_governance.translate_labels', this.checked)",
            description: '自动将 Markdown 超链接中的文字标题翻译为目标语言（例如将 [快速开始](url) 翻译为 [Quick Start](url)）。'
        })}
                    ${renderItem('翻译页面跳转锚点 (Translate Anchor Hashes)', 'translation.governance.link_governance.translate_anchors', lg.translate_anchors ?? true, 'checkbox', {
            onchange: "window.syncTranslationGovernanceField('translation.governance.link_governance.translate_anchors', this.checked)",
            description: '自动翻译网页目录锚点并规范为小写连字符（如 #1-安装准备 转换为 #1-install-prep），确保多语言网页点击目录能够精准跳转。'
        })}
                    ${renderItem('站内链接自动对齐目标语言 (Auto-Localize Internal Links)', 'translation.governance.link_governance.auto_localize_internal_links', lg.auto_localize_internal_links ?? true, 'checkbox', {
            onchange: "window.syncTranslationGovernanceField('translation.governance.link_governance.auto_localize_internal_links', this.checked)",
            description: '自动将站内相对链接重定向到对应语言目录，避免在英文版页面中点击链接跳回中文版。'
        })}
                    ${renderItem('外部网址保护模式 (URL Protection Mode)', 'translation.governance.link_governance.external_links_mask_mode', lg.external_links_mask_mode || 'url_only', 'select', {
            items: [
                { value: 'url_only', text: '🔒 仅保护 URL (推荐)' },
                { value: 'all', text: '🔒 完整保护整条链接' },
                { value: 'none', text: '🔓 不执行保护' }
            ],
            onchange: "window.syncTranslationGovernanceField('translation.governance.link_governance.external_links_mask_mode', this.value)",
            description: '外部超链接在发送给大模型时的保护策略。推荐使用「仅保护 URL」，既能防止大模型篡改外部网址，又允许翻译链接文字。'
        })}
                </div>

                <!-- B. 各类型内容翻译规则 -->
                <div class="settings-group" style="margin-bottom: 2.5rem;">
                    <h4 style="color: var(--accent-secondary); margin-bottom: 5px; font-size: 0.95rem; font-family: 'JetBrains Mono', monospace;">🧱 各类型内容翻译规则 (Content Block Rules)</h4>
                    <p class="section-desc" style="margin-bottom: 15px;">针对文稿中不同类型的内容（如正文、标题、代码、表格、提示框、注释等）单独指定翻译或忽略规则。</p>
                    <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 15px;">
                        ${Object.entries(blockTypes).map(([key, info]) => {
            const rule = blockRules[key] || {};
            const action = rule.action || (key === 'code' || key === 'html' || key === 'comment' ? 'bypass' : 'translate');
            const overrideVal = rule.prompt_override || '';
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
                                        <option value="translate" ${action === 'translate' ? 'selected' : ''}>🌐 正常翻译该内容</option>
                                        <option value="bypass" ${action === 'bypass' ? 'selected' : ''}>⏩ 原样保留不翻译</option>
                                        <option value="strip" ${action === 'strip' ? 'selected' : ''}>🗑️ 彻底删除不展示</option>
                                        <option value="parse_comments_only" ${action === 'parse_comments_only' ? 'selected' : ''}>💬 代码块仅翻译注释</option>
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
            </div>
        `;
    };
})();
