/**
 * 🎨 [V1.0] Illacme Plenipes Design Studio - Core Orchestrator
 * 职责：设计中心一级模块前端交互中枢，支持意境生图工坊、引擎接入与物权资产库。
 * 🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
 */

(function () {
    let _activeSubTab = 'workspace';
    let _cachedProviders = [];
    let _cachedAssets = [];

    window.loadDesignCenter = async function (subId) {
        if (subId) _activeSubTab = subId;
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const pRes = await fetchApi('/api/design/providers');
            if (pRes && pRes.providers) {
                _cachedProviders = pRes.providers;
                window._cachedDesignProviders = _cachedProviders;
            }
        } catch (e) { console.warn("[DesignStudio] Fetch providers failed:", e); }

        window.renderDesignSubTab(_activeSubTab);
    };

    window.switchDesignSubTab = function (subTab) { _activeSubTab = subTab; window.renderDesignSubTab(subTab); };
    window.renderDesignSubTab = function (subTab) {
        if (subTab) _activeSubTab = subTab;
        document.querySelectorAll('#design-nav-tabs-slot .tactical-tab-btn').forEach(b => { b.classList.toggle('active', b.getAttribute('data-subtab') === _activeSubTab); });
        window.renderStudioTargetBanner();
        const root = document.getElementById('design-center-root');
        if (!root) return;
        if (_activeSubTab === 'workspace') root.innerHTML = window.buildDesignWorkspaceHtml();
        else if (_activeSubTab === 'providers') root.innerHTML = window.buildDesignProvidersHtml();
        else if (_activeSubTab === 'assets') window.loadAndRenderDesignAssets(root);
    };

    window.renderStudioTargetBanner = function () {
        const slot = document.getElementById('design-target-banner-slot'), vH = document.querySelector('#view-design .view-header'), vD = document.getElementById('view-design');
        if (!slot) return;
        const curTab = (typeof _activeSubTab !== 'undefined') ? _activeSubTab : 'workspace';
        if (!window._designTargetDoc || curTab !== 'workspace') {
            slot.style.display = 'none'; slot.innerHTML = '';
            if (vH) vH.style.marginBottom = ''; if (vD) vD.style.gap = '16px'; return;
        }
        const isFromSyndicate = window._designTargetDoc.fromSyndicate;
        slot.style.display = 'block';
        if (vH) vH.style.marginBottom = '0px'; if (vD) vD.style.gap = '12px';
        slot.innerHTML = `<div class="studio-target-banner" style="border-radius:6px;padding:6px 12px;display:flex;justify-content:space-between;align-items:center;font-size:0.75rem;"><div style="display:flex;align-items:center;gap:8px;overflow:hidden;min-width:0;"><span class="banner-pulse-dot" style="display:inline-block;width:6px;height:6px;border-radius:50%;flex-shrink:0;"></span><span class="banner-label" style="font-weight:700;white-space:nowrap;">🎯 正在为文稿定制封面：</span><span class="banner-title" style="font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">《${window._designTargetDoc.title || window._designTargetDoc.relPath}》</span><span class="banner-path" style="font-size:0.68rem;white-space:nowrap;">(${window._designTargetDoc.relPath})</span></div><div style="display:flex;gap:6px;align-items:center;flex-shrink:0;">${isFromSyndicate ? `<button type="button" class="mini-btn glow-btn banner-btn-return" style="padding:2px 8px;font-size:0.68rem;font-weight:600;border-radius:4px;cursor:pointer;display:flex;align-items:center;gap:3px;" onclick="window.returnToSyndicateFromStudio()" title="直接返回社媒分发抽屉">↩️ 返回分发</button>` : ''}<button type="button" class="mini-btn banner-btn-cancel" style="padding:2px 8px;font-size:0.68rem;border-radius:4px;cursor:pointer;" onclick="window.clearStudioTargetDoc()" title="断开关联，切换为全局自由生图模式">取消关联</button></div></div>`;
    };

    window.buildDesignWorkspaceHtml = function () {
        const catMap = { 'local_opensource': '💻 本地极客与开源', 'stock_library': '📸 免费商用图库', 'cloud_api': '☁️ 云端商业 API' };
        let pOptions = '';
        Object.entries(catMap).forEach(([cat, label]) => {
            const list = _cachedProviders.filter(p => p.category === cat);
            if (list.length > 0) pOptions += `<optgroup label="${label}">` + list.map(p => `<option value="${p.id}">${p.icon} ${p.name} [${p.tag || p.category}]</option>`).join('') + `</optgroup>`;
        });
        const ratioOpts = [
            { v: '16:9', i: '🖥️', s: '博客/知乎', t: '博客/知乎宽屏横版 (16:9)', a: true },
            { v: '2.35:1', i: '📱', s: '微信头条', t: '微信公众号首图头条 (2.35:1)' },
            { v: '3:4', i: '📕', s: '社交图文', t: '小红书/社交竖版图文 (3:4)' },
            { v: '1:1', i: '⏹️', s: '方形插图', t: '通用方形图文/插图 (1:1)' }
        ].map(r => `<label class="lang-radio-btn${r.a ? ' active' : ''}" style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:6px 2px;border-radius:6px;cursor:pointer;text-align:center;min-width:0;box-sizing:border-box;" title="${r.t}"><input type="radio" name="studio_ratio" value="${r.v}" ${r.a ? 'checked' : ''} style="display:none;" onchange="window.selectStudioRatio(this)"><span style="font-size:0.75rem;font-weight:700;white-space:nowrap;display:flex;align-items:center;gap:2px;">${r.i} ${r.v}</span><span style="font-size:0.62rem;color:inherit;opacity:0.85;white-space:nowrap;margin-top:2px;">${r.s}</span></label>`).join('');

        return `
            <div style="display: flex; gap: 16px; align-items: stretch;">
                <div class="glass-panel" style="width: 420px; flex-shrink: 0; padding: 16px; border-radius: 12px; display: flex; flex-direction: column; gap: 10px;">
                    <div style="font-size: 0.92rem; font-weight: 700; color: var(--accent-secondary); display: flex; align-items: center; justify-content: space-between;">
                        <span>🖌️ 智能生图工作台</span>
                        <span style="font-size: 0.72rem; color: var(--text-dim);">13 大引擎矩阵</span>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <label style="font-size: 0.74rem; color: var(--text-dim);">图源与生成引擎</label>
                        <select id="studio-provider-select" class="studio-form-control" style="width: 100%; padding: 6px 8px; border-radius: 6px; font-size: 0.8rem;">
                            ${pOptions || '<option value="local_og">🎨 极客排版 · 本地 OG 卡片</option><option value="unsplash">📸 Unsplash 免鉴权商业图库</option>'}
                        </select>
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 4px;">
                        <label style="font-size: 0.74rem; color: var(--text-dim);">画幅与展示比例</label>
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px;">${ratioOpts}</div>
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 5px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <label style="font-size: 0.74rem; color: var(--text-dim);">生图提示词 (Prompt)</label>
                            <button type="button" class="mini-btn" id="studio-refine-prompt-btn" style="font-size: 0.65rem; padding: 2px 8px;" onclick="window.polishStudioPrompt(this)">🪄 意境提炼</button>
                        </div>
                        <div style="display: flex; gap: 4px; flex-wrap: wrap;">
                            ${window._designTargetDoc ? `<button type="button" class="mini-btn glow-btn" style="font-size:0.65rem; padding:1px 6px; color:#000; background:#00f2fe; border:none; font-weight:700;" onclick="window.fillTargetDocPrompt()" title="提取文章标题为提示词">💡 填入标题</button>` : ''}
                            <button type="button" class="mini-btn" style="font-size:0.65rem; padding:1px 5px;" onclick="window.insertStudioPreset('赛博科技网络节点与流体光影，高端极简')">⚡ 赛博</button>
                            <button type="button" class="mini-btn" style="font-size:0.65rem; padding:1px 5px;" onclick="window.insertStudioPreset('深蓝暗色科技背景，金色抽象几何拓扑结构')">🔷 拓扑</button>
                            <button type="button" class="mini-btn" style="font-size:0.65rem; padding:1px 5px;" onclick="window.insertStudioPreset('3D cute claymorphism render, isometric minimalist technology')">🏺 粘土</button>
                            <button type="button" class="mini-btn" style="font-size:0.65rem; padding:1px 5px;" onclick="window.insertStudioPreset('Traditional Chinese ink wash painting, ethereal mountain and mist, modern zen')">🌊 水墨</button>
                            <button type="button" class="mini-btn" style="font-size:0.65rem; padding:1px 5px;" onclick="window.insertStudioPreset('Cinematic 35mm film photography, natural grain, dramatic moody lighting')">🎞️ 胶片</button>
                            <button type="button" class="mini-btn" style="font-size:0.65rem; padding:1px 5px;" onclick="window.insertStudioPreset('Swiss style graphic design, bold typography, flat vector illustration')">📐 扁平</button>
                        </div>
                        <textarea id="studio-prompt-input" class="studio-form-control" placeholder="输入意境描述，点击上方风格标签追加词缀，或点击「🪄 意境提炼」自动扩写商业级英文 Prompt..." style="width: 100%; height: 78px; padding: 8px; border-radius: 6px; font-size: 0.8rem; resize: vertical; box-sizing: border-box;"></textarea>
                    </div>

                    <div style="display:flex; flex-direction:column; gap:5px; margin-top:4px;">
                        <button type="button" class="mini-btn glow-btn" id="studio-generate-btn" style="padding: 8px; font-size: 0.85rem; font-weight: 700; background: var(--accent-secondary, #00f2fe); color: #000; border: none; border-radius: 7px; cursor: pointer;" onclick="window.dispatchStudioGenerate()">✨ 立即调度生成</button>
                        ${window._designTargetDoc ? `<button type="button" class="mini-btn glow-btn" id="studio-generate-apply-btn" style="padding: 8px; font-size: 0.8rem; font-weight: 700; background: linear-gradient(135deg, #00f2fe, #00ff88); color: #000; border: none; border-radius: 7px; cursor: pointer;" onclick="window.dispatchStudioGenerate(true)" title="生成完成后自动直接写入原稿 Frontmatter">🎯 生成并立即设为封面</button>` : ''}
                    </div>
                </div>

                <!-- 右侧预览展示区 -->
                <div class="glass-panel" style="flex: 1; padding: 20px; border-radius: 12px; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative;" id="studio-result-panel">
                    <div id="studio-placeholder" style="display: flex; flex-direction: column; align-items: center; gap: 12px; color: var(--text-dim);">
                        <span style="font-size: 3rem; opacity: 0.4;">🎨</span>
                        <div style="font-size: 0.88rem;">在左侧选择引擎并输入提示词，点击「立即调度生成」</div>
                        <div style="font-size: 0.72rem; opacity: 0.7;">生成产物将自动落盘至媒体资产库</div>
                    </div>
                </div>
            </div>
        `;
    };

    window.selectStudioRatio = function (el) {
        document.querySelectorAll('input[name="studio_ratio"]').forEach(r => r.parentElement.classList.remove('active'));
        el.parentElement.classList.add('active');
    };
    window.insertStudioPreset = function (text) {
        const ipt = document.getElementById('studio-prompt-input');
        if (!ipt) return;
        const cur = ipt.value.trim();
        ipt.value = !cur ? text : (cur.includes(text) ? cur : cur + (cur.endsWith('，') || cur.endsWith(', ') ? '' : '，') + text);
        ipt.focus();
        if (window.showToast) window.showToast('✨ 已追加风格意境词缀', 'info');
    };
    window.polishStudioPrompt = async function (btn) {
        const ipt = document.getElementById('studio-prompt-input');
        if (!ipt) return;
        const cur = ipt.value.trim(), base = cur || 'Illacme Plenipes 数字出版与知识星谱';
        if (!btn) btn = document.getElementById('studio-refine-prompt-btn');
        if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner-gear">⚙️</span> 提炼中...'; }
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const res = await fetchApi('/api/design/prompt/refine', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prompt: base, style: 'cinematic' }) });
            if (res && res.success && res.refined_prompt) {
                ipt.value = res.refined_prompt;
                if (typeof window.showToast === 'function') window.showToast(`✨ [${(res.engine_used || 'AI').toUpperCase()}] 意境提示词提炼完成`, 'success');
            } else { throw new Error((res && res.message) || '提炼失败'); }
        } catch (e) {
            ipt.value = `Cinematic concept art of "${base}", dramatic studio rim lighting, 8k resolution, octane render, photorealistic depth of field`;
            if (typeof window.showToast === 'function') window.showToast('✨ 意境提示词已生成 (保底模式)', 'success');
        } finally {
            if (btn) { btn.disabled = false; btn.innerHTML = '🪄 意境提炼'; }
        }
    };

    window.fillTargetDocPrompt = function () {
        if (!window._designTargetDoc) return;
        const ipt = document.getElementById('studio-prompt-input');
        if (ipt) { ipt.value = window._designTargetDoc.title || window._designTargetDoc.relPath || ''; ipt.focus(); if (window.showToast) window.showToast('💡 已填充文章标题为提示词', 'info'); }
    };

    window.dispatchStudioGenerate = async function (autoApply = false) {
        const promptIpt = document.getElementById('studio-prompt-input');
        const providerSel = document.getElementById('studio-provider-select');
        const ratioRadio = document.querySelector('input[name="studio_ratio"]:checked');
        const btn = document.getElementById(autoApply ? 'studio-generate-apply-btn' : 'studio-generate-btn') || document.getElementById('studio-generate-btn');
        const resPanel = document.getElementById('studio-result-panel');

        const prompt = promptIpt ? promptIpt.value.trim() : '';
        if (!prompt) { if (window.showToast) window.showToast('⚠️ 请输入生图提示词', 'warning'); return; }

        const providerId = providerSel ? providerSel.value : 'unsplash';
        const ratio = ratioRadio ? ratioRadio.value : '16:9';

        if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner-gear">⚙️</span> 正在渲染中...'; }
        if (resPanel) resPanel.innerHTML = `<div style="display:flex;flex-direction:column;align-items:center;gap:14px;"><span class="spinner-gear" style="font-size:2.4rem;">⚙️</span><div style="font-size:0.88rem;color:var(--accent-secondary);">正在由 [${providerId.toUpperCase()}] 引擎渲染生成，请稍候...</div></div>`;

        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const res = await fetchApi('/api/design/generate', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ provider_id: providerId, prompt, aspect_ratio: ratio, style: 'vivid' })
            });

            if (res && res.success && res.url) {
                if (window.showToast) window.showToast('✨ 图像生成成功，已登记至资产账本', 'success');
                if (autoApply && window._designTargetDoc) {
                    await window.applyTargetDocCover(res.url);
                    return;
                }
                const targetBtn = window._designTargetDoc ? `<button type="button" class="mini-btn glow-btn" style="font-size:0.72rem;padding:5px 12px;background:var(--accent-secondary,#00f2fe);color:#000;font-weight:700;border:none;" onclick="window.applyTargetDocCover('${res.url}')">🎯 一键设为《${window._designTargetDoc.title || '当前文章'}》封面</button>` : '';
                const safePrompt = (prompt || '').replace(/'/g, "\\'");
                resPanel.innerHTML = `
                    <div style="display:flex; flex-direction:column; align-items:center; gap:12px; width:100%; height:100%; justify-content:center;">
                        <img src="${res.url}?t=${Date.now()}" alt="生成产物" style="max-width:90%; max-height:380px; object-fit:contain; border-radius:8px; box-shadow:0 10px 30px rgba(0,0,0,0.6); border:1px solid rgba(0,242,254,0.3); cursor:pointer; transition:transform 0.2s;" onclick="window.openStudioImageModal && window.openStudioImageModal('${res.url}', '${safePrompt}', '${res.provider}', '${res.aspect_ratio}')" title="🔍 点击查看高清大图与参数详情" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'" />
                        <div style="font-size:0.72rem; color:var(--text-dim); display:flex; gap:10px; align-items:center;"><span>尺寸: ${res.aspect_ratio} | 引擎: ${res.provider}</span><span style="color:var(--accent-secondary,#00f2fe); cursor:pointer; text-decoration:underline;" onclick="window.openStudioImageModal && window.openStudioImageModal('${res.url}', '${safePrompt}', '${res.provider}', '${res.aspect_ratio}')">🔍 查看大图</span></div>
                        <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap; justify-content:center;">
                            ${targetBtn}
                            <button type="button" class="mini-btn" style="font-size:0.72rem; padding:5px 12px; color:#a78bfa; border-color:rgba(167,139,250,0.4);" onclick="window.openStudioImageModal && window.openStudioImageModal('${res.url}', '${safePrompt}', '${res.provider}', '${res.aspect_ratio}')">🔍 查看大图</button>
                            <button type="button" class="mini-btn" style="font-size:0.72rem; padding:5px 12px; color:#00f2fe; border-color:rgba(0,242,254,0.3);" onclick="window.copyStudioResultMarkdown('${res.url}')">📋 复制 Markdown</button>
                            <button type="button" class="mini-btn" style="font-size:0.72rem; padding:5px 12px; color:#00f2fe; border-color:rgba(0,242,254,0.3);" onclick="window.openAssetApplyCoverModal('${res.url}')">🖼️ 设为文章封面</button>
                            <button type="button" class="mini-btn" style="font-size:0.72rem; padding:5px 12px; color:#38bdf8; border-color:rgba(56,189,248,0.4);" onclick="window.openAssetHostingModal(${res.asset_id || 'null'}, '${res.url}')">☁️ 托管图床</button><a href="${res.url}" download class="mini-btn" style="font-size:0.72rem; padding:5px 12px; text-decoration:none;">⬇️ 下载原图</a>
                        </div>
                    </div>`;
            } else { throw new Error((res && res.message) || '生成失败'); }
        } catch (e) {
            if (window.showToast) window.showToast(`🛑 生图异常: ${e.message}`, 'error');
            if (resPanel) resPanel.innerHTML = `<div style="color:#f87171; font-size:0.88rem;">生图异常: ${e.message}</div>`;
        } finally {
            if (btn) { btn.disabled = false; btn.innerHTML = autoApply ? '🎯 生成并立即设为封面' : '✨ 立即调度生成'; }
        }
    };

    window.applyTargetDocCover = async function (coverUrl) {
        if (!window._designTargetDoc) return;
        const { relPath, title, fromSyndicate } = window._designTargetDoc;
        const docCopy = { ...window._designTargetDoc };
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const res = await fetchApi('/api/design/assets/apply-cover', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ doc_id: relPath, cover_url: coverUrl })
            });
            if (res && res.success) {
                if (window.showToast) window.showToast(`✨ 成功将图片设为《${title || relPath}》封面！`, 'success');
                window._designTargetDoc = null; window.renderDesignSubTab('workspace');
                if (typeof window.loadVault === 'function') window.loadVault(null, window.vaultCurrentPage || 1);
                if (fromSyndicate) setTimeout(() => { window._designTargetDoc = docCopy; window.returnToSyndicateFromStudio(); }, 400);
            } else { throw new Error((res && res.message) || '应用失败'); }
        } catch (e) { if (window.showToast) window.showToast(`🛑 设为封面失败: ${e.message}`, 'error'); }
    };

    window.returnToSyndicateFromStudio = async function () {
        if (!window._designTargetDoc) return;
        const { relPath, title } = window._designTargetDoc;
        if (typeof window.showView === 'function') await window.showView('vault'); else window.location.hash = '#/vault';
        setTimeout(() => { if (typeof window.openArticleSyndicationDrawer === 'function') window.openArticleSyndicationDrawer(relPath, title); }, 120);
    };

    window.clearStudioTargetDoc = function () { window._designTargetDoc = null; window.renderDesignSubTab('workspace'); };
    window.copyStudioResultMarkdown = function (url) {
        const md = `![配图](${url})`;
        navigator.clipboard.writeText(md).then(() => window.showToast && window.showToast('📋 已复制 Markdown 语法', 'success')).catch(() => prompt('请手动复制 Markdown:', md));
    };

    window.buildDesignProvidersHtml = function () {
        const list = _cachedProviders || [];
        const total = list.length;
        const counts = { cloud: list.filter(p => p.category === 'cloud_api').length, local: list.filter(p => p.category === 'local_opensource').length, stock: list.filter(p => p.category === 'stock_library').length };
        return `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; flex-wrap:wrap; gap:10px;">
                <div style="font-size:0.78rem; color:var(--text-dim); display:flex; align-items:center; gap:6px;">
                    <span>🔌</span><span>已集成 <strong style="color:var(--accent-secondary,#00f2fe);">${total}</strong> 大图像引擎，可点击「测试」嗅探连通状态</span>
                </div>
                <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;" id="provider-category-filter">
                    <button type="button" class="mini-btn active" style="padding:4px 10px; font-size:0.74rem;" onclick="window.filterDesignProviders('all', this)">全部 (${total})</button>
                    <button type="button" class="mini-btn" style="padding:4px 10px; font-size:0.74rem;" onclick="window.filterDesignProviders('stock_library', this)">📸 免费商用 (${counts.stock})</button>
                    <button type="button" class="mini-btn" style="padding:4px 10px; font-size:0.74rem;" onclick="window.filterDesignProviders('local_opensource', this)">💻 本地开源 (${counts.local})</button>
                    <button type="button" class="mini-btn" style="padding:4px 10px; font-size:0.74rem;" onclick="window.filterDesignProviders('cloud_api', this)">☁️ 云端 API (${counts.cloud})</button>
                </div>
            </div>
            <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(320px, 1fr)); gap:16px; padding-bottom:20px;" id="provider-cards-grid">
                ${list.map(p => {
            const b = p.config_status === 'out_of_box' ? ['#00f2fe', 'rgba(0,242,254,0.12)', 'rgba(0,242,254,0.3)', '⚡ 免配置即用'] : (p.is_configured ? ['#00ff88', 'rgba(0,255,136,0.12)', 'rgba(0,255,136,0.3)', '🔑 已配置凭证'] : (p.category === 'stock_library' ? ['#a5b4fc', 'rgba(165,180,252,0.12)', 'rgba(165,180,252,0.25)', '⚪ 免Key通道'] : (p.category === 'cloud_api' ? ['#fbbf24', 'rgba(251,191,36,0.12)', 'rgba(251,191,36,0.3)', '⚠️ 待配置 Key'] : ['#cbd5e1', 'rgba(203,213,225,0.1)', 'rgba(203,213,225,0.2)', '⚙️ 待配置服务'])));
            return `
                    <div class="glass-panel provider-card" data-cat="${p.category}" style="padding:16px; border-radius:10px; display:flex; flex-direction:column; gap:10px; border:1px solid rgba(255,255,255,0.08);">
                        <div style="display:flex; align-items:center; justify-content:space-between;">
                            <div style="display:flex; align-items:center; gap:8px; font-weight:700; color:var(--text-bright); font-size:0.9rem;"><span>${p.icon}</span><span>${p.name}</span></div>
                            <span style="font-size:0.65rem; color:${b[0]}; background:${b[1]}; padding:2px 6px; border-radius:4px; border:1px solid ${b[2]};">${b[3]}</span>
                        </div>
                        ${p.tag ? `<div style="font-size:0.68rem; color:#38bdf8; background:rgba(56,189,248,0.08); padding:2px 6px; border-radius:4px; width:fit-content; border:1px solid rgba(56,189,248,0.2);">${p.tag}</div>` : ''}
                        <div style="font-size:0.74rem; color:var(--text-dim); line-height:1.4;">${p.desc}</div>
                        <div style="margin-top:auto; display:flex; gap:8px; align-items:center; border-top:1px solid rgba(255,255,255,0.06); padding-top:10px;">
                            <button type="button" class="mini-btn" style="padding:6px 12px; font-size:0.72rem; background:rgba(0,242,254,0.12); border:1px solid rgba(0,242,254,0.35); color:#00f2fe; border-radius:4px; cursor:pointer;" onclick="window.openDesignProviderConfigModal('${p.id}')">⚙️ 配置模型</button>
                            <button type="button" class="mini-btn" style="flex:1; padding:6px; font-size:0.72rem;" onclick="window.testDesignProviderConnection('${p.id}')">🔌 测试</button>
                            <span id="provider-status-${p.id}" style="font-size:0.7rem; color:var(--text-dim);">待探测</span>
                        </div>
                    </div>`;
        }).join('')}
            </div>`;
    };

    window.filterDesignProviders = function (cat, btn) {
        document.querySelectorAll('#provider-category-filter button').forEach(b => b.classList.remove('active'));
        if (btn) btn.classList.add('active');
        document.querySelectorAll('#provider-cards-grid .provider-card').forEach(c => { c.style.display = (cat === 'all' || c.getAttribute('data-cat') === cat) ? 'flex' : 'none'; });
    };

    window.testDesignProviderConnection = async function (providerId) {
        const badge = document.getElementById(`provider-status-${providerId}`);
        if (badge) { badge.innerText = '探测中...'; badge.style.color = '#f59e0b'; }
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const res = await fetchApi('/api/design/providers/test', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ provider_id: providerId }) });
            if (badge) {
                badge.innerText = (res && res.success) ? `🟢 在线 (${res.latency_ms}ms)` : `🔴 ${(res && res.message) || '离线'}`;
                badge.style.color = (res && res.success) ? '#00ff88' : '#f87171';
            }
        } catch (e) { if (badge) { badge.innerText = '🔴 异常'; badge.style.color = '#f87171'; } }
    };
})();
