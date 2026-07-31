/**
 * 🎭 [I5-SOP02-Split] Illacme Plenipes Localization Style Module
 * 职责：全域翻译风格预设定义（translationStyles 常量）与风格选择渲染器。
 */

window.translationStyles = {
    professional: {
        name: "💼 商务专业 (Professional)",
        badge: "商用",
        desc: "正式、严谨，采用严密的行业术语，适用于商业报告、官方规范与业务文档。",
        translate_system: "You are a professional translator. Translate the following Markdown content from {source_lang} to {target_lang}. Keep all Markdown syntax, frontmatter keys, and LaTeX formulas intact. Use formal tone and professional vocabulary. Do not add any explanations.",
        translate_user: "### Content ###\n{text}\n### Translation ###",
        title_system: "You are a professional editor. Translate and polish the following title into {target_lang}. Keep it concise, formal, and professional. Output ONLY the title.",
        title_user: "{title}",
        metadata_system: "You are a professional editor. Translate and polish the provided metadata into {target_lang} using formal terminology. Output ONLY the result.",
        metadata_user: "Type: {meta_type}\nValue: {text}",
        slug_system: "Generate a URL-friendly slug based on the title. Only output the slug string.",
        slug_user: "{title}",
        seo_system: "You are a professional business SEO strategist. Generate professional, authoritative SEO metadata optimized for maximum CTR.\n\nYour output MUST be a valid JSON object with these fields:\n- \"seo_title\": A compelling, professional title (max 60 chars)\n- \"description\": A persuasive meta description (max 160 chars) using professional business language\n- \"keywords\": An array of 5-8 high-relevance professional keywords\n- \"og_title\": An Open Graph title optimized for corporate sharing\n\nRules:\n- Use formal and professional tone.\n- Prioritize industry-standard terminology.\n- Output language: {lang_name}",
        seo_user: "### Content to Optimize ###\nTitle: {title}\nBody (excerpt):\n{text}\n\n### Generate SEO JSON ###"
    },
    casual: {
        name: "💬 活泼随性 (Casual)",
        badge: "日常",
        desc: "口语化、自然亲切，注重本地读者的日常表达，适用于个人随笔、博客分享与社媒文案。",
        translate_system: "You are a friendly translator. Translate the following Markdown content from {source_lang} to {target_lang} in a natural, conversational tone. Keep all Markdown syntax and frontmatter intact. Do not add any explanations.",
        translate_user: "### Content ###\n{text}\n### Translation ###",
        title_system: "You are a creative editor. Translate the following title into {target_lang} in a catchy, natural, and conversational way. Output ONLY the title.",
        title_user: "{title}",
        metadata_system: "You are a creative editor. Translate the provided metadata into {target_lang} using natural, modern language. Output ONLY the result.",
        metadata_user: "Type: {meta_type}\nValue: {text}",
        slug_system: "Generate a URL-friendly slug based on the title. Only output the slug string.",
        slug_user: "{title}",
        seo_system: "You are a creative social media SEO copywriter. Generate engaging, friendly, and catchy SEO metadata optimized for maximum social sharing and CTR.\n\nYour output MUST be a valid JSON object with these fields:\n- \"seo_title\": An inviting, highly engaging title (max 60 chars)\n- \"description\": A conversational, catchy meta description (max 160 chars) that hooks the reader\n- \"keywords\": An array of 5-8 popular keywords matching current trends\n- \"og_title\": A catchy Open Graph title for social networks\n\nRules:\n- Keep the tone friendly, conversational, and lighthearted.\n- Use engaging hooks.\n- Output language: {lang_name}",
        seo_user: "### Content to Optimize ###\nTitle: {title}\nBody (excerpt):\n{text}\n\n### Generate SEO JSON ###"
    },
    literal: {
        name: "🔍 精准直译 (Literal)",
        badge: "直译",
        desc: "结构对称、忠于原文，尽可能保留句型与字面对应，适用于学术条约及比对校验场景。",
        translate_system: "You are a precise translator. Translate the following Markdown content from {source_lang} to {target_lang} literally, preserving the original structure and word choice as much as possible. Keep all Markdown syntax intact. Do not add any explanations.",
        translate_user: "### Content ###\n{text}\n### Translation ###",
        title_system: "You are a precise translator. Translate the following title into {target_lang} as literally as possible. Output ONLY the title.",
        title_user: "{title}",
        metadata_system: "You are a precise translator. Translate the provided metadata into {target_lang} literally. Output ONLY the result.",
        metadata_user: "Type: {meta_type}\nValue: {text}",
        slug_system: "Generate a URL-friendly slug based on the title. Only output the slug string.",
        slug_user: "{title}",
        seo_system: "You are a precise SEO analyst. Generate highly accurate, objective SEO metadata directly reflecting the source content for maximum precision.\n\nYour output MUST be a valid JSON object with these fields:\n- \"seo_title\": A literal, precise title (max 60 chars)\n- \"description\": An objective, exact meta description (max 160 chars)\n- \"keywords\": An array of 5-8 precise keywords directly extracted from the text\n- \"og_title\": An Open Graph title matching the main title exactly\n\nRules:\n- Stick strictly to the facts in the text. No clickbait or marketing fluff.\n- Output language: {lang_name}",
        seo_user: "### Content to Optimize ###\nTitle: {title}\nBody (excerpt):\n{text}\n\n### Generate SEO JSON ###"
    },
    academic: {
        name: "🎓 学术客观 (Academic)",
        badge: "学术",
        desc: "客观严谨、使用被动语态与书面学术用词，完美保留 LaTeX 复杂公式与文献脚注。",
        translate_system: "You are an academic translator. Translate the following Markdown paper from {source_lang} to {target_lang}. Use formal academic style, precise terminology, and objective tone. Maintain all LaTeX mathematical environments, footnotes, citations, and Markdown markup intact. Do not alter the formatting.",
        translate_user: "### Content ###\n{text}\n### Translation ###",
        title_system: "You are a scholarly editor. Translate the following paper title into {target_lang} with high academic accuracy. Output ONLY the title.",
        title_user: "{title}",
        metadata_system: "You are a scholarly editor. Translate the following metadata into {target_lang} using academic terminology. Output ONLY the result.",
        metadata_user: "Type: {meta_type}\nValue: {text}",
        slug_system: "Generate a URL-friendly slug based on the title. Only output the slug string.",
        slug_user: "{title}",
        seo_system: "You are an academic research SEO editor. Generate scholarly, objective SEO metadata suitable for indexation in research databases and scientific search engines.\n\nYour output MUST be a valid JSON object with these fields:\n- \"seo_title\": A formal, descriptive academic title (max 60 chars)\n- \"description\": An informative, objective meta description (max 160 chars) summarizing the core thesis\n- \"keywords\": An array of 5-8 formal academic subject terms\n- \"og_title\": A scholarly Open Graph title for educational sharing\n\nRules:\n- Use formal academic style, precise terminology, and objective tone.\n- Avoid sensationalism.\n- Output language: {lang_name}",
        seo_user: "### Content to Optimize ###\nTitle: {title}\nBody (excerpt):\n{text}\n\n### Generate SEO JSON ###"
    },
    technical: {
        name: "💻 技术极客 (Technical)",
        badge: "技术",
        desc: "面向开发者与工程师，保留通用技术名词不予硬译，完美对齐行内代码与代码块结构。",
        translate_system: "You are a technical translator specializing in computer science. Translate the following developer documentation from {source_lang} to {target_lang}. Keep industry standard terms (e.g., 'API', 'Docker', 'GIL') in English. Keep all code blocks, inline code, and formatting strictly unchanged.",
        translate_user: "### Content ###\n{text}\n### Translation ###",
        title_system: "You are a technical writer. Translate the following technical article title into {target_lang}, retaining essential technical terms in English. Output ONLY the title.",
        title_user: "{title}",
        metadata_system: "You are a technical writer. Translate the following metadata into {target_lang}, preserving standard technology terms. Output ONLY the result.",
        metadata_user: "Type: {meta_type}\nValue: {text}",
        slug_system: "Generate a URL-friendly slug based on the title. Only output the slug string.",
        slug_user: "{title}",
        seo_system: "You are a developer relations SEO specialist. Generate developer-friendly SEO metadata retaining technical accuracy and keywords.\n\nYour output MUST be a valid JSON object with these fields:\n- \"seo_title\": A precise, technical title (max 60 chars) featuring core technologies\n- \"description\": A concise, clear meta description (max 160 chars) containing technical details/use cases\n- \"keywords\": An array of 5-8 developer-oriented keywords (e.g., API names, frameworks)\n- \"og_title\": A tech-focused Open Graph title\n\nRules:\n- Maintain industry-standard technical terms (e.g. API, CLI, Docker) in English.\n- Avoid non-technical marketing fluff.\n- Output language: {lang_name}",
        seo_user: "### Content to Optimize ###\nTitle: {title}\nBody (excerpt):\n{text}\n\n### Generate SEO JSON ###"
    },
    literary: {
        name: "🎭 文学唯美 (Literary)",
        badge: "信达雅",
        desc: "意境重于字词、行文优雅且追求文学感官，适用于散文随笔、故事创作与诗歌小说。",
        translate_system: "You are a literary translator. Translate the following prose from {source_lang} to {target_lang} with an emphasis on tone, style, and flow. Capture the emotional resonance and elegance of the original text. Maintain all Markdown formatting. Avoid literal translation where a more elegant expression exists.",
        translate_user: "### Content ###\n{text}\n### Translation ###",
        title_system: "You are a literary editor. Translate the following title into {target_lang} with poetic beauty. Output ONLY the title.",
        title_user: "{title}",
        metadata_system: "You are a literary editor. Translate the following metadata into {target_lang} with high literary elegance. Output ONLY the result.",
        metadata_user: "Type: {meta_type}\nValue: {text}",
        slug_system: "Generate a URL-friendly slug based on the title. Only output the slug string.",
        slug_user: "{title}",
        seo_system: "You are a literary editor and SEO writer. Generate elegant, evocative SEO metadata that captures the mood and theme of the text while ensuring discoverability.\n\nYour output MUST be a valid JSON object with these fields:\n- \"seo_title\": An evocative, beautifully crafted title (max 60 chars)\n- \"description\": A poetic, inviting meta description (max 160 chars) capturing the narrative flow\n- \"keywords\": An array of 5-8 thematic or atmospheric keywords\n- \"og_title\": A beautiful Open Graph title\n\nRules:\n- Prioritize prose quality, style, and emotional resonance.\n- Output language: {lang_name}",
        seo_user: "### Content to Optimize ###\nTitle: {title}\nBody (excerpt):\n{text}\n\n### Generate SEO JSON ###"
    }
};

