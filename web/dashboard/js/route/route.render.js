/**
 * 🛣️ [V75.0] Advanced Channel Routing - Render Module
 * 职责：渲染高级路由矩阵与专属风格映射表盘，并单独渲染 Slug 策略配置页面。
 */

window.renderRouteMatrixCategory = () => {
    const isLicensed = window.settingsData._is_licensed || false;
    const routes = window.settingsData.route_matrix || [];
    const themeSlots = window.settingsData._theme_slots || {};

    let html = `
        <div class="full-width">
            <div class="section-header" style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="display: flex; align-items: center; gap: 10px;">
                        🛣️ 高级频道路由与魔法矩阵
                        ${isLicensed ? '<span class="pro-badge">PRO</span>' : '<span class="community-badge" style="background: rgba(255,255,255,0.1); color: #888; font-size: 0.65rem; padding: 2px 6px; border-radius: 10px;">COMMUNITY</span>'}
                    </h3>
                </div>
            </div>
            
            <p class="section-desc" style="margin-bottom: 25px;">
                突破单纯的物理目录映射，将本地特定文件夹（Local Folder）路由至全新的逻辑出版路径（Web Path），同时可为其指派专属的「网页前端模板」与「AI 翻译风格」。<br>
                <span style="color: var(--accent-secondary); font-size: 0.85rem;">* 社区版默认退化至原始物理路径。</span>
            </p>
            
            <div class="matrix-table glass-panel" style="border-radius: 12px; overflow: hidden; position: relative;">
                ${!isLicensed ? `
                    <div class="pro-overlay" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(10, 11, 24, 0.6); backdrop-filter: blur(4px); z-index: 10; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                        <div style="font-size: 3rem; margin-bottom: 15px; filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.5));">👑</div>
                        <h3 style="color: #FFD700; font-weight: 600; font-size: 1.2rem; margin-bottom: 10px; letter-spacing: 1px;">Pro Only Feature</h3>
                        <p style="color: #ccc; max-width: 400px; line-height: 1.6;">高级频道路由、自定义发布 URL 前缀及专属翻译风格矩阵仅在授权版中开放。</p>
                        <p style="color: #888; font-size: 0.8rem; margin-top: 15px;">系统当前已自动为您回落至无缝的物理路径映射模式。</p>
                    </div>
                ` : ''}

                <div class="matrix-header" style="display: grid; grid-template-columns: 1.5fr 1.5fr 1.5fr 1fr 60px; gap: 15px; padding: 15px 20px; background: rgba(0,0,0,0.2); font-size: 0.85rem; color: var(--text-dim); font-weight: 600; border-bottom: 1px solid var(--glass-border);">
                    <span>📁 文库路径 (Local Path)</span>
                    <span>🔗 网页路径 (Web Path)</span>
                    <span>🧩 网页模板 (Page Template)</span>
                    <span>🎭 翻译风格</span>
                    <span style="text-align: center;">操作</span>
                </div>
                
                <div class="matrix-body" id="route-matrix-body" style="padding: 10px;">
                    ${routes.length === 0 ? `
                        <div class="empty-state" style="padding: 40px; text-align: center; color: var(--text-dim);">
                            暂无路由策略。您的全部文件目前均按照原始物理路径进行映射发布。
                        </div>
                    ` : routes.map((route, idx) => `
                        <div class="matrix-row route-item" data-idx="${idx}" style="display: grid; grid-template-columns: 1.5fr 1.5fr 1.5fr 1fr 60px; gap: 15px; padding: 12px 10px; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.03); transition: background 0.2s;">
                            <div>
                                ${(() => {
                                    const directories = window.settingsData._directories || [];
                                    const sourceVal = route.source || '';
                                    const hasDirs = directories.length > 0;
                                    const isStandard = !sourceVal || directories.includes(sourceVal);
                                    let html = '';
                                    if (hasDirs) {
                                        html += `<select class="setting-input source-select" style="width: 100%; display: ${isStandard ? 'block' : 'none'};" ${!isLicensed ? 'disabled' : ''} onchange="if(this.value === '_custom') { this.style.display='none'; this.nextElementSibling.style.display='block'; this.nextElementSibling.value=''; this.nextElementSibling.focus(); } else { this.nextElementSibling.value=this.value; } syncRouteMatrixToSettings();">`;
                                        html += `<option value="" ${!sourceVal ? 'selected' : ''}>-- 选择文库目录 --</option>`;
                                        directories.forEach(d => {
                                            if (d) html += `<option value="${d}" ${sourceVal === d ? 'selected' : ''}>📁 ${d}</option>`;
                                        });
                                        html += `<option value="_custom" ${!isStandard ? 'selected' : ''}>✏️ 自定义输入...</option>`;
                                        html += `</select>`;
                                    }
                                    html += `<input type="text" class="setting-input source-input" value="${sourceVal}" placeholder="例如: journal" style="width: 100%; display: ${!hasDirs || !isStandard ? 'block' : 'none'};" ${!isLicensed ? 'disabled' : ''} onchange="syncRouteMatrixToSettings()" oninput="syncRouteMatrixToSettings()">`;
                                    return html;
                                })()}
                            </div>
                            <div>
                                <input type="text" class="setting-input prefix-input" value="${route.prefix || ''}" placeholder="例如: /blog/" style="width: 100%; color: var(--accent-secondary); font-family: monospace;" ${!isLicensed ? 'disabled' : ''} onchange="syncRouteMatrixToSettings()" oninput="syncRouteMatrixToSettings()">
                            </div>
                            <div>
                                ${(() => {
                                    const hasSlots = Object.keys(themeSlots).length > 0;
                                    const slotVal = route.target_slot || '';
                                    const isStandard = !slotVal || Object.keys(themeSlots).includes(slotVal);
                                    let html = '';
                                    if (hasSlots) {
                                        html += `<select class="setting-input slot-select" style="width: 100%; display: ${isStandard ? 'block' : 'none'};" ${!isLicensed ? 'disabled' : ''} onchange="if(this.value === '_custom') { this.style.display='none'; this.nextElementSibling.style.display='block'; this.nextElementSibling.value=''; this.nextElementSibling.focus(); } else { this.nextElementSibling.value=this.value; } syncRouteMatrixToSettings();">`;
                                        html += `<option value="" ${!slotVal ? 'selected' : ''}>-- 选择网页模板 --</option>`;
                                        Object.entries(themeSlots).forEach(([k, v]) => {
                                            html += `<option value="${k}" ${slotVal === k ? 'selected' : ''}>${v.label || k}</option>`;
                                        });
                                        html += `<option value="_custom" ${!isStandard ? 'selected' : ''}>✏️ 自定义输入...</option>`;
                                        html += `</select>`;
                                    }
                                    html += `<input type="text" class="setting-input slot-input" value="${slotVal}" placeholder="例如: custom_template" style="width: 100%; display: ${!hasSlots || !isStandard ? 'block' : 'none'};" ${!isLicensed ? 'disabled' : ''} onchange="syncRouteMatrixToSettings()" oninput="syncRouteMatrixToSettings()">`;
                                    return html;
                                })()}
                            </div>
                            <div>
                                <select class="setting-input style-input" style="width: 100%;" ${!isLicensed ? 'disabled' : ''} onchange="syncRouteMatrixToSettings()">
                                    <option value="">继承全局默认</option>
                                    <option value="professional" ${route.style === 'professional' ? 'selected' : ''}>💼 商务严谨</option>
                                    <option value="casual" ${route.style === 'casual' ? 'selected' : ''}>☕ 随性自然</option>
                                    <option value="literal" ${route.style === 'literal' ? 'selected' : ''}>⚖️ 精准直译</option>
                                </select>
                            </div>
                            <div style="text-align: center;">
                                <button class="mini-btn" onclick="removeRouteMatrixRow(this)" style="background: rgba(255,50,50,0.1); border: 1px solid rgba(255,50,50,0.3); color: #ff5555; height: 32px; width: 32px; padding: 0; border-radius: 6px; cursor: pointer; transition: all 0.2s;" title="删除此规则" ${!isLicensed ? 'disabled' : ''}>×</button>
                            </div>
                        </div>
                    `).join('')}
                </div>
                
                <div style="padding: 12px; text-align: center; border-top: 1px dashed rgba(255,255,255,0.05); background: rgba(0,0,0,0.1);">
                    <button class="mini-btn glow-btn" onclick="addRouteMatrixRow()" style="background: transparent; border: 1px dashed ${isLicensed ? 'var(--accent-primary)' : 'var(--text-muted)'}; color: ${isLicensed ? 'var(--accent-primary)' : 'var(--text-muted)'}; width: 100%; padding: 8px; border-radius: 6px; cursor: ${isLicensed ? 'pointer' : 'not-allowed'}; transition: all 0.3s; font-size: 0.85rem;" onmouseover="${isLicensed ? "this.style.background='rgba(0, 242, 255, 0.1)'" : ''}" onmouseout="this.style.background='transparent'" title="${isLicensed ? '添加新路由规则' : '专属版特权功能 (点击查看详情)'}">
                        ➕ 添加新路由规则
                    </button>
                </div>
            </div>
            
            <div style="margin-top: 25px; padding: 15px 20px; background: rgba(0, 242, 255, 0.05); border: 1px dashed rgba(0, 242, 255, 0.2); border-radius: 8px;">
                <h5 style="color: #00f2ff; margin-bottom: 8px; font-size: 0.9rem;">💡 策略运行原理</h5>
                <ul style="font-size: 0.8rem; color: #bbb; line-height: 1.6; padding-left: 20px; margin: 0;">
                    <li>当扫描引擎遇到与 <b>源目录</b> 匹配的文件夹时，将物理拦截原路，并将其分发至配置的 <b>Web 路由路径</b>。</li>
                    <li>指派独立的<b>网页模板</b>将覆盖全局默认的渲染管线，允许为该频道的文章套用完全不同的前端布局组件。</li>
                    <li>当进行双语多语言生成时，AI 将自动采用本配置行锁定的 <b>翻译风格</b>。</li>
                </ul>
            </div>
        </div>
    `;

    return html;
};

