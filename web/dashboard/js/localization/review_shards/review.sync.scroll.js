/**
 * 🔒 [I5] Illacme Plenipes Translation Review - Scroll & Hover Synchronizer Shard
 * 职责：三向段落鼠标悬停联动高亮、3 轴段落锚定与物理边界吸附滚动同步。
 */

(function () {
    /* ─── 集中绑定三栏交互：三向联动高亮与锚定滚动同步 ───────────────── */
    window._bindReviewInteractions = function () {
        const colTarget = document.getElementById('col-target');
        const colPreview = document.getElementById('col-preview');
        const colSource = document.getElementById('col-source');
        if (!colTarget || !colPreview || !colSource) return;

        // 1. 三向段落高亮联动
        const highlightPara = (idx, add) => {
            ['review-para', 'source-para', 'preview-para'].forEach(prefix => {
                const el = document.getElementById(`${prefix}-${idx}`);
                if (el) {
                    if (add) el.classList.add('linked-hover');
                    else el.classList.remove('linked-hover');
                }
            });
        };

        [colTarget, colPreview, colSource].forEach(col => {
            col.addEventListener('mouseover', (e) => {
                const block = e.target.closest('[id^="review-para-"], [id^="source-para-"], [id^="preview-para-"]');
                if (block) highlightPara(block.id.split('-').pop(), true);
            });
            col.addEventListener('mouseout', (e) => {
                const block = e.target.closest('[id^="review-para-"], [id^="source-para-"], [id^="preview-para-"]');
                if (block) highlightPara(block.id.split('-').pop(), false);
            });
        });

        // 2. 基于物理边界吸附与段落锚定的 3 轴同步联动滚动
        let activeScrollSource = null;
        let scrollTimeout = null;

        const onScrollHandler = (e) => {
            const target = e.currentTarget;
            if (activeScrollSource && activeScrollSource !== target) return;
            activeScrollSource = target;

            const maxScroll = target.scrollHeight - target.clientHeight;
            if (maxScroll <= 0) return;

            const isAtBottom = (maxScroll - target.scrollTop) < 15;
            const isAtTop = target.scrollTop < 15;
            const scrollRatio = target.scrollTop / maxScroll;

            const visibleCols = [colTarget, colPreview, colSource].filter(c => c && c.style.display !== 'none');

            if (isAtBottom) {
                // 🛡️ [边界吸附红线] 一栏到达最底部，强制所有分栏精准到达各自 100% 底部
                visibleCols.forEach(c => {
                    if (c !== target) {
                        c.scrollTop = c.scrollHeight - c.clientHeight;
                    }
                });
            } else if (isAtTop) {
                // 🛡️ [边界吸附红线] 一栏到达最顶部，强制所有分栏精准复位至 0
                visibleCols.forEach(c => {
                    if (c !== target) {
                        c.scrollTop = 0;
                    }
                });
            } else {
                // 🛡️ [中间区段段落锚定 + 比例补偿]
                const targetRect = target.getBoundingClientRect();
                const blocks = Array.from(target.querySelectorAll('[id^="review-para-"], [id^="source-para-"], [id^="preview-para-"]'));
                let activeIdx = null, diff = 0;

                for (const b of blocks) {
                    const rect = b.getBoundingClientRect();
                    if (rect.bottom - targetRect.top > 10) {
                        activeIdx = b.id.split('-').pop();
                        diff = rect.top - targetRect.top;
                        break;
                    }
                }

                const prefixes = { 'col-target': 'review-para', 'col-preview': 'preview-para', 'col-source': 'source-para' };
                visibleCols.forEach(c => {
                    if (c !== target) {
                        if (activeIdx !== null) {
                            const targetEl = c.querySelector(`#${prefixes[c.id]}-${activeIdx}`);
                            if (targetEl) {
                                const colRect = c.getBoundingClientRect();
                                const elRect = targetEl.getBoundingClientRect();
                                c.scrollTop += (elRect.top - colRect.top) - diff;
                            } else {
                                const cMax = c.scrollHeight - c.clientHeight;
                                c.scrollTop = Math.round(scrollRatio * cMax);
                            }
                        } else {
                            const cMax = c.scrollHeight - c.clientHeight;
                            c.scrollTop = Math.round(scrollRatio * cMax);
                        }
                    }
                });
            }

            if (scrollTimeout) clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => { activeScrollSource = null; }, 80);
        };

        colTarget.addEventListener('scroll', onScrollHandler);
        colPreview.addEventListener('scroll', onScrollHandler);
        colSource.addEventListener('scroll', onScrollHandler);
    };
})();
