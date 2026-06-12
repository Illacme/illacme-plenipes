/**
 * 🕹️ Illacme Compute Center - Operations Shard (SOP-02 DECOUPLED)
 * 职责：负责所有涉及 REST API 网络通信、脉冲感应与配置持久化保存的物理操作。
 */

window.ComputeHandlers = window.ComputeHandlers || {};

/**
 * 📡 物理节点脉冲探测
 */
window.ComputeHandlers.probeNode = async function(id) {
    const statusEl = document.getElementById(`probe-status-${id}`);
    const latencyEl = document.getElementById(`latency-${id}`);
    if (statusEl) statusEl.innerHTML = '<span class="pulsing">发射脉冲探测中...</span>';

    try {
        const startTime = Date.now();
        const res = await apiFetch('/api/compute/nodes/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: id })
        });
        const duration = Date.now() - startTime;

        if (statusEl) {
            if (res?.status === 'success') {
                statusEl.innerHTML = `<span class="online">✅ 物理响应正常 | 链路固化完毕</span>`;
                if (latencyEl) latencyEl.innerHTML = `<span class="healthy">${res.latency || duration}ms</span>`;
                document.getElementById(`node-unit-${id}`)?.classList.add('pulse-glow');
                return true;
            } else {
                statusEl.innerHTML = `<span class="offline">${res.error || '❌ 信号断裂'}</span>`;
                if (latencyEl) latencyEl.innerHTML = `<span class="offline">TIMEOUT</span>`;
                return false;
            }
        }
    } catch (e) {
        if (statusEl) statusEl.innerHTML = `<span class="offline">❌ 探测崩溃: ${e.message}</span>`;
        return false;
    }
};

/**
 * 📡 全域脉冲同步
 */
window.ComputeHandlers.probeAllNodes = async function() {
    const nodes = document.querySelectorAll('.node-unit:not(.hidden)');
    if (nodes.length === 0) return;

    if (typeof addAudit === 'function') addAudit(`📡 正在启动全域脉冲感应，目标: ${nodes.length} 个算力单元...`, "info");

    const promises = Array.from(nodes).map(node => {
        const id = node.id.replace('node-unit-', '');
        return this.probeNode(id);
    });

    await Promise.all(promises);
    if (typeof addAudit === 'function') addAudit(`✅ 全域脉冲探测任务执行完毕。`, "success");
};

/**
 * 💾 固化算力调度策略
 */
window.ComputeHandlers.saveComputeStrategy = async function(event, skipRefetch = false) {
    const btn = event?.target || document.querySelector('.strategy-command-deck .primary-btn');
    if (!btn) return;

    const originalText = btn.innerText;
    btn.innerText = "正在保存配置...";

    const t = window.settingsData?.translation || {};
    const payload = {
        'translation.primary_node': t.primary_node,
        'translation.primary_model': t.primary_model,
        'translation.fallback_node': t.fallback_node,
        'translation.fallback_model': t.fallback_model,
        'translation.strategy': t.strategy,
        'translation.llm_concurrency': t.llm_concurrency || 1,
        'translation.api_timeout': t.api_timeout || 600,
        'translation.max_retries': t.max_retries || 5,
        'translation.max_chunk_size': t.max_chunk_size || 2500,
        'translation.enable_thinking': t.enable_thinking !== undefined ? t.enable_thinking : false,
        'translation.enable_ai': t.enable_ai !== undefined ? t.enable_ai : true
    };

    const res = await apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    btn.innerText = originalText;
    if (res?.status === 'success') {
        if (typeof showNotification === 'function') showNotification('✅ 算力配置保存成功', 'success');
        btn.classList.remove('pulse-alert');
        btn.disabled = true;
        btn.innerHTML = '✅ 配置已保存';
        
        // 🚀 [V74.70] 勋章联动：立即同步并触发成功脉冲
        this.syncStrategyBadge();
        const badge = document.querySelector('.strategy-mode-badge');
        if (badge) {
            badge.classList.add('pulse-success');
            setTimeout(() => badge.classList.remove('pulse-success'), 2000);
        }
        
        setTimeout(() => {
            btn.innerHTML = originalText;
        }, 2000);

        // 🚀 立即刷新治理上下文与 AI 助手能力状态，防止大盘显示滞后
        if (typeof window.refreshGovernanceContext === 'function') {
            window.refreshGovernanceContext();
        }
        if (window.SovereignAgent && typeof window.SovereignAgent.initModelCapabilities === 'function') {
            window.SovereignAgent.initModelCapabilities();
        }

        if (!skipRefetch) {
            const freshRes = await apiFetch('/api/system/config');
            const freshConfig = freshRes.config || freshRes;
            if (freshConfig.translation) {
                window.settingsData.translation = freshConfig.translation;
                this.syncStrategyBadge();

                // 重新渲染当前 Tab 以实时体现置灰及拦截状态
                const viewport = document.getElementById('compute-tab-viewport');
                if (viewport && window.ComputeUI) {
                    const activeTabBtn = document.querySelector('.tactical-tabs .t-tab.active');
                    const currentTab = activeTabBtn ? activeTabBtn.getAttribute('data-tab') : 'strategy';
                    if (currentTab === 'strategy' && typeof window.ComputeUI.renderStrategyTab === 'function') {
                        window.ComputeUI.renderStrategyTab(viewport, freshConfig.translation);
                    } else if (currentTab === 'infrastructure' && typeof window.ComputeUI.renderInfrastructureTab === 'function') {
                        window.ComputeUI.renderInfrastructureTab(viewport);
                    }
                }
            }
        }
    } else {
        if (typeof showNotification === 'function') showNotification('❌ 固化失败: ' + (res?.error || '物理链路异常'), 'error');
    }
};

