/**
 * 📋 [V125.2] Illacme Plenipes - Hosting Deploy Log Drawer
 * 职责：全站托管部署实时流水、终端控制台日志与通道状态卡片交互。
 * 🛡️ [SOP-02 模块规范] 单文件严格保持在 300 行以内。
 */

window._currentHostingLogBatchId = null;
window._hostingLogPollTimer = null;

function _ensureHostingLogDrawerDom() {
    if (document.getElementById('hosting-log-drawer')) return;
    const html = `
        <div id="hosting-log-backdrop" class="vault-drawer-backdrop" onclick="window.closeHostingDeployLogDrawer()"></div>
        <div id="hosting-log-drawer" class="glass-panel drawer-shell hosting-logs-drawer">
            <div class="drawer-header-row">
                <div class="drawer-header-title-group" style="display: flex; align-items: center; gap: 8px;">
                    <h3 class="drawer-header-title" style="margin: 0; font-size: 1.05rem;">📋 部署控制台流水</h3>
                    <span id="hlog-batch-code" class="batch-short-code mono" title="点击复制批次号" onclick="window.copyHostingLogBatchId()">#--</span>
                    <span id="hlog-status-badge" class="ledger-badge badge-idle">--</span>
                </div>
                <button type="button" class="drawer-close-cross" onclick="window.closeHostingDeployLogDrawer()">×</button>
            </div>
            <div class="hlog-meta-strip">
                <div class="hlog-meta-item" id="hlog-source-item" style="display: none;"><span class="k">触发原稿:</span><span id="hlog-source" class="v highlight" style="max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="">--</span></div>
                <div class="hlog-meta-item"><span class="k">装帧主题:</span><span id="hlog-theme" class="v highlight">--</span></div>
                <div class="hlog-meta-item"><span class="k">网页数量:</span><span id="hlog-pages" class="v">--</span></div>
                <div class="hlog-meta-item"><span class="k">内容体积:</span><span id="hlog-size" class="v">--</span></div>
                <div class="hlog-meta-item"><span class="k">执行用时:</span><span id="hlog-dur" class="v">--</span></div>
            </div>
            <div class="drawer-body hlog-drawer-body">
                <div class="hlog-section-title"><span>🌐 平台通道推送明细</span></div>
                <div id="hlog-targets-list" class="hlog-targets-grid">
                    <div style="color: var(--text-muted); font-size: 0.8rem; padding: 6px 0;">正在解析目标渠道...</div>
                </div>
                <div class="hlog-section-title" style="margin-top: 14px; display: flex; justify-content: space-between; align-items: center;">
                    <span>💻 控制台输出 (STDOUT / STDERR)</span>
                    <div class="hlog-terminal-actions">
                        <button class="mini-btn" onclick="window.copyHostingDeployLogs()" title="复制全部控制台日志">📋 复制日志</button>
                        <button class="mini-btn" onclick="window.refreshHostingDeployLogs()" title="刷新日志">🔄 刷新</button>
                    </div>
                </div>
                <div class="hlog-terminal-box">
                    <div class="hlog-terminal-header">
                        <div class="hlog-terminal-dots"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span></div>
                        <span class="hlog-terminal-title mono">deploy_stdout.log</span>
                        <span id="hlog-live-indicator" class="hlog-live-tag" style="display: none;">● 实时传输中</span>
                    </div>
                    <pre id="hlog-terminal-content" class="hlog-terminal-pre mono">正在读取部署流水...</pre>
                </div>
            </div>
            <div class="drawer-footer hlog-footer drawer-footer-row">
                <button class="secondary-btn" style="flex: 1;" onclick="window.closeHostingDeployLogDrawer()">关闭</button>
                <button class="primary-btn glow-btn" id="hlog-redeploy-btn" style="flex: 2;" onclick="window.redeployCurrentHostingBatch();">
                    <span class="btn-icon">🔄</span> 再次发布网站
                </button>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', html);
}

window.openHostingDeployLogDrawer = async function (batchId) {
    if (!batchId) return;
    window._currentHostingLogBatchId = batchId;
    _ensureHostingLogDrawerDom();

    const drawer = document.getElementById('hosting-log-drawer');
    const backdrop = document.getElementById('hosting-log-backdrop');
    if (drawer) {
        drawer.classList.add('is-open');
        drawer.style.right = '0px';
    }
    if (backdrop) {
        backdrop.classList.add('is-open');
        backdrop.style.display = 'block';
    }

    const shortId = batchId.includes('_') ? '#' + batchId.split('_').pop() : '#' + batchId.slice(-6);
    const codeEl = document.getElementById('hlog-batch-code');
    if (codeEl) codeEl.innerText = shortId;
    const pre = document.getElementById('hlog-terminal-content');
    if (pre) pre.innerText = '正在调取控制台部署流水...';

    await window.refreshHostingDeployLogs();
};

window.closeHostingDeployLogDrawer = function () {
    if (window._hostingLogPollTimer) {
        clearInterval(window._hostingLogPollTimer);
        window._hostingLogPollTimer = null;
    }
    const drawer = document.getElementById('hosting-log-drawer');
    const backdrop = document.getElementById('hosting-log-backdrop');
    if (drawer) {
        drawer.classList.remove('is-open');
        drawer.style.right = '-640px';
    }
    if (backdrop) {
        backdrop.classList.remove('is-open');
        backdrop.style.display = 'none';
    }
};

window.refreshHostingDeployLogs = async function () {
    const batchId = window._currentHostingLogBatchId;
    if (!batchId || typeof apiFetch !== 'function') return;

    try {
        const res = await apiFetch(`/api/dispatch/hosting/batch/${batchId}`);
        if (!res || res.status !== 'success' || !res.batch) return;
        window.renderHostingDeployLogDrawerContent(res.batch);
    } catch (e) {
        const pre = document.getElementById('hlog-terminal-content');
        if (pre) pre.innerText = `[ERROR] 调取批次详情异常: ${e.message || e}`;
    }
};

window.renderHostingDeployLogDrawerContent = function (b) {
    const statusMap = {
        'SUCCESS': { label: '✅ 发布成功', cls: 'badge-success' },
        'PARTIAL_SUCCESS': { label: '⚠️ 部分成功', cls: 'badge-warning' },
        'RUNNING': { label: '⏳ 正在发布', cls: 'badge-running' },
        'FAILED': { label: '❌ 发布失败', cls: 'badge-failed' },
        'PENDING': { label: '⏸️ 待命排队', cls: 'badge-idle' }
    };
    const st = statusMap[b.overall_status] || { label: b.overall_status || '未知', cls: 'badge-idle' };
    const stEl = document.getElementById('hlog-status-badge');
    if (stEl) { stEl.className = `ledger-badge ${st.cls}`; stEl.innerText = st.label; }

    const docId = b.doc_id || (b.trigger_source && b.trigger_source.startsWith('vault_drawer:') ? b.trigger_source.split('vault_drawer:')[1] : (b.targets && b.targets._trigger_doc ? b.targets._trigger_doc : null));
    const srcItem = document.getElementById('hlog-source-item');
    const srcEl = document.getElementById('hlog-source');
    if (srcItem && srcEl) {
        if (docId) {
            srcItem.style.display = 'flex';
            srcEl.innerText = `📄 ${docId.split('/').pop()}`;
            srcEl.title = `触发原稿: ${docId}`;
        } else {
            srcItem.style.display = 'none';
        }
    }

    const themeName = (window.getThemeDisplayName ? window.getThemeDisplayName(b.theme) : b.theme) || 'Sovereign';
    const thEl = document.getElementById('hlog-theme'); if (thEl) thEl.innerText = `🎨 ${themeName}`;
    const pgEl = document.getElementById('hlog-pages'); if (pgEl) pgEl.innerText = `${b.pages_count ?? 0} 个网页`;
    const sizeText = b.bundle_size_kb != null
        ? (b.bundle_size_kb < 1024 ? `${Number(b.bundle_size_kb).toFixed(1)} KB` : `${(b.bundle_size_kb / 1024).toFixed(1)} MB`)
        : '--';
    const szEl = document.getElementById('hlog-size'); if (szEl) szEl.innerText = sizeText;
    const durEl = document.getElementById('hlog-dur');
    if (durEl) {
        if ((b.overall_status === 'RUNNING' || b.overall_status === 'PENDING') && b.started_at) {
            const startTs = new Date(b.started_at.replace(/-/g, '/')).getTime();
            const elapsed = isNaN(startTs) ? (b.duration_sec ? Math.round(b.duration_sec) : 0) : Math.max(0, Math.round((Date.now() - startTs) / 1000));
            durEl.innerText = `${elapsed}s (运行中)`;
        } else {
            durEl.innerText = b.duration_sec != null ? `${Math.round(b.duration_sec)}s` : '--';
        }
    }

    const tList = document.getElementById('hlog-targets-list');
    if (tList) {
        const targets = b.targets || {};
        const keys = Object.keys(targets).filter(k => !k.startsWith('_'));
        if (keys.length === 0) {
            tList.innerHTML = `<div class="hlog-target-chip idle"><span class="name">🌐 全部就绪渠道</span><span class="status">待命中</span></div>`;
        } else {
            const platformNames = {
                github_pages: 'GitHub Pages', vercel: 'Vercel', cloudflare_pages: 'Cloudflare Pages',
                cloudflare: 'Cloudflare Pages', netlify: 'Netlify', firebase_hosting: 'Firebase Hosting',
                supabase_storage: 'Supabase Storage', render: 'Render', railway: 'Railway',
                gitlab_pages: 'GitLab Pages', gitee_pages: 'Gitee Pages', s3_compatible: 'S3 存储'
            };
            const esc = window.escapeHtml || (s => s);
            tList.innerHTML = keys.map(k => {
                const item = targets[k] || {};
                const flt = (window._lastHostingOverview?.fleet || []).find(f => f && f.id === k);
                const name = flt?.name || platformNames[k] || k;
                const isSuccess = item.status === 'SUCCESS';
                const isRunning = item.status === 'RUNNING';
                const isPending = item.status === 'PENDING';
                let cls = 'idle';
                let badgeText = '待命中';
                if (isSuccess) { cls = 'ok'; badgeText = '✅ 就绪'; }
                else if (isRunning) { cls = 'running'; badgeText = '⏳ 推送中'; }
                else if (isPending) { cls = 'pending'; badgeText = '⏸️ 准备中'; }
                else if (item.status === 'FAILED') { cls = 'err'; badgeText = '❌ 失败'; }

                const rawUrl = item.url || (isSuccess ? flt?.site_url : '') || '';
                const linkLabel = docId ? '访问文章 ↗' : '访问线上 ↗';
                const urlHtml = rawUrl && rawUrl.startsWith('http')
                    ? `<a href="${esc(rawUrl)}" target="_blank" rel="noopener noreferrer" class="link" onclick="event.stopPropagation();">${linkLabel}</a>`
                    : '';
                const errHtml = item.error ? `<div class="err-msg" title="${esc(item.error)}">⚠️ ${esc(item.error)}</div>` : '';
                return `
                    <div class="hlog-target-chip ${cls}">
                        <div class="chip-head">
                            <span class="name">🌐 ${esc(name)}</span>
                            <span class="chip-badge ${cls}">${badgeText}</span>
                        </div>
                        ${urlHtml}
                        ${errHtml}
                    </div>
                `;
            }).join('');
        }
    }

    const pre = document.getElementById('hlog-terminal-content');
    if (pre) {
        const raw = b.logs_excerpt || '[INFO] 暂无控制台日志';
        pre.innerHTML = window.colorizeTerminalLogs ? window.colorizeTerminalLogs(raw) : (window.escapeHtml ? window.escapeHtml(raw) : raw);
        pre.scrollTop = pre.scrollHeight;
    }

    const liveTag = document.getElementById('hlog-live-indicator');
    if (b.overall_status === 'RUNNING' || b.overall_status === 'PENDING') {
        if (liveTag) liveTag.style.display = 'inline-block';
        if (!window._hostingLogPollTimer) {
            window._hostingLogPollTimer = setInterval(() => window.refreshHostingDeployLogs(), 2000);
        }
    } else {
        if (liveTag) liveTag.style.display = 'none';
        if (window._hostingLogPollTimer) {
            clearInterval(window._hostingLogPollTimer);
            window._hostingLogPollTimer = null;
            if (typeof window.loadHostingDeployCenter === 'function') {
                window.loadHostingDeployCenter();
            }
        }
    }

    window._currentHostingLogBatch = b;
    const redeployBtn = document.getElementById('hlog-redeploy-btn');
    if (redeployBtn) {
        const isRunning = b.overall_status === 'RUNNING' || b.overall_status === 'PENDING';
        redeployBtn.disabled = isRunning;
        const targets = b.targets || {};
        const targetKeys = Object.keys(targets).filter(k => !k.startsWith('_'));
        if (targetKeys.length === 1) {
            const flt = (window._lastHostingOverview?.fleet || []).find(f => f && f.id === targetKeys[0]);
            const chName = flt?.name || targetKeys[0];
            const btnText = docId ? `再次同步到 ${chName}` : `再次发布 (${chName})`;
            redeployBtn.innerHTML = `<span class="btn-icon">🔄</span> ${window.escapeHtml ? window.escapeHtml(btnText) : btnText}`;
            redeployBtn.title = docId ? `重新为原稿 [${docId}] 触发向 ${chName} 推流` : `重新将全站内容发布到 ${chName}`;
        } else {
            const btnText = docId ? `再次全网同步原稿` : `再次发布网站`;
            redeployBtn.innerHTML = `<span class="btn-icon">🔄</span> ${btnText}`;
            redeployBtn.title = docId ? `重新为原稿 [${docId}] 触发全平台推流` : `重新将全站内容发布到全部已就绪平台`;
        }
    }
};

window.redeployCurrentHostingBatch = function () {
    const b = window._currentHostingLogBatch;
    const targets = b?.targets || {};
    const targetKeys = Object.keys(targets).filter(k => !k.startsWith('_'));
    const targetChannel = targetKeys.length === 1 ? targetKeys[0] : null;
    const docId = b?.doc_id || (b?.trigger_source && b.trigger_source.startsWith('vault_drawer:') ? b.trigger_source.split('vault_drawer:')[1] : (targets._trigger_doc || null));
    if (typeof window.triggerFullHostingDeploy === 'function') {
        window.triggerFullHostingDeploy(targetChannel, { isRedeploy: true, batchId: b?.batch_id, docId: docId });
    }
};

window.colorizeTerminalLogs = function (text) {
    if (!text) return '';
    const esc = window.escapeHtml || (s => s);
    return text.split('\n').map(line => {
        let safe = esc(line);
        if (line.includes('[SUCCESS]')) return `<span class="term-success">${safe}</span>`;
        if (line.includes('[ERROR]') || line.includes('❌')) return `<span class="term-error">${safe}</span>`;
        if (line.includes('[SOURCE]')) return `<span class="term-source" style="color: #38bdf8; font-weight: 600;">${safe}</span>`;
        if (line.includes('[INIT]') || line.includes('[BUNDLE]')) return `<span class="term-init">${safe}</span>`;
        if (line.includes('[PUSH]') || line.includes('[PROGRESS]') || line.includes('[QUEUE]')) return `<span class="term-push">${safe}</span>`;
        if (line.includes('[FINISH]')) return `<span class="term-finish">${safe}</span>`;
        return `<span class="term-line">${safe}</span>`;
    }).join('\n');
};

window.copyHostingDeployLogs = function () {
    const pre = document.getElementById('hlog-terminal-content');
    const text = pre ? (pre.innerText || pre.textContent) : '';
    if (!text) return;
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
        if (typeof showToast === 'function') showToast('已复制控制台日志到剪贴板', 'success');
    }
};

window.copyHostingLogBatchId = function () {
    const id = window._currentHostingLogBatchId;
    if (id && navigator.clipboard) {
        navigator.clipboard.writeText(id);
        if (typeof showToast === 'function') showToast(`已复制批次号: ${id}`, 'info');
    }
};
