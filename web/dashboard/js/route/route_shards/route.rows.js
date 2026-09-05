/**
 * 🛣️ [V100.9] Illacme Plenipes Route Matrix - Rows Management & Ordering Shard
 * 职责：矩阵行增删、上移/下移排序与动画移除。
 */

(function () {
    window.moveRouteMatrixRow = (btn, direction) => {
        const isLicensed = window.settingsData?._is_licensed || false;
        if (!isLicensed) return;

        const row = btn.closest('.route-item');
        if (!row) return;

        const tbody = document.getElementById('route-matrix-body');
        if (!tbody) return;

        if (direction === 'up') {
            const prev = row.previousElementSibling;
            if (prev && prev.classList.contains('route-item')) {
                tbody.insertBefore(row, prev);
            }
        } else if (direction === 'down') {
            const next = row.nextElementSibling;
            if (next && next.classList.contains('route-item')) {
                tbody.insertBefore(next, row);
            }
        }

        window.refreshRouteMatrixOrderButtons();
        if (typeof window.syncRouteMatrixToSettings === 'function') {
            window.syncRouteMatrixToSettings();
        }
    };

    window.refreshRouteMatrixOrderButtons = () => {
        const rows = document.querySelectorAll('#route-matrix-body .route-item');
        const total = rows.length;
        rows.forEach((r, idx) => {
            r.setAttribute('data-idx', idx);
            const upBtn = r.querySelector('.move-up-btn');
            const downBtn = r.querySelector('.move-down-btn');
            if (upBtn) {
                upBtn.disabled = (idx === 0);
                upBtn.style.color = (idx === 0) ? 'rgba(255,255,255,0.2)' : 'var(--text-dim)';
                upBtn.style.cursor = (idx === 0) ? 'default' : 'pointer';
            }
            if (downBtn) {
                downBtn.disabled = (idx === total - 1);
                downBtn.style.color = (idx === total - 1) ? 'rgba(255,255,255,0.2)' : 'var(--text-dim)';
                downBtn.style.cursor = (idx === total - 1) ? 'default' : 'pointer';
            }
        });
    };

    window.addRouteMatrixRow = () => {
        const isLicensed = window.settingsData?._is_licensed || false;
        if (!isLicensed) {
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: '👑 专属版本权益提示',
                    html: '高级频道路由与专属翻译风格矩阵为 <b>Illacme Plenipes 专属授权版 (PRO)</b> 的特权功能。<br><br>系统当前已为您自动回落至无缝的物理路径映射模式。',
                    icon: 'info',
                    background: 'rgba(20, 15, 25, 0.95)',
                    color: '#fff',
                    confirmButtonColor: 'var(--accent-primary, #a34cff)',
                    confirmButtonText: '我知道了'
                });
            } else {
                alert('本功能为专属版专属功能，当前已自动降级至物理路由模式。');
            }
            return;
        }

        const themeSlots = window.settingsData?._theme_slots || {};
        const hasSlots = Object.keys(themeSlots).length > 0;

        const tbody = document.getElementById('route-matrix-body');
        if (!tbody) return;
        const emptyState = tbody.querySelector('.empty-state');
        if (emptyState) emptyState.remove();

        const newIdx = tbody.querySelectorAll('.route-item').length;

        const rowHtml = `
            <div class="matrix-row route-item" data-idx="${newIdx}" style="display: grid; grid-template-columns: 36px 1.4fr 1.0fr 1.45fr 1.5fr 0.95fr 42px 36px; gap: 8px; padding: 8px 6px; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.03); transition: background 0.2s;">
                <!-- 0. 排序控制器 -->
                <div class="order-controls" style="display: flex; flex-direction: column; gap: 2px; align-items: center; justify-content: center;">
                    <button type="button" class="mini-btn move-up-btn" onclick="window.moveRouteMatrixRow(this, 'up')" style="padding: 0; width: 22px; height: 13px; font-size: 0.55rem; line-height: 1; border-radius: 3px; background: rgba(255,255,255,0.05); color: var(--text-dim); border: 1px solid rgba(255,255,255,0.08); cursor: pointer;" title="上移">▲</button>
                    <button type="button" class="mini-btn move-down-btn" onclick="window.moveRouteMatrixRow(this, 'down')" disabled style="padding: 0; width: 22px; height: 13px; font-size: 0.55rem; line-height: 1; border-radius: 3px; background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.08); cursor: default;" title="下移">▼</button>
                </div>
                <!-- 1. 文库目录 -->
                <div>
                    ${window.buildSourcePickerHtml ? window.buildSourcePickerHtml('', true, false, 'docs') : ''}
                </div>
                <!-- 2. 网页路径 -->
                <div>
                    <input type="text" class="setting-input prefix-input" value="" placeholder="例如: /docs/" title="${window.getLivePathTooltip ? window.getLivePathTooltip({ source: '', prefix: '' }) : ''}" style="width: 100%; color: var(--accent-secondary); font-family: monospace; font-size: 0.74rem; padding: 5px 6px;" onchange="syncRouteMatrixToSettings()" oninput="syncRouteMatrixToSettings(); window.updateAllLivePathBadges();">
                </div>
                <!-- 3. 网页模板 -->
                <div>
                    ${(() => {
                const formatSlotDisplay = (k, v) => {
                    const rawLabel = (v && v.label) ? v.label : k;
                    if (k === 'showcase') return `🎨 展示中心 (show)`;
                    if (rawLabel.includes('(')) return rawLabel;
                    const icons = { docs: '📚', blog: '📰', pages: '📄', page: '📄', showcase: '🎨', static: '📦' };
                    const icon = icons[k] || '🧩';
                    return `${icon} ${rawLabel} (${k})`;
                };
                let html = '';
                if (hasSlots) {
                    html += `<select class="setting-input slot-select" style="width: 100%; font-size: 0.74rem; padding: 5px 6px;" onchange="if(this.value === '_custom') { this.style.display='none'; this.nextElementSibling.style.display='block'; this.nextElementSibling.value=''; this.nextElementSibling.focus(); } else { this.nextElementSibling.value=this.value; } const _row = this.closest('.matrix-row'); const _srcInput = _row?.querySelector('.source-input'); const _dl = _srcInput ? document.getElementById(_srcInput.getAttribute('list')) : null; if(_dl && window.buildSourceDatalistOptions) { _dl.innerHTML = window.buildSourceDatalistOptions(this.value, _srcInput.value); } syncRouteMatrixToSettings(); if(window.updateAllLivePathBadges) window.updateAllLivePathBadges();">`;
                    Object.entries(themeSlots).forEach(([k, v]) => {
                        html += `<option value="${k}">${formatSlotDisplay(k, v)}</option>`;
                    });
                    html += `<option value="_custom">✏️ 自定义... </option>`;
                    html += `</select>`;
                }
                html += `<input type="text" class="setting-input slot-input" value="docs" placeholder="例如: docs" style="width: 100%; font-size: 0.74rem; padding: 5px 6px; display: ${!hasSlots ? 'block' : 'none'};" onchange="const _row = this.closest('.matrix-row'); const _srcInput = _row?.querySelector('.source-input'); const _dl = _srcInput ? document.getElementById(_srcInput.getAttribute('list')) : null; if(_dl && window.buildSourceDatalistOptions) { _dl.innerHTML = window.buildSourceDatalistOptions(this.value, _srcInput.value); } syncRouteMatrixToSettings(); if(window.updateAllLivePathBadges) window.updateAllLivePathBadges();" oninput="syncRouteMatrixToSettings()">`;
                return html;
            })()}
                </div>
                <!-- 4. 顶栏导航 -->
                <div style="display: flex; gap: 4px; align-items: center; position: relative;">
                    <button type="button" class="mini-btn icon-picker-btn" onclick="window.toggleIconPicker(this, event)" style="width: 30px; height: 26px; padding: 0; font-size: 0.92rem; border-radius: 6px; background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 255, 0.25); cursor: pointer; flex-shrink: 0; display: flex; align-items: center; justify-content: center; transition: all 0.2s;" title="点击弹出选择常见图标">
                        <span class="icon-preview">📚</span>
                    </button>
                    <input type="hidden" class="nav-icon-input" value="📚">
                    <input type="text" class="setting-input nav-label-input" value="" placeholder="显示名称" style="flex: 1; min-width: 0; font-size: 0.74rem; padding: 5px 6px;" onchange="syncRouteMatrixToSettings()" oninput="syncRouteMatrixToSettings()">
                    
                    <button type="button" class="mini-btn nav-i18n-btn" onclick="window.toggleNavI18nModal(this, event)" style="padding: 2px 6px; height: 26px; font-size: 0.7rem; border-radius: 6px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: var(--text-dim); cursor: pointer; flex-shrink: 0; display: flex; align-items: center; gap: 3px;" title="配置多语种导航名称">
                        <span>🌐</span>
                        <span class="i18n-count-badge" style="font-size: 0.65rem; font-weight: 700;">+</span>
                    </button>
                    <input type="hidden" class="nav-i18n-input" value="{}">
                </div>
                <!-- 5. 译文风格 -->
                <div>
                    ${window.buildTranslationStyleSelectHtml ? window.buildTranslationStyleSelectHtml('', true, false) : `
                        <select class="setting-input style-input" style="width: 100%; font-size: 0.74rem; padding: 5px 6px;" onchange="syncRouteMatrixToSettings()">
                            <option value="">继承全局默认</option>
                        </select>
                    `}
                </div>
                <!-- 6. 顶栏展示 -->
                <div style="text-align: center;">
                    <input type="checkbox" class="nav-show-input" checked onchange="syncRouteMatrixToSettings()" style="cursor: pointer; transform: scale(1.1); accent-color: var(--accent-secondary, #00f2fe);" title="是否在网站顶栏导航显示" />
                </div>
                <!-- 7. 操作 -->
                <div style="text-align: center;">
                    <button class="mini-btn" onclick="removeRouteMatrixRow(this)" style="background: rgba(255,50,50,0.1); border: 1px solid rgba(255,50,50,0.3); color: #ff5555; height: 26px; width: 26px; padding: 0; border-radius: 6px; cursor: pointer; transition: all 0.2s; font-size: 0.85rem;" title="删除此规则">×</button>
                </div>
            </div>
        `;

        tbody.insertAdjacentHTML('beforeend', rowHtml);

        window.refreshRouteMatrixOrderButtons();

        const container = document.querySelector('#view-settings .tab-content-area');
        if (container) {
            container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
        }

        if (typeof window.syncRouteMatrixToSettings === 'function') {
            window.syncRouteMatrixToSettings();
        }
        if (typeof window.updateAllLivePathBadges === 'function') {
            window.updateAllLivePathBadges();
        }
    };

    window.removeRouteMatrixRow = (btn) => {
        const isLicensed = window.settingsData?._is_licensed || false;
        if (!isLicensed) {
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: '👑 专属版本权益提示',
                    html: '高级频道路由与专属翻译风格矩阵为 <b>Illacme Plenipes 专属授权版 (PRO)</b> 的特权功能。<br><br>系统当前已为您自动回落至无缝的物理路径映射模式。',
                    icon: 'info',
                    background: 'rgba(20, 15, 25, 0.95)',
                    color: '#fff',
                    confirmButtonColor: 'var(--accent-primary, #a34cff)',
                    confirmButtonText: '我知道了'
                });
            } else {
                alert('本功能为专属版专属功能，当前已自动降级至物理路由模式。');
            }
            return;
        }

        const row = btn.closest('.route-item');
        if (row) {
            row.style.opacity = '0';
            row.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                row.remove();

                const tbody = document.getElementById('route-matrix-body');
                if (tbody && tbody.querySelectorAll('.route-item').length === 0) {
                    tbody.innerHTML = `
                        <div class="empty-state" style="padding: 40px; text-align: center; color: var(--text-dim);">
                            暂无路由与导航策略。您的全部文件目前均按照原始物理路径进行映射发布。
                        </div>
                    `;
                } else {
                    window.refreshRouteMatrixOrderButtons();
                }
                if (typeof window.syncRouteMatrixToSettings === 'function') {
                    window.syncRouteMatrixToSettings();
                }
            }, 200);
        }
    };
})();
