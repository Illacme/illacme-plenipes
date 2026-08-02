/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Pod Card HTML & 3D Physics Shard
 * 职责：能力节点 Pod 卡片 HTML 构造器与 3D 视差微动效。
 */

window.buildPluginPodHtml = (p, isPinned) => {
    const portalInfo = window.PLATFORM_PORTAL_LINKS ? window.PLATFORM_PORTAL_LINKS[p.id] : null;
    const homeUrl = portalInfo ? portalInfo.home : null;

    const canConfig = window.isPluginConfigurable(p);
    const canTest = ['hosting', 'image_hosting', 'publisher', 'notification'].includes(p.category) && p.is_manageable;
    const statusBadge = window.checkPluginConfiguredStatus(p);

    let controlBtnsHtml = '';
    if (canConfig && canTest) {
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

    return `
    <div class="shield-pod plugin-pod ${p.is_in_use ? 'active-duty' : ''}">
        <div class="shield-status">
            <div style="display:flex; align-items:center; gap:8px;">
                <button type="button" onclick="window.togglePinPlugin('${p.id}', event)" title="${isPinned ? '取消常用置顶' : '置顶为常用能力'}" style="background: transparent; border: none; cursor: pointer; font-size: 0.85rem; padding: 0; line-height: 1; opacity: ${isPinned ? '1' : '0.35'}; transition: all 0.2s;" onmouseover="this.style.opacity='1';">⭐</button>
                <span class="status-dot-mini ${p.is_enabled ? 'healthy' : 'blocked'}" id="dot-${p.category}-${p.id}"></span>
                <span class="shield-id">RELEASE ${p.version ? p.version.split(' ')[0] : 'V1.0'}</span>
            </div>
            ${p.is_manageable
            ? `<div class="log-tag ${statusBadge.class}" style="${statusBadge.style}">${statusBadge.label}</div>`
            : `<div class="log-tag info" style="margin-right: 0 !important;">${p.status ? p.status.toUpperCase() : 'ACTIVE'}</div>`
        }
        </div>
        
        <div class="shield-body" style="flex:1; display:flex; flex-direction:column;">
            <h4 style="font-size:1.1rem; color:var(--text-bright); margin-bottom:5px; display:flex; align-items:center; justify-content:space-between; gap:8px;">
                <span>${p.name || p.id}</span>
                ${homeUrl ? `<a href="${homeUrl}" target="_blank" onclick="event.stopPropagation()" title="访问 ${p.name || p.id} 官方网站" style="font-size:0.68rem; color:var(--neon-cyan); text-decoration:none; opacity:0.9; font-weight:500; border:1px solid rgba(0, 242, 255, 0.35); padding:2px 8px; border-radius:6px; background:rgba(0, 242, 254, 0.08); display:inline-flex; align-items:center; gap:4px; flex-shrink:0; margin-right: 0 !important; transition:all 0.2s;" onmouseover="this.style.background='rgba(0,242,255,0.2)'; this.style.borderColor='var(--neon-cyan)';" onmouseout="this.style.background='rgba(0,242,255,0.08)'; this.style.borderColor='rgba(0, 242, 255, 0.35)';">🌐 官网 ↗</a>` : ''}
            </h4>
            <p style="margin-bottom:15px; flex:1; font-size:0.75rem; color:var(--text-dim);">${p.description || 'Capability syncing...'}</p>
            
            ${p.is_manageable ? (() => {
            const isConfigured = statusBadge && statusBadge.label && statusBadge.label.includes('配置齐全');
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
            `}

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
