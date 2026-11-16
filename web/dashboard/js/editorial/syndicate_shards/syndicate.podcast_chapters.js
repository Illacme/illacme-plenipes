// web/dashboard/js/editorial/syndicate_shards/syndicate.podcast_chapters.js
// 🎙️ 播客工坊章节分段、交互式跳转与 Show Notes 时间戳一键复制中枢
// 🛡️ [SOP-01] 物理行数严格保持在 300 行以内。

(function (window) {
    'use strict';

    let _lastChaptersShownotes = '';

    function _esc(str) {
        if (!str) return '';
        return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    /**
     * 渲染播客章节药丸与 Show Notes 控制面板
     */
    function renderPodcastChaptersHtml(chapters, shownotes) {
        if (!Array.isArray(chapters) || chapters.length === 0) {
            return '';
        }
        _lastChaptersShownotes = shownotes || '';

        const pillItems = chapters.map(c => {
            const sec = parseInt(c.start_seconds || 0, 10);
            const timeStr = _esc(c.start_time || '00:00');
            const title = _esc(c.title || '章节');
            return `<button type="button" class="mini-btn chapter-jump-pill" onclick="window.seekPodcastAudio(${sec})" style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);color:#cbd5e1;border-radius:20px;padding:3px 10px;font-size:0.75rem;cursor:pointer;white-space:nowrap;display:inline-flex;align-items:center;gap:5px;transition:all 0.2s ease;">
                <span style="color:#a855f7;font-family:monospace;font-weight:600;">⏱️ ${timeStr}</span>
                <span>${title}</span>
            </button>`;
        }).join('');

        return `<div class="podcast-chapters-panel" style="margin-top:12px;background:rgba(15,23,42,0.6);border:1px solid rgba(168,85,247,0.22);border-radius:10px;padding:12px 14px;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                <div style="font-size:0.8rem;color:#f8fafc;font-weight:600;display:flex;align-items:center;gap:6px;">
                    <span>⏱️ 节目章节时间轴</span>
                    <span style="font-size:0.7rem;color:#94a3b8;font-weight:normal;">(${chapters.length} 个分段 · 点击快速试听)</span>
                </div>
                <button type="button" class="mini-btn glow-btn" onclick="window.copyPodcastChapters(this)" style="background:linear-gradient(135deg, rgba(168,85,247,0.2) 0%, rgba(99,102,241,0.25) 100%);border:1px solid rgba(168,85,247,0.5);color:#c084fc;padding:3px 10px;font-size:0.74rem;border-radius:6px;cursor:pointer;">
                    📋 复制时间戳 Show Notes
                </button>
            </div>
            <div class="podcast-chapters-scroll" style="display:flex;align-items:center;gap:8px;overflow-x:auto;padding-bottom:4px;scrollbar-width:thin;">
                ${pillItems}
            </div>
        </div>`;
    }

    /**
     * 一键复制小宇宙 / Apple / Spotify 标准格式的 Show Notes
     */
    function copyPodcastChapters(btn) {
        if (!_lastChaptersShownotes) {
            if (typeof window.showToast === 'function') {
                window.showToast('暂无生成的时间戳文本', 'warning');
            }
            return;
        }

        navigator.clipboard.writeText(_lastChaptersShownotes).then(() => {
            const originalText = btn ? btn.innerHTML : '';
            if (btn) {
                btn.innerHTML = '✅ 已复制 Show Notes！';
                btn.style.borderColor = '#4ade80';
                btn.style.color = '#4ade80';
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.style.borderColor = 'rgba(168,85,247,0.5)';
                    btn.style.color = '#c084fc';
                }, 2000);
            }
            if (typeof window.showToast === 'function') {
                window.showToast('分段时间戳已复制！可直接粘贴至小宇宙、Apple播客或Spotify节目简介', 'success');
            }
        }).catch(err => {
            console.error('复制失败:', err);
            if (typeof window.showToast === 'function') {
                window.showToast('复制到剪贴板失败，请手动选取', 'error');
            }
        });
    }

    /**
     * 点击章节药丸快速跳转音频播放位置
     */
    function seekPodcastAudio(seconds) {
        const audioEl = document.getElementById('podcast-player-audio');
        if (!audioEl) {
            console.warn('未找到播放器元素 #podcast-player-audio');
            return;
        }
        audioEl.currentTime = Math.max(0, seconds);
        audioEl.play().catch(e => console.warn('音频快进播放受阻:', e));
    }

    // 挂载至全局命名空间
    window.renderPodcastChaptersHtml = renderPodcastChaptersHtml;
    window.copyPodcastChapters = copyPodcastChapters;
    window.seekPodcastAudio = seekPodcastAudio;

    // 🎙️ 全库待合成播客音频一键批量合成队列控制器
    let _batchPodcastAbort = false, _batchPodcastRunning = false;

    window.cancelBatchPodcastSynthesis = function () {
        _batchPodcastAbort = true;
        const btn = document.getElementById('batch-podcast-cancel-btn');
        if (btn) { btn.disabled = true; btn.innerText = '🛑 正在中断...'; }
    };

    window.closeBatchPodcastModal = function () {
        if (_batchPodcastRunning) { window.cancelBatchPodcastSynthesis(); return; }
        const el = document.getElementById('batch-podcast-modal-backdrop');
        if (el) el.style.display = 'none';
    };

    window.openBatchPodcastModal = async function () {
        if (_batchPodcastRunning) return;
        let pending = [];
        try {
            const res = typeof window.apiFetch === 'function' ? await window.apiFetch('/api/podcast/overview') : await fetch('/api/podcast/overview').then(r => r.json());
            pending = (res && Array.isArray(res.pending_docs)) ? res.pending_docs : [];
        } catch (e) {
            if (typeof window.showToast === 'function') window.showToast('扫描待合成播客失败: ' + e.message, 'error');
            return;
        }
        if (pending.length === 0) {
            if (typeof window.showToast === 'function') window.showToast('🎉 当前所有开启伴读播客的稿件均已合成就绪，无需补合！', 'success');
            return;
        }
        let bd = document.getElementById('batch-podcast-modal-backdrop');
        if (!bd) {
            bd = document.createElement('div');
            bd.id = 'batch-podcast-modal-backdrop';
            bd.style.cssText = 'display:none;position:fixed;inset:0;background:rgba(0,0,0,0.75);backdrop-filter:blur(8px);z-index:99999;align-items:center;justify-content:center;padding:20px;';
            document.body.appendChild(bd);
        }
        const listHtml = pending.map((d, i) => `
            <div id="batch-pod-item-${i}" style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;border-radius:8px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);margin-bottom:6px;font-size:0.82rem;">
                <div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#e2e8f0;"><span style="color:#94a3b8;margin-right:6px;">#${i + 1}</span>${_esc(d.title || d.rel_path)} <span style="font-size:0.72rem;color:#64748b;">(${_esc(d.rel_path)})</span></div>
                <span id="batch-pod-stat-${i}" style="font-size:0.74rem;color:#fbbf24;white-space:nowrap;margin-left:10px;">⏳ 待合成</span>
            </div>`).join('');

        bd.innerHTML = `<div style="background:#090d16;border:1px solid rgba(168,85,247,0.35);box-shadow:0 25px 50px -12px rgba(0,0,0,0.8);width:100%;max-width:600px;border-radius:16px;overflow:hidden;display:flex;flex-direction:column;">
            <div style="display:flex;justify-content:space-between;align-items:center;padding:16px 20px;border-bottom:1px solid rgba(255,255,255,0.08);background:rgba(15,23,42,0.85);">
                <div style="display:flex;align-items:center;gap:10px;"><span style="font-size:1.3rem;">🎙️</span><div><div style="font-size:0.98rem;font-weight:700;color:#f8fafc;">批量合成待处理播客音频 (共 ${pending.length} 篇)</div><div style="font-size:0.74rem;color:#94a3b8;">自动提炼双人对谈剧本并合成 128kbps 伴读 MP3 与章节时间轴</div></div></div>
                <button type="button" onclick="window.closeBatchPodcastModal()" style="background:none;border:none;color:#94a3b8;font-size:1.1rem;cursor:pointer;">✕</button>
            </div>
            <div style="padding:16px 20px;">
                <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:12px;padding:8px 12px;background:rgba(168,85,247,0.08);border:1px solid rgba(168,85,247,0.25);border-radius:8px;">
                    <span style="font-size:0.78rem;color:#e2e8f0;font-weight:600;">🌐 衍生语种矩阵:</span>
                    <div style="display:flex;gap:12px;font-size:0.78rem;color:#cbd5e1;">
                        <label style="display:inline-flex;align-items:center;gap:4px;cursor:pointer;"><input type="checkbox" class="batch-pod-lang-cb" value="zh" checked> 🇨🇳 中文 (zh)</label>
                        <label style="display:inline-flex;align-items:center;gap:4px;cursor:pointer;"><input type="checkbox" class="batch-pod-lang-cb" value="en"> 🇺🇸 English (en)</label>
                        <label style="display:inline-flex;align-items:center;gap:4px;cursor:pointer;"><input type="checkbox" class="batch-pod-lang-cb" value="ja"> 🇯🇵 日本語 (ja)</label>
                    </div>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#cbd5e1;margin-bottom:8px;"><span id="batch-podcast-status-text">已就绪，点击下方按钮开始顺序合成</span><span id="batch-podcast-pct">0 / ${pending.length}</span></div>
                <div style="height:8px;background:rgba(255,255,255,0.08);border-radius:99px;overflow:hidden;margin-bottom:14px;"><div id="batch-podcast-bar" style="height:100%;width:0%;background:linear-gradient(90deg,#a855f7,#38bdf8);transition:width 0.3s ease;"></div></div>
                <div style="max-height:260px;overflow-y:auto;padding-right:4px;">${listHtml}</div>
            </div>
            <div style="display:flex;justify-content:flex-end;gap:10px;padding:12px 20px;border-top:1px solid rgba(255,255,255,0.08);background:rgba(15,23,42,0.5);">
                <button type="button" id="batch-podcast-cancel-btn" class="mini-btn" onclick="window.closeBatchPodcastModal()" style="padding:6px 14px;">关闭</button>
                <button type="button" id="batch-podcast-start-btn" class="primary-btn glow-btn" onclick="window.startBatchPodcastExecution()" style="padding:6px 16px;background:linear-gradient(135deg,#a855f7,#6366f1);border:none;color:#fff;">🚀 开始一键批量合成</button>
            </div>
        </div>`;
        bd.style.display = 'flex';
        window._pendingPodcastBatchList = pending;
    };

    window.startBatchPodcastExecution = async function () {
        const list = window._pendingPodcastBatchList || [];
        if (_batchPodcastRunning || list.length === 0) return;
        const checkedLangs = Array.from(document.querySelectorAll('.batch-pod-lang-cb:checked')).map(cb => cb.value);
        const langs = checkedLangs.length > 0 ? checkedLangs : ['zh'];
        _batchPodcastRunning = true; _batchPodcastAbort = false;
        const startBtn = document.getElementById('batch-podcast-start-btn'), cancelBtn = document.getElementById('batch-podcast-cancel-btn');
        const statusTxt = document.getElementById('batch-podcast-status-text'), pctTxt = document.getElementById('batch-podcast-pct'), barEl = document.getElementById('batch-podcast-bar');
        if (startBtn) { startBtn.disabled = true; startBtn.innerText = '⚙️ 正在合成队列...'; }
        if (cancelBtn) { cancelBtn.innerText = '🛑 停止队列'; }

        const token = localStorage.getItem('token') || '';
        const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };
        let doneCount = 0;

        for (let i = 0; i < list.length; i++) {
            if (_batchPodcastAbort) break;
            const item = list[i], statEl = document.getElementById(`batch-pod-stat-${i}`);
            if (statusTxt) statusTxt.innerText = `正在处理 (${i + 1}/${list.length}): 《${item.title}》 [${langs.join('/').toUpperCase()}]...`;
            try {
                for (const lg of langs) {
                    if (_batchPodcastAbort) break;
                    if (statEl) { statEl.style.color = '#38bdf8'; statEl.innerText = `📝 提炼剧本 (${lg.toUpperCase()})...`; }
                    const sResp = await fetch('/api/podcast/script/extract', { method: 'POST', headers, body: JSON.stringify({ rel_path: item.rel_path, lang: lg, style: 'tech_deep', max_turns: 10, use_ai: false }) });
                    const sData = await sResp.json();
                    if (!sResp.ok || sData.status !== 'success') throw new Error(sData.detail || '剧本提取失败');
                    if (_batchPodcastAbort) break;
                    if (statEl) { statEl.style.color = '#c084fc'; statEl.innerText = `🎙️ 合成音频 (${lg.toUpperCase()})...`; }
                    const synResp = await fetch('/api/podcast/synthesize', { method: 'POST', headers, body: JSON.stringify({ rel_path: item.rel_path, title: sData.data.title || item.title, turns: sData.data.turns, lang: lg, style: 'tech_deep', bgm_style: 'cyber_ambient', pause_ms: 380 }) });
                    const synData = await synResp.json();
                    if (!synResp.ok || synData.status !== 'success') throw new Error(synData.detail || '语音合成失败');
                }
                if (_batchPodcastAbort) { if (statEl) statEl.innerText = '⏹️ 已取消'; break; }
                doneCount++;
                if (statEl) { statEl.style.color = '#4ade80'; statEl.innerText = `✅ 已合成 (${langs.join('/').toUpperCase()})`; }
            } catch (err) {
                if (statEl) { statEl.style.color = '#f87171'; statEl.innerText = '❌ 失败: ' + (err.message || '异常'); }
            }
            if (barEl) barEl.style.width = `${Math.round(((i + 1) / list.length) * 100)}%`;
            if (pctTxt) pctTxt.innerText = `${i + 1} / ${list.length}`;
        }

        _batchPodcastRunning = false;
        if (statusTxt) statusTxt.innerText = _batchPodcastAbort ? `⏹️ 队列已中止 (已完成 ${doneCount}/${list.length} 篇)` : `🎉 批量合成完毕！成功生成 ${doneCount} 篇 × ${langs.length} 语种播客音频`;
        if (startBtn) startBtn.innerText = '✅ 已完成';
        if (cancelBtn) { cancelBtn.disabled = false; cancelBtn.innerText = '关闭窗口'; }
        if (typeof window.loadVault === 'function') window.loadVault(null, null, { keepScroll: true, silent: true });
        if (typeof window.loadDispatchPodcastCenter === 'function') window.loadDispatchPodcastCenter();
        if (typeof window.updatePodcastBadge === 'function') window.updatePodcastBadge();
    };

    window.triggerMultiLangPodcastSynthesis = async function (relPath, style = 'tech_deep', bgm = 'cyber_ambient', btn = null) {
        if (!relPath) return;
        const origText = btn ? btn.innerText : '';
        if (btn) { btn.disabled = true; btn.innerText = '🌐 多语联产中 (zh/en/ja)...'; }
        const token = localStorage.getItem('token') || '';
        const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };
        const ttsProvider = (document.getElementById('podcast-tts-provider') || {}).value || window.settingsData?.podcast?.podcast_tts_engines?.default_provider || 'edge';
        const rate = (document.getElementById('podcast-rate-select') || {}).value || '+0%';
        const focusPrompt = ((document.getElementById('podcast-focus-input') || {}).value || '').trim() || null;
        const hostA = ((document.getElementById('podcast-host-a') || {}).value || '').trim() || null;
        const hostB = ((document.getElementById('podcast-host-b') || {}).value || '').trim() || null;
        const langs = typeof window.getEnabledPodcastLangs === 'function' ? window.getEnabledPodcastLangs() : ['zh', 'en', 'ja'];
        let okLangs = [], skippedLangs = [];
        try {
            for (const lg of langs) {
                if (btn) btn.innerText = `🌐 检查 ${lg.toUpperCase()}...`;
                const info = await fetch(`/api/podcast/info?rel_path=${encodeURIComponent(relPath)}&lang=${encodeURIComponent(lg)}&style=${encodeURIComponent(style)}`).then((r) => r.json()).catch(() => null);
                if (info && info.exists) { skippedLangs.push(lg.toUpperCase()); continue; }
                if (btn) btn.innerText = `🌐 正在衍生 ${lg.toUpperCase()}...`;
                const sResp = await fetch('/api/podcast/script/extract', { method: 'POST', headers, body: JSON.stringify({ rel_path: relPath, lang: lg, style, max_turns: 10, use_ai: false, focus_prompt: focusPrompt, host_a_name: hostA, host_b_name: hostB }) });
                const sData = await sResp.json();
                if (!sResp.ok || sData.status !== 'success') continue;
                const synResp = await fetch('/api/podcast/synthesize', { method: 'POST', headers, body: JSON.stringify({ rel_path: relPath, title: sData.data.title || 'Podcast', turns: sData.data.turns, lang: lg, style, bgm_style: bgm, pause_ms: 380, rate, tts_provider: ttsProvider }) });
                const synData = await synResp.json();
                if (synResp.ok && synData.status === 'success') okLangs.push(lg.toUpperCase());
            }
            const summary = [okLangs.length ? `新生成: ${okLangs.join('/')}` : '', skippedLangs.length ? `已跳过已有: ${skippedLangs.join('/')}` : ''].filter(Boolean).join(' · ') || '无新增语种';
            if (typeof window.showToast === 'function') window.showToast(`🎉 批量联产完成！${summary}`, 'success');
            if (typeof window.openPodcastStudioModal === 'function') await window.openPodcastStudioModal(relPath);
        } catch (e) {
            if (typeof window.showToast === 'function') window.showToast('多语联产异常: ' + (e.message || e), 'error');
        } finally {
            if (btn) { btn.disabled = false; btn.innerText = origText || '🌐 多语联产 (中/英/日)'; }
        }
    };

    window.deletePodcastEpisode = async function (filename, imprintId = 'default') {
        if (!filename) return;
        const ok = typeof window.confirmSovereignAction === 'function'
            ? await window.confirmSovereignAction({ title: '🗑️ 确认删除该期播客单集？', text: `即将物理删除音频缓存文件 <b>${_esc(filename)}</b> 及其章节标记文件。`, confirmText: '确认删除', confirmColor: '#ef4444', cancelText: '取消' })
            : window.confirm(`确认删除播客单集 ${filename} 吗？`);
        if (!ok) return;
        try {
            const token = localStorage.getItem('token') || '';
            const resp = await fetch(`/api/podcast/audio/${encodeURIComponent(imprintId)}/${encodeURIComponent(filename)}`, { method: 'DELETE', headers: { 'Authorization': `Bearer ${token}` } });
            const data = await resp.json();
            if (!resp.ok || data.status !== 'success') throw new Error(data.detail || '删除失败');
            if (typeof window.showToast === 'function') window.showToast(`🗑️ 已清理播客单集: ${filename}`, 'success');
            if (typeof window.loadDispatchPodcastCenter === 'function') window.loadDispatchPodcastCenter();
            if (typeof window.updatePodcastBadge === 'function') window.updatePodcastBadge();
            if (typeof window.loadVault === 'function') window.loadVault(null, null, { keepScroll: true, silent: true });
        } catch (e) {
            if (typeof window.showToast === 'function') window.showToast('删除单集失败: ' + (e.message || e), 'error');
        }
    };

    window.batchSyncPodcastsToCdn = async function (btn) {
        const orig = btn ? btn.innerText : '';
        if (btn) { btn.disabled = true; btn.innerText = '☁️ 正在批量转储...'; }
        try {
            const token = localStorage.getItem('token') || '';
            const resp = await fetch('/api/podcast/storage/sync', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ sync_all: true })
            });
            const data = await resp.json();
            if (!resp.ok || data.status !== 'success') throw new Error(data.detail || '批量转储失败');
            if (typeof window.showToast === 'function') window.showToast(`☁️ 已成功将 ${data.synced_count || 0} 期播客单集同步至 R2/S3 CDN！`, 'success');
            if (typeof window.loadDispatchPodcastCenter === 'function') window.loadDispatchPodcastCenter();
        } catch (e) {
            if (typeof window.showToast === 'function') window.showToast(e.message || '批量转储异常', 'error');
        } finally {
            if (btn) { btn.disabled = false; btn.innerText = orig || '☁️ 批量转储 CDN'; }
        }
    };

})(window);

