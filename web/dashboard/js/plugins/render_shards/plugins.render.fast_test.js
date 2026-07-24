/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Fast Test & Connectivity Log Terminal Shard
 * 职责：卡片快捷物理连通性测试、全自动保存、演练诊断日志终端抽屉与剪贴板一键复制。
 */

// 卡片上快捷一键测试连接
window.fastTestPluginConnectivity = async (id, category, btn) => {
    if (!btn || btn.disabled) return;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "⏳ 测试中...";
    btn.style.opacity = "0.7";

    const cardEl = btn.closest('.plugin-pod');
    const statusDot = cardEl ? cardEl.querySelector('.status-dot-mini') : null;
    const logTagEl = cardEl ? cardEl.querySelector('.log-tag') : null;
    let originalDotClass = "";
    if (statusDot) {
        originalDotClass = statusDot.className;
        statusDot.className = 'status-dot-mini pulsing-orange';
    }

    let settings = {};
    if (window.settingsData) {
        settings = {
            ...(window.settingsData.image_hosting?.[id] || {}),
            ...(window.settingsData.publish_control?.direct_upload?.[id] || {}),
            ...(window.settingsData.publish_control?.webhook_endpoints?.[id] || {}),
            ...(window.settingsData.syndication?.[id] || {})
        };
    }

    const currentDrawer = document.getElementById('plugin-drawer');
    const drawerTitle = document.getElementById('p-drawer-title');
    const isEditingThisPlugin = drawerTitle && drawerTitle.innerText && drawerTitle.innerText.toLowerCase().includes(id.toLowerCase());

    if (currentDrawer && isEditingThisPlugin) {
        currentDrawer.querySelectorAll('input, select, textarea').forEach(input => {
            const path = input.getAttribute('data-path') || input.name;
            if (path && input.value !== undefined) {
                const parts = path.split('.');
                const key = parts[parts.length - 1];
                let val = input.value;
                if (input.type === 'checkbox') val = input.checked;
                else if (input.type === 'number') val = parseFloat(input.value) || 0;
                settings[key] = val;
            }
        });
    }

    try {
        const fetchFunc = window.apiFetch || (async (url, init) => {
            const r = await fetch(url, init);
            return r.json();
        });

        const res = await fetchFunc('/api/plugins/dry-run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, parentId: category, settings })
        });

        btn.disabled = false;
        btn.innerText = originalText;
        btn.style.opacity = "1";

        if (res && res.success) {
            window.probePassState = window.probePassState || {};
            window.probePassState[id] = true;

            if (statusDot) statusDot.className = 'status-dot-mini healthy';
            if (logTagEl) {
                logTagEl.style.background = 'rgba(0, 255, 136, 0.08)';
                logTagEl.style.color = '#00ff88';
                logTagEl.style.border = '1px solid rgba(0, 255, 136, 0.2)';
                logTagEl.innerText = "🟢 通道畅通";
            }

            if (typeof window.savePluginConfig === 'function') {
                try { await window.savePluginConfig(true); } catch(e) {}
            }

            if (window.showToast) {
                window.showToast(`🟢 [${id.toUpperCase()}] 物理连接测试成功！已全自动保存配置。`, 'success');
            }
        } else {
            const errMsg = (res && (res.error || res.message || res.detail || (Array.isArray(res.logs) && res.logs.length ? res.logs.filter(l => typeof l === 'string' && (l.includes('ERROR') || l.includes('WARN'))).pop() : null))) || "物理通道无法连通，请检查凭据或代理参数。";
            
            if (res && res.logs) {
                window.lastTestLogs = window.lastTestLogs || {};
                window.lastTestLogs[id] = res.logs;
            }

            if (statusDot) statusDot.className = 'status-dot-mini blocked';
            if (logTagEl) {
                logTagEl.style.background = 'rgba(255, 77, 77, 0.12)';
                logTagEl.style.color = '#ff4d4d';
                logTagEl.style.border = '1px solid rgba(255, 77, 77, 0.3)';
                logTagEl.style.cursor = 'pointer';
                logTagEl.title = '点击查看完整调试日志';
                logTagEl.innerText = "❌ 连接失败 (查看日志)";
                logTagEl.onclick = (e) => {
                    e.stopPropagation();
                    window.showPluginLogDrawer(id, id.toUpperCase(), 'error', res ? res.logs : null);
                };
            }

            if (typeof window.focusErrorField === 'function') {
                for (let field of ['account_id', 'token', 'key', 'proxy', 'project_name', 'bucket']) {
                    if (errMsg.toLowerCase().includes(field)) {
                        window.focusErrorField(field);
                        break;
                    }
                }
            }

            if (window.showToast) {
                window.showToast(`❌ [${id.toUpperCase()}] 物理测试失败: ${errMsg}`, 'error');
            }
        }
    } catch (err) {
        btn.disabled = false;
        btn.innerText = originalText;
        btn.style.opacity = "1";
        if (statusDot && originalDotClass) statusDot.className = originalDotClass;
        if (window.showToast) {
            window.showToast(`❌ 测试异常: ${err.message || err}`, 'error');
        }
    }
};

