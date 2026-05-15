/**
 * 🕹️ Illacme Compute Center - Diagnosis & Discovery Shard (V74.24 DECOUPLED)
 * 职责：承载活跃模型感应、资产发现及策略建议逻辑。
 * 🚀 物理对正：隶属于 window.ComputeHandlers 命名空间。
 */

(function() {
    const Diag = {
        /**
         * 📡 活跃模型感应
         */
        async discoverModels(event, nodeId) {
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }
            const btn = event?.currentTarget || event?.target;
            if (!btn) return;

            const originalText = btn.innerText;
            const type = document.getElementById('swal-input-type').value;
            const key = document.getElementById('swal-input-key').value;
            const url = document.getElementById('swal-input-url').value;
            const resultsContainer = document.getElementById('asset-discovery-menu');

            if (!type) {
                if (typeof addAudit === 'function') addAudit(`⚠️ 物理链路握手失败：请先选择算力协议。`, "warning");
                return;
            }

            btn.innerText = "正在感应...";
            btn.disabled = true;
            if (resultsContainer) {
                resultsContainer.innerHTML = '<div class="loading-mini">全域扫描中...</div>';
                resultsContainer.classList.add('show');
            }

            try {
                const query = new URLSearchParams({ node_id: nodeId, provider: type, api_key: key, base_url: url });
                const res = await apiFetch(`/api/compute/models?${query}`);

                if (res.models && res.models.length > 0) {
                    resultsContainer.innerHTML = `
                        <div class="dropdown-search-vessel">
                            <input type="text" class="dropdown-search-input" placeholder="🔍 检索感应资产..." 
                                   oninput="window.ComputeHandlers.filterDiscoveredModels(this.value)" onclick="event.stopPropagation()">
                        </div>
                        <div id="discovered-models-scroll" style="max-height: 200px; overflow-y: auto;">
                            ${res.models.map(m => `
                                <div class="dropdown-item" onclick="window.ComputeHandlers.selectDiscoveredModel('${m}')">
                                    <span>💎 ${m}</span>
                                </div>
                            `).join('')}
                        </div>
                    `;
                } else {
                    resultsContainer.innerHTML = '<div class="p-3 text-center text-muted">未发现活跃资产</div>';
                }
            } catch (e) {
                resultsContainer.innerHTML = '<div class="p-3 text-center text-danger">感应链路中断</div>';
            } finally {
                btn.innerText = originalText;
                btn.disabled = false;
            }
        },

        selectDiscoveredModel(model) {
            const input = document.getElementById('swal-input-model');
            if (input) input.value = model;
            document.querySelectorAll('.custom-dropdown-menu').forEach(m => m.classList.remove('show'));
        },

        filterDiscoveredModels(term) {
            const items = document.querySelectorAll('#discovered-models-scroll .dropdown-item');
            const lowerTerm = term.toLowerCase();
            items.forEach(item => {
                const name = item.innerText.toLowerCase();
                item.style.display = name.includes(lowerTerm) ? 'flex' : 'none';
            });
        },

        /**
         * 📡 策略页模型建议感应
         */
        async fetchNodeModels(nodeId, targetField) {
            const suggestions = document.getElementById(`${targetField}_suggestions`);
            if (!nodeId || !suggestions) return;

            suggestions.innerHTML = '<div class="suggestion-item loading">📡 正在感应单元模型...</div>';
            suggestions.classList.add('show');

            try {
                const res = await apiFetch(`/api/compute/models?node_id=${nodeId}`);
                if (res?.models?.length > 0) {
                    suggestions.innerHTML = res.models.map(m => `
                        <div class="suggestion-item" onclick="window.ComputeHandlers.applyModelSuggestion('${targetField}', '${m}')">
                            <span class="icon">💎</span> ${m}
                        </div>
                    `).join('');
                } else {
                    suggestions.innerHTML = '<div class="suggestion-item error">⚠️ 未感应到活跃模型</div>';
                }
            } catch (e) {
                suggestions.innerHTML = '<div class="suggestion-item error">🛑 感应链路中断</div>';
            }
        },

        applyModelSuggestion(targetField, model) {
            const input = document.getElementById(`${targetField}_input`);
            const suggestions = document.getElementById(`${targetField}_suggestions`);
            if (input) input.value = model;
            if (suggestions) {
                suggestions.innerHTML = '';
                suggestions.classList.remove('show');
            }
            window.ComputeHandlers.updateStrategy(targetField, model);
        }
    };

    // 🚀 [V74.24] 物理挂载至全局总线
    Object.assign(window.ComputeHandlers, Diag);
})();
