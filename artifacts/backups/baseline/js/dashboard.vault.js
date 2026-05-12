/**
 * 📂 [V55.0] Illacme Plenipes Vault & Editor Module
 * 职责：稿件仓库管理、元数据治理与物理原件编辑。
 */

// 1. 状态矩阵
window.currentDocId = null;
window.activeDocId = null;
window.vaultSearchTimeout = null;

// 2. 稿件仓库加载器
window.loadVault = async (query = '') => {
    const listEl = document.getElementById('vault-list');
    if (!listEl) return;

    listEl.innerHTML = Array(5).fill(0).map(() => `
        <tr>
            <td><div class="skeleton" style="width: 50px; height: 20px;"></div></td>
            <td><div class="skeleton" style="width: 140px; height: 20px;"></div></td>
            <td><div class="skeleton" style="width: 200px; height: 20px;"></div></td>
            <td><div class="skeleton" style="width: 40px; height: 20px;"></div></td>
            <td><div class="skeleton" style="width: 60px; height: 20px;"></div></td>
            <td><div class="skeleton" style="width: 80px; height: 30px;"></div></td>
        </tr>
    `).join('');

    try {
        const data = await apiFetch('/api/vault/list');
        if (!data || !data.manuscripts) {
            listEl.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:2rem; opacity:0.5;">⚠️ 仓库扫描失败，请核验物理链路。</td></tr>';
            return;
        }

        let manuscripts = data.manuscripts;
        if (query) {
            const q = query.toLowerCase();
            manuscripts = manuscripts.filter(m =>
                m.title.toLowerCase().includes(q) ||
                m.path.toLowerCase().includes(q) ||
                m.slug.toLowerCase().includes(q)
            );
        }

        if (manuscripts.length === 0) {
            listEl.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:2rem; opacity:0.5;">📭 仓库空空如也，未发现合规稿件。</td></tr>';
            return;
        }

        listEl.innerHTML = manuscripts.map(m => `
            <tr>
                <td><span class="status-badge status-${m.status.toLowerCase()}">${m.status}</span></td>
                <td><div style="font-weight:600; color:var(--text-bright);">${m.title}</div><div style="font-size:0.7rem; opacity:0.4;">/${m.slug}</div></td>
                <td><code class="path-tag" title="${m.path}">${m.path.length > 40 ? '...' + m.path.slice(-37) : m.path}</code></td>
                <td><span class="lang-tag">${m.lang.toUpperCase()}</span></td>
                <td><span class="mono">${m.word_count.toLocaleString()}</span></td>
                <td>
                    <div style="display:flex; gap:8px;">
                        <button class="mini-action-btn" title="快速编辑" onclick="openEditor('${m.id}')">📝</button>
                        <button class="mini-action-btn" title="分发详情" onclick="openVaultDrawer('${m.id}')">⚙️</button>
                    </div>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        console.error("Vault load error:", e);
        listEl.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:2rem; color:var(--accent-primary);">🚨 物理链路异常: ${e.message}</td></tr>`;
    }
};

// 3. 抽屉式元数据编辑器
window.openVaultDrawer = async (relPath) => {
    window.currentDocId = relPath;
    const drawer = document.getElementById('vault-drawer');
    const doc = await apiFetch(`/ledger/document/${encodeURIComponent(relPath)}`);

    if (!doc) return;

    document.getElementById('drawer-path').innerText = doc.rel_path;
    document.getElementById('drawer-title').value = doc.title || '';
    document.getElementById('drawer-slug').value = doc.slug || '';
    const prefixInput = document.getElementById('drawer-prefix');
    prefixInput.value = doc.route_prefix || '';
    if (!window.settingsData._is_licensed) {
        prefixInput.readOnly = true;
        prefixInput.style.opacity = '0.5';
        prefixInput.title = "社区版不支持子目录重映射 (Prefix Mapping)";
    } else {
        prefixInput.readOnly = false;
        prefixInput.style.opacity = '1';
        prefixInput.title = "";
    }
    document.getElementById('drawer-desc').value = (doc.seo_data || {}).description || '';

    drawer.style.display = 'flex';
};

window.closeVaultDrawer = () => {
    document.getElementById('vault-drawer').style.display = 'none';
};

window.saveVaultMetadata = async () => {
    if (!window.currentDocId) return;

    const payload = {
        title: document.getElementById('drawer-title').value,
        slug: document.getElementById('drawer-slug').value,
        route_prefix: document.getElementById('drawer-prefix').value,
        seo_data: {
            description: document.getElementById('drawer-desc').value
        }
    };

    const res = await apiFetch(`/ledger/document/${encodeURIComponent(window.currentDocId)}/metadata`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res && res.success) {
        addAudit(`✅ 资产元数据已固化: ${window.currentDocId}`, "success");
        closeVaultDrawer();
        const searchInput = document.getElementById('vault-search');
        loadVault(searchInput ? searchInput.value : '');
    } else {
        addAudit("❌ 元数据固化失败，请检查链路。", "error");
    }
};

// 4. 全量物理编辑器 (Modal)
window.openEditor = async (docId) => {
    window.activeDocId = docId;
    const modal = document.getElementById('editor-modal');
    const body = document.getElementById('editor-body');
    const title = document.getElementById('editor-title');
    const mTitle = document.getElementById('editor-meta-title');
    const mSlug = document.getElementById('editor-meta-slug');

    title.innerText = "EXTRACTING PHYSICAL ASSET...";
    modal.style.display = 'flex';

    const doc = await apiFetch(`/ledger/document/${docId}`);
    if (doc) {
        title.innerText = `EDITOR: ${doc.title || docId}`;
        body.value = doc.content || "";
        if (mTitle) mTitle.value = doc.title || "";
        if (mSlug) mSlug.value = doc.slug || "";
    }
};

window.closeEditor = () => {
    document.getElementById('editor-modal').style.display = 'none';
    const configTabs = document.getElementById('config-tabs');
    if (configTabs) configTabs.style.display = 'none';
};

window.saveDocument = async () => {
    const content = document.getElementById('editor-body').value;
    const status = document.getElementById('save-status');
    status.innerText = "💾 正在写入磁道...";

    const res = await apiFetch(`/ledger/document/${window.activeDocId}/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
    });

    if (res && res.success) {
        status.innerText = "✅ 写入成功";
        addAudit(`📄 资产 ${window.activeDocId.substring(0, 8)} 已完成物理变更。`);
        setTimeout(closeEditor, 800);
        if (typeof currentView !== 'undefined' && window.currentView === 'overview') {
            if (typeof refreshGalaxy === 'function') refreshGalaxy();
        }
    }
};
