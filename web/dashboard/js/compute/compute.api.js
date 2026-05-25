/**
 * ⚙️ Illacme Compute Center - API Logic Shard
 * 职责：封装算力节点的所有异步请求逻辑。
 */

window.ComputeAPI = {
    /**
     * 📡 单点脉冲：测试节点健康度
     */
    async probeNode(id, endpoint) {
        const statusEl = document.getElementById(`probe-status-${id}`);
        if (statusEl) statusEl.innerHTML = '<span class="loading-spinner"></span> 探测中...';

        try {
            const res = await apiFetch('/api/compute/nodes/test', {
                method: 'POST',
                body: JSON.stringify({ id, endpoint })
            });
            if (statusEl) {
                const latency = res.latency || 'N/A';
                const statusColor = res.status === 'online' ? 'text-green-500' : 'text-red-500';
                statusEl.innerHTML = `<span class="${statusColor}">${res.status.toUpperCase()}</span> (${latency}ms)`;
            }
            return res;
        } catch (err) {
            if (statusEl) statusEl.innerHTML = '<span class="text-red-500">FAILED</span>';
            throw err;
        }
    },

    /**
     * 📡 全域脉冲：并行测试所有活动节点
     */
    async probeAllNodes() {
        const activeIds = window._activeNodeIds || [];
        if (activeIds.length === 0) return;

        console.log(`🚀 [全域脉冲] 启动对 ${activeIds.length} 个节点的并行探测...`);
        const promises = activeIds.map(id => {
            const card = document.querySelector(`[data-node-id="${id}"]`);
            const endpoint = card ? card.dataset.endpoint : '';
            return this.probeNode(id, endpoint).catch(e => console.error(`Node ${id} probe failed:`, e));
        });
        await Promise.all(promises);
    },

    /**
     * 🛰️ 模型感应：自动发现节点的可用模型
     */
    async discoverModels(id, endpoint, provider) {
        const menu = document.getElementById('asset-discovery-menu');
        if (menu) menu.innerHTML = '<li><a class="dropdown-item disabled">正在感应...</a></li>';

        try {
            const res = await apiFetch('/api/compute/models', {
                method: 'POST',
                body: JSON.stringify({ id, endpoint, provider })
            });

            if (menu) {
                if (res.models && res.models.length > 0) {
                    menu.innerHTML = res.models.map(m => `
                        <li><a class="dropdown-item" onclick="applyModelToNode('${id}', '${m}')">
                            <i class="bi bi-cpu me-2"></i>${m}
                        </a></li>
                    `).join('');
                } else {
                    menu.innerHTML = '<li><a class="dropdown-item disabled">未感应到可用模型</a></li>';
                }
            }
        } catch (err) {
            if (menu) menu.innerHTML = '<li><a class="dropdown-item text-red-500">感应失败</a></li>';
        }
    },

    /**
     * 🔒 固化策略：持久化算力调度配置
     */
    async saveComputeStrategy(strategy, primary, fallback, primaryModel, fallbackModel) {
        try {
            await apiFetch('/api/config/update', {
                method: 'POST',
                body: JSON.stringify({
                    "translation.strategy": strategy,
                    "translation.primary_node": primary,
                    "translation.fallback_node": fallback,
                    "translation.primary_model": primaryModel,
                    "translation.fallback_model": fallbackModel
                })
            });
            Swal.fire({
                icon: 'success',
                title: '算力策略已固化',
                toast: true,
                position: 'top-end',
                timer: 2000,
                showConfirmButton: false
            });
            // 重新刷新全局配置
            await apiFetch('/api/system/config');
            if (window.syncStrategyBadge) window.syncStrategyBadge();
        } catch (err) {
            Swal.fire('物理落盘失败', err.message, 'error');
        }
    }
};
