/**
 * 🖼️ [V2.1] Illacme Plenipes Article Syndication - Channel Cover Studio Shard
 * 职责：全渠道封面真机高保真交互取景器（纯鼠标拖拽平移、滚轮自由无级缩放、自适应窄屏与多画幅）。
 * 🛡️ [SOP-01] 物理行数保持在 300 行以内。
 */
(function () {
    window.currentSyndicateCover = window.currentSyndicateCover || {
        mode: 'global', url: '', offset: 0, aspect_ratio: '16:9', overrides: {}
    };
    if (!window.currentSyndicateCover.overrides) window.currentSyndicateCover.overrides = {};

    const CHANNEL_RATIO_META = {
        'wechat': { ratio: '2.35:1', cssRatio: '2.35 / 1', label: '微信 2.35:1 列表大图', icon: '💬', maxH: '230px' },
        'xiaohongshu': { ratio: '3:4', cssRatio: '3 / 4', label: '小红书 3:4 竖屏双列瀑布流', icon: '📕', maxH: '380px' },
        'rednote': { ratio: '3:4', cssRatio: '3 / 4', label: '小红书 3:4 竖屏大图', icon: '📕', maxH: '380px' },
        'instagram': { ratio: '1:1', cssRatio: '1 / 1', label: 'Instagram 1:1 正方图', icon: '📷', maxH: '300px' },
        'zhihu': { ratio: '16:9', cssRatio: '16 / 9', label: '知乎 16:9 专栏题图', icon: '知', maxH: '260px' },
        'juejin': { ratio: '16:9', cssRatio: '16 / 9', label: '掘金 16:9 技术横幅', icon: '掘', maxH: '260px' },
        'devto': { ratio: '16:9', cssRatio: '16 / 9', label: 'Dev.to 16:9 社区主图', icon: '👩‍💻', maxH: '260px' }
    };

    window.getChannelAspectMeta = function (channel) {
        const c = String(channel || '').toLowerCase();
        return CHANNEL_RATIO_META[c] || { ratio: '16:9', cssRatio: '16 / 9', label: '16:9 全画幅专栏', icon: '🌐', maxH: '260px' };
    };

    window.getChannelCoverConfig = function (channel) {
        const c = String(channel || '').toLowerCase();
        window.currentSyndicateCover.overrides = window.currentSyndicateCover.overrides || {};
        return window.currentSyndicateCover.overrides[c] || { focal_x: 50, focal_y: 50, zoom: 100, override_url: '' };
    };

    window.renderChannelCoverStudio = function (channel, containerEl, defaultCoverUrl) {
        if (!containerEl) return;
        const c = String(channel || 'wechat').toLowerCase();
        const meta = window.getChannelAspectMeta(c);
        const cfg = window.getChannelCoverConfig(c);
        const masterUrl = (window.currentSyndicateCover && window.currentSyndicateCover.url) || defaultCoverUrl || '';
        const activeUrl = cfg.override_url || masterUrl;
        const isOverridden = !!cfg.override_url;

        containerEl.innerHTML = `
            <div class="channel-cover-studio-panel">
                <div class="channel-cover-studio-header">
                    <div class="channel-cover-studio-title-box">
                        <span>${meta.icon}</span><span>${meta.label}</span>
                        ${isOverridden ? '<span class="channel-cover-studio-tag--purple">已独立配图</span>' : '<span class="channel-cover-studio-tag--cyan">母图自适应</span>'}
                    </div>
                    <div class="channel-cover-studio-actions">
                        <button type="button" class="channel-cover-studio-btn--pick" onclick="window.pickOverrideCoverForChannel('${c}')" title="为本平台单独指定封面海报">🖼️ 独立配图</button>
                        ${isOverridden ? `<button type="button" class="channel-cover-studio-btn--reset" onclick="window.resetChannelCoverOverride('${c}')" title="清除独立覆盖，恢复跟随母图自适应">🔄 还原母图</button>` : ''}
                        <button type="button" class="channel-cover-studio-btn--default" onclick="window.resetChannelCropParams('${c}')" title="重置缩放与焦点为默认居中">↺ 重置</button>
                    </div>
                </div>
                <div id="channel-crop-viewport-${c}" class="channel-crop-viewport" style="aspect-ratio:${meta.cssRatio};max-height:${meta.maxH};" title="鼠标直接拖拽平移取景，滚轮自由缩放变焦">
                    ${activeUrl ? `
                        <img id="channel-preview-cover-img-${c}" class="channel-preview-cover-img" src="${activeUrl}" alt="封面排版" onload="window.updateChannelCoverTransform('${c}')" />
                        <div class="channel-crop-grid-overlay"></div>
                        <div id="channel-preview-focal-hint-${c}" class="channel-crop-focal-hint">🔍 100% · 按住拖拽 · 滚轮缩放</div>
                    ` : '<div class="syndicate-preview-empty">暂无有效封面图片</div>'}
                </div>
            </div>
        `;
        window.bindViewportDragAndWheel(c);
        setTimeout(() => window.updateChannelCoverTransform(c), 20);
    };

    window.updateChannelCoverTransform = function (channel) {
        const c = String(channel || '').toLowerCase();
        const img = document.getElementById(`channel-preview-cover-img-${c}`);
        const vp = document.getElementById(`channel-crop-viewport-${c}`);
        if (!img || !vp) return;

        const cfg = window.getChannelCoverConfig(c);
        const fx = typeof cfg.focal_x === 'number' ? cfg.focal_x : 50;
        const fy = typeof cfg.focal_y === 'number' ? cfg.focal_y : 50;
        const zm = typeof cfg.zoom === 'number' ? cfg.zoom : 100;
        const scale = zm / 100;

        const vpW = vp.clientWidth || 380;
        const vpH = vp.clientHeight || Math.round(vpW / 1.77);
        const vpRatio = vpW / Math.max(1, vpH);

        const natW = img.naturalWidth || 1600;
        const natH = img.naturalHeight || 900;
        const imgRatio = natW / Math.max(1, natH);

        let baseW, baseH;
        if (imgRatio > vpRatio) {
            baseH = vpH;
            baseW = vpH * imgRatio;
        } else {
            baseW = vpW;
            baseH = vpW / imgRatio;
        }

        const renderW = Math.round(baseW * scale);
        const renderH = Math.round(baseH * scale);
        const maxMoveX = Math.max(0, renderW - vpW);
        const maxMoveY = Math.max(0, renderH - vpH);

        const transX = Math.round((0.5 - fx / 100) * maxMoveX);
        const transY = Math.round((0.5 - fy / 100) * maxMoveY);

        img.style.width = `${renderW}px`;
        img.style.height = `${renderH}px`;
        img.style.transform = `translate(calc(-50% + ${transX}px), calc(-50% + ${transY}px))`;

        const hint = document.getElementById(`channel-preview-focal-hint-${c}`);
        if (hint) {
            const isDefault = (fx === 50 && fy === 50 && zm === 100);
            hint.innerHTML = isDefault
                ? `🔍 100% · 按住拖拽 · 滚轮缩放`
                : `🔍 ${zm}% · 🎯 (${fx}%, ${fy}%)`;
        }
    };

    window.bindViewportDragAndWheel = function (channel) {
        const c = String(channel || '').toLowerCase();
        const vp = document.getElementById(`channel-crop-viewport-${c}`);
        if (!vp) return;

        let isDragging = false, startX = 0, startY = 0, initialFx = 50, initialFy = 50;

        vp.onmousedown = function (e) {
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            const cfg = window.getChannelCoverConfig(c);
            initialFx = typeof cfg.focal_x === 'number' ? cfg.focal_x : 50;
            initialFy = typeof cfg.focal_y === 'number' ? cfg.focal_y : 50;
            vp.style.cursor = 'grabbing';
            e.preventDefault();
        };

        const onMouseMove = function (e) {
            if (!isDragging) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            const img = document.getElementById(`channel-preview-cover-img-${c}`);
            if (!img) return;

            const vpW = vp.clientWidth || 380;
            const vpH = vp.clientHeight || 200;
            const cfg = window.getChannelCoverConfig(c);
            const scale = (cfg.zoom || 100) / 100;
            const imgRatio = (img.naturalWidth || 16) / Math.max(1, (img.naturalHeight || 9));
            const vpRatio = vpW / Math.max(1, vpH);

            let baseW = imgRatio > vpRatio ? vpH * imgRatio : vpW;
            let baseH = imgRatio > vpRatio ? vpH : vpW / imgRatio;
            const renderW = baseW * scale;
            const renderH = baseH * scale;

            const maxMoveX = Math.max(0, renderW - vpW);
            const maxMoveY = Math.max(0, renderH - vpH);

            let newFx = initialFx;
            if (maxMoveX > 0) {
                const deltaFx = (dx / maxMoveX) * -100;
                newFx = Math.max(0, Math.min(100, Math.round(initialFx + deltaFx)));
            }

            let newFy = initialFy;
            if (maxMoveY > 0) {
                const deltaFy = (dy / maxMoveY) * -100;
                newFy = Math.max(0, Math.min(100, Math.round(initialFy + deltaFy)));
            }

            window.setChannelFocal(c, newFx, newFy);
        };

        const onMouseUp = function () {
            if (isDragging) {
                isDragging = false;
                vp.style.cursor = 'grab';
            }
        };

        if (typeof document !== 'undefined' && typeof document.addEventListener === 'function') {
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        }

        vp.onwheel = function (e) {
            e.preventDefault();
            const cfg = window.getChannelCoverConfig(c);
            const currentZoom = typeof cfg.zoom === 'number' ? cfg.zoom : 100;
            const delta = e.deltaY < 0 ? 5 : -5;
            const newZoom = Math.max(100, Math.min(250, currentZoom + delta));
            window.setChannelZoom(c, newZoom);
        };
    };

    window.setChannelFocal = function (channel, fx, fy) {
        const c = String(channel || '').toLowerCase();
        window.currentSyndicateCover.overrides = window.currentSyndicateCover.overrides || {};
        window.currentSyndicateCover.overrides[c] = window.currentSyndicateCover.overrides[c] || { focal_x: 50, focal_y: 50, zoom: 100, override_url: '' };
        window.currentSyndicateCover.overrides[c].focal_x = fx;
        window.currentSyndicateCover.overrides[c].focal_y = fy;
        window.updateChannelCoverTransform(c);
        window.updateDrawerFineTuneBadge();
    };

    window.setChannelZoom = function (channel, zoom) {
        const c = String(channel || '').toLowerCase();
        window.currentSyndicateCover.overrides = window.currentSyndicateCover.overrides || {};
        window.currentSyndicateCover.overrides[c] = window.currentSyndicateCover.overrides[c] || { focal_x: 50, focal_y: 50, zoom: 100, override_url: '' };
        window.currentSyndicateCover.overrides[c].zoom = zoom;
        window.updateChannelCoverTransform(c);
        window.updateDrawerFineTuneBadge();
    };

    window.updateChannelFocalXY = window.setChannelFocal;
    window.onChannelZoomChange = function (c, v) { window.setChannelZoom(c, parseInt(v, 10)); };
    window.onChannelFocalXChange = function (c, v) {
        const cfg = window.getChannelCoverConfig(c);
        window.setChannelFocal(c, parseInt(v, 10), cfg.focal_y || 50);
    };
    window.onChannelFocalYChange = function (c, v) {
        const cfg = window.getChannelCoverConfig(c);
        window.setChannelFocal(c, cfg.focal_x || 50, parseInt(v, 10));
    };

    window.resetChannelCropParams = function (channel) {
        const c = String(channel || '').toLowerCase();
        window.currentSyndicateCover.overrides = window.currentSyndicateCover.overrides || {};
        if (window.currentSyndicateCover.overrides[c]) {
            window.currentSyndicateCover.overrides[c].focal_x = 50;
            window.currentSyndicateCover.overrides[c].focal_y = 50;
            window.currentSyndicateCover.overrides[c].zoom = 100;
        }
        window.updateChannelCoverTransform(c);
        window.updateDrawerFineTuneBadge();
    };

    window.pickOverrideCoverForChannel = function (channel) {
        window._pickingCoverForChannel = String(channel || '').toLowerCase();
        if (typeof window.openSyndicateAssetPickerModal === 'function') window.openSyndicateAssetPickerModal();
    };

    window.applyChannelCoverOverride = function (channel, assetUrl) {
        const c = String(channel || '').toLowerCase();
        window.currentSyndicateCover.overrides = window.currentSyndicateCover.overrides || {};
        window.currentSyndicateCover.overrides[c] = window.currentSyndicateCover.overrides[c] || { focal_x: 50, focal_y: 50, zoom: 100, override_url: '' };
        window.currentSyndicateCover.overrides[c].override_url = assetUrl;
        const container = document.getElementById('syndicate-feed-card-slot');
        if (container) window.renderChannelCoverStudio(c, container, assetUrl);
        window.updateDrawerFineTuneBadge();
        if (typeof window.showToast === 'function') window.showToast(`已为 ${c.toUpperCase()} 设定专属独立封面海报`, 'success');
    };

    window.resetChannelCoverOverride = function (channel) {
        const c = String(channel || '').toLowerCase();
        if (window.currentSyndicateCover && window.currentSyndicateCover.overrides) delete window.currentSyndicateCover.overrides[c];
        const container = document.getElementById('syndicate-feed-card-slot');
        if (container) window.renderChannelCoverStudio(c, container);
        window.updateDrawerFineTuneBadge();
        if (typeof window.showToast === 'function') window.showToast(`已恢复 ${c.toUpperCase()} 跟随母图智能裁切`, 'info');
    };

    window.updateDrawerFineTuneBadge = function () {
        const overrides = (window.currentSyndicateCover && window.currentSyndicateCover.overrides) || {};
        const tunedCount = Object.keys(overrides).filter(k => {
            const o = overrides[k];
            return (o && (o.override_url || (typeof o.focal_y === 'number' && o.focal_y !== 50) || (typeof o.focal_x === 'number' && o.focal_x !== 50) || (typeof o.zoom === 'number' && o.zoom !== 100)));
        }).length;
        const slot = document.getElementById('syndicate-finetune-badge-slot');
        if (slot) {
            slot.innerHTML = tunedCount > 0
                ? `<span class="syndicate-finetune-badge">✨ 已精修 ${tunedCount} 端</span>`
                : '';
        }
    };
})();
