/**
 * 🚀 Illacme Plenipes Localization Review - Template Shard
 * 职责：翻译校对工作台全屏抽屉 DOM 骨架动态挂载与模板组装。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
 */

window.ensureReviewDrawerMounted = function () {
    if (document.getElementById('review-drawer-overlay')) {
        return;
    }

    const drawerHtml = `
    <div id="review-drawer-overlay" class="review-drawer-overlay"
        onclick="if(event.target===this) window.closeTranslationReview()">
        <div id="review-drawer" class="review-drawer-window">

            <!-- Header -->
            <div class="review-drawer-header">
                <span id="review-drawer-title" class="review-drawer-title">🔍 译文校对工作台</span>

                <div style="display:flex; align-items:center; gap:12px;">
                    <!-- 视图切换器 -->
                    <div class="review-view-toggle">
                        <button id="btn-view-preview" class="review-toggle-btn active" onclick="window.toggleReviewPreview()"
                            data-tooltip="显示/隐藏预览分栏" data-tooltip-pos="bottom">👁️ 预览</button>
                        <button id="btn-view-source" class="review-toggle-btn" onclick="window.toggleReviewSource()"
                            data-tooltip="显示/隐藏原文分栏" data-tooltip-pos="bottom">📜 原文</button>
                    </div>

                    <!-- 右上角操作按钮：支持从社交广播工作流深度串联跳转时自动变身为「‹ 返回广播中枢」 -->
                    <button id="btn-close-review-drawer" class="review-close-btn" onclick="window.handleReviewDrawerCloseClick()"
                        data-tooltip="关闭或返回上级" data-tooltip-pos="bottom">✕</button>
                </div>
            </div>

            <!-- Lang Tabs -->
            <div id="review-lang-tabs" class="review-lang-tabs-bar"></div>

            <!-- ⚠️ 出版模式警告 Banner -->
            <div id="review-mode-alert" style="display:none; flex-shrink:0;"></div>

            <!-- Body (scrollable) -->
            <div id="review-body" class="review-body-scroll"></div>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', drawerHtml);
};

// 立即在脚本加载后自动挂载底板
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.ensureReviewDrawerMounted);
} else {
    window.ensureReviewDrawerMounted();
}
