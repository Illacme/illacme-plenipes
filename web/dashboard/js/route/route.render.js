/**
 * 🛣️ [V75.0] Advanced Channel Routing - Render Module
 * 职责：渲染高级路由矩阵与专属风格映射表盘，并单独渲染 Slug 策略配置页面。
 */

window.renderRouteMatrixCategory = () => {
    const settings = window.settingsData || {};
    const isLicensed = settings._is_licensed || false;
    const routes = settings.route_matrix || [];
    const themeSlots = settings._theme_slots || {};
    const directories = settings._directories || [];

    // 💡 检测是否有常见的规范目录可供智能推荐
    const mappingRules = { "Blog": "blog", "Docs": "docs", "Pages": "pages" };
    const detectedSubdirs = Object.keys(mappingRules).filter(d => directories.includes(d));
    const showSmartRecommendation = (routes.length === 0) && (detectedSubdirs.length > 0);

    let html = `
        <div class="full-width">
            ${showSmartRecommendation ? `
                <div style="margin-bottom: 20px; padding: 12px 18px; background: rgba(0, 242, 255, 0.06); border: 1px dashed rgba(0, 242, 255, 0.3); border-radius: 8px; display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 1.2rem;">💡</span>
                        <div>
                            <div style="color: #00f2fe; font-weight: 600; font-size: 0.83rem;">智能感知推荐</div>
                            <div style="color: var(--text-dim); font-size: 0.75rem;">探测到您的文库中包含 <b>${detectedSubdirs.join(', ')}</b> 等目录，是否一键装载推荐的频道映射与全景导航？</div>
                        </div>
                    </div>
                    <button class="mini-btn glow-btn" onclick="window.applyRecommendedRouteMatrix(['${detectedSubdirs.join("','")}'])" style="padding: 5px 12px; font-size: 0.75rem; background: var(--accent-primary, #00f2fe); color: #000; border: none; border-radius: 6px; font-weight: 600; cursor: pointer; flex-shrink: 0; margin-left: 15px;">
                        ✨ 一键装载推荐频道与导航
                    </button>
                </div>
            ` : ''}

            <div class="matrix-table glass-panel" style="border-radius: 12px; overflow: hidden; position: relative;">
                ${!isLicensed ? `
                    <div class="pro-overlay" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(10, 11, 24, 0.65); backdrop-filter: blur(4px); z-index: 10; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                        <span class="community-edition-badge" style="font-size: 0.72rem; color: #fbbf24; background: rgba(251, 191, 36, 0.15); border: 1px solid rgba(251, 191, 36, 0.3); padding: 3px 12px; border-radius: 12px; font-weight: 600; margin-bottom: 12px;">🌱 免费社区版功能受限</span>
                        <h3 style="color: #FFD700; font-weight: 600; font-size: 1.1rem; margin-bottom: 8px; letter-spacing: 1px;">自定义路由矩阵锁定</h3>
                        <p style="color: #ccc; max-width: 420px; line-height: 1.6; font-size: 0.82rem;">自定义频道路由前缀、URL Mapping 与插槽样式定制属于高级出版功能。</p>
                        <p style="color: #888; font-size: 0.78rem; margin-top: 10px;">免费社区版系统已为您自动激活无缝的物理路径透传映射。</p>
                    </div>
                ` : ''}

                <!-- 🚀 [窄屏优化] 容器平滑横向滚动与防挤压最小宽度 -->
                <div style="overflow-x: auto; width: 100%; -webkit-overflow-scrolling: touch;">
                    <div style="min-width: 880px;">
                        <div class="matrix-header" style="display: grid; grid-template-columns: 36px 1.4fr 1.0fr 1.45fr 1.5fr 0.95fr 42px 36px; gap: 8px; padding: 12px 14px; background: rgba(0,0,0,0.25); font-size: 0.76rem; color: var(--text-dim); font-weight: 600; border-bottom: 1px solid var(--glass-border); align-items: center; white-space: nowrap;">
                            <span style="text-align: center;" title="调整导航菜单在顶栏的排列顺序">↕️ 排序</span>
                            <span>📁 文库路径</span>
                            <span>🔗 网页路径</span>
                            <span>🧩 网页模板</span>
                            <span>🏷️ 顶栏导航菜单</span>
                            <span>🗣️ 译文风格</span>
                            <span style="text-align: center;">👁️ 顶栏</span>
                            <span style="text-align: center;">操作</span>
                        </div>
                        
                        <div class="matrix-body" id="route-matrix-body" style="padding: 6px 10px;">
                            ${routes.length === 0 ? `
                                <div class="empty-state" style="padding: 40px; text-align: center; color: var(--text-dim);">
                                    暂无路由与导航策略。您的全部文件目前均按照原始物理路径进行映射发布。
                                </div>
                            ` : routes.map((route, idx) => `
                                <div class="matrix-row route-item" data-idx="${idx}" style="display: grid; grid-template-columns: 36px 1.4fr 1.0fr 1.45fr 1.5fr 0.95fr 42px 36px; gap: 8px; padding: 8px 6px; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.03); transition: background 0.2s; ${route.external_url ? 'background: rgba(0, 242, 254, 0.03); border-left: 2px solid var(--neon-cyan, #00f2fe); border-radius: 4px; margin: 3px 0;' : ''}">
                                    <!-- 0. 顺序调整控制器 -->
                                    <div class="order-controls" style="display: flex; flex-direction: column; gap: 2px; align-items: center; justify-content: center;">
                                        <button type="button" class="mini-btn move-up-btn" onclick="window.moveRouteMatrixRow(this, 'up')" ${!isLicensed || idx === 0 ? 'disabled' : ''} style="padding: 0; width: 22px; height: 13px; font-size: 0.55rem; line-height: 1; border-radius: 3px; background: rgba(255,255,255,0.05); color: ${idx === 0 ? 'rgba(255,255,255,0.2)' : 'var(--text-dim)'}; border: 1px solid rgba(255,255,255,0.08); cursor: ${idx === 0 ? 'default' : 'pointer'};" title="上移">▲</button>
                                        <button type="button" class="mini-btn move-down-btn" onclick="window.moveRouteMatrixRow(this, 'down')" ${!isLicensed || idx === routes.length - 1 ? 'disabled' : ''} style="padding: 0; width: 22px; height: 13px; font-size: 0.55rem; line-height: 1; border-radius: 3px; background: rgba(255,255,255,0.05); color: ${idx === routes.length - 1 ? 'rgba(255,255,255,0.2)' : 'var(--text-dim)'}; border: 1px solid rgba(255,255,255,0.08); cursor: ${idx === routes.length - 1 ? 'default' : 'pointer'};" title="下移">▼</button>
                                    </div>
                                    <!-- 1. 文库目录 -->
                                    <div>
                                        ${window.buildSourcePickerHtml ? window.buildSourcePickerHtml(route.source, isLicensed, !!route.external_url, route.target_slot || 'docs') : ''}
                                    </div>
                                    <!-- 2. 网页路径 / 外部 URL -->
                                    <div>
                                        ${route.external_url ? `
                                            <input type="text" class="setting-input ext-url-input" value="${route.external_url}" placeholder="https://github.com/..." title="${window.getLivePathTooltip ? window.getLivePathTooltip(route) : ''}" style="width: 100%; color: var(--neon-cyan, #00f2fe); font-family: monospace; font-size: 0.74rem; padding: 5px 6px;" ${!isLicensed ? 'disabled' : ''} onchange="syncRouteMatrixToSettings()" oninput="syncRouteMatrixToSettings(); window.updateAllLivePathBadges();">
                                        ` : `
                                            <input type="text" class="setting-input prefix-input" value="${route.prefix || ''}" placeholder="例如: /blog/" title="${window.getLivePathTooltip ? window.getLivePathTooltip(route) : ''}" style="width: 100%; color: var(--accent-secondary); font-family: monospace; font-size: 0.74rem; padding: 5px 6px;" ${!isLicensed ? 'disabled' : ''} onchange="syncRouteMatrixToSettings()" oninput="syncRouteMatrixToSettings(); window.updateAllLivePathBadges();">
                                        `}
                                    </div>
                                    <!-- 3. 网页模板槽位 -->
                                    <div>
                                        ${route.external_url ? `
                                            <span style="font-size: 0.72rem; color: var(--text-dim); padding: 4px 8px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 4px; display: inline-flex; align-items: center; gap: 4px;">🔗 外部直链 (无需模板)</span>
                                        ` : (() => {
            const defaultSlots = window.DEFAULT_THEME_SLOTS || {
                "docs": { "label": "📚 文档中心 (docs)" },
                "blog": { "label": "📰 博客文章 (blog)" },
                "showcase": { "label": "🎨 展示中心 (show)" },
                "pages": { "label": "📄 独立页面 (pages)" },
                "static": { "label": "📦 静态资源 (static)" }
            };
            const mergedSlots = Object.assign({}, defaultSlots, themeSlots || {});
            const hasSlots = Object.keys(mergedSlots).length > 0;
            const slotVal = route.target_slot || 'docs';
            const isStandard = !slotVal || Object.keys(mergedSlots).includes(slotVal) || (slotVal === 'pages' && mergedSlots.page) || (slotVal === 'page' && mergedSlots.pages);
            const formatSlotDisplay = (k, v) => {
                const rawLabel = (v && v.label) ? v.label : k;
                if (k === 'showcase') return `🎨 展示中心 (show)`;
                if (rawLabel.includes('(')) return rawLabel;
                const icons = { docs: '📚', blog: '📰', pages: '📄', page: '📄', showcase: '🎨', static: '📦' };
                const icon = icons[k] || '🧩';
                return `${icon} ${rawLabel} (${k})`;
            };
            let html = '';
            if (hasSlots) {
                html += `<select class="setting-input slot-select" style="width: 100%; font-size: 0.74rem; padding: 5px 6px; display: ${isStandard ? 'block' : 'none'};" ${!isLicensed ? 'disabled' : ''} onchange="if(this.value === '_custom') { this.style.display='none'; this.nextElementSibling.style.display='block'; this.nextElementSibling.value=''; this.nextElementSibling.focus(); } else { this.nextElementSibling.value=this.value; } const _row = this.closest('.matrix-row'); const _srcInput = _row?.querySelector('.source-input'); const _dl = _srcInput ? document.getElementById(_srcInput.getAttribute('list')) : null; if(_dl && window.buildSourceDatalistOptions) { _dl.innerHTML = window.buildSourceDatalistOptions(this.value, _srcInput.value); } syncRouteMatrixToSettings(); if(window.updateAllLivePathBadges) window.updateAllLivePathBadges();">`;
                Object.entries(mergedSlots).forEach(([k, v]) => {
                    const isSelected = (slotVal === k) || (slotVal === 'page' && k === 'pages') || (slotVal === 'pages' && k === 'page');
                    html += `<option value="${k}" ${isSelected ? 'selected' : ''}>${formatSlotDisplay(k, v)}</option>`;
                });
                html += `<option value="_custom" ${!isStandard ? 'selected' : ''}>✏️ 自定义... </option>`;
                html += `</select>`;
            }
            html += `<input type="text" class="setting-input slot-input" value="${slotVal}" placeholder="例如: docs" style="width: 100%; font-size: 0.74rem; padding: 5px 6px; display: ${!hasSlots || !isStandard ? 'block' : 'none'};" ${!isLicensed ? 'disabled' : ''} onchange="const _row = this.closest('.matrix-row'); const _srcInput = _row?.querySelector('.source-input'); const _dl = _srcInput ? document.getElementById(_srcInput.getAttribute('list')) : null; if(_dl && window.buildSourceDatalistOptions) { _dl.innerHTML = window.buildSourceDatalistOptions(this.value, _srcInput.value); } syncRouteMatrixToSettings(); if(window.updateAllLivePathBadges) window.updateAllLivePathBadges();" oninput="syncRouteMatrixToSettings()">`;
            return html;
        })()}
                                    </div>
                                    <!-- 4. 顶栏导航展示 (带图标快捷选择与 🌐 多语种配置) -->
                                    <div style="display: flex; gap: 4px; align-items: center; position: relative;">
                                        <button type="button" class="mini-btn icon-picker-btn" onclick="window.toggleIconPicker(this, event)" ${!isLicensed ? 'disabled' : ''} style="width: 30px; height: 26px; padding: 0; font-size: 0.92rem; border-radius: 6px; background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 255, 0.25); cursor: pointer; flex-shrink: 0; display: flex; align-items: center; justify-content: center; transition: all 0.2s;" title="点击弹出选择常见图标">
                                            <span class="icon-preview">${route.nav_icon || (route.external_url ? '🌐' : '📚')}</span>
                                        </button>
                                        <input type="hidden" class="nav-icon-input" value="${route.nav_icon || (route.external_url ? '🌐' : '📚')}">
                                        <input type="text" class="setting-input nav-label-input" value="${route.nav_label || ''}" placeholder="${route.source || (route.external_url ? '外部链接' : '显示名称')}" style="flex: 1; min-width: 0; font-size: 0.74rem; padding: 5px 6px;" ${!isLicensed ? 'disabled' : ''} onchange="syncRouteMatrixToSettings()" oninput="syncRouteMatrixToSettings()">
                                        
                                        <!-- 🌐 多语种导航配置按钮 -->
                                        ${(() => {
            const i18nMap = route.nav_label_i18n || {};
            const customCount = Object.keys(i18nMap).filter(k => !!i18nMap[k]).length;
            const hasCustom = customCount > 0;
            return `
                                                <button type="button" class="mini-btn nav-i18n-btn" onclick="window.toggleNavI18nModal(this, event)" ${!isLicensed ? 'disabled' : ''} style="padding: 2px 6px; height: 26px; font-size: 0.7rem; border-radius: 6px; background: ${hasCustom ? 'rgba(0, 255, 136, 0.15)' : 'rgba(255, 255, 255, 0.05)'}; border: 1px solid ${hasCustom ? 'rgba(0, 255, 136, 0.4)' : 'rgba(255, 255, 255, 0.1)'}; color: ${hasCustom ? 'var(--neon-green, #00ff88)' : 'var(--text-dim)'}; cursor: pointer; flex-shrink: 0; display: flex; align-items: center; gap: 3px;" title="${hasCustom ? `已定制 ${customCount} 种语言导航名称` : '配置多语种导航名称'}">
                                                    <span>🌐</span>
                                                    <span class="i18n-count-badge" style="font-size: 0.65rem; font-weight: 700;">${hasCustom ? customCount : '+'}</span>
                                                </button>
                                                <input type="hidden" class="nav-i18n-input" value='${JSON.stringify(i18nMap).replace(/'/g, "&apos;")}'>
                                            `;
        })()}
                                    </div>
                                    <!-- 5. 专属翻译风格 -->
                                    <div>
                                        ${window.buildTranslationStyleSelectHtml ? window.buildTranslationStyleSelectHtml(route.style, isLicensed, !!route.external_url) : `
                                            <select class="setting-input style-input" style="width: 100%; font-size: 0.74rem; padding: 5px 6px;" ${!isLicensed ? 'disabled' : ''} onchange="syncRouteMatrixToSettings()">
                                                <option value="">继承全局默认</option>
                                                <option value="professional" ${route.style === 'professional' ? 'selected' : ''}>💼 商务严谨</option>
                                                <option value="casual" ${route.style === 'casual' ? 'selected' : ''}>☕ 随性自然</option>
                                                <option value="literal" ${route.style === 'literal' ? 'selected' : ''}>⚖️ 精准直译</option>
                                            </select>
                                        `}
                                    </div>
                                    <!-- 6. 顶栏显示开关 -->
                                    <div style="text-align: center;">
                                        <input type="checkbox" class="nav-show-input" ${(route.show_in_nav !== false) ? 'checked' : ''} ${!isLicensed ? 'disabled' : ''} onchange="syncRouteMatrixToSettings()" style="cursor: pointer; transform: scale(1.1); accent-color: var(--accent-secondary, #00f2fe);" title="是否在网站顶栏导航显示" />
                                    </div>
                                    <!-- 7. 操作 -->
                                    <div style="text-align: center;">
                                        <button class="mini-btn" onclick="removeRouteMatrixRow(this)" style="background: rgba(255,50,50,0.1); border: 1px solid rgba(255,50,50,0.3); color: #ff5555; height: 26px; width: 26px; padding: 0; border-radius: 6px; cursor: pointer; transition: all 0.2s; font-size: 0.85rem;" title="删除此规则" ${!isLicensed ? 'disabled' : ''}>×</button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        
                        <div style="padding: 10px 14px; display: flex; gap: 10px; justify-content: space-between; border-top: 1px dashed var(--glass-border); background: var(--bg-glass, rgba(0,0,0,0.05)); border-radius: 0 0 8px 8px;">
                            <button type="button" class="add-rule-btn" onclick="addRouteMatrixRow()" style="flex: 1; background: var(--white-03, rgba(255,255,255,0.03)); border: 1px dashed ${isLicensed ? 'var(--accent-secondary, #00f2fe)' : 'var(--text-muted)'}; color: ${isLicensed ? 'var(--accent-secondary, #00f2fe)' : 'var(--text-muted)'}; padding: 8px 12px; border-radius: 6px; cursor: ${isLicensed ? 'pointer' : 'not-allowed'}; transition: all 0.25s ease; font-size: 0.8rem; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 6px;" title="${isLicensed ? '添加新内容频道' : '专属版特权功能'}">
                                ➕ 添加内容频道
                            </button>
                            <button type="button" class="add-rule-btn" onclick="addExternalNavRow()" style="flex: 1; background: var(--white-03, rgba(255,255,255,0.03)); border: 1px dashed ${isLicensed ? 'var(--neon-green, #00ff88)' : 'var(--text-muted)'}; color: ${isLicensed ? 'var(--neon-green, #00ff88)' : 'var(--text-muted)'}; padding: 8px 12px; border-radius: 6px; cursor: ${isLicensed ? 'pointer' : 'not-allowed'}; transition: all 0.25s ease; font-size: 0.8rem; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 6px;" title="${isLicensed ? '添加外部链接导航' : '专属版特权功能'}">
                                🌐 添加外部链接导航
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 22px; display: flex; flex-direction: column; gap: 14px;">
                <!-- 🏠 全站首页与根路径入口指引 -->
                <div style="padding: 14px 18px; background: rgba(0, 242, 255, 0.04); border: 1px solid rgba(0, 242, 255, 0.2); border-radius: 8px; display: flex; align-items: flex-start; gap: 12px;">
                    <span style="font-size: 1.3rem; margin-top: 2px;">🏠</span>
                    <div style="flex: 1;">
                        <div style="color: #00f2fe; font-weight: 600; font-size: 0.85rem; margin-bottom: 4px;">全站首页 (Home Index) 与根路径寻址规则</div>
                        <div style="color: var(--text-dim); font-size: 0.76rem; line-height: 1.5;">
                            若您未在上方指定根路径（<code>/</code>）频道，系统将默认采用文库根目录的 <b>README.md</b> 或 <b>index.md</b> 编译为全站静态首页。所有 SSG 主题均已内置品牌主页插槽适配。
                        </div>
                    </div>
                </div>

                <!-- 💡 频道与全景导航工作原理 -->
                <div style="padding: 14px 18px; background: rgba(255, 255, 255, 0.02); border: 1px dashed rgba(255, 255, 255, 0.15); border-radius: 8px;">
                    <h5 style="color: var(--accent-secondary, #00f2fe); margin-bottom: 8px; font-size: 0.88rem; font-weight: 700;">💡 频道与全景导航工作原理</h5>
                    <ul style="font-size: 0.78rem; color: var(--text-dim); line-height: 1.6; padding-left: 18px; margin: 0;">
                        <li><b>频道即导航</b>：配置好内容频道与 Web 路径后，系统自动将其编译为网站顶栏的导航菜单项（勾选“顶栏”即可生效）。</li>
                        <li><b>冲突实时预警</b>：网页路径（前缀）必须全站唯一。若输入了重复的路径，输入框将即时警示并阻断保存，防止破坏构建。</li>
                        <li><b>文库目录自愈感知</b>：若本地文件夹被改名或移动，系统会自动感知并提供一键关联自愈按钮。</li>
                        <li><b>跨 SSG 零死链自愈</b>：无论从 Sovereign 切换到 Docusaurus、VitePress 还是 Starlight，所有频道路径与多语言路由全部由适配器 100% 自动对齐。</li>
                    </ul>
                </div>
            </div>
        </div>
    `;

    setTimeout(() => {
        if (typeof window.updateAllLivePathBadges === 'function') {
            window.updateAllLivePathBadges();
        }
    }, 50);

    return html;
};

// ⚡ [SOP-02 模块拆分] 
// 网址路径与组织形态子面板渲染函数 (renderSlugSettingsCategory) -> route_shards/route.slug_render.js


/**
 * 🎨 切换装帧主题后，自动动态匹配并对齐频道映射的模板插槽与导航定义
 */
window.autoAlignRouteMatrixWithActiveTheme = async function (themeId) {
    try {
        const slotsRes = await apiFetch('/api/system/theme/slots');
        if (slotsRes && slotsRes.slots) {
            if (!window.settingsData) window.settingsData = {};
            window.settingsData._theme_slots = slotsRes.slots;

            const routes = window.settingsData.route_matrix || [];
            const slotKeys = Object.keys(slotsRes.slots);
            let updated = false;

            routes.forEach(route => {
                if (!route.external_url && route.target_slot && !slotKeys.includes(route.target_slot)) {
                    const fallbackSlot = slotKeys.includes('docs') ? 'docs' : slotKeys[0];
                    if (fallbackSlot) {
                        route.target_slot = fallbackSlot;
                        updated = true;
                    }
                }
            });

            if (updated && typeof window.syncRouteMatrixToSettings === 'function') {
                window.syncRouteMatrixToSettings();
            }

            const activeMatrix = document.getElementById('route-matrix-body');
            if (activeMatrix && typeof window.renderRouteMatrixCategory === 'function') {
                const subContent = document.getElementById('dissemination-routing-sub-content');
                if (subContent) {
                    subContent.innerHTML = window.renderRouteMatrixCategory();
                }
            }
        }
    } catch (e) {
        console.warn('⚠️ [RouteMatrix] 对齐新主题插槽失败:', e);
    }
};
