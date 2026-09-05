/**
 * 🎨 [V57.4] Illacme Plenipes System Settings Render Component
 * 职责：系统设置中的“常规配置”与“安全审计”选项卡 DOM 的渲染。
 * 对应重构拆分协议：SOP-02/SOP-05 模板一合规物理平移。
 */

(function() {
    // 3. 基础信息渲染
    function renderGeneralCategory() {
        const data = window.settingsData || {};
        const renderSettingsItem = window.renderSettingsItem || (() => '');

        const generalSubDescs = {
            identity: '💡 配置全站品牌展示名称、副标题描述、全局 LOGO 与浏览器 Favicon 图标。',
            compliance: '💡 配置主站点线上网址、默认作者署名与出版知识产权许可协议。',
            storage: '💡 管理本地文库路径、Markdown 语法解析协议与段落缓存淘汰策略。',
            engine: '💡 配置首页工作台自启、系统运行日志级别、全局代理、网络超时与遥测采集容量上限。'
        };

        if (!window.switchGeneralSubTab) {
            window.switchGeneralSubTab = (subTab, btn) => {
                window.currentActiveGeneralSubTab = subTab;
                const container = document.getElementById('general-sub-tab-bar');
                if (container) {
                    const btns = container.querySelectorAll('.sub-tab-btn');
                    btns.forEach(b => b.classList.remove('active'));
                }
                if (btn) {
                    btn.classList.add('active');
                } else if (event) {
                    event.currentTarget.classList.add('active');
                }

                const panels = ['identity', 'compliance', 'storage', 'engine'];
                panels.forEach(p => {
                    const el = document.getElementById(`gen-panel-${p}`);
                    if (el) el.style.display = (p === subTab) ? 'block' : 'none';
                });

                const descEl = document.getElementById('gen-sub-tab-desc');
                if (descEl) descEl.innerHTML = generalSubDescs[subTab] || '';

                if (subTab === 'storage' && typeof window.refreshCacheStats === 'function') {
                    window.refreshCacheStats();
                }

                if (typeof window.updateSaveButtonVisibility === 'function') {
                    window.updateSaveButtonVisibility(subTab);
                }
            };
        }

        const activeSub = window.currentActiveGeneralSubTab || 'identity';
        if (activeSub === 'storage' && typeof window.refreshCacheStats === 'function') {
            setTimeout(() => { window.refreshCacheStats(); }, 50);
        }

        return `
            <div class="category-header-banner" style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px; padding: 18px 22px; background: rgba(0, 242, 255, 0.03); border: 1px solid var(--glass-border); border-radius: 12px; backdrop-filter: blur(10px);">
                <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <h2 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: var(--text-main); letter-spacing: 0.5px;">⚙️ 基础配置与运维</h2>
                    </div>
                </div>

                <div class="sub-tab-navigation-bar" id="general-sub-tab-bar" style="display: flex; gap: 8px; margin-top: 10px; border-bottom: 1px solid var(--glass-border); padding-bottom: 10px;">
                    <button type="button" class="sub-tab-btn ${activeSub === 'identity' ? 'active' : ''}" onclick="window.switchGeneralSubTab('identity', this)" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">📛 身份标识</button>
                    <button type="button" class="sub-tab-btn ${activeSub === 'compliance' ? 'active' : ''}" onclick="window.switchGeneralSubTab('compliance', this)" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">⚖️ 出版合规</button>
                    <button type="button" class="sub-tab-btn ${activeSub === 'storage' ? 'active' : ''}" onclick="window.switchGeneralSubTab('storage', this)" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">📂 存储适配</button>
                    <button type="button" class="sub-tab-btn ${activeSub === 'engine' ? 'active' : ''}" onclick="window.switchGeneralSubTab('engine', this)" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">⚙️ 运行基座</button>
                </div>

                <div id="gen-sub-tab-desc" style="font-size: 0.82rem; color: var(--text-muted); margin-top: 4px;">
                    ${generalSubDescs[activeSub] || ''}
                </div>
            </div>

                <div id="gen-panel-identity" style="display: ${activeSub === 'identity' ? 'block' : 'none'};">
                    <div class="settings-group">
                        <div class="settings-grid">
                            ${renderSettingsItem('品牌展示名称', 'imprint_name', data.imprint_name || '', 'text', {
                                description: '您的品牌/期刊显示名称（如：极客技术周刊、产品设计随笔）。'
                            })}
                            ${renderSettingsItem('品牌描述', 'imprint_description', data.imprint_description || '', 'text', {
                                description: '品牌核心定位一句话介绍，将在主页与面板中展示。'
                            })}
                            ${renderSettingsItem('全局站点名称', 'site_name', data.site_name || '', 'text', {
                                placeholder: '未填则自愈 fallback 为品牌展示名称',
                                description: '部署到线上网站的页面主标题。若留空则自动跟随品牌名称。'
                            })}
                            ${renderSettingsItem('全局站点描述', 'site_description', data.site_description || '', 'text', {
                                placeholder: '未填则自愈 fallback 为品牌描述',
                                description: '主站点的全局摘要，用于首页 Subtitle 与搜索引擎 SEO 检索描述。'
                            })}
                            ${renderSettingsItem('全局品牌 Logo 路径', 'logo_path', data.logo_path || '', 'text', {
                                placeholder: '例如: /static/logo.png',
                                description: '全站 Header 展示的品牌 LOGO 图标相对路径。'
                            })}
                            ${renderSettingsItem('全局 Favicon 图标路径', 'favicon_path', data.favicon_path || '', 'text', {
                                placeholder: '例如: /static/favicon.ico',
                                description: '浏览器标签页上显示的网站小图标 (Favicon) 路径。'
                            })}
                        </div>
                    </div>
                </div>

                <div id="gen-panel-compliance" style="display: ${activeSub === 'compliance' ? 'block' : 'none'};">
                    <div class="settings-group">
                        <div class="settings-grid">
                            ${renderSettingsItem('主站点 URL', 'site_url', data.site_url || '', 'text', {
                                description: '主站点的真实线上访问网址（如 https://blog.example.com），用于生成规范 Canonical URL。'
                            })}
                            ${renderSettingsItem('默认作者署名', 'frontmatter_defaults.author', data.frontmatter_defaults?.author || '', 'text', {
                                description: '出版物文章的默认作者署名。如原稿 Frontmatter 未指定作者，将自动使用此项。'
                            })}
                            ${renderSettingsItem('全域版权声明', 'frontmatter_defaults.copyright', data.frontmatter_defaults?.copyright || '© 2024 All Rights Reserved', 'text', {
                                description: '全站页脚及各文章底部默认附带的版权归属声明。'
                            })}
                            ${renderSettingsItem('出版许可证 (License)', 'frontmatter_defaults.license', data.frontmatter_defaults?.license || 'CC BY-NC-SA 4.0', 'text', {
                                description: '内容出版知识产权许可证（如 CC BY-NC-SA 4.0 署名-非商业性使用-相同方式共享）。'
                            })}
                            ${renderSettingsItem('工信部 ICP 备案号', 'frontmatter_defaults.icp_license', data.frontmatter_defaults?.icp_license || '', 'text', {
                                placeholder: '如：京ICP备12345678号-1',
                                description: '工信部域名信息备案号。配置后将在全站页脚显示并自动挂载工信部备案系统 (beian.miit.gov.cn) 官方直链。'
                            })}
                            ${renderSettingsItem('全国公安网安备号', 'frontmatter_defaults.police_license', data.frontmatter_defaults?.police_license || '', 'text', {
                                placeholder: '如：京公网安备 11010802020110号',
                                description: '全国公安机关互联网站安全管理服务平台备案号。配置后将在页脚自动佩戴警徽徽章与直链。'
                            })}
                        </div>
                    </div>
                </div>

                <div id="gen-panel-storage" style="display: ${activeSub === 'storage' ? 'block' : 'none'};">
                    <div class="settings-group">
                        <div class="settings-grid">
                            ${renderSettingsItem('原稿文库路径', 'vault_root', data.vault_root || '', 'static', {
                                description: '🔒 物理主权路径在品牌确立后不可变。如需迁移资产领土，请新建品牌。'
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
                            ${renderSettingsItem('Markdown 换行渲染模式', 'ingress_settings.hard_line_break', data.ingress_settings?.hard_line_break ?? false, 'select', {
                                items: [
                                    {value: false, text: '📄 标准模式 — 单个换行符保留为段落流，需空行真正换行 (CommonMark 标准)'},
                                    {value: true,  text: '✍️ 直觉模式 — 单个换行符直接渲染为新行，所见即所得，推荐日常写作使用 (GFM 兼容)'}
                                ],
                                onchange: `window.updateConfigField('ingress_settings.hard_line_break', this.value === 'true')`,
                                description: '控制原稿文库编辑器预览区和译文校对工作台中的换行渲染方式。<br>· <b>标准模式</b>：Markdown 原生行为，段落内换行不生效，需空行分段；适合有 Markdown 经验的专业用户。<br>· <b>直觉模式</b>：按 Enter 即换行，预览效果与编辑区完全对齐；适合从其他编辑器迁移或习惯"所见即所得"的用户。<br><span style="color: var(--text-dim); font-size: 0.8em;">⚠️ 修改后需保存配置，刷新页面后生效。</span>'
                            })}
                            ${renderSettingsItem('段落缓存存储目录', 'block_cache_dir', data.block_cache_dir || '', 'text', {
                                placeholder: '默认为空（自愈退避至项目根目录下的隐藏目录 .plenipes/blocks/）',
                                description: '跨品牌共享段落缓存物理存储根目录。支持自定义重定向以实现在任意品牌和任意 SSG 主题之间共用。'
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
                            
                            <!-- 🚚 物理分级迁移内嵌快捷操作条 -->
                            <div style="margin-top: -10px; margin-bottom: 20px; padding: 12px 16px; background: rgba(0, 242, 255, 0.03); border: 1px solid rgba(0, 242, 255, 0.12); border-radius: 8px; display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap;">
                                <div style="display: flex; align-items: center; gap: 10px; flex: 1; min-width: 260px;">
                                    <span style="font-size: 1.2rem;">🚚</span>
                                    <span style="font-size: 0.8rem; opacity: 0.85; line-height: 1.4;">修改上述【目录分级】参数后，可点击右侧按钮将磁盘现有段落缓存一键安全迁移至新分级路径：</span>
                                </div>
                                <button type="button" class="primary-btn glow-btn" onclick="window.manualMigrateCache()" style="padding: 6px 14px; font-size: 0.78rem; height: 32px; white-space: nowrap; word-break: keep-all;">🚚 物理分级迁移</button>
                            </div>

                            ${renderSettingsItem('算力缓存自动回收', 'enable_cache_eviction', data.enable_cache_eviction ?? false, 'select', {
                                items: [
                                    {value: false, text: '❌ 禁用 — 算力缓存永久保留，不主动回收（适合本地磁盘空间充裕环境）'},
                                    {value: true,  text: '🟢 启用 — 引擎定时清理过期与超出容量上限的段落缓存（推荐，保持磁盘轻量）'}
                                ],
                                onchange: `window.updateConfigField('enable_cache_eviction', this.value === 'true')`,
                                description: '控制是否启用段落缓存的过期及 LRU 淘汰机制。启用后将在大扫除（Janitor）时进行自动净化。'
                            })}
                            ${renderSettingsItem('缓存保留天数 (Retention Days)', 'cache_eviction_days', data.cache_eviction_days ?? 30, 'number', {
                                onchange: `window.updateConfigField('cache_eviction_days', parseInt(this.value))`,
                                placeholder: '默认 30 天',
                                description: '设定缓存文件的有效期。超过该天数未被修改/访问的段落缓存将被自动物理抹除。'
                            })}
                            ${renderSettingsItem('缓存容量上限 (Max Cache Size)', 'cache_max_size_mb', data.cache_max_size_mb ?? 512, 'number', {
                                onchange: `window.updateConfigField('cache_max_size_mb', parseInt(this.value))`,
                                placeholder: '默认 512 MB',
                                description: '当全部缓存文件大小之和超出此上限（MB）时，将根据修改时间（LRU）由旧到新依次自动进行淘汰清理。'
                            })}
                        </div>
                    </div>

                    <div class="settings-group mt-large">
                        <h4>🧰 分层缓存与双轨容灾治理中枢 (Granular Cache Hub)</h4>
                        <p class="section-desc" style="font-size: 0.85rem; opacity: 0.85; margin-bottom: 16px;">细粒度独立管理大模型算力资产、文件指纹账本与构建产物缓存，支持 0 算力开销全量重编与物理冷备自愈。</p>
                        
                        <!-- 📊 状态盘点面板 -->
                        <div style="background: rgba(0, 242, 255, 0.03); border: 1px solid var(--glass-border, rgba(255,255,255,0.08)); padding: 16px 20px; border-radius: 10px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-wrap: wrap;">
                            <div style="display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <div style="font-size: 1.3rem;">🧱</div>
                                    <div>
                                        <div style="font-size: 0.75rem; opacity: 0.75;">段落翻译缓存</div>
                                        <div style="display: flex; gap: 8px; align-items: center;">
                                            <span style="font-size: 0.95rem; font-weight: bold; color: var(--accent-primary, #00f2ff);" id="cache-stats-count">正在统计...</span>
                                            <span style="opacity: 0.3;">/</span>
                                            <span style="font-size: 0.95rem; font-weight: bold; color: #00ff88;" id="cache-stats-size">正在统计...</span>
                                        </div>
                                    </div>
                                </div>
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <div style="font-size: 1.3rem;">📂</div>
                                    <div>
                                        <div style="font-size: 0.75rem; opacity: 0.75;">物理元信息镜像</div>
                                        <span style="font-size: 0.95rem; font-weight: bold; color: #ffb800;" id="cache-stats-meta-count">正在统计...</span>
                                    </div>
                                </div>
                                <div style="display: flex; align-items: center; gap: 10px;">
                                    <div style="font-size: 1.3rem;">⚡</div>
                                    <div>
                                        <div style="font-size: 0.75rem; opacity: 0.75;">构建与镜像产物</div>
                                        <span style="font-size: 0.95rem; font-weight: bold; color: #a371f7;" id="cache-stats-build-size">正在统计...</span>
                                    </div>
                                </div>
                            </div>
                            <button type="button" class="sub-tab-btn" onclick="window.refreshCacheStats()" style="padding: 6px 14px; font-size: 0.75rem; white-space: nowrap; word-break: keep-all;">🔄 重新盘点</button>
                        </div>

                        <!-- 🛠️ 分层功能操作网格 (2列 x 3排 黄金比例布局) -->
                        <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px;">
                            <!-- 第一排-左：0 算力开销仅重置指纹 -->
                            <div style="background: rgba(0, 242, 255, 0.03); border: 1px solid rgba(0, 242, 255, 0.22); padding: 14px; border-radius: 10px; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; box-shadow: 0 4px 16px rgba(0, 242, 255, 0.04);">
                                <div>
                                    <div style="display: flex; align-items: center; justify-content: space-between; gap: 6px; margin-bottom: 8px;">
                                        <span style="font-size: 0.86rem; font-weight: 600; color: #00f2ff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 5px;">⚡ 仅重置增量指纹</span>
                                        <span class="badge" style="font-size: 0.65rem; background: rgba(0,242,255,0.12); color: #00f2ff; border: 1px solid rgba(0,242,255,0.3); padding: 1px 6px; border-radius: 4px; white-space: nowrap; flex-shrink: 0; font-weight: 500;">0 算力开销</span>
                                    </div>
                                    <p style="font-size: 0.77rem; opacity: 0.85; line-height: 1.4; margin: 0; color: var(--text-bright, #e0e6ed);">清空文件指纹解除跳过限制。<b>正文译文、AI别名/SEO及拓扑元数据完整保留</b>，下次发布 0 算力全速重新组装。</p>
                                </div>
                                <button type="button" class="primary-btn glow-btn" onclick="event.preventDefault(); event.stopPropagation(); window.resetFingerprintsOnly()" style="padding: 6px 12px; font-size: 0.78rem; height: 32px; width: 100%; justify-content: center; font-weight: 500;">⚡ 仅重置指纹</button>
                            </div>

                            <!-- 第一排-右：物理快照自愈重建账本 -->
                            <div style="background: rgba(0, 255, 136, 0.025); border: 1px solid rgba(0, 255, 136, 0.22); padding: 14px; border-radius: 10px; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; box-shadow: 0 4px 16px rgba(0, 255, 136, 0.04);">
                                <div>
                                    <div style="display: flex; align-items: center; justify-content: space-between; gap: 6px; margin-bottom: 8px;">
                                        <span style="font-size: 0.86rem; font-weight: 600; color: #00ff88; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 5px;">🩹 物理快照自愈</span>
                                        <span class="badge" style="font-size: 0.65rem; background: rgba(0,255,136,0.12); color: #00ff88; border: 1px solid rgba(0,255,136,0.3); padding: 1px 6px; border-radius: 4px; white-space: nowrap; flex-shrink: 0; font-weight: 500;">冷备自愈</span>
                                    </div>
                                    <p style="font-size: 0.77rem; opacity: 0.85; line-height: 1.4; margin: 0; color: var(--text-bright, #e0e6ed);">从本地 <code>cache/metadata/</code> 镜像无损恢复 SQLite 账本。<b>0 算力开销</b>，秒级还原历史沉淀的全部元数据。</p>
                                </div>
                                <button type="button" class="sub-tab-btn" onclick="event.preventDefault(); event.stopPropagation(); window.rebuildLedgerFromCache()" style="padding: 6px 12px; font-size: 0.78rem; height: 32px; width: 100%; justify-content: center; border-color: rgba(0,255,136,0.4); color: #00ff88; font-weight: 500;">🩹 自愈重建账本</button>
                            </div>

                            <!-- 第二排-左：清空段落翻译缓存 -->
                            <div style="background: rgba(255, 184, 0, 0.025); border: 1px solid rgba(255, 184, 0, 0.22); padding: 14px; border-radius: 10px; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; box-shadow: 0 4px 16px rgba(255, 184, 0, 0.04);">
                                <div>
                                    <div style="display: flex; align-items: center; justify-content: space-between; gap: 6px; margin-bottom: 8px;">
                                        <span style="font-size: 0.86rem; font-weight: 600; color: #ffb800; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 5px;">🧱 清空段落翻译</span>
                                        <span class="badge" style="font-size: 0.65rem; background: rgba(255,184,0,0.12); color: #ffb800; border: 1px solid rgba(255,184,0,0.3); padding: 1px 6px; border-radius: 4px; white-space: nowrap; flex-shrink: 0; font-weight: 500;">正文重译</span>
                                    </div>
                                    <p style="font-size: 0.77rem; opacity: 0.85; line-height: 1.4; margin: 0; color: var(--text-bright, #e0e6ed);">物理清空 <code>cache/blocks/</code> 文本库。<b>下次发布时各段落将重新调用大模型翻译</b>（耗费 Token 与时间）。</p>
                                </div>
                                <button type="button" class="danger-btn" onclick="event.preventDefault(); event.stopPropagation(); window.clearBlockCacheAll()" style="padding: 6px 12px; font-size: 0.78rem; height: 32px; width: 100%; justify-content: center; font-weight: 500;">🧱 清空段落缓存</button>
                            </div>

                            <!-- 第二排-右：重置 AI 元数据缓存 -->
                            <div style="background: rgba(163, 113, 247, 0.025); border: 1px solid rgba(163, 113, 247, 0.22); padding: 14px; border-radius: 10px; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; box-shadow: 0 4px 16px rgba(163, 113, 247, 0.04);">
                                <div>
                                    <div style="display: flex; align-items: center; justify-content: space-between; gap: 6px; margin-bottom: 8px;">
                                        <span style="font-size: 0.86rem; font-weight: 600; color: #a371f7; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 5px;">🏷️ 重置 AI 元数据</span>
                                        <span class="badge" style="font-size: 0.65rem; background: rgba(163,113,247,0.12); color: #a371f7; border: 1px solid rgba(163,113,247,0.3); padding: 1px 6px; border-radius: 4px; white-space: nowrap; flex-shrink: 0; font-weight: 500;">元数据重塑</span>
                                    </div>
                                    <p style="font-size: 0.77rem; opacity: 0.85; line-height: 1.4; margin: 0; color: var(--text-bright, #e0e6ed);">仅清空 AI 衍生的网址别名与 SEO 摘要。<b>正文段落译文完好保留</b>，下次发布仅重新推导这些元数据。</p>
                                </div>
                                <button type="button" class="sub-tab-btn" onclick="event.preventDefault(); event.stopPropagation(); window.clearAIMetadataCache()" style="padding: 6px 12px; font-size: 0.78rem; height: 32px; width: 100%; justify-content: center; border-color: rgba(163,113,247,0.4); color: #a371f7; font-weight: 500;">🏷️ 重置 AI 元数据</button>
                            </div>

                            <!-- 第三排-左：清理构建与源码镜像缓存 -->
                            <div style="background: rgba(136, 164, 230, 0.025); border: 1px solid rgba(136, 164, 230, 0.22); padding: 14px; border-radius: 10px; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; box-shadow: 0 4px 16px rgba(136, 164, 230, 0.04);">
                                <div>
                                    <div style="display: flex; align-items: center; justify-content: space-between; gap: 6px; margin-bottom: 8px;">
                                        <span style="font-size: 0.86rem; font-weight: 600; color: #88a4e6; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 5px;">🧹 清理构建产物</span>
                                        <span class="badge" style="font-size: 0.65rem; background: rgba(136,164,230,0.12); color: #88a4e6; border: 1px solid rgba(136,164,230,0.3); padding: 1px 6px; border-radius: 4px; white-space: nowrap; flex-shrink: 0; font-weight: 500;">构建排障</span>
                                    </div>
                                    <p style="font-size: 0.77rem; opacity: 0.85; line-height: 1.4; margin: 0; color: var(--text-bright, #e0e6ed);">清理 <code>cache/sources/</code> 与 <code>build/</code> 遗留编译产物。<b>不影响任何 AI 译文、元数据或指纹账本</b>。</p>
                                </div>
                                <button type="button" class="sub-tab-btn" onclick="event.preventDefault(); event.stopPropagation(); window.clearBuildCache()" style="padding: 6px 12px; font-size: 0.78rem; height: 32px; width: 100%; justify-content: center; border-color: rgba(136,164,230,0.4); color: #88a4e6; font-weight: 500;">🧹 清理构建产物</button>
                            </div>

                            <!-- 第三排-右：全量归零重置 -->
                            <div style="background: rgba(255, 77, 77, 0.025); border: 1px solid rgba(255, 77, 77, 0.22); padding: 14px; border-radius: 10px; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; box-shadow: 0 4px 16px rgba(255, 77, 77, 0.04);">
                                <div>
                                    <div style="display: flex; align-items: center; justify-content: space-between; gap: 6px; margin-bottom: 8px;">
                                        <span style="font-size: 0.86rem; font-weight: 600; color: #ff4d4d; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 5px;">💣 彻底清空账本</span>
                                        <span class="badge" style="font-size: 0.65rem; background: rgba(255,77,77,0.12); color: #ff4d4d; border: 1px solid rgba(255,77,77,0.3); padding: 1px 6px; border-radius: 4px; white-space: nowrap; flex-shrink: 0; font-weight: 500;">账本归零</span>
                                    </div>
                                    <p style="font-size: 0.77rem; opacity: 0.85; line-height: 1.4; margin: 0; color: var(--text-bright, #e0e6ed);">清空 SQLite 账本与元信息镜像。<b>段落翻译缓存（Block Cache）与原稿文件完好保留</b>，但元数据需重新扫描建立。</p>
                                </div>
                                <button type="button" class="danger-btn" onclick="event.preventDefault(); event.stopPropagation(); window.resetLedgerOnly()" style="padding: 6px 12px; font-size: 0.78rem; height: 32px; width: 100%; justify-content: center; font-weight: 500;">💣 清空文档账本</button>
                            </div>
                        </div>
                    </div>



                </div>

                <div id="gen-panel-engine" style="display: ${activeSub === 'engine' ? 'block' : 'none'};">
                    <div class="settings-group">
                        <div class="settings-grid">
                            ${renderSettingsItem('首页工作台自动展开', 'ui.launchpad_auto_open', (typeof window.shouldAutoOpenLaunchpad === 'function' ? window.shouldAutoOpenLaunchpad() : true), 'checkbox', {
                                onchange: `window.setLaunchpadAutoOpenPreference(this.checked); if(typeof window.addAudit==='function') window.addAudit('🚀 首页工作台自启偏好已更新为: ' + (this.checked ? '开启' : '关闭'), 'info');`,
                                description: '控制进入管理后台首页（概览）时是否自动展开全屏出版工作台（Launchpad）。关闭后进入首页将直接展示 3D 知识星系宇宙，随时可按键盘快捷键 I 或点击顶部 Logo 呼出。',
                                effectiveness: 'live'
                            }, 'local')}
                            ${renderSettingsItem('系统日志级别', 'system.log_level', data.system?.log_level || 'INFO', 'select', {
                                items: [
                                    {value: 'DEBUG', text: 'DEBUG (全量输出)'},
                                    {value: 'INFO', text: 'INFO (常规运行)'},
                                    {value: 'WARNING', text: 'WARNING (仅告警)'},
                                    {value: 'ERROR', text: 'ERROR (仅异常)'}
                                ],
                                description: '控制服务器后端在终端输出的日志详细程度。建议使用 WARNING 级别以保持静音。'
                            })}
                            ${renderSettingsItem('全局网络代理 (Global Proxy)', 'global_proxy', data.global_proxy || '', 'text', {
                                placeholder: '例如: http://127.0.0.1:10809 (留空表示直连)',
                                description: '全站兜底网络代理地址。若发布渠道未配置独立代理，将自动使用此全局代理。填写 direct 表示强行直连。'
                            })}
                            ${renderSettingsItem('第三方 API 网络请求超时 (Timeout)', 'system.network_timeout', data.system?.network_timeout ?? 15, 'number', {
                                onchange: `window.updateConfigField('system.network_timeout', parseInt(this.value))`,
                                placeholder: '默认 15 秒',
                                min: 1,
                                max: 120,
                                description: '控制系统在连接 GitHub、Dev.to、Vercel 等第三方 API 或测试物理链路时的请求超时上限（秒）。推荐在代理环境或高延迟网络下设置为 15~30 秒。'
                            })}
                            ${renderSettingsItem('启用 HTTP 访问日志', 'system.access_log', data.system?.access_log ?? true, 'checkbox', {
                                description: '是否记录每一次网页 and API 访问（包含心跳请求）。建议关闭以防终端频繁被 stats 心跳刷屏。'
                            })}
                            ${renderSettingsItem('遥测负载历史保存上限', 'system.telemetry_history_limit', data.system?.telemetry_history_limit ?? 150, 'number', {
                                onchange: `window.updateConfigField('system.telemetry_history_limit', parseInt(this.value))`,
                                placeholder: '默认 150 点',
                                min: 10,
                                max: 500,
                                description: '设定控制塔遥测趋势图（系统负载与 AI 吞吐）常驻记录的时序点数上限（每 2 秒采集一个点）。建议在 40 到 300 点之间配置。该项热加载即时生效，无需重启服务。'
                            })}
                            ${renderSettingsItem('遥测长效归档采样间隔', 'system.telemetry_archive_interval_seconds', data.system?.telemetry_archive_interval_seconds ?? 120, 'number', {
                                onchange: `window.updateConfigField('system.telemetry_archive_interval_seconds', parseInt(this.value))`,
                                placeholder: '默认 120 秒',
                                min: 10,
                                description: '设定长效归档负载（12h模式）的物理采样间隔（秒）。每隔此时间，后端会自动对期间所有高频负载数据取平均值，作为一个归档时序点推入长效历史。'
                            })}
                            ${renderSettingsItem('遥测长效归档保存上限', 'system.telemetry_archive_limit', data.system?.telemetry_archive_limit ?? 360, 'number', {
                                onchange: `window.updateConfigField('system.telemetry_archive_limit', parseInt(this.value))`,
                                placeholder: '默认 360 点',
                                min: 10,
                                max: 1000,
                                description: '设定控制塔长效归档时序的最大保留点数。默认 360 点，配合 120 秒采样间隔，可支持保存展示过去 12 小时的完整演进曲线。该项配置热加载即时生效。'
                            })}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    window.renderGeneralCategory = renderGeneralCategory;
})();
