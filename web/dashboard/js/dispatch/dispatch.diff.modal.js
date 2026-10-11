/**
 * 🔍 [V126.0] Illacme Plenipes - Dispatch Single-Doc Diff Inspection & Decision Modal
 * 职责：提供单篇分发原稿修改增量 Diff 差异透视与推流决策辅助模态框。
 */

(function () {
    const _esc = (s) => (window.escapeHtml ? window.escapeHtml(s || '') : (s || ''));

    window.openDispatchDiffModal = async function (relPath, targetId = '', langCode = 'zh-CN', targetName = '') {
        if (!relPath) return;

        let root = document.getElementById('dispatch-diff-modal-root');
        if (!root) {
            root = document.createElement('div');
            root.id = 'dispatch-diff-modal-root';
            root.className = 'syndicate-modal-backdrop';
            document.body.appendChild(root);
        }

        const safePath = _esc(relPath);
        const safeTarget = _esc(targetName || targetId || '社交媒体');

        // 1. 先呈现高档毛玻璃弹窗与加载骨架
        root.innerHTML = `
            <div class="syndicate-preview-modal-card glass-panel dispatch-diff-modal-card">
                <div class="syndicate-modal-header">
                    <div class="syndicate-modal-title-group">
                        <span class="syndicate-modal-title-icon">🔍</span>
                        <div class="syndicate-modal-title-text">
                            <div class="syndicate-modal-title">原稿改动差异对比与决策中枢</div>
                            <div class="syndicate-modal-subtitle">稿件：${safePath} · 渠道：${safeTarget}</div>
                        </div>
                    </div>
                    <div class="syndicate-modal-header-actions">
                        <button type="button" class="syndicate-modal-close-btn" onclick="window.closeDispatchDiffModal()" title="关闭 (Esc)">×</button>
                    </div>
                </div>
                <div id="dispatch-diff-modal-body" class="syndicate-modal-body dispatch-diff-modal-body">
                    <div class="dispatch-diff-loading">
                        <span class="spinner-gear">⚙️</span>
                        <span>正在检索原稿在上次发布时的 Git 快照并计算增量差异...</span>
                    </div>
                </div>
            </div>
        `;
        root.classList.add('is-open');

        // 绑定 ESC 关闭快捷键
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                window.closeDispatchDiffModal();
                window.removeEventListener('keydown', escHandler);
            }
        };
        window.addEventListener('keydown', escHandler);

        // 2. 异步请求后端 Diff 接口
        try {
            const fetchFunc = window.apiFetch || window.fetch;
            const url = `/api/dispatch/ledger/diff?rel_path=${encodeURIComponent(relPath)}&target_id=${encodeURIComponent(targetId || '')}`;
            const res = await (typeof window.apiFetch === 'function' ? fetchFunc(url) : fetch(url).then(r => r.json()));
            
            const data = (res && res.data) ? res.data : null;
            if (!data) {
                throw new Error((res && res.detail) || '无法提取差异数据');
            }

            renderDiffModalContent(root, data, relPath, targetId, langCode, targetName);
        } catch (err) {
            const bodyEl = document.getElementById('dispatch-diff-modal-body');
            if (bodyEl) {
                bodyEl.innerHTML = `
                    <div class="dispatch-diff-empty-state">
                        <div style="font-size: 2rem; margin-bottom: 8px;">⚠️</div>
                        <div style="font-weight: 700; color: var(--neon-red); margin-bottom: 6px;">无法加载原稿改动差异</div>
                        <div style="font-size: 0.8rem; color: var(--text-muted);">${_esc(err.message || '网络连接或文件检索超时')}</div>
                    </div>
                `;
            }
        }
    };

    window.closeDispatchDiffModal = function () {
        const root = document.getElementById('dispatch-diff-modal-root');
        if (root) {
            root.classList.remove('is-open');
        }
    };

    function renderDiffModalContent(root, data, relPath, targetId, langCode, targetName) {
        const bodyEl = document.getElementById('dispatch-diff-modal-body');
        if (!bodyEl) return;

        const adds = data.additions || 0;
        const dels = data.deletions || 0;
        const timeDelta = data.time_delta_human || '已检测到更新';
        const displayPub = (window.formatDispatchFullTime && data.published_at) ? window.formatDispatchFullTime(data.published_at) : (data.published_at || '历史发布');
        const displayMod = (window.formatDispatchFullTime && data.modified_at) ? window.formatDispatchFullTime(data.modified_at) : (data.modified_at || '当前版本');
        const safeTargetName = _esc(targetName || data.target_name || targetId);
        const safePath = _esc(relPath);

        // 🛡️ [V127.0] 频控与安全冷却状态感知
        const remCooldown = (window.DispatchCooldownManager && window.DispatchCooldownManager.getRemaining(relPath, targetId)) || 0;
        const isCooling = remCooldown > 0;
        const taskKey = `${relPath}::${targetId}`;
        const republishBtnText = isCooling ? `🛡️ 平台安全冷却中 (${remCooldown}s)` : `📡 立即向 [${safeTargetName}] 推流更新`;
        const republishDisabled = isCooling ? 'disabled' : '';
        const republishClass = `primary-btn glow-btn ${isCooling ? 'is-cooling-btn' : ''}`;

        // 构建 Diff 行级可视化
        let diffViewHtml = '';
        if (data.has_diff && Array.isArray(data.diff_lines) && data.diff_lines.length > 0) {
            diffViewHtml = '<div class="dispatch-diff-code-window">';
            data.diff_lines.forEach(line => {
                const lineType = line.type || 'context';
                const safeText = _esc(line.text || '');
                if (lineType === 'header') {
                    diffViewHtml += `<div class="dispatch-diff-line is-header"><span class="diff-sign"></span><span class="diff-content">${safeText}</span></div>`;
                } else if (lineType === 'addition') {
                    diffViewHtml += `<div class="dispatch-diff-line is-addition"><span class="diff-sign">+</span><span class="diff-content">${safeText}</span></div>`;
                } else if (lineType === 'deletion') {
                    diffViewHtml += `<div class="dispatch-diff-line is-deletion"><span class="diff-sign">-</span><span class="diff-content">${safeText}</span></div>`;
                } else {
                    diffViewHtml += `<div class="dispatch-diff-line is-context"><span class="diff-sign"> </span><span class="diff-content">${safeText}</span></div>`;
                }
            });
            diffViewHtml += '</div>';
        } else {
            diffViewHtml = `
                <div class="dispatch-diff-empty-state">
                    <div style="font-size: 2.2rem; margin-bottom: 8px;">📑</div>
                    <div style="font-weight: 700; color: var(--text-bright); margin-bottom: 6px;">未检测到显式文本差异</div>
                    <div style="font-size: 0.82rem; color: var(--text-muted); max-width: 480px; line-height: 1.5;">
                        ${data.error ? _esc(data.error) : '文件物理修改时间晚于发布时间，但正文未产生新增/删除行（可能是微调了文件属性或元数据已同步）。'}
                    </div>
                </div>
            `;
        }

        bodyEl.innerHTML = `
            <div class="dispatch-diff-layout">
                <!-- 顶部元数据与对比看板 -->
                <div class="dispatch-diff-meta-bar">
                    <div class="dispatch-diff-meta-item">
                        <span class="meta-label">上次发布:</span>
                        <span class="meta-val">${_esc(displayPub)}</span>
                    </div>
                    <div class="dispatch-diff-arrow">➔</div>
                    <div class="dispatch-diff-meta-item">
                        <span class="meta-label">原稿修订:</span>
                        <span class="meta-val">${_esc(displayMod)}</span>
                    </div>
                    <div class="dispatch-diff-badge-pill is-time-delta">
                        <span>⏱️</span>
                        <span>${_esc(timeDelta)}</span>
                    </div>
                    <div class="dispatch-diff-stats-group">
                        <span class="diff-stat-tag addition">+${adds} 行</span>
                        <span class="diff-stat-tag deletion">-${dels} 行</span>
                    </div>
                </div>

                <!-- 差异代码对照窗口 -->
                <div class="dispatch-diff-content-slot">
                    ${diffViewHtml}
                </div>

                <!-- 底部决策控制条 -->
                <div class="dispatch-diff-decision-bar">
                    <div class="decision-hint">
                        <span>💡 审阅建议：若包含重要内容或代码修正，建议立即推流覆盖；若仅为微小排版微调可暂缓。</span>
                        ${isCooling ? `<div class="decision-cooling-badge"><span>🛡️ 平台频控保护：已开启 ${safeTargetName} 防封冷却 (剩 ${remCooldown}s)</span></div>` : ''}
                    </div>
                    <div class="decision-actions">
                        <button type="button" class="secondary-btn" onclick="window.closeDispatchDiffModal()">
                            <span>✖️ 暂不更新</span>
                        </button>
                        <button type="button" class="secondary-btn" onclick="window.closeDispatchDiffModal(); if(typeof window.openSyndicateLivePreviewModal==='function') window.openSyndicateLivePreviewModal('${safePath}', '${_esc(targetId)}');">
                            <span>👁️ 前置排版工坊</span>
                        </button>
                        <button type="button" class="${republishClass}" id="diff-modal-republish-btn" ${republishDisabled} data-cooldown-task="${taskKey}" onclick="handleDiffModalRepublish('${safePath}', '${_esc(targetId)}', '${_esc(langCode)}')">
                            <span>${republishBtnText}</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    window.handleDiffModalRepublish = async function (relPath, targetId, langCode) {
        const btn = document.getElementById('diff-modal-republish-btn');
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-gear">⚙️</span> 正在推流中...';
        }
        if (typeof showToast === 'function') {
            showToast(`🚀 已针对 [${targetId.toUpperCase()}] 下发原地更新推流指令...`, 'info');
        }

        if (typeof window.republishSingleSyndicationDoc === 'function') {
            await window.republishSingleSyndicationDoc(relPath, targetId, langCode);
        }

        setTimeout(() => {
            window.closeDispatchDiffModal();
        }, 1200);
    };
})();
