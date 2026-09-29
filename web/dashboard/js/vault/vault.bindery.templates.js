/**
 * 📚 [V125.0] Illacme Plenipes Vault - Book Bindery Modal Templates Shard
 * 职责：数字装订弹窗的 DOM 模板渲染、CSS 响应式注入与格式化工具函数。
 * 规范：100% 遵守 SOP-03 前端视觉主权与双主题自适应规范，严守 300 行架构门禁。
 */

(function() {
    'use strict';

    function ensureStyles() {
        if (document.getElementById('bindery-responsive-theme-css')) return;
        const style = document.createElement('style');
        style.id = 'bindery-responsive-theme-css';
        style.textContent = `
            .bindery-modal-backdrop { position: fixed; inset: 0; z-index: 9999; background: rgba(0, 0, 0, 0.75); backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center; }
            .bindery-modal-card { width: 660px; max-width: 95vw; max-height: 94vh; overflow: hidden; padding: 12px 18px; border-radius: 14px; background: rgba(var(--bg-modal-solid-rgb, 14, 20, 32), 0.98); border: 1px solid rgba(16, 185, 129, 0.35); box-shadow: 0 25px 60px var(--black-50, rgba(0,0,0,0.6)), 0 0 30px rgba(16, 185, 129, 0.1); display: flex; flex-direction: column; gap: 7px; box-sizing: border-box; }
            .bindery-header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid var(--glass-border, rgba(255,255,255,0.08)); padding-bottom: 5px; }
            .bindery-title { font-size: 1.1rem; font-weight: 700; color: var(--text-bright, #ffffff); display: flex; align-items: center; gap: 8px; }
            .bindery-badge { font-size: 0.68rem; color: #10b981; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); padding: 1px 7px; border-radius: 10px; font-weight: 600; }
            .bindery-subtitle { font-size: 0.75rem; color: var(--text-dim, rgba(255,255,255,0.65)); margin-top: 2px; }
            .bindery-close-btn { background: none; border: none; color: var(--text-dim, rgba(255,255,255,0.5)); font-size: 1.35rem; cursor: pointer; padding: 0 4px; line-height: 1; transition: color 0.2s ease; }
            .bindery-close-btn:hover { color: var(--text-bright, #ffffff); }
            .bindery-label { display: block; font-size: 0.74rem; color: var(--text-dim, rgba(255,255,255,0.7)); font-weight: 600; margin-bottom: 2px; }
            .bindery-label-accent { display: block; font-size: 0.74rem; color: var(--neon-green, #10b981); font-weight: 600; margin-bottom: 2px; }
            .bindery-input, .bindery-select { width: 100%; box-sizing: border-box; background: var(--white-05, rgba(255,255,255,0.05)); border: 1px solid var(--glass-border, rgba(255,255,255,0.15)); border-radius: 7px; padding: 4px 8px; color: var(--text-bright, #ffffff); font-size: 0.8rem; outline: none; transition: all 0.2s ease; }
            .bindery-input:focus, .bindery-select:focus { border-color: #10b981; box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15); }
            .bindery-select option, .bindery-select optgroup { background: rgba(var(--bg-dropdown-solid-rgb, 14, 20, 32), 0.98); color: var(--text-bright, #ffffff); }
            .bindery-driver-card { background: rgba(255, 255, 255, 0.03); border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1)); border-radius: 7px; padding: 4px 7px; display: flex; align-items: center; justify-content: space-between; cursor: pointer; transition: all 0.2s ease; }
            .bindery-driver-card:hover { border-color: rgba(16, 185, 129, 0.4); }
            .bindery-driver-card.active { background: rgba(16, 185, 129, 0.09); border-color: rgba(16, 185, 129, 0.6); box-shadow: 0 0 10px rgba(16, 185, 129, 0.15); }
            .bindery-driver-title { font-size: 0.78rem; font-weight: 700; color: var(--text-bright, #ffffff); }
            .bindery-driver-desc { font-size: 0.64rem; color: var(--text-dim, rgba(255,255,255,0.6)); }
            .bindery-footer { display: flex; justify-content: flex-end; gap: 8px; margin-top: 2px; border-top: 1px solid var(--glass-border, rgba(255,255,255,0.08)); padding-top: 6px; }
            .bindery-nav-tab { background: none; border: none; border-bottom: 2px solid transparent; color: var(--text-dim, rgba(255,255,255,0.6)); font-size: 0.82rem; font-weight: 600; padding: 4px 10px; cursor: pointer; transition: all 0.2s; }
            .bindery-nav-tab:hover { color: var(--text-bright, #fff); } .bindery-nav-tab.active { color: #10b981; border-bottom-color: #10b981; }
            .bindery-shelf-card:hover { border-color: rgba(16, 185, 129, 0.35) !important; background: rgba(255, 255, 255, 0.05) !important; }
            .bindery-del-btn:hover { color: #ef4444 !important; }
            .bindery-matrix-chip { background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.15); color: var(--text-bright, #ffffff); transition: all 0.2s ease; }
            .bindery-matrix-chip:hover { border-color: rgba(16, 185, 129, 0.5) !important; background: rgba(16, 185, 129, 0.1) !important; }
            .bindery-status-item { display:flex; justify-content:space-between; align-items:center; padding:3px 6px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.08); border-radius:5px; margin-top:2px; font-size:0.72rem; gap:6px; transition:all 0.2s; }
            .bindery-status-item:hover { background:rgba(255,255,255,0.08); border-color:rgba(16,185,129,0.3); }
            .bindery-status-item-text { font-family:var(--font-mono, monospace); color:var(--text-bright, #ffffff); min-width:0; flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
            .bindery-status-item-text strong { color:#34d399; font-weight:700; }
            .bindery-shelf-quick-btn { background:rgba(56,189,248,0.15); color:#38bdf8; border:1px solid rgba(56,189,248,0.3); border-radius:5px; padding:2px 7px; font-size:0.7rem; cursor:pointer; transition:all 0.2s; }
            .bindery-shelf-quick-btn:hover { background:rgba(56,189,248,0.25); color:#7dd3fc; }
            .bindery-sub-action-btn { padding:1px 5px; font-size:0.7rem; border-radius:4px; color:var(--text-bright, #fff); border:1px solid var(--glass-border, rgba(255,255,255,0.12)); cursor:pointer; background:rgba(255,255,255,0.06); transition:all 0.2s; display:inline-flex; align-items:center; justify-content:center; }
            .bindery-sub-action-btn:hover { background:rgba(255,255,255,0.14); color:#fff; }
            [data-theme="light"] .bindery-matrix-chip { background: #f1f5f9 !important; border-color: #cbd5e1 !important; color: #1e293b !important; }
            [data-theme="light"] .bindery-matrix-chip span { color: #1e293b !important; }
            [data-theme="light"] .bindery-status-item { background: #ffffff !important; border-color: rgba(16,185,129,0.35) !important; box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important; }
            [data-theme="light"] .bindery-status-item-text { color: #1e293b !important; }
            [data-theme="light"] .bindery-status-item-text strong { color: #047857 !important; }
            [data-theme="light"] .bindery-shelf-quick-btn { background: #e0f2fe !important; color: #0369a1 !important; border-color: #7dd3fc !important; font-weight:600 !important; }
            [data-theme="light"] .bindery-shelf-quick-btn:hover { background: #bae6fd !important; color: #0284c7 !important; }
            [data-theme="light"] .bindery-sub-action-btn { background: #f1f5f9 !important; border-color: #cbd5e1 !important; color: #1e293b !important; }
            [data-theme="light"] .bindery-sub-action-btn:hover { background: #e2e8f0 !important; color: #0f172a !important; border-color: #94a3b8 !important; }`;
        document.head.appendChild(style);
    }

    function esc(str) { return !str ? '' : String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;'); }
    function formatSize(b) { if (!b || b <= 0) return '0 B'; const u = ['B', 'KB', 'MB', 'GB'], i = Math.floor(Math.log(b) / Math.log(1024)); return (b / Math.pow(1024, i)).toFixed(1) + ' ' + u[i]; }

    function buildLoadingHtml() {
        return `<div class="glass-panel bindery-modal-card" style="width: 480px; text-align: center; padding: 32px 24px;">
            <div class="spinner" style="display:inline-block; width:36px; height:36px; border:3px solid rgba(16,185,129,0.2); border-top-color:#10b981; border-radius:50%; animation:spin 1s linear infinite; margin-bottom:15px;"></div>
            <div style="font-size:0.95rem; color:var(--text-bright, #fff); font-weight:600;">正在勘测文库章节与出版版式...</div>
        </div><style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>`;
    }

    function buildModalCardHtml(scopesData, currentScope, defaultTitle, sticky = {}) {
        const isSingle = currentScope && currentScope.startsWith('single:');
        const singleDocTitle = (scopesData.single_doc && scopesData.single_doc.title) || (isSingle ? currentScope.slice(7) : '');
        let categoryOptionsHtml = isSingle ? `<option value="${esc(currentScope)}" selected>📄 单篇: ${esc(singleDocTitle)}</option>` : '';
        categoryOptionsHtml += (scopesData.categories || []).map(cat => `<option value="${esc(cat.id)}" ${cat.id === currentScope ? 'selected' : ''}>${esc(cat.name)}</option>`).join('');

        const availLangs = scopesData.available_languages || [
            { code: 'zh', name: '简体中文', icon: '🇨🇳', count: 0, is_source: true },
            { code: 'en', name: 'English', icon: '🇬🇧', count: 0 },
            { code: 'ja', name: '日本語', icon: '🇯🇵', count: 0 }
        ];

        const sourceLang = (availLangs.find(l => l.is_source) || {}).code || scopesData.default_lang || 'zh';
        const effectiveLang = sticky.lang || sourceLang;
        const sourceLangObj = availLangs.find(l => l.code === effectiveLang) || availLangs.find(l => l.code === sourceLang) || availLangs[0] || { code: 'zh', name: '简体中文' };
        const sourceLangLabel = sourceLangObj.name ? (sourceLangObj.name.includes('版') ? sourceLangObj.name : sourceLangObj.name + '版') : '单语言版';

        const singleLangOptions = availLangs.map(l => `<option value="${esc(l.code)}" ${l.code === effectiveLang ? 'selected' : ''}>${l.icon || '🌐'} ${esc(l.name)} (${l.is_source ? '源稿 ' + l.count + ' 篇' : '译文 ' + l.count + ' 篇'})</option>`).join('');
        const langOptionsHtml = `<optgroup label="── 单语言独立版本 ──">${singleLangOptions}</optgroup><optgroup label="── 多语言综合矩阵 ──"><option value="polyglot" ${effectiveLang === 'polyglot' ? 'selected' : ''}>📑 双语/多语对照版 (单本内置多栏对照研读)</option><option value="matrix_batch" ${effectiveLang === 'matrix_batch' ? 'selected' : ''}>📦 多语言单行本并发制作 (${availLangs.length} 本独立电子书)</option></optgroup>`;

        const matrixChipsHtml = availLangs.map(l => `<label class="bindery-matrix-chip" style="display:inline-flex; align-items:center; gap:3px; font-size:0.66rem; border-radius:4px; padding:1px 5px; cursor:pointer; white-space:nowrap; flex-shrink:0;"><input type="checkbox" class="bindery-matrix-cb" value="${esc(l.code)}" ${l.count > 0 || l.is_source ? 'checked' : ''} onchange="window.updateMatrixSubmitBtn()" style="accent-color:#10b981;" /><span>${l.icon || '🌐'} ${esc(l.name)}</span></label>`).join('');
        const polyChipsHtml = availLangs.map(l => `<label class="bindery-matrix-chip" style="display:inline-flex; align-items:center; gap:3px; font-size:0.66rem; border-radius:4px; padding:1px 5px; cursor:pointer; white-space:nowrap; flex-shrink:0;"><input type="checkbox" class="bindery-poly-cb" value="${esc(l.code)}" ${l.code === sourceLang || l.code === 'en' ? 'checked' : ''} onchange="window.updatePolyglotSubmitBtn()" style="accent-color:#10b981;" /><span>${l.icon || '🌐'} ${esc(l.name)}${l.code === sourceLang ? ' (主)' : ''}</span></label>`).join('');

        return `
            <div class="glass-panel bindery-modal-card">
                <div class="bindery-header">
                    <div style="min-width:0; flex:1; padding-right:12px;">
                        <div class="bindery-title"><span>📚 数字出版装订中枢</span><span class="bindery-badge">EPUB / WebBook / PDF / DOCX / MD / TXT</span></div>
                        <div class="bindery-subtitle" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">文库原稿整卷编排、双链自愈跳转，封装为标准流式电子书、独立网页书或印刷级印本。</div>
                    </div>
                    <button class="bindery-close-btn" onclick="window.closeBinderyModal()" title="关闭">×</button>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--glass-border, rgba(255,255,255,0.08)); padding-bottom:4px;">
                    <div style="display:flex; gap:6px;">
                        <button id="btn-bindery-tab-build" class="bindery-nav-tab active" onclick="window.switchBinderyTab('build')">🖨️ 装订新版</button>
                        <button id="btn-bindery-tab-shelf" class="bindery-nav-tab" onclick="window.switchBinderyTab('shelf')" style="display:flex; align-items:center; gap:5px;"><span>📚 我的书架</span><span id="bindery-shelf-badge" class="bindery-badge" style="font-size:0.62rem; padding:1px 5px;">0</span></button>
                    </div>
                    <div id="bindery-shelf-header-actions" style="display:none; align-items:center; gap:6px;"></div>
                </div>
                <div id="bindery-panel-build" style="display: flex; flex-direction: column; gap: 7px; overflow-y: auto; scrollbar-width: thin; max-height: calc(94vh - 75px);">
                    <div style="display: grid; grid-template-columns: 3fr 2fr; gap: 8px;">
                        <div>
                            <label class="bindery-label-accent">📖 出版物标题 (Title)</label>
                            <input type="text" id="bindery-input-title" class="bindery-input" value="${esc(defaultTitle)}" placeholder="电子书主标题..." />
                        </div>
                        <div>
                            <label class="bindery-label">✍️ 著作者/出版署名</label>
                            <input type="text" id="bindery-input-author" class="bindery-input" value="${esc(sticky.author || scopesData.default_author || 'Illacme Editorial Team')}" placeholder="作者或制作团队..." />
                        </div>
                    </div>

                    <!-- 封面装帧与出版规格整合区块 -->
                    <div style="display: flex; gap: 10px; background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border, rgba(255,255,255,0.1)); border-radius: 8px; padding: 7px 10px; align-items: stretch;">
                        <div id="bindery-cover-preview-box" onclick="document.getElementById('bindery-cover-file-input')?.click()" style="width: 68px; min-height: 98px; border-radius: 6px; overflow: hidden; background: #0b1219; border: 1px solid rgba(16,185,129,0.35); flex-shrink: 0; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.35); position:relative; cursor:pointer;" title="点击上传自定义封面图片">
                            <img id="bindery-cover-img" style="width: 100%; height: 100%; object-fit: cover; display: block;" alt="Cover" />
                            <div id="bindery-cover-none-ph" style="display:none; text-align:center; color:var(--text-dim, #94a3b8); font-size:0.75rem; line-height:1.4;">📰<br/><span style="font-size:0.62rem; color:#38bdf8;">纯净免封</span></div>
                            <input type="file" id="bindery-cover-file-input" accept="image/*" style="display:none;" onchange="window.handleBinderyCoverUpload(this.files[0])" />
                        </div>
                        <div style="flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: space-between; gap: 6px;">
                            <div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom:2px;">
                                    <label class="bindery-label" style="margin: 0;">🖼️ 出版装帧封面策略</label>
                                    <span id="bindery-cover-badge" class="bindery-badge" style="font-size: 0.6rem; padding:1px 4px;">✨ 智能排版</span>
                                </div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                                    <select id="bindery-select-cover-mode" class="bindery-select" onchange="window.refreshCoverPreview()">
                                        <option value="none" ${(sticky.cover_mode || (isSingle ? 'none' : 'auto')) === 'none' ? 'selected' : ''}>📰 纯净正文流 (免大封面)</option>
                                        <option value="auto" ${(sticky.cover_mode || (isSingle ? 'none' : 'auto')) === 'auto' ? 'selected' : ''}>✨ 智能自愈 (文库/排版)</option>
                                        <option value="generated" ${sticky.cover_mode === 'generated' ? 'selected' : ''}>🎨 艺术装帧大封面</option>
                                        <option value="custom" ${sticky.cover_mode === 'custom' ? 'selected' : ''}>📁 自定义上传封面...</option>
                                    </select>
                                    <select id="bindery-select-cover-style" class="bindery-select" onchange="window.refreshCoverPreview()">
                                        <option value="dark_emerald" ${(sticky.cover_style || 'dark_emerald') === 'dark_emerald' ? 'selected' : ''}>🌿 黑曜翡翠 (Emerald)</option>
                                        <option value="classic_navy" ${sticky.cover_style === 'classic_navy' ? 'selected' : ''}>🌌 藏青午夜 (Navy)</option>
                                        <option value="obsidian_gold" ${sticky.cover_style === 'obsidian_gold' ? 'selected' : ''}>👑 黑金雅致 (Gold)</option>
                                    </select>
                                    <button id="btn-bindery-upload-cover" type="button" class="secondary-btn" onclick="document.getElementById('bindery-cover-file-input')?.click()" style="display:none; padding:4px 6px; font-size:0.72rem; border-radius:5px; align-items:center; justify-content:center; gap:4px; border:1px solid rgba(16,185,129,0.4); color:#10b981; cursor:pointer; background:rgba(16,185,129,0.08);">📤 选择本地图片</button>
                                </div>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; align-items: start;">
                                <div>
                                    <label class="bindery-label" style="margin-bottom:2px;">📂 章节收录范围</label>
                                    <select id="bindery-select-scope" class="bindery-select">${categoryOptionsHtml}</select>
                                </div>
                                <div>
                                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:2px;">
                                        <label class="bindery-label" style="margin:0;">🌍 出版语种与规格</label>
                                        <div style="display:flex; align-items:center; gap:4px;">
                                            <span id="bindery-matrix-toggle-btn" style="display:none; cursor:pointer; color:#10b981; font-size:0.62rem; user-select:none; padding:1px 4px; border-radius:3px; background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.25);" onclick="window.toggleAllBinderyMatrixLangs()" title="点击全选/反选">反选</span>
                                            <span id="bindery-lang-hint-badge" class="bindery-badge" style="font-size:0.6rem; padding:1px 4px;">单语言版</span>
                                        </div>
                                    </div>
                                    <select id="bindery-select-lang" class="bindery-select" onchange="window.onBinderyLangModeChange(this.value)">${langOptionsHtml}</select>
                                    <div id="bindery-matrix-chips-row" style="display:none; margin-top:3px; align-items:center; gap:3px; flex-wrap:nowrap; overflow-x:auto; padding-bottom:1px; scrollbar-width:thin;">${matrixChipsHtml}</div>
                                    <div id="bindery-poly-chips-row" style="display:none; margin-top:3px; align-items:center; gap:3px; flex-wrap:nowrap; overflow-x:auto; padding-bottom:1px; scrollbar-width:thin;">${polyChipsHtml}</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 装订驱动与格式（3x2 布局） -->
                    <div>
                        <label class="bindery-label" style="margin-bottom:3px;">🖨️ 装订驱动与格式</label>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 5px;">
                            <div class="bindery-driver-card ${(sticky.format || 'epub') === 'epub' ? 'active' : ''}" id="btn-driver-epub" onclick="window.selectBinderyFormat('epub')">
                                <div style="display:flex; align-items:center; gap:5px;">
                                    <span style="font-size:0.95rem;">📖</span>
                                    <div><div class="bindery-driver-title">EPUB 3.0</div><div class="bindery-driver-desc">流式重排</div></div>
                                </div>
                                <span style="font-size:0.62rem; color:#10b981; font-weight:700;">● 推荐</span>
                            </div>
                            <div class="bindery-driver-card ${sticky.format === 'webbook' ? 'active' : ''}" id="btn-driver-webbook" onclick="window.selectBinderyFormat('webbook')">
                                <div style="display:flex; align-items:center; gap:5px;">
                                    <span style="font-size:0.95rem;">🌐</span>
                                    <div><div class="bindery-driver-title">WebBook</div><div class="bindery-driver-desc">离线网页</div></div>
                                </div>
                                <span style="font-size:0.62rem; color:#38bdf8; font-weight:700;">● 独立</span>
                            </div>
                            <div class="bindery-driver-card ${sticky.format === 'pdf' ? 'active' : ''}" id="btn-driver-pdf" onclick="window.selectBinderyFormat('pdf')">
                                <div style="display:flex; align-items:center; gap:5px;">
                                    <span style="font-size:0.95rem;">📄</span>
                                    <div><div class="bindery-driver-title">PDF 印本</div><div class="bindery-driver-desc">固定印刷</div></div>
                                </div>
                                <span style="font-size:0.62rem; color:#a855f7; font-weight:700;">● 印本</span>
                            </div>
                            <div class="bindery-driver-card ${sticky.format === 'docx' ? 'active' : ''}" id="btn-driver-docx" onclick="window.selectBinderyFormat('docx')">
                                <div style="display:flex; align-items:center; gap:5px;">
                                    <span style="font-size:0.95rem;">📑</span>
                                    <div><div class="bindery-driver-title">Word 文档</div><div class="bindery-driver-desc">出版投稿</div></div>
                                </div>
                                <span style="font-size:0.62rem; color:#f59e0b; font-weight:700;">● 文档</span>
                            </div>
                            <div class="bindery-driver-card ${sticky.format === 'markdown' ? 'active' : ''}" id="btn-driver-markdown" onclick="window.selectBinderyFormat('markdown')">
                                <div style="display:flex; align-items:center; gap:5px;">
                                    <span style="font-size:0.95rem;">📝</span>
                                    <div><div class="bindery-driver-title">Markdown 合集</div><div class="bindery-driver-desc">长篇归档</div></div>
                                </div>
                                <span style="font-size:0.62rem; color:#06b6d4; font-weight:700;">● RAG</span>
                            </div>
                            <div class="bindery-driver-card ${sticky.format === 'txt' ? 'active' : ''}" id="btn-driver-txt" onclick="window.selectBinderyFormat('txt')">
                                <div style="display:flex; align-items:center; gap:5px;">
                                    <span style="font-size:0.95rem;">📜</span>
                                    <div><div class="bindery-driver-title">TXT 便携</div><div class="bindery-driver-desc">极简文本</div></div>
                                </div>
                                <span style="font-size:0.62rem; color:#8b5cf6; font-weight:700;">● 便携</span>
                            </div>
                        </div>
                    </div>

                    <div id="bindery-status-area" style="display:none; max-height:126px; overflow:hidden; padding:5px 8px; border-radius:7px; font-size:0.78rem; line-height:1.3;"></div>

                    <div class="bindery-footer">
                        <button id="btn-bindery-cancel" class="secondary-btn" onclick="window.closeBinderyModal()" style="padding: 5px 14px; font-size: 0.82rem; border-radius: 7px; cursor:pointer;">取消</button>
                        <button id="btn-execute-binding" class="primary-btn glow-btn" onclick="window.executeBookBinding()" style="padding: 5px 18px; font-size: 0.82rem; border-radius: 7px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color:#fff; border:none; font-weight:600; cursor:pointer; display:flex; align-items:center; gap:6px;"><span>🚀 立即装订 (${esc(sourceLangLabel)})</span></button>
                    </div>
                </div>

                <div id="bindery-panel-shelf" style="display: none; flex-direction: column; gap: 8px;">
                    <div id="bindery-shelf-list"></div>
                    <div style="display: flex; justify-content: flex-end; margin-top: 4px; border-top: 1px solid var(--glass-border, rgba(255,255,255,0.08)); padding-top: 8px;"><button class="secondary-btn" onclick="window.closeBinderyModal()" style="padding: 5px 14px; font-size: 0.82rem; border-radius: 7px; cursor:pointer;">关闭</button></div>
                </div>
            </div>
        `;
    }

    function buildSuccessStatusHtml(result, formattedSize) {
        const isPdf = result.format === 'pdf' || (result.filename && result.filename.endsWith('.pdf'));
        const isWb = result.format === 'webbook' || (result.filename && result.filename.endsWith('.html'));
        const pvTitle = isPdf ? '在线阅览 (PDF 印本)' : (isWb ? '在线翻阅 (WebBook)' : '在线翻阅 (EPUB 3.0)');
        const pvUrl = result.preview_url || (result.filename ? `/api/bindery/view?file=${encodeURIComponent(result.filename)}` : null);
        const pvBtn = pvUrl ? `<a href="${pvUrl}" target="_blank" rel="noopener noreferrer" class="primary-btn glow-btn" title="${pvTitle}" style="padding:2px 6px; font-size:0.75rem; text-decoration:none; display:inline-flex; align-items:center; justify-content:center; border-radius:5px; background:#0284c7; color:#fff; flex-shrink:0;">👁️</a>` : '';
        const dlUrl = result.download_url || (result.filename ? `/api/bindery/download?file=${encodeURIComponent(result.filename)}` : '#');

        if (result.mode === 'matrix' && Array.isArray(result.results)) {
            const itemsHtml = result.results.map(r => {
                const sz = formatSize(r.size_bytes || 0), fn = r.filename || '';
                const rIsPdf = r.format === 'pdf' || fn.endsWith('.pdf'), rIsWb = r.format === 'webbook' || fn.endsWith('.html');
                const rTitle = rIsPdf ? '在线阅览 (PDF)' : (rIsWb ? '在线翻阅 (WebBook)' : '在线翻阅 (EPUB)');
                const itemPv = r.preview_url || (fn ? `/api/bindery/view?file=${encodeURIComponent(fn)}` : null);
                const itemPvBtn = itemPv ? `<a href="${itemPv}" target="_blank" rel="noopener noreferrer" class="primary-btn glow-btn" title="${rTitle}" style="padding:1px 5px; font-size:0.7rem; text-decoration:none; border-radius:4px; background:#0284c7; color:#fff; display:inline-flex; align-items:center; justify-content:center; flex-shrink:0;">👁️</a>` : '';
                const itemDlUrl = r.download_url || (fn ? `/api/bindery/download?file=${encodeURIComponent(fn)}` : '#');
                const chNum = (r.chapter_count !== undefined && r.chapter_count !== null) ? `${r.chapter_count}篇 / ` : '';
                return `<div class="bindery-status-item">
                    <span class="bindery-status-item-text" title="${esc(fn)}"><strong>[${esc((r.language || r.lang || '').toUpperCase())}]</strong> ${esc(fn)} (${chNum}${sz})</span>
                    <div style="display:flex; align-items:center; gap:5px; flex-shrink:0;">${itemPvBtn}<a href="${itemDlUrl}" download="${esc(fn)}" class="primary-btn" title="下载出版物" style="padding:1px 5px; font-size:0.7rem; text-decoration:none; border-radius:4px; background:#10b981; color:#fff; display:inline-flex; align-items:center; justify-content:center; flex-shrink:0;">⬇️</a><button type="button" onclick="window.revealBookInFolder('${esc(fn)}')" class="secondary-btn bindery-sub-action-btn" title="在系统文件夹中显示">📂</button><button type="button" onclick="window.openBinderyQrModal('${esc(fn)}')" class="secondary-btn bindery-sub-action-btn" title="扫码同步至移动设备 (手机/平板/Kindle)">📱</button></div>
                </div>`;
            }).join('');

            return `<div style="display:flex; flex-direction:column; gap:4px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div><strong>🎉 多语言制作完成！</strong> 共并发生成 <strong>${result.total_built || result.results.length}</strong> 本电子书</div>
                    <button class="bindery-shelf-quick-btn" onclick="window.switchBinderyTab('shelf')">📚 查看书架</button>
                </div>
                <div style="max-height:86px; overflow-y:auto; scrollbar-width:thin; padding-right:2px;">${itemsHtml}</div>
            </div>`;
        }

        const countText = (result.chapter_count !== undefined && result.chapter_count !== null) ? `已收录 <strong>${result.chapter_count}</strong> 篇章节` : `已完成编排封装`;
        return `<div style="display:flex; justify-content:space-between; align-items:center; gap:8px;">
            <div style="min-width:0; flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"><strong>🎉 装订完成！</strong> ${countText} (${formattedSize})</div>
            <div style="display:flex; align-items:center; gap:5px; flex-shrink:0;">
                ${pvBtn}
                <a href="${dlUrl}" download="${esc(result.filename)}" class="primary-btn glow-btn" title="下载保存出版物" style="padding:3px 7px; font-size:0.8rem; text-decoration:none; display:inline-flex; align-items:center; justify-content:center; border-radius:5px; background:#10b981; color:#fff; flex-shrink:0;">⬇️</a>
                <button type="button" onclick="window.revealBookInFolder('${esc(result.filename)}')" class="secondary-btn bindery-sub-action-btn" title="在系统文件夹中显示" style="padding:3px 7px; font-size:0.8rem;">📂</button>
                <button type="button" onclick="window.openBinderyQrModal('${esc(result.filename)}')" class="secondary-btn bindery-sub-action-btn" title="扫码同步至移动设备 (手机/平板/Kindle)" style="padding:3px 7px; font-size:0.8rem;">📱</button>
            </div>
        </div>`;
    }

    window.BinderyTemplates = {
        ensureStyles,
        esc,
        formatSize,
        buildLoadingHtml,
        buildModalCardHtml,
        buildSuccessStatusHtml
    };
})();
