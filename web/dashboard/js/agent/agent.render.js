/**
 * 🏢 Illacme Plenipes - Sovereign Copilot (Agent) UI Render Layer - Main Hub
 * 职责：调度子模块、处理通用消息追加日志等。
 * 对应重构拆分协议：SOP-02/SOP-05 模板一合规重组。
 */
(function() {
    if (window._dbgLog) window._dbgLog('📦 agent.render.js initializing');

    const renderMarkdown = text => (typeof window.renderMarkdown === 'function' ? window.renderMarkdown(text) : text);

    window.SovereignAgent = window.SovereignAgent || {};
    window.SovereignAgent.render = window.SovereignAgent.render || {};

    /**
     * 向控制面板的 feed 容器追加特定样式的消息
     * @param {string} text 
     * @param {string} typeClass 
     */
    window.SovereignAgent.render.appendMessage = function(text, typeClass) {
        const agentFeed = document.getElementById('agent-feed');
        if (!agentFeed) return;
        const msgDiv = document.createElement('div');
        msgDiv.className = `agent-msg ${typeClass}`;
        msgDiv.innerHTML = renderMarkdown(text);
        agentFeed.appendChild(msgDiv);
        agentFeed.scrollTop = agentFeed.scrollHeight;
    };

    const _esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');

    /**
     * 🎨 [Feature: Rich Editorial Artifact Cards] 渲染主编智能体生成的播客/电子书/封面富媒体卡片
     */
    window.SovereignAgent.render.renderArtifactCard = function(data) {
        const agentFeed = document.getElementById('agent-feed');
        if (!agentFeed || !data || !data.artifact) return;

        const art = data.artifact;
        const aType = art.artifact_type || '';
        const card = document.createElement('div');
        card.className = 'agent-msg artifact-card glass-panel';
        card.style.cssText = 'margin: 8px 0; padding: 10px 12px; border-radius: 8px; border-left: 3px solid var(--accent-secondary); background: var(--neon-cyan-05); display: flex; flex-direction: column; gap: 6px;';

        if (aType === 'podcast') {
            const title = _esc(art.title || art.document || art.filename || '播客单集');
            const audioUrl = _esc(art.audio_url || '');
            const lang = _esc((art.lang || 'zh').toUpperCase());
            const durSec = art.duration_ms ? `${(Number(art.duration_ms) / 1000).toFixed(1)}s` : '已就绪';
            card.innerHTML = `
                <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;">
                    <span style="font-weight:700;color:var(--accent-secondary);font-size:0.74rem;">🎙️ 播客单集已合成</span>
                    <span class="version-tag tiny" style="font-size:0.6rem;">${lang} · ${durSec}</span>
                </div>
                <div style="font-size:0.72rem;color:var(--text-bright);font-weight:600;">${title}</div>
                ${audioUrl ? `<audio controls preload="metadata" src="${audioUrl}" style="width:100%;height:32px;margin-top:2px;"></audio>` : ''}
                <div style="display:flex;justify-content:flex-end;gap:6px;margin-top:2px;">
                    <button type="button" class="mini-btn" onclick="if(typeof window.showView==='function'){window.showView('tasks','podcast');}" style="font-size:0.65rem;padding:2px 8px;">📡 打开播客电台</button>
                </div>`;
        } else if (aType === 'ebook') {
            const fname = _esc(art.filename || 'digital_book');
            const fmt = _esc((art.format || 'webbook').toUpperCase());
            const lang = _esc((art.target_lang || 'zh').toUpperCase());
            const rawDl = art.download_url && !art.download_url.includes('/api/bindery/download/')
                ? art.download_url
                : `/api/bindery/download?file=${encodeURIComponent(art.filename || 'digital_book')}`;
            const rawPv = art.preview_url || `/api/bindery/view?file=${encodeURIComponent(art.filename || 'digital_book')}`;
            const dlUrl = _esc(rawDl);
            const pvUrl = _esc(rawPv);
            card.innerHTML = `
                <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;">
                    <span style="font-weight:700;color:var(--accent-secondary);font-size:0.74rem;">📚 数字典籍已装订</span>
                    <span class="version-tag tiny" style="font-size:0.6rem;">${fmt} · ${lang}</span>
                </div>
                <div style="font-size:0.72rem;color:var(--text-bright);font-family:var(--font-mono);word-break:break-all;">${fname}</div>
                <div style="display:flex;justify-content:flex-end;gap:6px;margin-top:4px;flex-wrap:wrap;">
                    <a href="${pvUrl}" target="_blank" class="mini-btn" style="font-size:0.65rem;padding:2px 8px;text-decoration:none;">📖 在线翻阅</a>
                    <a href="${dlUrl}" download="${fname}" class="mini-btn" style="font-size:0.65rem;padding:2px 8px;text-decoration:none;">📥 下载印本</a>
                    <button type="button" class="mini-btn" onclick="if(typeof window.showView==='function'){window.showView('tasks','shelf');}" style="font-size:0.65rem;padding:2px 8px;">📚 打开书架</button>
                </div>`;
        } else if (aType === 'cover') {
            const title = _esc(art.title || art.document || '文章封面');
            const coverUrl = _esc(art.cover_url || '');
            const ratio = _esc(art.aspect_ratio || '16:9');
            const strat = _esc(art.strategy || 'og_card');
            card.innerHTML = `
                <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;">
                    <span style="font-weight:700;color:var(--accent-secondary);font-size:0.74rem;">🖼️ 视觉封面已生成</span>
                    <span class="version-tag tiny" style="font-size:0.6rem;">${ratio} · ${strat}</span>
                </div>
                <div style="font-size:0.7rem;color:var(--text-dim);">${title} ${art.applied_to_frontmatter ? '· ✅ 已绑定 Frontmatter' : ''}</div>
                ${coverUrl ? `<img src="${coverUrl}?t=${Date.now()}" alt="${title}" style="width:100%;max-height:130px;object-fit:cover;border-radius:6px;cursor:pointer;border:1px solid var(--neon-cyan-20);" onclick="if(typeof window.showImageModal==='function')window.showImageModal('${coverUrl}','${title}');" />` : ''}`;
        } else {
            return;
        }

        agentFeed.appendChild(card);
        agentFeed.scrollTop = agentFeed.scrollHeight;
    };

    /**
     * 🤖 [Feature: Dead-Letter AI Self-Healing] 从发布中心死信行一键唤醒右侧主编智能体执行故障诊断与修复
     */
    window.askCopilotToDiagnoseTask = function(relPath, targetId, errorMsg) {
        const appContainer = document.getElementById('app-container');
        if (appContainer && appContainer.classList.contains('right-collapsed')) {
            if (typeof window.toggleSidebar === 'function') window.toggleSidebar('right');
            else appContainer.classList.remove('right-collapsed');
        }
        const cleanErr = String(errorMsg || '未知异常').slice(0, 160);
        const prompt = `请诊断并协助修复分发异常：稿件 ${relPath || '全站'} 推送至渠道 ${targetId || '目标平台'} 失败（错误摘要：${cleanErr}）。请调用 diagnose_dispatch_failures 并给出具体自愈方案。`;
        if (window.SovereignAgent && typeof window.SovereignAgent.submitPrompt === 'function') {
            window.SovereignAgent.submitPrompt(prompt);
        } else {
            const input = document.getElementById('agent-command-input');
            if (input) {
                input.value = prompt;
                input.focus();
            }
        }
    };
})();
