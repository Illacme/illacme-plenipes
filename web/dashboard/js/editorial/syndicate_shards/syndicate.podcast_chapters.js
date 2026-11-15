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

})(window);

