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
            .bindery-modal-backdrop { position: fixed; inset: 0; z-index: 9999; background: rgba(0, 0, 0, 0.75); backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center; opacity: 0; pointer-events: none; transition: opacity 0.25s ease; }
            .bindery-modal-card { width: 620px; max-width: 92vw; padding: 24px 28px; border-radius: 16px; background: rgba(var(--bg-modal-solid-rgb, 14, 20, 32), 0.98); border: 1px solid rgba(16, 185, 129, 0.35); box-shadow: 0 25px 60px var(--black-50, rgba(0,0,0,0.6)), 0 0 30px rgba(16, 185, 129, 0.1); display: flex; flex-direction: column; gap: 16px; transition: all 0.3s ease; }
            .bindery-header { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid var(--glass-border, rgba(255,255,255,0.08)); padding-bottom: 12px; }
            .bindery-title { font-size: 1.25rem; font-weight: 700; color: var(--text-bright, #ffffff); display: flex; align-items: center; gap: 8px; }
            .bindery-badge { font-size: 0.7rem; color: #10b981; background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); padding: 2px 8px; border-radius: 10px; font-weight: 600; }
            .bindery-subtitle { font-size: 0.8rem; color: var(--text-dim, rgba(255,255,255,0.65)); margin-top: 4px; }
            .bindery-close-btn { background: none; border: none; color: var(--text-dim, rgba(255,255,255,0.5)); font-size: 1.4rem; cursor: pointer; padding: 0 4px; line-height: 1; transition: color 0.2s ease; }
            .bindery-close-btn:hover { color: var(--text-bright, #ffffff); }
            .bindery-label { display: block; font-size: 0.78rem; color: var(--text-dim, rgba(255,255,255,0.7)); font-weight: 600; margin-bottom: 5px; }
            .bindery-label-accent { display: block; font-size: 0.78rem; color: var(--neon-green, #10b981); font-weight: 600; margin-bottom: 5px; }
            .bindery-input, .bindery-select { width: 100%; box-sizing: border-box; background: var(--white-05, rgba(255,255,255,0.05)); border: 1px solid var(--glass-border, rgba(255,255,255,0.15)); border-radius: 8px; padding: 7px 10px; color: var(--text-bright, #ffffff); font-size: 0.85rem; outline: none; transition: all 0.2s ease; }
            .bindery-input:focus, .bindery-select:focus { border-color: #10b981; box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15); }
            .bindery-select option, .bindery-select optgroup { background: rgba(var(--bg-dropdown-solid-rgb, 14, 20, 32), 0.98); color: var(--text-bright, #ffffff); }
            .bindery-driver-card { flex: 1; background: rgba(255, 255, 255, 0.03); border: 1px solid var(--glass-border, rgba(255, 255, 255, 0.1)); border-radius: 8px; padding: 10px 12px; display: flex; align-items: center; justify-content: space-between; cursor: pointer; transition: all 0.2s ease; }
            .bindery-driver-card:hover { border-color: rgba(16, 185, 129, 0.4); }
            .bindery-driver-card.active { background: rgba(16, 185, 129, 0.09); border-color: rgba(16, 185, 129, 0.6); box-shadow: 0 0 12px rgba(16, 185, 129, 0.15); }
            .bindery-driver-title { font-size: 0.85rem; font-weight: 700; color: var(--text-bright, #ffffff); }
            .bindery-driver-desc { font-size: 0.72rem; color: var(--text-dim, rgba(255,255,255,0.6)); }
            .bindery-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: 6px; border-top: 1px solid var(--glass-border, rgba(255,255,255,0.08)); padding-top: 14px; }
            .bindery-nav-tab { background: none; border: none; border-bottom: 2px solid transparent; color: var(--text-dim, rgba(255,255,255,0.6)); font-size: 0.85rem; font-weight: 600; padding: 6px 12px; cursor: pointer; transition: all 0.2s; }
            .bindery-nav-tab:hover { color: var(--text-bright, #fff); }
            .bindery-nav-tab.active { color: #10b981; border-bottom-color: #10b981; }
            .bindery-shelf-card:hover { border-color: rgba(16, 185, 129, 0.35) !important; background: rgba(255, 255, 255, 0.05) !important; }
            .bindery-del-btn:hover { color: #ef4444 !important; }
            .bindery-matrix-chip { background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.15); color: var(--text-bright, #ffffff); transition: all 0.2s ease; }
            .bindery-matrix-chip:hover { border-color: rgba(16, 185, 129, 0.5) !important; background: rgba(16, 185, 129, 0.1) !important; }
            [data-theme="light"] .bindery-matrix-chip { background: #f1f5f9 !important; border-color: #cbd5e1 !important; color: #1e293b !important; }
            [data-theme="light"] .bindery-matrix-chip span { color: #1e293b !important; }
        `;
        document.head.appendChild(style);
    }

    function esc(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function formatSize(bytes) {
        if (!bytes || bytes <= 0) return '0 B';
        const units = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return (bytes / Math.pow(1024, i)).toFixed(1) + ' ' + units[i];
    }

    function buildLoadingHtml() {
        return `
            <div class="glass-panel bindery-modal-card" style="width: 480px; text-align: center; padding: 32px 24px;">
                <div class="spinner" style="display:inline-block; width:36px; height:36px; border:3px solid rgba(16,185,129,0.2); border-top-color:#10b981; border-radius:50%; animation:spin 1s linear infinite; margin-bottom:15px;"></div>
                <div style="font-size:0.95rem; color:var(--text-bright, #fff); font-weight:600;">正在勘测文库章节与出版版式...</div>
            </div>
            <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>
        `;
    }

    function buildModalCardHtml(scopesData, currentScope, defaultTitle) {
        const isSingle = currentScope && currentScope.startsWith('single:');
        const singleDocTitle = (scopesData.single_doc && scopesData.single_doc.title) || (isSingle ? currentScope.slice(7) : '');
        let categoryOptionsHtml = isSingle ? `<option value="${esc(currentScope)}" selected>📄 单篇: ${esc(singleDocTitle)}</option>` : '';
        categoryOptionsHtml += (scopesData.categories || []).map(cat => `
            <option value="${esc(cat.id)}" ${cat.id === currentScope ? 'selected' : ''}>${esc(cat.name)}</option>
        `).join('');

        const availLangs = scopesData.available_languages || [
            { code: 'zh', name: '简体中文', icon: '🇨🇳', count: 0, is_source: true },
            { code: 'en', name: 'English', icon: '🇬🇧', count: 0 },
            { code: 'ja', name: '日本語', icon: '🇯🇵', count: 0 }
        ];

        const sourceLang = (availLangs.find(l => l.is_source) || {}).code || scopesData.default_lang || 'zh';
        const sourceLangObj = availLangs.find(l => l.code === sourceLang) || availLangs[0] || { code: 'zh', name: '简体中文' };
        const sourceLangLabel = sourceLangObj.name ? (sourceLangObj.name.includes('版') ? sourceLangObj.name : sourceLangObj.name + '版') : '单语言版';

        const singleLangOptions = availLangs.map(l => `
            <option value="${esc(l.code)}" ${l.code === sourceLang ? 'selected' : ''}>
                ${l.icon || '🌐'} ${esc(l.name)} (${l.is_source ? '源稿 ' + l.count + ' 篇' : '译文 ' + l.count + ' 篇'})
            </option>
        `).join('');

        const langOptionsHtml = `
            <optgroup label="── 单语言独立版本 ──">
                ${singleLangOptions}
            </optgroup>
            <optgroup label="── 多语言综合矩阵 ──">
                <option value="polyglot">📑 双语/多语对照版 (单本内置多栏对照研读)</option>
                <option value="matrix_batch">📦 多语言单行本并发制作 (${availLangs.length} 本独立电子书)</option>
            </optgroup>
        `;

        const matrixChipsHtml = availLangs.map(l => `
            <label class="bindery-matrix-chip" style="display:inline-flex; align-items:center; gap:4px; font-size:0.72rem; border-radius:5px; padding:2px 6px; cursor:pointer;">
                <input type="checkbox" class="bindery-matrix-cb" value="${esc(l.code)}" ${l.count > 0 || l.is_source ? 'checked' : ''} onchange="window.updateMatrixSubmitBtn()" style="accent-color:#10b981;" />
                <span>${l.icon || '🌐'} ${esc(l.name)}</span>
            </label>
        `).join('');

        return `
            <div class="glass-panel bindery-modal-card">
                <div class="bindery-header">
                    <div>
                        <div class="bindery-title">
                            <span>📚 数字出版装订中枢</span>
                            <span class="bindery-badge">EPUB / WebBook / PDF</span>
                        </div>
                        <div class="bindery-subtitle">
                            将文库原稿整卷编排、自愈双链跳转，并封装为国际标准流式电子书、独立网页书或精致 PDF 印本。
                        </div>
                    </div>
                    <button class="bindery-close-btn" onclick="window.closeBinderyModal()" title="关闭">×</button>
                </div>

                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--glass-border, rgba(255,255,255,0.08)); padding-bottom:6px;">
                    <div style="display:flex; gap:8px;">
                        <button id="btn-bindery-tab-build" class="bindery-nav-tab active" onclick="window.switchBinderyTab('build')">🖨️ 装订新版</button>
                        <button id="btn-bindery-tab-shelf" class="bindery-nav-tab" onclick="window.switchBinderyTab('shelf')" style="display:flex; align-items:center; gap:6px;"><span>📚 我的书架</span><span id="bindery-shelf-badge" class="bindery-badge" style="font-size:0.65rem; padding:1px 6px;">0</span></button>
                    </div>
                    <div id="bindery-shelf-header-actions" style="display:none; align-items:center; gap:8px;"></div>
                </div>

                <div id="bindery-panel-build" style="display: flex; flex-direction: column; gap: 14px;">
                    <div style="display: grid; grid-template-columns: 3fr 2fr; gap: 12px;">
                        <div>
                            <label class="bindery-label-accent">📖 出版物标题 (Title)</label>
                            <input type="text" id="bindery-input-title" class="bindery-input" value="${esc(defaultTitle)}" placeholder="电子书主标题..." />
                        </div>
                        <div>
                            <label class="bindery-label">✍️ 著作者/出版署名</label>
                            <input type="text" id="bindery-input-author" class="bindery-input" value="${esc(scopesData.default_author)}" placeholder="作者或制作团队..." />
                        </div>
                    </div>

                    <!-- 保持原单语种完全对称平衡的两列网格 -->
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; align-items: start;">
                        <div>
                            <label class="bindery-label">📂 章节收录范围</label>
                            <select id="bindery-select-scope" class="bindery-select">${categoryOptionsHtml}</select>
                        </div>
                        <div>
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
                                <label class="bindery-label" style="margin:0;">🌍 出版语种与版本规格</label>
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <span id="bindery-matrix-toggle-btn" style="display:none; cursor:pointer; color:#10b981; font-size:0.65rem; user-select:none; padding:1px 5px; border-radius:4px; background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.25);" onclick="window.toggleAllBinderyMatrixLangs()" title="点击全选/反选">反选</span>
                                    <span id="bindery-lang-hint-badge" class="bindery-badge" style="font-size:0.65rem;">单语言版</span>
                                </div>
                            </div>
                            <select id="bindery-select-lang" class="bindery-select" onchange="window.onBinderyLangModeChange(this.value)">${langOptionsHtml}</select>
                            
                            <!-- 轻巧内嵌的语种勾选行 (独占整行宽度，杜绝多语种拥挤换行) -->
                            <div id="bindery-matrix-chips-row" style="display:none; margin-top:6px; align-items:center; gap:4px; flex-wrap:wrap;">
                                ${matrixChipsHtml}
                            </div>
                        </div>
                    </div>

                    <!-- 封面装帧区块 -->
                    <div style="display: flex; gap: 14px; background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border, rgba(255,255,255,0.1)); border-radius: 10px; padding: 10px 12px; align-items: center;">
                        <div id="bindery-cover-preview-box" style="width: 72px; height: 110px; border-radius: 6px; overflow: hidden; background: #0b1219; border: 1px solid rgba(16,185,129,0.35); flex-shrink: 0; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 16px rgba(0,0,0,0.45); position:relative;">
                            <img id="bindery-cover-img" style="width: 100%; height: 100%; object-fit: cover; display: block;" alt="Cover" />
                            <div id="bindery-cover-none-ph" style="display:none; text-align:center; color:var(--text-dim, #94a3b8); font-size:0.75rem; line-height:1.4;">📰<br/><span style="font-size:0.62rem; color:#38bdf8;">纯净免封</span></div>
                        </div>
                        <div style="flex: 1; display: flex; flex-direction: column; gap: 7px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <label class="bindery-label" style="margin: 0;">🖼️ 出版装帧封面策略</label>
                                <span id="bindery-cover-badge" class="bindery-badge" style="font-size: 0.65rem;">✨ 智能排版</span>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                                <select id="bindery-select-cover-mode" class="bindery-select" onchange="window.refreshCoverPreview()">
                                    <option value="none" ${isSingle ? 'selected' : ''}>📰 纯净正文流 (免大封面)</option>
                                    <option value="auto" ${!isSingle ? 'selected' : ''}>✨ 智能自愈 (文库/排版)</option>
                                    <option value="generated">🎨 艺术装帧大封面</option>
                                </select>
                                <select id="bindery-select-cover-style" class="bindery-select" onchange="window.refreshCoverPreview()">
                                    <option value="dark_emerald" selected>🌿 黑曜翡翠 (Emerald)</option>
                                    <option value="classic_navy">🌌 藏青午夜 (Navy)</option>
                                    <option value="obsidian_gold">👑 黑金雅致 (Gold)</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div>
                        <label class="bindery-label">🖨️ 装订驱动与格式</label>
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px;">
                            <div class="bindery-driver-card active" id="btn-driver-epub" onclick="window.selectBinderyFormat('epub')" style="padding: 7px 10px;">
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <span style="font-size:1.1rem;">📖</span>
                                    <div><div class="bindery-driver-title">EPUB 3.0</div><div class="bindery-driver-desc">流式重排研读</div></div>
                                </div>
                                <span style="font-size:0.68rem; color:#10b981; font-weight:700;">● 推荐</span>
                            </div>
                            <div class="bindery-driver-card" id="btn-driver-webbook" onclick="window.selectBinderyFormat('webbook')" style="padding: 7px 10px;">
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <span style="font-size:1.1rem;">🌐</span>
                                    <div><div class="bindery-driver-title">WebBook</div><div class="bindery-driver-desc">离线独立网页</div></div>
                                </div>
                                <span style="font-size:0.68rem; color:#38bdf8; font-weight:700;">● 独立</span>
                            </div>
                            <div class="bindery-driver-card" id="btn-driver-pdf" onclick="window.selectBinderyFormat('pdf')" style="padding: 7px 10px;">
                                <div style="display:flex; align-items:center; gap:6px;">
                                    <span style="font-size:1.1rem;">📄</span>
                                    <div><div class="bindery-driver-title">PDF 印本</div><div class="bindery-driver-desc">固定版式印刷</div></div>
                                </div>
                                <span style="font-size:0.68rem; color:#a855f7; font-weight:700;">● 印本</span>
                            </div>
                        </div>
                    </div>

                    <div id="bindery-status-area" style="display:none; padding:10px 14px; border-radius:8px; font-size:0.82rem; line-height:1.4;"></div>

                    <div class="bindery-footer">
                        <button id="btn-bindery-cancel" class="secondary-btn" onclick="window.closeBinderyModal()" style="padding: 7px 18px; font-size: 0.85rem; border-radius: 8px; cursor:pointer;">取消</button>
                        <button id="btn-execute-binding" class="primary-btn glow-btn" onclick="window.executeBookBinding()" style="padding: 7px 22px; font-size: 0.85rem; border-radius: 8px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color:#fff; border:none; font-weight:600; cursor:pointer; display:flex; align-items:center; gap:6px;">
                            <span>🚀 立即装订 (${esc(sourceLangLabel)})</span>
                        </button>
                    </div>
                </div>

                <div id="bindery-panel-shelf" style="display: none; flex-direction: column; gap: 10px;">
                    <div id="bindery-shelf-list"></div>
                    <div style="display: flex; justify-content: flex-end; margin-top: 6px; border-top: 1px solid var(--glass-border, rgba(255,255,255,0.08)); padding-top: 14px;">
                        <button class="secondary-btn" onclick="window.closeBinderyModal()" style="padding: 7px 18px; font-size: 0.85rem; border-radius: 8px; cursor:pointer;">关闭</button>
                    </div>
                </div>
            </div>
        `;
    }

    function buildSuccessStatusHtml(result, formattedSize) {
        const isWb = result.format === 'webbook' || (result.filename && result.filename.endsWith('.html'));
        const pvUrl = result.preview_url || (isWb ? `/api/bindery/view?file=${encodeURIComponent(result.filename)}` : null);
        const pvBtn = pvUrl
            ? `<a href="${pvUrl}" target="_blank" rel="noopener noreferrer" class="primary-btn glow-btn" title="在线翻阅 (WebBook)" style="padding:4px 8px; font-size:0.85rem; text-decoration:none; display:inline-flex; align-items:center; justify-content:center; border-radius:6px; background:#0284c7; color:#fff; flex-shrink:0;">👁️</a>`
            : '';

        if (result.mode === 'matrix' && Array.isArray(result.results)) {
            const itemsHtml = result.results.map(r => {
                const sz = formatSize(r.size_bytes || 0);
                const itemWb = r.format === 'webbook' || (r.filename && r.filename.endsWith('.html'));
                const itemPv = r.preview_url || (itemWb ? `/api/bindery/view?file=${encodeURIComponent(r.filename)}` : null);
                const itemPvBtn = itemPv ? `<a href="${itemPv}" target="_blank" rel="noopener noreferrer" class="primary-btn glow-btn" title="在线翻阅 (WebBook)" style="padding:2px 6px; font-size:0.75rem; text-decoration:none; border-radius:4px; background:#0284c7; color:#fff; display:inline-flex; align-items:center; justify-content:center; flex-shrink:0;">👁️</a>` : '';
                const chNum = (r.chapter_count !== undefined && r.chapter_count !== null) ? `${r.chapter_count}篇 / ` : '';
                return `<div style="display:flex; justify-content:space-between; align-items:center; padding:5px 8px; background:rgba(255,255,255,0.04); border-radius:6px; margin-top:4px; font-size:0.75rem; gap:8px;">
                    <span style="font-family:var(--font-mono, monospace); color:var(--text-main, #fff); min-width:0; flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${esc(r.filename)}"><strong>[${esc(r.language.toUpperCase())}]</strong> ${esc(r.filename)} (${chNum}${sz})</span>
                    <div style="display:flex; align-items:center; gap:6px; flex-shrink:0;">${itemPvBtn}<button type="button" onclick="window.revealBookInFolder('${esc(r.filename)}')" class="secondary-btn" title="在系统文件夹中显示" style="padding:2px 6px; font-size:0.75rem; border-radius:4px; color:var(--text-bright, #fff); border:1px solid var(--glass-border, rgba(255,255,255,0.12)); cursor:pointer; background:rgba(255,255,255,0.06);">📂</button><a href="${r.download_url}" download="${esc(r.filename)}" class="primary-btn" title="下载电子书" style="padding:2px 6px; font-size:0.75rem; text-decoration:none; border-radius:4px; background:#10b981; color:#fff; display:inline-flex; align-items:center; justify-content:center; flex-shrink:0;">⬇️</a></div>
                </div>`;
            }).join('');

            return `<div style="display:flex; flex-direction:column; gap:6px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div><strong>🎉 多语言电子书制作完成！</strong> 共并发生成 <strong>${result.total_built || result.results.length}</strong> 本电子书</div>
                    <button onclick="window.switchBinderyTab('shelf')" style="background:rgba(56,189,248,0.15); color:#38bdf8; border:1px solid rgba(56,189,248,0.3); border-radius:6px; padding:3px 8px; font-size:0.72rem; cursor:pointer;">📚 查看书架</button>
                </div>
                <div style="max-height:120px; overflow-y:auto;">${itemsHtml}</div>
            </div>`;
        }

        const countText = (result.chapter_count !== undefined && result.chapter_count !== null)
            ? `已收录 <strong>${result.chapter_count}</strong> 篇章节`
            : `已完成编排封装`;

        return `<div style="display:flex; justify-content:space-between; align-items:center; gap:8px;">
            <div style="min-width:0; flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"><strong>🎉 装订完成！</strong> ${countText} (${formattedSize})</div>
            <div style="display:flex; align-items:center; gap:6px; flex-shrink:0;">
                ${pvBtn}
                <button type="button" onclick="window.revealBookInFolder('${esc(result.filename)}')" class="secondary-btn" title="在系统文件夹中显示" style="padding:4px 8px; font-size:0.85rem; border-radius:6px; color:var(--text-bright, #fff); border:1px solid var(--glass-border, rgba(255,255,255,0.14)); cursor:pointer; background:rgba(255,255,255,0.06); display:inline-flex; align-items:center; justify-content:center;">📂</button>
                <a href="${result.download_url}" download="${esc(result.filename)}" class="primary-btn" title="下载出版物" style="padding:4px 8px; font-size:0.85rem; text-decoration:none; display:inline-flex; align-items:center; justify-content:center; border-radius:6px; background:#10b981; color:#fff; flex-shrink:0;">⬇️</a>
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
