/**
 * 🪐 [V100.0] Illacme Plenipes 3D Galaxy Engine - Node Director Control Shard
 * 职责：管理星球属性、AI 摘要、实体渲染与手动星链关联动作。
 * 符合 SOP-02 模块拆分协议，行数严格控制在 300 行内。
 */

window.injectGalaxyDirectorDOM = () => {
    const rightColumn = document.getElementById('galaxy-right-column');
    if (!rightColumn) return;

    // 2. 注入星球控制仪 (作为子节点挂在右侧控制列，自然排在检索框下方)
    if (!document.getElementById('galaxy-node-director')) {
        const dirDiv = document.createElement('div');
        dirDiv.id = 'galaxy-node-director';
        dirDiv.className = 'glass-panel';
        dirDiv.style.cssText = 'display: none; flex-direction: column; border-radius: 16px; padding: 20px; max-height: calc(100vh - 180px); overflow: hidden; width: 100%; box-sizing: border-box; margin-top: 0;';
        dirDiv.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid var(--glass-border); padding-bottom: 8px; flex-shrink: 0;"><span style="font-size: 0.7rem; font-weight: 900; color: var(--accent-secondary);">🪐 星球控制仪</span><button onclick="window.closeNodeDirector()" style="background: none; border: none; color: var(--text-dim); font-size: 1.2rem; cursor: pointer; line-height: 1; outline: none;">×</button></div>
            <div class="scroll-container" style="display: flex; flex-direction: column; gap: 12px; overflow-y: auto; flex: 1; min-height: 0; margin-bottom: 12px; padding-right: 4px;">
                <div><h3 id="node-dir-title" style="margin: 0 0 4px 0; font-size: 0.95rem; color: var(--text-bright); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">-</h3><span id="node-dir-path" class="mono" style="font-size: 0.6rem; color: var(--text-dim); word-break: break-all; display: block;">-</span></div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; background: var(--white-03); padding: 8px; border-radius: 8px; border: 1px solid var(--glass-border);">
                    <div style="text-align: center;"><div style="font-size: 0.5rem; color: var(--text-dim);">字符数</div><div id="node-dir-words" style="font-family: var(--font-mono); font-size: 0.75rem; font-weight: 800;">0</div></div>
                    <div style="text-align: center; border-left: 1px solid var(--glass-border); border-right: 1px solid var(--glass-border);"><div style="font-size: 0.5rem; color: var(--text-dim);">物理 (Wiki)</div><div id="node-dir-wikilinks" style="font-family: var(--font-mono); font-size: 0.75rem; font-weight: 800; color: var(--neon-cyan);">0</div></div>
                    <div style="text-align: center;"><div style="font-size: 0.5rem; color: var(--text-dim);">语义 (AI)</div><div id="node-dir-semantic" style="font-family: var(--font-mono); font-size: 0.75rem; font-weight: 800; color: var(--accent-primary);">0</div></div>
                </div>
                <div><span style="font-size: 0.55rem; color: var(--text-dim); text-transform: uppercase; font-weight: 800;">AI 摘要 (Gist)</span><p id="node-dir-gist" style="margin: 4px 0 0 0; font-size: 0.65rem; line-height: 1.4; color: var(--text-dim); background: var(--white-02); padding: 8px; border-radius: 6px; border: 1px solid var(--glass-border); max-height: 70px; overflow-y: auto;">-</p></div>
                <div><span style="font-size: 0.55rem; color: var(--text-dim); text-transform: uppercase; font-weight: 800;">提取实体</span><div id="node-dir-entities" style="display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; max-height: 80px; overflow-y: auto;"></div></div>
                <div style="border-top: 1px solid var(--glass-border); padding-top: 8px;"><span style="font-size: 0.55rem; color: var(--text-dim); text-transform: uppercase; font-weight: 800; display: block; margin-bottom: 4px;">关联物理/语义星链</span><div id="node-dir-connections-list" class="scroll-container" style="max-height: 100px; overflow-y: auto; display: flex; flex-direction: column; gap: 4px;"></div></div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 6px; border-top: 1px solid var(--glass-border); padding-top: 10px; flex-shrink: 0;">
                <button class="primary-btn glow-btn" id="node-dir-btn-edit" style="width: 100%; height: 26px; font-size: 0.7rem; padding: 0;">✍️ 编辑原稿</button>
                <button class="primary-btn glow-btn" id="node-dir-btn-publish" style="width: 100%; height: 26px; font-size: 0.7rem; background: var(--neon-cyan-05); border-color: var(--neon-cyan-15); padding: 0;">🚀 单篇发布</button>
                <button class="primary-btn glow-btn" id="node-dir-btn-rebuild" style="width: 100%; height: 26px; font-size: 0.7rem; background: var(--accent-primary-05); border-color: var(--accent-primary-10); padding: 0;">🧠 语义重构</button>
                <button class="primary-btn glow-btn" id="node-dir-btn-link" style="width: 100%; height: 26px; font-size: 0.7rem; background: var(--neon-cyan-05); border-color: var(--neon-cyan-15); padding: 0;">🔗 建立新关联</button>
            </div>
        `;
        rightColumn.appendChild(dirDiv);
    }
};

window.showNodeDirector = async (node) => {
    window._currentNode = node;
    const panel = document.getElementById('galaxy-node-director');
    if (!panel) return;

    panel.style.display = 'flex';
    document.getElementById('node-dir-title').innerText = node.title || node.id;
    document.getElementById('node-dir-path').innerText = node.id;

    try {
        const detail = await apiFetch(`/ledger/document/${encodeURIComponent(node.id)}`);
        if (detail && !detail.error) {
            document.getElementById('node-dir-words').innerText = detail.word_count || (detail.content ? detail.content.length : 0);
            const gist = detail.frontmatter?.gist || detail.gist || '暂无 AI 摘要';
            document.getElementById('node-dir-gist').innerText = gist;

            const entities = detail.frontmatter?.entities || detail.entities || {};
            const entContainer = document.getElementById('node-dir-entities');
            entContainer.innerHTML = '';
            let entCount = 0;
            for (const cat in entities) {
                if (Array.isArray(entities[cat])) {
                    entities[cat].forEach(e => {
                        const span = document.createElement('span');
                        span.className = 'entity-badge';
                        span.innerText = e;
                        entContainer.appendChild(span);
                        entCount++;
                    });
                }
            }
            if (entCount === 0) entContainer.innerHTML = '<span style="font-size:0.6rem; color:var(--text-dim);">无提取实体</span>';
        }
    } catch (e) {
        console.error("加载节点元数据失败:", e);
    }

    renderConnectionsList(node);

    document.getElementById('node-dir-btn-edit').onclick = () => {
        window.closeNodeDirector();
        if (typeof window.openEditor === 'function') window.openEditor(node.id);
    };

    document.getElementById('node-dir-btn-publish').onclick = async () => {
        try {
            const btn = document.getElementById('node-dir-btn-publish');
            btn.innerText = '🚀 发布中...';
            btn.disabled = true;
            const res = await apiFetch('/api/publish/trigger', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: 'static', paths: [node.id] })
            });
            if (res && res.status === 'task_queued') {
                if (window.Swal) window.Swal.fire({ icon: 'success', title: '单篇分发已启动', text: `发布任务 ID: ${res.task_id}`, background: 'rgba(20,20,20,0.95)', color: '#fff' });
            } else {
                alert('发布启动失败: ' + (res.message || '未知错误'));
            }
        } catch (err) {
            alert('发布故障: ' + err.message);
        } finally {
            const btn = document.getElementById('node-dir-btn-publish');
            btn.innerText = '🚀 单篇发布';
            btn.disabled = false;
        }
    };

    document.getElementById('node-dir-btn-rebuild').onclick = async () => {
        try {
            const btn = document.getElementById('node-dir-btn-rebuild');
            btn.innerText = '🧠 分析中...';
            btn.disabled = true;
            const res = await apiFetch('/api/galaxy/rebuild-node', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ doc_id: node.id })
            });
            if (res && res.success) {
                if (window.Swal) window.Swal.fire({ icon: 'success', title: 'AI 语义分析完成', text: res.message, background: 'rgba(20,20,20,0.95)', color: '#fff' });
                if (typeof window.refreshGalaxy === 'function') await window.refreshGalaxy();
                setTimeout(() => window.showNodeDirector(node), 500);
            } else {
                alert('语义重构失败: ' + (res.error || '未知错误'));
            }
        } catch (err) {
            alert('语义重构故障: ' + err.message);
        } finally {
            const btn = document.getElementById('node-dir-btn-rebuild');
            btn.innerText = '🧠 语义重构';
            btn.disabled = false;
        }
    };

    document.getElementById('node-dir-btn-link').onclick = () => {
        window._galaxyConnectionSourceNode = node;
        window.closeNodeDirector();
        if (window.Swal) {
            window.Swal.fire({
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 4000,
                icon: 'info',
                title: '请在星图中点击另一个节点建立手动关联',
                background: 'rgba(20,20,20,0.95)',
                color: '#fff'
            });
        }
    };
};

window.closeNodeDirector = () => {
    const panel = document.getElementById('galaxy-node-director');
    if (panel) panel.style.display = 'none';
    window._currentNode = null;
};

function renderConnectionsList(node) {
    const container = document.getElementById('node-dir-connections-list');
    if (!container || !window.galaxyGraph) return;

    const data = window.galaxyGraph.graphData();
    const links = data.links.filter(l => {
        const src = l.source?.id || l.source;
        const tgt = l.target?.id || l.target;
        return src === node.id || tgt === node.id;
    });

    let wikiCount = 0, semanticCount = 0;
    links.forEach(l => {
        if (l.type === 'wikilink') wikiCount++;
        else semanticCount++;
    });
    document.getElementById('node-dir-wikilinks').innerText = wikiCount;
    document.getElementById('node-dir-semantic').innerText = semanticCount;

    if (links.length === 0) {
        container.innerHTML = '<span style="font-size:0.6rem; color:var(--text-dim); text-align:center;">暂无任何星链连接</span>';
        return;
    }

    container.innerHTML = links.map(l => {
        const src = l.source?.id || l.source;
        const tgt = l.target?.id || l.target;
        const otherId = src === node.id ? tgt : src;
        const otherNode = data.nodes.find(n => n.id === otherId);
        const name = otherNode?.title || otherId.split('/').pop();
        const typeClass = l.type === 'wikilink' ? 'wikilink' : 'semantic';
        const typeText = l.type === 'wikilink' ? 'Wiki' : 'AI';
        return `
            <div class="node-dir-conn-item">
                <span class="node-dir-conn-type ${typeClass}">${typeText}</span>
                <span class="node-dir-conn-name" title="${otherId}" onclick="window.focusConnectionNode('${otherId}')">${name}</span>
                <button class="node-dir-conn-delete" onclick="window.triggerUnlink('${node.id}', '${otherId}')" title="断开关联">🗑️</button>
            </div>
        `;
    }).join('');
}

window.focusConnectionNode = (nodeId) => {
    if (!window.galaxyGraph) return;
    const nodes = window.galaxyGraph.graphData().nodes;
    const node = nodes.find(n => n.id === nodeId);
    if (node && typeof focusNodeIn3D === 'function') {
        focusNodeIn3D(node);
        window.showNodeDirector(node);
    }
};

window.confirmManualConnection = (targetNode) => {
    const srcNode = window._galaxyConnectionSourceNode;
    window._galaxyConnectionSourceNode = null;
    if (!srcNode || srcNode.id === targetNode.id) return;

    if (window.Swal) {
        window.Swal.fire({
            title: '确认建立连接？',
            html: `确定要在 <b>${srcNode.title || srcNode.id}</b> 与 <b>${targetNode.title || targetNode.id}</b> 之间建立手动语义关联吗？`,
            icon: 'question',
            showCancelButton: true,
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            background: 'rgba(20,20,20,0.95)',
            color: '#fff'
        }).then(async (result) => {
            if (result.isConfirmed) {
                try {
                    const res = await apiFetch('/api/galaxy/link', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ src: srcNode.id, target: targetNode.id })
                    });
                    if (res && res.status === 'success') {
                        if (typeof window.refreshGalaxy === 'function') await window.refreshGalaxy();
                        window.showNodeDirector(targetNode);
                    }
                } catch (e) {
                    alert('连接失败: ' + e.message);
                }
            }
        });
    }
};

window.triggerUnlink = (srcId, targetId) => {
    if (window.Swal) {
        window.Swal.fire({
            title: '确认断开关联？',
            text: '该操作将从高维图谱中移除这两个节点间的语义或手动关联线。',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: '确定断开',
            cancelButtonText: '取消',
            background: 'rgba(20,20,20,0.95)',
            color: '#fff',
            confirmButtonColor: '#d33'
        }).then(async (result) => {
            if (result.isConfirmed) {
                try {
                    const res = await apiFetch('/api/galaxy/unlink', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ src: srcId, target: targetId })
                    });
                    if (res && res.status === 'success') {
                        if (typeof window.refreshGalaxy === 'function') await window.refreshGalaxy();
                        const data = window.galaxyGraph?.graphData();
                        const currentNode = data?.nodes.find(n => n.id === srcId);
                        if (currentNode) {
                            window.showNodeDirector(currentNode);
                        } else {
                            window.closeNodeDirector();
                        }
                    }
                } catch (e) {
                    alert('断开失败: ' + e.message);
                }
            }
        });
    }
};
