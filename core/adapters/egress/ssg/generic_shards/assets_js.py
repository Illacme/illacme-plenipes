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
                        var isShown = menu.style.display === 'block';
                        menu.style.display = isShown ? '' : 'block';
                    });
                    document.addEventListener('click', function(e) {
                        if (!dropdown.contains(e.target)) {
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
    """
