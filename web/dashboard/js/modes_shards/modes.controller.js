/**
 * 📋 [V57.0] Illacme Plenipes Publishing Modes - Controller Shard
 * 职责：出版模式切换、SEO 策略联动与算力就绪感知控制器。
 */

(function () {
    'use strict';

    window.checkAIReadiness = () => {
        const nodes = window.settingsData?.translation?.compute_nodes || {};
        return Object.keys(nodes).length > 0;
    };

    window.switchPublishingMode = async (mode) => {
        if (typeof window.checkSettingsDirtyAndConfirm === 'function') {
            const proceed = await window.checkSettingsDirtyAndConfirm();
            if (!proceed) {
                if (typeof renderSettingsCategory === 'function') renderSettingsCategory('modes');
                return;
            }
        }

        const enableAi = window.settingsData.translation?.enable_ai !== false;

        if (mode !== 'basic' && !enableAi) {
            if (typeof addAudit === 'function') addAudit(`🛑 无法切换至 ${mode.toUpperCase()} 模式：未开启 AI 算力总控`, "error");
            if (typeof showNotification === 'function') showNotification(`🔒 无法选择 ${mode.toUpperCase()}：未开启 AI 算力总控`, 'error');
            return;
        }

        if (mode !== 'basic' && typeof checkAIReadiness === 'function' && !checkAIReadiness()) {
            if (typeof addAudit === 'function') addAudit(`🛑 无法切换至 ${mode.toUpperCase()} 模式：未配置 AI 算力`, "error");
            return;
        }
        const defaultStrategies = {
            'global': 'ai_sync',
            'enhanced': 'ai_alignment',
            'basic': 'heuristic'
        };

        // 🚀 [V74.96] 记忆机制：优先从 localStorage 提取用户上一次在该模式选定的策略
        const lastStrategyKey = `illacme_plenipes_last_strategy_for_${mode}`;
        const defaultStrategy = localStorage.getItem(lastStrategyKey) || defaultStrategies[mode] || 'heuristic';

        // 🚀 [模式与多语言联动] 切换至 global 自动开启多语言矩阵，切换至 enhanced/basic 自动关闭多语言矩阵
        const updatePayload = {
            'governance.publishing_mode': mode,
            'governance.seo_strategy': defaultStrategy
        };
        if (mode === 'global') {
            updatePayload['i18n_settings.enabled'] = true;
        } else if (mode === 'enhanced') {
            updatePayload['i18n_settings.enabled'] = false;
        }

        if (typeof addAudit === 'function') addAudit(`📋 正在切换出版模式至: ${mode.toUpperCase()}...`);
        const res = await apiFetch('/api/config/update', {
            method: 'POST',
            body: JSON.stringify(updatePayload)
        });
        if (res && res.status === 'success') {
            localStorage.setItem(lastStrategyKey, defaultStrategy);

            window.settingsData = { ...window.settingsData, ...res.active_config };
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('modes');

            // 🚀 刷新左侧治理边栏感知状态
            if (typeof window.refreshGovernanceContext === 'function') {
                window.refreshGovernanceContext();
            }

            // 🚀 交互自愈：切换模式后自动平滑滚动置顶
            const container = document.querySelector('.view-panel.active .tab-content-area');
            if (container) {
                container.scrollTo({ top: 0, behavior: 'smooth' });
            }

            const modeTitles = {
                'global': '全球多语言分发',
                'enhanced': '智能母语增强',
                'basic': '基础物理出版'
            };
            const currentTitle = modeTitles[mode] || mode.toUpperCase();

            if (typeof addAudit === 'function') addAudit(`✅ 出版模式已切换至 [${currentTitle}]，启用 [${defaultStrategy}] 策略`, "success");
            if (typeof showNotification === 'function') {
                showNotification(`✅ 出版模式已切换至「${currentTitle}」(建议下次同步时清除缓存)`, 'success');
            }
        }
    };

    window.switchSeoStrategy = async (mode, strategy) => {
        if (typeof window.checkSettingsDirtyAndConfirm === 'function') {
            const proceed = await window.checkSettingsDirtyAndConfirm();
            if (!proceed) {
                if (typeof renderSettingsCategory === 'function') renderSettingsCategory('modes');
                return;
            }
        }

        const enableAi = window.settingsData.translation?.enable_ai !== false;
        const i18nEnabled = window.settingsData.i18n_settings?.enabled !== false;

        if (mode === 'global' && (!enableAi || !i18nEnabled)) {
            return;
        }
        if (mode === 'enhanced' && !enableAi) {
            return;
        }

        if (typeof addAudit === 'function') addAudit(`🎯 正在切换 SEO 策略至: ${strategy}...`);
        const res = await apiFetch('/api/config/update', {
            method: 'POST',
            body: JSON.stringify({ 'governance.publishing_mode': mode, 'governance.seo_strategy': strategy })
        });
        if (res && res.status === 'success') {
            const lastStrategyKey = `illacme_plenipes_last_strategy_for_${mode}`;
            localStorage.setItem(lastStrategyKey, strategy);

            window.settingsData = { ...window.settingsData, ...res.active_config };
            if (typeof renderSettingsCategory === 'function') renderSettingsCategory('modes');

            if (typeof window.refreshGovernanceContext === 'function') {
                window.refreshGovernanceContext();
            }

            const container = document.querySelector('.view-panel.active .tab-content-area');
            if (container) {
                container.scrollTo({ top: 0, behavior: 'smooth' });
            }

            if (typeof addAudit === 'function') addAudit(`✅ SEO 策略已切换至 [${strategy}]`, "success");
        }
    };

})();
