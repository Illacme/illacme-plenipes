/**
 * 🛰️ [V103.0] Illacme Plenipes Article Syndication - Live Preview Engine Shard
 * 职责：Discord Embed、Telegram Card、Dev.to 等富文本广播卡片实时预览渲染引擎与 Tab 切换。
 */

(function () {
    window.currentSyndicatePreviewTarget = 'discord';

    window.switchSyndicatePreviewTarget = function (target) {
        window.currentSyndicatePreviewTarget = target;
        const tabBtns = document.querySelectorAll('#syndicate-preview-tabs .preview-tab-btn');
        tabBtns.forEach(btn => {
            if (btn.getAttribute('data-ptarget') === target) {
                btn.classList.add('active');
                btn.style.background = '';
                btn.style.color = '';
                btn.style.borderColor = '';
            } else {
                btn.classList.remove('active');
                btn.style.background = '';
                btn.style.color = '';
                btn.style.borderColor = '';
            }
        });
        window.renderSyndicateCardPreview(target);
    };

    window.renderSyndicateCardPreview = function (target) {
        target = target || window.currentSyndicatePreviewTarget || 'discord';
        const container = document.getElementById('syndicate-card-preview-renderer');
        if (!container) return;

        const langRadio = document.querySelector('input[name="syndicate_lang"]:checked');
        const selectedLang = (langRadio ? langRadio.value : 'zh').toUpperCase();
        const title = window.currentSyndicatingTitle || window.currentSyndicatingRelPath || '未命名文稿';
        const siteUrl = window.settingsData?.compliance?.site_url || 'https://your-domain.com';
        const slug = (window.currentSyndicatingRelPath || 'article').replace(/\.md$/i, '');
        const canonicalUrl = `${siteUrl.replace(/\/$/, '')}/${slug}`;

        if (target === 'discord') {
            container.innerHTML = `
                <div class="syndicate-card-discord" style="border-radius: 6px; padding: 12px 14px; border-left: 4px solid #0284c7; font-family: system-ui, -apple-system, sans-serif; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                        <span class="discord-brand-title" style="font-size: 0.68rem; font-weight: 700; color: #0284c7;">✨ Illacme Sovereign Broadcast</span>
                        <span class="discord-lang-badge" style="font-size: 0.62rem; padding: 1px 5px; border-radius: 3px; background: rgba(2, 132, 199, 0.15); color: #0284c7;">[${selectedLang}]</span>
                    </div>
                    <div class="discord-article-title" style="font-size: 0.88rem; font-weight: 700; color: #0284c7; margin-bottom: 6px; line-height: 1.3;">
                        📝 ${title}
                    </div>
                    <div class="discord-article-desc" style="font-size: 0.76rem; line-height: 1.45; margin-bottom: 8px;">
                        这是文章在 [${selectedLang}] 语种下的自动生成摘要与段落提炼。多语言内容将通过工业级 AST 解析与 Canonical 指向精准对齐。
                    </div>
                    <div class="discord-card-footer" style="display: flex; align-items: center; justify-content: space-between; font-size: 0.68rem; border-top: 1px solid rgba(0,0,0,0.08); padding-top: 6px;">
                        <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 260px;">🔗 ${canonicalUrl}</span>
                        <span>⚡ SSG 全息广播</span>
                    </div>
                </div>
            `;
        } else if (target === 'telegram') {
            container.innerHTML = `
                <div class="syndicate-card-telegram" style="border-radius: 8px; padding: 12px 14px; border: 1px solid rgba(2, 132, 199, 0.25); font-family: system-ui, -apple-system, sans-serif;">
                    <div class="telegram-article-title" style="font-size: 0.84rem; font-weight: 700; margin-bottom: 6px;">
                        📌 <b>${title}</b> <span style="font-size: 0.65rem; color: #0284c7;">[${selectedLang}]</span>
                    </div>
                    <div class="telegram-article-desc" style="font-size: 0.76rem; line-height: 1.45; margin-bottom: 10px;">
                        这是推送到 Telegram 频道的摘要内容。支持 Markdown 格式与超链接跳转。
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <span style="background: rgba(2, 132, 199, 0.12); border: 1px solid rgba(2, 132, 199, 0.35); color: #0284c7; padding: 3px 10px; border-radius: 4px; font-size: 0.72rem; font-weight: 600;">📖 阅读全文 ↗</span>
                    </div>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="syndicate-card-devto" style="border-radius: 8px; padding: 12px 14px; border: 1px solid rgba(0, 0, 0, 0.1); font-family: system-ui, -apple-system, sans-serif;">
                    <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                        <span style="font-size: 0.65rem; background: #0f172a; color: #fff; padding: 1px 6px; border-radius: 3px; font-weight: 700;">DEV.TO</span>
                        <span style="font-size: 0.72rem; color: #64748b; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 260px;">Canonical: <code>${canonicalUrl}</code></span>
                    </div>
                    <div class="devto-article-title" style="font-size: 0.88rem; font-weight: 700; margin-bottom: 6px;">
                        ${title}
                    </div>
                    <div style="font-size: 0.72rem; color: #0284c7; display: flex; gap: 6px;">
                        <span>#markdown</span> <span>#i18n</span> <span>#publishing</span>
                    </div>
                </div>
            `;
        }
    };
})();
