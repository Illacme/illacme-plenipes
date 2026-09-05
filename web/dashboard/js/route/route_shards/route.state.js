/**
 * 🛣️ [V100.9] Illacme Plenipes Route Matrix - State & Settings Sync Shard
 * 职责：矩阵表格 DOM 状态抽取、数据序列化与配置脏检查触发。
 */

(function () {
    window.syncRouteMatrixToSettings = () => {
        const isLicensed = window.settingsData?._is_licensed || false;
        if (!isLicensed) return;

        const routeItems = document.querySelectorAll('.route-item');
        const newRouteMatrix = [];

        routeItems.forEach((item, idx) => {
            const sourceInput = item.querySelector('.source-input');
            const prefixInput = item.querySelector('.prefix-input');
            const extUrlInput = item.querySelector('.ext-url-input');
            const slotInput = item.querySelector('.slot-input');
            const styleInput = item.querySelector('.style-input');
            const navLabelInput = item.querySelector('.nav-label-input');
            const navIconInput = item.querySelector('.nav-icon-input');
            const navShowInput = item.querySelector('.nav-show-input');
            const navI18nInput = item.querySelector('.nav-i18n-input');

            const source = sourceInput ? sourceInput.value.trim() : "";
            const prefix = prefixInput ? prefixInput.value.trim() : "";
            const extUrl = extUrlInput ? extUrlInput.value.trim() : "";
            const target_slot = slotInput ? slotInput.value.trim() : "docs";
            const style = styleInput ? styleInput.value : "";
            const nav_label = navLabelInput ? navLabelInput.value.trim() : "";
            const nav_icon = navIconInput ? navIconInput.value.trim() : "";
            const show_in_nav = navShowInput ? navShowInput.checked : true;

            let nav_label_i18n = null;
            if (navI18nInput && navI18nInput.value) {
                try {
                    const parsed = JSON.parse(navI18nInput.value);
                    if (parsed && typeof parsed === 'object' && Object.keys(parsed).length > 0) {
                        nav_label_i18n = parsed;
                    }
                } catch (e) {}
            }

            if (extUrl) {
                newRouteMatrix.push({
                    source: "",
                    prefix: "",
                    target_slot: "external",
                    external_url: extUrl,
                    nav_label: nav_label || "External Link",
                    nav_label_i18n: nav_label_i18n,
                    nav_icon: nav_icon || "🌐",
                    show_in_nav: show_in_nav,
                    nav_position: "right",
                    nav_order: idx,
                    style: null
                });
                return;
            }

            // Skip empty sources
            if (!source) return;

            newRouteMatrix.push({
                source: source,
                prefix: prefix || "",
                target_slot: target_slot || "docs",
                nav_label: nav_label || source,
                nav_label_i18n: nav_label_i18n,
                nav_icon: nav_icon || "📚",
                show_in_nav: show_in_nav,
                nav_position: "left",
                nav_order: idx,
                style: style || null
            });
        });

        if (window.settingsData) {
            window.settingsData.route_matrix = newRouteMatrix;
        }

        // 🚀 [V106.0] 实时执行路径冲突前置检测与视觉标记
        if (typeof window.detectRouteMatrixConflicts === 'function') {
            const conflicts = window.detectRouteMatrixConflicts(newRouteMatrix);
            window.highlightRouteMatrixConflicts(conflicts);
        }

        if (typeof window.checkSettingsDirty === 'function') {
            window.checkSettingsDirty();
        }
    };

    /**
     * 🚨 [V106.0] 路径冲突分析纯函数 (返回冲突行索引及冲突描述)
     */
    window.detectRouteMatrixConflicts = (routes) => {
        const conflicts = []; // { index: number, reason: string, type: 'duplicate' | 'shadow' }
        if (!routes || !Array.isArray(routes) || routes.length <= 1) return conflicts;

        const prefixMap = new Map(); // normalizedPrefix -> [index]

        routes.forEach((r, idx) => {
            if (r.target_slot === 'external' || r.external_url) return;
            const rawPrefix = (r.prefix || r.source || 'docs').trim().replace(/\\/g, '/');
            const normPrefix = rawPrefix.toLowerCase().replace(/^\/+|\/+$/g, '');

            if (!prefixMap.has(normPrefix)) {
                prefixMap.set(normPrefix, []);
            }
            prefixMap.get(normPrefix).push(idx);
        });

        prefixMap.forEach((indices, normPrefix) => {
            if (indices.length > 1) {
                const displayPath = normPrefix ? `/${normPrefix}/` : '/ (根路径)';
                indices.forEach(idx => {
                    const otherIndices = indices.filter(i => i !== idx).map(i => `#${i + 1}`).join(', ');
                    conflicts.push({
                        index: idx,
                        reason: `网页路径【${displayPath}】与第 ${otherIndices} 项重复，将导致构建产物互相覆盖`,
                        type: 'duplicate'
                    });
                });
            }
        });

        return conflicts;
    };

    /**
     * 🎨 [V106.0] 将冲突状态渲染到表格对应行的输入框中
     */
    window.highlightRouteMatrixConflicts = (conflicts) => {
        const rows = document.querySelectorAll('#route-matrix-body .route-item');
        if (!rows || rows.length === 0) return;

        // 先清理所有旧的高亮与气泡
        rows.forEach(r => {
            const prefixInput = r.querySelector('.prefix-input');
            if (prefixInput) {
                prefixInput.classList.remove('input-conflict-warning');
                prefixInput.style.borderColor = '';
                prefixInput.style.boxShadow = '';
            }
            const oldBubble = r.querySelector('.route-conflict-bubble');
            if (oldBubble) oldBubble.remove();
        });

        if (!conflicts || conflicts.length === 0) return;

        conflicts.forEach(c => {
            const targetRow = rows[c.index];
            if (!targetRow) return;

            const prefixInput = targetRow.querySelector('.prefix-input');
            if (prefixInput) {
                prefixInput.classList.add('input-conflict-warning');
                prefixInput.style.borderColor = 'rgba(255, 77, 79, 0.8)';
                prefixInput.style.boxShadow = '0 0 8px rgba(255, 77, 79, 0.35)';

                // 挂载行内警告气泡
                const cell = prefixInput.parentElement;
                if (cell && !cell.querySelector('.route-conflict-bubble')) {
                    const bubble = document.createElement('div');
                    bubble.className = 'route-conflict-bubble';
                    bubble.style.cssText = 'display: flex; align-items: center; gap: 4px; font-size: 0.65rem; color: #ff4d4f; background: rgba(255, 77, 79, 0.1); border: 1px solid rgba(255, 77, 79, 0.3); border-radius: 4px; padding: 2px 6px; margin-top: 3px; line-height: 1.3;';
                    bubble.innerHTML = `<span>⚠️</span> <span>${c.reason}</span>`;
                    cell.appendChild(bubble);
                }
            }
        });
    };

    /**
     * 🛡️ [V106.0] 暴露给全局保存前置调用的阻断守卫
     */
    window.validateRouteMatrixBeforeSave = () => {
        const routes = window.settingsData?.route_matrix || [];
        const conflicts = window.detectRouteMatrixConflicts ? window.detectRouteMatrixConflicts(routes) : [];
        if (conflicts && conflicts.length > 0) {
            const first = conflicts[0];
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: '🚨 发现频道路由冲突',
                    html: `在第 <b>${first.index + 1}</b> 行中：<br>${first.reason}<br><br>为防止静态站点构建相互覆盖并产生死链，请先修正重复的网页路径。`,
                    icon: 'warning',
                    background: 'rgba(20, 15, 25, 0.95)',
                    color: '#fff',
                    confirmButtonColor: '#ff4d4f',
                    confirmButtonText: '立即修正'
                });
            } else if (typeof showToast === 'function') {
                showToast(`🚨 路由冲突：${first.reason}`, 'error');
            }
            return false;
        }
        return true;
    };
})();
