/**
 * 🪐 [V100.0] Illacme Plenipes 3D Galaxy Engine - Node Director Control Shard
 * 职责：管理星球属性、AI 摘要、实体渲染与手动星链关联动作。
 * 符合 SOP-02 模块拆分协议，行数严格控制在 300 行内。
 */

window._activeGalaxyNode = null;

// 🪐 [V107.8] 全局星谱状态自愈与镜头自动对焦恢复钩子
window.restoreGalaxyDirectorIfActive = () => {
    if (window.currentView === 'overview' && window._activeGalaxyNode) {
        const node = window._activeGalaxyNode;
        if (typeof window.showNodeDirector === 'function') window.showNodeDirector(node);
        if (typeof window.focusNodeIn3D === 'function') window.focusNodeIn3D(node);
    }
};

window.injectGalaxyDirectorDOM = () => {
    const rightCol = document.getElementById('galaxy-right-column');
    if (!rightCol || document.getElementById('galaxy-node-director')) return;

    const dir = document.createElement('div');
    dir.id = 'galaxy-node-director';
    dir.className = 'glass-panel';
    dir.style.cssText = 'display: none; flex-direction: column; border-radius: 16px; padding: 18px; height: auto; max-height: calc(100% - 46px); min-height: 0; flex: 0 1 auto; overflow: hidden; width: 100%; box-sizing: border-box; margin-top: 0; box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45); pointer-events: auto;';
    dir.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid var(--glass-border); padding-bottom: 6px; flex-shrink: 0;"><span style="font-size: 0.7rem; font-weight: 900; color: var(--accent-secondary);">🪐 星球控制仪</span><button onclick="window.closeNodeDirector()" style="background: none; border: none; color: var(--text-dim); font-size: 1.2rem; cursor: pointer; line-height: 1; outline: none;">×</button></div>
        <div class="scroll-container" style="display: flex; flex-direction: column; gap: 10px; overflow-y: auto; flex: 1 1 auto; min-height: 0; margin-bottom: 10px; padding-right: 4px;">
            <div><h3 id="node-dir-title" style="margin: 0 0 4px 0; font-size: 0.95rem; color: var(--text-bright); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">-</h3><span id="node-dir-path" class="mono" style="font-size: 0.6rem; color: var(--text-dim); word-break: break-all; display: block;">-</span></div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; background: var(--white-03); padding: 8px; border-radius: 8px; border: 1px solid var(--glass-border); flex-shrink: 0;">
                <div style="text-align: center;" title="正文字数统计 (全球多语种自适应)"><div style="font-size: 0.5rem; color: var(--text-dim);">字数</div><div id="node-dir-words" style="font-family: var(--font-mono); font-size: 0.75rem; font-weight: 800;">0</div></div>
                <div style="text-align: center; border-left: 1px solid var(--glass-border); border-right: 1px solid var(--glass-border);" title="原稿 [[WikiLinks]] 双向引用数"><div style="font-size: 0.5rem; color: var(--text-dim);">文档双链</div><div id="node-dir-wikilinks" style="font-family: var(--font-mono); font-size: 0.75rem; font-weight: 800; color: var(--neon-cyan);">0</div></div>
                <div style="text-align: center;" title="AI 语义算法推荐概念关联数"><div style="font-size: 0.5rem; color: var(--text-dim);">智能关联</div><div id="node-dir-semantic" style="font-family: var(--font-mono); font-size: 0.75rem; font-weight: 800; color: var(--accent-primary);">0</div></div>
            </div>
            <div>
                <div onclick="window.toggleDirectorSection('gist')" style="display: flex; justify-content: space-between; align-items: center; cursor: pointer; user-select: none; padding: 2px 0;" title="点击折叠/展开 AI 摘要">
                    <span style="font-size: 0.55rem; color: var(--text-dim); text-transform: uppercase; font-weight: 800;">AI 核心摘要</span>
                    <span id="node-dir-gist-arrow" style="font-size: 0.65rem; color: var(--text-dim);">▾</span>
                </div>
                <p id="node-dir-gist" style="margin: 4px 0 0 0; font-size: 0.65rem; line-height: 1.4; color: var(--text-dim); background: var(--white-02); padding: 8px; border-radius: 6px; border: 1px solid var(--glass-border); max-height: 70px; overflow-y: auto;">-</p>
            </div>
            <div>
                <div onclick="window.toggleDirectorSection('entities')" style="display: flex; justify-content: space-between; align-items: center; cursor: pointer; user-select: none; padding: 2px 0;" title="点击折叠/展开提炼关键词">
                    <span style="font-size: 0.55rem; color: var(--text-dim); text-transform: uppercase; font-weight: 800;">提炼关键词 / 实体</span>
                    <span id="node-dir-entities-arrow" style="font-size: 0.65rem; color: var(--text-dim);">▾</span>
                </div>
                <div id="node-dir-entities" style="display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px; max-height: 80px; overflow-y: auto;"></div>
            </div>
            <div style="border-top: 1px solid var(--glass-border); padding-top: 6px; display: flex; flex-direction: column;">
                <span style="font-size: 0.55rem; color: var(--text-dim); text-transform: uppercase; font-weight: 800; display: block; margin-bottom: 4px; flex-shrink: 0;">关联知识笔记</span>
                <div id="node-dir-connections-list" class="scroll-container" style="max-height: 150px; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; transition: max-height 0.25s cubic-bezier(0.4, 0, 0.2, 1);"></div>
            </div>
        </div>
        <div style="border-top: 1px solid var(--glass-border); padding-top: 8px; flex-shrink: 0; display: flex; flex-direction: column; gap: 6px; position: relative; z-index: 100;">
            <div id="node-dir-status-bar" style="display: none; font-size: 0.62rem; color: var(--neon-cyan); text-align: center; padding: 4px 6px; background: var(--white-03); border: 1px solid var(--glass-border); border-radius: 6px; font-weight: 600;"></div>
            <!-- 🚀 4 联核心快捷操作（编辑、预览、推流、发布） -->
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px;">
                <button class="primary-btn glow-btn" id="node-dir-btn-edit" style="height: 28px; font-size: 0.65rem; padding: 0; background: var(--white-05); border-color: var(--glass-border);" title="在 Markdown 创作工作台中编辑此篇笔记">✍️ 编辑</button>
                <button class="primary-btn glow-btn" id="node-dir-btn-preview" style="height: 28px; font-size: 0.65rem; padding: 0; background: var(--white-05); border-color: var(--glass-border);" title="在新标签页中实时渲染预览独立站效果（自动探活并拉起服务）">👁️ 预览</button>
                <button class="primary-btn glow-btn" id="node-dir-btn-syndicate" style="height: 28px; font-size: 0.65rem; padding: 0; background: var(--white-05); border-color: var(--glass-border);" title="呼出全域渠道推流抽屉 (微信 · 知乎 · B站 · Dev.to 等)">📢 推流</button>
                <button class="primary-btn glow-btn" id="node-dir-btn-publish" style="height: 28px; font-size: 0.65rem; background: var(--neon-cyan-05); border-color: var(--neon-cyan-30); color: var(--neon-cyan); font-weight: 700; padding: 0;" title="呼出独立站全站托管与多语种网页发布抽屉">🌐 发布</button>
            </div>
            <!-- 🚀 星系 AI、3D 手动连线与更多文库操作下拉 -->
            <div style="display: grid; grid-template-columns: 1fr 1fr 34px; gap: 5px; position: relative;">
                <button class="primary-btn glow-btn" id="node-dir-btn-rebuild" style="height: 26px; font-size: 0.62rem; background: var(--accent-primary-05); border-color: var(--accent-primary-20); color: var(--text-dim); padding: 0;" title="调用 AI 提炼本篇核心摘要、关键词并重算星系引力">🧠 提炼摘要</button>
                <button class="primary-btn glow-btn" id="node-dir-btn-link" style="height: 26px; font-size: 0.62rem; background: var(--white-03); border-color: var(--glass-border); color: var(--text-dim); padding: 0;" title="在 3D 星图中点击另一个星球建立引力连线">🔗 连线笔记</button>
                <button class="primary-btn glow-btn" id="node-dir-btn-more" style="height: 26px; width: 34px; font-size: 0.75rem; padding: 0; background: var(--white-03); border-color: var(--glass-border); color: var(--text-dim);" title="更多原稿操作 (译文校对 · 文章封面 · 重命名 · 物理销毁)">···</button>
                <!-- 更多操作下拉菜单 (采用 vault-more-menu 竖向抽屉样式，向上展开且层级顶置) -->
                <div id="node-dir-more-menu" class="vault-more-menu dropup custom-glass-dropdown" style="display: none; flex-direction: column; position: absolute; right: 0; bottom: calc(100% + 8px); z-index: 10200; min-width: 180px; background: rgba(13, 17, 28, 0.98); border: 1px solid var(--neon-cyan-30); border-radius: 8px; padding: 5px 0; box-shadow: 0 -12px 36px rgba(0,0,0,0.85), 0 0 15px rgba(0,242,255,0.15);">
                    <button class="vault-more-item" id="node-dir-more-review">🌍 多语种译文校对</button>
                    <button class="vault-more-item" id="node-dir-more-cover">🖼️ 更换或生成封面</button>
                    <button class="vault-more-item" id="node-dir-more-move">📤 重命名与分类迁移</button>
                    <div class="vault-more-divider"></div>
                    <button class="vault-more-item danger" id="node-dir-more-delete">🗑️ 物理安全彻底销毁</button>
                </div>
            </div>
        </div>`;
    rightCol.appendChild(dir);
};

window._directorFoldState = window._directorFoldState || { gist: false, entities: false };
window.toggleDirectorSection = (sec) => { window._directorFoldState[sec] = !window._directorFoldState[sec]; _applyDirectorFold(); };
const _applyDirectorFold = () => {
    const s = window._directorFoldState;
    const gEl = document.getElementById('node-dir-gist'), gArr = document.getElementById('node-dir-gist-arrow');
    const eEl = document.getElementById('node-dir-entities'), eArr = document.getElementById('node-dir-entities-arrow');
    const list = document.getElementById('node-dir-connections-list');
    if (gEl && gArr) { gEl.style.display = s.gist ? 'none' : 'block'; gArr.innerText = s.gist ? '▸' : '▾'; }
    if (eEl && eArr) { eEl.style.display = s.entities ? 'none' : 'flex'; eArr.innerText = s.entities ? '▸' : '▾'; }
    if (list) list.style.maxHeight = (s.gist && s.entities) ? '360px' : (s.gist || s.entities ? '250px' : '150px');
};

const _renderEntityBadges = (container, entities) => {
    if (!container) return;
    container.innerHTML = '';
    let count = 0;
    const add = (txt) => {
        if (!txt || typeof txt !== 'string') return;
        const s = document.createElement('span');
        s.className = 'entity-badge'; s.innerText = txt.trim();
        container.appendChild(s); count++;
    };
    if (Array.isArray(entities)) entities.forEach(add);
    else if (typeof entities === 'object' && entities !== null) {
        Object.values(entities).forEach(v => Array.isArray(v) ? v.forEach(add) : (typeof v === 'string' && add(v)));
    }
    if (count === 0) container.innerHTML = '<span style="font-size:0.6rem; color:var(--text-dim);">无提取实体</span>';
};

window.showNodeDirector = async (node) => {
    window.dismissCustomTooltip?.();
    window._currentNode = node;
    window._activeGalaxyNode = node;
    const panel = document.getElementById('galaxy-node-director');
    if (!panel) return;
    panel.style.display = 'flex';
    document.getElementById('node-dir-title').innerText = node.title || node.id;
    document.getElementById('node-dir-path').innerText = node.id;

    let docDetail = null;
    try {
        docDetail = await apiFetch(`/ledger/document/${encodeURIComponent(node.id)}`);
        if (docDetail && !docDetail.error) {
            let words = (typeof docDetail.word_count === 'number') ? docDetail.word_count : (docDetail.seo_data?.word_count || 0);
            if (!words && docDetail.content && typeof calculateUniversalWordCount === 'function') words = calculateUniversalWordCount(docDetail.content);
            document.getElementById('node-dir-words').innerText = (words || 0).toLocaleString();
            document.getElementById('node-dir-gist').innerText = docDetail.frontmatter?.gist || docDetail.gist || node.gist || '暂无 AI 摘要';
            _renderEntityBadges(document.getElementById('node-dir-entities'), docDetail.frontmatter?.entities || docDetail.entities || node.entities);
        }
    } catch (e) { console.error("加载节点元数据失败:", e); }

    if (typeof window.renderConnectionsList === 'function') window.renderConnectionsList(node);
    _applyDirectorFold();

    const titleStr = node.title || node.id;
    const docSlug = node.slug || docDetail?.slug || '';
    const docCover = docDetail?.cover || '';

    // 1. 快捷核心操作绑定
    const hideAndRun = (fn) => { panel.style.display = 'none'; if (typeof fn === 'function') fn(); };
    document.getElementById('node-dir-btn-edit').onclick = () => hideAndRun(() => window.openEditor?.(node.id));
    document.getElementById('node-dir-btn-preview').onclick = () => window.openArticleLivePreview?.(node.id, docSlug);
    document.getElementById('node-dir-btn-syndicate').onclick = () => hideAndRun(() => window.openArticleSyndicationDrawer?.(node.id, titleStr));
    document.getElementById('node-dir-btn-publish').onclick = () => hideAndRun(() => window.openVaultDrawer?.(node.id));

    // 2. 更多操作下拉与子项绑定
    const moreMenu = document.getElementById('node-dir-more-menu');
    document.getElementById('node-dir-btn-more').onclick = (e) => {
        e.stopPropagation();
        if (moreMenu) moreMenu.style.display = (moreMenu.style.display === 'none' || !moreMenu.style.display) ? 'flex' : 'none';
    };
    const closeMoreAndRun = (fn) => { if (moreMenu) moreMenu.style.display = 'none'; hideAndRun(fn); };
    document.getElementById('node-dir-more-review').onclick = () => closeMoreAndRun(() => window.openTranslationReview?.(node.id));
    document.getElementById('node-dir-more-cover').onclick = () => closeMoreAndRun(() => window.openDocCoverPickerModal?.(node.id, titleStr, docCover));
    document.getElementById('node-dir-more-move').onclick = () => { if (moreMenu) moreMenu.style.display = 'none'; window.triggerMoveDocument?.(node.id); };
    document.getElementById('node-dir-more-delete').onclick = () => { if (moreMenu) moreMenu.style.display = 'none'; window.triggerDirectDocDelete?.(node.id, titleStr); };

    // 7. 🧠 提炼摘要与关键词
    document.getElementById('node-dir-btn-rebuild').onclick = async () => {
        const btn = document.getElementById('node-dir-btn-rebuild'), sBar = document.getElementById('node-dir-status-bar');
        try {
            btn.innerText = '🧠 提炼中...'; btn.disabled = true;
            if (sBar) { sBar.style.display = 'block'; sBar.innerText = '🧠 正在调用模型提炼摘要、关键词并编织星系引力...'; }
            const res = await apiFetch('/api/galaxy/rebuild-node', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ doc_id: node.id }) });
            if (res && res.success) {
                if (res.gist) { node.gist = res.gist; document.getElementById('node-dir-gist').innerText = res.gist; }
                if (res.entities) { node.entities = res.entities; _renderEntityBadges(document.getElementById('node-dir-entities'), res.entities); }
                const fullGraph = await apiFetch('/api/galaxy/graph?mode=full');
                if (fullGraph && fullGraph.nodes && window.galaxyGraph) {
                    const curData = window.galaxyGraph.graphData(), nodeMap = {};
                    curData.nodes.forEach(n => { nodeMap[n.id] = n; });
                    fullGraph.nodes.forEach(fn => { if (nodeMap[fn.id]) Object.assign(nodeMap[fn.id], fn); });
                    const validLinks = (fullGraph.links || []).filter(l => nodeMap[l.source?.id || l.source] && nodeMap[l.target?.id || l.target]);
                    window.galaxyGraph.graphData({ nodes: Object.values(nodeMap), links: validLinks });
                }
                window.renderConnectionsList(node);
                if (sBar) { sBar.innerText = '✅ 核心摘要、实体与星系关联已提炼更新！'; setTimeout(() => { if (sBar) sBar.style.display = 'none'; }, 4000); }
                window.Swal?.fire({ toast: true, position: 'top-end', icon: 'success', title: '提炼摘要与关联完成', text: res.message, showConfirmButton: false, timer: 3500, background: 'rgba(20,20,20,0.95)', color: '#fff' });
            } else { if (sBar) sBar.style.display = 'none'; alert('提炼失败: ' + (res.error || res.message || '未知错误')); }
        } catch (err) { if (sBar) sBar.style.display = 'none'; alert('提炼故障: ' + err.message); }
        finally { btn.innerText = '🧠 提炼摘要'; btn.disabled = false; }
    };

    // 8. 🔗 连线其他笔记
    document.getElementById('node-dir-btn-link').onclick = () => {
        window._galaxyConnectionSourceNode = node;
        window.Swal?.fire({ toast: true, position: 'top-end', showConfirmButton: false, timer: 4000, icon: 'info', title: '请在星图中点击另一个星球建立关联连线', background: 'rgba(20,20,20,0.95)', color: '#fff' });
    };
};

// 📂 点击空白处自闭更多操作下拉
if (!window._nodeDirMoreListenerBound) {
    window._nodeDirMoreListenerBound = true;
    document.addEventListener('click', () => {
        const m = document.getElementById('node-dir-more-menu');
        if (m) m.style.display = 'none';
    });
}

window.closeNodeDirector = (resetCamera = false) => {
    window.dismissCustomTooltip?.();
    const panel = document.getElementById('galaxy-node-director');
    if (panel) panel.style.display = 'none';
    const moreMenu = document.getElementById('node-dir-more-menu');
    if (moreMenu) moreMenu.style.display = 'none';
    window._currentNode = null;
    window._activeGalaxyNode = null;
    if (resetCamera && window.galaxyGraph) {
        window.galaxyGraph.cameraPosition({ x: 0, y: 0, z: 280 }, { x: 0, y: 0, z: 0 }, 1200);
    }
};

window.renderConnectionsList = (targetNode) => {
    const node = targetNode || window._currentNode;
    const container = document.getElementById('node-dir-connections-list');
    if (!container || !window.galaxyGraph || !node) return;
    const data = window.galaxyGraph.graphData();
    const links = (data.links || []).filter(l => (l.source?.id || l.source) === node.id || (l.target?.id || l.target) === node.id);
    let wikiCount = 0, semanticCount = 0;
    links.forEach(l => { if (l.type === 'wikilink') wikiCount++; else semanticCount++; });
    const wEl = document.getElementById('node-dir-wikilinks'), sEl = document.getElementById('node-dir-semantic');
    if (wEl) wEl.innerText = wikiCount;
    if (sEl) sEl.innerText = semanticCount;
    if (links.length === 0) { container.innerHTML = '<span style="font-size:0.6rem; color:var(--text-dim); text-align:center; padding: 6px 0;">暂无关联笔记</span>'; return; }
    container.innerHTML = links.map(l => {
        const src = l.source?.id || l.source, tgt = l.target?.id || l.target;
        const otherId = src === node.id ? tgt : src;
        const otherNode = (data.nodes || []).find(n => n.id === otherId);
        const name = otherNode?.title || otherId.split('/').pop();
        const typeClass = l.type === 'wikilink' ? 'wikilink' : 'semantic';
        const typeText = l.type === 'wikilink' ? '双链' : (l.is_manual ? '手动' : '智能');
        const typeDesc = l.type === 'wikilink' ? '文档内手动双向链接' : (l.is_manual ? '手动建立的主权关联' : 'AI 语义算法推荐关联');
        return `<div class="node-dir-conn-item"><span class="node-dir-conn-type ${typeClass}" title="${typeDesc}">${typeText}</span><span class="node-dir-conn-name" onclick="window.focusConnectionNode('${otherId}')">${name}</span><button class="node-dir-conn-delete" onclick="window.triggerUnlink('${node.id}', '${otherId}')" title="断开此关联连线">🗑️</button></div>`;
    }).join('');
};

window.focusConnectionNode = (nodeId) => {
    window.dismissCustomTooltip?.(600);
    if (!window.galaxyGraph) return;
    const node = window.galaxyGraph.graphData().nodes.find(n => n.id === nodeId);
    if (node && typeof focusNodeIn3D === 'function') { focusNodeIn3D(node); window.showNodeDirector(node); }
};

window.confirmManualConnection = (targetNode) => {
    const srcNode = window._galaxyConnectionSourceNode;
    window._galaxyConnectionSourceNode = null;
    if (!srcNode || srcNode.id === targetNode.id) return;
    window.Swal?.fire({
        title: '确认建立笔记关联？', html: `确定要在 <b>${srcNode.title || srcNode.id}</b> 与 <b>${targetNode.title || targetNode.id}</b> 之间建立关联连线吗？`,
        icon: 'question', showCancelButton: true, confirmButtonText: '确定建立', cancelButtonText: '取消', background: 'rgba(20,20,20,0.95)', color: '#fff'
    }).then(async (result) => {
        if (!result.isConfirmed) return;
        try {
            const res = await apiFetch('/api/galaxy/link', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ src: srcNode.id, target: targetNode.id }) });
            if (res?.status === 'success') {
                if (typeof window.refreshGalaxy === 'function') await window.refreshGalaxy();
                window.showNodeDirector(srcNode);
            }
        } catch (e) { alert('连线失败: ' + e.message); }
    });
};

window.triggerUnlink = (srcId, targetId) => {
    window.Swal?.fire({
        title: '确认断开连线？', text: '该操作将断开这两篇笔记在星谱中的关联连线。',
        icon: 'warning', showCancelButton: true, confirmButtonText: '确定断开', cancelButtonText: '取消', background: 'rgba(20,20,20,0.95)', color: '#fff', confirmButtonColor: '#d33'
    }).then(async (result) => {
        if (!result.isConfirmed) return;
        try {
            const res = await apiFetch('/api/galaxy/unlink', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ src: srcId, target: targetId }) });
            if (res?.status === 'success') {
                if (typeof window.refreshGalaxy === 'function') await window.refreshGalaxy();
                const currentNode = window.galaxyGraph?.graphData()?.nodes.find(n => n.id === srcId);
                if (currentNode) window.showNodeDirector(currentNode); else window.closeNodeDirector();
            }
        } catch (e) { alert('断开失败: ' + e.message); }
    });
};

function calculateUniversalWordCount(text) {
    if (!text) return 0;
    const b = text.replace(/^---[\s\S]*?---\s*/, '').replace(/```[\s\S]*?```|`[^`\n]*`|<[^>]+>/g, ' ');
    const cjk = (b.match(/[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u30ff\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]/g) || []).length;
    const words = (b.replace(/[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u30ff\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]/g, ' ').match(/[\p{L}\p{N}]+(?:[-'][\p{L}\p{N}]+)*/gu) || []).length;
    return cjk + words;
}
