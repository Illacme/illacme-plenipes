/**
 * 🚀 Illacme Plenipes Dashboard Core - Publish Precheck & Confirmation Shard
 * 职责：出版前置看门狗挂起、脏数据落盘预存、环境与资产预检接口调用及精美确认弹窗渲染。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
 */

window.runPublishPrecheck = async function (force = false, activeId = 'default', bypassCompletedCheck = false) {
    // 🚀 [V78.6] 挂起监控狗：防止下面强制落盘时触发自动同步抢占预检
    try {
        await apiFetch('/api/system/watchdog/suspend', { method: 'POST' });
    } catch (e) {
        console.warn('[Publish] 挂起监控狗失败:', e);
    }

    // 强制将编辑器里的脏数据保存落盘，避免预检扫不到最新修改
    if (typeof window.saveDocument === 'function') {
        try {
            await window.saveDocument();
        } catch (e) {
            console.warn('[Publish] 预保存文档失败:', e);
        }
    }

    if (typeof window.addAudit === 'function') {
        window.addAudit('正在进行发布前置预检...', 'info');
    }

    let precheckRes = null;
    // 🚀 [V78.5] 双段式预检：执行物理环境与资产完整性核查
    if (!force) {
        precheckRes = await apiFetch('/api/system/sync/precheck', { method: 'POST' });
        if (precheckRes) {
            // 强阻断 (Critical)
            if (precheckRes.critical_errors && precheckRes.critical_errors.length > 0) {
                if (window.Swal) {
                    await window.Swal.fire({
                        title: '🚨 致命环境损坏',
                        html: `无法启动发布流水线，发现严重环境问题：<br><br><div style="text-align:left;color:#d33;font-size:0.9em;background:#fee;padding:10px;border-radius:4px;">${precheckRes.critical_errors.join('<br>')}</div><br>请修复后重试！`,
                        icon: 'error',
                        confirmButtonText: '我知道了',
                        confirmButtonColor: '#3085d6'
                    });
                }
                if (typeof window.addAudit === 'function') window.addAudit('预检失败：系统环境损坏，已强行拦截发布！', 'error');
                try { await apiFetch('/api/system/watchdog/resume', { method: 'POST' }); } catch (e) {}
                return { proceed: false, precheckRes };
            }

            // 🚀 如果后端账本记录表明当前品牌已完成过初始同步，且前端未绕过已完成校验，直接切至终端重新发布界面
            if (!bypassCompletedCheck && precheckRes.has_synced) {
                localStorage.setItem(`sync_completed_${activeId}`, 'true');
                localStorage.setItem('sync_completed', 'true');
                const modal = document.getElementById('terminal-modal');
                if (modal) {
                    modal.style.display = 'flex';
                    const title = document.getElementById('terminal-title');
                    if (title) title.innerText = '🚀 全域全息同步 (已完成)';
                    const toolbar = document.getElementById('terminal-toolbar');
                    if (toolbar) toolbar.style.display = 'none';

                    const out = document.getElementById('terminal-output');
                    if (out) {
                        out.innerHTML = '';
                        modal.dataset.context = 'republish_prompt';
                    }

                    if (typeof window.appendTerminalLog === 'function') {
                        window.appendTerminalLog('📡 [系统] 检测到当前同步已 100% 完成。', '#00ff88');
                        window.appendTerminalLog('💡 您可以点击下方按钮选择“重新发布”以强行重新生成和分发所有资产。', '#38bdf8');
                    }

                    const okBtn = document.getElementById('btn-terminal-ok');
                    if (okBtn) okBtn.style.display = 'none';

                    const abortBtn = document.getElementById('btn-terminal-abort');
                    if (abortBtn) abortBtn.style.display = 'none';

                    const republishBtn = document.getElementById('btn-terminal-republish');
                    if (republishBtn) republishBtn.style.display = 'block';

                    const statusEl = document.getElementById('terminal-status');
                    if (statusEl) {
                        statusEl.innerText = 'COMPLETED';
                        statusEl.className = 'online';
                    }
                }
                if (typeof window.addAudit === 'function') {
                    window.addAudit('网站已处于100%发布状态，已弹出重新发布选项。', 'info');
                }
                try { await apiFetch('/api/system/watchdog/resume', { method: 'POST' }); } catch (e) {}
                return { proceed: false, precheckRes };
            }
        }
    }

    // 🚀 [Sovereign-UX] 预检完美通过或仅有 warnings 时，统一先弹出精美的确认弹窗
    const mode = (precheckRes && precheckRes.publishing_mode) || (window.settingsData && window.settingsData.governance && window.settingsData.governance.publishing_mode) || 'basic';
    const modeText = mode === 'basic' ? '基础模式 (Basic) — 多语言透传' :
                     mode === 'enhanced' ? '增强模式 (Enhanced) — SEO字段AI翻译' : '全球出版模式 (Global) — 全量AI翻译';

    const hasWarnings = precheckRes && precheckRes.warnings && precheckRes.warnings.length > 0;
    const statusHtml = hasWarnings ?
        `<span style="color: #e67e22; font-weight: bold;">⚠️ 预检警告 (有 ${precheckRes.warnings.length} 处资产丢失)</span>` :
        `<span style="color: #00ff88; font-weight: bold;">🟢 物理环境完美就绪 (0 资产丢失)</span>`;

    let warningDetailsHtml = '';
    if (hasWarnings) {
        const warningsListHtml = precheckRes.warnings.map(w => {
            const docPath = w.doc_id ? (w.doc_id.startsWith('*') ? w.doc_id.substring(1) : w.doc_id) : '';
            const docLinkHtml = docPath && docPath !== 'Unknown'
                ? `<a href="javascript:void(0)" onclick="if (window.Swal) window.Swal.close(); if (typeof window.openEditor === 'function') { window.openEditor('${docPath.replace(/'/g, "\\\\'")}') } else { console.warn('openEditor not found') }" style="color: var(--accent-secondary, #3085d6); text-decoration: underline; cursor: pointer; font-weight: bold;">${docPath}</a>`
                : '未知文档';
            return `<div style="padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.06); text-align: left; word-break: break-all; line-height: 1.4;">
                <span style="color: #e67e22; font-weight: 600; font-family: monospace;">• ${w.asset}</span>
                <br>
                <span style="font-size: 0.85em; color: #888; padding-left: 10px;">引用源: ${docLinkHtml}</span>
            </div>`;
        }).join('');

        warningDetailsHtml = `
            <br>
            <details style="text-align: left; background: rgba(0, 0, 0, 0.2); padding: 10px; border-radius: 6px; border: 1px solid rgba(255, 255, 255, 0.08);">
                <summary style="cursor: pointer; font-weight: bold; color: #3085d6; outline: none; user-select: none;">
                    查看具体丢失的 ${precheckRes.warnings.length} 处资产清单
                </summary>
                <div style="max-height: 120px; overflow-y: auto; margin-top: 8px; font-size: 0.9em; color: #ccc;">
                    ${warningsListHtml}
                </div>
            </details>
        `;
    }

    const confirmHtml = `
        <div style="text-align: left; font-size: 0.95rem; line-height: 1.6; color: #e0e0e0;">
            <p style="margin-bottom: 12px; color: #aaa;">启动全域全息同步流水线，系统将执行全量静态页面生成，并分发对齐至已启用的第三方渠道：</p>
            <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 14px; margin-bottom: 16px; backdrop-filter: blur(10px);">
                <div style="margin-bottom: 10px; display: flex; align-items: center;">
                    <span style="color: #00ff88; font-weight: bold; width: 90px; display: inline-block;">⚙️ 出版模式:</span>
                    <span style="color: var(--text-bright, #ffffff); font-weight: 500;">${modeText}</span>
                </div>
                <div style="margin-bottom: 10px; display: flex; align-items: center;">
                    <span style="color: #00ff88; font-weight: bold; width: 90px; display: inline-block;">🛡️ 预检状态:</span>
                    <span>${statusHtml}</span>
                </div>
                <div style="display: flex; align-items: flex-start;">
                    <span style="color: #00ff88; font-weight: bold; width: 90px; display: inline-block;">📡 渠道矩阵:</span>
                    <span style="color: var(--text-bright, #ffffff); font-weight: 500; flex: 1;">一键发布至已开启的托管平台与社媒分发渠道</span>
                </div>
            </div>
            ${warningDetailsHtml}
            <p style="text-align: center; font-weight: bold; margin-top: 15px; color: var(--text-bright, #ffffff); font-size: 1.05rem;">🚀 确定要启动全域发布点火吗？</p>
        </div>
    `;

    if (!force) {
        if (window.Swal) {
            const result = await window.Swal.fire({
                title: '🚀 全域全息发布就绪预检',
                html: confirmHtml,
                icon: hasWarnings ? 'warning' : 'info',
                showCancelButton: true,
                confirmButtonText: '🚀 确认点火发布',
                cancelButtonText: '取消并返回',
                confirmButtonColor: '#00ff88',
                cancelButtonColor: '#d33',
                background: 'rgba(20, 20, 25, 0.95)',
                color: '#fff',
                customClass: {
                    popup: 'glass-modal-swal'
                }
            });

            if (!result.isConfirmed) {
                if (typeof window.addAudit === 'function') window.addAudit('已取消全域发布。', 'info');
                try { await apiFetch('/api/system/watchdog/resume', { method: 'POST' }); } catch (e) {}
                return { proceed: false, precheckRes };
            }
        } else {
            const ok = confirm(`全域同步准备完毕。模式: ${modeText}。确定要执行发布吗？`);
            if (!ok) {
                try { await apiFetch('/api/system/watchdog/resume', { method: 'POST' }); } catch (e) {}
                return { proceed: false, precheckRes };
            }
        }
    }

    return { proceed: true, precheckRes };
};
