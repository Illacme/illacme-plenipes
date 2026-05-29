/**
 * 🛣️ [V75.0] Advanced Channel Routing - Render Module
 * 职责：渲染高级路由矩阵与专属风格映射表盘
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
                <div>
                    <button class="primary-btn" id="btn-save-route-matrix" onclick="saveRouteMatrix()" ${!isLicensed ? 'disabled' : ''} style="background: rgba(0, 242, 255, 0.2); border: 1px solid rgba(0, 242, 255, 0.4); color: #00f2ff; min-width: 130px; justify-content: center;">
                        💾 保存全量路由
                    </button>
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
                                        html += `<select class="setting-input source-select" style="width: 100%; display: ${isStandard ? 'block' : 'none'};" ${!isLicensed ? 'disabled' : ''} onchange="if(this.value === '_custom') { this.style.display='none'; this.nextElementSibling.style.display='block'; this.nextElementSibling.value=''; this.nextElementSibling.focus(); } else { this.nextElementSibling.value=this.value; }">`;
                                        html += `<option value="" ${!sourceVal ? 'selected' : ''}>-- 选择文库目录 --</option>`;
                                        directories.forEach(d => {
                                            if (d) html += `<option value="${d}" ${sourceVal === d ? 'selected' : ''}>📁 ${d}</option>`;
                                        });
                                        html += `<option value="_custom" ${!isStandard ? 'selected' : ''}>✏️ 自定义输入...</option>`;
                                        html += `</select>`;
                                    }
                                    html += `<input type="text" class="setting-input source-input" value="${sourceVal}" placeholder="例如: journal" style="width: 100%; display: ${!hasDirs || !isStandard ? 'block' : 'none'};" ${!isLicensed ? 'disabled' : ''}>`;
                                    return html;
                                })()}
                            </div>
                            <div>
                                <input type="text" class="setting-input prefix-input" value="${route.prefix || ''}" placeholder="例如: /blog/" style="width: 100%; color: var(--accent-secondary); font-family: monospace;" ${!isLicensed ? 'disabled' : ''}>
                            </div>
                            <div>
                                ${(() => {
            const hasSlots = Object.keys(themeSlots).length > 0;
            const slotVal = route.target_slot || '';
            const isStandard = !slotVal || Object.keys(themeSlots).includes(slotVal);
            let html = '';
            if (hasSlots) {
                html += `<select class="setting-input slot-select" style="width: 100%; display: ${isStandard ? 'block' : 'none'};" ${!isLicensed ? 'disabled' : ''} onchange="if(this.value === '_custom') { this.style.display='none'; this.nextElementSibling.style.display='block'; this.nextElementSibling.value=''; this.nextElementSibling.focus(); } else { this.nextElementSibling.value=this.value; }">`;
                html += `<option value="" ${!slotVal ? 'selected' : ''}>-- 选择网页模板 --</option>`;
                Object.entries(themeSlots).forEach(([k, v]) => {
                    html += `<option value="${k}" ${slotVal === k ? 'selected' : ''}>${v.label || k}</option>`;
                });
                html += `<option value="_custom" ${!isStandard ? 'selected' : ''}>✏️ 自定义输入...</option>`;
                html += `</select>`;
            }
            html += `<input type="text" class="setting-input slot-input" value="${slotVal}" placeholder="例如: custom_template" style="width: 100%; display: ${!hasSlots || !isStandard ? 'block' : 'none'};" ${!isLicensed ? 'disabled' : ''}>`;
            return html;
        })()}
                            </div>
                            <div>
                                <select class="setting-input style-input" style="width: 100%;" ${!isLicensed ? 'disabled' : ''}>
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
                    <button class="mini-btn glow-btn" onclick="addRouteMatrixRow()" ${!isLicensed ? 'disabled' : ''} style="background: transparent; border: 1px dashed var(--accent-primary); color: var(--accent-primary); width: 100%; padding: 8px; border-radius: 6px; cursor: pointer; transition: all 0.3s; font-size: 0.85rem;" onmouseover="this.style.background='rgba(0, 242, 255, 0.1)'" onmouseout="this.style.background='transparent'" title="${isLicensed ? '添加新路由规则' : '授权版专属功能'}">
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
