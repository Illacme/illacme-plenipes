/**
 * 🪐 [V100.0] Illacme Plenipes 3D Galaxy Engine - Node Director Control Shard
 * 职责：管理星球属性、AI 摘要、实体渲染与手动星链关联动作。
 * 符合 SOP-02 模块拆分协议，行数严格控制在 300 行内。
 */

window.injectGalaxyDirectorDOM = () => {
    const rightCol = document.getElementById('galaxy-right-column');
    if (!rightCol || document.getElementById('galaxy-node-director')) return;

    const dir = document.createElement('div');
    dir.id = 'galaxy-node-director';
    dir.className = 'glass-panel';
    dir.style.cssText = 'display: none; flex-direction: column; border-radius: 16px; padding: 18px; max-height: calc(100vh - 180px); overflow: hidden; width: 100%; box-sizing: border-box; margin-top: 0;';
    dir.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid var(--glass-border); padding-bottom: 6px; flex-shrink: 0;"><span style="font-size: 0.7rem; font-weight: 900; color: var(--accent-secondary);">🪐 星球控制仪</span><button onclick="window.closeNodeDirector()" style="background: none; border: none; color: var(--text-dim); font-size: 1.2rem; cursor: pointer; line-height: 1; outline: none;">×</button></div>
        <div class="scroll-container" style="display: flex; flex-direction: column; gap: 10px; overflow-y: auto; flex: 1; min-height: 0; margin-bottom: 10px; padding-right: 4px;">
            <div><h3 id="node-dir-title" style="margin: 0 0 4px 0; font-size: 0.95rem; color: var(--text-bright); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">-</h3><span id="node-dir-path" class="mono" style="font-size: 0.6rem; color: var(--text-dim); word-break: break-all; display: block;">-</span></div>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; background: var(--white-03); padding: 8px; border-radius: 8px; border: 1px solid var(--glass-border);">
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
            <div style="border-top: 1px solid var(--glass-border); padding-top: 6px;">
                <span style="font-size: 0.55rem; color: var(--text-dim); text-transform: uppercase; font-weight: 800; display: block; margin-bottom: 4px;">关联知识笔记</span>
                <div id="node-dir-connections-list" class="scroll-container" style="max-height: 100px; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; transition: max-height 0.2s ease;"></div>
            </div>
        </div>
        <div style="border-top: 1px solid var(--glass-border); padding-top: 8px; flex-shrink: 0; display: flex; flex-direction: column; gap: 6px;">
            <div id="node-dir-status-bar" style="display: none; font-size: 0.62rem; color: var(--neon-cyan); text-align: center; padding: 4px 6px; background: var(--white-03); border: 1px solid var(--glass-border); border-radius: 6px; font-weight: 600;"></div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                <button class="primary-btn glow-btn" id="node-dir-btn-edit" style="height: 30px; font-size: 0.68rem; padding: 0; background: var(--white-05); border-color: var(--glass-border);" title="在编辑器中打开并编辑此篇 Markdown 笔记原稿">✍️ 编辑原稿</button>
                <button class="primary-btn glow-btn" id="node-dir-btn-publish" style="height: 30px; font-size: 0.68rem; background: var(--neon-cyan-05); border-color: var(--neon-cyan-30); color: var(--neon-cyan); font-weight: 700; padding: 0;" title="单独编译并发布此篇笔记到全站与各分发渠道">🚀 单篇发布</button>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                <button class="primary-btn glow-btn" id="node-dir-btn-rebuild" style="height: 26px; font-size: 0.62rem; background: var(--accent-primary-05); border-color: var(--accent-primary-20); color: var(--text-dim); padding: 0;" title="调用 AI 提炼本篇核心摘要、关键词，并重新计算星系引力关联">🧠 提炼摘要与关联</button>
                <button class="primary-btn glow-btn" id="node-dir-btn-link" style="height: 26px; font-size: 0.62rem; background: var(--white-03); border-color: var(--glass-border); color: var(--text-dim); padding: 0;" title="在 3D 星图中点击另一个节点，在两篇笔记间建立关联连线">🔗 连线其他笔记</button>
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
    if (list) list.style.maxHeight = (s.gist && s.entities) ? '320px' : (s.gist || s.entities ? '210px' : '100px');
};
window._nodePublishPollTimer = null;
const _stopNodePublishPoll = () => { if (window._nodePublishPollTimer) { clearInterval(window._nodePublishPollTimer); window._nodePublishPollTimer = null; } };

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
    const panel = document.getElementById('galaxy-node-director');
    if (!panel) return;
    panel.style.display = 'flex';
    document.getElementById('node-dir-title').innerText = node.title || node.id;
    document.getElementById('node-dir-path').innerText = node.id;

    try {
        const detail = await apiFetch(`/ledger/document/${encodeURIComponent(node.id)}`);
        if (detail && !detail.error) {
            let words = (typeof detail.word_count === 'number') ? detail.word_count : (detail.seo_data?.word_count || 0);
            if (!words && detail.content) words = calculateUniversalWordCount(detail.content);
            document.getElementById('node-dir-words').innerText = (words || 0).toLocaleString();
            document.getElementById('node-dir-gist').innerText = detail.frontmatter?.gist || detail.gist || node.gist || '暂无 AI 摘要';
            _renderEntityBadges(document.getElementById('node-dir-entities'), detail.frontmatter?.entities || detail.entities || node.entities);
        }
    } catch (e) { console.error("加载节点元数据失败:", e); }

    renderConnectionsList(node);
    _applyDirectorFold();

    document.getElementById('node-dir-btn-edit').onclick = () => {
        window.closeNodeDirector();
        if (typeof window.openEditor === 'function') window.openEditor(node.id);
    };

    document.getElementById('node-dir-btn-publish').onclick = async () => {
        const btn = document.getElementById('node-dir-btn-publish'), sBar = document.getElementById('node-dir-status-bar');
        try {
            btn.innerText = '🚀 发布中...'; btn.disabled = true;
            if (sBar) { sBar.style.display = 'block'; sBar.innerText = '⚡ 正在提交单篇分发任务...'; }
            const res = await apiFetch('/api/publish/trigger', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: 'static', paths: [node.id] })
            });
            if (res && res.status === 'task_queued') {
                if (sBar) sBar.innerText = `⏳ 任务 #${res.task_id} 已点火，后台编译同步中...`;
                _stopNodePublishPoll();
                let polls = 0;
                window._nodePublishPollTimer = setInterval(async () => {
                    polls++;
                    try {
                        const s = await apiFetch('/api/system/sync/status');
                        if (s && !s.is_publishing) {
                            _stopNodePublishPoll();
                            btn.innerText = '🚀 单篇发布'; btn.disabled = false;
                            if (sBar) { sBar.innerText = '✅ 单篇分发已闭环完成！'; setTimeout(() => { if (sBar) sBar.style.display = 'none'; }, 4000); }
                            window.Swal?.fire({ toast: true, position: 'top-end', icon: 'success', title: `《${node.title || node.id}》单篇发布完成`, showConfirmButton: false, timer: 3000, background: 'rgba(20,20,20,0.95)', color: '#fff' });
                        } else if (polls > 60) {
                            _stopNodePublishPoll();
                            btn.innerText = '🚀 单篇发布'; btn.disabled = false;
                            if (sBar) sBar.style.display = 'none';
                        }
                    } catch (_) { _stopNodePublishPoll(); btn.innerText = '🚀 单篇发布'; btn.disabled = false; if (sBar) sBar.style.display = 'none'; }
                }, 1000);
            } else {
                if (sBar) sBar.style.display = 'none'; btn.innerText = '🚀 单篇发布'; btn.disabled = false;
                alert('发布启动失败: ' + (res.message || '未知错误'));
            }
        } catch (err) {
            if (sBar) sBar.style.display = 'none'; btn.innerText = '🚀 单篇发布'; btn.disabled = false;
            alert('发布故障: ' + err.message);
        }
    };

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
        finally { btn.innerText = '🧠 提炼摘要与关联'; btn.disabled = false; }
    };

    document.getElementById('node-dir-btn-link').onclick = () => {
        window._galaxyConnectionSourceNode = node;
        window.Swal?.fire({ toast: true, position: 'top-end', showConfirmButton: false, timer: 4000, icon: 'info', title: '请在星图中点击另一个星球建立关联连线', background: 'rgba(20,20,20,0.95)', color: '#fff' });
    };
};