window.renderTranslationStyleCategory = () => {
    const i18n = window.settingsData.i18n_settings || {};
    const isEnabled = i18n.enabled !== false; // 默认为 true

    if (!isEnabled) return `
            <div class="full-width">
                <div class="glass-panel" style="padding: 40px 30px; text-align: center; color: var(--text-dim); display: flex; flex-direction: column; align-items: center; gap: 15px; border-radius: 12px; background: rgba(255, 255, 255, 0.02); border: 1px dashed var(--glass-border);">
                    <span style="font-size: 3.5rem; filter: drop-shadow(0 0 10px rgba(0, 242, 255, 0.15));">🌍</span>
                    <h4 style="color: var(--text-bright, #ffffff); margin: 0; font-size: 1.2rem; font-weight: 700; letter-spacing: 0.5px;">多语言翻译引擎未启用</h4>
                    <p style="font-size: 0.85rem; max-width: 420px; line-height: 1.6; margin: 0; color: var(--text-dim);">
                        当前品牌的多语言翻译矩阵已关闭。在此状态下无法调整翻译风格。如需微调 Prompt 模板，请先前往 <strong>🌍 翻译阵列</strong> 开启多语言总开关。
                    </p>
                </div>
            </div>
        `;

    const prompts = window.settingsData.translation?.prompts || {};
    const ts = prompts.translate_system || '';
    const tu = prompts.translate_user || '';
    const tis = prompts.title_system || '';
    const tiu = prompts.title_user || '';
    const ms = prompts.metadata_system || '';
    const mu = prompts.metadata_user || '';
    const ss = prompts.slug_system || '';
    const su = prompts.slug_user || '';
    const seos = prompts.seo_system || '';
    const seou = prompts.seo_user || '';

    // 智能反向推导当前属于哪个风格预设
    let activeStyleKey = 'custom';
    for (const [key, tpl] of Object.entries(window.translationStyles)) {
        const isMatch = (
            tpl.translate_system === ts &&
            tpl.translate_user === tu &&
            tpl.title_system === tis &&
            tpl.title_user === tiu &&
            tpl.metadata_system === ms &&
            tpl.metadata_user === mu &&
            tpl.slug_system === ss &&
            tpl.slug_user === su &&
            (tpl.seo_system || '') === seos &&
            (tpl.seo_user || '') === seou
        );
        if (isMatch) {
            activeStyleKey = key;
            break;
        }
    }
    
    if (!ts && !tis && !ms && !ss && !seos) {
        activeStyleKey = 'professional'; // 默认值
    }

    const currentStyle = window.translationStyles[activeStyleKey] || {
        badge: "自定义",
        desc: "正在使用专属于该品牌的个性化翻译 Prompt 模板。",
        translate_system: ts,
        translate_user: tu,
        title_system: tis,
        title_user: tiu,
        metadata_system: ms,
        metadata_user: mu,
        slug_system: ss,
        slug_user: su,
        seo_system: seos,
        seo_user: seou
    };

    const textareaStyle = `
        width: 100%; box-sizing: border-box; font-family: 'Fira Code', Consolas, Monaco, monospace; font-size: 0.72rem; padding: 12px; 
        background: ${activeStyleKey === 'custom' ? 'var(--bg-agent-input)' : 'rgba(var(--bg-modal-solid-rgb, 13, 14, 28), 0.5)'}; 
        border: ${activeStyleKey === 'custom' ? '1.5px solid rgba(var(--accent-primary-rgb), 0.25)' : '1px solid var(--glass-border)'}; 
        border-radius: 8px; color: var(--text-bright, #ffffff); min-height: 80px; resize: vertical; line-height: 1.5; outline: none; transition: all 0.2s ease;
        cursor: ${activeStyleKey === 'custom' ? 'text' : 'default'};
    `;

    return `
            <div class="full-width">
                <div class="settings-grid">
                    <div class="settings-group">
                        <div style="display: flex; gap: 15px; align-items: center; margin-bottom: 15px;">
                        <select id="style-selector" class="setting-input" onchange="window.updateStylePreview(this.value)" style="flex: 1; min-height: 38px;">
                            ${Object.entries(window.translationStyles).map(([key, tpl]) => `
                                <option value="${key}" ${key === activeStyleKey ? 'selected' : ''}>${tpl.name}</option>
                            `).join('')}
                            <option value="custom" ${activeStyleKey === 'custom' ? 'selected' : ''}>✍️ 自定义风格 (Custom Prompt)</option>
                        </select>
                    </div>
                    
                    <!-- 风格详情卡片描述区 -->
                    <div id="style-description-box" style="padding: 12px 16px; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; background: rgba(var(--bg-rgb), 0.2); font-size: 0.8rem; line-height: 1.5; color: var(--text-normal); margin-bottom: 20px; display: flex; align-items: center; gap: 12px; transition: all 0.3s ease;">
                        <span style="background: var(--accent-secondary, #00f2ff); color: var(--bg-solid, #005); padding: 2px 6px; border-radius: 4px; font-weight: 800; font-size: 0.7rem;">${currentStyle.badge}</span>
                        <p style="margin: 0; font-weight: 500;">${currentStyle.desc}</p>
                    </div>

                    <!-- Prompt 编辑与展示区（完全对称化双栏设计） -->
                    <div class="prompt-wrapper" style="display: flex; flex-direction: column; gap: 20px; margin-top: 15px;">
                        
                        <!-- 1. 正文翻译 (Content) -->
                        <div class="glass-panel" style="padding: 15px; border-radius: 12px; border: 1px solid var(--glass-border); display: flex; flex-direction: column; gap: 12px; background: rgba(0,0,0,0.1);">
                            <h4 style="color: #00f2ff; font-size: 0.85rem; margin: 0; display: flex; align-items: center; gap: 8px;">
                                📄 正文翻译 Prompt 策略 (Markdown Content)
                            </h4>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                                <div style="display: flex; flex-direction: column; gap: 6px;">
                                    <span style="font-size: 0.75rem; font-weight: 600; color: var(--text-bright); opacity: 0.75;">系统角色提示词 (System Role)</span>
                                    <textarea id="prompt-preview-translate-system" onchange="updateConfigField('translation.prompts.translate_system', this.value)" oninput="window.checkStyleMatch()" ${activeStyleKey !== 'custom' ? 'readonly' : ''} style="${textareaStyle}">${currentStyle.translate_system || ''}</textarea>
                                </div>
                                <div style="display: flex; flex-direction: column; gap: 6px;">
                                    <span style="font-size: 0.75rem; font-weight: 600; color: var(--text-bright); opacity: 0.75;">用户提示词模板 (User Prompt)</span>
                                    <textarea id="prompt-preview-translate-user" onchange="updateConfigField('translation.prompts.translate_user', this.value)" oninput="window.checkStyleMatch()" ${activeStyleKey !== 'custom' ? 'readonly' : ''} style="${textareaStyle}">${currentStyle.translate_user || ''}</textarea>
                                </div>
                            </div>
                        </div>

                        <!-- 2. 标题翻译 (Title) -->
                        <div class="glass-panel" style="padding: 15px; border-radius: 12px; border: 1px solid var(--glass-border); display: flex; flex-direction: column; gap: 12px; background: rgba(0,0,0,0.1);">
                            <h4 style="color: #00f2ff; font-size: 0.85rem; margin: 0; display: flex; align-items: center; gap: 8px;">
                                📌 标题翻译 Prompt 策略 (Title)
                            </h4>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                                <div style="display: flex; flex-direction: column; gap: 6px;">
                                    <span style="font-size: 0.75rem; font-weight: 600; color: var(--text-bright); opacity: 0.75;">系统角色提示词 (System Role)</span>
                                    <textarea id="prompt-preview-title-system" onchange="updateConfigField('translation.prompts.title_system', this.value)" oninput="window.checkStyleMatch()" ${activeStyleKey !== 'custom' ? 'readonly' : ''} style="${textareaStyle}">${currentStyle.title_system || ''}</textarea>
                                </div>
                                <div style="display: flex; flex-direction: column; gap: 6px;">
                                    <span style="font-size: 0.75rem; font-weight: 600; color: var(--text-bright); opacity: 0.75;">用户提示词模板 (User Prompt)</span>
                                    <textarea id="prompt-preview-title-user" onchange="updateConfigField('translation.prompts.title_user', this.value)" oninput="window.checkStyleMatch()" ${activeStyleKey !== 'custom' ? 'readonly' : ''} style="${textareaStyle}">${currentStyle.title_user || ''}</textarea>
                                </div>
                            </div>
                        </div>

                        <!-- 3. 网页元数据 (Metadata) -->
                        <div class="glass-panel" style="padding: 15px; border-radius: 12px; border: 1px solid var(--glass-border); display: flex; flex-direction: column; gap: 12px; background: rgba(0,0,0,0.1);">
                            <h4 style="color: #00f2ff; font-size: 0.85rem; margin: 0; display: flex; align-items: center; gap: 8px;">
                                🏷️ 网页元数据 Prompt 策略 (Metadata)
                            </h4>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                                <div style="display: flex; flex-direction: column; gap: 6px;">
                                    <span style="font-size: 0.75rem; font-weight: 600; color: var(--text-bright); opacity: 0.75;">系统角色提示词 (System Role)</span>
                                    <textarea id="prompt-preview-meta-system" onchange="updateConfigField('translation.prompts.metadata_system', this.value)" oninput="window.checkStyleMatch()" ${activeStyleKey !== 'custom' ? 'readonly' : ''} style="${textareaStyle}">${currentStyle.metadata_system || ''}</textarea>
                                </div>
                                <div style="display: flex; flex-direction: column; gap: 6px;">
                                    <span style="font-size: 0.75rem; font-weight: 600; color: var(--text-bright); opacity: 0.75;">用户提示词模板 (User Prompt)</span>
                                    <textarea id="prompt-preview-meta-user" onchange="updateConfigField('translation.prompts.metadata_user', this.value)" oninput="window.checkStyleMatch()" ${activeStyleKey !== 'custom' ? 'readonly' : ''} style="${textareaStyle}">${currentStyle.metadata_user || ''}</textarea>
                                </div>
                            </div>
                        </div>

                        <!-- 4. AI Slug 生成 (Slug) -->
                        <div class="glass-panel" style="padding: 15px; border-radius: 12px; border: 1px solid var(--glass-border); display: flex; flex-direction: column; gap: 12px; background: rgba(0,0,0,0.1);">
                            <h4 style="color: #00f2ff; font-size: 0.85rem; margin: 0; display: flex; align-items: center; gap: 8px;">
                                🔗 AI Slug 生成 Prompt 策略 (Slug)
                            </h4>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                                <div style="display: flex; flex-direction: column; gap: 6px;">
                                    <span style="font-size: 0.75rem; font-weight: 600; color: var(--text-bright); opacity: 0.75;">系统角色提示词 (System Role)</span>
                                    <textarea id="prompt-preview-slug-system" onchange="updateConfigField('translation.prompts.slug_system', this.value)" oninput="window.checkStyleMatch()" ${activeStyleKey !== 'custom' ? 'readonly' : ''} style="${textareaStyle}">${currentStyle.slug_system || ''}</textarea>
                                </div>
                                <div style="display: flex; flex-direction: column; gap: 6px;">
                                    <span style="font-size: 0.75rem; font-weight: 600; color: var(--text-bright); opacity: 0.75;">用户提示词模板 (User Prompt)</span>
                                    <textarea id="prompt-preview-slug-user" onchange="updateConfigField('translation.prompts.slug_user', this.value)" oninput="window.checkStyleMatch()" ${activeStyleKey !== 'custom' ? 'readonly' : ''} style="${textareaStyle}">${currentStyle.slug_user || ''}</textarea>
                                </div>
                            </div>
                        </div>

                        <!-- 5. AI SEO 增强 (SEO) -->
                        <div class="glass-panel" style="padding: 15px; border-radius: 12px; border: 1px solid var(--glass-border); display: flex; flex-direction: column; gap: 12px; background: rgba(0,0,0,0.1);">
                            <h4 style="color: #00f2ff; font-size: 0.85rem; margin: 0; display: flex; align-items: center; gap: 8px;">
                                🚀 AI SEO 增强 Prompt 策略 (SEO)
                            </h4>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                                <div style="display: flex; flex-direction: column; gap: 6px;">
                                    <span style="font-size: 0.75rem; font-weight: 600; color: var(--text-bright); opacity: 0.75;">系统角色提示词 (System Role)</span>
                                    <textarea id="prompt-preview-seo-system" onchange="updateConfigField('translation.prompts.seo_system', this.value)" oninput="window.checkStyleMatch()" ${activeStyleKey !== 'custom' ? 'readonly' : ''} style="${textareaStyle}">${currentStyle.seo_system || ''}</textarea>
                                </div>
                                <div style="display: flex; flex-direction: column; gap: 6px;">
                                    <span style="font-size: 0.75rem; font-weight: 600; color: var(--text-bright); opacity: 0.75;">用户提示词模板 (User Prompt)</span>
                                    <textarea id="prompt-preview-seo-user" onchange="updateConfigField('translation.prompts.seo_user', this.value)" oninput="window.checkStyleMatch()" ${activeStyleKey !== 'custom' ? 'readonly' : ''} style="${textareaStyle}">${currentStyle.seo_user || ''}</textarea>
                                </div>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    `;
};
