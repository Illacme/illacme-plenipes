/**
 * 🛰️ [V105.0] Illacme Plenipes Syndication - Reader Audio Companion Shard
 * 职责：为文章高保真排版审查视窗与读者消费闭环注入 Cyber-Glass 嵌入式伴读播放条。
 * 🛡️ [SOP-01 规范]：单文件严格 ≤ 300 行。
 */

(function () {
    const _esc = (s) => (s === null || s === undefined ? '' : String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'));

    function formatTime(seconds) {
        if (!seconds || isNaN(seconds) || seconds < 0) return '0:00';
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        return `${m}:${s < 10 ? '0' : ''}${s}`;
    }

    const SPEEDS = [1.0, 1.25, 1.5, 2.0, 0.75];

    window.renderSyndicateAudioBar = function (audioData, container) {
        if (!container) return;
        if (!audioData || !audioData.has_audio || !audioData.audio_url) {
            container.innerHTML = '';
            container.style.display = 'none';
            return;
        }

        container.style.display = 'block';
        const audioUrl = audioData.audio_url;
        const styleName = audioData.style_name || '技术播客';
        const rssUrl = audioData.rss_url || '/api/podcast/feed/default';

        container.innerHTML = `
            <div class="syndicate-audio-card glass-panel" id="syndicate-audio-player-card">
                <div class="syndicate-audio-top-row">
                    <div class="syndicate-audio-badge">
                        <span class="audio-pulse-dot"></span>
                        <span class="audio-badge-icon">🎧</span>
                        <span class="audio-badge-text">AI 伴读播客 · <b>${_esc(styleName)}</b></span>
                    </div>
                    <div class="syndicate-audio-meta-links">
                        <a href="${_esc(rssUrl)}" target="_blank" rel="noopener noreferrer" class="audio-rss-chip" title="订阅通用 RSS 播客源">
                            <span>📻</span> 播客订阅
                        </a>
                        <a href="${_esc(audioUrl)}" download class="audio-rss-chip audio-download-chip" title="下载原版 128kbps MP3">
                            <span>⬇️</span> 下载 MP3
                        </a>
                    </div>
                </div>
                <div class="syndicate-audio-controls-row">
                    <button type="button" class="audio-play-toggle-btn" id="syn-audio-play-btn" title="播放 / 暂停">
                        <span class="play-icon">▶</span>
                    </button>
                    <span class="audio-time-label" id="syn-audio-cur-time">0:00</span>
                    <div class="audio-slider-container">
                        <input type="range" class="audio-timeline-slider" id="syn-audio-slider" min="0" max="100" value="0" step="0.1">
                        <div class="audio-progress-fill" id="syn-audio-progress-fill"></div>
                    </div>
                    <span class="audio-time-label audio-time-dim" id="syn-audio-total-time">--:--</span>
                    <button type="button" class="audio-pill-action-btn" id="syn-audio-speed-btn" title="切换播放倍速">1.0x</button>
                    <button type="button" class="audio-pill-action-btn" id="syn-audio-vol-btn" title="静音切换">🔊</button>
                </div>
                <audio id="syn-audio-element" src="${_esc(audioUrl)}" preload="metadata"></audio>
            </div>
        `;

        const audioEl = container.querySelector('#syn-audio-element');
        const playBtn = container.querySelector('#syn-audio-play-btn');
        const slider = container.querySelector('#syn-audio-slider');
        const progressFill = container.querySelector('#syn-audio-progress-fill');
        const curTimeEl = container.querySelector('#syn-audio-cur-time');
        const totalTimeEl = container.querySelector('#syn-audio-total-time');
        const speedBtn = container.querySelector('#syn-audio-speed-btn');
        const volBtn = container.querySelector('#syn-audio-vol-btn');
        const playerCard = container.querySelector('#syndicate-audio-player-card');

        if (!audioEl || !playBtn) return;

        let curSpeedIdx = 0;

        playBtn.addEventListener('click', () => {
            if (audioEl.paused) {
                audioEl.play().catch(e => console.warn('音频播放受阻:', e));
            } else {
                audioEl.pause();
            }
        });

        audioEl.addEventListener('play', () => {
            playBtn.innerHTML = '<span class="play-icon">⏸</span>';
            playBtn.classList.add('is-playing');
            if (playerCard) playerCard.classList.add('is-playing');
        });

        audioEl.addEventListener('pause', () => {
            playBtn.innerHTML = '<span class="play-icon">▶</span>';
            playBtn.classList.remove('is-playing');
            if (playerCard) playerCard.classList.remove('is-playing');
        });

        audioEl.addEventListener('loadedmetadata', () => {
            if (audioEl.duration && !isNaN(audioEl.duration)) {
                totalTimeEl.textContent = formatTime(audioEl.duration);
            }
        });

        audioEl.addEventListener('timeupdate', () => {
            const cur = audioEl.currentTime;
            const dur = audioEl.duration;
            curTimeEl.textContent = formatTime(cur);
            if (dur && !isNaN(dur) && dur > 0) {
                const pct = (cur / dur) * 100;
                slider.value = pct;
                if (progressFill) progressFill.style.width = `${pct}%`;
                totalTimeEl.textContent = formatTime(dur);
            }
        });

        audioEl.addEventListener('ended', () => {
            playBtn.innerHTML = '<span class="play-icon">▶</span>';
            playBtn.classList.remove('is-playing');
            if (playerCard) playerCard.classList.remove('is-playing');
            slider.value = 0;
            if (progressFill) progressFill.style.width = '0%';
            curTimeEl.textContent = '0:00';
        });

        slider.addEventListener('input', () => {
            const dur = audioEl.duration;
            if (dur && !isNaN(dur) && dur > 0) {
                const targetSec = (slider.value / 100) * dur;
                audioEl.currentTime = targetSec;
                if (progressFill) progressFill.style.width = `${slider.value}%`;
            }
        });

        speedBtn.addEventListener('click', () => {
            curSpeedIdx = (curSpeedIdx + 1) % SPEEDS.length;
            const spd = SPEEDS[curSpeedIdx];
            audioEl.playbackRate = spd;
            speedBtn.textContent = `${spd}x`;
        });

        volBtn.addEventListener('click', () => {
            audioEl.muted = !audioEl.muted;
            volBtn.textContent = audioEl.muted ? '🔇' : '🔊';
        });
    };
})();

