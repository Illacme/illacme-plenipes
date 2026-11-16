# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Generic SSG Adapter Assets JS Shard
模块职责：提供 Universal 主题前端客户端 JavaScript 控制逻辑（主题切换、语种下拉、博客多视图切换与标签过滤）。
"""


def get_universal_client_js() -> str:
    """获取 Universal 主题前端客户端 JavaScript 控制逻辑"""
    return """
        function toggleUniversalTheme() {
            var current = document.documentElement.getAttribute('data-theme') || 'dark';
            var next = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('universal-theme', next);
        }

        // 🌐 多语言下拉交互支持 (支持点击展开/常驻与外部点击收起)
        document.addEventListener('DOMContentLoaded', function() {
            var dropdown = document.getElementById('lang-dropdown');
            if (dropdown) {
                var btn = dropdown.querySelector('.lang-dropdown-btn');
                var menu = dropdown.querySelector('.lang-dropdown-menu');
                if (btn && menu) {
                    btn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        dropdown.classList.toggle('active');
                        var isShown = menu.style.display === 'flex';
                        menu.style.display = isShown ? 'none' : 'flex';
                    });
                    document.addEventListener('click', function(e) {
                        if (!dropdown.contains(e.target)) {
                            dropdown.classList.remove('active');
                            menu.style.display = '';
                        }
                    });
                }
            }
        });

        // 博客交互：视图切换与标签过滤
        document.addEventListener('DOMContentLoaded', function() {
            var blogApp = document.getElementById('blog-app');
            if (!blogApp) return;

            var switchBtns = blogApp.querySelectorAll('.view-switch-btn');
            var views = {
                timeline: document.getElementById('view-timeline'),
                grid: document.getElementById('view-grid'),
                compact: document.getElementById('view-compact')
            };

            switchBtns.forEach(function(btn) {
                btn.addEventListener('click', function() {
                    var targetView = btn.dataset.view;
                    switchBtns.forEach(function(b) { b.classList.remove('active'); });
                    btn.classList.add('active');
                    Object.keys(views).forEach(function(k) {
                        if (views[k]) views[k].classList.remove('active');
                    });
                    if (views[targetView]) views[targetView].classList.add('active');
                });
            });

            var tagBtns = blogApp.querySelectorAll('.blog-tag-filter');
            tagBtns.forEach(function(tBtn) {
                tBtn.addEventListener('click', function() {
                    var tag = tBtn.dataset.tag;
                    tagBtns.forEach(function(tb) { tb.classList.remove('active'); });
                    tBtn.classList.add('active');

                    var items = blogApp.querySelectorAll('.timeline-item, .blog-card, .compact-row');
                    items.forEach(function(it) {
                        var tags = (it.dataset.tags || '').split(',');
                        if (tag === 'all' || tags.indexOf(tag) !== -1) {
                            it.style.display = '';
                        } else {
                            it.style.display = 'none';
                        }
                    });
                });
            });
        });

        // 🎧 伴读播客播放器交互控制
        document.addEventListener('DOMContentLoaded', function() {
            var players = document.querySelectorAll('.universal-audio-player, .sovereign-audio-player');
            var fmtTime = function(sec) {
                if (!sec || isNaN(sec)) return '0:00';
                var m = Math.floor(sec / 60), s = Math.floor(sec % 60);
                return m + ':' + (s < 10 ? '0' : '') + s;
            };
            players.forEach(function(wrap) {
                var audio = wrap.querySelector('.audio-native');
                var playBtn = wrap.querySelector('.audio-play-btn');
                var scrub = wrap.querySelector('.audio-scrub');
                var curTime = wrap.querySelector('.audio-cur-time');
                var totTime = wrap.querySelector('.audio-total-time');
                var speedBtn = wrap.querySelector('.audio-speed-btn');
                var muteBtn = wrap.querySelector('.audio-mute-btn');
                var pills = wrap.querySelectorAll('.chapter-pill');
                if (!audio || !playBtn) return;
                playBtn.addEventListener('click', function() {
                    if (audio.paused) { audio.play(); playBtn.textContent = '⏸'; }
                    else { audio.pause(); playBtn.textContent = '▶'; }
                });
                audio.addEventListener('loadedmetadata', function() {
                    if (totTime) totTime.textContent = fmtTime(audio.duration);
                });
                audio.addEventListener('timeupdate', function() {
                    if (curTime) curTime.textContent = fmtTime(audio.currentTime);
                    if (scrub && audio.duration) scrub.value = ((audio.currentTime / audio.duration) * 100).toFixed(1);
                });
                audio.addEventListener('ended', function() { playBtn.textContent = '▶'; });
                if (scrub) {
                    scrub.addEventListener('input', function() {
                        if (audio.duration) audio.currentTime = ( parseFloat(scrub.value) / 100 ) * audio.duration;
                    });
                }
                if (speedBtn) {
                    var speeds = [1.0, 1.25, 1.5, 2.0], idx = 0;
                    speedBtn.addEventListener('click', function() {
                        idx = (idx + 1) % speeds.length;
                        audio.playbackRate = speeds[idx];
                        speedBtn.textContent = speeds[idx] + 'x';
                    });
                }
                if (muteBtn) {
                    muteBtn.addEventListener('click', function() {
                        audio.muted = !audio.muted;
                        muteBtn.textContent = audio.muted ? '🔇' : '🔊';
                    });
                }
                pills.forEach(function(pill) {
                    pill.addEventListener('click', function() {
                        var t = parseFloat(pill.getAttribute('data-time') || '0');
                        audio.currentTime = t;
                        audio.play();
                        playBtn.textContent = '⏸';
                    });
                });
            });
        });
    """
