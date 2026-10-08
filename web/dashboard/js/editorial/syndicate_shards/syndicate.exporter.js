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
        if (!text) {
            _notify('⚠️ 当前格式暂无可用文本', 'warning');
            return false;
        }
        try {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                await navigator.clipboard.writeText(text);
            } else {
                const ta = document.createElement('textarea');
                ta.value = text;
                ta.style.position = 'fixed';
                ta.style.opacity = '0';
                document.body.appendChild(ta);
                ta.select();
                document.execCommand('copy');
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

    /**
     * 1. 复制微信公众号富文本 (HTML + 纯文本双通道)
     */
    window.copyWeChatRichText = async function () {
        const html = window._currentRenderedHtml;
        if (!html) {
            _notify('⚠️ 暂未生成微信排版 HTML', 'warning');
            return;
        }
        try {
            if (navigator.clipboard && window.ClipboardItem) {
                const plainText = document.getElementById('preview-rendered-body-slot')?.innerText || html;
                await navigator.clipboard.write([
                    new ClipboardItem({
                        'text/html': new Blob([html], { type: 'text/html' }),
                        'text/plain': new Blob([plainText], { type: 'text/plain' })
                    })
                ]);
            } else {
                await writeClipboardText(html, null);
            }
            _notify('📋 公众号富文本已复制！可直接在微信公众号后台粘贴 (Cmd+V)', 'success');
        } catch (err) {
            console.error('Copy WeChat rich text error:', err);
            _notify('🛑 复制富文本失败，请手动选取正文复制', 'error');
        }
    };

    /**
     * 2. 复制当前渠道专属适配 Markdown
     */
    window.copyPlatformMarkdown = async function () {
        const md = window._currentRenderedMarkdown || '';
        await writeClipboardText(md, '📑 当前渠道适配 Markdown 已复制！');
    };

    /**
     * 3. 复制通用 Markdown（图床直链 / 纯净正文）
     */
    window.copyCleanMarkdownWithCdn = async function () {
        const md = window._currentCdnMarkdown || window._currentCleanMarkdown || window._currentRenderedMarkdown || '';
        await writeClipboardText(md, '🌐 图床直链 Markdown 已复制！可直接粘贴至知乎/掘金/CSDN');
    };

    /**
     * 4. 复制标准 Frontmatter Markdown (适用 Dev.to/Hashnode/Hexo)
     */
    window.copyFrontmatterMarkdown = async function () {
        const md = window._currentFrontmatterMarkdown || window._currentRenderedMarkdown || '';
        await writeClipboardText(md, '🏷️ 带 Frontmatter 格式已复制！适配 Dev.to/Hashnode/Hexo');
    };

    /**
     * 5. 复制标题与导语摘要
     */
    window.copyTitleAndDigest = async function () {
        const title = window._currentPreviewTitle || '';
        const digest = window._currentPreviewDigest || '';
        const text = `【标题】：${title}\n【导语】：${digest}`;
        await writeClipboardText(text, '📝 标题与导语已复制！方便表单填报');
    };

    /**
     * 切换多格式导出菜单显示/隐藏
     */
    window.toggleSyndicateExportMenu = function () {
        const menu = document.getElementById('syndicate-export-dropdown-menu');
        if (!menu) return;
        const isOpen = menu.classList.contains('is-active');
        if (isOpen) {
            menu.classList.remove('is-active');
        } else {
            menu.classList.add('is-active');
        }
    };

    /**
     * 统一构造排版审查视窗右侧操作区工具栏
     */
    window.renderSyndicateActionsToolbar = function (target, curTheme, activeMobile) {
        const isWechat = (target === 'wechat');
        return `
            <div class="syndicate-viewport-switcher" style="white-space: nowrap; flex-shrink: 0;">
                <button type="button" class="syndicate-viewport-btn ${activeMobile ? 'is-active' : ''}" style="white-space: nowrap;" onclick="window._previewViewport='mobile';window.renderSyndicateCardPreview()">📱 手机</button>
                <button type="button" class="syndicate-viewport-btn ${!activeMobile ? 'is-active' : ''}" style="white-space: nowrap;" onclick="window._previewViewport='desktop';window.renderSyndicateCardPreview()">💻 宽屏</button>
            </div>
            ${isWechat ? `
            <select class="syndicate-viewport-btn" style="width: auto !important; max-width: 105px !important; flex: 0 0 auto !important; padding: 4px 8px; font-size: 0.78rem; outline: none; border-radius: 6px; white-space: nowrap; flex-shrink: 0;" onchange="window.switchSyndicateTheme(this.value)" title="选择微信公众号专属配色矩阵">
                <option value="default" ${curTheme === 'default' ? 'selected' : ''}>🎨 科技蓝</option>
                <option value="emerald" ${curTheme === 'emerald' ? 'selected' : ''}>🌿 翡翠绿</option>
                <option value="amber" ${curTheme === 'amber' ? 'selected' : ''}>🍂 暖秋金</option>
                <option value="minimal" ${curTheme === 'minimal' ? 'selected' : ''}>🌙 极简灰</option>
            </select>
            <button type="button" class="syndicate-copy-wechat-btn glow-btn" style="white-space: nowrap; flex-shrink: 0;" onclick="window.copyWeChatRichText()" title="一键复制带行内 CSS 与脚注的高保真微信富文本">
                <span>📋 复制公众号富文本</span>
            </button>
            ` : ''}
            
            <!-- 多格式导出中枢下拉组件 -->
            <div class="syndicate-export-menu-wrapper" style="position: relative; display: inline-flex; align-items: center; white-space: nowrap; flex-shrink: 0;">
                <button type="button" class="syndicate-copy-markdown-btn" onclick="window.toggleSyndicateExportMenu()" style="display: inline-flex; align-items: center; gap: 5px; white-space: nowrap; flex-shrink: 0;" title="选择不同平台的发布格式导出">
                    <span>📦 多格式导出 ▾</span>
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