/**
 * 🔄 恢复出厂策略
 */
window.ComputeHandlers.resetComputeStrategy = async function() {
    if (!confirm("⚠️ 确定要恢复出厂策略吗？\n这将从系统底座拉取默认参数并覆盖当前品牌配置。")) return;

    try {
        // 🚀 [V74.85] 权威溯源：从后端获取全局底座配置，而非在前端硬编码
        const res = await apiFetch('/api/system/config?level=global');
        const globalConfig = res.config || res;
        const g = globalConfig.translation || {};
        
        window.settingsData.translation = window.settingsData.translation || {};
        const t = window.settingsData.translation;
        
        // 1. 拨乱反正：用系统底座值覆盖内存
        t.llm_concurrency = g.llm_concurrency || 1;
        t.api_timeout = g.api_timeout || 600;
        t.max_retries = g.max_retries || 5;
        t.max_chunk_size = g.max_chunk_size || 2500;
        t.strategy = g.strategy || 'single';
        t.enable_thinking = g.enable_thinking !== undefined ? g.enable_thinking : false;
        t.enable_ai = g.enable_ai !== undefined ? g.enable_ai : true;
        
        // 2. 强效视觉同步
        const setVal = (id, val) => {
            const el = document.getElementById(id);
            if (el) {
                el.value = val;
                el.classList.add('highlight-change');
                setTimeout(() => el.classList.remove('highlight-change'), 1000);
            }
        };

        setVal('input-llm-concurrency', t.llm_concurrency);
        setVal('input-api-timeout', t.api_timeout);
        setVal('input-max-retries', t.max_retries);
        setVal('input-max-chunk-size', t.max_chunk_size);
        setVal('input-enable-thinking', t.enable_thinking ? 'true' : 'false');
        setVal('input-enable-ai', t.enable_ai ? 'true' : 'false');
        
        const strategySelect = document.getElementById('select-compute-strategy');
        if (strategySelect) strategySelect.value = t.strategy;

        // 3. 🚀 [V74.95] 精准重绘：传入容器与权威内存数据，阻断 API 回滚
        const viewport = document.getElementById('compute-tab-viewport');
        if (window.ComputeUI && typeof window.ComputeUI.renderStrategyTab === 'function' && viewport) {
            window.ComputeUI.renderStrategyTab(viewport, window.settingsData.translation);
            
            // 强效视觉高亮
            setTimeout(() => {
                ['llm-concurrency', 'api-timeout', 'max-retries', 'max-chunk-size'].forEach(id => {
                    const el = document.getElementById(`input-${id}`);
                    if (el) {
                        el.classList.add('highlight-change');
                        setTimeout(() => el.classList.remove('highlight-change'), 1000);
                    }
                });
            }, 100);
        }
        
        // 4. 触发固化保存 (带上 skipRefetch 标志)
        this.saveComputeStrategy({ target: document.getElementById('btn-save-compute-strategy') }, true);
        
        if (typeof showNotification === 'function') showNotification('🔄 已成功从系统底座恢复默认策略', 'info');
    } catch (err) {
        console.error("Reset failed:", err);
        if (typeof showNotification === 'function') showNotification('❌ 无法获取系统默认配置', 'error');
    }
};
