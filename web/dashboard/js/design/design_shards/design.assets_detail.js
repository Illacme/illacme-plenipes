/**
 * 🎨 [V1.0] Illacme Plenipes Design Studio - Assets Detail & Self-healing Shard
 * 职责：媒体资产详情弹层展示、生图提示词复用、封面绑定与缺失封面一键自愈。
 */

(function () {
    'use strict';

    const normalizeEngine = (strat) => {
        const clean = (strat || '').replace(/^ai_/, '').toLowerCase();
        return (clean === 'local_og' || clean === 'og_card' || clean === 'og') ? 'og_card' : clean;
    };

    window.openAssetDetailModal = function (assetId) {
        const list = window._designAssetsList || [];
        const a = list.find(x => x.id === assetId);
        if (!a) return;
        const promptText = a.prompt || a.rel_path || '默认封面模板';
        const engName = normalizeEngine(a.strategy) === 'og_card' ? '🎨 OG 技术卡片' : (a.strategy || 'cover').toUpperCase();
        const refCount = a.reference_count || (a.references && a.references.length) || 0;

        const modalHtml = `
            <div id="asset-detail-modal" class="modal-overlay active" style="z-index:9999; display:flex; align-items:center; justify-content:center; background:rgba(0,0,0,0.75); backdrop-filter:blur(6px); position:fixed; inset:0;" onclick="if(event.target===this)this.remove()">
                <div class="glass-panel" style="width:720px; max-width:92vw; max-height:88vh; border-radius:14px; border:1px solid rgba(0,242,254,0.3); display:flex; flex-direction:column; overflow:hidden; box-shadow:0 20px 50px rgba(0,0,0,0.8); background:#0c1017;" onclick="event.stopPropagation()">
                    <div style="padding:14px 18px; border-bottom:1px solid rgba(255,255,255,0.08); display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-weight:700; color:#fff; font-size:0.92rem; display:flex; align-items:center; gap:8px;">
                            <span>🗃️ 媒体资产详情</span><span style="font-size:0.7rem; color:#00f2fe; background:rgba(0,242,254,0.1); padding:2px 8px; border-radius:4px;">#${a.id}</span>
                        </div>
                        <button type="button" class="mini-btn" style="padding:4px 8px; font-size:0.8rem;" onclick="document.getElementById('asset-detail-modal').remove()">✕</button>
                    </div>
                    <div style="padding:16px 20px; overflow-y:auto; display:flex; flex-direction:column; gap:14px;">
                        <div style="width:100%; max-height:340px; background:#000; border-radius:8px; overflow:hidden; display:flex; align-items:center; justify-content:center; border:1px solid rgba(255,255,255,0.1);">
                            <img src="${a.source_url}" style="max-width:100%; max-height:340px; object-fit:contain;" />
                        </div>
                        <div style="display:flex; flex-direction:column; gap:4px;">
                            <label style="font-size:0.72rem; color:var(--text-dim);">生图提示词 (Prompt)</label>
                            <div style="background:rgba(0,0,0,0.4); padding:8px 12px; border-radius:6px; border:1px solid rgba(255,255,255,0.08); font-size:0.78rem; color:#fff; line-height:1.4; user-select:text;">${promptText}</div>
                        </div>
                        <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:8px; font-size:0.72rem; color:var(--text-dim);">
                            <div style="background:rgba(255,255,255,0.03); padding:6px 10px; border-radius:6px;"><div>驱动引擎</div><div style="color:#00f2fe; font-weight:600; margin-top:2px;">${engName}</div></div>
                            <div style="background:rgba(255,255,255,0.03); padding:6px 10px; border-radius:6px;"><div>落盘时间</div><div style="color:#fff; margin-top:2px;">${a.created_at || '未知'}</div></div>
                            <div style="background:rgba(255,255,255,0.03); padding:6px 10px; border-radius:6px;"><div>引用状态</div><div style="color:${refCount>0?'#10b981':'#f59e0b'}; font-weight:600; margin-top:2px;">${refCount>0?`关联 ${refCount} 篇`:'⭕ 闲置'}</div></div>
                        </div>
                    </div>
                    <div style="padding:12px 18px; border-top:1px solid rgba(255,255,255,0.08); background:rgba(0,0,0,0.3); display:flex; justify-content:space-between; align-items:center;">
                        <button type="button" class="mini-btn" style="padding:5px 12px; font-size:0.74rem;" onclick="document.getElementById('asset-detail-modal').remove(); window.switchDesignSubTab('workspace');">🪄 带入生图</button>
                        <div style="display:flex; gap:8px;">
                            <button type="button" class="mini-btn" style="padding:5px 12px; font-size:0.74rem;" onclick="window.copyAssetMarkdown('${a.cdn_url || a.source_url}')">📋 复制 MD</button>
                            <button type="button" class="mini-btn" style="padding:5px 12px; font-size:0.74rem; background:rgba(0,242,254,0.15); border-color:rgba(0,242,254,0.4); color:#00f2fe;" onclick="document.getElementById('asset-detail-modal').remove(); window.openAssetApplyCoverModal('${a.source_url}')">🖼️ 设为文章封面</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    };

    window.healMissingCovers = async function () {
        const fetchApi = window.apiFetch || (async (url, opts) => (await fetch(url, opts)).json());
        if (window.showToast) window.showToast('🔍 正在全面扫描文库并自愈缺失封面...', 'info');
        try {
            const res = await fetchApi('/api/design/batch/heal-missing-covers', { method: 'POST' });
            if (res && res.success) {
                if (window.showToast) window.showToast(`✨ 自愈完成：共扫描 ${res.scanned} 篇，成功补齐 ${res.healed_count} 个缺失封面！`, 'success');
                if (typeof window.loadVisualAssetsList === 'function') window.loadVisualAssetsList();
                if (typeof window.loadVaultFiles === 'function') window.loadVaultFiles();
            } else {
                if (window.showToast) window.showToast(res.detail || '自愈处理异常', 'error');
            }
        } catch (e) {
            console.error('[HealMissingCovers] Failed:', e);
            if (window.showToast) window.showToast('自愈请求网络异常', 'error');
        }
    };

})();
