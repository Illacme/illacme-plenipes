/**
 * 🕹️ Illacme Compute Center - Event Handlers Shard (V74.24 DECOUPLED)
 * 职责：负责算力中心的核心事件路由、策略同步、脉冲探测与桥接兼容。
 */

window.ComputeHandlers = {
    /**
     * 🛰️ 策略勋章同步中枢
     */
    syncStrategyBadge(forcedValue = null) {
        const strategy = forcedValue || window.settingsData?.translation?.strategy || 'single';
        const badgeSlot = document.getElementById('compute-strategy-badge-slot');
        if (badgeSlot) {
            badgeSlot.innerHTML = `<div class="strategy-mode-badge badge active" style="font-size: 0.65rem; padding: 4px 12px;">[${strategy.toUpperCase()} MODE]</div>`;
        }
    },

    /**
     * 🕹️ 调度策略联动更新
     */
    updateStrategy(key, value) {
        if (!window.settingsData.translation) window.settingsData.translation = {};
        window.settingsData.translation[key] = value;

        // 🚀 [V73.6] 智能对正逻辑：切换节点时自动补全模型信息
        if (key.endsWith('_node')) {
            const type = key.split('_')[0]; 
            const selector = document.getElementById(`${key}_selector`);
            const selectedOption = selector.options[selector.selectedIndex];
            const defaultModel = selectedOption.getAttribute('data-model');

            if (defaultModel) {
                const input = document.getElementById(`${type}_model_input`);
                if (input) {
                    input.value = defaultModel;
                    window.settingsData.translation[`${type}_model`] = defaultModel;
                    if (typeof addAudit === 'function') addAudit(`📡 已自动锚定单元 [${value}] 的物理默认模型: ${defaultModel}`, "info");
                }
            }
        }

        if (key === 'strategy') {
            document.querySelectorAll('.strategy-item').forEach(el => el.classList.remove('active'));
            const items = document.querySelectorAll('.strategy-item');
            items.forEach(item => {
                if (item.getAttribute('onclick').includes(`'${value}'`)) {
                    item.classList.add('active');
                }
            });
            this.syncStrategyBadge(value);
            if (typeof addAudit === 'function') addAudit(`⚖️ 算力调度模式已实时切换为: ${value.toUpperCase()}`, "info");
        }

        const saveBtn = document.getElementById('btn-save-compute-strategy');
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.classList.add('pulse-alert');
            saveBtn.innerHTML = '🛡️ 配置已变更，请保存';
        }
    },

    /**
     * 📡 物理节点脉冲探测
     */
    async probeNode(id) {
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
                    statusEl.innerHTML = `<span class="offline">❌ 感应丢失: ${res.error || '信号断裂'}</span>`;
                    if (latencyEl) latencyEl.innerHTML = `<span class="offline">TIMEOUT</span>`;
                    return false;
                }
            }
        } catch (e) {
            if (statusEl) statusEl.innerHTML = `<span class="offline">❌ 探测崩溃: ${e.message}</span>`;
            return false;
        }
    },

    /**
     * 📡 全域脉冲同步
     */
    async probeAllNodes() {
        const nodes = document.querySelectorAll('.node-unit:not(.hidden)');
        if (nodes.length === 0) return;

        if (typeof addAudit === 'function') addAudit(`📡 正在启动全域脉冲感应，目标: ${nodes.length} 个算力单元...`, "info");

        const promises = Array.from(nodes).map(node => {
            const id = node.id.replace('node-unit-', '');
            return this.probeNode(id);
        });

        await Promise.all(promises);
        if (typeof addAudit === 'function') addAudit(`✅ 全域脉冲探测任务执行完毕。`, "success");
    },

    /**
     * 🔍 算力单元实时过滤
     */
    filterNodes(query) {
        const lowerQuery = query.toLowerCase();
        const nodes = document.querySelectorAll('.node-unit');
        let visibleCount = 0;

        nodes.forEach(node => {
            const id = node.id.replace('node-unit-', '').toLowerCase();
            const type = (node.querySelector('.node-type')?.innerText || '').toLowerCase();
            const model = (node.querySelector('.model-name')?.innerText || '').toLowerCase();

            const isMatch = id.includes(lowerQuery) || type.includes(lowerQuery) || model.includes(lowerQuery);
            node.classList.toggle('hidden', !isMatch);
            if (isMatch) visibleCount++;
        });

        const grid = document.querySelector('.node-grid');
        const hintId = 'no-nodes-hint';
        if (visibleCount === 0) {
            if (!document.getElementById(hintId)) {
                const hint = document.createElement('div');
                hint.id = hintId;
                hint.style.cssText = 'grid-column: 1/-1; padding: 100px; text-align: center; color: var(--text-dim); font-style: italic;';
                hint.innerHTML = '🕳️ 未发现匹配的算力单元';
                grid.appendChild(hint);
            }
        } else {
            const hint = document.getElementById(hintId);
            if (hint) hint.remove();
        }
    },

    /**
     * 💾 固化算力调度策略
     */
    async saveComputeStrategy(event, skipRefetch = false) {
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
            'translation.max_chunk_size': t.max_chunk_size || 2500
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

            if (!skipRefetch) {
                const freshRes = await apiFetch('/api/system/config');
                const freshConfig = freshRes.config || freshRes;
                if (freshConfig.translation) {
                    window.settingsData.translation = freshConfig.translation;
                    this.syncStrategyBadge();
                }
            }
        } else {
            if (typeof showNotification === 'function') showNotification('❌ 固化失败: ' + (res?.error || '物理链路异常'), 'error');
        }
    },

    async resetComputeStrategy() {
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
    },
    
    /**
     * 🕹️ 视图切换调度 (职责归位)
     */
    switchComputeTab: async function(tab) {
        const container = document.getElementById('compute-tab-viewport');
        if (!container) return;

        // 切换 Tab 激活状态
        document.querySelectorAll('.tactical-tabs .t-tab').forEach(btn => {
            const isTarget = btn.getAttribute('onclick').includes(`'${tab}'`);
            btn.classList.toggle('active', isTarget);
        });

        // 动态调整顶部工具栏
        const topActions = document.getElementById('compute-header-actions-top');
        const navActions = document.getElementById('compute-nav-actions-slot');
        if (topActions) {
            const saveBtn = document.getElementById('btn-save-compute-strategy');
            const addNodeBtn = document.getElementById('btn-add-node');
            const probeNodesBtn = document.getElementById('btn-probe-nodes');
            const refreshBtn = document.getElementById('btn-refresh-compute');
            const resetBtn = document.getElementById('id-btn-reset-compute-strategy');

            if (tab === 'infrastructure') {
                topActions.style.display = 'flex';
                if (navActions) navActions.style.display = 'flex';
                if (saveBtn) saveBtn.style.display = 'none';
                if (resetBtn) resetBtn.style.display = 'none';
                if (addNodeBtn) addNodeBtn.style.display = 'flex';
                if (probeNodesBtn) probeNodesBtn.style.display = 'flex';
                if (refreshBtn) refreshBtn.style.display = 'flex';
            } else {
                topActions.style.display = 'none';
                if (navActions) navActions.style.display = 'flex';
                if (saveBtn) saveBtn.style.display = 'flex';
                if (resetBtn) resetBtn.style.display = 'flex';
                if (addNodeBtn) addNodeBtn.style.display = 'none';
                if (probeNodesBtn) probeNodesBtn.style.display = 'none';
                if (refreshBtn) refreshBtn.style.display = 'none';
            }
        }

        // 注入加载动画
        container.innerHTML = `
            <div class="loading-scanner">
                <div class="scan-line"></div>
                <p>正在扫描 ${tab === 'infrastructure' ? '算力资源' : '全域配置'}...</p>
            </div>
        `;

        if (tab === 'infrastructure') {
            await window.ComputeUI.renderInfrastructureTab(container);
        } else {
            await window.ComputeUI.renderStrategyTab(container);
        }
    },

    /**
     * 🎨 全局通知助手
     */
    showNotification: (text, type = 'success') => {
        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true
        });
        Toast.fire({ icon: type, title: text });
    }
};

/**
 * 🛰️ 桥接器：保持 HTML inline 事件绑定 100% 兼容
 */
window.probeNode = (id) => window.ComputeHandlers.probeNode(id);
window.editNode = (id) => window.ComputeHandlers.editNode(id);
window.switchComputeTab = (tab) => window.ComputeHandlers.switchComputeTab(tab);
window.showNotification = (text, type) => window.ComputeHandlers.showNotification(text, type);
window.showAddNodeModal = () => window.ComputeHandlers.showAddNodeModal();
window.probeAllNodes = () => window.ComputeHandlers.probeAllNodes();
window.filterNodes = (q) => window.ComputeHandlers.filterNodes(q);
window.saveComputeStrategy = (e) => window.ComputeHandlers.saveComputeStrategy(e);
