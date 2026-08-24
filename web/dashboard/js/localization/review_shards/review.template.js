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
    <div id="review-drawer-overlay" style="display:none; opacity:0; position:fixed; inset:0; z-index:9000;
                background:rgba(0,0,0,0.55); backdrop-filter:blur(4px);
                justify-content:flex-end; align-items:stretch;
                transition:opacity 0.25s cubic-bezier(0.4,0,0.2,1);"
        onclick="if(event.target===this) window.closeTranslationReview()">
        <div id="review-drawer"
            style="width:min(1400px,85vw); height:100%; background:rgb(var(--bg-modal-solid-rgb));
                    border-left:1px solid var(--glass-border); display:flex; flex-direction:column;
                    box-shadow:-8px 0 40px rgba(0,0,0,0.6); overflow:hidden; transition: width 0.3s cubic-bezier(0.4,0,0.2,1);">

            <!-- Header -->
            <div style="display:flex; align-items:center; justify-content:space-between;
                         padding:16px 20px 12px; border-bottom:1px solid var(--glass-border);
                         background:rgba(var(--bg-modal-solid-rgb),0.85); flex-shrink:0;">
                <span id="review-drawer-title" style="font-weight:700; font-size:0.95rem;
                       color:var(--text-bright); letter-spacing:0.3px;">🔍 译文校对工作台</span>

                <div style="display:flex; align-items:center; gap:12px;">
                    <!-- 视图切换器 -->
                    <div class="review-view-toggle"
                        style="display:flex; background:var(--white-05); border-radius:6px; padding:2px; border:1px solid var(--white-08); gap:4px;">
                        <button id="btn-view-preview" onclick="window.toggleReviewPreview()"
                            style="background:var(--white-10); color:var(--text-bright); border:none; padding:4px 10px; border-radius:4px; font-size:0.8rem; cursor:pointer; font-weight:600; box-shadow:0 1px 3px rgba(0,0,0,0.15); transition:all 0.2s;"
                            data-tooltip="显示/隐藏预览分栏" data-tooltip-pos="bottom">👁️ 预览</button>
                        <button id="btn-view-source" onclick="window.toggleReviewSource()"
                            style="background:var(--white-10); color:var(--text-bright); border:none; padding:4px 10px; border-radius:4px; font-size:0.8rem; cursor:pointer; font-weight:600; box-shadow:0 1px 3px rgba(0,0,0,0.15); transition:all 0.2s;"
                            data-tooltip="显示/隐藏原文分栏" data-tooltip-pos="bottom">📜 原文</button>
                    </div>

                    <!-- 右上角操作按钮：支持从社交广播工作流深度串联跳转时自动变身为「‹ 返回广播中枢」 -->
                    <button id="btn-close-review-drawer" onclick="window.handleReviewDrawerCloseClick()" style="background:none; border:none; color:var(--text-dim); font-size:1.3rem;
                               cursor:pointer; line-height:1; padding:2px 6px; border-radius:4px;
                               display:inline-flex; align-items:center; gap:4px; transition:color 0.2s;"
                        data-tooltip="关闭或返回上级" data-tooltip-pos="bottom">✕</button>
                </div>
            </div>

            <!-- Lang Tabs -->
            <div id="review-lang-tabs" style="display:flex; gap:8px; padding:12px 20px; flex-shrink:0;
                         border-bottom:1px solid var(--glass-border); flex-wrap:wrap;"></div>

            <!-- ⚠️ 出版模式警告 Banner -->
            <div id="review-mode-alert" style="display:none; flex-shrink:0;"></div>

            <!-- Body (scrollable) -->
            <div id="review-body" style="flex:1; overflow-y:auto; padding:20px;
                         display:flex; flex-direction:column; gap:16px;"></div>
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
