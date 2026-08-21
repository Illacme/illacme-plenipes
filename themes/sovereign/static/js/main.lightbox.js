/**
 * Illacme-plenipes Sovereign Theme - Image Lightbox Engine
 * 职责：为文章插图与架构图提供纯原生、零依赖的高清全屏毛玻璃灯箱浏览与平滑缩放。
 * 🛡️ [AEL-Iter-v12.0]：完全遵循零依赖与无障碍交互标准，杜绝三方依赖。
 */

(function (window) {
    'use strict';

    /**
     * 初始化图片灯箱
     */
    function initLightbox() {
        const prose = document.querySelector('.prose-sovereign');
        if (!prose) return;

        // 仅抓取正文区域的内容图片，排除头像、图标与 Badge
        const images = prose.querySelectorAll('img:not(.logo-img):not(.avatar):not(.icon)');
        if (images.length === 0) return;

        // 1. 创建全局唯一的灯箱 DOM 结构
        let lightboxOverlay = document.getElementById('sovereign-lightbox');
        if (!lightboxOverlay) {
            lightboxOverlay = document.createElement('div');
            lightboxOverlay.id = 'sovereign-lightbox';
            lightboxOverlay.className = 'sovereign-lightbox-overlay';
            lightboxOverlay.innerHTML = `
                <div class="lightbox-backdrop"></div>
                <div class="lightbox-stage">
                    <img class="lightbox-image" src="" alt="Enlarged view">
                    <button class="lightbox-close" type="button" aria-label="关闭灯箱" title="关闭 (Esc)">✕</button>
                    <div class="lightbox-caption"></div>
                </div>
            `;
            document.body.appendChild(lightboxOverlay);

            const closeBtn = lightboxOverlay.querySelector('.lightbox-close');
            const backdrop = lightboxOverlay.querySelector('.lightbox-backdrop');

            const closeLightbox = () => {
                lightboxOverlay.classList.remove('active');
                document.body.classList.remove('lightbox-open');
            };

            closeBtn.addEventListener('click', closeLightbox);
            backdrop.addEventListener('click', closeLightbox);

            // 键盘 Esc 键退出
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && lightboxOverlay.classList.contains('active')) {
                    closeLightbox();
                }
            });
        }

        const targetImg = lightboxOverlay.querySelector('.lightbox-image');
        const captionEl = lightboxOverlay.querySelector('.lightbox-caption');

        // 2. 为每张合规图片绑定点击展开事件
        images.forEach((img) => {
            if (img.dataset.lightboxInit) return;
            img.dataset.lightboxInit = 'true';
            img.classList.add('lightbox-zoomable');

            img.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                targetImg.src = img.currentSrc || img.src;
                targetImg.alt = img.alt || '';
                
                const captionText = img.getAttribute('title') || img.getAttribute('alt') || '';
                if (captionText) {
                    captionEl.textContent = captionText;
                    captionEl.style.display = 'block';
                } else {
                    captionEl.textContent = '';
                    captionEl.style.display = 'none';
                }

                lightboxOverlay.classList.add('active');
                document.body.classList.add('lightbox-open');
            });
        });
    }

    // 挂载至全局 window 状态总线
    window.initLightbox = initLightbox;

})(window);