// 物理测试连通性日志抽屉 (Connectivity Log Drawer)
window.showPluginLogDrawer = (id, title, status, logs) => {
    let drawer = document.getElementById('log-terminal-drawer');
    if (!drawer) {
        drawer = document.createElement('div');
        drawer.id = 'log-terminal-drawer';
        drawer.style.cssText = 'position: fixed; top: 0; right: -520px; width: 480px; height: 100vh; background: rgba(10, 10, 15, 0.95); backdrop-filter: blur(16px); border-left: 1px solid var(--glass-border); box-shadow: -10px 0 30px rgba(0,0,0,0.6); z-index: 9999; transition: right 0.35s cubic-bezier(0.16, 1, 0.3, 1); display: flex; flex-direction: column; font-family: monospace;';
        document.body.appendChild(drawer);
    }

    const rawLogs = logs || window.lastTestLogs?.[id] || ['暂无详细的诊断日志'];
    const logsArray = Array.isArray(rawLogs) ? rawLogs : (typeof rawLogs === 'string' ? [rawLogs] : [rawLogs]);
    const cleanLogTexts = [];
    const formattedLogs = logsArray.map(l => {
        let str = "";
        if (typeof l === 'object' && l !== null) {
            const msg = l.message || l.text || l.msg || l.detail || l.content || JSON.stringify(l);
            const level = l.level || l.type || '';
            str = level ? `[${String(level).toUpperCase()}] ${msg}` : String(msg);
        } else {
            str = String(l);
        }
        cleanLogTexts.push(str);

        if (str.includes('ERROR') || str.includes('❌') || str.includes('失败')) {
            return `<div style="color: #ff4d4d; margin-bottom: 3px; font-family: monospace;">${str}</div>`;
        } else if (str.includes('WARN') || str.includes('⚠️')) {
            return `<div style="color: #f59e0b; margin-bottom: 3px; font-family: monospace;">${str}</div>`;
        } else if (str.includes('SUCCESS') || str.includes('🟢') || str.includes('成功')) {
            return `<div style="color: #00ff88; margin-bottom: 3px; font-family: monospace;">${str}</div>`;
        }
        return `<div style="color: #d1d5db; margin-bottom: 3px; font-family: monospace;">${str}</div>`;
    }).join('');

    window.lastCleanLogText = cleanLogTexts.join('\n');

    drawer.innerHTML = `
        <div style="padding: 16px 20px; border-bottom: 1px solid var(--glass-border); display: flex; justify-content: space-between; align-items: center; background: rgba(0,0,0,0.3);">
            <div>
                <h3 style="margin: 0; font-size: 1.05rem; color: #fff;">📋 物理连通性日志</h3>
                <span style="font-size: 0.72rem; color: var(--text-dim);">${title || id.toUpperCase()} 通道演练诊断信息</span>
            </div>
            <button type="button" onclick="document.getElementById('log-terminal-drawer').style.right = '-520px'" style="background: transparent; border: none; color: #888; font-size: 1.2rem; cursor: pointer;">✕</button>
        </div>
        <div style="flex: 1; padding: 16px; overflow-y: auto; font-size: 0.78rem; line-height: 1.6; background: #07070a; color: #d1d5db; word-break: break-all;">
            ${formattedLogs}
        </div>
        <div style="padding: 12px 16px; border-top: 1px solid var(--glass-border); display: flex; gap: 8px; justify-content: flex-end; background: rgba(0,0,0,0.3);">
            <button type="button" onclick="window.copyLogTerminalContent(this)" style="font-size: 0.75rem; background: rgba(0, 242, 255, 0.1); border: 1px solid rgba(0, 242, 255, 0.3); color: var(--neon-cyan); padding: 5px 12px; border-radius: 6px; cursor: pointer; transition: all 0.25s ease;">📋 一键复制日志</button>
            <button type="button" onclick="document.getElementById('log-terminal-drawer').style.right = '-520px'" style="font-size: 0.75rem; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); color: #fff; padding: 5px 12px; border-radius: 6px; cursor: pointer;">关闭</button>
        </div>
    `;

    setTimeout(() => { drawer.style.right = '0px'; }, 10);
};

// 全局日志终端复制与即时微交互提示
window.copyLogTerminalContent = async (btn) => {
    const textToCopy = window.lastCleanLogText || '';
    try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(textToCopy);
        } else {
            const ta = document.createElement('textarea');
            ta.value = textToCopy;
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
        }

        if (btn) {
            const originalText = btn.innerHTML;
            const originalBg = btn.style.background;
            const originalBorder = btn.style.border;
            const originalColor = btn.style.color;

            btn.innerHTML = '✅ 已成功复制到剪贴板！';
            btn.style.background = 'rgba(0, 255, 136, 0.25)';
            btn.style.border = '1px solid rgba(0, 255, 136, 0.6)';
            btn.style.color = '#00ff88';

            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.style.background = originalBg;
                btn.style.border = originalBorder;
                btn.style.color = originalColor;
            }, 1500);
        }

        if (window.showToast) {
            window.showToast('🟢 诊断日志已成功复制到剪贴板！', 'success');
        }
    } catch(err) {
        if (btn) btn.innerText = '❌ 复制失败';
    }
};
