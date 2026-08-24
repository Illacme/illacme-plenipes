/**
 * 🛣️ [V100.9] Illacme Plenipes Route Matrix - External Links & Recommendation Shard
 * 职责：外部直链导航菜单行添加与智能推荐矩阵策略应用。
 */

(function () {
    window.addExternalNavRow = () => {
        const isLicensed = window.settingsData?._is_licensed || false;
        if (!isLicensed) {
            if (typeof Swal !== 'undefined') {
                Swal.fire({
                    title: '👑 专属版本权益提示',
                    html: '高级频道路由与专属全景导航为 <b>Illacme Plenipes 专属授权版 (PRO)</b> 的特权功能。',
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

        const tbody = document.getElementById('route-matrix-body');
        if (!tbody) return;
        const emptyState = tbody.querySelector('.empty-state');
        if (emptyState) emptyState.remove();

        const newIdx = tbody.querySelectorAll('.route-item').length;
        
        const rowHtml = `
            <div class="matrix-row route-item" data-idx="${newIdx}" style="display: grid; grid-template-columns: 36px 1.1fr 1fr 1fr 1.4fr 0.9fr 46px 36px; gap: 8px; padding: 8px 4px; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.03); transition: background 0.2s;">
                <!-- 0. 排序控制器 -->
                <div class="order-controls" style="display: flex; flex-direction: column; gap: 2px; align-items: center; justify-content: center;">
                    <button type="button" class="mini-btn move-up-btn" onclick="window.moveRouteMatrixRow(this, 'up')" style="padding: 0; width: 22px; height: 13px; font-size: 0.55rem; line-height: 1; border-radius: 3px; background: rgba(255,255,255,0.05); color: var(--text-dim); border: 1px solid rgba(255,255,255,0.08); cursor: pointer;" title="上移">▲</button>
                    <button type="button" class="mini-btn move-down-btn" onclick="window.moveRouteMatrixRow(this, 'down')" disabled style="padding: 0; width: 22px; height: 13px; font-size: 0.55rem; line-height: 1; border-radius: 3px; background: rgba(255,255,255,0.05); color: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.08); cursor: default;" title="下移">▼</button>
                </div>
                <!-- 1. 文库目录 -->
                <div>
                    <input type="text" class="setting-input source-input" value="🌐 外部直链" disabled style="width: 100%; font-size: 0.74rem; padding: 5px 6px; opacity: 0.7;">
                </div>
                <!-- 2. 网页路径 -->
                <div>
                    <input type="text" class="setting-input ext-url-input" value="https://" placeholder="https://..." style="width: 100%; color: var(--neon-cyan, #00f2fe); font-family: monospace; font-size: 0.74rem; padding: 5px 6px;" onchange="syncRouteMatrixToSettings()" oninput="syncRouteMatrixToSettings()">
                </div>
                <!-- 3. 网页模板 -->
                <div>
                    <span style="font-size: 0.72rem; color: var(--text-dim); padding: 4px 8px; background: rgba(255,255,255,0.03); border-radius: 4px; display: inline-block;">🔗 外部直链</span>
                </div>
                <!-- 4. 顶栏导航 -->
                <div style="display: flex; gap: 4px; align-items: center; position: relative;">
                    <button type="button" class="mini-btn icon-picker-btn" onclick="window.toggleIconPicker(this, event)" style="width: 30px; height: 26px; padding: 0; font-size: 0.92rem; border-radius: 6px; background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 255, 0.25); cursor: pointer; flex-shrink: 0; display: flex; align-items: center; justify-content: center; transition: all 0.2s;" title="点击弹出选择常见图标">
                        <span class="icon-preview">🌐</span>
                    </button>
                    <input type="hidden" class="nav-icon-input" value="🌐">
                    <input type="text" class="setting-input nav-label-input" value="GitHub / 官网" placeholder="菜单显示名称" style="flex: 1; min-width: 0; font-size: 0.74rem; padding: 5px 6px;" onchange="syncRouteMatrixToSettings()" oninput="syncRouteMatrixToSettings()">
                    
                    <button type="button" class="mini-btn nav-i18n-btn" onclick="window.toggleNavI18nModal(this, event)" style="padding: 2px 6px; height: 26px; font-size: 0.7rem; border-radius: 6px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: var(--text-dim); cursor: pointer; flex-shrink: 0; display: flex; align-items: center; gap: 3px;" title="配置多语种导航名称">
                        <span>🌐</span>
                        <span class="i18n-count-badge" style="font-size: 0.65rem; font-weight: 700;">+</span>
                    </button>
                    <input type="hidden" class="nav-i18n-input" value="{}">
                </div>
                <!-- 5. 翻译风格 -->
                <div>
                    <select class="setting-input style-input" disabled style="width: 100%; font-size: 0.74rem; padding: 5px 6px; opacity: 0.5;">
                        <option value="">不适用</option>
                    </select>
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
        
        if (typeof window.refreshRouteMatrixOrderButtons === 'function') {
            window.refreshRouteMatrixOrderButtons();
        }
        
        const container = document.querySelector('#view-settings .tab-content-area');
        if (container) {
            container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
        }

        if (typeof window.syncRouteMatrixToSettings === 'function') {
            window.syncRouteMatrixToSettings();
        }
    };

    window.applyRecommendedRouteMatrix = (detectedSubdirs) => {
        const recommended = [];
        
        const defaultMeta = {
            "Docs": { 
                prefix: "docs", slot: "docs", label: "文档中心", icon: "📚",
                i18n: { "en": "Documentation", "ja": "ドキュメント", "fr": "Documentation", "de": "Dokumentation" }
            },
            "Blog": { 
                prefix: "blog", slot: "blog", label: "官方博客", icon: "📰",
                i18n: { "en": "Blog", "ja": "ブログ", "fr": "Blog", "de": "Blog" }
            },
            "Pages": { 
                prefix: "pages", slot: "pages", label: "展示页面", icon: "📄",
                i18n: { "en": "Showcase", "ja": "ショーケース", "fr": "Vitrines", "de": "Seiten" }
            },
        };

        detectedSubdirs.forEach((d, idx) => {
            const meta = defaultMeta[d] || { prefix: d.toLowerCase(), slot: "docs", label: d, icon: "📁", i18n: {} };
            recommended.push({
                source: d,
                prefix: meta.prefix,
                target_slot: meta.slot,
                nav_label: meta.label,
                nav_label_i18n: meta.i18n || {},
                nav_icon: meta.icon,
                show_in_nav: true,
                nav_position: "left",
                nav_order: idx,
                style: null
            });
        });

        if (window.settingsData) {
            window.settingsData.route_matrix = recommended;
        }
        if (typeof window.checkSettingsDirty === 'function') {
            window.checkSettingsDirty();
        }

        // 重新渲染当前 Tab
        if (typeof window.renderDisseminationRoutingCategory === 'function') {
            window.renderDisseminationRoutingCategory();
            setTimeout(() => {
                if (typeof window.switchDisseminationRoutingSubTab === 'function') {
                    window.switchDisseminationRoutingSubTab('route_matrix');
                }
            }, 30);
        }
    };
})();
