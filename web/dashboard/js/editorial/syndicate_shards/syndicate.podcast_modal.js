/**
 * 🎙️ [V1.0] Illacme Plenipes - Dual-Host Conversational Tech Podcast Studio
 * 职责：双人对话式技术播客剧本提炼、AI 深度编剧交互、BGM 智能闪避混音、128k MP3 合成。
 * 🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
 */

(function () {
    let _currentRelPath = '', _currentScript = null, _currentAudioInfo = null;
    let _selectedLang = 'zh', _selectedStyle = 'tech_deep', _selectedBgm = 'cyber_ambient', _isProcessing = false;

    const _esc = (s) => (s === null || s === undefined ? '' : String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'));

    const _LANG_LABELS = { zh: '中文 (晓晓/云希)', 'zh-tw': '繁體中文', en: 'English (Jenny/Guy)', ja: '日本語 (七海/圭太)', ko: '한국어', fr: 'Français', de: 'Deutsch', es: 'Español', pt: 'Português', ru: 'Русский', ar: 'العربية' };
    window.getEnabledPodcastLangs = function () {
        const i18n = window.settingsData?.i18n_settings || {};
        const src = String(i18n.source_language || 'zh').trim().toLowerCase();
        const tgts = Array.isArray(i18n.target_languages) ? i18n.target_languages.map((x) => String(x || '').trim().toLowerCase()).filter(Boolean) : [];
        const raw = tgts.length ? [src, ...tgts] : ['zh', 'en', 'ja'];
        return [...new Set(raw.filter(Boolean))];
    };

    window.openPodcastStudioModal = async function (relPath) {
        _currentRelPath = relPath || window.currentSyndicatingRelPath || (window.currentPreviewDoc && window.currentPreviewDoc.rel_path) || '';
        if (!_currentRelPath) return typeof window.showToast === 'function' && window.showToast('请先选择一篇文库稿件', 'warning');
        _ensureModalDom();
        _renderPodcastLangSelector();
        const savedProv = window.settingsData?.podcast?.podcast_tts_engines?.default_provider;
        const provSel = document.getElementById('podcast-tts-provider');
        if (provSel && savedProv && provSel.querySelector(`option[value="${savedProv}"]`)) provSel.value = savedProv;
        const backdrop = document.getElementById('syndicate-podcast-modal-backdrop');
        if (backdrop) backdrop.style.display = 'flex';
        await _extractScript(false);
    };

    window.closePodcastStudioModal = function () {
        const bd = document.getElementById('syndicate-podcast-modal-backdrop'), a = document.getElementById('podcast-player-audio');
        if (bd) bd.style.display = 'none';
        if (a) a.pause();
    };

    window.switchPodcastLang = async function (l) { if (!_isProcessing && _selectedLang !== l) { _selectedLang = l || 'zh'; _renderPodcastLangSelector(); await _extractScript(false); } };
    window.switchPodcastStyle = async function (s) { if (!_isProcessing && _selectedStyle !== s) { _selectedStyle = s || 'tech_deep'; _updatePillButtons('podcast-style-pills', _selectedStyle); await _extractScript(false); } };
    window.switchPodcastBgm = function (b) { if (!_isProcessing && _selectedBgm !== b) { _selectedBgm = b || 'cyber_ambient'; _updatePillButtons('podcast-bgm-pills', _selectedBgm); if (_currentAudioInfo) { _currentAudioInfo = null; _renderPlayerArea(); } } };

    window.triggerPodcastAiRewrite = async function () {
        if (_isProcessing) return;
        let confirmed = false;
        if (typeof window.confirmSovereignAction === 'function') {
            confirmed = await window.confirmSovereignAction({ title: '✨ 开启 AI 深度智能编剧？', text: '将调用当前算力中心模型对全文进行深度思辨与拟真剧本重构。<br><span style="color:#c084fc;font-size:0.82rem;">⏱️ 预计耗时约 3~8 秒 · 消耗模型上下文 Token</span>', confirmText: '🚀 确认开始编剧', confirmColor: '#a855f7', cancelText: '取消' });
        } else confirmed = window.confirm('将调用算力中心大模型深度重构播客剧本 (预计耗时 3~8 秒)，是否确认开始？');
        if (!confirmed) return;
        const stopProgress = _renderAiProgress();
        try {
            await _extractScript(true); stopProgress();
            if (typeof window.showToast === 'function') window.showToast('✨ 大模型已成功深度重构播客剧本！', 'success');
        } catch (err) {
            stopProgress();
            if (typeof window.showToast === 'function') window.showToast(`AI 编剧失败: ${err.message}`, 'error');
        }
    };

    window.extractScriptRule = function () { _extractScript(false); };
    window.updatePodcastTurnText = function (idx, text) {
        if (_currentScript?.turns?.[idx]) {
            _currentScript.turns[idx].text = (text || '').trim();
            if (_currentAudioInfo) { _currentAudioInfo = null; _renderPlayerArea(); }
        }
    };

    window.triggerPodcastSynthesis = async function () {
        if (_isProcessing || !_currentScript || !_currentScript.turns?.length) return;
        _isProcessing = true;
        _updateActionBtnState(true, '⚙️ 正在合成人声与智能垫乐混音 (约 5-10 秒)...');
        try {
            const token = localStorage.getItem('token') || '';
            const resp = await fetch('/api/podcast/synthesize', {
                method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ rel_path: _currentRelPath, title: _currentScript.title || '技术对谈播客', turns: _currentScript.turns, lang: _selectedLang, style: _selectedStyle, bgm_style: _selectedBgm, pause_ms: 380, rate: (document.getElementById('podcast-rate-select') || {}).value || '+0%', tts_provider: (document.getElementById('podcast-tts-provider') || {}).value || 'edge' })
            });
            const data = await resp.json();
            if (!resp.ok || data.status !== 'success') throw new Error(data.detail || '音频合成失败');
            _currentAudioInfo = data.data;
            if (typeof window.showToast === 'function') {
                if (data.data?.fallback_reason) window.showToast(`⚠️ ${data.data.fallback_reason}`, 'warning');
                else window.showToast(`🎉 播客单轨音频合成成功 (${data.data?.actual_provider || 'edge'})！`, 'success');
            }
            _renderPlayerArea();
        } catch (err) {
            if (typeof window.showToast === 'function') window.showToast(`合成失败: ${err.message}`, 'error');
        } finally {
            _isProcessing = false;
            _updateActionBtnState(false);
        }
    };

    window.copyPodcastRssFeed = function () {
        const url = `${window.location.origin}/api/podcast/feed/default?lang=${_selectedLang}`;
        navigator.clipboard?.writeText(url).then(() => { if (typeof window.showToast === 'function') window.showToast('📋 播客 RSS 订阅链接已复制！', 'success'); });
    };

    window.syncPodcastToCloud = async function (btn) {
        if (!_currentAudioInfo || !_currentAudioInfo.filename) return;
        const orig = btn.innerText; btn.innerText = '☁️ 转储中...'; btn.disabled = true;
        try {
            const resp = await fetch('/api/podcast/storage/sync', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` }, body: JSON.stringify({ filename: _currentAudioInfo.filename, rel_path: _currentRelPath, lang: _selectedLang, style: _selectedStyle }) });
            const data = await resp.json();
            if (!resp.ok || data.status !== 'success') throw new Error(data.detail || '云端转储失败');
            _currentAudioInfo.cdn_url = data.data?.cdn_url; btn.innerText = '✅ 已加速';
            if (typeof window.showToast === 'function') window.showToast(`☁️ 播客已成功转储至 CDN：${data.data?.cdn_url || ''}`, 'success');
            _renderPlayerArea();
        } catch (err) {
            btn.innerText = orig; btn.disabled = false;
            if (typeof window.showToast === 'function') window.showToast(err.message, 'error');
        }
    };

    async function _extractScript(useAi = false) {
        _isProcessing = true;
        if (!useAi) { _renderLoading('正在智能提炼双人对谈剧本并检索音频...'); _currentAudioInfo = null; }
        try {
            const token = localStorage.getItem('token') || '';
            const focusVal = ((document.getElementById('podcast-focus-input') || {}).value || '').trim();
            const hostA = ((document.getElementById('podcast-host-a') || {}).value || '').trim();
            const hostB = ((document.getElementById('podcast-host-b') || {}).value || '').trim();
            const scriptReq = fetch('/api/podcast/script/extract', {
                method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ rel_path: _currentRelPath, lang: _selectedLang, style: _selectedStyle, max_turns: 10, use_ai: !!useAi, focus_prompt: focusVal || null, host_a_name: hostA || null, host_b_name: hostB || null })
            });
            const audioReq = useAi ? Promise.resolve(null) : fetch(`/api/podcast/info?rel_path=${encodeURIComponent(_currentRelPath)}&lang=${_selectedLang}&style=${_selectedStyle}`).then((r) => r.json()).catch(() => null);

            const [sResp, aData] = await Promise.all([scriptReq, audioReq]);
            const sData = await sResp.json();
            if (!sResp.ok || sData.status !== 'success') throw new Error(sData.detail || '提炼剧本失败');
            _currentScript = sData.data;
            _currentScript.is_ai_generated = !!useAi;
            _currentAudioInfo = (aData && aData.exists && aData.data) ? aData.data : null;

            if (useAi) {
                const bar = document.getElementById('podcast-progress-bar'), pct = document.getElementById('podcast-progress-pct'), msg = document.getElementById('podcast-progress-msg');
                if (bar) bar.style.width = '100%'; if (pct) pct.textContent = '100%'; if (msg) msg.textContent = '🎉 剧本重构完成，正在呈现提词器...';
                await new Promise((r) => setTimeout(r, 260));
            }
            _renderScriptView();
        } catch (err) { _renderError(err.message); throw err; } finally { _isProcessing = false; }
    }

    function _renderAiProgress() {
        const bodyEl = document.getElementById('podcast-modal-body');
        if (!bodyEl) return () => {};
        bodyEl.innerHTML = `<div style="text-align:center;padding:56px 20px;"><div style="font-size:2.4rem;margin-bottom:12px;display:inline-block;animation:spin 3s linear infinite;">✨</div><div class="podcast-title" style="font-size:1.05rem;font-weight:600;margin-bottom:6px;">AI 深度智能编剧构思中</div><div id="podcast-progress-msg" class="podcast-sub" style="font-size:0.85rem;min-height:22px;">🔍 深入解析原稿核心架构与逻辑断点...</div><div style="width:100%;max-width:440px;height:8px;background:rgba(148,163,184,0.2);border-radius:99px;overflow:hidden;margin:18px auto;border:1px solid rgba(148,163,184,0.2);"><div id="podcast-progress-bar" style="height:100%;width:15%;background:linear-gradient(90deg,#a855f7,#38bdf8);border-radius:99px;transition:width 0.4s ease;box-shadow:0 0 12px rgba(168,85,247,0.5);"></div></div><div id="podcast-progress-pct" style="font-size:0.82rem;color:#c084fc;font-weight:600;">15%</div></div>`;
        const stages = [[32, '🔍 深入解析原稿核心架构与逻辑断点...'], [58, '🧠 算力大模型构思双人辩证与交替对白...'], [82, '🎙️ 注入拟人自然口语化修辞与过渡设问...'], [95, '⚡ 格式校验闭环，正在装配提词器...']];
        let idx = 0;
        const timer = setInterval(() => {
            if (idx < stages.length) {
                const [pctVal, msgVal] = stages[idx++];
                const bar = document.getElementById('podcast-progress-bar'), msg = document.getElementById('podcast-progress-msg'), pct = document.getElementById('podcast-progress-pct');
                if (bar) bar.style.width = `${pctVal}%`; if (msg) msg.textContent = msgVal; if (pct) pct.textContent = `${pctVal}%`;
            }
        }, 850);
        return () => clearInterval(timer);
    }

    function _renderScriptView() {
        const bodyEl = document.getElementById('podcast-modal-body');
        if (!bodyEl || !_currentScript) return;

        const turnsHtml = (_currentScript.turns || []).map((t, idx) => {
            const isA = t.speaker === 'host_a', col = isA ? '#0ea5e9' : '#9333ea', alpha = isA ? '14,165,233' : '147,51,234';
            return `<div style="display:flex;gap:12px;margin-bottom:10px;align-items:flex-start;"><div style="flex-shrink:0;width:74px;text-align:right;"><span style="display:inline-block;padding:2px 8px;border-radius:6px;font-size:0.74rem;font-weight:600;background:rgba(${alpha},0.14);color:${col};border:1px solid rgba(${alpha},0.35);">${_esc(t.speaker_name)}</span><div class="podcast-sub" style="font-size:0.65rem;margin-top:2px;">${isA ? '主讲人' : '搭档'}</div></div><div class="podcast-turn-bubble" contenteditable="true" onblur="window.updatePodcastTurnText(${idx}, this.innerText)" style="flex:1;background:rgba(${alpha},0.06);border:1px solid rgba(${alpha},0.32);border-radius:8px;padding:9px 13px;font-size:0.86rem;line-height:1.5;outline:none;" title="点击可直接编辑修改台词">${_esc(t.text)}</div></div>`;
        }).join('');

        const durMin = Math.floor((_currentScript.estimated_duration_sec || 60) / 60), durSec = (_currentScript.estimated_duration_sec || 60) % 60;
        const isAi = !!_currentScript.is_ai_generated;
        const aiBadge = isAi ? '<span style="font-size:0.7rem;background:rgba(168,85,247,0.2);color:#a855f7;padding:2px 8px;border-radius:4px;border:1px solid rgba(168,85,247,0.4);margin-left:8px;">✨ AI 深度编剧</span>' : '';
        const aiActionBtn = isAi
            ? `<button type="button" class="mini-btn glow-btn" onclick="window.triggerPodcastAiRewrite()" style="background:linear-gradient(135deg,#a855f7,#6366f1);color:#fff;">✨ 再次 AI 编剧</button><button type="button" class="mini-btn" onclick="window.extractScriptRule()" style="margin-left:4px;">⚡ 还原规则提取</button>`
            : `<button id="podcast-ai-rewrite-btn" type="button" class="mini-btn glow-btn" onclick="window.triggerPodcastAiRewrite()" style="background:linear-gradient(135deg,#a855f7,#6366f1);color:#fff;">✨ AI 深度编剧</button>`;

        bodyEl.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid var(--border-subtle,rgba(148,163,184,0.2));flex-wrap:wrap;gap:8px;flex-shrink:0;"><div><h3 class="podcast-title" style="margin:0;font-size:1rem;font-weight:600;display:flex;align-items:center;">《${_esc(_currentScript.title)}》 ${aiBadge}</h3><div class="podcast-sub" style="font-size:0.74rem;margin-top:2px;">话题：${_esc(_currentScript.topic)} · 预计时长：${durMin}分${durSec}秒 · 共 ${_currentScript.turns?.length || 0} 轮对谈 · <span style="color:#9333ea;">💡 点击台词可直接微调修改</span></div></div><div style="display:flex;gap:6px;align-items:center;">${aiActionBtn}<button type="button" class="mini-btn" onclick="window.copyPodcastRssFeed()" title="复制标准 Podcast RSS 链接">📻 复制 RSS</button></div></div><div style="flex:1;min-height:140px;overflow-y:auto;padding-right:6px;margin-bottom:12px;">${turnsHtml}</div><div id="podcast-player-container" style="flex-shrink:0;"></div>`;
        _renderPlayerArea();
    }

    function _renderPlayerArea() {
        const container = document.getElementById('podcast-player-container');
        if (!container) return;
        const sNames = { tech_deep: '深度剖析', casual_brief: '通俗快讯', debate: '观点交锋', solo_read: '单人伴读' };
        const bNames = { cyber_ambient: '🌌 科技未来垫乐', lofi_chill: '☕ Lo-Fi 温暖垫乐', white_noise: '🍃 沉浸微风底噪', none: '纯净干音' };
        const label = `${_LANG_LABELS[_selectedLang] || _selectedLang.toUpperCase()} · ${sNames[_selectedStyle] || _selectedStyle} · ${bNames[_selectedBgm] || _selectedBgm}`;

        if (_currentAudioInfo && _currentAudioInfo.audio_url) {
            const kbSize = Math.round((_currentAudioInfo.file_size_bytes || 0) / 1024);
            const cdnBadge = _currentAudioInfo.cdn_url ? `<span style="font-size:0.7rem;color:#38bdf8;background:rgba(56,189,248,0.15);padding:1px 6px;border-radius:4px;border:1px solid rgba(56,189,248,0.3);margin-left:6px;" title="${_esc(_currentAudioInfo.cdn_url)}">☁️ CDN 已加速</span>` : '';
            const cdnBtn = !_currentAudioInfo.cdn_url ? `<button type="button" class="mini-btn" onclick="window.syncPodcastToCloud(this)" style="background:rgba(249,115,22,0.18);color:#fb923c;border:1px solid rgba(249,115,22,0.35);">☁️ CDN 转储</button>` : '';
            const audioSrc = _esc(_currentAudioInfo.cdn_url || _currentAudioInfo.audio_url);
            const chaps = _currentAudioInfo.chapters || (_currentScript ? _currentScript.chapters : null);
            const notes = _currentAudioInfo.shownotes_formatted || (_currentScript ? _currentScript.shownotes_formatted : '');
            const chapsHtml = window.renderPodcastChaptersHtml ? window.renderPodcastChaptersHtml(chaps, notes) : '';
            container.innerHTML = `<div class="podcast-player-card" style="border:1px solid rgba(168,85,247,0.3);border-radius:10px;padding:10px 14px;display:flex;align-items:center;gap:12px;"><span style="font-size:1.6rem;">🎧</span><div style="flex:1;min-width:0;"><div class="podcast-title" style="font-size:0.83rem;font-weight:500;">单轨技术播客已就绪 · ${label} (${kbSize} KB) ${cdnBadge}</div><audio id="podcast-player-audio" controls src="${audioSrc}" style="width:100%;height:32px;margin-top:6px;outline:none;"></audio></div><div style="display:flex;gap:6px;flex-shrink:0;">${cdnBtn}${_currentAudioInfo.transcript_url ? `<a href="${_esc(_currentAudioInfo.transcript_url)}" download class="mini-btn" style="text-decoration:none;display:inline-flex;align-items:center;" title="下载 WebVTT 同步字幕">📝 字幕</a>` : ''}<a href="${audioSrc}" download="${_esc(_currentAudioInfo.filename || 'podcast.mp3')}" class="mini-btn glow-btn" style="background:#8b5cf6;color:#fff;text-decoration:none;display:inline-flex;align-items:center;">⬇️ 下载</a><button type="button" class="mini-btn" onclick="window.triggerPodcastSynthesis()">🔄 重置</button></div></div>${chapsHtml}`;
        } else {
            const langCount = window.getEnabledPodcastLangs().length;
            container.innerHTML = `<div style="display:flex;justify-content:flex-end;gap:10px;flex-wrap:wrap;"><button type="button" class="mini-btn" onclick="if(window.triggerMultiLangPodcastSynthesis) window.triggerMultiLangPodcastSynthesis('${_esc(_currentRelPath)}','${_selectedStyle}','${_selectedBgm}',this)" style="background:rgba(56,189,248,0.14);color:#38bdf8;border:1px solid rgba(56,189,248,0.35);padding:8px 14px;font-size:0.84rem;border-radius:8px;">🌐 批量联产 (${langCount} 语)</button><button id="podcast-synthesize-btn" type="button" class="mini-btn glow-btn" onclick="window.triggerPodcastSynthesis()" style="background:linear-gradient(135deg, #a855f7 0%, #6366f1 100%);color:#fff;padding:8px 20px;font-size:0.9rem;border-radius:8px;">🎙️ 一键合成 ${label} 播客单轨 MP3</button></div>`;
        }
    }

    function _renderLoading(msg) {
        const el = document.getElementById('podcast-modal-body');
        if (el) el.innerHTML = `<div style="text-align:center;padding:60px 20px;"><div style="font-size:2rem;margin-bottom:12px;">🎙️</div><div style="color:#94a3b8;font-size:0.9rem;">${_esc(msg)}</div></div>`;
    }
    function _renderError(msg) {
        const el = document.getElementById('podcast-modal-body');
        if (el) el.innerHTML = `<div style="text-align:center;padding:40px 20px;"><div style="font-size:2rem;margin-bottom:12px;">⚠️</div><div style="color:#ef4444;font-size:0.9rem;margin-bottom:16px;">${_esc(msg)}</div><button type="button" class="mini-btn" onclick="window.openPodcastStudioModal('${_esc(_currentRelPath)}')">重试</button></div>`;
    }
    function _renderPodcastLangSelector() {
        const box = document.getElementById('podcast-lang-pills');
        if (!box) return;
        const langs = window.getEnabledPodcastLangs();
        if (!langs.includes(_selectedLang)) _selectedLang = langs[0] || 'zh';
        const lbl = (c) => _LANG_LABELS[c] || c.toUpperCase();
        if (langs.length <= 3) {
            box.innerHTML = langs.map((v) => `<button type="button" class="podcast-pill-btn ${v===_selectedLang?'active':''}" data-val="${v}" onclick="window.switchPodcastLang('${v}')">${lbl(v)}</button>`).join('');
            return;
        }
        const quick = langs.slice(0, 2).map((v) => `<button type="button" class="podcast-pill-btn ${v===_selectedLang?'active':''}" data-val="${v}" onclick="window.switchPodcastLang('${v}')">${lbl(v)}</button>`).join('');
        const opts = langs.map((v) => `<option value="${v}" ${v===_selectedLang?'selected':''}>${lbl(v)}</option>`).join('');
        box.innerHTML = `${quick}<select id="podcast-lang-select" class="podcast-input" onchange="window.switchPodcastLang(this.value)" style="width:auto;max-width:155px;padding:3px 8px;" title="共 ${langs.length} 个已启用语种">${opts}</select>`;
    }
    function _updatePillButtons(cid, val) { document.getElementById(cid)?.querySelectorAll('.podcast-pill-btn').forEach((b) => b.classList.toggle('active', b.getAttribute('data-val') === val)); }
    function _updateActionBtnState(loading, text) {
        const btn = document.getElementById('podcast-synthesize-btn');
        if (btn) { btn.disabled = loading; btn.textContent = loading ? text : '🎙️ 一键合成双人播客单轨 MP3'; btn.style.opacity = loading ? '0.6' : '1'; }
    }

    function _ensureModalDom() {
        if (document.getElementById('syndicate-podcast-modal-backdrop')) return;
        const sPills = [['tech_deep','深度剖析'],['casual_brief','通俗快讯'],['debate','观点交锋'],['solo_read','单人伴读']].map(([v,l]) => `<button type="button" class="podcast-pill-btn ${v==='tech_deep'?'active':''}" data-val="${v}" onclick="window.switchPodcastStyle('${v}')">${l}</button>`).join('');
        const bPills = [['cyber_ambient','🌌 科技未来'],['lofi_chill','☕ Lo-Fi 温暖'],['white_noise','🍃 沉浸微风'],['none','🎙️ 纯净干音']].map(([v,l]) => `<button type="button" class="podcast-pill-btn ${v==='cyber_ambient'?'active':''}" data-val="${v}" onclick="window.switchPodcastBgm('${v}')">${l}</button>`).join('');
        const html = `<div id="syndicate-podcast-modal-backdrop" style="display:none;position:fixed;inset:0;background:rgba(15,23,42,0.45);backdrop-filter:blur(8px);z-index:99999;align-items:center;justify-content:center;padding:20px;">
            <style>
                .podcast-modal-card{background:#0b1020;color:#e2e8f0;border:1px solid rgba(168,85,247,0.3);box-shadow:0 25px 50px -12px rgba(0,0,0,0.65);}
                .podcast-modal-header{background:rgba(15,23,42,0.85);border-bottom:1px solid rgba(255,255,255,0.08);}
                .podcast-modal-toolbar{background:rgba(15,23,42,0.45);border-bottom:1px solid rgba(255,255,255,0.06);}
                .podcast-title{color:#f8fafc;} .podcast-sub{color:#94a3b8;} .podcast-turn-bubble{color:#e2e8f0;}
                .podcast-player-card,.podcast-inline-cfg{background:rgba(15,23,42,0.72);}
                .podcast-input{background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.14);border-radius:6px;padding:5px 9px;color:#e2e8f0;font-size:0.76rem;}
                .podcast-pill-btn{background:rgba(255,255,255,0.06);color:#cbd5e1;border:1px solid rgba(255,255,255,0.14);border-radius:6px;padding:4px 10px;font-size:0.76rem;cursor:pointer;transition:all .2s ease;}
                .podcast-pill-btn:hover{color:#fff;background:rgba(255,255,255,0.12);}
                .podcast-pill-btn.active{background:rgba(168,85,247,0.22);color:#f3e8ff;font-weight:600;border-color:rgba(168,85,247,0.65);}
                [data-theme="light"] .podcast-modal-card{background:#ffffff;color:#1e293b;border-color:#e2e8f0;box-shadow:0 20px 50px rgba(15,23,42,0.18);}
                [data-theme="light"] .podcast-modal-header{background:#f8fafc;border-bottom-color:#e2e8f0;}
                [data-theme="light"] .podcast-modal-toolbar{background:#f1f5f9;border-bottom-color:#e2e8f0;}
                [data-theme="light"] .podcast-title{color:#0f172a;} [data-theme="light"] .podcast-sub{color:#64748b;} [data-theme="light"] .podcast-turn-bubble{color:#1e293b;}
                [data-theme="light"] .podcast-player-card,[data-theme="light"] .podcast-inline-cfg{background:#f8fafc;border-color:#cbd5e1 !important;}
                [data-theme="light"] .podcast-input{background:#ffffff;border-color:#cbd5e1;color:#0f172a;}
                [data-theme="light"] .podcast-pill-btn{background:#ffffff;color:#475569;border-color:#cbd5e1;}
                [data-theme="light"] .podcast-pill-btn:hover{color:#0f172a;background:#f8fafc;}
                [data-theme="light"] .podcast-pill-btn.active{background:rgba(147,51,234,0.1);color:#7e22ce;border-color:#9333ea;}
            </style>
            <div class="podcast-modal-card" style="width:100%;max-width:880px;border-radius:16px;display:flex;flex-direction:column;max-height:90vh;overflow:hidden;">
                <div class="podcast-modal-header" style="display:flex;align-items:center;justify-content:space-between;padding:14px 20px;flex-shrink:0;">
                    <div style="display:flex;align-items:center;gap:10px;"><span style="font-size:1.3rem;">🎙️</span><div><div class="podcast-title" style="font-size:1rem;font-weight:600;">双人对话式技术播客工坊 (Podcast Studio)</div><div class="podcast-sub" style="font-size:0.75rem;">智能提炼双人剧本 · 商业级氛围垫乐与自适应闪避 · 128k MP3 单轨缝合与 RSS 分发</div></div></div>
                    <button type="button" class="podcast-sub" onclick="window.closePodcastStudioModal()" style="background:none;border:none;font-size:1.2rem;cursor:pointer;padding:4px 8px;">✕</button>
                </div>
                <div class="podcast-modal-toolbar" style="padding:10px 20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;flex-shrink:0;">
                    <div style="display:flex;align-items:center;gap:6px;"><span class="podcast-sub" style="font-size:0.75rem;">语种:</span><div id="podcast-lang-pills" style="display:flex;gap:4px;align-items:center;"></div></div>
                    <div style="display:flex;align-items:center;gap:6px;"><span class="podcast-sub" style="font-size:0.75rem;">风格:</span><div id="podcast-style-pills" style="display:flex;gap:4px;">${sPills}</div></div>
                    <div style="display:flex;align-items:center;gap:6px;"><span class="podcast-sub" style="font-size:0.75rem;">垫乐:</span><div id="podcast-bgm-pills" style="display:flex;gap:4px;">${bPills}</div></div>
                    <div style="display:flex;align-items:center;gap:6px;"><span class="podcast-sub" style="font-size:0.75rem;">语速:</span><select id="podcast-rate-select" class="podcast-input" style="width:auto;padding:3px 8px;"><option value="-10%">0.9x</option><option value="+0%" selected>1.0x</option><option value="+15%">1.15x</option><option value="+25%">1.25x</option></select><span class="podcast-sub" style="font-size:0.75rem;margin-left:4px;">主播:</span><input id="podcast-host-a" class="podcast-input" type="text" placeholder="主讲名(默认)" style="width:86px;padding:3px 7px;" onchange="window.extractScriptRule()"><input id="podcast-host-b" class="podcast-input" type="text" placeholder="搭档名(默认)" style="width:86px;padding:3px 7px;" onchange="window.extractScriptRule()"></div>
                    <div style="display:flex;align-items:center;gap:8px;width:100%;padding-top:6px;border-top:1px dashed var(--border-subtle,rgba(148,163,184,0.25));flex-wrap:nowrap;">
                        <span class="podcast-sub" style="font-size:0.74rem;white-space:nowrap;flex-shrink:0;">🎯 聚焦引导:</span>
                        <input id="podcast-focus-input" class="podcast-input" type="text" placeholder="可选：如“面向初学者科普”或“重点辩论架构取舍”..." style="flex:1 1 240px;min-width:180px;">
                        <span class="podcast-sub" style="font-size:0.74rem;white-space:nowrap;flex-shrink:0;">🎙️ 引擎:</span>
                        <select id="podcast-tts-provider" class="podcast-input" onchange="if(window.refreshPodcastInlineEngineConfig) window.refreshPodcastInlineEngineConfig(this.value)" style="width:auto;max-width:195px;flex-shrink:0;"><optgroup label="🆓 免费 / 本地开源"><option value="edge">Edge TTS (免费免配)</option><option value="kokoro">Kokoro TTS (开源 82M)</option><option value="chattts">ChatTTS (开源对话)</option><option value="cosyvoice">CosyVoice / 音色克隆</option><option value="piper">Piper TTS (离线极轻)</option></optgroup><optgroup label="✨ 商业级 / 含试用额度"><option value="openai">OpenAI TTS (及兼容)</option><option value="minimax">MiniMax (海螺中文)</option><option value="volcengine">火山引擎 · 豆包语音</option><option value="gemini">Google Gemini TTS</option><option value="elevenlabs">ElevenLabs</option><option value="fish_audio">Fish Audio</option></optgroup></select>
                        <button type="button" class="mini-btn" onclick="if(window.togglePodcastInlineEngineConfig) window.togglePodcastInlineEngineConfig();" title="原地展开当前所选语音引擎的配置面板" style="padding:5px 10px;font-size:0.74rem;white-space:nowrap;flex-shrink:0;">⚙️ 配置引擎</button>
                    </div>
                    <div id="podcast-engine-inline-config" class="podcast-inline-cfg" style="display:none;width:100%;padding:8px 10px;border-radius:8px;border:1px solid rgba(168,85,247,0.35);"></div>
                </div>
                <div id="podcast-modal-body" style="padding:14px 20px;flex:1;min-height:0;display:flex;flex-direction:column;overflow:hidden;"></div>
            </div>
        </div>`;
        document.body.insertAdjacentHTML('beforeend', html);
    }
})();
