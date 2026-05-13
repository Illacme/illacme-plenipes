/**
 * 🕹️ Illacme Compute Center - Event Handlers Shard
 * 职责：负责算力中心的所有用户交互分发、联动逻辑与业务处理。
 */

window.ComputeHandlers = {
    /**
     * 🚀 [V74.80] 驱动-URL 联动基因
     */
    async selectProvider(protoId) {
        const urlInput = document.getElementById('swal-input-url');
        if (!urlInput) return;

        // 从缓存或 API 实时获取协议默认 URL
        try {
            const res = await apiFetch('/api/plugins/list');
            const proto = res.plugins.find(p => p.id === protoId);
            if (proto && proto.default_url) {
                urlInput.value = proto.default_url;
                urlInput.classList.add('flash-highlight');
                setTimeout(() => urlInput.classList.remove('flash-highlight'), 1000);
            }
        } catch (err) {
            console.error('Failed to fetch protocol defaults:', err);
        }
    },

    /**
     * 🔄 切换 Tab 路由逻辑
     */
    switchComputeTab(tabId) {
        // 1. 清除旧状态
        const root = document.getElementById('compute-center-root');
        if (!root) return;
        
        // 2. 注入特定 Tab 内容
        if (tabId === 'infrastructure') {
            window.ComputeUI.injectSearchHeader();
            // 渲染节点列表逻辑 (已由 loadComputeCenter 驱动)
        } else if (tabId === 'strategy') {
            const header = document.getElementById('compute-header-actions-top');
            if (header) header.innerHTML = ''; // 策略页不显示搜索框
        }
    },

    /**
     * 🔍 搜索过滤逻辑
     */
    filterNodes(query) {
        const q = query.toLowerCase();
        const cards = document.querySelectorAll('.compute-card');
        cards.forEach(card => {
            const id = card.dataset.nodeId.toLowerCase();
            const url = card.dataset.endpoint.toLowerCase();
            card.style.display = (id.includes(q) || url.includes(q)) ? 'block' : 'none';
        });
    },

    /**
     * 🔧 修改节点参数
     */
    editNode(id) {
        window.ComputeUI.showNodeModal(id);
    },

    /**
     * 💾 保存节点（固化至配置）
     */
    async saveNode(data) {
        try {
            const path = `translation.compute_nodes.${data.id}`;
            await apiFetch('/api/config/update', {
                method: 'POST',
                body: JSON.stringify({
                    [`${path}.type`]: data.type,
                    [`${path}.base_url`]: data.base_url,
                    [`${path}.api_key`]: data.api_key
                })
            });
            
            Swal.fire({ icon: 'success', title: '节点参数已固化', toast: true, position: 'top-end', timer: 1500 });
            
            // 强制重新加载以更新 UI
            if (window.loadComputeCenter) window.loadComputeCenter();
        } catch (err) {
            Swal.fire('保存失败', err.message, 'error');
        }
    }
};