window.closeNodeDirector = () => {
    window.dismissCustomTooltip?.();
    _stopNodePublishPoll();
    const panel = document.getElementById('galaxy-node-director');
    if (panel) panel.style.display = 'none';
    window._currentNode = null;
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
        if (result.isConfirmed) {
            try {
                const res = await apiFetch('/api/galaxy/link', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ src: srcNode.id, target: targetNode.id }) });
                if (res && res.status === 'success') {
                    if (typeof window.refreshGalaxy === 'function') await window.refreshGalaxy();
                    window.showNodeDirector(srcNode);
                }
            } catch (e) { alert('连线失败: ' + e.message); }
        }
    });
};

window.triggerUnlink = (srcId, targetId) => {
    window.Swal?.fire({
        title: '确认断开连线？', text: '该操作将断开这两篇笔记在星谱中的关联连线。',
        icon: 'warning', showCancelButton: true, confirmButtonText: '确定断开', cancelButtonText: '取消', background: 'rgba(20,20,20,0.95)', color: '#fff', confirmButtonColor: '#d33'
    }).then(async (result) => {
        if (result.isConfirmed) {
            try {
                const res = await apiFetch('/api/galaxy/unlink', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ src: srcId, target: targetId }) });
                if (res && res.status === 'success') {
                    if (typeof window.refreshGalaxy === 'function') await window.refreshGalaxy();
                    const currentNode = window.galaxyGraph?.graphData()?.nodes.find(n => n.id === srcId);
                    if (currentNode) window.showNodeDirector(currentNode);
                    else window.closeNodeDirector();
                }
            } catch (e) { alert('断开失败: ' + e.message); }
        }
    });
};

function calculateUniversalWordCount(text) {
    if (!text) return 0;
    const body = text.replace(/^---[\s\S]*?---\s*/, '').replace(/```[\s\S]*?```|`[^`\n]*`|<[^>]+>/g, ' ');
    const cjk = (body.match(/[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u30ff\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]/g) || []).length;
    const words = (body.replace(/[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u30ff\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]/g, ' ').match(/[\p{L}\p{N}]+(?:[-'][\p{L}\p{N}]+)*/gu) || []).length;
    return cjk + words;
}
