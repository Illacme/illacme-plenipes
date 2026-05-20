/**
 * 🧪 [V87.0] Illacme Plenipes Plugins Sandbox & Config Saver
 * 职责：物理沙盒干跑仿真、280ms 流式淡入终端日志渲染、以及 config.yaml 配置强力捕获与固化落盘。
 */

// 🚀 物理沙盒干跑前端控制台交互算子（高保真流式淡入动画效果）
window.triggerPluginDryRun = async (id, parentId = null) => {
    const terminalWrapper = document.getElementById('sandbox-console-wrapper');
    const terminal = document.getElementById('sandbox-console-terminal');
    if (!terminalWrapper || !terminal) return;

    // 展现透明终端，启动脉冲动画
    terminalWrapper.style.display = 'block';
    terminal.innerHTML = '<div style="color: var(--accent-secondary); opacity: 0.8; font-style: italic; animation: pulse 1.5s infinite;">📡 物理演练通道点火中，正在抓取并对齐当前表单临时参数...</div>';
    
    // 自动滑动定位到演练面板
    terminalWrapper.scrollIntoView({ behavior: 'smooth' });

    // 抓取当前已修改 but 未保存的配置（与 updateConfigField 无缝联动）
    let settings = {};
    if (parentId === 'webhook_gateway') {
        settings = window.settingsData.publish_control?.webhook_endpoints?.[id] || {};
    } else if (parentId) {
        settings = window.settingsData.syndication?.[id] || {};
    } else {
        settings = window.settingsData.syndication?.[id] || window.settingsData.publish_control?.direct_upload?.[id] || {};
    }

    try {
        const res = await apiFetch('/api/plugins/dry-run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, parentId, settings })
        });

        if (!res || !res.logs) {
            terminal.innerHTML = '<div style="color: #ff4d4d; font-weight: bold;">❌ 物理沙箱干跑路由通信超时，未获得遥测回吐。</div>';
            return;
        }

        // 流式高科技模拟淡入，逐行打点
        terminal.innerHTML = '';
        let i = 0;
        const streamInterval = setInterval(() => {
            if (i >= res.logs.length) {
                clearInterval(streamInterval);
                return;
            }
            const log = res.logs[i];
            let color = '#d1d1d1'; // INFO
            if (log.level === 'WARN') color = '#ffaa00';
            else if (log.level === 'ERROR') color = '#ff4d4d';
            else if (log.level === 'SUCCESS') color = '#00ff88';

            const line = document.createElement('div');
            line.style.color = color;
            line.style.opacity = '0';
            line.style.transition = 'opacity 0.25s ease-out';
            line.style.marginBottom = '4px';
            line.innerText = `[${log.time}] [${log.level}] ${log.message}`;
            
            terminal.appendChild(line);
            
            // 触发微淡入并保持终端触底滚动
            setTimeout(() => { line.style.opacity = '1'; }, 10);
            terminal.scrollTop = terminal.scrollHeight;
            
            i++;
        }, 280); // 精雕细琢的 280ms 节奏，极其逼真的发布沙盘动态推演反馈

    } catch (e) {
        terminal.innerHTML = `<div style="color: #ff4d4d;">❌ 沙盘物理通信报错: ${e}</div>`;
    }
};

// 🚀 [V75.5] 100% 物理自愈：专门针对插件/通道抽屉配置设计的“强力同步保存并关闭”算子
window.savePluginSettingsAndClose = async () => {
    if (typeof addAudit === 'function') addAudit("💾 开始抓取当前面板临时参数并准备固化...");

    // 1. 强力抓取抽屉内所有 input 的当前最新状态，写入 window.settingsData
    const drawerBody = document.getElementById('p-drawer-body');
    if (drawerBody) {
        const inputs = drawerBody.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            const path = input.getAttribute('data-path');
            if (path) {
                let val;
                if (input.type === 'checkbox') {
                    val = input.checked;
                } else if (input.type === 'number') {
                    val = parseFloat(input.value);
                } else {
                    val = input.value;
                }
                
                // 写入 window.settingsData
                const keys = path.split('.');
                let current = window.settingsData;
                for (let i = 0; i < keys.length - 1; i++) {
                    if (!current[keys[i]]) current[keys[i]] = {};
                    current = current[keys[i]];
                }
                current[keys[keys.length - 1]] = val;
            }
        });
    }

    // 2. 调用后台保存接口落盘
    const fullConfig = typeof window.flattenObject === 'function' ? window.flattenObject(window.settingsData) : window.settingsData;
    const payload = {};
    
    Object.keys(fullConfig).forEach(key => {
        if (!key.split('.').some(part => part.startsWith('_'))) {
            payload[key] = fullConfig[key];
        }
    });

    const res = await apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res && res.status === 'success') {
        if (typeof addAudit === 'function') addAudit("✅ 插件配置已成功固化至物理磁盘。", 'success');
        if (res.active_config) {
            window.settingsData = { ...window.settingsData, ...res.active_config };
        }

        // 3. 弹出高保真玻璃磨砂通知，给用户强烈的物理确认视觉反馈！
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: '💾 保存成功',
                text: '插件能力配置已成功固化并写入物理磁盘 config.yaml / config.local.ya' + 'ml！',
                icon: 'success',
                confirmButtonText: '确定',
                background: 'var(--card-bg)',
                color: 'var(--text-bright)',
                confirmButtonColor: 'var(--accent-primary)'
            });
        }

        // 4. 自动关闭抽屉
        if (typeof closePluginDrawer === 'function') {
            closePluginDrawer();
        }

        // 5. 重新渲染插件矩阵列表，以刷新状态
        if (typeof renderPlugins === 'function') {
            renderPlugins();
        }
        
        // 6. 即时更新左侧身份及状态面板
        if (typeof refreshGovernanceContext === 'function') {
            await refreshGovernanceContext();
        }
    } else {
        const errMsg = res ? res.error : '物理链路异常';
        if (typeof addAudit === 'function') addAudit(`❌ 插件配置保存失败: ${errMsg}`, 'error');
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: '❌ 保存失败',
                text: errMsg,
                icon: 'error',
                confirmButtonText: '了解',
                background: 'var(--card-bg)',
                color: 'var(--text-bright)',
                confirmButtonColor: 'var(--accent-primary)'
            });
        }
    }
};
