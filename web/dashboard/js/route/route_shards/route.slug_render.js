/**
 * 🛣️ [V1.0] Advanced Channel Routing - Slug Settings Render Shard
 * 职责：渲染治理中心【📝 网址路径】二级子面板 (renderSlugSettingsCategory)。
 * 包含：基础 Slug 命名法则、网址路径组织形态三卡片 (目录树复刻/极简根目录/智能SEO前缀) 与实时 URL 沙盒宿主容器构建。
 * 对应重构拆分协议：SOP-01/SOP-02 模板一合规物理平移。
 */

(function () {
    'use strict';

    window.renderSlugSettingsCategory = function () {
        const settings = window.settingsData || {};
        const isLicensed = settings._is_licensed || false;
        const translation = settings.translation || {};
        const activeTheme = (settings.active_theme || 'universal').toLowerCase();
        const isNativeTheme = ['sovereign', 'universal', 'default'].includes(activeTheme);

        // 🚀 [V106.0] 智能防呆守卫：若当前为第三方生态框架，强制安全收敛为 nested
        let dirMode = translation.slug_dir_mode || 'nested';
        if (!isNativeTheme && dirMode !== 'nested') {
            dirMode = 'nested';
            translation.slug_dir_mode = 'nested';
        }
        const slugMode = translation.slug_mode || 'ai';

        const flatClick = isNativeTheme ? "window.selectSlugDirModeCard('flat')" : `window.notifySlugLockedByTheme('flat', '${activeTheme}')`;
        const prefixClick = isNativeTheme ? "window.selectSlugDirModeCard('prefix')" : `window.notifySlugLockedByTheme('prefix', '${activeTheme}')`;

        let html = `
            <div class="full-width">
                <!-- 1. 基础 Slug 命名法则 -->
                <div style="margin-bottom: 25px;">
                    <h4 style="font-size: 0.95rem; color: var(--text-bright, #ffffff); margin-bottom: 12px; font-weight: 600;">1. 基础命名法则 (Slug Naming)</h4>
                    <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                        <label style="flex: 1; min-width: 260px; padding: 15px 20px; background: ${slugMode === 'ai' ? 'rgba(0, 242, 255, 0.08)' : 'var(--bg-glass, rgba(255,255,255,0.02))'}; border: 1px solid ${slugMode === 'ai' ? 'var(--accent-secondary, #00f2fe)' : 'var(--glass-border)'}; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 12px;">
                            <input type="radio" name="translation_slug_mode" value="ai" ${slugMode === 'ai' ? 'checked' : ''} onchange="window.settingsData.translation.slug_mode='ai'; window.updateSlugSandboxPreview(); if(typeof addAudit==='function') addAudit('📝 Slug 命名法则已切换为【🤖 AI 自动推导】');" />
                            <div>
                                <div style="font-weight: 600; color: var(--text-bright, #ffffff); font-size: 0.9rem;">🤖 AI 智能推导 (推荐)</div>
                                <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 4px;">自动提取中文标题的核心语义，转化为简短优雅的英文短网址</div>
                            </div>
                        </label>
                        <label style="flex: 1; min-width: 260px; padding: 15px 20px; background: ${slugMode === 'filename' ? 'rgba(0, 242, 255, 0.08)' : 'var(--bg-glass, rgba(255,255,255,0.02))'}; border: 1px solid ${slugMode === 'filename' ? 'var(--accent-secondary, #00f2fe)' : 'var(--glass-border)'}; border-radius: 8px; cursor: pointer; display: flex; align-items: center; gap: 12px;">
                            <input type="radio" name="translation_slug_mode" value="filename" ${slugMode === 'filename' ? 'checked' : ''} onchange="window.settingsData.translation.slug_mode='filename'; window.updateSlugSandboxPreview(); if(typeof addAudit==='function') addAudit('📝 Slug 命名法则已切换为【📁 物理文件名清洗】');" />
                            <div>
                                <div style="font-weight: 600; color: var(--text-bright, #ffffff); font-size: 0.9rem;">📁 物理文件名清洗</div>
                                <div style="font-size: 0.75rem; color: var(--text-dim); margin-top: 4px;">直接擦除原始文件名中的特殊标点与空格，保留源文件物理名</div>
                            </div>
                        </label>
                    </div>
                </div>

                <!-- 2. 网址路径组织形态卡片 (默认项排在首位) -->
                <div style="margin-bottom: 20px;">
                    <h4 style="font-size: 0.9rem; color: var(--text-bright, #ffffff); margin-bottom: 10px; font-weight: 600;">2. 网址路径组织形态 (网址结构三选一)</h4>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; width: 100%;">
                        <!-- 卡片 1: 目录树复刻 (默认推荐) -->
                        <div class="slug-dir-card ${dirMode === 'nested' ? 'active' : ''}" data-mode="nested" onclick="window.selectSlugDirModeCard('nested')">
                            <span class="slug-corner-badge badge-nested">${!isNativeTheme ? '🛡️ 框架专享' : '🌟 默认推荐'}</span>
                            <div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px; margin-bottom: 8px;">
                                    <span style="font-weight: 600; font-size: 0.85rem; color: var(--text-bright, #ffffff); white-space: nowrap;">📂 目录树复刻</span>
                                    <span class="slug-radio-indicator">${dirMode === 'nested' ? '✓' : ''}</span>
                                </div>
                                <p style="font-size: 0.72rem; color: var(--text-dim); line-height: 1.4; margin-bottom: 10px; font-weight: 400;">
                                    网页网址与您本地原稿文件夹的多级层级结构 <b>1:1 完全物理对齐</b>。
                                </p>
                            </div>
                            <div class="sample-url-box" title="site.com/docs/tech/guide/install.html">
                                site.com/docs/tech/guide/install.html
                            </div>
                        </div>

                        <!-- 卡片 2: 极简根目录 -->
                        <div class="slug-dir-card ${dirMode === 'flat' ? 'active' : ''} ${!isNativeTheme ? 'disabled' : ''}" data-mode="flat" onclick="${flatClick}" title="${!isNativeTheme ? '当前第三方主题依赖文件树路由，不支持极简根目录' : ''}">
                            <span class="slug-corner-badge ${!isNativeTheme ? 'badge-locked' : 'badge-flat'}">${!isNativeTheme ? '🔒 框架受限' : '⚡ 最短 URL'}</span>
                            <div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px; margin-bottom: 8px;">
                                    <span style="font-weight: 600; font-size: 0.85rem; color: var(--text-bright, #ffffff); white-space: nowrap;">📄 极简根目录</span>
                                    <span class="slug-radio-indicator">${dirMode === 'flat' ? '✓' : ''}</span>
                                </div>
                                <p style="font-size: 0.72rem; color: var(--text-dim); line-height: 1.4; margin-bottom: 10px; font-weight: 400;">
                                    忽略本地原稿文件夹层级，所有网页统一平铺落盘在<b>站点根目录</b>下，网址最短最简洁。
                                </p>
                            </div>
                            <div class="sample-url-box" title="site.com/install-guide.html">
                                site.com/install-guide.html
                            </div>
                        </div>

                        <!-- 卡片 3: 目录前缀 -->
                        <div class="slug-dir-card ${dirMode === 'prefix' ? 'active' : ''} ${!isNativeTheme ? 'disabled' : ''}" data-mode="prefix" onclick="${prefixClick}" title="${!isNativeTheme ? '当前第三方主题依赖文件树路由，不支持智能前缀' : ''}">
                            <span class="slug-corner-badge ${!isNativeTheme ? 'badge-locked' : 'badge-prefix'}">${!isNativeTheme ? '🔒 框架受限' : '🎯 SEO 增强'}</span>
                            <div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px; margin-bottom: 8px;">
                                    <span style="font-weight: 600; font-size: 0.85rem; color: var(--text-bright, #ffffff); white-space: nowrap;">🔗 智能 SEO 前缀</span>
                                    <span class="slug-radio-indicator">${dirMode === 'prefix' ? '✓' : ''}</span>
                                </div>
                                <p style="font-size: 0.72rem; color: var(--text-dim); line-height: 1.4; margin-bottom: 10px; font-weight: 400;">
                                    物理文件仍落盘在根目录，自动将原稿父文件夹提取并拼接为连字符 URL 前缀（深层子目录按层级以连字符 <code>-</code> 依次拼接）。
                                </p>
                            </div>
                            <div class="sample-url-box" title="site.com/tech-guide-install.html">
                                site.com/tech-guide-install.html
                            </div>
                        </div>
                    </div>

                    <!-- 架构兼容性与第三方框架建议提示卡片 -->
                    <div style="margin-top: 12px; padding: 12px 16px; background: rgba(0, 242, 255, 0.04); border: 1px solid rgba(0, 242, 255, 0.15); border-radius: 8px; font-size: 0.78rem; color: var(--text-dim); line-height: 1.5;">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                            <span style="font-size: 0.95rem;">🛡️</span>
                            <strong style="color: var(--text-bright, #ffffff);">主题架构兼容性提示 (Theme Architecture Compatibility)</strong>
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 4px;">
                            <div>
                                <span style="color: #10b981; font-weight: 600;">✓ 原生渲染引擎 (Sovereign / Universal)</span>：100% 原生支持【极简根目录】、【智能 SEO 前缀】与【目录树复刻】，系统会自动进行跨级内链修正与双向链接平铺重写。
                            </div>
                            <div>
                                <span style="color: #f59e0b; font-weight: 600;">⚠️ 外部生态框架 (Docusaurus / VitePress / Starlight / Nextra / Hugo / Hexo)</span>：依赖物理文件树与 Feature Slots 槽位规则，推荐使用<b>【📂 目录树复刻 (nested)】</b>，以确保第三方框架打包器正确识别侧边栏与多语言路由。
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 3. 实时 URL 沙盒模拟器 -->
                <div style="margin-bottom: 25px; padding: 20px; background: rgba(0, 242, 255, 0.03); border: 1px dashed rgba(0, 242, 255, 0.2); border-radius: 12px; position: relative;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h4 style="font-size: 0.95rem; color: var(--accent-secondary, #00f2fe); font-weight: 600; margin: 0; display: flex; align-items: center; gap: 8px;">
                            🧪 实时 URL 沙盒模拟器 (Live URL Playground)
                        </h4>
                        <span style="font-size: 0.72rem; color: var(--text-dim);">随选随变 · 即时计算推导</span>
                    </div>

                    <div style="display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap;">
                        <div style="flex: 1; min-width: 250px;">
                            <label style="font-size: 0.78rem; color: var(--text-dim); display: block; margin-bottom: 6px;">📂 选择测试原稿路径:</label>
                            <select id="sandbox-file-select" onchange="window.updateSlugSandboxPreview();" style="width: 100%; padding: 8px 12px; background: var(--bg-solid, rgba(0,0,0,0.4)); border: 1px solid var(--glass-border); border-radius: 6px; color: var(--text-bright, #ffffff); font-size: 0.82rem;">
                                <option value="tech/guide/安装与部署指南.md">tech/guide/安装与部署指南.md</option>
                                <option value="journal/2026/我的第二脑随想.md">journal/2026/我的第二脑随想.md</option>
                                <option value="projects/core/系统架构说明.md">projects/core/系统架构说明.md</option>
                                <option value="_custom">✏️ 手动输入自定义路径...</option>
                            </select>
                        </div>
                        <div style="flex: 1; min-width: 250px;">
                            <label style="font-size: 0.78rem; color: var(--text-dim); display: block; margin-bottom: 6px;">✏️ 自定义相对路径 (可选):</label>
                            <input type="text" id="sandbox-custom-input" placeholder="例如: docs/setup/quick-start.md" oninput="window.updateSlugSandboxPreview();" style="width: 100%; padding: 8px 12px; background: var(--bg-solid, rgba(0,0,0,0.4)); border: 1px solid var(--glass-border); border-radius: 6px; color: var(--text-bright, #ffffff); font-size: 0.82rem;" />
                        </div>
                    </div>

                    <!-- 多语种全息并列推导矩阵盒子 -->
                    <div style="margin-bottom: 12px;">
                        <div style="font-size: 0.78rem; color: var(--text-dim); margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between;">
                            <span>🌐 多语种全息推导矩阵 (母语 + 全量目标翻译语种):</span>
                            <span style="font-size: 0.7rem; color: var(--accent-secondary, #00f2fe);">所见即所得 · 联动主语言前缀开关</span>
                        </div>
                        <div id="sandbox-multilingual-matrix">
                            <div style="padding: 15px; text-align: center; color: var(--text-dim); font-size: 0.78rem;">⏳ 正在推导全息多语种访问路径...</div>
                        </div>
                    </div>

                    <!-- 动态解析诊断徽标栏 -->
                    <div id="sandbox-preview-diagnostic-bar"></div>

                    <!-- 🚀 物理就绪状态与重新发布友好提醒卡片 -->
                    <div id="sandbox-preview-status-box"></div>
                </div>

                <!-- 4. 高级频道重定向引流提示 -->
                <div style="padding: 15px 20px; background: rgba(255, 255, 255, 0.02); border: 1px dashed rgba(255, 255, 255, 0.1); border-radius: 8px; font-size: 0.82rem; color: var(--text-dim); display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 1.1rem;">🎯</span>
                        <span>需要把特定文件夹（如 <code>vault/journal</code>）单独映射为特定 Web 频道（如 <code>/blog/</code>）并指定模板？</span>
                    </div>
                    <a href="javascript:void(0)" onclick="if(typeof window.switchDisseminationRoutingSubTab==='function'){window.switchDisseminationRoutingSubTab('route_matrix', this);}else if(typeof window.switchI18nRoutingSubTab==='function'){window.switchI18nRoutingSubTab('route_matrix', this);}" style="color: #00f2fe; text-decoration: none; font-weight: 600; padding: 6px 14px; background: rgba(0, 242, 255, 0.1); border-radius: 6px; border: 1px solid rgba(0, 242, 255, 0.3); font-size: 0.78rem;">
                        🧭 打开频道映射矩阵 ➔
                    </a>
                </div>
            </div>
        `;

        setTimeout(() => {
            if (typeof window.populateSandboxRealFiles === 'function') window.populateSandboxRealFiles();
            else if (typeof window.updateSlugSandboxPreview === 'function') window.updateSlugSandboxPreview();
        }, 50);
        return html;
    };
})();
