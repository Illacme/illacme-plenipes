/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Pod Card HTML & 3D Physics Shard
 * 职责：能力节点 Pod 卡片 HTML 构造器与 3D 视差微动效。
 */

// 🔒 [SOP-02 物理拆分] 平台品牌徽章、专属图标与分类回退样式字典已抽离至独立分片：
// -> web/dashboard/js/plugins/render_shards/plugins.render.badges.js



window.buildPluginPodHtml = (p, isPinned) => {
    const rawId = (p.id || '').toLowerCase();
    const cleanId = rawId.replace(/_/g, '');
    let portalInfo = window.PLATFORM_PORTAL_LINKS ? (window.PLATFORM_PORTAL_LINKS[rawId] || window.PLATFORM_PORTAL_LINKS[cleanId]) : null;
    if (!portalInfo && window.PLATFORM_PORTAL_LINKS) {
        for (const k in window.PLATFORM_PORTAL_LINKS) {
            if (rawId.includes(k) || k.includes(rawId)) {
                portalInfo = window.PLATFORM_PORTAL_LINKS[k];
                break;
            }
        }
    }
    const homeUrl = portalInfo ? portalInfo.home : (p.homepage || p.home_url || null);
    const brand = window.getPlatformBrandBadge(p.id, p.category);

    const isTheme = p.category === 'theme';
    const isProtocol = p.category === 'protocol';
    const canConfig = window.isPluginConfigurable(p);
    const canTest = ['hosting', 'image_hosting', 'publisher', 'notification', 'ebook', 'tunnel'].includes(p.category) && p.is_manageable;
    const statusBadge = window.checkPluginConfiguredStatus(p);

    // 统计当前驱动在算力中心已划定的单元数与节点 ID 列表
    const computeNodes = window.settingsData?.translation?.compute_nodes || {};
    const matchingNodeIds = Object.entries(computeNodes)
        .filter(([k, n]) => (n && (n.type || '').toLowerCase() === rawId) || (n && (n.provider || '').toLowerCase() === rawId))
        .map(([k]) => k);
    const usedCount = matchingNodeIds.length;

    let controlBtnsHtml = '';
    if (isTheme) {
        const loc = p.location || 'native';
        const isNativeCloud = (loc === 'native' && !p.is_in_use);
        const secondActionBtn = isNativeCloud
            ? `<button class="action-btn glow-btn" style="font-size:0.75rem; border-color: rgba(245, 158, 11, 0.4); color: #ffb700;" onclick="if(window.ThemeHandlers&&window.ThemeHandlers.bootstrapTheme){window.ThemeHandlers.bootstrapTheme('${p.id}');}else{if(typeof addAudit==='function')addAudit('⚡ 正在引导下载主题母本: ${p.id}...');}">⚡ 引导下载</button>`
            : `<button class="action-btn secondary" style="font-size:0.75rem;" onclick="if(window.ThemeHandlers&&window.ThemeHandlers.invokeGlobalAction){window.ThemeHandlers.invokeGlobalAction('install');}else{if(typeof addAudit==='function')addAudit('📡 正在对齐主题静态资产...');}">🏗️ 检查依赖</button>`;

        controlBtnsHtml = `
            <div class="p-control-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:8px;">
                <button class="action-btn" onclick="openPluginConfig('${p.id}', '${p.category}')">⚙️ CONFIG</button>
                ${secondActionBtn}
            </div>
        `;
    } else if (isProtocol) {
        controlBtnsHtml = `
            <div class="p-control-group" style="display:grid; grid-template-columns: 1fr; gap:8px;">
                <button class="action-btn glow-btn" style="font-size:0.78rem; font-weight:700; border-color: rgba(0, 242, 255, 0.4); color: var(--accent-secondary); padding: 8px 12px; display:flex; align-items:center; justify-content:center; gap:6px;" onclick="window.createComputeNodeFromProtocol('${p.id}')">
                    <span>➕ 基于此渠道新增算力单元</span>
                </button>
            </div>
        `;
    } else if (canConfig && canTest) {
        controlBtnsHtml = `
            <div class="p-control-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:8px;">
                <button class="action-btn" onclick="openPluginConfig('${p.id}', '${p.category}')">⚙️ CONFIG</button>
                <button class="action-btn p-btn-test-direct" data-id="${p.id}" data-category="${p.category}" onclick="window.fastTestPluginConnectivity('${p.id}', '${p.category}', this)">⚡ 测试连接</button>
            </div>
        `;
    } else if (canConfig && !canTest) {
        controlBtnsHtml = `
            <div class="p-control-group" style="display:grid; grid-template-columns: 1fr; gap:8px;">
                <button class="action-btn" onclick="openPluginConfig('${p.id}', '${p.category}')">⚙️ CONFIG</button>
            </div>
        `;
    } else if (!canConfig && canTest) {
        if (p.category === 'ebook') {
            controlBtnsHtml = `
                <div class="p-control-group" style="display:grid; grid-template-columns: 1fr 1fr; gap:8px;">
                    <button class="action-btn glow-btn" style="border-color: rgba(16,185,129,0.5); color: #10b981; background: rgba(16,185,129,0.12); font-size: 0.75rem;" onclick="if(typeof window.openBinderyModal==='function'){window.openBinderyModal('all', null, '${p.id}');}else{if(typeof window.showView==='function')window.showView('vault');}">📚 立即装订</button>
                    <button class="action-btn p-btn-test-direct" data-id="${p.id}" data-category="${p.category}" onclick="window.fastTestPluginConnectivity('${p.id}', '${p.category}', this)" style="font-size: 0.75rem;">⚡ 通道自检</button>
                </div>
            `;
        } else if (p.category === 'tunnel') {
            controlBtnsHtml = `
                <div class="p-control-group" style="display:grid; grid-template-columns: 1fr; gap:8px;">
                    <button class="action-btn p-btn-test-direct glow-btn" data-id="${p.id}" data-category="${p.category}" onclick="window.fastTestPluginConnectivity('${p.id}', '${p.category}', this)" style="font-size: 0.75rem;">⚡ 通道自检</button>
                </div>
            `;
        } else {
            controlBtnsHtml = `
                <div class="p-control-group" style="display:grid; grid-template-columns: 1fr; gap:8px;">
                    <button class="action-btn p-btn-test-direct" data-id="${p.id}" data-category="${p.category}" onclick="window.fastTestPluginConnectivity('${p.id}', '${p.category}', this)">⚡ 测试连接</button>
                </div>
            `;
        }
    } else {
        controlBtnsHtml = `
            <div class="p-control-group" style="display:block; text-align:center; padding: 4px 0;">
                <span style="font-size:0.7rem; color:var(--text-dim); opacity:0.7; font-weight:500;">⚡ 物理内置驱动 (免配置)</span>
            </div>
        `;
    }

    const starChar = isPinned ? '★' : '☆';
    const starStyle = isPinned
        ? 'color: #ffb700; text-shadow: 0 0 6px rgba(255, 183, 0, 0.7); opacity: 1; transform: scale(1.08);'
        : 'color: var(--text-dim); text-shadow: none; opacity: 0.65;';

    // primaryHostingId 供卡片内主/镜像角色行使用（顶部不再显示徽章）
    const primaryHostingId = window.settingsData?.publish_control?.primary_hosting_id || '';

    // 协议驱动卡片专属顶部品类徽章（展示接入认证与部署形态）
    const AUTH_DEPLOYMENT_MAP = {
        'ollama': { label: '💻 本地离线 · 免密', color: '#10b981', bg: 'rgba(16, 185, 129, 0.08)', border: 'rgba(16, 185, 129, 0.25)' },
        'lmstudio': { label: '💻 本地离线 · 免密', color: '#10b981', bg: 'rgba(16, 185, 129, 0.08)', border: 'rgba(16, 185, 129, 0.25)' },
        'lmstudio_v1': { label: '💻 本地离线 · 免密', color: '#10b981', bg: 'rgba(16, 185, 129, 0.08)', border: 'rgba(16, 185, 129, 0.25)' },
        'localai': { label: '💻 本地私有 · 免密', color: '#10b981', bg: 'rgba(16, 185, 129, 0.08)', border: 'rgba(16, 185, 129, 0.25)' },
        'openrouter': { label: '🌐 聚合网关 · Key', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.08)', border: 'rgba(245, 158, 11, 0.25)' },
        'together': { label: '🌐 聚合网关 · Key', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.08)', border: 'rgba(245, 158, 11, 0.25)' },
        'siliconflow': { label: '🌐 聚合算力 · Key', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.08)', border: 'rgba(245, 158, 11, 0.25)' },
        'groq': { label: '⚡ 极速推理 · Key', color: '#06b6d4', bg: 'rgba(6, 182, 212, 0.08)', border: 'rgba(6, 182, 212, 0.25)' }
    };
    const defaultAuth = { label: '🔑 官方云端 · Key', color: 'var(--neon-cyan)', bg: 'rgba(0, 242, 255, 0.06)', border: 'rgba(0, 242, 255, 0.2)' };
    const authInfo = AUTH_DEPLOYMENT_MAP[rawId] || defaultAuth;

    // 官方推荐 / 典型模型标识
    const PROBE_MODEL_MAP = {
        'openai': 'gpt-4o',
        'deepseek': 'deepseek-chat',
        'gemini': 'gemini-2.0-flash',
        'claude': 'claude-3-5-sonnet',
        'anthropic': 'claude-3-5-sonnet',
        'ollama': 'llama3.2',
        'lmstudio': 'qwen2.5',
        'lmstudio_v1': 'qwen2.5',
        'volcengine': 'Doubao-pro',
        'minimax': 'abab6.5s',
        'zhipu': 'glm-4-flash',
        'moonshot': 'moonshot-v1',
        'kimi': 'moonshot-v1',
        'mistral': 'mistral-large',
        'openrouter': 'deepseek-r1',
        'together': 'Llama-3.3',
        'siliconflow': 'DeepSeek-V3',
        'groq': 'llama-3.3-70b',
        'dashscope': 'qwen-plus',
        'baichuan': 'Baichuan4',
        'spark': 'spark-v3.5',
        'hunyuan': 'hunyuan-lite',
        'cohere': 'command-r'
    };
    const typicalModel = PROBE_MODEL_MAP[rawId] || '基准模型';

    let topBadgeHtml = '';
    if (isProtocol) {
        topBadgeHtml = `<div class="log-tag" style="background: ${authInfo.bg}; color: ${authInfo.color}; border: 1px solid ${authInfo.border}; font-size: 0.68rem; font-weight: 600;">${authInfo.label}</div>`;
    } else if (p.is_manageable) {
        topBadgeHtml = `<div class="log-tag ${statusBadge.class}" style="${statusBadge.style}">${statusBadge.label}</div>`;
    } else {
        topBadgeHtml = `<div class="log-tag info" style="margin-right: 0 !important;">${p.status ? p.status.toUpperCase() : 'ACTIVE'}</div>`;
    }

    return `
    <div class="shield-pod plugin-pod ${p.is_in_use ? 'active-duty' : ''}">
        <div class="shield-status">
            <div style="display:flex; align-items:center; gap:8px;">
                <button type="button" class="plugin-pin-btn ${isPinned ? 'pinned' : ''}" onclick="window.togglePinPlugin('${p.id}', event)" title="${isPinned ? '取消常用置顶' : '置顶为常用能力'}" style="background: transparent; border: none; cursor: pointer; font-size: 0.95rem; padding: 0 2px; line-height: 1; transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1); ${starStyle}" onmouseover="if (!${isPinned}) { this.style.color='#ffb700'; this.style.opacity='0.9'; }" onmouseout="if (!${isPinned}) { this.style.color='var(--text-dim)'; this.style.opacity='0.65'; }">${starChar}</button>
                <span class="status-dot-mini ${p.is_enabled ? 'healthy' : 'blocked'}" id="dot-${p.category}-${p.id}"></span>
                <span class="shield-id">${p.version ? p.version.split(' ')[0] : 'V1.0'}</span>
            </div>
            ${topBadgeHtml}
        </div>

        
        <div class="shield-body" style="flex:1; display:flex; flex-direction:column;">
            <div class="plugin-pod-header" style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
                <div class="plugin-brand-avatar" title="${p.name || p.id}" style="width:24px; height:24px; min-width:24px; border-radius:6px; display:inline-flex; align-items:center; justify-content:center; font-size:0.95rem; background:${brand.bg}; border:1px solid ${brand.border}; box-shadow:0 1px 4px rgba(0,0,0,0.25); flex-shrink:0; user-select:none;">
                    ${brand.icon}
                </div>
                <div style="min-width:0; flex:1; display:flex; align-items:baseline; gap:6px; overflow:hidden;">
                    <span style="font-size:0.98rem; font-weight:700; color:var(--text-bright); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${p.name || p.id}">
                        ${p.name || p.id}
                    </span>
                    <span style="font-size:0.65rem; color:var(--text-muted, #94a3b8); opacity:0.65; font-family:var(--font-mono, monospace); white-space:nowrap;">
                        ${p.id}
                    </span>
                </div>
                ${homeUrl ? `<a href="${homeUrl}" target="_blank" onclick="event.stopPropagation()" title="访问 ${p.name || p.id} 官方主页 / API 密钥申请控制台 ↗" class="plugin-home-link" style="font-size:0.75rem; color:var(--neon-cyan); text-decoration:none; opacity:0.85; font-weight:700; border:1px solid rgba(0, 242, 255, 0.25); padding:1px 6px; border-radius:4px; background:rgba(0, 242, 254, 0.06); display:inline-flex; align-items:center; justify-content:center; flex-shrink:0; margin-right: 0 !important; line-height:1.2; transition:all 0.2s;" onmouseover="this.style.background='rgba(0,242,255,0.2)'; this.style.borderColor='var(--neon-cyan)';" onmouseout="this.style.background='rgba(0,242,255,0.06)'; this.style.borderColor='rgba(0, 242, 255, 0.25)';">↗</a>` : ''}
            </div>
            <p style="margin-bottom:10px; flex:1; font-size:0.75rem; color:var(--text-dim); line-height:1.45;">${p.description || 'Capability syncing...'}</p>
            
            ${isProtocol ? (() => {
                let hostLabel = '';
                if (p.default_url) {
                    try {
                        const u = new URL(p.default_url);
                        hostLabel = u.host;
                    } catch (e) {
                        hostLabel = p.default_url.replace(/https?:\/\//, '').split('/')[0];
                    }
                }
                const familyMap = {
                    'standard': 'OpenAI 兼容',
                    'reasoner': '深度推理',
                    'local': '本地推断',
                    'aggregator': '全域聚合',
                    'anthropic': 'Claude 契约',
                    'gemini': 'Gemini 矩阵',
                    'native': '原生驱动'
                };
                const familyText = familyMap[(p.protocol_family || '').toLowerCase()] || p.protocol_family || '官方标准';
                const aliasesStr = Array.isArray(p.aliases) && p.aliases.length > 0 ? p.aliases.join(', ') : '';

                return `
                    <div class="protocol-specs-strip" style="display:flex; flex-direction:column; gap:6px; margin-bottom:12px; font-size:0.68rem; line-height:1.2;">
                        ${hostLabel ? `
                            <div style="display:flex; align-items:center;">
                                <span style="background:rgba(0, 242, 255, 0.06); border:1px solid rgba(0, 242, 255, 0.2); color:var(--accent-secondary); padding:2px 6px; border-radius:4px; font-family:var(--font-mono, monospace); max-width:100%; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="默认物理端点: ${p.default_url}">🌐 ${hostLabel}</span>
                            </div>` : ''}
                        <div style="display:flex; flex-wrap:wrap; gap:5px; align-items:center;">
                            <span style="background:rgba(255, 255, 255, 0.04); border:1px solid var(--white-08); color:var(--text-dim); padding:2px 6px; border-radius:4px;" title="协议家族架构: ${p.protocol_family || 'native'}">🏷️ ${familyText}</span>
                            ${aliasesStr ? `<span style="background:rgba(255, 255, 255, 0.02); border:1px solid var(--white-08); color:var(--text-dim); opacity:0.85; padding:2px 6px; border-radius:4px;" title="兼容别名: ${aliasesStr}">别名: ${aliasesStr}</span>` : ''}
                        </div>
                    </div>
                `;
            })() : ''}

            ${isTheme ? '' : (isProtocol ? `
                <div class="pod-telemetry" style="margin-bottom:15px; padding:8px 12px; display:flex; align-items:center; justify-content:space-between; background:rgba(0,242,255,0.03); border:1px solid rgba(0,242,255,0.1); border-radius:8px; white-space:nowrap; gap:6px;">
                    <span class="tiny-label" style="display:inline-flex; align-items:center; gap:5px; font-weight:600; color:var(--text-dim); font-size:0.72rem; white-space:nowrap; cursor:default; user-select:none;" title="基准探针模型: ${typicalModel}" onclick="event.stopPropagation()">
                        <span style="color:var(--accent-secondary);">⚡</span>
                        <b style="color:var(--text-bright); font-weight:700;">${typicalModel}</b>
                    </span>
                    <span style="font-size:0.72rem; color:${usedCount > 0 ? 'var(--neon-green)' : 'var(--text-dim)'}; font-weight:700; white-space:nowrap; ${usedCount > 0 ? 'cursor:pointer; text-decoration:underline; text-underline-offset:2px;' : 'cursor:default;'}" title="${usedCount > 0 ? `已接入算力单元: ${matchingNodeIds.join(', ')}（点击跳转并定位单元）` : '未接入算力单元'}" onclick="event.stopPropagation(); ${usedCount > 0 ? `window.locateAndHighlightComputeNode('${matchingNodeIds[0]}')` : ''}">
                        ${usedCount > 0 ? `🟢 ${usedCount} 单元在用` : '⚪ 暂未接入'}
                    </span>
                </div>
            ` : (p.is_manageable ? (() => {
            let dotColor = 'rgba(255, 255, 255, 0.35)', statusText = '当前品牌未启用', textColor = 'var(--text-dim)', glowEffect = '';
            const isCredReady = (typeof window.isPluginCredentialReady === 'function') ? !!window.isPluginCredentialReady(p.id, p.category, p.cfg)?.ready : true;
            const effectiveInUse = Boolean(p.is_in_use && isCredReady);

            if (!p.is_enabled) {
                dotColor = '#ff4d4d'; statusText = '全局已禁用'; textColor = '#ff4d4d';
            } else if (!isCredReady) {
                dotColor = 'rgba(255, 255, 255, 0.25)'; statusText = '未配置凭据'; textColor = 'var(--text-dim)';
            } else if (effectiveInUse) {
                dotColor = 'var(--neon-green)'; statusText = '当前品牌已启用'; textColor = 'var(--neon-green)';
                glowEffect = 'box-shadow: 0 0 8px rgba(var(--neon-green-rgb), 0.6);';
            }
            const toggleTitle = !p.is_enabled ? '需先在顶部全局启用该插件' : (!isCredReady ? '需先点击 CONFIG 配置凭据后方可启用' : (effectiveInUse ? '在当前品牌停用' : '在当前品牌启用'));

            return `
                <div class="pod-telemetry" style="margin-bottom:15px; padding:8px 12px; display:flex; align-items:center; justify-content:space-between; white-space:nowrap; gap:6px; ${!p.is_enabled ? 'opacity:0.55; filter:grayscale(0.8); cursor:not-allowed;' : ''}">
                    <span class="tiny-label" style="display:inline-flex; align-items:center; gap:6px; font-weight:600; color:${textColor}; font-size:0.75rem; white-space:nowrap;">
                        <span style="background:${dotColor}; width:7px; height:7px; min-width:7px; border-radius:50%; display:inline-block; ${glowEffect}"></span>
                        ${statusText}
                    </span>
                    <label class="switch-toggle" style="margin:0;" onclick="event.stopPropagation();" title="${toggleTitle}">
                        <input type="checkbox" id="chk-use-${p.category}-${p.id}" ${effectiveInUse ? 'checked' : ''} ${!p.is_enabled ? 'disabled' : ''} onchange="window.toggleBrandActivation('${p.id}', this.checked, '${p.category}')">
                        <span class="slider round"></span>
                    </label>
                </div>
                `;
        })() : `
              <div class="pod-telemetry" style="margin-bottom:15px; padding:8px 12px; display:flex; align-items:center; white-space:nowrap;">
                  ${p.is_in_use ? `<span class="tiny-label" style="color:var(--neon-green); display:flex; align-items:center; gap:6px; white-space:nowrap;"><span class="heartbeat-indicator pulsing" style="background:var(--neon-green); width:6px; height:6px;"></span>${p.category === 'ebook' ? '内置装订引擎' : '品牌已绑定'}</span>` : '<span class="tiny-label" style="color:var(--text-dim); white-space:nowrap;">系统基础节点</span>'}
              </div>
            `))}

            ${(p.category === 'hosting' && p.is_in_use) ? (() => {
                const _isPrimary = primaryHostingId === p.id;
                return _isPrimary
                    ? `<div style="display:flex;align-items:center;justify-content:space-between;margin-top:-10px;margin-bottom:10px;padding:0 12px;white-space:nowrap;">
                           <span style="font-size:0.7rem;color:var(--neon-green);font-weight:800;letter-spacing:0.2px;white-space:nowrap;display:inline-flex;align-items:center;gap:4px;">🏠 官方主站</span>
                           <span class="hosting-canonical-tip" style="font-size:0.65rem;color:var(--text-muted, #475569);font-weight:600;white-space:nowrap;" title="搜索引擎以此为主访问入口（Canonical 权威收录），其余平台作为备用镜像同步更新">首选访问源 ℹ️</span>
                       </div>`
                    : `<div style="display:flex;align-items:center;justify-content:space-between;margin-top:-10px;margin-bottom:10px;padding:0 12px;white-space:nowrap;">
                           <span style="font-size:0.68rem;color:var(--text-dim);font-weight:600;opacity:0.8;white-space:nowrap;display:inline-flex;align-items:center;gap:4px;">🔄 备用镜像</span>
                           <button type="button" onclick="window.setHostingAsPrimary('${p.id}',event)" title="将此平台切换为主站" style="font-size:0.65rem;color:var(--neon-green);background:none;border:none;cursor:pointer;font-weight:600;padding:0;text-decoration:underline;text-underline-offset:2px;transition:opacity 0.15s;white-space:nowrap;" onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">设为主站 →</button>
                       </div>`;
            })() : ''}

            ${controlBtnsHtml}
        </div>
    </div>
`;

};


// 🔒 [SOP-02 物理拆分] 能力节点卡片 3D 视差物理微动效与算力中心路由跳转已抽离至独立分片：
// -> web/dashboard/js/plugins/render_shards/plugins.render.physics.js

