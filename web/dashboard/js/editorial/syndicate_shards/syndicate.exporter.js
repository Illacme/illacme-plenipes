/**
 * 🛰️ [V105.4] Illacme Plenipes Syndication Multi-Format Exporter
 * 职责：前置排版工坊多平台格式一键导出中枢（微信富文本 / 图床直链 Markdown / Frontmatter / 标题导语）
 * 🛡️ [SOP-01 规范]：严格收敛于 300 行以内。
 */

(function () {
    const _notify = (msg, type = 'info') => {
        if (typeof window.showToast === 'function') window.showToast(msg, type);
        else alert(msg);
    };

    /**
     * 通用文本剪贴板安全写入（现代 API + 降级兼容）
     */
    async function writeClipboardText(text, successMsg) {
        if (!text) { _notify('⚠️ 当前格式暂无可用文本', 'warning'); return false; }
        try {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(text);
            } else {
                const ta = document.createElement('textarea');
                ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
                document.body.appendChild(ta); ta.select(); document.execCommand('copy');
                document.body.removeChild(ta);
            }
            if (successMsg) _notify(successMsg, 'success');
            return true;
        } catch (err) {
            console.error('Clipboard write error:', err);
            _notify('🛑 剪贴板写入失败，请检查浏览器权限', 'error');
            return false;
        }
    }

    /** 1. 复制微信公众号富文本 (HTML + 纯文本双通道) */
    window.copyWeChatRichText = async function () {
        const html = window._currentRenderedHtml;
        if (!html) { _notify('⚠️ 暂未生成微信排版 HTML', 'warning'); return; }
        try {
            if (navigator.clipboard && window.ClipboardItem) {
                const plainText = document.getElementById('preview-rendered-body-slot')?.innerText || html;
                await navigator.clipboard.write([
                    new ClipboardItem({ 'text/html': new Blob([html], { type: 'text/html' }), 'text/plain': new Blob([plainText], { type: 'text/plain' }) })
                ]);
            } else { await writeClipboardText(html, null); }
            _notify('📋 公众号富文本已复制！可直接在微信公众号后台粘贴 (Cmd+V)', 'success');
        } catch (err) {
            console.error('Copy WeChat rich text error:', err);
            _notify('🛑 复制富文本失败，请手动选取正文复制', 'error');
        }
    };

    /** 2. 复制当前渠道专属适配 Markdown */
    window.copyPlatformMarkdown = async function () {
        const md = window._currentRenderedMarkdown || '';
        await writeClipboardText(md, '📑 当前渠道适配 Markdown 已复制！');
    };

    /** 3. 复制通用 Markdown（图床直链 / 纯净正文） */
    window.copyCleanMarkdownWithCdn = async function () {
        const md = window._currentCdnMarkdown || window._currentCleanMarkdown || window._currentRenderedMarkdown || '';
        await writeClipboardText(md, '🌐 图床直链 Markdown 已复制！可直接粘贴至知乎/掘金/CSDN');
    };

    /** 4. 复制标准 Frontmatter Markdown (适用 Dev.to/Hashnode/Hexo) */
    window.copyFrontmatterMarkdown = async function () {
        const md = window._currentFrontmatterMarkdown || window._currentRenderedMarkdown || '';
        await writeClipboardText(md, '🏷️ 带 Frontmatter 格式已复制！适配 Dev.to/Hashnode/Hexo');
    };

    /** 5. 复制标题与导语摘要 */
    window.copyTitleAndDigest = async function () {
        const title = window._currentPreviewTitle || '';
        const digest = window._currentPreviewDigest || '';
        await writeClipboardText(`【标题】：${title}\n【导语】：${digest}`, '📝 标题与导语已复制！方便表单填报');
    };

    /** 6. 复制知乎专栏高保真富文本 */
    window.copyZhihuRichText = async function () {
        const html = window._currentRenderedHtml;
        if (!html) { _notify('⚠️ 暂未生成知乎排版 HTML', 'warning'); return; }
        try {
            if (navigator.clipboard && window.ClipboardItem) {
                const plainText = document.getElementById('preview-rendered-body-slot')?.innerText || html;
                await navigator.clipboard.write([
                    new ClipboardItem({ 'text/html': new Blob([html], { type: 'text/html' }), 'text/plain': new Blob([plainText], { type: 'text/plain' }) })
                ]);
            } else { await writeClipboardText(html, null); }
            _notify('📋 知乎富文本已复制！可直接在知乎专栏编辑器中粘贴 (Cmd+V)', 'success');
        } catch (err) {
            console.error('Copy Zhihu rich text error:', err);
            _notify('🛑 复制富文本失败，已降级复制 Markdown', 'warning');
            await window.copyPlatformMarkdown();
        }
    };

    /** 7. 复制掘金排版 (含导读与版权声明) */
    window.copyJuejinMarkdown = async function () {
        const md = window._currentRenderedMarkdown || window._currentCdnMarkdown || '';
        await writeClipboardText(md, '📋 掘金 Markdown 已复制！已包含导读卡片与版权保护声明');
    };

    /** 8. 复制小红书精炼图文笔记 */
    window.copyXiaohongshuNote = async function () {
        const title = window._currentPreviewTitle || '';
        const md = window._currentRenderedMarkdown || '';
        await writeClipboardText(`【标题】：${title}\n\n${md}`, '📋 小红书图文笔记已复制！已精炼 20 字标题与热门话题标签');
    };

    /** 切换设备仿真机型 */
    window.setSyndicatePreviewDevice = function (dev) {
        window._previewDevice = dev;
        if (typeof window.renderSyndicateCardPreview === 'function') window.renderSyndicateCardPreview();
    };

    /** 微调排版字号 */
    window.setSyndicateFontSize = function (size) {
        window._syndicateFontSize = size;
        const pxMap = { 'small': '14px', 'medium': '16px', 'large': '18px' };
        const px = pxMap[size] || '16px';
        window._syndicateFontSizePx = px;
        const bodySlot = document.getElementById('preview-rendered-body-slot');
        if (bodySlot) {
            bodySlot.style.setProperty('--preview-body-font-size', px);
            bodySlot.style.fontSize = px;
        }
        const container = document.getElementById('syndicate-modal-actions-slot');
        if (container && typeof window.renderSyndicateActionsToolbar === 'function') {
            const curTheme = window._currentSyndicateTheme || 'default';
            const target = window.currentSyndicatePreviewTarget || 'wechat';
            const dev = window._previewDevice || 'iphone';
            container.innerHTML = window.renderSyndicateActionsToolbar(target, curTheme, dev, size);
        }
    };

    /** 切换多格式导出菜单显示/隐藏 */
    window.toggleSyndicateExportMenu = function () {
        const menu = document.getElementById('syndicate-export-dropdown-menu');
        if (!menu) return;
        menu.classList.toggle('is-active');
    };

    /**
     * 统一构造排版审查视窗右侧操作区工具栏
     */
    window.renderSyndicateActionsToolbar = function (target, curTheme, activeDevice, activeFontSize) {
        const isWechat = (target === 'wechat');
        const isZhihu = (target === 'zhihu');
        const isXhs = (target === 'xiaohongshu' || target === 'red' || target === 'rednote');
        const isJuejin = (target === 'juejin');

        const dev = activeDevice || window._previewDevice || (isWechat || isXhs ? 'iphone' : 'desktop');
        const fontSz = activeFontSize || window._syndicateFontSize || 'medium';

        let primaryBtnHtml = '';
        if (isWechat) {
            primaryBtnHtml = `<button type="button" class="syndicate-copy-btn glow-btn syndicate-btn--wechat" onclick="window.copyWeChatRichText()" title="一键复制微信公众号富文本 (Cmd+V 直粘)"><span>📋 复制公众号富文本</span></button>`;
        } else if (isZhihu) {
            primaryBtnHtml = `<button type="button" class="syndicate-copy-btn glow-btn syndicate-btn--zhihu" onclick="window.copyZhihuRichText()" title="一键复制知乎高保真富文本 (Cmd+V 直粘知乎专栏)"><span>📋 复制知乎富文本</span></button>`;
        } else if (isXhs) {
            primaryBtnHtml = `<button type="button" class="syndicate-copy-btn glow-btn syndicate-btn--xhs" onclick="window.copyXiaohongshuNote()" title="一键复制小红书精炼标题与话题笔记"><span>📋 复制小红书笔记</span></button>`;
        } else if (isJuejin) {
            primaryBtnHtml = `<button type="button" class="syndicate-copy-btn glow-btn syndicate-btn--juejin" onclick="window.copyJuejinMarkdown()" title="一键复制掘金排版 Markdown"><span>📋 复制掘金排版</span></button>`;
        } else {
            primaryBtnHtml = `<button type="button" class="syndicate-copy-btn glow-btn" onclick="window.copyCleanMarkdownWithCdn()" title="一键复制当前渠道排版 Markdown"><span>📋 复制适配排版</span></button>`;
        }

        return `
            <div class="syndicate-viewport-switcher" title="切换排版仿真机型">
                <button type="button" class="syndicate-viewport-btn ${dev === 'iphone' ? 'is-active' : ''}" onclick="window.setSyndicatePreviewDevice('iphone')">📱 iPhone</button>
                <button type="button" class="syndicate-viewport-btn ${dev === 'android' ? 'is-active' : ''}" onclick="window.setSyndicatePreviewDevice('android')">🤖 Android</button>
                <button type="button" class="syndicate-viewport-btn ${dev === 'pad' ? 'is-active' : ''}" onclick="window.setSyndicatePreviewDevice('pad')">📟 平板</button>
                <button type="button" class="syndicate-viewport-btn ${dev === 'desktop' ? 'is-active' : ''}" onclick="window.setSyndicatePreviewDevice('desktop')">💻 宽屏</button>
            </div>
            <div class="syndicate-font-switcher" title="微调预览字号">
                <button type="button" class="syndicate-font-btn ${fontSz === 'small' ? 'is-active' : ''}" onclick="window.setSyndicateFontSize('small')" title="紧凑小字号 (14px)">A-</button>
                <button type="button" class="syndicate-font-btn ${fontSz === 'medium' ? 'is-active' : ''}" onclick="window.setSyndicateFontSize('medium')" title="标准阅读字号 (16px)">A</button>
                <button type="button" class="syndicate-font-btn ${fontSz === 'large' ? 'is-active' : ''}" onclick="window.setSyndicateFontSize('large')" title="醒目大字号 (18px)">A+</button>
            </div>
            ${isWechat ? `
            <select class="syndicate-viewport-btn" style="width: auto !important; max-width: 105px !important; flex: 0 0 auto !important; padding: 4px 8px; font-size: 0.78rem; outline: none; border-radius: 6px; white-space: nowrap; flex-shrink: 0;" onchange="window.switchSyndicateTheme(this.value)" title="选择微信公众号专属配色矩阵">
                <option value="default" ${curTheme === 'default' ? 'selected' : ''}>🎨 科技蓝</option>
                <option value="emerald" ${curTheme === 'emerald' ? 'selected' : ''}>🌿 翡翠绿</option>
                <option value="amber" ${curTheme === 'amber' ? 'selected' : ''}>🍂 暖秋金</option>
                <option value="minimal" ${curTheme === 'minimal' ? 'selected' : ''}>🌙 极简灰</option>
            </select>
            ` : ''}
            ${primaryBtnHtml}
            <div class="syndicate-export-menu-wrapper" style="position: relative; display: inline-flex; align-items: center; white-space: nowrap; flex-shrink: 0;">
                <button type="button" class="syndicate-copy-markdown-btn" onclick="window.toggleSyndicateExportMenu()" style="display: inline-flex; align-items: center; gap: 5px; white-space: nowrap; flex-shrink: 0;" title="选择不同平台的发布格式导出">
                    <span>📦 更多格式 ▾</span>
                </button>
                <div id="syndicate-export-dropdown-menu" class="syndicate-export-dropdown glass-panel">
                    <div class="export-dropdown-item" onclick="window.copyCleanMarkdownWithCdn();window.toggleSyndicateExportMenu();">
                        <span class="item-icon">🌐</span>
                        <div class="item-meta">
                            <span class="item-title">通用 Markdown（图床直链）</span>
                            <span class="item-desc">相对路径自动补全 CDN，知乎/掘金/CSDN 零报错</span>
                        </div>
                    </div>
                    <div class="export-dropdown-item" onclick="window.copyFrontmatterMarkdown();window.toggleSyndicateExportMenu();">
                        <span class="item-icon">🏷️</span>
                        <div class="item-meta">
                            <span class="item-title">带 Frontmatter 格式</span>
                            <span class="item-desc">含 YAML 元数据与 Canonical URL，适配 Dev.to/Hashnode</span>
                        </div>
                    </div>
                    <div class="export-dropdown-item" onclick="window.copyPlatformMarkdown();window.toggleSyndicateExportMenu();">
                        <span class="item-icon">📑</span>
                        <div class="item-meta">
                            <span class="item-title">当前渠道适配 Markdown</span>
                            <span class="item-desc">应用了当前渠道规则的专属格式</span>
                        </div>
                    </div>
                    <div class="export-dropdown-item" onclick="window.copyTitleAndDigest();window.toggleSyndicateExportMenu();">
                        <span class="item-icon">📝</span>
                        <div class="item-meta">
                            <span class="item-title">一键复制标题与导语</span>
                            <span class="item-desc">提取精炼标题和摘要，方便表单快速填报</span>
                        </div>
                    </div>
                    ${!isWechat ? `
                    <div class="export-dropdown-item" onclick="window.copyWeChatRichText();window.toggleSyndicateExportMenu();">
                        <span class="item-icon">📱</span>
                        <div class="item-meta">
                            <span class="item-title">公众号高保真富文本</span>
                            <span class="item-desc">全局内联 CSS 与外链脚注，直接粘贴微信</span>
                        </div>
                    </div>` : ''}
                    ${!isZhihu ? `
                    <div class="export-dropdown-item" onclick="window.copyZhihuRichText();window.toggleSyndicateExportMenu();">
                        <span class="item-icon">知</span>
                        <div class="item-meta">
                            <span class="item-title">知乎高保真富文本</span>
                            <span class="item-desc">包含代码高亮与公式图片，直接粘贴知乎</span>
                        </div>
                    </div>` : ''}
                </div>
            </div>
        `;
    };

    // 点击外部自动关闭下拉菜单
    document.addEventListener('click', (e) => {
        const wrapper = document.querySelector('.syndicate-export-menu-wrapper');
        const menu = document.getElementById('syndicate-export-dropdown-menu');
        if (menu && menu.classList.contains('is-active')) {
            if (wrapper && !wrapper.contains(e.target)) {
                menu.classList.remove('is-active');
            }
        }
    });
})();
