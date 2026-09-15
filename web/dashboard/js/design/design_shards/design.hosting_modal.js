/**
 * 🎨 [V1.0] Illacme Plenipes Design Studio - Asset Image Hosting Modal Shard
 * 职责：为指定媒体资产提供公网图床上传托管、CDN 链接生成与文档外链批量同步。
 * 🛡️ [SOP-01] 物理行数严格控制在 300 行以内。
 */

(function () {
    window.openAssetHostingModal = async function (assetId, sourceUrl) {
        const existing = document.getElementById('asset-hosting-modal');
        if (existing) existing.remove();

        const badgeText = assetId ? `#${assetId}` : '新生成';
        const modalHtml = `
            <div id="asset-hosting-modal" class="modal-overlay active" style="z-index:10000; display:flex; align-items:center; justify-content:center; background:rgba(0,0,0,0.8); backdrop-filter:blur(8px); position:fixed; inset:0;">
                <div class="glass-panel" style="width:580px; max-width:92vw; max-height:86vh; border-radius:14px; border:1px solid rgba(0,242,254,0.35); display:flex; flex-direction:column; overflow:hidden; box-shadow:0 24px 60px rgba(0,0,0,0.85);">
                    <!-- 顶栏 -->
                    <div style="padding:16px 20px; border-bottom:1px solid rgba(255,255,255,0.08); display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-weight:700; color:#fff; font-size:0.95rem; display:flex; align-items:center; gap:8px;">
                            <span>☁️ 媒体资产图床托管</span>
                            <span style="font-size:0.7rem; color:#00f2fe; background:rgba(0,242,254,0.1); padding:2px 8px; border-radius:4px;">${badgeText}</span>
                        </div>
                        <button type="button" class="mini-btn" style="padding:4px 8px; font-size:0.8rem;" onclick="document.getElementById('asset-hosting-modal').remove()">✕</button>
                    </div>

                    <!-- 内容区 -->
                    <div style="padding:20px; overflow-y:auto; display:flex; flex-direction:column; gap:16px;">
                        <div style="font-size:0.78rem; color:var(--text-dim); line-height:1.5;">
                            将本地生成的图片物理上传至公网图床，获取永久 CDN 加速外链，彻底解决知乎、微信、Medium 等平台分发时的内网防盗链与图片失效问题。
                        </div>

                        <!-- 目标图床选择 -->
                        <div style="display:flex; flex-direction:column; gap:8px;">
                            <label style="font-size:0.75rem; color:var(--text-dim); font-weight:600;">选择分发图床驱动 (Target Host)</label>
                            <div id="hosting-target-options" style="display:flex; flex-direction:column; gap:8px; max-height:220px; overflow-y:auto;">
                                <div style="color:var(--text-dim); font-size:0.75rem; text-align:center; padding:20px 0;">正在探测已集成图床驱动...</div>
                            </div>
                        </div>

                        <!-- 同步替换勾选 -->
                        <div style="background:rgba(0,242,254,0.05); padding:10px 14px; border-radius:8px; border:1px solid rgba(0,242,254,0.2); display:flex; align-items:center; gap:10px;">
                            <input type="checkbox" id="hosting-sync-ref-checkbox" checked style="cursor:pointer; accent-color:#00f2fe; width:15px; height:15px;" />
                            <label for="hosting-sync-ref-checkbox" style="font-size:0.75rem; color:var(--text-bright); cursor:pointer;">
                                🔄 上传成功后，自动将引用此图片的原稿封面替换为公网 CDN URL
                            </label>
                        </div>
                    </div>

                    <!-- 底栏操作 -->
                    <div style="padding:14px 20px; border-top:1px solid rgba(255,255,255,0.08); background:rgba(0,0,0,0.3); display:flex; justify-content:flex-end; gap:10px;">
                        <button type="button" class="mini-btn" style="padding:6px 14px; font-size:0.76rem;" onclick="document.getElementById('asset-hosting-modal').remove()">取消</button>
                        <button type="button" class="mini-btn glow-btn" id="btn-do-upload-hosting" style="padding:6px 18px; font-size:0.78rem; background:var(--accent-secondary, #00f2fe); color:#000; font-weight:700; border:none;" onclick="window.dispatchAssetUploadHosting(${assetId || 'null'}, '${sourceUrl || ''}')">
                            🚀 立即上传托管
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        await window.loadHostingTargets();
    };

    window.loadHostingTargets = async function () {
        const container = document.getElementById('hosting-target-options');
        if (!container) return;
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const res = await fetchApi('/api/design/assets/hosting-targets');
            const targets = (res && res.targets) || [];
            if (targets.length === 0) {
                container.innerHTML = '<div style="color:#f87171; font-size:0.75rem; padding:10px;">未发现可用图床插件</div>';
                return;
            }
            container.innerHTML = targets.map((t, idx) => {
                const isChecked = idx === 0 ? 'checked' : '';
                const badgeColor = t.is_ready ? '#00ff88' : 'var(--text-dim)';
                const badgeBg = t.is_ready ? 'rgba(0,255,136,0.1)' : 'rgba(255,255,255,0.05)';
                const badgeBorder = t.is_ready ? 'rgba(0,255,136,0.3)' : 'rgba(255,255,255,0.1)';
                return `
                    <label style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; background:rgba(255,255,255,0.03); border-radius:8px; border:1px solid rgba(255,255,255,0.08); cursor:pointer; transition:all 0.15s;"
                           onmouseover="this.style.borderColor='rgba(0,242,254,0.4)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.08)'">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <input type="radio" name="asset_hosting_provider" value="${t.id}" ${isChecked} style="accent-color:#00f2fe; cursor:pointer;" />
                            <div style="display:flex; flex-direction:column; gap:2px;">
                                <span style="font-size:0.8rem; font-weight:600; color:#fff;">${t.icon} ${t.name}</span>
                                <span style="font-size:0.68rem; color:var(--text-dim);">${t.desc}</span>
                            </div>
                        </div>
                        <span style="font-size:0.65rem; color:${badgeColor}; background:${badgeBg}; border:1px solid ${badgeBorder}; padding:2px 8px; border-radius:4px;">
                            ${t.status_label}
                        </span>
                    </label>
                `;
            }).join('');
        } catch (e) {
            container.innerHTML = `<div style="color:#f87171; font-size:0.75rem;">加载图床驱动失败: ${e.message}</div>`;
        }
    };

    window.dispatchAssetUploadHosting = async function (assetId, sourceUrl) {
        const checkedRadio = document.querySelector('input[name="asset_hosting_provider"]:checked');
        const providerId = checkedRadio ? checkedRadio.value : 'github';
        const syncRef = !!document.getElementById('hosting-sync-ref-checkbox')?.checked;
        const btn = document.getElementById('btn-do-upload-hosting');

        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-gear">⚙️</span> 正在上传图床...';
        }

        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const payload = { provider_id: providerId, sync_references: syncRef };
            if (assetId) payload.asset_id = assetId;
            if (sourceUrl) payload.source_url = sourceUrl;
            const res = await fetchApi('/api/design/assets/upload-hosting', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res && res.success && res.cdn_url) {
                if (typeof window.showToast === 'function') {
                    const syncNote = res.synced_docs_count > 0 ? `，并已同步更新 ${res.synced_docs_count} 篇原稿封面` : '';
                    window.showToast(`✨ 图床托管成功！公网外链已登记${syncNote}`, 'success');
                }
                const modal = document.getElementById('asset-hosting-modal');
                if (modal) modal.remove();

                const detailModal = document.getElementById('asset-detail-modal');
                if (detailModal) detailModal.remove();

                // 重新渲染资产库网格
                if (typeof window.loadAndRenderDesignAssets === 'function') {
                    window.loadAndRenderDesignAssets(document.getElementById('design-center-root'));
                }
                // 如果在文库列表，轻量刷新
                if (syncRef && typeof window.loadVault === 'function') {
                    window.loadVault(null, window.vaultCurrentPage || 1);
                }
            } else {
                throw new Error((res && (res.detail || res.message)) || '上传失败');
            }
        } catch (e) {
            if (typeof window.showToast === 'function') window.showToast(`🛑 图床上传失败: ${e.message}`, 'error');
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '🚀 立即上传托管';
            }
        }
    };
})();