window.renderSlugSettingsCategory = () => {
    const isLicensed = window.settingsData._is_licensed || false;
    const translation = window.settingsData.translation || {};
    const prompts = translation.prompts || {};

    // 1. Slug 命名模式
    const slugModeHtml = window.renderSettingsItem(
        'Slug 命名模式',
        'translation.slug_mode',
        translation.slug_mode || 'ai',
        'select',
        {
            items: [
                { value: 'ai', text: '🤖 AI 自动推导友好 Slug' },
                { value: 'filename', text: '📁 物理文件名清洗自愈' }
            ],
            disabled: !isLicensed,
            description: '决定系统如何处理文档发布的 Slug 命名。AI 模式下，系统会结合原稿标题推导英文 Slug。'
        }
    );

    // 2. Slug 目录处理方式
    const slugDirModeHtml = window.renderSettingsItem(
        'Slug 目录处理方式',
        'translation.slug_dir_mode',
        translation.slug_dir_mode || 'flat',
        'select',
        {
            items: [
                { value: 'flat', text: '📄 扁平模式 (忽略源目录路径)' },
                { value: 'prefix', text: '🔗 目录前缀模式 (拼接连字符前缀)' },
                { value: 'nested', text: '📂 嵌套路径模式 (物理保留斜杠层级)' }
            ],
            disabled: !isLicensed,
            description: '若文档存在子目录，决定如何将映射子目录体现到 Slug 中。例如，源目录 docs/tech/intro.md 映射为 tech/intro，对应：扁平(intro)、前缀(tech-intro)、嵌套(tech/intro)。'
        }
    );

    // 3. Slug 最大字符长度
    const maxSlugLengthHtml = window.renderSettingsItem(
        'Slug 最大字符长度',
        'translation.max_slug_length',
        translation.max_slug_length ?? 100,
        'number',
        {
            disabled: !isLicensed,
            placeholder: '100',
            description: 'Slug 生成后的最大保留长度（默认 100，超出将截断）。'
        }
    );
    let html = `
        <div class="full-width">
            <div class="section-header" style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="display: flex; align-items: center; gap: 10px;">
                        🔗 Slug 命名与路径拼接策略
                        ${isLicensed ? '<span class="pro-badge">PRO</span>' : '<span class="community-badge" style="background: rgba(255,255,255,0.1); color: #888; font-size: 0.65rem; padding: 2px 6px; border-radius: 10px;">COMMUNITY</span>'}
                    </h3>
                </div>
            </div>
            
            <p class="section-desc" style="margin-bottom: 25px;">
                配置文档发布时自动生成的 URL Slug 逻辑及目录路径整合方案，支持结合 AI 或物理文件名进行全自动治理。<br>
                <span style="color: var(--accent-secondary); font-size: 0.85rem;">* 社区版默认退化至扁平 AI Slug 模式。</span>
            </p>
            
            <div class="settings-group glass-panel" style="padding: 25px; border-radius: 12px; border: 1px solid var(--glass-border); position: relative; overflow: hidden;">
                ${!isLicensed ? `
                    <div class="pro-overlay" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(10, 11, 24, 0.6); backdrop-filter: blur(4px); z-index: 10; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                        <div style="font-size: 3rem; margin-bottom: 15px; filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.5));">👑</div>
                        <h3 style="color: #FFD700; font-weight: 600; font-size: 1.2rem; margin-bottom: 10px; letter-spacing: 1px;">Pro Only Feature</h3>
                        <p style="color: #ccc; max-width: 400px; line-height: 1.6;">自定义 Slug 命名策略、目录映射前缀/嵌套模式及 AI 提示词控制仅在授权版中开放。</p>
                        <p style="color: #888; font-size: 0.8rem; margin-top: 15px;">系统当前已自动为您回落至默认的扁平 AI Slug 生成模式。</p>
                    </div>
                ` : ''}
                <div>
                    ${slugModeHtml}
                    ${slugDirModeHtml}
                    ${maxSlugLengthHtml}
                </div>
            </div>
            
            <div style="margin-top: 25px; padding: 15px 20px; background: rgba(0, 242, 255, 0.05); border: 1px dashed rgba(0, 242, 255, 0.2); border-radius: 8px;">
                <h5 style="color: #00f2ff; margin-bottom: 8px; font-size: 0.9rem;">💡 目录路径处理策略</h5>
                <ul style="font-size: 0.8rem; color: #bbb; line-height: 1.6; padding-left: 20px; margin: 0;">
                    <li><b>扁平模式 (Flat)</b>：仅保留文档自身的 Slug，完全忽略父目录（如 <code>tech/intro</code> 生成 Slug 为 <code>intro</code>）。</li>
                    <li><b>前缀模式 (Prefix)</b>：提取当前文档所在子目录并用连字符拼接为前缀（如 <code>tech/intro</code> 生成 Slug 为 <code>tech-intro</code>）。</li>
                    <li><b>嵌套模式 (Nested)</b>：保留完整的多级目录层次结构并用斜杠拼接（如 <code>tech/intro</code> 生成 Slug 为 <code>tech/intro</code>）。</li>
                </ul>
            </div>

            <div style="margin-top: 20px; padding: 15px 20px; background: rgba(255, 255, 255, 0.02); border: 1px dashed rgba(255, 255, 255, 0.1); border-radius: 8px; font-size: 0.8rem; color: var(--text-dim); display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.1rem;">💡</span>
                <span>
                    如需调整 AI 自动推导 Slug 时的 <b>System / User Prompt 提示词策略</b>，该功能已统一合并至 
                    <a href="javascript:void(0)" onclick="window.switchToSettingsTab('translation_style')" style="color: #00f2ff; text-decoration: underline; font-weight: 600; cursor: pointer;">🎭 翻译风格</a> 
                    菜单中，以实现全域多场景提示词的完全对称化管理。
                </span>
            </div>
        </div>
    `;

    return html;
};
