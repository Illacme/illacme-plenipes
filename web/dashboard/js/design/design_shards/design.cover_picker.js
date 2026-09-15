// -*- coding: utf-8 -*-
/**
 * 🎨 Design Studio - Vault Document Cover Picker Shard
 * 职责：提供高规格、支持海量文库实时检索过滤、已有封面状态感知、前后视觉对比的文档封面注入中枢。
 * 🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
 * 🛡️ [UI-UX Sovereignty] 商业级毛玻璃视效与即时高亮反馈。
 */

(function () {
    let _allDocs = [];
    let _filteredDocs = [];
    let _selectedDocId = null;
    let _currentCoverUrl = '';
    let _activeFilter = 'all'; // 'all' | 'unassigned' | 'assigned'
    let _searchQuery = '';

    window.openAssetApplyCoverModal = async function (coverUrl) {
        _currentCoverUrl = coverUrl;
        _selectedDocId = null;
        _activeFilter = 'all';
        _searchQuery = '';

        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            // 拉取全站文档元数据（支持大上限）
            const vRes = await fetchApi('/api/vault/search?limit=200');
            _allDocs = (vRes && (vRes.items || vRes.documents || vRes.docs)) || [];
        } catch (e) {
            console.warn("[CoverPicker] Failed to fetch vault docs:", e);
            _allDocs = [];
        }
        _filteredDocs = [..._allDocs];

        // 移除可能存在的旧弹窗
        const old = document.getElementById('apply-cover-modal');
        if (old) old.remove();

        const modalHtml = `
            <div id="apply-cover-modal" class="modal-overlay active" style="z-index:10000; display:flex; align-items:center; justify-content:center; background:rgba(0,0,0,0.8); backdrop-filter:blur(10px); position:fixed; inset:0; padding:16px;">
                <div class="glass-panel" style="width:780px; max-width:96vw; max-height:90vh; border-radius:14px; border:1px solid rgba(0,242,254,0.35); display:flex; flex-direction:column; overflow:hidden; box-shadow:0 25px 60px rgba(0,0,0,0.9);">
                    
                    <!-- Header -->
                    <div style="padding:16px 20px; border-bottom:1px solid rgba(255,255,255,0.08); display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.02);">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="font-size:1.1rem;">🖼️</span>
                            <div>
                                <div style="font-weight:700; color:#fff; font-size:0.95rem; letter-spacing:0.3px;">文库原稿封面注入中枢</div>
                                <div style="font-size:0.72rem; color:var(--text-dim); margin-top:1px;">海量原稿即时过滤检索 · 状态感知 · 一键写回 Frontmatter</div>
                            </div>
                        </div>
                        <button type="button" class="mini-btn" style="padding:4px 9px; font-size:0.82rem;" onclick="document.getElementById('apply-cover-modal').remove()">✕</button>
                    </div>

                    <!-- 拟注入资产预览卡片 -->
                    <div style="padding:12px 20px; background:rgba(0,0,0,0.35); border-bottom:1px solid rgba(255,255,255,0.06); display:flex; align-items:center; gap:14px;">
                        <img src="${coverUrl}" style="width:110px; height:62px; object-fit:cover; border-radius:6px; border:1px solid rgba(0,242,254,0.4); box-shadow:0 4px 12px rgba(0,0,0,0.4);" />
                        <div style="flex:1; overflow:hidden; font-size:0.74rem;">
                            <div style="color:var(--text-dim); margin-bottom:3px;">拟注入新封面资产:</div>
                            <div style="color:#00f2fe; font-family:monospace; font-size:0.78rem; font-weight:600; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">
                                ${coverUrl.split('/').pop()}
                            </div>
                            <div style="color:var(--text-dim); font-size:0.7rem; margin-top:2px;">
                                格式: Web/Static Image · 点击下方目标原稿完成匹配
                            </div>
                        </div>
                    </div>

                    <!-- 搜索与筛选工具栏 -->
                    <div style="padding:12px 20px; display:flex; gap:10px; align-items:center; flex-wrap:wrap; background:rgba(255,255,255,0.015); border-bottom:1px solid rgba(255,255,255,0.06);">
                        <div style="position:relative; flex:1; min-width:220px;">
                            <span style="position:absolute; left:10px; top:50%; transform:translateY(-50%); font-size:0.78rem; color:var(--text-dim);">🔍</span>
                            <input type="text" id="cover-picker-search-input" 
                                placeholder="输入文章标题、路径、关键词快速搜索..." 
                                style="width:100%; padding:7px 10px 7px 32px; border-radius:6px; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.15); color:#fff; font-size:0.78rem; outline:none; transition:border-color 0.2s;"
                                onfocus="this.style.borderColor='#00f2fe'" onblur="this.style.borderColor='rgba(255,255,255,0.15)'"
                                oninput="window.filterCoverPickerDocs(this.value)" />
                        </div>
                        <div style="display:flex; gap:6px; align-items:center;" id="cover-picker-filter-group">
                            <button type="button" class="mini-btn active" style="padding:4px 10px; font-size:0.72rem;" onclick="window.switchCoverPickerFilter('all', this)">全部 (<span id="cp-count-all">${_allDocs.length}</span>)</button>
                            <button type="button" class="mini-btn" style="padding:4px 10px; font-size:0.72rem;" onclick="window.switchCoverPickerFilter('unassigned', this)">⬜ 待设封面 (<span id="cp-count-unassigned">${_allDocs.filter(d => !d.cover).length}</span>)</button>
                            <button type="button" class="mini-btn" style="padding:4px 10px; font-size:0.72rem;" onclick="window.switchCoverPickerFilter('assigned', this)">🖼️ 已有封面 (<span id="cp-count-assigned">${_allDocs.filter(d => !!d.cover).length}</span>)</button>
                        </div>
                    </div>

                    <!-- 原稿可滚动网格/列表区域 -->
                    <div id="cover-picker-docs-container" style="flex:1; overflow-y:auto; padding:14px 20px; display:flex; flex-direction:column; gap:8px; max-height:340px; min-height:220px;">
                        ${window.renderCoverPickerDocItems()}
                    </div>

                    <!-- 选中文档与对比提示 Footer -->
                    <div style="padding:14px 20px; border-top:1px solid rgba(255,255,255,0.08); background:rgba(0,0,0,0.4); display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                        <div style="font-size:0.75rem; color:var(--text-dim); display:flex; align-items:center; gap:6px; flex:1; min-width:260px;">
                            <span>目标原稿:</span>
                            <span id="cover-picker-selected-hint" style="color:#00f2fe; font-weight:600; font-family:monospace;">未选择文档 (请在上方列表点击选中)</span>
                        </div>
                        <div style="display:flex; gap:10px;">
                            <button type="button" class="mini-btn" style="padding:6px 14px; font-size:0.76rem;" onclick="document.getElementById('apply-cover-modal').remove()">取消</button>
                            <button type="button" class="mini-btn" id="confirm-apply-cover-btn" 
                                style="padding:6px 20px; font-size:0.76rem; background:rgba(255,255,255,0.05); border-color:rgba(255,255,255,0.15); color:var(--text-dim); cursor:not-allowed;" 
                                disabled onclick="window.submitApplyCover('${coverUrl}')">
                                确认注入封面
                            </button>
                        </div>
                    </div>

                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        setTimeout(() => {
            const ipt = document.getElementById('cover-picker-search-input');
            if (ipt) ipt.focus();
        }, 100);
    };

    window.renderCoverPickerDocItems = function () {
        if (!_filteredDocs || _filteredDocs.length === 0) {
            return `
                <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:40px 0; color:var(--text-dim); font-size:0.8rem; gap:8px;">
                    <span>🔍 未找到匹配的原稿文档</span>
                    <button type="button" class="mini-btn" style="font-size:0.72rem; padding:4px 10px;" onclick="document.getElementById('cover-picker-search-input').value=''; window.filterCoverPickerDocs('');">清空搜索条件</button>
                </div>
            `;
        }

        return _filteredDocs.map(d => {
            const relPath = d.rel_path || d.id || '';
            const title = (d.seo_data && d.seo_data.title) || d.title || relPath;
            const hasCover = !!d.cover;
            const isSelected = _selectedDocId === relPath;
            const borderStyle = isSelected ? '1px solid #00f2fe' : '1px solid rgba(255,255,255,0.08)';
            const bgStyle = isSelected ? 'background:rgba(0,242,254,0.12); box-shadow:0 0 12px rgba(0,242,254,0.25);' : 'background:rgba(255,255,255,0.03);';
            const badge = hasCover 
                ? `<span style="font-size:0.68rem; color:#f59e0b; background:rgba(245,158,11,0.12); border:1px solid rgba(245,158,11,0.3); padding:2px 6px; border-radius:4px;">🖼️ 已有封面</span>`
                : `<span style="font-size:0.68rem; color:#10b981; background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.3); padding:2px 6px; border-radius:4px;">⬜ 待设封面</span>`;

            return `
                <div class="cover-picker-item" onclick="window.selectCoverPickerDoc('${relPath.replace(/'/g, "\\'")}')"
                    style="display:flex; justify-content:space-between; align-items:center; padding:10px 14px; border-radius:8px; ${borderStyle} ${bgStyle} cursor:pointer; transition:all 0.15s ease;"
                    onmouseover="if('${_selectedDocId}' !== '${relPath}') this.style.borderColor='rgba(0,242,254,0.4)'"
                    onmouseout="if('${_selectedDocId}' !== '${relPath}') this.style.borderColor='rgba(255,255,255,0.08)'">
                    <div style="display:flex; flex-direction:column; gap:3px; overflow:hidden; flex:1; margin-right:12px;">
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="font-weight:600; color:#fff; font-size:0.84rem; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">《${title}》</span>
                            ${badge}
                        </div>
                        <div style="font-size:0.7rem; color:var(--text-dim); display:flex; gap:10px; align-items:center;">
                            <span style="font-family:monospace; color:rgba(255,255,255,0.6);">📁 ${relPath}</span>
                            ${d.last_updated ? `<span>🕒 ${d.last_updated}</span>` : ''}
                        </div>
                    </div>
                    <div style="flex-shrink:0;">
                        ${isSelected 
                            ? `<span style="font-size:0.75rem; color:#00f2fe; font-weight:700; background:rgba(0,242,254,0.2); padding:4px 10px; border-radius:6px; border:1px solid #00f2fe;">✔️ 已选中</span>` 
                            : `<button type="button" class="mini-btn" style="padding:4px 10px; font-size:0.72rem;">选择</button>`
                        }
                    </div>
                </div>
            `;
        }).join('');
    };

    window.selectCoverPickerDoc = function (relPath) {
        _selectedDocId = relPath;
        const targetDoc = _allDocs.find(d => (d.rel_path || d.id) === relPath);
        const title = (targetDoc && targetDoc.seo_data && targetDoc.seo_data.title) || (targetDoc && targetDoc.title) || relPath;

        // 更新提示与按钮状态
        const hint = document.getElementById('cover-picker-selected-hint');
        if (hint) {
            hint.innerHTML = `《${title}》 <span style="font-size:0.68rem; color:var(--text-dim);">(${relPath})</span>`;
        }
        const btn = document.getElementById('confirm-apply-cover-btn');
        if (btn) {
            btn.disabled = false;
            btn.style.cursor = 'pointer';
            btn.style.color = '#fff';
            btn.style.background = 'linear-gradient(135deg, rgba(0,242,254,0.3), rgba(2,132,199,0.5))';
            btn.style.borderColor = '#00f2fe';
            btn.style.boxShadow = '0 0 14px rgba(0,242,254,0.4)';
        }

        // 重新渲染卡片高亮
        const container = document.getElementById('cover-picker-docs-container');
        if (container) container.innerHTML = window.renderCoverPickerDocItems();
    };

    window.filterCoverPickerDocs = function (query) {
        _searchQuery = (query || '').trim().toLowerCase();
        window.applyCoverPickerFiltering();
    };

    window.switchCoverPickerFilter = function (filterType, btn) {
        _activeFilter = filterType;
        if (btn && btn.parentElement) {
            btn.parentElement.querySelectorAll('.mini-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }
        window.applyCoverPickerFiltering();
    };

    window.applyCoverPickerFiltering = function () {
        _filteredDocs = _allDocs.filter(d => {
            // 状态过滤
            if (_activeFilter === 'unassigned' && d.cover) return false;
            if (_activeFilter === 'assigned' && !d.cover) return false;

            // 文本检索过滤
            if (_searchQuery) {
                const title = ((d.seo_data && d.seo_data.title) || d.title || '').toLowerCase();
                const path = (d.rel_path || d.id || '').toLowerCase();
                const tags = Array.isArray(d.tags) ? d.tags.join(' ').toLowerCase() : '';
                if (!title.includes(_searchQuery) && !path.includes(_searchQuery) && !tags.includes(_searchQuery)) {
                    return false;
                }
            }
            return true;
        });

        const container = document.getElementById('cover-picker-docs-container');
        if (container) container.innerHTML = window.renderCoverPickerDocItems();
    };

    window.submitApplyCover = async function (coverUrl) {
        if (!_selectedDocId) {
            if (typeof window.showToast === 'function') window.showToast('⚠️ 请先在上方列表中选择目标文档', 'warning');
            return;
        }
        const btn = document.getElementById('confirm-apply-cover-btn');
        if (btn) { btn.disabled = true; btn.innerText = '正在写入...'; }
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const res = await fetchApi('/api/design/assets/apply-cover', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ doc_id: _selectedDocId, cover_url: coverUrl })
            });
            if (res && res.success) {
                if (typeof window.showToast === 'function') {
                    window.showToast(res.message || '✨ 封面已成功注入目标原稿 Frontmatter！', 'success');
                }
                const modal = document.getElementById('apply-cover-modal');
                if (modal) modal.remove();
            } else {
                throw new Error((res && res.message) || '写入封面失败');
            }
        } catch (e) {
            if (typeof window.showToast === 'function') window.showToast(`🛑 写入失败: ${e.message}`, 'error');
            if (btn) { btn.disabled = false; btn.innerText = '确认注入封面'; }
        }
    };
})();
