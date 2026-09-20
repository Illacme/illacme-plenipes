// -*- coding: utf-8 -*-
/**
 * ⚡ [V1.0] Design Studio - Batch Cover Operations Shard
 * 职责：文库全量原稿封面巡检、覆盖率可视化与分批流水线智能装配中枢。
 * 🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
 * 🛡️ [SOP-03] 商业级暗黑毛玻璃视觉主权与逐篇微交互。
 */

(function () {
    let _batchReport = null;
    let _selectedDocIds = new Set();
    let _isProcessing = false;

    window.openBatchCoverModal = async function () {
        const old = document.getElementById('batch-cover-modal');
        if (old) old.remove();

        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        let report = { total_count: 0, covered_count: 0, uncovered_count: 0, coverage_rate: '0.0%', uncovered_docs: [] };

        try {
            const res = await fetchApi('/api/design/batch/uncovered-docs');
            if (res) report = res;
        } catch (e) {
            console.warn('[BatchCover] Fetch report failed:', e);
        }

        _batchReport = report;
        _selectedDocIds = new Set((report.uncovered_docs || []).map(d => d.doc_id));
        _isProcessing = false;

        const modalHtml = `
            <div id="batch-cover-modal" class="modal-overlay active" style="z-index:100000; display:flex; align-items:center; justify-content:center; background:rgba(0,0,0,0.82); backdrop-filter:blur(12px); position:fixed; inset:0; padding:16px;">
                <div class="glass-panel" style="width:820px; max-width:96vw; max-height:88vh; border-radius:14px; border:1px solid rgba(0,242,254,0.35); display:flex; flex-direction:column; overflow:hidden; box-shadow:0 24px 60px rgba(0,0,0,0.9);">
                    
                    <!-- 顶栏：标题与巡检进度 -->
                    <div class="batch-modal-header" style="padding:16px 20px; border-bottom:1px solid rgba(255,255,255,0.08); display:flex; justify-content:space-between; align-items:center;">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="font-size:1.3rem;">⚡</span>
                            <div>
                                <div class="batch-modal-title" style="font-weight:700; color:var(--text-bright); font-size:0.96rem; letter-spacing:0.3px;">文库原稿批量智能配图中枢</div>
                                <div style="font-size:0.72rem; color:var(--text-dim); margin-top:2px;">一键全库封面巡检 · 视觉覆盖率看板 · 流水线批量装配</div>
                            </div>
                        </div>
                        <button type="button" class="mini-btn" style="padding:4px 9px; font-size:0.85rem;" onclick="document.getElementById('batch-cover-modal').remove()">✕</button>
                    </div>

                    <!-- 封面覆盖率看板条插槽 -->
                    <div id="batch-cover-progress-slot">
                        ${window.renderBatchCoverProgressHtml(report)}
                    </div>

                    <!-- 策略与参数选择栏 -->
                    <div class="batch-toolbar" style="padding:12px 20px; border-bottom:1px solid rgba(255,255,255,0.06); display:flex; gap:14px; align-items:center; flex-wrap:wrap; font-size:0.75rem;">
                        <div style="display:flex; align-items:center; gap:6px;">
                            <span style="color:var(--text-dim);">图源策略:</span>
                            <select id="batch-cover-strategy" class="studio-select batch-select" style="padding:4px 8px; border-radius:6px; font-size:0.75rem;">
                                <option value="og_card" selected>🎨 极客排版·本地 OG 卡片 (推荐·毫秒级离线)</option>
                                <option value="minimal_badge">🏷️ 极简艺术徽章 (轻量纯离线)</option>
                                <option value="brand_presets">🏛️ 品牌母本预置图库 (视觉统一)</option>
                                <option value="picsum">📸 Lorem Picsum (随机艺术免Key)</option>
                                <option value="unsplash">🌐 Unsplash 摄影图库 (免Key)</option>
                            </select>
                        </div>
                        <div style="display:flex; align-items:center; gap:6px;">
                            <span style="color:var(--text-dim);">比例:</span>
                            <select id="batch-cover-ratio" class="studio-select batch-select" style="padding:4px 8px; border-radius:6px; font-size:0.75rem;">
                                <option value="16:9" selected>16:9 标准横版</option>
                                <option value="3:2">3:2 胶片画幅</option>
                                <option value="2:1">2:1 宽屏 Banner</option>
                            </select>
                        </div>
                        <div style="margin-left:auto; display:flex; gap:8px;">
                            <button type="button" class="mini-btn" style="font-size:0.7rem; padding:3px 8px;" onclick="window.toggleAllBatchDocs(true)">全选</button>
                            <button type="button" class="mini-btn" style="font-size:0.7rem; padding:3px 8px;" onclick="window.toggleAllBatchDocs(false)">清空</button>
                        </div>
                    </div>

                    <!-- 待配图文章网格/列表 -->
                    <div id="batch-cover-docs-container" style="flex:1; overflow-y:auto; padding:16px 20px; display:flex; flex-direction:column; gap:8px;">
                        ${window.renderBatchDocsListHtml()}
                    </div>

                    <!-- 底部操作栏 -->
                    <div class="batch-footer" style="padding:14px 20px; border-top:1px solid rgba(255,255,255,0.08); display:flex; justify-content:space-between; align-items:center;">
                        <div id="batch-cover-summary" style="font-size:0.75rem; color:var(--text-dim);">
                            已勾选 <strong id="batch-selected-count" style="color:var(--accent-secondary);">${_selectedDocIds.size}</strong> 篇原稿
                        </div>
                        <div style="display:flex; gap:10px; align-items:center;">
                            <button type="button" class="mini-btn" style="padding:6px 14px; font-size:0.78rem;" onclick="document.getElementById('batch-cover-modal').remove()">关闭</button>
                            <button type="button" id="batch-execute-btn" class="mini-btn glow-btn" style="padding:6px 20px; font-size:0.78rem; font-weight:700; background:var(--accent-secondary,#00f2fe); color:#000; border:none; border-radius:6px; cursor:pointer;" onclick="window.executeBatchCoverGeneration()">
                                ⚡ 一键批量装配封面
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
    };

    window.renderBatchCoverProgressHtml = function (report) {
        const rep = report || _batchReport || { total_count: 0, covered_count: 0, uncovered_count: 0 };
        const total = rep.total_count || 0;
        const covered = rep.covered_count || 0;
        const uncovered = rep.uncovered_count || 0;
        const percent = total > 0 ? ((covered / total) * 100).toFixed(1) : '100.0';
        const isDone = uncovered === 0;

        return `
            <div class="batch-progress-bar-slot" style="padding:12px 20px; border-bottom:1px solid rgba(255,255,255,0.06); display:flex; flex-direction:column; gap:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem;">
                    <span style="color:var(--text-bright);">📊 文库视觉装配进度：<strong id="batch-progress-covered-num" style="color:var(--accent-secondary);">${covered}</strong> / ${total} 篇</span>
                    <span id="batch-progress-status-badge" style="color:${isDone ? '#00ff88' : '#f59e0b'}; font-weight:600;">
                        ${isDone ? '✨ 已 100% 全量覆盖' : `⚠️ 待配图 ${uncovered} 篇 (${percent}%)`}
                    </span>
                </div>
                <div class="batch-progress-track" style="height:6px; width:100%; border-radius:3px; overflow:hidden;">
                    <div id="batch-progress-bar-inner" style="height:100%; width:${percent}%; background:linear-gradient(90deg, #00f2fe, #00ff88); transition:width 0.35s ease;"></div>
                </div>
            </div>
        `;
    };

    window.updateBatchCoverProgressLive = function (curCovered, totalDocs) {
        const total = totalDocs || (_batchReport && _batchReport.total_count) || 1;
        const covered = Math.min(curCovered, total);
        const uncovered = Math.max(0, total - covered);
        const percent = total > 0 ? ((covered / total) * 100).toFixed(1) : '100.0';
        const numEl = document.getElementById('batch-progress-covered-num');
        const badgeEl = document.getElementById('batch-progress-status-badge');
        const barEl = document.getElementById('batch-progress-bar-inner');
        if (numEl) numEl.innerText = covered;
        if (badgeEl) {
            badgeEl.style.color = uncovered === 0 ? '#00ff88' : '#f59e0b';
            badgeEl.innerText = uncovered === 0 ? '✨ 已 100% 全量覆盖' : `⚠️ 待配图 ${uncovered} 篇 (${percent}%)`;
        }
        if (barEl) barEl.style.width = `${percent}%`;
    };

    window.renderBatchDocsListHtml = function () {
        const docs = (_batchReport && _batchReport.uncovered_docs) || [];
        if (docs.length === 0) {
            return `
                <div style="text-align:center; padding:50px 0; color:var(--text-dim);">
                    <div style="font-size:2.4rem; margin-bottom:10px;">🎉</div>
                    <div class="batch-empty-title" style="font-size:0.92rem; color:var(--text-bright); font-weight:600;">全库原稿视觉封面已 100% 装配齐全！</div>
                    <div style="font-size:0.74rem; color:var(--text-dim); margin-top:4px;">无需额外配图，整站文章在独立站与分发渠道均具备精美预览卡片</div>
                </div>
            `;
        }

        return docs.map(d => {
            const isChecked = _selectedDocIds.has(d.doc_id);
            const safeId = d.doc_id.replace(/"/g, '&quot;');
            const safeCid = d.doc_id.replace(/[^a-zA-Z0-9_-]/g, '_');
            return `
                <label id="batch-item-row-${safeCid}" class="batch-item-row" style="display:flex; align-items:center; gap:12px; padding:10px 14px; border-radius:8px; cursor:pointer; transition:all 0.2s;">
                    <input type="checkbox" id="batch-checkbox-${safeCid}" data-doc-id="${safeId}" ${isChecked ? 'checked' : ''} onchange="window.toggleBatchDocSelect('${safeId}', this.checked)" style="accent-color:#00f2fe; width:15px; height:15px; cursor:pointer;" />
                    <div style="flex:1; overflow:hidden;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span class="batch-doc-title" style="font-weight:600; color:var(--text-bright); font-size:0.82rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">《${d.title}》</span>
                            <span style="font-size:0.65rem; color:#00f2fe; background:rgba(0,242,254,0.1); padding:1px 6px; border-radius:4px;">${d.category || '未分类'}</span>
                        </div>
                        <div style="font-size:0.68rem; color:var(--text-dim); margin-top:2px; font-family:monospace; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">📁 ${d.doc_id}</div>
                    </div>
                    <div id="batch-status-badge-${safeCid}" style="font-size:0.72rem; color:var(--text-dim); white-space:nowrap;">待装配</div>
                </label>
            `;
        }).join('');
    };

    window.toggleBatchDocSelect = function (docId, checked) {
        if (checked) _selectedDocIds.add(docId);
        else _selectedDocIds.delete(docId);
        const cntEl = document.getElementById('batch-selected-count');
        if (cntEl) cntEl.innerText = _selectedDocIds.size;
    };

    window.toggleAllBatchDocs = function (selectAll) {
        const docs = (_batchReport && _batchReport.uncovered_docs) || [];
        _selectedDocIds = selectAll ? new Set(docs.map(d => d.doc_id)) : new Set();
        const container = document.getElementById('batch-cover-docs-container');
        if (container) container.innerHTML = window.renderBatchDocsListHtml();
        const cntEl = document.getElementById('batch-selected-count');
        if (cntEl) cntEl.innerText = _selectedDocIds.size;
    };

    window.executeBatchCoverGeneration = async function () {
        if (_isProcessing) return;
        const targetIds = Array.from(_selectedDocIds);
        if (targetIds.length === 0) {
            if (typeof window.showToast === 'function') window.showToast('⚠️ 请至少勾选一篇待配图原稿', 'warning');
            return;
        }

        const stratSel = document.getElementById('batch-cover-strategy');
        const ratioSel = document.getElementById('batch-cover-ratio');
        const btn = document.getElementById('batch-execute-btn');
        const summaryEl = document.getElementById('batch-cover-summary');
        const strategy = stratSel ? stratSel.value : 'og_card';
        const ratio = ratioSel ? ratioSel.value : '16:9';

        _isProcessing = true;
        if (btn) { btn.disabled = true; btn.style.opacity = '0.7'; }

        const initialCovered = (_batchReport && _batchReport.covered_count) || 0;
        const totalDocs = (_batchReport && _batchReport.total_count) || targetIds.length;
        const BATCH_SIZE = 5;
        let totalApplied = 0;
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());

        try {
            for (let i = 0; i < targetIds.length; i += BATCH_SIZE) {
                const chunk = targetIds.slice(i, i + BATCH_SIZE);
                const curStart = i + 1;
                const curEnd = Math.min(i + chunk.length, targetIds.length);

                if (btn) btn.innerHTML = `⏳ 装配中 (${curStart}~${curEnd} / ${targetIds.length})...`;
                if (summaryEl) summaryEl.innerHTML = `<span style="color:#f59e0b;">⚙️ 正在装配第 ${curStart} ~ ${curEnd} 篇原稿...</span>`;

                chunk.forEach(docId => {
                    const cid = docId.replace(/[^a-zA-Z0-9_-]/g, '_');
                    const badge = document.getElementById(`batch-status-badge-${cid}`);
                    if (badge) { badge.innerText = '⚙️ 渲染中...'; badge.style.color = '#f59e0b'; }
                });

                const res = await fetchApi('/api/design/batch/generate-and-apply', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ doc_ids: chunk, strategy, aspect_ratio: ratio })
                });

                if (res && res.success) {
                    const applied = res.applied_count || chunk.length;
                    totalApplied += applied;
                    chunk.forEach(docId => {
                        const cid = docId.replace(/[^a-zA-Z0-9_-]/g, '_');
                        const badge = document.getElementById(`batch-status-badge-${cid}`);
                        if (badge) { badge.innerText = '🟢 已装配'; badge.style.color = '#00ff88'; badge.style.fontWeight = '600'; }
                        const chk = document.getElementById(`batch-checkbox-${cid}`);
                        if (chk) { chk.disabled = true; }
                    });
                    window.updateBatchCoverProgressLive(initialCovered + totalApplied, totalDocs);
                }
            }

            if (typeof window.showToast === 'function') window.showToast(`✨ 成功为 ${totalApplied} 篇原稿装配高质量封面！`, 'success');
            if (summaryEl) summaryEl.innerHTML = `<span style="color:#00ff88; font-weight:600;">✅ 装配完成：成功 ${totalApplied} 篇！</span>`;

            // 重新拉取报告并权威更新视图
            const newReport = await fetchApi('/api/design/batch/uncovered-docs');
            if (newReport) {
                _batchReport = newReport;
                _selectedDocIds.clear();
                const slot = document.getElementById('batch-cover-progress-slot');
                if (slot) slot.innerHTML = window.renderBatchCoverProgressHtml(newReport);
                const container = document.getElementById('batch-cover-docs-container');
                if (container) container.innerHTML = window.renderBatchDocsListHtml();
            }

            if (btn) { btn.innerHTML = '✅ 全量装配完成'; btn.disabled = true; }
            if (typeof window.loadVault === 'function') window.loadVault(null, window.vaultCurrentPage || 1);
            if (typeof window.loadDesignCenter === 'function') window.loadDesignCenter();
        } catch (e) {
            if (typeof window.showToast === 'function') window.showToast(`🛑 批量配图异常: ${e.message}`, 'error');
            if (summaryEl) summaryEl.innerHTML = `<span style="color:#f87171;">🛑 异常: ${e.message}</span>`;
            if (btn) { btn.disabled = false; btn.style.opacity = '1'; btn.innerHTML = '⚡ 一键批量装配封面'; }
        } finally {
            _isProcessing = false;
        }
    };
})();
