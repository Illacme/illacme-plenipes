/**
 * 🔌 [V1.0] Illacme Plenipes Design Studio - Provider Config Modal Shard
 * 职责：生图模型参数动态表单渲染、算力基座凭据一键智能同步与持久化。
 * 🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
 */

(function () {
    let _currentProviderId = null;
    let _suggestedOpenAI = null;

    window.openDesignProviderConfigModal = async function (providerId) {
        _currentProviderId = providerId;
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());

        let providers = window._designCachedProviders || [];
        let p = providers.find(item => item.id === providerId);
        if (!p) {
            try {
                const pRes = await fetchApi('/api/design/providers');
                if (pRes && pRes.providers) {
                    providers = pRes.providers;
                    window._designCachedProviders = providers;
                    p = providers.find(item => item.id === providerId);
                }
            } catch (e) {
                console.warn("Fetch providers failed:", e);
            }
        }
        if (!p) return;

        // 获取当前已持久化配置及算力建议
        let savedCfg = p.saved_config || {};
        try {
            const cfgRes = await fetchApi(`/api/design/providers/config?provider_id=${providerId}`);
            if (cfgRes && cfgRes.configs) {
                savedCfg = cfgRes.configs[providerId] || savedCfg;
                _suggestedOpenAI = cfgRes.suggested || null;
            }
        } catch (e) {
            console.warn("Fetch provider configs failed:", e);
        }

        let modal = document.getElementById('design-provider-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'design-provider-modal';
            modal.style.cssText = 'position:fixed; inset:0; background:rgba(0,0,0,0.75); backdrop-filter:blur(6px); z-index:999999; display:flex; align-items:center; justify-content:center;';
            document.body.appendChild(modal);
        }
        modal.style.display = 'flex';

        const fields = p.fields || [];
        const isCloud = (p.category === 'cloud_api');

        // 智能同步卡片 (支持 OpenAI / FLUX / 智谱 / Gemini 等同源节点自动识别)
        let syncNoticeHtml = '';
        if (_suggestedOpenAI && (_suggestedOpenAI.available || _suggestedOpenAI.has_openai)) {
            syncNoticeHtml = `
                <div style="background: rgba(99,102,241,0.12); border: 1px solid rgba(99,102,241,0.3); border-radius: 8px; padding: 10px 12px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div style="display: flex; flex-direction: column; gap: 2px;">
                        <span style="font-size: 0.76rem; font-weight: 600; color: #a5b4fc;">💡 算力基座已就绪同源节点</span>
                        <span style="font-size: 0.68rem; color: var(--text-dim);">节点: ${_suggestedOpenAI.node_name} (${_suggestedOpenAI.api_key_masked})</span>
                    </div>
                    <button type="button" class="mini-btn" onclick="window.syncDesignFromCompute('${providerId}')" style="padding: 5px 10px; font-size: 0.72rem; background: rgba(0,242,254,0.15); border: 1px solid rgba(0,242,254,0.35); color: #00f2fe; border-radius: 4px; cursor: pointer; white-space: nowrap;">
                        🔗 一键同步凭据
                    </button>
                </div>
            `;
        }

        modal.innerHTML = `
            <div class="glass-panel" style="width: 480px; max-width: 90vw; border-radius: 12px; padding: 22px; display: flex; flex-direction: column; gap: 14px; box-shadow: 0 20px 60px rgba(0,0,0,0.8); border: 1px solid rgba(255,255,255,0.15);">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px;">
                    <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #fff; font-size: 0.96rem;">
                        <span>${p.icon}</span>
                        <span>配置 ${p.name}</span>
                    </div>
                    <button type="button" onclick="document.getElementById('design-provider-modal').style.display='none'" style="background:none; border:none; color:var(--text-dim); cursor:pointer; font-size:1.2rem;">✕</button>
                </div>

                ${syncNoticeHtml}

                <form id="design-provider-form" onsubmit="event.preventDefault();" style="display: flex; flex-direction: column; gap: 12px;">
                    ${fields.map(f => {
                        const val = (savedCfg && savedCfg[f.key]) !== undefined ? savedCfg[f.key] : (f.default || '');
                        return `
                            <div style="display: flex; flex-direction: column; gap: 4px;">
                                <label style="font-size: 0.74rem; color: var(--text-dim); display: flex; justify-content: space-between;">
                                    <span>${f.label}</span>
                                    ${f.required ? '<span style="color:#f87171; font-size:0.65rem;">必填</span>' : ''}
                                </label>
                                <input type="${f.type || 'text'}" id="dp-field-${f.key}" data-key="${f.key}" value="${val}" placeholder="${f.default || ''}" style="width: 100%; padding: 8px 10px; border-radius: 6px; background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.15); color: #fff; font-size: 0.82rem; box-sizing: border-box;" />
                            </div>
                        `;
                    }).join('')}
                </form>

                <div style="display: flex; gap: 8px; justify-content: space-between; align-items: center; margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 12px;">
                    <div id="dp-modal-test-status" style="font-size: 0.74rem; color: var(--text-dim); display: flex; align-items: center; gap: 6px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 220px;">
                        <span>🔌 连通状态：待探测</span>
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <button type="button" class="mini-btn" onclick="document.getElementById('design-provider-modal').style.display='none'" style="padding: 6px 14px; font-size: 0.78rem; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); color: var(--text-dim); border-radius: 6px; cursor: pointer;">
                            取消
                        </button>
                        <button type="button" id="dp-modal-test-btn" class="mini-btn" onclick="window.saveAndTestDesignProvider()" style="padding: 6px 14px; font-size: 0.78rem; background: rgba(0,242,254,0.12); border: 1px solid rgba(0,242,254,0.3); color: #00f2fe; border-radius: 6px; cursor: pointer; transition: all 0.2s;">
                            🔌 测试连通
                        </button>
                        <button type="button" class="mini-btn glow-btn" onclick="window.saveDesignProviderConfig()" style="padding: 6px 18px; font-size: 0.78rem; font-weight: 700; background: var(--accent-secondary, #00f2fe); color: #000; border: none; border-radius: 6px; cursor: pointer;">
                            💾 保存配置
                        </button>
                    </div>
                </div>
            </div>
        `;
    };

    window.getDesignProviderFormValues = function () {
        const form = document.getElementById('design-provider-form');
        if (!form) return {};
        const inputs = form.querySelectorAll('input[data-key]');
        const cfg = {};
        inputs.forEach(ipt => {
            const k = ipt.getAttribute('data-key');
            cfg[k] = ipt.value.trim();
        });
        return cfg;
    };

    window.saveDesignProviderConfig = async function (silent = false) {
        if (!_currentProviderId) return false;
        const cfg = window.getDesignProviderFormValues();
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());

        try {
            const res = await fetchApi('/api/design/providers/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    provider_id: _currentProviderId,
                    config: cfg
                })
            });

            if (res && res.success) {
                if (!silent && typeof window.showToast === 'function') {
                    window.showToast(`✨ [${_currentProviderId}] 参数配置已保存生效`, 'success');
                }
                const modal = document.getElementById('design-provider-modal');
                if (modal && !silent) modal.style.display = 'none';
                if (typeof window.loadDesignCenter === 'function') {
                    window.loadDesignCenter('providers');
                }
                return true;
            } else {
                throw new Error((res && res.message) || '保存失败');
            }
        } catch (e) {
            if (typeof window.showToast === 'function') window.showToast(`🛑 保存失败: ${e.message}`, 'error');
            return false;
        }
    };

    window.saveAndTestDesignProvider = async function () {
        if (!_currentProviderId) return;
        const testBtn = document.getElementById('dp-modal-test-btn');
        const statusEl = document.getElementById('dp-modal-test-status');

        if (testBtn) {
            testBtn.disabled = true;
            testBtn.style.opacity = '0.7';
            testBtn.style.cursor = 'not-allowed';
            testBtn.innerText = '⏳ 探测中...';
        }
        if (statusEl) {
            statusEl.innerHTML = '<span style="color:#f59e0b; display:inline-flex; align-items:center; gap:4px;">⚙️ 保存并验证中...</span>';
        }

        try {
            const saved = await window.saveDesignProviderConfig(true);
            if (!saved) {
                if (statusEl) statusEl.innerHTML = '<span style="color:#f87171;">🛑 参数保存失败</span>';
                return;
            }

            const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
            const res = await fetchApi('/api/design/providers/test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ provider_id: _currentProviderId })
            });

            const ok = Boolean(res && res.success);
            const latency = res && res.latency_ms !== undefined ? `${res.latency_ms}ms` : '';
            const msg = (res && res.message) || (ok ? '在线' : '离线');

            if (statusEl) {
                statusEl.innerHTML = ok
                    ? `<span style="color:#00ff88; font-weight:600;">🟢 连通正常 (${latency})</span>`
                    : `<span style="color:#f87171; font-weight:500;" title="${msg}">🔴 失败: ${msg}</span>`;
            }

            const badge = document.getElementById(`provider-status-${_currentProviderId}`);
            if (badge) {
                badge.innerText = ok ? `🟢 在线 (${latency})` : `🔴 ${msg}`;
                badge.style.color = ok ? '#00ff88' : '#f87171';
            }

            if (typeof window.showToast === 'function') {
                if (ok) {
                    window.showToast(`✨ [${_currentProviderId}] 连通验证成功 (${latency})`, 'success');
                } else {
                    window.showToast(`🛑 [${_currentProviderId}] 连通验证失败: ${msg}`, 'error');
                }
            }
        } catch (e) {
            if (statusEl) statusEl.innerHTML = `<span style="color:#f87171;">🔴 异常: ${e.message}</span>`;
            if (typeof window.showToast === 'function') window.showToast(`🛑 连通探测异常: ${e.message}`, 'error');
        } finally {
            if (testBtn) {
                testBtn.disabled = false;
                testBtn.style.opacity = '1';
                testBtn.style.cursor = 'pointer';
                testBtn.innerText = '🔌 重新测试';
            }
        }
    };

    window.syncDesignFromCompute = async function (targetId) {
        const pid = targetId || _currentProviderId || 'openai';
        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const res = await fetchApi('/api/design/providers/sync-compute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ provider_id: pid })
            });

            if (res && res.success) {
                if (typeof window.showToast === 'function') window.showToast(`✅ [${pid}] 凭据已从算力基座无缝同步`, 'success');
                window.openDesignProviderConfigModal(pid);
            } else {
                throw new Error((res && res.message) || '同步失败');
            }
        } catch (e) {
            if (typeof window.showToast === 'function') window.showToast(`🛑 同步异常: ${e.message}`, 'error');
        }
    };
})();
