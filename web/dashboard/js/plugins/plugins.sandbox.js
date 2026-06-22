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
    terminal.innerHTML = '<div style="color: var(--accent-secondary); opacity: 0.8; font-style: italic; animation: pulse 1.5s infinite;">📡 物理通道连接测试中，正在抓取并对齐当前表单临时参数...</div>';
    
    // 自动滑动定位到测试终端 (仅在抽屉 body 容器内部滚动，防止外层 window 或整个抽屉浮层发生位移溢出)
    const drawerBody = document.getElementById('p-drawer-body');
    if (drawerBody) {
        drawerBody.scrollTo({
            top: drawerBody.scrollHeight,
            behavior: 'smooth'
        });
    }

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

        window.probePassState = window.probePassState || {};
        if (res && res.success) {
            window.probePassState[id] = true;
        } else {
            window.probePassState[id] = false;
        }

        if (!res || !res.logs) {
            terminal.innerHTML = '<div style="color: #ff4d4d; font-weight: bold;">❌ 物理通道连接测试超时，未获得连接反馈。</div>';
            return;
        }

        // 流式高科技模拟淡入，逐行打点
        terminal.innerHTML = '';
        let i = 0;
        const streamInterval = setInterval(() => {
            if (i >= res.logs.length) {
                clearInterval(streamInterval);
                
                // 🔍 检查是否有依赖缺失的 Warn 级日志
                const hasDepWarning = res.logs.some(log => log.message.includes('install') || log.message.includes('安装') || log.message.includes('依赖库'));
                const oldContainer = document.getElementById('dep-install-container');
                if (oldContainer) oldContainer.remove();

                if (hasDepWarning) {
                    const installBox = document.createElement('div');
                    installBox.id = 'dep-install-container';
                    installBox.style.marginTop = '10px';
                    installBox.style.display = 'flex';
                    installBox.style.justifyContent = 'space-between';
                    installBox.style.alignItems = 'center';
                    installBox.style.padding = '8px 12px';
                    installBox.style.background = 'rgba(255, 170, 0, 0.1)';
                    installBox.style.border = '1px solid rgba(255, 170, 0, 0.3)';
                    installBox.style.borderRadius = '6px';
                    installBox.style.transition = 'opacity 0.3s ease-out';
                    
                    installBox.innerHTML = `
                        <span style="font-size: 0.72rem; color: #ffaa00;">检测到本地环境缺少该驱动所需的 Python 依赖包。</span>
                        <button id="btn-install-dep" class="p-btn" style="padding: 4px 10px; font-size: 0.7rem; background: var(--accent-primary); border-radius: 4px; color: var(--text-bright); border: none; cursor: pointer;" onclick="window.installPluginDependencies('${id}')">🔌 一键安装依赖</button>
                    `;
                    terminal.parentNode.appendChild(installBox);
                    
                    if (drawerBody) {
                        drawerBody.scrollTo({
                            top: drawerBody.scrollHeight,
                            behavior: 'smooth'
                        });
                    }
                }
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
        terminal.innerHTML = `<div style="color: #ff4d4d;">❌ 连接测试物理通信报错: ${e}</div>`;
    }
};

window.installPluginDependencies = async (id) => {
    const btn = document.getElementById('btn-install-dep');
    const container = document.getElementById('dep-install-container');
    const terminal = document.getElementById('sandbox-console-terminal');
    if (!btn || !terminal) return;

    btn.disabled = true;
    btn.innerText = '⏳ 正在安装中...';
    
    const addLogLine = (msg, level = 'INFO') => {
        const line = document.createElement('div');
        let color = '#d1d1d1';
        if (level === 'ERROR') color = '#ff4d4d';
        else if (level === 'SUCCESS') color = '#00ff88';
        line.style.color = color;
        line.style.marginBottom = '4px';
        const now = new Date().toTimeString().split(' ')[0];
        line.innerText = `[${now}] [${level}] ${msg}`;
        terminal.appendChild(line);
        terminal.scrollTop = terminal.scrollHeight;
    };

    addLogLine('🔑 物理触发一键依赖自愈管线，自动连接远端镜像源...', 'INFO');

    try {
        const res = await apiFetch('/api/plugins/install-deps', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id })
        });

        if (res && res.success) {
            if (res.logs) {
                res.logs.forEach(l => {
                    addLogLine(l.message, l.level);
                });
            }
            addLogLine('🟢 物理依赖自动装载完成！将在 1.5 秒后自动为您重启「测试连接」...', 'SUCCESS');
            if (container) {
                setTimeout(() => {
                    container.style.opacity = '0';
                    setTimeout(() => container.remove(), 300);
                }, 1000);
            }
            setTimeout(() => {
                window.triggerPluginDryRun(id);
            }, 1500);
        } else {
            const errMsg = res ? (res.error || '依赖包部分安装失败') : '安装超时';
            if (res && res.logs) {
                res.logs.forEach(l => {
                    addLogLine(l.message, l.level);
                });
            }
            addLogLine(`❌ 依赖自动安装中止: ${errMsg}`, 'ERROR');
            btn.disabled = false;
            btn.innerText = '重新一键安装';
        }
    } catch (e) {
        addLogLine(`❌ 物理通信中断: ${e}`, 'ERROR');
        btn.disabled = false;
        btn.innerText = '重新一键安装';
    }
};

// 🚀 [V75.5] 100% 物理自愈：专门针对插件/通道抽屉配置设计的“强力同步保存并关闭”算子
window.savePluginSettingsAndClose = async () => {
    if (typeof addAudit === 'function') addAudit("💾 开始同步当前面板参数并准备保存...");

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
        if (typeof addAudit === 'function') addAudit("✅ 插件能力配置已成功保存并生效。", 'success');
        if (res.active_config) {
            window.settingsData = { ...window.settingsData, ...res.active_config };
        }

        // 3. 弹出高保真玻璃磨砂通知，给用户强烈的物理确认视觉反馈！
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                title: '💾 保存成功',
                text: '插件能力配置已成功保存，系统配置已即刻更新生效！',
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
