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
            <p class="section-desc" style="font-size: 0.8rem; margin-bottom: 25px; opacity: 0.85;">
                突破单纯的物理目录映射，将本地特定文件夹路由至全新的逻辑出版路径，并可为其指派专属的前端网页模板与 AI 翻译风格。
                ${!isLicensed ? '<br><span style="color: var(--accent-secondary); font-size: 0.75rem;">* 社区版将自动退避至物理目录映射模式。</span>' : ''}
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
    const dirMode = translation.slug_dir_mode || 'flat';
    const slugMode = translation.slug_mode || 'ai';

    let html = `
        <div class="full-width">
            <p class="section-desc" style="font-size: 0.85rem; margin-bottom: 25px; opacity: 0.85; line-height: 1.6;">
                配置全局原稿发布的 <b>URL 域名后缀格式与目录路径结构</b>。系统内置零技术门槛的物理路径推导引擎，帮助您打造极具 SEO 优势或清晰简洁的动态数字花园。
            </p>

            <!-- 1. 基础 Slug 命名法则 -->
            <div style="margin-bottom: 25px;">
                <h4 style="font-size: 0.95rem; color: #fff; margin-bottom: 12px; font-weight: 600;">1. 基础命名法则 (Slug Naming)</h4>
                <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                    <label style="flex: 1; min-width: 260px; padding: 15px 20px; background: ${slugMode === 'ai' ? 'rgba(0, 242, 255, 0.08)' : 'rgba(255,255,255,0.02)'}; border: 1px solid ${slugMode === 'ai' ? 'var(--accent-secondary, #00f2fe)' : 'var(--glass-border)'}; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 12px;">
                        <input type="radio" name="translation_slug_mode" value="ai" ${slugMode === 'ai' ? 'checked' : ''} onchange="window.settingsData.translation.slug_mode='ai'; window.updateSlugSandboxPreview(); if(typeof addAudit==='function') addAudit('📝 Slug 命名法则已切换为【🤖 AI 自动推导】');" />
                        <div>
                            <div style="font-weight: 600; color: #fff; font-size: 0.9rem;">🤖 AI 智能推导 (推荐)</div>
                            <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 4px;">自动提取中文标题的核心语义，转化为简短优雅的英文短网址</div>
                        </div>
                    </label>
                    <label style="flex: 1; min-width: 260px; padding: 15px 20px; background: ${slugMode === 'filename' ? 'rgba(0, 242, 255, 0.08)' : 'rgba(255,255,255,0.02)'}; border: 1px solid ${slugMode === 'filename' ? 'var(--accent-secondary, #00f2fe)' : 'var(--glass-border)'}; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 12px;">
                        <input type="radio" name="translation_slug_mode" value="filename" ${slugMode === 'filename' ? 'checked' : ''} onchange="window.settingsData.translation.slug_mode='filename'; window.updateSlugSandboxPreview(); if(typeof addAudit==='function') addAudit('📝 Slug 命名法则已切换为【📁 物理文件名清洗】');" />
                        <div>
                            <div style="font-weight: 600; color: #fff; font-size: 0.9rem;">📁 物理文件名清洗</div>
                            <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 4px;">直接擦除原始文件名中的特殊标点与空格，保留源文件物理名</div>
                        </div>
                    </label>
                </div>
            </div>

            <!-- 2. 网址路径组织形态卡片 (强制一行三列物理并排，同屏直观联动) -->
            <div style="margin-bottom: 20px;">
                <h4 style="font-size: 0.9rem; color: #fff; margin-bottom: 10px; font-weight: 600;">2. 网址路径组织形态 (网址结构三选一)</h4>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; width: 100%;">
                    <!-- 卡片 1: 极简根目录 -->
                    <div class="slug-dir-card ${dirMode === 'flat' ? 'active' : ''}" data-mode="flat" onclick="window.selectSlugDirModeCard('flat')" style="padding: 12px 14px; border-radius: 8px; cursor: pointer; transition: all 0.3s ease; border: 1px solid ${dirMode === 'flat' ? 'var(--accent-secondary, #00f2fe)' : 'var(--glass-border)'}; background: ${dirMode === 'flat' ? 'rgba(0, 242, 255, 0.06)' : 'rgba(255, 255, 255, 0.02)'}; flex: 1; min-width: 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-weight: 600; font-size: 0.85rem; color: #fff; white-space: nowrap;">📄 极简根目录</span>
                            <span style="font-size: 0.65rem; background: rgba(0, 242, 255, 0.2); color: #00f2fe; padding: 1px 5px; border-radius: 4px; font-weight: 600; shrink: 0;">推荐</span>
                        </div>
                        <p style="font-size: 0.72rem; color: var(--text-dim); line-height: 1.4; margin-bottom: 8px; min-height: 28px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                            忽略 Obsidian 本地子文件夹层级，所有网页物理落盘并挂载在<b>站点根目录</b>下。
                        </p>
                        <div style="font-family: monospace; font-size: 0.7rem; background: rgba(0,0,0,0.35); padding: 5px 8px; border-radius: 4px; color: #00f2fe; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="site.com/install-guide.html">
                            site.com/install-guide.html
                        </div>
                    </div>

                    <!-- 卡片 2: 目录前缀 -->
                    <div class="slug-dir-card ${dirMode === 'prefix' ? 'active' : ''}" data-mode="prefix" onclick="window.selectSlugDirModeCard('prefix')" style="padding: 12px 14px; border-radius: 8px; cursor: pointer; transition: all 0.3s ease; border: 1px solid ${dirMode === 'prefix' ? 'var(--accent-secondary, #00f2fe)' : 'var(--glass-border)'}; background: ${dirMode === 'prefix' ? 'rgba(0, 242, 255, 0.06)' : 'rgba(255, 255, 255, 0.02)'}; flex: 1; min-width: 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-weight: 600; font-size: 0.85rem; color: #fff; white-space: nowrap;">🔗 智能 SEO 前缀</span>
                        </div>
                        <p style="font-size: 0.72rem; color: var(--text-dim); line-height: 1.4; margin-bottom: 8px; min-height: 28px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                            物理文件仍落盘在根目录，自动提取父文件夹为 Slug 连字符前缀，提升 SEO。
                        </p>
                        <div style="font-family: monospace; font-size: 0.7rem; background: rgba(0,0,0,0.35); padding: 5px 8px; border-radius: 4px; color: #00f2fe; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="site.com/tech-guide-install.html">
                            site.com/tech-guide-install.html
                        </div>
                    </div>

                    <!-- 卡片 3: 目录树复刻 -->
                    <div class="slug-dir-card ${dirMode === 'nested' ? 'active' : ''}" data-mode="nested" onclick="window.selectSlugDirModeCard('nested')" style="padding: 12px 14px; border-radius: 8px; cursor: pointer; transition: all 0.3s ease; border: 1px solid ${dirMode === 'nested' ? 'var(--accent-secondary, #00f2fe)' : 'var(--glass-border)'}; background: ${dirMode === 'nested' ? 'rgba(0, 242, 255, 0.06)' : 'rgba(255, 255, 255, 0.02)'}; flex: 1; min-width: 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-weight: 600; font-size: 0.85rem; color: #fff; white-space: nowrap;">📂 目录树复刻</span>
                        </div>
                        <p style="font-size: 0.72rem; color: var(--text-dim); line-height: 1.4; margin-bottom: 8px; min-height: 28px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                            网页网址与您的本地 Obsidian 文件夹多级层级结构 <b>1:1 完全物理对齐</b>。
                        </p>
                        <div style="font-family: monospace; font-size: 0.7rem; background: rgba(0,0,0,0.35); padding: 5px 8px; border-radius: 4px; color: #00f2fe; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="site.com/docs/tech/guide/install.html">
                            site.com/docs/tech/guide/...
                        </div>
                    </div>
                </div>
            </div>

            <!-- 3. 实时 URL 沙盒模拟器 -->
            <div style="margin-bottom: 25px; padding: 20px; background: rgba(0, 242, 255, 0.03); border: 1px dashed rgba(0, 242, 255, 0.2); border-radius: 12px; position: relative;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <h4 style="font-size: 0.95rem; color: #00f2fe; font-weight: 600; margin: 0; display: flex; align-items: center; gap: 8px;">
                        🧪 实时 URL 沙盒模拟器 (Live URL Playground)
                    </h4>
                    <span style="font-size: 0.72rem; color: var(--text-dim);">随选随变 · 即时计算推导</span>
                </div>

                <div style="display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 250px;">
                        <label style="font-size: 0.78rem; color: var(--text-dim); display: block; margin-bottom: 6px;">📂 选择测试原稿路径:</label>
                        <select id="sandbox-file-select" onchange="window.updateSlugSandboxPreview();" style="width: 100%; padding: 8px 12px; background: rgba(0,0,0,0.4); border: 1px solid var(--glass-border); border-radius: 6px; color: #fff; font-size: 0.82rem;">
                            <option value="tech/guide/安装与部署指南.md">tech/guide/安装与部署指南.md</option>
                            <option value="journal/2026/我的第二脑随想.md">journal/2026/我的第二脑随想.md</option>
                            <option value="projects/core/系统架构说明.md">projects/core/系统架构说明.md</option>
                            <option value="_custom">✏️ 手动输入自定义路径...</option>
                        </select>
                    </div>
                    <div style="flex: 1; min-width: 250px;">
                        <label style="font-size: 0.78rem; color: var(--text-dim); display: block; margin-bottom: 6px;">✏️ 自定义相对路径 (可选):</label>
                        <input type="text" id="sandbox-custom-input" placeholder="例如: docs/setup/quick-start.md" oninput="window.updateSlugSandboxPreview();" style="width: 100%; padding: 8px 12px; background: rgba(0,0,0,0.4); border: 1px solid var(--glass-border); border-radius: 6px; color: #fff; font-size: 0.82rem;" />
                    </div>
                </div>

                <!-- 模拟器推导高亮盒子 -->
                <div style="background: rgba(10, 11, 24, 0.7); padding: 15px; border-radius: 8px; border: 1px solid rgba(0, 242, 255, 0.15); display: flex; flex-direction: column; gap: 8px; font-family: monospace; font-size: 0.8rem;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #888; width: 140px; shrink: 0;">🌐 线上访问 URL:</span>
                        <span id="sandbox-preview-web-url" style="color: #00f2fe; word-break: break-all;">-</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #888; width: 140px; shrink: 0;">📁 物理落盘位置:</span>
                        <span id="sandbox-preview-disk-path" style="color: var(--text-dim); word-break: break-all;">-</span>
                    </div>
                </div>
            </div>

            <!-- 4. 高级频道重定向引流提示 -->
            <div style="padding: 15px 20px; background: rgba(255, 255, 255, 0.02); border: 1px dashed rgba(255, 255, 255, 0.1); border-radius: 8px; font-size: 0.82rem; color: var(--text-dim); display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.1rem;">🎯</span>
                    <span>需要把特定文件夹（如 <code>vault/journal</code>）单独映射为特定 Web 频道（如 <code>/blog/</code>）并指定模板？</span>
                </div>
                <a href="javascript:void(0)" onclick="window.switchI18nRoutingSubTab('route_matrix', this)" style="color: #00f2fe; text-decoration: none; font-weight: 600; padding: 6px 14px; background: rgba(0, 242, 255, 0.1); border-radius: 6px; border: 1px solid rgba(0, 242, 255, 0.3); font-size: 0.78rem;">
                    🧭 打开物理路由矩阵 ➔
                </a>
            </div>
        </div>
    `;

    // 延迟少许触发沙盒计算与真实文稿列表 populate
    setTimeout(() => {
        if (typeof window.populateSandboxRealFiles === 'function') {
            window.populateSandboxRealFiles();
        } else if (typeof window.updateSlugSandboxPreview === 'function') {
            window.updateSlugSandboxPreview();
        }
    }, 50);

    return html;
};
