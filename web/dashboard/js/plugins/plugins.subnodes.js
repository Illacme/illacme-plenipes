/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Subnodes Shard
 */
var renderSettingsItem = window.renderSettingsItem || (() => "");

window.filterSubItems = (input) => {
    const term = input.value.toLowerCase();
    const card = input.closest('.plugin-card');
    const rows = card.querySelectorAll('.sub-item-row');
    rows.forEach(row => {
        const name = row.getAttribute('data-sub-name');
        const target = row.getAttribute('data-sub-target');
        row.style.display = (name.includes(term) || target.includes(term)) ? 'flex' : 'none';
    });
};

window.filterConsoleTable = (input) => {
    const term = input.value.toLowerCase();
    const rows = document.querySelectorAll('.console-tr');
    rows.forEach(row => {
        const searchData = row.getAttribute('data-search');
        row.style.display = searchData.includes(term) ? '' : 'none';
    });
};

window.editSubItem = async (parentId, subId) => {
    const body = document.getElementById('p-drawer-body');
    const p = window.allPlugins.find(x => x.id === parentId);
    if (!p) return;

    const dryRunBtn = document.getElementById('btn-dry-run-plugin');
    if (dryRunBtn) {
        dryRunBtn.style.display = 'block';
        dryRunBtn.setAttribute('onclick', `triggerPluginDryRun('${subId}', '${parentId}')`);
    }

    let subHtml = `
        <div class="sub-editor-header" style="margin-bottom: 1.5rem;">
            <button class="p-action-btn secondary" style="padding: 4px 10px; font-size: 0.75rem;" onclick="openPluginConfig('${parentId}')">⬅️ 返回通道列表</button>
            <h4 style="margin-top: 1rem; color: var(--accent-primary);">⚙️ 节点管理: ${subId.toUpperCase()}</h4>
        </div>
        <div class="settings-grid">
    `;

    if (parentId === 'webhook_gateway') {
        const endpoint = window.settingsData.publish_control?.webhook_endpoints?.[subId] || {};
        let urlPlaceholder = "例如: https://hooks.slack.com/services/...";
        let desc = "开启后，当前激活的品牌将在执行出版发布任务时向该 Webhook 端点推送数据。";
        let hasSecret = true;

        if (subId === 'feishu') {
            urlPlaceholder = "例如: https://open.feishu.cn/open-apis/bot/v2/hook/...";
        } else if (subId === 'dingtalk') {
            urlPlaceholder = "例如: https://oapi.dingtalk.com/robot/send?access_token=...";
            hasSecret = false;
        } else if (subId === 'private_api') {
            urlPlaceholder = "例如: https://api.yourdomain.com/v1/publish-notify";
        }

        subHtml += `
            ${renderSettingsItem('通道激活', `publish_control.webhook_endpoints.${subId}.enabled`, endpoint.enabled, 'checkbox', {description: desc})}
            ${renderSettingsItem('物理端点 (URL)', `publish_control.webhook_endpoints.${subId}.url`, endpoint.url, 'text', {placeholder: urlPlaceholder})}
        `;
        if (hasSecret) {
            subHtml += `
                ${renderSettingsItem('主权密钥 (Secret / Sign Key)', `publish_control.webhook_endpoints.${subId}.secret`, endpoint.secret, 'password', {placeholder: "签名验证 Key (可选，防重放)"})}
            `;
        }
    } else {
        const cfg = window.settingsData.syndication?.[subId] || {};
        subHtml += window.renderPlatformConfig(subId, cfg, p.category);
    }

    subHtml += `
        </div>
        <div id="sandbox-console-wrapper" style="display: none; margin-top: 25px; border-top: 1px solid var(--glass-border); padding-top: 15px;">
            <label class="tiny-label" style="color: var(--accent-secondary); margin-bottom: 8px; display: block; font-weight: 700; font-size: 0.7rem;">🧪 物理沙盒仿真演练终端 (Sandbox Emulation Terminal)</label>
            <div id="sandbox-console-terminal" style="background: rgba(0,0,0,0.55); border: 1px solid var(--glass-border); border-radius: 8px; padding: 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #00ff88; max-height: 180px; overflow-y: auto; line-height: 1.5; box-shadow: inset 0 0 10px rgba(0,0,0,0.7); scrollbar-width: thin;">
                <!-- 滚动日志 -->
            </div>
        </div>
        <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--glass-border); display: flex; flex-direction: column; gap: 1rem;">
            <button class="primary-btn glow-btn" onclick="savePluginSettingsAndClose()">💾 保存节点配置</button>
            <p style="font-size: 0.7rem; color: var(--text-dim);">⚠️ 注意：修改将直接同步至物理配置文件，保存后请重启系统生效。</p>
        </div>
    `;

    body.innerHTML = subHtml;
};
