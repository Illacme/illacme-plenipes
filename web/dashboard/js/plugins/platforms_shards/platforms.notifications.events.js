/**
 * 🔔 [V107.0] Illacme Plenipes Plugins - Notification Lifecycle Events Subscription Shard
 * 职责：商业级消息通知事件订阅中枢卡片渲染、快捷预设方案与实时交互控制器。
 */

// 🚀 [V107.0] 商业级消息通知事件订阅中枢卡片渲染器
window.renderLifecycleEventsSubscription = (id, cfg, defaultEvents = ['SYNC_SUCCESS', 'SYNC_FAIL', 'SYNDICATION_COMPLETED', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_SUCCESS']) => {
    const rawEvents = cfg && cfg.events;
    let events = Array.isArray(rawEvents) ? rawEvents : (rawEvents ? [rawEvents] : defaultEvents);
    // 兼容传统简写
    events = events.map(e => {
        if (e === 'SUCCESS') return 'SYNC_SUCCESS';
        if (e === 'FAIL') return 'SYNC_FAIL';
        if (e === 'START') return 'SYNC_START';
        if (e === 'BLOCKED') return 'COMPLIANCE_BLOCKED';
        return e;
    });
    const hasEvent = (ev) => events.includes(ev);

    const isAlertsOnly = events.length === 5 && ['SYNC_FAIL', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_FAILED'].every(k => events.includes(k));
    const isAllEvents = events.length >= 8 && ['SYNC_SUCCESS', 'SYNC_FAIL', 'SYNC_START', 'SYNDICATION_COMPLETED', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_SUCCESS'].every(k => events.includes(k));
    const isRecommended = !isAlertsOnly && !isAllEvents && events.length === 7 && ['SYNC_SUCCESS', 'SYNC_FAIL', 'SYNDICATION_COMPLETED', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_SUCCESS'].every(k => events.includes(k));
    const activePreset = isAlertsOnly ? 'alerts_only' : (isAllEvents ? 'all' : (isRecommended ? 'recommended' : 'custom'));

    const getEventLabelStyle = (evKey, checked) => {
        if (!checked) return 'background: rgba(255,255,255,0.015); border: 1px solid rgba(255,255,255,0.06);';
        if (evKey === 'COMPLIANCE_BLOCKED') return 'background: rgba(245, 158, 11, 0.06); border: 1px solid rgba(245, 158, 11, 0.35);';
        if (evKey.includes('FAIL') || evKey.includes('MELT')) return 'background: rgba(239, 68, 68, 0.06); border: 1px solid rgba(239, 68, 68, 0.35);';
        return 'background: rgba(0, 242, 254, 0.06); border: 1px solid rgba(0, 242, 254, 0.35);';
    };

    return `
        <div class="lifecycle-subscription-card" style="margin-top: 18px; padding: 16px 18px; border-radius: 12px; background: rgba(255, 255, 255, 0.025); border: 1px solid rgba(255, 255, 255, 0.08);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
                <span style="font-size: 0.9rem; font-weight: 600; color: var(--text-bright); display: flex; align-items: center; gap: 6px;">
                    🔔 消息通知事件订阅中枢 (Event Subscriptions)
                </span>
                <span style="font-size: 0.74rem; color: var(--neon-cyan, #00f2fe);">智能分流 · 静默降噪</span>
            </div>
            <p style="margin: 0 0 12px 0; font-size: 0.76rem; color: var(--text-dim); line-height: 1.45;">
                定制该渠道需要接收的业务通知场景。未订阅的事件将全自动静默拦截，避免无效打扰与短信资费消耗。
            </p>

            <!-- 快捷预设按钮组 -->
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; background: rgba(0,0,0,0.3); padding: 5px 8px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
                <span style="font-size: 0.73rem; color: var(--text-dim); margin-right: 4px;">快捷预设:</span>
                <button type="button" class="preset-btn" data-preset="recommended" onclick="window.applyNotificationPreset('${id}', 'recommended')" style="padding: 3px 10px; font-size: 0.75rem; border-radius: 6px; border: 1px solid ${activePreset === 'recommended' ? 'var(--neon-cyan, #00f2fe)' : 'rgba(255,255,255,0.1)'}; background: ${activePreset === 'recommended' ? 'rgba(0, 242, 254, 0.15)' : 'transparent'}; color: ${activePreset === 'recommended' ? '#fff' : 'var(--text-dim)'}; cursor: pointer;">
                    🌟 智能推荐
                </button>
                <button type="button" class="preset-btn" data-preset="alerts_only" onclick="window.applyNotificationPreset('${id}', 'alerts_only')" style="padding: 3px 10px; font-size: 0.75rem; border-radius: 6px; border: 1px solid ${activePreset === 'alerts_only' ? '#ef4444' : 'rgba(255,255,255,0.1)'}; background: ${activePreset === 'alerts_only' ? 'rgba(239, 68, 68, 0.15)' : 'transparent'}; color: ${activePreset === 'alerts_only' ? '#fff' : 'var(--text-dim)'}; cursor: pointer;">
                    🚨 仅紧急告警
                </button>
                <button type="button" class="preset-btn" data-preset="all" onclick="window.applyNotificationPreset('${id}', 'all')" style="padding: 3px 10px; font-size: 0.75rem; border-radius: 6px; border: 1px solid ${activePreset === 'all' ? '#a855f7' : 'rgba(255,255,255,0.1)'}; background: ${activePreset === 'all' ? 'rgba(168, 85, 247, 0.15)' : 'transparent'}; color: ${activePreset === 'all' ? '#fff' : 'var(--text-dim)'}; cursor: pointer;">
                    📡 开发者全知
                </button>
            </div>

            <!-- 四大场景卡片 -->
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <!-- 场景 1: 文章出版与构建 -->
                <div style="background: rgba(0,0,0,0.2); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);">
                    <div style="font-size: 0.78rem; font-weight: 600; color: #93c5fd; margin-bottom: 8px;">
                        📚 文章出版与构建 (Publishing)
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 8px;">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; padding: 6px 10px; border-radius: 6px; transition: all 0.2s ease; ${getEventLabelStyle('SYNC_SUCCESS', hasEvent('SYNC_SUCCESS'))}">
                            <input type="checkbox" data-event-key="SYNC_SUCCESS" onchange="window.updateChannelEventSubscription('${id}', 'SYNC_SUCCESS', this.checked, this)" ${hasEvent('SYNC_SUCCESS') ? 'checked' : ''}>
                            <span>✅ 全量出版完成</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; padding: 6px 10px; border-radius: 6px; transition: all 0.2s ease; ${getEventLabelStyle('SYNC_FAIL', hasEvent('SYNC_FAIL'))}">
                            <input type="checkbox" data-event-key="SYNC_FAIL" onchange="window.updateChannelEventSubscription('${id}', 'SYNC_FAIL', this.checked, this)" ${hasEvent('SYNC_FAIL') ? 'checked' : ''}>
                            <span>❌ 编译出版失败</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; padding: 6px 10px; border-radius: 6px; transition: all 0.2s ease; ${getEventLabelStyle('SYNC_START', hasEvent('SYNC_START'))}">
                            <input type="checkbox" data-event-key="SYNC_START" onchange="window.updateChannelEventSubscription('${id}', 'SYNC_START', this.checked, this)" ${hasEvent('SYNC_START') ? 'checked' : ''}>
                            <span>🚀 发布流水线启动</span>
                        </label>
                    </div>
                </div>

                <!-- 场景 2: 跨平台社交分发 -->
                <div style="background: rgba(0,0,0,0.2); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);">
                    <div style="font-size: 0.78rem; font-weight: 600; color: #a78bfa; margin-bottom: 8px;">
                        🌐 跨平台社交分发 (Syndication)
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 8px;">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; padding: 6px 10px; border-radius: 6px; transition: all 0.2s ease; ${getEventLabelStyle('SYNDICATION_COMPLETED', hasEvent('SYNDICATION_COMPLETED'))}">
                            <input type="checkbox" data-event-key="SYNDICATION_COMPLETED" onchange="window.updateChannelEventSubscription('${id}', 'SYNDICATION_COMPLETED', this.checked, this)" ${hasEvent('SYNDICATION_COMPLETED') ? 'checked' : ''}>
                            <span>📤 社交全网分发完成</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; padding: 6px 10px; border-radius: 6px; transition: all 0.2s ease; ${getEventLabelStyle('SYNDICATION_FAILED', hasEvent('SYNDICATION_FAILED'))}">
                            <input type="checkbox" data-event-key="SYNDICATION_FAILED" onchange="window.updateChannelEventSubscription('${id}', 'SYNDICATION_FAILED', this.checked, this)" ${hasEvent('SYNDICATION_FAILED') ? 'checked' : ''}>
                            <span>⚠️ 渠道分发异常</span>
                        </label>
                    </div>
                </div>

                <!-- 场景 3: 安全合规与算力告警 -->
                <div style="background: rgba(0,0,0,0.2); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);">
                    <div style="font-size: 0.78rem; font-weight: 600; color: #f87171; margin-bottom: 8px;">
                        🛡️ 安全合规与算力告警 (Safety & AI Sentinel)
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 8px;">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; padding: 6px 10px; border-radius: 6px; transition: all 0.2s ease; ${getEventLabelStyle('AI_MELT', hasEvent('AI_MELT'))}">
                            <input type="checkbox" data-event-key="AI_MELT" onchange="window.updateChannelEventSubscription('${id}', 'AI_MELT', this.checked, this)" ${hasEvent('AI_MELT') ? 'checked' : ''}>
                            <span>⚡ AI 算力熔断 (Token耗尽)</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; padding: 6px 10px; border-radius: 6px; transition: all 0.2s ease; ${getEventLabelStyle('COMPLIANCE_BLOCKED', hasEvent('COMPLIANCE_BLOCKED'))}">
                            <input type="checkbox" data-event-key="COMPLIANCE_BLOCKED" onchange="window.updateChannelEventSubscription('${id}', 'COMPLIANCE_BLOCKED', this.checked, this)" ${hasEvent('COMPLIANCE_BLOCKED') ? 'checked' : ''}>
                            <span>🔒 出版合规与敏感词拦截</span>
                        </label>
                    </div>
                </div>

                <!-- 场景 4: 云端托管与上线 -->
                <div style="background: rgba(0,0,0,0.2); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);">
                    <div style="font-size: 0.78rem; font-weight: 600; color: #34d399; margin-bottom: 8px;">
                        🚀 云端托管与上线 (Hosting & Deployment)
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 8px;">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; padding: 6px 10px; border-radius: 6px; transition: all 0.2s ease; ${getEventLabelStyle('DEPLOY_SUCCESS', hasEvent('DEPLOY_SUCCESS'))}">
                            <input type="checkbox" data-event-key="DEPLOY_SUCCESS" onchange="window.updateChannelEventSubscription('${id}', 'DEPLOY_SUCCESS', this.checked, this)" ${hasEvent('DEPLOY_SUCCESS') ? 'checked' : ''}>
                            <span>🌐 全站部署上线成功</span>
                        </label>
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: var(--text-normal); cursor: pointer; padding: 6px 10px; border-radius: 6px; transition: all 0.2s ease; ${getEventLabelStyle('DEPLOY_FAILED', hasEvent('DEPLOY_FAILED'))}">
                            <input type="checkbox" data-event-key="DEPLOY_FAILED" onchange="window.updateChannelEventSubscription('${id}', 'DEPLOY_FAILED', this.checked, this)" ${hasEvent('DEPLOY_FAILED') ? 'checked' : ''}>
                            <span>🚨 云端构建推流失败</span>
                        </label>
                    </div>
                </div>
            </div>
        </div>
    `;
};

// 🚀 [V107.0] 一键应用预设方案 (纯 DOM 丝滑响应，无闪烁，无表单数据丢失)
window.applyNotificationPreset = (id, presetType) => {
    let targetEvents = [];
    if (presetType === 'alerts_only') {
        targetEvents = ['SYNC_FAIL', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_FAILED'];
    } else if (presetType === 'all') {
        targetEvents = ['SYNC_SUCCESS', 'SYNC_FAIL', 'SYNC_START', 'SYNDICATION_COMPLETED', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_SUCCESS', 'DEPLOY_FAILED'];
    } else {
        // 智能推荐
        targetEvents = ['SYNC_SUCCESS', 'SYNC_FAIL', 'SYNDICATION_COMPLETED', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_SUCCESS'];
    }

    // 1. 同步更新全局内存数据模型
    window.settingsData = window.settingsData || {};
    window.settingsData.publish_control = window.settingsData.publish_control || {};
    window.settingsData.publish_control.webhook_endpoints = window.settingsData.publish_control.webhook_endpoints || {};
    window.settingsData.publish_control.webhook_endpoints[id] = window.settingsData.publish_control.webhook_endpoints[id] || {};
    window.settingsData.publish_control.webhook_endpoints[id].events = targetEvents;

    // 2. 毫秒级直接操作 DOM 元素，更新勾选与视觉边框柔和高亮
    const cardEl = document.querySelector('.lifecycle-subscription-card');
    if (cardEl) {
        // 更新所有复选框状态与边框
        const checkboxes = cardEl.querySelectorAll('input[data-event-key]');
        checkboxes.forEach(cb => {
            const evKey = cb.getAttribute('data-event-key');
            const isChecked = targetEvents.includes(evKey);
            cb.checked = isChecked;
            if (cb.parentElement) {
                if (!isChecked) {
                    cb.parentElement.style.borderColor = 'rgba(255, 255, 255, 0.06)';
                    cb.parentElement.style.background = 'rgba(255, 255, 255, 0.015)';
                } else if (evKey === 'COMPLIANCE_BLOCKED') {
                    cb.parentElement.style.borderColor = 'rgba(245, 158, 11, 0.35)';
                    cb.parentElement.style.background = 'rgba(245, 158, 11, 0.06)';
                } else if (evKey.includes('FAIL') || evKey.includes('MELT')) {
                    cb.parentElement.style.borderColor = 'rgba(239, 68, 68, 0.35)';
                    cb.parentElement.style.background = 'rgba(239, 68, 68, 0.06)';
                } else {
                    cb.parentElement.style.borderColor = 'rgba(0, 242, 254, 0.35)';
                    cb.parentElement.style.background = 'rgba(0, 242, 254, 0.06)';
                }
            }
        });

        // 更新预设按钮的高亮状态
        const presetBtns = cardEl.querySelectorAll('.preset-btn');
        presetBtns.forEach(btn => {
            const pType = btn.getAttribute('data-preset');
            if (pType === presetType) {
                if (presetType === 'recommended') {
                    btn.style.borderColor = 'var(--neon-cyan, #00f2fe)';
                    btn.style.background = 'rgba(0, 242, 254, 0.15)';
                    btn.style.color = '#fff';
                } else if (presetType === 'alerts_only') {
                    btn.style.borderColor = '#ef4444';
                    btn.style.background = 'rgba(239, 68, 68, 0.15)';
                    btn.style.color = '#fff';
                } else if (presetType === 'all') {
                    btn.style.borderColor = '#a855f7';
                    btn.style.background = 'rgba(168, 85, 247, 0.15)';
                    btn.style.color = '#fff';
                }
            } else {
                btn.style.borderColor = 'rgba(255,255,255,0.1)';
                btn.style.background = 'transparent';
                btn.style.color = 'var(--text-dim)';
            }
        });
    }

    if (typeof window.markSettingsDirty === 'function') {
        window.markSettingsDirty();
    }
};

// 🚀 [V107.0] 实时更新渠道事件订阅配置
window.updateChannelEventSubscription = (id, eventKey, isChecked, inputEl) => {
    window.settingsData = window.settingsData || {};
    window.settingsData.publish_control = window.settingsData.publish_control || {};
    window.settingsData.publish_control.webhook_endpoints = window.settingsData.publish_control.webhook_endpoints || {};
    window.settingsData.publish_control.webhook_endpoints[id] = window.settingsData.publish_control.webhook_endpoints[id] || {};

    const node = window.settingsData.publish_control.webhook_endpoints[id];
    let currentEvents = Array.isArray(node.events) ? [...node.events] : (id === 'sms' ? ['SYNC_FAIL', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_FAILED'] : ['SYNC_SUCCESS', 'SYNC_FAIL', 'SYNDICATION_COMPLETED', 'SYNDICATION_FAILED', 'AI_MELT', 'COMPLIANCE_BLOCKED', 'DEPLOY_SUCCESS']);

    if (isChecked) {
        if (!currentEvents.includes(eventKey)) currentEvents.push(eventKey);
    } else {
        currentEvents = currentEvents.filter(k => k !== eventKey);
    }
    node.events = currentEvents;

    if (inputEl && inputEl.parentElement) {
        if (!isChecked) {
            inputEl.parentElement.style.borderColor = 'rgba(255, 255, 255, 0.06)';
            inputEl.parentElement.style.background = 'rgba(255, 255, 255, 0.015)';
        } else if (eventKey === 'COMPLIANCE_BLOCKED') {
            inputEl.parentElement.style.borderColor = 'rgba(245, 158, 11, 0.35)';
            inputEl.parentElement.style.background = 'rgba(245, 158, 11, 0.06)';
        } else if (eventKey.includes('FAIL') || eventKey.includes('MELT')) {
            inputEl.parentElement.style.borderColor = 'rgba(239, 68, 68, 0.35)';
            inputEl.parentElement.style.background = 'rgba(239, 68, 68, 0.06)';
        } else {
            inputEl.parentElement.style.borderColor = 'rgba(0, 242, 254, 0.35)';
            inputEl.parentElement.style.background = 'rgba(0, 242, 254, 0.06)';
        }
    }

    // 当用户手动点选单个复选框时，重置所有预设按钮为普通透明状态（表示当前处于自定义模式）
    const cardEl = document.querySelector('.lifecycle-subscription-card');
    if (cardEl) {
        const presetBtns = cardEl.querySelectorAll('.preset-btn');
        presetBtns.forEach(btn => {
            btn.style.borderColor = 'rgba(255,255,255,0.1)';
            btn.style.background = 'transparent';
            btn.style.color = 'var(--text-dim)';
        });
    }

    if (typeof window.markSettingsDirty === 'function') {
        window.markSettingsDirty();
    }
};
