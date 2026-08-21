/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Pod Card HTML & 3D Physics Shard
 * 职责：能力节点 Pod 卡片 HTML 构造器与 3D 视差微动效。
 */

window.getPlatformBrandBadge = (id, category = '') => {
    const rawId = (id || '').toLowerCase();
    const cleanId = rawId.replace(/_/g, '');

    const BRAND_DICT = {
        // 📢 社交媒体与分发平台 (Publishers & Syndication)
        'xiaohongshu': { icon: '📕', color: '#ff2442', bg: 'rgba(255, 36, 66, 0.14)', border: 'rgba(255, 36, 66, 0.35)' },
        'red': { icon: '📕', color: '#ff2442', bg: 'rgba(255, 36, 66, 0.14)', border: 'rgba(255, 36, 66, 0.35)' },
        'toutiao': { icon: '⚡', color: '#ed4040', bg: 'rgba(237, 64, 64, 0.14)', border: 'rgba(237, 64, 64, 0.35)' },
        'csdn': { icon: '📑', color: '#fc5531', bg: 'rgba(252, 85, 49, 0.14)', border: 'rgba(252, 85, 49, 0.35)' },
        'cnblogs': { icon: '🌿', color: '#2b73af', bg: 'rgba(43, 115, 175, 0.14)', border: 'rgba(43, 115, 175, 0.35)' },
        'bilibili': { icon: '📺', color: '#00aeec', bg: 'rgba(0, 174, 236, 0.14)', border: 'rgba(0, 174, 236, 0.35)' },
        'segmentfault': { icon: '💡', color: '#009a61', bg: 'rgba(0, 154, 97, 0.14)', border: 'rgba(0, 154, 97, 0.35)' },
        'oschina': { icon: '🇨🇳', color: '#21b351', bg: 'rgba(33, 179, 81, 0.14)', border: 'rgba(33, 179, 81, 0.35)' },
        'devto': { icon: '👩‍💻', color: '#ffffff', bg: 'rgba(255, 255, 255, 0.12)', border: 'rgba(255, 255, 255, 0.3)' },
        'dev_to': { icon: '👩‍💻', color: '#ffffff', bg: 'rgba(255, 255, 255, 0.12)', border: 'rgba(255, 255, 255, 0.3)' },
        'hashnode': { icon: '🔷', color: '#2962ff', bg: 'rgba(41, 98, 255, 0.14)', border: 'rgba(41, 98, 255, 0.35)' },
        'medium': { icon: '📝', color: '#ffffff', bg: 'rgba(255, 255, 255, 0.14)', border: 'rgba(255, 255, 255, 0.3)' },
        'ghost': { icon: '👻', color: '#738a94', bg: 'rgba(115, 138, 148, 0.14)', border: 'rgba(115, 138, 148, 0.35)' },
        'wordpress': { icon: '📰', color: '#21759b', bg: 'rgba(33, 117, 155, 0.14)', border: 'rgba(33, 117, 155, 0.35)' },
        'wechat': { icon: '💬', color: '#07c160', bg: 'rgba(7, 193, 96, 0.14)', border: 'rgba(7, 193, 96, 0.35)' },
        'zhihu': { icon: '💡', color: '#0084ff', bg: 'rgba(0, 132, 255, 0.14)', border: 'rgba(0, 132, 255, 0.35)' },
        'juejin': { icon: '🧱', color: '#1e80ff', bg: 'rgba(30, 128, 255, 0.14)', border: 'rgba(30, 128, 255, 0.35)' },
        'substack': { icon: '📮', color: '#ff6719', bg: 'rgba(255, 103, 25, 0.14)', border: 'rgba(255, 103, 25, 0.35)' },
        'telegram': { icon: '✈️', color: '#24a1de', bg: 'rgba(36, 161, 222, 0.14)', border: 'rgba(36, 161, 222, 0.35)' },
        'discord': { icon: '💬', color: '#5865f2', bg: 'rgba(88, 101, 242, 0.14)', border: 'rgba(88, 101, 242, 0.35)' },
        'linkedin': { icon: '💼', color: '#0a66c2', bg: 'rgba(10, 102, 194, 0.14)', border: 'rgba(10, 102, 194, 0.35)' },

        // 🌐 全站托管 (Hosting Platforms)
        'cloudflare_pages': { icon: '🟧', color: '#f38020', bg: 'rgba(243, 128, 32, 0.14)', border: 'rgba(243, 128, 32, 0.35)' },
        'cloudflare': { icon: '🟧', color: '#f38020', bg: 'rgba(243, 128, 32, 0.14)', border: 'rgba(243, 128, 32, 0.35)' },
        'github_pages': { icon: '🐙', color: '#ffffff', bg: 'rgba(255, 255, 255, 0.12)', border: 'rgba(255, 255, 255, 0.3)' },
        'github': { icon: '🐙', color: '#ffffff', bg: 'rgba(255, 255, 255, 0.12)', border: 'rgba(255, 255, 255, 0.3)' },
        'gitee_pages': { icon: '🔴', color: '#c71d23', bg: 'rgba(199, 29, 35, 0.14)', border: 'rgba(199, 29, 35, 0.35)' },
        'gitee': { icon: '🔴', color: '#c71d23', bg: 'rgba(199, 29, 35, 0.14)', border: 'rgba(199, 29, 35, 0.35)' },
        'gitlab_pages': { icon: '🦊', color: '#fc6d26', bg: 'rgba(252, 109, 38, 0.14)', border: 'rgba(252, 109, 38, 0.35)' },
        'coding_pages': { icon: '💎', color: '#3273dc', bg: 'rgba(50, 115, 220, 0.14)', border: 'rgba(50, 115, 220, 0.35)' },
        'netlify': { icon: '🌐', color: '#00c7b7', bg: 'rgba(0, 199, 183, 0.14)', border: 'rgba(0, 199, 183, 0.35)' },
        'vercel': { icon: '▲', color: '#ffffff', bg: 'rgba(255, 255, 255, 0.14)', border: 'rgba(255, 255, 255, 0.35)' },
        'zeabur': { icon: '⛵', color: '#6366f1', bg: 'rgba(99, 102, 241, 0.14)', border: 'rgba(99, 102, 241, 0.35)' },
        'render': { icon: '🟣', color: '#46e3b7', bg: 'rgba(70, 227, 183, 0.14)', border: 'rgba(70, 227, 183, 0.35)' },
        'railway': { icon: '🚂', color: '#ec4899', bg: 'rgba(236, 72, 153, 0.14)', border: 'rgba(236, 72, 153, 0.35)' },
        'firebase': { icon: '🔥', color: '#ffca28', bg: 'rgba(255, 202, 40, 0.14)', border: 'rgba(255, 202, 40, 0.35)' },

        // 📷 图床与对象存储 (Image Hosting & Object Storage)
        's3': { icon: '🪣', color: '#ff9900', bg: 'rgba(255, 153, 0, 0.14)', border: 'rgba(255, 153, 0, 0.35)' },
        'sm_ms': { icon: '🖼️', color: '#1890ff', bg: 'rgba(24, 144, 255, 0.14)', border: 'rgba(24, 144, 255, 0.35)' },
        'smms': { icon: '🖼️', color: '#1890ff', bg: 'rgba(24, 144, 255, 0.14)', border: 'rgba(24, 144, 255, 0.35)' },
        'imgur': { icon: '🟢', color: '#1bb76e', bg: 'rgba(27, 183, 110, 0.14)', border: 'rgba(27, 183, 110, 0.35)' },
        'telegraph': { icon: '📰', color: '#999999', bg: 'rgba(255, 255, 255, 0.1)', border: 'rgba(255, 255, 255, 0.25)' },
        'aliyun_oss': { icon: '☁️', color: '#ff6a00', bg: 'rgba(255, 106, 0, 0.14)', border: 'rgba(255, 106, 0, 0.35)' },
        'tencent_cos': { icon: '🐧', color: '#00a4ff', bg: 'rgba(0, 164, 255, 0.14)', border: 'rgba(0, 164, 255, 0.35)' },
        'upyun_uss': { icon: '☁️', color: '#00b7ee', bg: 'rgba(0, 183, 238, 0.14)', border: 'rgba(0, 183, 238, 0.35)' },
        'upyun': { icon: '☁️', color: '#00b7ee', bg: 'rgba(0, 183, 238, 0.14)', border: 'rgba(0, 183, 238, 0.35)' },
        'qiniu': { icon: '🔵', color: '#0099ff', bg: 'rgba(0, 153, 255, 0.14)', border: 'rgba(0, 153, 255, 0.35)' },
        'qiniu_kodo': { icon: '🔵', color: '#0099ff', bg: 'rgba(0, 153, 255, 0.14)', border: 'rgba(0, 153, 255, 0.35)' },
        'lsky_pro': { icon: '🌌', color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.14)', border: 'rgba(59, 130, 246, 0.35)' },
        'superbed': { icon: '🛏️', color: '#ec4899', bg: 'rgba(236, 72, 153, 0.14)', border: 'rgba(236, 72, 153, 0.35)' },
        'sftp': { icon: '🔒', color: '#10b981', bg: 'rgba(16, 185, 129, 0.14)', border: 'rgba(16, 185, 129, 0.35)' },

        // 🔔 消息通知 (Notifications)
        'feishu': { icon: '🕊️', color: '#00d6b9', bg: 'rgba(0, 214, 185, 0.14)', border: 'rgba(0, 214, 185, 0.35)' },
        'dingtalk': { icon: '🔔', color: '#0089ff', bg: 'rgba(0, 137, 255, 0.14)', border: 'rgba(0, 137, 255, 0.35)' },
        'wecom': { icon: '💬', color: '#2574eb', bg: 'rgba(37, 116, 235, 0.14)', border: 'rgba(37, 116, 235, 0.35)' },
        'email': { icon: '📧', color: '#ea4335', bg: 'rgba(234, 67, 53, 0.14)', border: 'rgba(234, 67, 53, 0.35)' },
        'sms': { icon: '📱', color: '#10b981', bg: 'rgba(16, 185, 129, 0.14)', border: 'rgba(16, 185, 129, 0.35)' },
        'app_push': { icon: '📲', color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.14)', border: 'rgba(139, 92, 246, 0.35)' },
        'generic_webhook': { icon: '🪝', color: '#00f2fe', bg: 'rgba(0, 242, 254, 0.14)', border: 'rgba(0, 242, 254, 0.35)' },
        'webhook_dispatch': { icon: '🪝', color: '#00f2fe', bg: 'rgba(0, 242, 254, 0.14)', border: 'rgba(0, 242, 254, 0.35)' },

        // 🎨 装帧主题与引擎 (Themes & SSG Engines)
        'sovereign': { icon: '👑', color: '#ffd700', bg: 'rgba(255, 215, 0, 0.18)', border: 'rgba(255, 215, 0, 0.45)' },
        'universal': { icon: '🌌', color: '#00f2fe', bg: 'rgba(0, 242, 254, 0.18)', border: 'rgba(0, 242, 254, 0.45)' },
        'docusaurus': { icon: '🦖', color: '#3ecc5f', bg: 'rgba(62, 204, 95, 0.18)', border: 'rgba(62, 204, 95, 0.45)' },
        'starlight': { icon: '🌟', color: '#9d4edd', bg: 'rgba(157, 78, 221, 0.18)', border: 'rgba(157, 78, 221, 0.45)' },
        'vitepress': { icon: '⚡', color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.18)', border: 'rgba(139, 92, 246, 0.45)' },
        'nextra': { icon: '📐', color: '#00f2fe', bg: 'rgba(0, 242, 254, 0.18)', border: 'rgba(0, 242, 254, 0.45)' },
        'hugo': { icon: '🦔', color: '#ff4088', bg: 'rgba(255, 64, 136, 0.18)', border: 'rgba(255, 64, 136, 0.45)' },
        'hexo': { icon: '⬡', color: '#0e83cd', bg: 'rgba(14, 131, 205, 0.18)', border: 'rgba(14, 131, 205, 0.45)' },
        'astro': { icon: '🚀', color: '#ff5d01', bg: 'rgba(255, 93, 1, 0.18)', border: 'rgba(255, 93, 1, 0.45)' },
        'nextjs': { icon: '▲', color: '#ffffff', bg: 'rgba(255, 255, 255, 0.18)', border: 'rgba(255, 255, 255, 0.45)' },
        'vuepress': { icon: '💚', color: '#42b983', bg: 'rgba(66, 185, 131, 0.18)', border: 'rgba(66, 185, 131, 0.45)' },

        // 🧠 AI 协议与核心组件 (AI Protocols & Processing)
        'openai': { icon: '🤖', color: '#10a37f', bg: 'rgba(16, 163, 127, 0.14)', border: 'rgba(16, 163, 127, 0.35)' },
        'anthropic': { icon: '🧠', color: '#d97706', bg: 'rgba(217, 119, 6, 0.14)', border: 'rgba(217, 119, 6, 0.35)' },
        'claude': { icon: '🧠', color: '#d97706', bg: 'rgba(217, 119, 6, 0.14)', border: 'rgba(217, 119, 6, 0.35)' },
        'gemini': { icon: '♊', color: '#4285f4', bg: 'rgba(66, 133, 244, 0.14)', border: 'rgba(66, 133, 244, 0.35)' },
        'deepseek': { icon: '🐋', color: '#0066ff', bg: 'rgba(0, 102, 255, 0.14)', border: 'rgba(0, 102, 255, 0.35)' },
        'ollama': { icon: '🦙', color: '#ffffff', bg: 'rgba(255, 255, 255, 0.14)', border: 'rgba(255, 255, 255, 0.35)' },
        'qwen': { icon: '🐲', color: '#ff6a00', bg: 'rgba(255, 106, 0, 0.14)', border: 'rgba(255, 106, 0, 0.35)' },
        'zhipu': { icon: '🌟', color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.14)', border: 'rgba(59, 130, 246, 0.35)' },
        'exif_scrubber': { icon: '🛡️', color: '#00ff88', bg: 'rgba(0, 255, 136, 0.14)', border: 'rgba(0, 255, 136, 0.35)' },
        'sensitive_filter': { icon: '🚫', color: '#ff4d4d', bg: 'rgba(255, 77, 77, 0.14)', border: 'rgba(255, 77, 77, 0.35)' },
        'ast_processor': { icon: '🧬', color: '#a855f7', bg: 'rgba(168, 85, 247, 0.14)', border: 'rgba(168, 85, 247, 0.35)' },
        'markdown_normalizer': { icon: '📝', color: '#00f2fe', bg: 'rgba(0, 242, 254, 0.14)', border: 'rgba(0, 242, 254, 0.35)' }
    };

    if (BRAND_DICT[rawId]) return BRAND_DICT[rawId];
    if (BRAND_DICT[cleanId]) return BRAND_DICT[cleanId];

    // 针对模糊命名的 fallback
    for (const k in BRAND_DICT) {
        if (rawId.includes(k)) return BRAND_DICT[k];
    }

    // 依据大类 fallback
    const CAT_FALLBACKS = {
        'publisher': { icon: '📢', color: '#00f2fe', bg: 'rgba(0, 242, 254, 0.12)', border: 'rgba(0, 242, 254, 0.3)' },
        'hosting': { icon: '🌐', color: '#38bdf8', bg: 'rgba(56, 189, 248, 0.12)', border: 'rgba(56, 189, 248, 0.3)' },
        'image_hosting': { icon: '📷', color: '#ec4899', bg: 'rgba(236, 72, 153, 0.12)', border: 'rgba(236, 72, 153, 0.3)' },
        'notification': { icon: '🔔', color: '#fbbf24', bg: 'rgba(251, 191, 36, 0.12)', border: 'rgba(251, 191, 36, 0.3)' },
        'theme': { icon: '🎨', color: '#a855f7', bg: 'rgba(168, 85, 247, 0.12)', border: 'rgba(168, 85, 247, 0.3)' },
        'protocol': { icon: '🧠', color: '#10b981', bg: 'rgba(16, 185, 129, 0.12)', border: 'rgba(16, 185, 129, 0.3)' },
        'transformer': { icon: '🛠️', color: '#f97316', bg: 'rgba(249, 115, 22, 0.12)', border: 'rgba(249, 115, 22, 0.3)' },
        'masker': { icon: '🛡️', color: '#06b6d4', bg: 'rgba(6, 182, 212, 0.12)', border: 'rgba(6, 182, 212, 0.3)' },
        'ingress_source': { icon: '📥', color: '#84cc16', bg: 'rgba(132, 204, 22, 0.12)', border: 'rgba(132, 204, 22, 0.3)' },
        'ingress_dialect': { icon: '📖', color: '#84cc16', bg: 'rgba(132, 204, 22, 0.12)', border: 'rgba(132, 204, 22, 0.3)' },
        'editorial': { icon: '🧬', color: '#6366f1', bg: 'rgba(99, 102, 241, 0.12)', border: 'rgba(99, 102, 241, 0.3)' }
    };

    return CAT_FALLBACKS[category] || { icon: '🧩', color: '#00f2fe', bg: 'rgba(0, 242, 254, 0.12)', border: 'rgba(0, 242, 254, 0.3)' };
};

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
    const canConfig = window.isPluginConfigurable(p);
    const canTest = ['hosting', 'image_hosting', 'publisher', 'notification'].includes(p.category) && p.is_manageable;
    const statusBadge = window.checkPluginConfiguredStatus(p);

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
        controlBtnsHtml = `
            <div class="p-control-group" style="display:grid; grid-template-columns: 1fr; gap:8px;">
                <button class="action-btn p-btn-test-direct" data-id="${p.id}" data-category="${p.category}" onclick="window.fastTestPluginConnectivity('${p.id}', '${p.category}', this)">⚡ 测试连接</button>
            </div>
        `;
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
        : 'color: rgba(255, 255, 255, 0.35); text-shadow: none; opacity: 0.55;';

    return `
    <div class="shield-pod plugin-pod ${p.is_in_use ? 'active-duty' : ''}">
        <div class="shield-status">
            <div style="display:flex; align-items:center; gap:8px;">
                <button type="button" class="plugin-pin-btn ${isPinned ? 'pinned' : ''}" onclick="window.togglePinPlugin('${p.id}', event)" title="${isPinned ? '取消常用置顶' : '置顶为常用能力'}" style="background: transparent; border: none; cursor: pointer; font-size: 0.95rem; padding: 0 2px; line-height: 1; transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1); ${starStyle}" onmouseover="if (!${isPinned}) { this.style.color='#ffb700'; this.style.opacity='0.9'; }" onmouseout="if (!${isPinned}) { this.style.color='rgba(255, 255, 255, 0.35)'; this.style.opacity='0.55'; }">${starChar}</button>
                <span class="status-dot-mini ${p.is_enabled ? 'healthy' : 'blocked'}" id="dot-${p.category}-${p.id}"></span>
                <span class="shield-id">${p.version ? p.version.split(' ')[0] : 'V1.0'}</span>
            </div>
            ${p.is_manageable
            ? `<div class="log-tag ${statusBadge.class}" style="${statusBadge.style}">${statusBadge.label}</div>`
            : `<div class="log-tag info" style="margin-right: 0 !important;">${p.status ? p.status.toUpperCase() : 'ACTIVE'}</div>`
        }
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
                ${homeUrl ? `<a href="${homeUrl}" target="_blank" onclick="event.stopPropagation()" title="访问 ${p.name || p.id} 官方平台 ↗" class="plugin-home-link" style="font-size:0.75rem; color:var(--neon-cyan); text-decoration:none; opacity:0.85; font-weight:700; border:1px solid rgba(0, 242, 255, 0.25); padding:1px 6px; border-radius:4px; background:rgba(0, 242, 254, 0.06); display:inline-flex; align-items:center; justify-content:center; flex-shrink:0; margin-right: 0 !important; line-height:1.2; transition:all 0.2s;" onmouseover="this.style.background='rgba(0,242,255,0.2)'; this.style.borderColor='var(--neon-cyan)';" onmouseout="this.style.background='rgba(0,242,255,0.06)'; this.style.borderColor='rgba(0, 242, 255, 0.25)';">↗</a>` : ''}
            </div>
            <p style="margin-bottom:12px; flex:1; font-size:0.75rem; color:var(--text-dim); line-height:1.45;">${p.description || 'Capability syncing...'}</p>
            
            ${isTheme ? '' : (p.is_manageable ? (() => {
            const isConfigured = statusBadge && statusBadge.label && (statusBadge.label.includes('🟢') || statusBadge.label.includes('就绪') || statusBadge.label.includes('配置齐全'));
            let dotColor = 'rgba(255, 255, 255, 0.35)';
            let statusText = '当前品牌未启用';
            let textColor = 'var(--text-dim)';
            let glowEffect = '';

            if (!p.is_enabled) {
                dotColor = '#ff4d4d';
                statusText = '全局已禁用';
                textColor = '#ff4d4d';
            } else if (p.is_in_use) {
                dotColor = '#00ff88';
                statusText = '当前品牌已启用';
                textColor = '#00ff88';
                glowEffect = 'box-shadow: 0 0 8px rgba(0, 255, 136, 0.6);';
            } else if (isConfigured) {
                dotColor = '#ffb700';
                statusText = '配置就绪 (待启用)';
                textColor = '#ffb700';
                glowEffect = 'box-shadow: 0 0 8px rgba(255, 183, 0, 0.5);';
            }

            return `
                <div class="pod-telemetry" style="margin-bottom:15px; padding:8px 12px; display:flex; align-items:center; justify-content:space-between; ${!p.is_enabled ? 'opacity:0.55; filter:grayscale(0.8); cursor:not-allowed;' : ''}">
                    <span class="tiny-label" style="display:inline-flex; align-items:center; gap:6px; font-weight:600; color:${textColor}; font-size:0.75rem;">
                        <span style="background:${dotColor}; width:7px; height:7px; border-radius:50%; display:inline-block; ${glowEffect}"></span>
                        ${statusText}
                    </span>
                    <label class="p-switch" style="${!p.is_enabled ? 'pointer-events:none;' : ''}">
                        <input type="checkbox" ${p.is_in_use ? 'checked' : ''} onchange="toggleBrandActivation('${p.id}', this.checked, '${p.category}')" ${!p.is_enabled ? 'disabled' : ''}>
                        <span class="p-slider round"></span>
                    </label>
                </div>
                `;
        })() : `
              <div class="pod-telemetry" style="margin-bottom:15px; padding:8px 12px; display:flex; align-items:center;">
                  ${p.is_in_use ? '<span class="tiny-label" style="color:#00ff88; display:flex; align-items:center; gap:6px;"><span class="heartbeat-indicator pulsing" style="background:#00ff88; width:6px; height:6px;"></span>品牌已绑定</span>' : '<span class="tiny-label" style="color:var(--text-dim);">系统基础节点</span>'}
              </div>
            `)}

            ${controlBtnsHtml}
        </div>
    </div>
`;
};

window.init3DHoverPhysics = () => {
    document.querySelectorAll('.shield-pod').forEach(pod => {
        if (pod.dataset.has3DPhysics) return;
        pod.dataset.has3DPhysics = 'true';

        pod.addEventListener('mousemove', (e) => {
            const rect = pod.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const tiltX = (y - centerY) / 16;
            const tiltY = -(x - centerX) / 16;

            pod.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) translateZ(4px)`;
            pod.style.setProperty('--mouse-x', `${(x / rect.width) * 100}%`);
            pod.style.setProperty('--mouse-y', `${(y / rect.height) * 100}%`);
        });

        pod.addEventListener('mouseleave', () => {
            pod.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateZ(0px)';
        });
    });
};
