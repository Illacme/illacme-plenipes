/**
 * 🎨 [V57.4] Illacme Plenipes System Settings Render Component
 * 职责：系统设置中的“常规配置”与“安全审计”选项卡 DOM 的渲染。
 * 对应重构拆分协议：SOP-02/SOP-05 模板一合规物理平移。
 */

(function() {
    // 3. 基础信息渲染
    function renderGeneralCategory() {
        const data = window.settingsData;

        const generalSubDescs = {
            identity: '💡 配置全站品牌展示名称、副标题描述、全局 LOGO 与浏览器 Favicon 图标。',
            compliance: '💡 配置主站点线上网址、默认作者署名与出版知识产权许可协议。',
            storage: '💡 管理本地笔记文库路径、编辑器语法解析协议与跨版图段落缓存淘汰策略。',
            engine: '💡 查看系统底座版本，配置日志输出级别、全局代理、网络超时与遥测采集容量上限。'
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

                if (typeof window.updateSaveButtonVisibility === 'function') {
                    window.updateSaveButtonVisibility(subTab);
                }
            };
        }

        const activeSub = window.currentActiveGeneralSubTab || 'identity';

        return `
            <div class="full-width">
                <div class="section-header"><h3>⚙️ 基础运维 (General Configuration & Operations)</h3></div>
                <p class="section-desc">管理您的站点品牌标识、出版合规声明、缓存存储策略与 Markdown 编译引擎基座。</p>
                
                <div class="security-sub-tab-bar" id="general-sub-tab-bar">
                    <button type="button" class="sub-tab-btn ${activeSub === 'identity' ? 'active' : ''}" onclick="window.switchGeneralSubTab('identity', this)">🏷️ 身份标识</button>
                    <button type="button" class="sub-tab-btn ${activeSub === 'compliance' ? 'active' : ''}" onclick="window.switchGeneralSubTab('compliance', this)">📖 出版合规</button>
                    <button type="button" class="sub-tab-btn ${activeSub === 'storage' ? 'active' : ''}" onclick="window.switchGeneralSubTab('storage', this)">📂 存储缓存</button>
                    <button type="button" class="sub-tab-btn ${activeSub === 'engine' ? 'active' : ''}" onclick="window.switchGeneralSubTab('engine', this)">⚙️ 系统基座</button>
                </div>
                <div id="gen-sub-tab-desc" style="font-size: 0.78rem; color: var(--accent-secondary, #00f2fe); margin-bottom: 18px; line-height: 1.4; opacity: 0.9;">
                    ${generalSubDescs[activeSub] || ''}
                </div>

                <div id="gen-panel-identity" style="display: ${activeSub === 'identity' ? 'block' : 'none'};">
                    <div class="settings-group">
                        <div class="settings-grid">
                            ${renderSettingsItem('版图展示名称', 'imprint_name', data.imprint_name || '', 'text', {
                                description: '您的品牌/期刊显示名称（如：极客技术周刊、产品设计随笔）。'
                            })}
                            ${renderSettingsItem('版图描述', 'imprint_description', data.imprint_description || '', 'text', {
                                description: '品牌核心定位一句话介绍，将在主页与面板中展示。'
                            })}
                            ${renderSettingsItem('全局站点名称', 'site_name', data.site_name || '', 'text', {
                                placeholder: '未填则自愈 fallback 为版图展示名称',
                                description: '部署到线上网站的页面主标题。若留空则自动跟随品牌名称。'
                            })}
                            ${renderSettingsItem('全局站点描述', 'site_description', data.site_description || '', 'text', {
                                placeholder: '未填则自愈 fallback 为版图描述',
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
                        </div>
                    </div>
                </div>

                <div id="gen-panel-storage" style="display: ${activeSub === 'storage' ? 'block' : 'none'};">
                    <div class="settings-group">
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
                                    <button type="button" class="danger-btn" onclick="event.preventDefault(); event.stopPropagation(); window.clearBlockCacheAll()" style="padding: 6px 14px; font-size: 0.75rem; height: 32px; line-height: 14px;">🗑️ 清空所有缓存</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div id="gen-panel-engine" style="display: ${activeSub === 'engine' ? 'block' : 'none'};">
                    <div class="settings-group">
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
                            ${renderSettingsItem('Markdown 换行渲染模式', 'ingress_settings.hard_line_break', data.ingress_settings?.hard_line_break ?? false, 'select', {
                                items: [
                                    {value: false, text: '📄 标准模式 — 单个换行符保留为段落流，需空行真正换行 (CommonMark 标准)'},
                                    {value: true,  text: '✍️ 直觉模式 — 单个换行符直接渲染为新行，所见即所得，推荐日常写作使用 (GFM 兼容)'}
                                ],
                                onchange: `window.updateConfigField('ingress_settings.hard_line_break', this.value === 'true')`,
                                description: '控制原稿文库编辑器预览区和译文校对工作台中的换行渲染方式。<br>· <b>标准模式</b>：Markdown 原生行为，段落内换行不生效，需空行分段；适合有 Markdown 经验的专业用户。<br>· <b>直觉模式</b>：按 Enter 即换行，预览效果与编辑区完全对齐；适合从其他编辑器迁移或习惯"所见即所得"的用户。<br><span style="color: var(--text-dim); font-size: 0.8em;">⚠️ 修改后需保存配置，刷新页面后生效。</span>'
                            })}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // 4. 安全审计渲染
    function renderSecurityCategory() {
        const sys = window.settingsData?.system || {};
        const gov = window.settingsData?.governance || {};
        const rg = gov.resource_guard || { cpu_threshold: 85, compute_ram_threshold: 50.0 };
        
        setTimeout(() => {
            if (typeof window.loadAndRenderConfigAudit === 'function') {
                window.loadAndRenderConfigAudit();
            }
            if (typeof window.loadAndRenderOperationAuditLogs === 'function') {
                window.loadAndRenderOperationAuditLogs();
            }
            if (typeof window.loadAndRenderAiLessonsVisualizer === 'function') {
                window.loadAndRenderAiLessonsVisualizer();
            }
        }, 50);

        const secSubDescs = {
            policy: '💡 配置后端 API 验证令牌、全站访问日志开关、CPU 警戒红线与本地大模型内存削峰控制。',
            topology: '💡 可视化展示全局主主权配置、品牌版图覆盖与环境变量的层级继承树结构。',
            logs: '💡 实时查阅后端守护进程与控制中心的关键操作与变更安全审计日志。',
            lessons: '💡 查阅 AI 引擎自动修正格式异常与超链接失效的历史自愈教训库。'
        };

        if (!window.switchSecuritySubTab) {
            window.switchSecuritySubTab = (subTab, btn) => {
                const container = document.getElementById('security-sub-tab-bar');
                if (container) {
                    const btns = container.querySelectorAll('.sub-tab-btn');
                    btns.forEach(b => b.classList.remove('active'));
                }
                if (btn) {
                    btn.classList.add('active');
                } else if (event) {
                    event.currentTarget.classList.add('active');
                }

                const panels = ['policy', 'topology', 'logs', 'lessons'];
                panels.forEach(p => {
                    const el = document.getElementById(`sec-panel-${p}`);
                    if (el) el.style.display = (p === subTab) ? 'block' : 'none';
                });

                const descEl = document.getElementById('sec-sub-tab-desc');
                if (descEl) descEl.innerHTML = secSubDescs[subTab] || '';

                if (typeof window.updateSaveButtonVisibility === 'function') {
                    window.updateSaveButtonVisibility(subTab);
                }
            };
        }

        return `
            <style>
                .security-sub-tab-bar {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 20px;
                    border-bottom: 1px solid rgba(255,255,255,0.08);
                    padding-bottom: 10px;
                    flex-wrap: wrap;
                }
                .sub-tab-btn {
                    background: var(--white-03, rgba(255,255,255,0.03));
                    border: 1px solid var(--white-08, rgba(255,255,255,0.08));
                    color: var(--text-dim, #888);
                    padding: 6px 14px;
                    border-radius: 4px;
                    font-size: 0.8rem;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    outline: none;
                }
                .sub-tab-btn:hover {
                    background: var(--white-08, rgba(255,255,255,0.08));
                    color: var(--text-bright, #fff);
                }
                .sub-tab-btn.active {
                    background: rgba(var(--accent-secondary-rgb, 0, 242, 255), 0.1);
                    border-color: rgba(var(--accent-secondary-rgb, 0, 242, 255), 0.3);
                    color: var(--accent-secondary, #00f2ff);
                    box-shadow: 0 0 8px rgba(var(--accent-secondary-rgb, 0, 242, 255), 0.15);
                }
            </style>

            <div class="full-width">
                <div class="section-header"><h3>🛡️ 安全审计 (Security Audit & Governance)</h3></div>
                <p class="section-desc">查看系统安全访问策略、主权配置继承关系、守护进程操作账本与 AI 自愈教训。</p>
                
                <div class="security-sub-tab-bar" id="security-sub-tab-bar">
                    <button type="button" class="sub-tab-btn active" onclick="window.switchSecuritySubTab('policy', this)">🛡️ 安全策略</button>
                    <button type="button" class="sub-tab-btn" onclick="window.switchSecuritySubTab('topology', this)">🗺️ 配置继承</button>
                    <button type="button" class="sub-tab-btn" onclick="window.switchSecuritySubTab('logs', this)">📜 操作账本</button>
                    <button type="button" class="sub-tab-btn" onclick="window.switchSecuritySubTab('lessons', this)">🧠 教训自愈</button>
                </div>
                <div id="sec-sub-tab-desc" style="font-size: 0.78rem; color: var(--accent-secondary, #00f2fe); margin-bottom: 18px; line-height: 1.4; opacity: 0.9;">
                    ${secSubDescs['policy']}
                </div>

                <div id="sec-panel-policy">
                    <div class="settings-grid">
                        ${renderSettingsItem('API 访问令牌 (Token)', 'system.api_token', sys.api_token || '', 'password', {
                            placeholder: '保持为空则不启用认证',
                            description: '后端 Web API 网关身份校验 Token，保持留空表示无密码访问。'
                        })}
                        ${renderSettingsItem('日志输出级别', 'system.log_level', sys.log_level || 'INFO', 'select', {
                            items: [
                                {value: 'DEBUG', text: 'DEBUG (全量输出)'},
                                {value: 'INFO', text: 'INFO (常规运行)'},
                                {value: 'WARNING', text: 'WARNING (仅告警)'},
                                {value: 'ERROR', text: 'ERROR (仅异常)'}
                            ],
                            description: '控制服务器后端在终端与日志文件中输出的详细程度。'
                        })}
                        ${renderSettingsItem('启用资产安全审计', 'system.enable_asset_audit', sys.enable_asset_audit ?? true, 'checkbox', {
                            description: '开启后，系统在编译原稿时会自动审计和监控静态资产与外部链接的合法性。'
                        })}
                        ${renderSettingsItem('资源负载红线 (%)', 'governance.resource_guard.cpu_threshold', rg.cpu_threshold ?? 85, 'number', {
                            description: 'CPU 负载警戒红线（%）。当宿主机 CPU 占用率持续高于此阈值时，自动平滑降低并发算力。'
                        })}
                        ${renderSettingsItem('本地算力内存削峰警戒线 (%)', 'governance.resource_guard.compute_ram_threshold', rg.compute_ram_threshold ?? 50.0, 'number', {
                            description: '当本地大模型（如 Ollama / LM Studio 等）常驻物理内存占用宿主机总内存比例超过此阈值时，自动降低 AI 并发以防宿主崩溃。'
                        })}
                    </div>
                </div>

                <div id="sec-panel-topology" style="display: none;">
                    <div id="config-audit-topology-container"></div>
                </div>

                <div id="sec-panel-logs" style="display: none;">
                    <div id="operation-audit-logs-container"></div>
                </div>

                <div id="sec-panel-lessons" style="display: none;">
                    <div id="ai-lessons-visualizer-container"></div>
                </div>
            </div>
        `;
    }

    // 挂载到全局 window 域，确保主控制中心能调用
    window.renderGeneralCategory = renderGeneralCategory;
    window.renderSecurityCategory = renderSecurityCategory;
})();
