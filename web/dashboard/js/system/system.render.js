/**
 * 🎨 [V57.4] Illacme Plenipes System Settings Render Component
 * 职责：系统设置中的“常规配置”与“安全审计”选项卡 DOM 的渲染。
 * 对应重构拆分协议：SOP-02/SOP-05 模板一合规物理平移。
 */

(function() {
    // 3. 基础信息渲染
    function renderGeneralCategory() {
        const data = window.settingsData;
        return `
            <div class="full-width">
                <div class="section-header"><h3>ℹ️ 基础信息 (General Information)</h3></div>
                <p class="section-desc">管理当前出版版图的核心身份标识与全域元数据。</p>
                
                <div class="settings-group">
                    <h4>🏷️ 品牌与站点身份 (Imprint & Site Identity)</h4>
                    <div class="settings-grid">
                        ${renderSettingsItem('版图展示名称', 'imprint_name', data.imprint_name || '')}
                        ${renderSettingsItem('版图描述', 'imprint_description', data.imprint_description || '')}
                        ${renderSettingsItem('全局站点名称', 'site_name', data.site_name || '', 'text', {placeholder: '未填则自愈 fallback 为版图展示名称'})}
                        ${renderSettingsItem('全局站点描述', 'site_description', data.site_description || '', 'text', {placeholder: '未填则自愈 fallback 为版图描述'})}
                        ${renderSettingsItem('全局品牌 Logo 路径', 'logo_path', data.logo_path || '', 'text', {placeholder: '例如: /static/logo.png'})}
                        ${renderSettingsItem('全局 Favicon 图标路径', 'favicon_path', data.favicon_path || '', 'text', {placeholder: '例如: /static/favicon.ico'})}
                    </div>
                </div>

                <div class="settings-group mt-large">
                    <h4>📖 出版合规与元数据 (Publishing Compliance & Metadata)</h4>
                    <div class="settings-grid">
                        ${renderSettingsItem('主站点 URL', 'site_url', data.site_url || '')}
                        ${renderSettingsItem('默认作者署名', 'frontmatter_defaults.author', data.frontmatter_defaults?.author || '')}
                        ${renderSettingsItem('全域版权声明', 'frontmatter_defaults.copyright', data.frontmatter_defaults?.copyright || '© 2024 All Rights Reserved')}
                        ${renderSettingsItem('出版许可证 (License)', 'frontmatter_defaults.license', data.frontmatter_defaults?.license || 'CC BY-NC-SA 4.0')}
                    </div>
                </div>

                <div class="settings-group mt-large">
                    <h4>📂 数据存储与原稿适配 (Storage & Dialect Adaptation)</h4>
                    <div class="settings-grid">
                        ${renderSettingsItem('原稿文库路径', 'vault_root', data.vault_root || '', 'static', {
                            description: '🔒 物理主权路径在版图确立后不可变。如需迁移资产领土，请新建版图。'
                        })}
                        ${renderSettingsItem('首选解析协议', 'ingress_settings.active_dialects', data.ingress_settings?.active_dialects?.[0] || 'auto', 'select', {
                            items: [
                                {value: 'auto', text: '✨ 自动感应 (Auto-Sensing)'},
                                {value: 'obsidian', text: 'Obsidian Connector'},
                                {value: 'logseq', text: 'Logseq Adapter'},
                                {value: 'notion', text: 'Notion Sync'},
                                {value: 'typora', text: 'Typora Dialect'},
                                {value: 'mkdocs', text: 'MkDocs Standard'}
                            ],
                            onchange: `window.updateConfigField('ingress_settings.active_dialects', [this.value])`,
                            description: '定义系统如何识别原稿格式。选择“自动感应”将根据文件特征物理识别；选择特定协议则执行主权强制解析。'
                        })}
                        ${renderSettingsItem('段落缓存存储目录', 'block_cache_dir', data.block_cache_dir || '', 'text', {
                            placeholder: '默认为空（自愈退避至项目根目录下的隐藏目录 .plenipes/blocks/）',
                            description: '跨版图共享段落缓存物理存储根目录。支持自定义重定向以实现在任意版图和任意 SSG 主题之间共用。'
                        })}
                        ${renderSettingsItem('段落缓存目录分级', 'block_cache_shard_levels', data.block_cache_shard_levels ?? 0, 'select', {
                            items: [
                                {value: 0, text: '📂 不分级 (如 blocks/lang/style/hash.txt)'},
                                {value: 1, text: '📂 一级前缀分流 (如 blocks/lang/style/ab/hash.txt)'},
                                {value: 2, text: '📂 二级前缀分流 (如 blocks/lang/style/ab/cd/hash.txt)'},
                                {value: 3, text: '📂 三级前缀分流 (如 blocks/lang/style/ab/cd/ef/hash.txt)'}
                            ],
                            onchange: `window.updateConfigField('block_cache_shard_levels', parseInt(this.value))`,
                            description: '通过分切段落原文哈希前缀的字符数进行多级目录分流，避免单个目录包含海量碎片文件导致的 IO 性能下降。'
                        })}
                        ${renderSettingsItem('Markdown 换行渲染模式', 'ingress_settings.hard_line_break', data.ingress_settings?.hard_line_break ?? false, 'select', {
                            items: [
                                {value: false, text: '📄 标准模式 — 单个换行符保留为段落流，需空行才能真正换行 (CommonMark 标准)'},
                                {value: true,  text: '✍️ 直觉模式 — 单个换行符直接渲染为新行，所见即所得，推荐日常写作使用 (GFM 兼容)'}
                            ],
                            onchange: `window.updateConfigField('ingress_settings.hard_line_break', this.value === 'true')`,
                            description: '控制原稿文库编辑器预览区和译文校对工作台中的换行渲染方式。<br>· <b>标准模式</b>：Markdown 原生行为，段落内换行不生效，需空行分段；适合有 Markdown 经验的专业用户。<br>· <b>直觉模式</b>：按 Enter 即换行，预览效果与编辑区完全对齐；适合从其他编辑器迁移或习惯"所见即所得"的用户。<br><span style="color: var(--text-dim); font-size: 0.8em;">⚠️ 修改后需保存配置，刷新页面后生效。</span>'
                        })}
                    </div>
                </div>

                <div class="settings-group mt-large">
                    <h4>🧰 段落缓存治理中枢 (Block Cache Hub)</h4>
                    <p class="section-desc" style="font-size: 0.8rem; opacity: 0.85; margin-bottom: 12px;">实时盘点和管理跨版图共享段落翻译缓存的占用状态并执行搬移和清理。</p>
                    <div class="settings-grid" style="grid-template-columns: 1fr 1fr; gap: 20px; background: rgba(255,255,255,0.02); padding: 15px; border-radius: 6px; border: 1px dashed rgba(255,255,255,0.08);">
                        <div style="display: flex; flex-direction: column; gap: 8px;">
                            <div style="font-size: 0.85rem; opacity: 0.75;">缓存状态盘点：</div>
                            <div style="font-size: 0.95rem; font-weight: bold; color: var(--accent, #00ff88);" id="cache-stats-count">正在统计...</div>
                            <div style="font-size: 0.95rem; font-weight: bold; color: var(--accent, #00ff88);" id="cache-stats-size">正在统计...</div>
                        </div>
                        <div style="display: flex; flex-direction: column; justify-content: center; gap: 10px;">
                            <div style="display: flex; gap: 10px;">
                                <button type="button" class="primary-btn glow-btn" onclick="window.manualMigrateCache()" style="padding: 6px 14px; font-size: 0.75rem; height: 32px; line-height: 14px;">🚚 物理分级迁移</button>
                                <button type="button" class="danger-btn" onclick="window.clearBlockCacheAll()" style="padding: 6px 14px; font-size: 0.75rem; height: 32px; line-height: 14px;">🗑️ 清空所有缓存</button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="settings-group mt-large">
                    <h4>⚙️ 系统基座与遥测运维 (Engine Base & Telemetry)</h4>
                    <div class="settings-grid">
                        ${renderSettingsItem('系统底座版本', 'version', data.version || 'V24.0', 'text', {readonly: true})}
                        ${renderSettingsItem('系统日志级别', 'system.log_level', data.system?.log_level || 'INFO', 'select', {
                            items: [
                                {value: 'DEBUG', text: 'DEBUG (全量输出)'},
                                {value: 'INFO', text: 'INFO (常规运行)'},
                                {value: 'WARNING', text: 'WARNING (仅告警)'},
                                {value: 'ERROR', text: 'ERROR (仅异常)'}
                            ],
                            description: '控制服务器后端在终端输出的日志详细程度。建议使用 WARNING 级别以保持静音。'
                        })}
                        ${renderSettingsItem('启用 HTTP 访问日志', 'system.access_log', data.system?.access_log ?? true, 'checkbox', {
                            description: '是否记录每一次网页 and API 访问（包含心跳请求）。建议关闭以防终端频繁被 stats 心跳刷屏。'
                        })}
                        ${renderSettingsItem('AI 并发排队超时 (秒)', 'system.resilience.ai_semaphore_timeout', data.system?.resilience?.ai_semaphore_timeout ?? 3600, 'number', {
                            description: '翻译在高并发且算力满载时，在本地队列中等待获取执行资源的最长等待秒数。如果任务在队列中积压超时将抛出 AI_SEMAPHORE_TIMEOUT，建议设置为 3600 秒以上以防任务被提前取消。'
                        })}
                    </div>
                </div>
            </div>
        `;
    }

    // 4. 安全审计渲染
    function renderSecurityCategory() {
        const sys = window.settingsData?.system || {};
        const gov = window.settingsData?.governance || {};
        const rg = gov.resource_guard || { cpu_threshold: 85 };
        
        setTimeout(() => {
            if (typeof window.loadAndRenderConfigAudit === 'function') {
                window.loadAndRenderConfigAudit();
            }
        }, 50);

        return `
            <div class="full-width">
                <div class="section-header"><h3>🛡️ 安全审计 (Security & Compliance)</h3></div>
                <p class="section-desc">配置系统安全底座与物理审计策略。</p>
                
                <div class="settings-grid">
                    ${renderSettingsItem('API 访问令牌 (Token)', 'system.api_token', sys.api_token || '', 'password', {placeholder: '保持为空则不启用认证'})}
                    ${renderSettingsItem('日志输出级别', 'system.log_level', sys.log_level || 'INFO', 'select', {
                        items: [
                            {value: 'DEBUG', text: 'DEBUG (全量输出)'},
                            {value: 'INFO', text: 'INFO (常规运行)'},
                            {value: 'WARNING', text: 'WARNING (仅告警)'},
                            {value: 'ERROR', text: 'ERROR (仅异常)'}
                        ]
                    })}
                    ${renderSettingsItem('启用资产安全审计', 'system.enable_asset_audit', sys.enable_asset_audit ?? true, 'checkbox')}
                    ${renderSettingsItem('资源负载红线 (%)', 'governance.resource_guard.cpu_threshold', rg.cpu_threshold, 'number')}
                </div>

                <div id="config-audit-topology-container" class="mt-large"></div>
            </div>
        `;
    }

    // 挂载到全局 window 域，确保主控制中心能调用
    window.renderGeneralCategory = renderGeneralCategory;
    window.renderSecurityCategory = renderSecurityCategory;
})();
