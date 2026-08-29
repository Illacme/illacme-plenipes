/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Cross-Plugin Diagnostics & Credentials Sensing Shard
 * 职责：全站配置 JSON 备份导出/导入、剪贴板 Token 特征智能感知回填与跨插件同源凭据复用算子。
 */

window.exportConfigBackup = () => {
    const data = window.settingsData || {};
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `illacme_plenipes_config_backup_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    if (window.showToast) window.showToast("🟢 配置备份文件导出成功！", "success");
};

window.importConfigBackup = (event) => {
    const file = event.target.files ? event.target.files[0] : null;
    if (!file) return;
    const reader = new FileReader();
    reader.onload = async (e) => {
        try {
            const parsed = JSON.parse(e.target.result);
            if (!parsed || typeof parsed !== 'object') throw new Error("无效的 JSON 配置格式");

            if (confirm("确认使用导入的文件恢复全站插件与平台配置？这将覆盖当前保存数据！")) {
                const fetchFunc = window.apiFetch || (async (url, init) => {
                    const r = await fetch(url, init);
                    return r.json();
                });
                const res = await fetchFunc('/api/system/config/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ config: parsed })
                });
                if (res && (res.status === 'success' || res.success)) {
                    window.settingsData = parsed;
                    if (window.loadPlugins) await window.loadPlugins(true);
                    if (window.showToast) window.showToast("🟢 成功导入配置备份！全站配置已自动同步。", "success");
                } else {
                    alert("导入保存失败: " + (res ? (res.error || res.message) : "未知错误"));
                }
            }
        } catch (err) {
            alert("解析配置文件失败: " + err.message);
        }
    };
    reader.readAsText(file);
};

// 剪贴板凭据智能感知与一秒导入 (Smart Clipboard Credentials Sense)
window.senseClipboardCredentials = async (isManualCall = false) => {
    try {
        if (!navigator.clipboard || !navigator.clipboard.readText) {
            if (isManualCall && window.showToast) window.showToast("当前浏览器未开放剪贴板读取权限", "warning");
            return;
        }
        const text = (await navigator.clipboard.readText() || '').trim();
        if (!text || text.length < 8) {
            if (isManualCall && window.showToast) window.showToast("未在剪贴板中检测到有效凭据字符串", "info");
            return;
        }

        // 🛡️ [凭据指纹精准检测] 避免将普通文本、日期 (如 2026-08-...) 或日志行误判为 API Key
        const isKnownKeyFormat = /^(ghp_|github_pat_|glpat-|wrangler_|Bearer |sk-|pk\.|key-|token-|AKIA|eyJ)/i.test(text);

        const activeDrawer = document.getElementById('plugin-drawer');
        const drawerTitle = document.getElementById('p-drawer-title');
        const isDrawerOpen = activeDrawer && activeDrawer.style.display !== 'none' && activeDrawer.offsetHeight > 0;

        if (isDrawerOpen) {
            if (isManualCall || isKnownKeyFormat) {
                const tokenInput = activeDrawer.querySelector('input[data-path*="token"], input[data-path*="api_key"], input[data-path*="secret_key"], input[data-path*="password"], input[name*="token"], input[type="password"]');
                if (tokenInput) {
                    tokenInput.value = text;
                    tokenInput.dispatchEvent(new Event('input', { bubbles: true }));
                    tokenInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    tokenInput.focus();
                    tokenInput.style.transition = 'all 0.3s';
                    tokenInput.style.outline = '2px solid #00ff88';
                    tokenInput.style.boxShadow = '0 0 15px rgba(0, 255, 136, 0.6)';
                    setTimeout(() => {
                        tokenInput.style.outline = '';
                        tokenInput.style.boxShadow = '';
                    }, 1500);

                    const pluginName = drawerTitle ? drawerTitle.innerText.replace('⚙️', '').trim() : '当前平台';
                    if (window.showToast) window.showToast(`🟢 已成功将剪贴板凭据智能填入 [${pluginName}]！`, "success");
                    return;
                }
            }
        }

        let detectedProvider = null;
        if (text.startsWith('ghp_') || text.startsWith('github_pat_')) {
            detectedProvider = { id: 'github_pages', name: 'GitHub Token', category: 'hosting' };
        } else if (text.startsWith('glpat-')) {
            detectedProvider = { id: 'gitlab_pages', name: 'GitLab Token', category: 'hosting' };
        } else if (text.startsWith('wrangler_')) {
            detectedProvider = { id: 'cloudflare_pages', name: 'Cloudflare Token', category: 'hosting' };
        } else if (text.startsWith('Bearer ')) {
            detectedProvider = { id: 'lsky_pro', name: 'Lsky Pro Token', category: 'image_hosting' };
        }

        if (detectedProvider && typeof window.openPluginDrawer === 'function') {
            window.openPluginDrawer(detectedProvider.id, detectedProvider.category);
            setTimeout(() => {
                const drawer = document.getElementById('plugin-drawer');
                if (drawer) {
                    const input = drawer.querySelector('input[data-path*="token"], input[data-path*="api_key"], input[type="password"]');
                    if (input) {
                        input.value = text;
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.focus();
                        if (window.showToast) window.showToast(`🟢 已自动打开 [${detectedProvider.name}] 并回填凭据！`, "success");
                    }
                }
            }, 200);
        } else {
            // 只有当确为 Key 格式且用户手动触发时，才弹窗提示捕获
            if (isKnownKeyFormat && isManualCall && window.showToast) {
                window.showToast(`💡 已从剪贴板捕获 Key (${text.slice(0, 8)}...)，请打开目标插件抽屉自动填充。`, "info");
            }
        }
    } catch (err) {
        if (isManualCall && window.showToast) window.showToast(`读取剪贴板提示: ${err.message || err}`, "warning");
    }
};

// 全站跨插件链路诊断算子
window.runCrossPluginDiagnostics = () => {
    const issues = [];
    const cfgData = window.settingsData || {};
    const plugins = window.allPlugins || [];
    const currentCat = window.activePluginCategory || 'all';

    plugins.forEach(p => {
        // 🎯 [精准分类过滤] 如果用户选中了特定的子菜单 Tab，只处理当前子菜单下的插件
        if (currentCat !== 'all') {
            let matchesCategory = false;
            if (currentCat === 'ingress') {
                matchesCategory = (p.category === 'ingress_source' || p.category === 'ingress_dialect');
            } else {
                matchesCategory = (p.category === currentCat);
            }
            if (!matchesCategory) return;
        }

        // ✅ [V80.2] 仅当插件在当前品牌已激活 (is_in_use) 时才提示凭据缺失
        // 未激活的插件配置不完整不影响任何操作，提示是无效噪声
        if (p.is_enabled && p.is_in_use && p.is_manageable && ['hosting', 'image_hosting', 'publisher', 'notification'].includes(p.category)) {
            let platformCfg = {};
            if (p.category === 'hosting') platformCfg = cfgData.publish_control?.direct_upload?.[p.id] || {};
            else if (p.category === 'image_hosting') platformCfg = cfgData.image_hosting?.[p.id] || {};
            else if (p.category === 'notification') platformCfg = cfgData.publish_control?.webhook_endpoints?.[p.id] || {};
            else platformCfg = cfgData.syndication?.[p.id] || {};

            // 按分类使用准确的操作动词，避免「分发」一词误用于托管与图床类插件
            const categoryVerbMap = {
                'hosting': '站点部署失败',
                'image_hosting': '图片上传失败',
                'notification': '通知推送失败',
                'publisher': '内容分发失败'
            };
            const failVerb = categoryVerbMap[p.category] || '操作失败';

            if (window.isPluginCredentialReady) {
                const cred = window.isPluginCredentialReady(p.id, p.category, platformCfg);
                if (!cred.ready && !['sftp', 'local_fs'].includes(p.id)) {
                    issues.push({
                        type: 'warning',
                        title: `⚠️ [${p.name || p.id.toUpperCase()}] 凭据待补全`,
                        desc: `已在当前品牌启用但凭据尚未配置完整，发布时可能导致${failVerb}。`,
                        actionText: '⚙️ 立即补全',
                        action: `openPluginConfig('${p.id}', '${p.category}')`
                    });
                }
            } else {
                const tokenVal = platformCfg.token || platformCfg.url || platformCfg.api_key || platformCfg.access_token || platformCfg.api_token || platformCfg.secret_key || platformCfg.integration_token || platformCfg.cookie || platformCfg.password || platformCfg.private_key || '';
                if (!tokenVal && !['sftp', 'local_fs'].includes(p.id)) {
                    issues.push({
                        type: 'warning',
                        title: `⚠️ [${p.name || p.id.toUpperCase()}] 凭据待补全`,
                        desc: `已在当前品牌启用但凭据尚未配置完整，发布时可能导致${failVerb}。`,
                        actionText: '⚙️ 立即补全',
                        action: `openPluginConfig('${p.id}', '${p.category}')`
                    });
                }
            }
        }
    });


    const ghPagesToken = cfgData.publish_control?.direct_upload?.github_pages?.token || cfgData.publish_control?.direct_upload?.github_pages?.access_token;
    const ghImgToken = cfgData.image_hosting?.github?.token || cfgData.image_hosting?.github?.access_token;

    // 💡 同源图床复用建议仅在全部或图床分类时触发
    if ((currentCat === 'all' || currentCat === 'image_hosting') && ghPagesToken && !ghImgToken) {
        issues.push({
            type: 'info',
            title: `💡 [GitHub 图床] 可复用 GitHub Pages 凭据`,
            desc: `检测到 GitHub Pages 已配置有效 Token，建议一键共享给 GitHub 图床。`,
            actionText: '📋 一键同源复用',
            action: `window.autoReuseSameOriginCredential('${ghPagesToken}', 'github', 'image_hosting')`
        });
    }

    if (issues.length === 0) return '';

    const firstIssue = issues[0];
    const isWarning = (firstIssue.type === 'warning');

    return `
        <div class="cross-plugin-diagnostics-banner" style="width: 100%; box-sizing: border-box; margin-bottom: 16px; padding: 12px 16px; border-radius: 10px; border: 1px dashed ${isWarning ? 'rgba(255, 183, 0, 0.4)' : 'var(--neon-cyan)'}; background: ${isWarning ? 'rgba(255, 183, 0, 0.06)' : 'rgba(0, 242, 255, 0.05)'}; display: flex; align-items: center; gap: 16px;">
            <div style="min-width: max-content; flex-shrink: 0; display: flex; flex-direction: column; gap: 6px;">
                <span style="font-size: 0.85rem; font-weight: 700; color: ${isWarning ? '#ffb700' : 'var(--neon-cyan)'}; white-space: nowrap;">${firstIssue.title}</span>
                <div>
                    <button type="button" onclick="${firstIssue.action}" style="font-size: 0.72rem; background: ${isWarning ? 'rgba(255, 183, 0, 0.15)' : 'rgba(0, 242, 255, 0.12)'}; border: 1px solid ${isWarning ? 'rgba(255, 183, 0, 0.35)' : 'rgba(0, 242, 255, 0.3)'}; color: ${isWarning ? '#ffb700' : 'var(--neon-cyan)'}; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-weight: 600;">${firstIssue.actionText}</button>
                </div>
            </div>
            <div style="flex: 1; font-size: 0.78rem; color: var(--text-dim); line-height: 1.5;">
                ${firstIssue.desc}
            </div>
        </div>
    `;
};

// 自动快速同源凭据复用算子
window.autoReuseSameOriginCredential = (sourceToken, targetId, targetCategory) => {
    if (typeof window.openPluginDrawer === 'function') {
        window.openPluginDrawer(targetId, targetCategory);
        setTimeout(() => {
            const drawer = document.getElementById('plugin-drawer');
            if (drawer && sourceToken) {
                const input = drawer.querySelector('input[name*="token"], input[name*="access_token"], input[data-path*="token"]');
                if (input) {
                    input.value = sourceToken;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    input.focus();
                    if (window.showToast) window.showToast("✅ 已全自动同步并填入同源 Token！", "success");
                }
            }
        }, 150);
    } else if (typeof window.openPluginConfig === 'function') {
        window.openPluginConfig(targetId, targetCategory);
        setTimeout(() => {
            const drawer = document.getElementById('plugin-drawer');
            if (drawer && sourceToken) {
                const input = drawer.querySelector('input[name*="token"], input[name*="access_token"], input[data-path*="token"]');
                if (input) {
                    input.value = sourceToken;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    input.focus();
                    if (window.showToast) window.showToast("✅ 已全自动同步并填入同源 Token！", "success");
                }
            }
        }, 150);
    }
};

window.addEventListener('focus', () => {
    const pluginsPanel = document.getElementById('view-plugins');
    if (pluginsPanel && pluginsPanel.classList.contains('active')) {
        window.senseClipboardCredentials();
    }
});
