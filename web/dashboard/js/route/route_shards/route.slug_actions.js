/**
 * 🛣️ [V1.0] Route & Slug Sandbox - Actions & Vault Prober Shard
 * 职责：别名策略视觉卡片切换、模式锁定提示、配置还原/保存/发布动作、金库真实原稿列表加载与本机 Finder 定位唤醒。
 * 对应重构拆分协议：SOP-01/SOP-02 模板一合规物理平移。
 */

(function () {
    'use strict';

    window.notifySlugLockedByTheme = function (mode, theme) {
        const labels = { 'flat': '极简根目录', 'prefix': '智能 SEO 前缀' };
        const modeName = labels[mode] || mode;
        const themeUpper = (theme || '当前主题').toUpperCase();
        const msg = `⚠️ 当前主题【${themeUpper}】采用文件树强绑定路由，不支持【${modeName}】，系统已锁定为【📂 目录树复刻】以保障最佳兼容。`;
        if (typeof showNotification === 'function') {
            showNotification(msg, 'warning');
        } else if (typeof showToast === 'function') {
            showToast(msg, 'warning');
        }
        if (typeof addAudit === 'function') {
            addAudit(msg);
        }
    };

    window.selectSlugDirModeCard = function (mode) {
        const settings = window.settingsData || {};
        const activeTheme = (settings.active_theme || 'universal').toLowerCase();
        const isNativeTheme = ['sovereign', 'universal', 'default'].includes(activeTheme);
        if (!isNativeTheme && mode !== 'nested') {
            window.notifySlugLockedByTheme(mode, activeTheme);
            return;
        }

        if (!settings.translation) {
            settings.translation = {};
        }
        settings.translation.slug_dir_mode = mode;

        // UI 卡片激活状态同步 (基于 CSS class，不再内联写入颜色，确保白天/黑夜主题自适应)
        const cards = document.querySelectorAll('.slug-dir-card');
        cards.forEach(card => {
            const isMatch = (card.getAttribute('data-mode') === mode);
            card.classList.toggle('active', isMatch);
            const radio = card.querySelector('.slug-radio-indicator');
            if (radio) {
                radio.innerText = isMatch ? '✓' : '';
            }
        });

        if (typeof window.checkSettingsDirty === 'function') {
            window.checkSettingsDirty();
        }

        if (typeof addAudit === 'function') {
            const labels = { 'flat': '极简根目录', 'prefix': '智能 SEO 前缀', 'nested': '目录树复刻' };
            addAudit(`📝 网址路径形态已选择为【${labels[mode] || mode}】(沙盒实时推导中)`);
        }

        // 触发沙盒实时推导更新
        if (typeof window.updateSlugSandboxPreview === 'function') {
            window.updateSlugSandboxPreview();
        }
    };

    window.realManuscriptCache = [];

    // 🚀 物理拉取金库全量真实原稿注入下拉框
    window.populateSandboxRealFiles = async function () {
        const selector = document.getElementById('sandbox-file-select');
        if (!selector) return;

        try {
            let manuscripts = window.realManuscriptCache;
            if (!manuscripts || manuscripts.length === 0) {
                const res = await apiFetch('/api/vault/list');
                if (res && res.manuscripts) {
                    manuscripts = res.manuscripts;
                    window.realManuscriptCache = manuscripts;
                }
            }

            if (manuscripts && manuscripts.length > 0) {
                selector.innerHTML = '';
                manuscripts.forEach(m => {
                    const path = m.rel_path || m.path;
                    if (!path) return;
                    const opt = document.createElement('option');
                    opt.value = path;
                    opt.text = `📄 ${path}`;
                    opt.dataset.slug = m.slug || '';
                    opt.dataset.title = m.title || '';
                    selector.appendChild(opt);
                });

                // 附带自定义输入项
                const customOpt = document.createElement('option');
                customOpt.value = '_custom';
                customOpt.text = '✏️ 手动输入自定义相对路径...';
                selector.appendChild(customOpt);

                // 刷新计算
                if (typeof window.updateSlugSandboxPreview === 'function') {
                    window.updateSlugSandboxPreview();
                }
            }
        } catch (e) {
            console.warn("Populate sandbox real files warning:", e);
        }
    };

    // 🚀 物理唤醒本机 Finder / 文件资源管理器
    window.openLocalWorkspaceFolder = async function (relPath) {
        try {
            const res = await apiFetch('/api/vault/open-local-folder', {
                method: 'POST',
                body: JSON.stringify({ rel_path: relPath })
            });
            if (res && res.status === 'ok') {
                if (typeof addAudit === 'function') addAudit(`📂 已成功物理唤醒本机 Finder 定位至: ${res.opened_path}`);
            } else {
                console.warn("Open local folder response:", res);
            }
        } catch (e) {
            console.error("Open local folder error:", e);
        }
    };

    /**
     * ↩️ 撤销试选，将网址路径形态一键还原为当前线上生效配置
     */
    window.revertSlugDirMode = function () {
        let initialDirMode = 'nested';
        if (window.initialSettingsState) {
            try {
                const initObj = JSON.parse(window.initialSettingsState);
                initialDirMode = initObj['translation.slug_dir_mode'] || initObj.translation?.slug_dir_mode || 'nested';
            } catch (e) { }
        }
        if (!window.settingsData) window.settingsData = {};
        if (!window.settingsData.translation) window.settingsData.translation = {};
        window.settingsData.translation.slug_dir_mode = initialDirMode;
        window.selectSlugDirModeCard(initialDirMode);
        if (typeof window.showToast === 'function') {
            const labels = { 'flat': '极简根目录', 'prefix': '智能 SEO 前缀', 'nested': '目录树复刻' };
            window.showToast(`↩️ 已还原为生效配置【${labels[initialDirMode] || initialDirMode}】`, 'info');
        }
    };

    /**
     * 💾 仅保存当前路径形态配置
     */
    window.saveSlugDirModeConfig = async function () {
        if (typeof window.saveSettings === 'function') {
            await window.saveSettings();
        }
    };

    /**
     * 🚀 保存配置并立即触发全网发布
     */
    window.saveAndPublishSlugDirMode = async function () {
        if (typeof window.saveSettings === 'function') {
            await window.saveSettings();
        }
        const pubBtn = document.getElementById('btn-publish') || document.querySelector('[onclick*="publish"]');
        if (pubBtn) {
            pubBtn.click();
        } else if (typeof window.triggerPublish === 'function') {
            window.triggerPublish();
        }
    };

    /**
     * 🚀 物理即时探测与重新发布提醒机制卡片渲染
     */
    window.renderSlugProbeStatus = async function (previewStatusBox, sourceInfo, dirMode) {
        if (!previewStatusBox || !sourceInfo) return;

        previewStatusBox.innerHTML = `<span style="color: #bbb; font-size: 0.72rem;">⏳ 正在感应线上多语言云端可达状态...</span>`;

        let isOnlineExist = false;
        try {
            const probeUrl = sourceInfo.fullWebUrl.includes('?') ? `${sourceInfo.fullWebUrl}&_t=${Date.now()}` : `${sourceInfo.fullWebUrl}?_t=${Date.now()}`;
            const res = await fetch(probeUrl, { method: 'HEAD', cache: 'no-store' });
            if (res.status === 200) {
                isOnlineExist = true;
            }
        } catch (e) {
            isOnlineExist = false;
        }

        const modeLabels = { 'flat': '极简根目录', 'prefix': '智能 SEO 前缀', 'nested': '目录树复刻' };
        const currentModeName = modeLabels[dirMode] || dirMode;

        // 判定是否与磁盘已保存的初始状态偏离
        let initialDirMode = 'nested';
        if (window.initialSettingsState) {
            try {
                const initObj = JSON.parse(window.initialSettingsState);
                initialDirMode = initObj['translation.slug_dir_mode'] || initObj.translation?.slug_dir_mode || 'nested';
            } catch (e) { }
        }
        const isModeChanged = (dirMode !== initialDirMode);

        if (isModeChanged) {
            previewStatusBox.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(255, 180, 0, 0.08); border: 1.5px solid #d4a72c; padding: 12px 14px; border-radius: 8px; margin-top: 12px; gap: 12px; flex-wrap: wrap;">
                    <div style="display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 240px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="color: #ffb400; font-weight: 700; font-size: 0.82rem;">⚠️ 检测到网址路径形态变更（当前试选：【${currentModeName}】）</span>
                            <span style="background: rgba(255, 180, 0, 0.15); color: #ffb400; font-size: 0.65rem; padding: 2px 6px; border-radius: 3px; font-weight: 600;">生产结构变更</span>
                        </div>
                        <div style="font-size: 0.72rem; line-height: 1.45; opacity: 0.85;">
                            💡 修改路径形态将重塑全站所有 HTML 落盘结构、公开 URL 与 Sitemap。为保护生产环境安全，请确认保存或一键重新发布。
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px; flex-shrink: 0;">
                        <button type="button" class="mini-btn secondary-btn" onclick="window.revertSlugDirMode();" style="padding: 6px 12px; font-size: 0.74rem; border-radius: 5px; cursor: pointer;" title="撤销试选，恢复为当前线上生效配置">
                            ↩️ 还原初始配置
                        </button>
                        <button type="button" class="mini-btn glow-btn" onclick="window.saveSlugDirModeConfig();" style="padding: 6px 12px; font-size: 0.74rem; border-radius: 5px; cursor: pointer; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);">
                            💾 仅保存配置
                        </button>
                        <button type="button" class="mini-btn primary-btn glow-btn" onclick="window.saveAndPublishSlugDirMode();" style="padding: 6px 14px; font-size: 0.74rem; border-radius: 5px; font-weight: 600; cursor: pointer;">
                            🚀 保存并立即发布
                        </button>
                    </div>
                </div>
            `;
        } else if (isOnlineExist) {
            previewStatusBox.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(0, 255, 170, 0.08); border: 1px solid rgba(0, 255, 170, 0.3); padding: 8px 12px; border-radius: 6px; margin-top: 10px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #00ffaa; font-weight: 600; font-size: 0.78rem;">🟢 线上母语版本已就绪 (200 OK)</span>
                        <span style="color: #aaa; font-size: 0.72rem;">多语种译本已在 GitHub Pages 云端节点部署完成</span>
                    </div>
                </div>
            `;
        } else {
            previewStatusBox.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(0, 242, 255, 0.05); border: 1px solid rgba(0, 242, 255, 0.2); padding: 10px 12px; border-radius: 6px; margin-top: 10px;">
                    <div style="display: flex; flex-direction: column; gap: 3px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="color: var(--accent-secondary, #00f2fe); font-weight: 600; font-size: 0.78rem;">✨ 当前形态已生效【${currentModeName}】</span>
                            <span style="color: #888; font-size: 0.72rem;">推导演算已就绪</span>
                        </div>
                        <div style="color: var(--text-dim); font-size: 0.72rem; line-height: 1.4;">
                            💡 点击卡片可自由试看其他组织形态；点击「🚀 重新发布全站」可刷新全量静态产物。
                        </div>
                    </div>
                    <button class="mini-btn glow-btn primary-btn" onclick="if(document.getElementById('btn-publish')) document.getElementById('btn-publish').click();" style="padding: 5px 12px; font-size: 0.75rem; border-radius: 4px; font-weight: 600; cursor: pointer; flex-shrink: 0; margin-left: 10px;">
                        🚀 重新发布全站
                    </button>
                </div>
            `;
        }
    };

})();
