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

        if (typeof window.checkSettingsDirty === 'function') {
            window.checkSettingsDirty();
        }
    };
})();
