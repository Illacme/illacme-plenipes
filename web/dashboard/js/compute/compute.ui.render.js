/**
 * 🎨 Illacme Compute Center - UI Rendering Shard (V74.24 GENOME RESTORED)
 * 子职责：物理算力节点列表卡片渲染与遥测 Telemetry 数据拼装
 * 还原声明：本文件内容 100% 提取自 83b7900 基准版本，严禁 AI 瞎创造。
 */

if (!window.ComputeUI) {
    window.ComputeUI = {};
}

/**
 * 🧱 获取节点类型对应的 Emoji 图标
 */
window.ComputeUI.getNodeIcon = function(type) {
    const map = {
        'openai': '🌐', 'ollama': '🦙', 'anthropic': '🎭', 'groq': '⚡',
        'deepseek': '🐳', 'google': '💎', 'siliconflow': '🌊', 'lmstudio': '🏠'
    };
    return map[type?.toLowerCase()] || '🤖';
};

/**
 * 🧱 物理底座层：工业化动力单元渲染实现
 */
window.ComputeUI.renderInfrastructureTabImpl = async function(container) {
    // 🚀 [V74.24] 强化感应：始终在切换 Tab 时尝试从服务器拉取最新配置
    try {
        const res = await apiFetch('/api/system/config');
        const config = res.config || res;
        if (config.translation) {
            window.settingsData = window.settingsData || {};
            window.settingsData.translation = config.translation;
        }
    } catch (e) {
        console.warn("Soft sync failed, falling back to memory:", e);
    }
    if (typeof window.ComputeHandlers.syncStrategyBadge === 'function') {
        window.ComputeHandlers.syncStrategyBadge();
    }

    const trans = window.settingsData?.translation || {};
    const nodes = trans.compute_nodes || {};
    window._activeNodeIds = Object.keys(nodes);

    const isAiDisabled = trans.enable_ai === false;

    // 🔒 算力关闭时置灰相关导航行为按钮
    const addBtn = document.getElementById('btn-add-node');
    const probeBtn = document.getElementById('btn-probe-nodes');
    if (isAiDisabled) {
        if (addBtn) { addBtn.disabled = true; addBtn.style.opacity = '0.5'; addBtn.style.pointerEvents = 'none'; }
        if (probeBtn) { probeBtn.disabled = true; probeBtn.style.opacity = '0.5'; probeBtn.style.pointerEvents = 'none'; }
    } else {
        if (addBtn) { addBtn.disabled = false; addBtn.style.opacity = ''; addBtn.style.pointerEvents = ''; }
        if (probeBtn) { probeBtn.disabled = false; probeBtn.style.opacity = ''; probeBtn.style.pointerEvents = ''; }
    }

    let html = `
        <div class="infrastructure-hub" data-version="V74.35_STABLE" style="margin-top: 5px;">
            ${isAiDisabled ? `
            <div class="tactical-info-pod" style="padding: 12px 16px; margin-bottom: 18px; border-radius: 8px; border: 1px solid rgba(255, 77, 77, 0.3); background: rgba(255, 77, 77, 0.04); display: flex; align-items: center; justify-content: space-between;">
                <div style="font-size: 0.8rem; color: #ff6b6b; font-weight: 600;">⚠️ 算力总控已关闭：下方算力单元处于待命状态。如需启用，请前往 <a href="javascript:void(0)" onclick="window.ComputeHandlers.switchComputeTab('strategy')" style="color: var(--accent-primary); text-decoration: underline;">调度策略</a> 开启。</div>
            </div>
            ` : `
            <!-- 💡 顶部轻量说明栏：通透亲和，与调度策略统一风格 -->
            <div class="strategy-top-memo" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; margin-bottom: 18px; background: rgba(255, 255, 255, 0.015); border: 1px dashed var(--glass-border); border-radius: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 0.9rem;">🔌</span>
                    <span style="font-size: 0.78rem; color: var(--text-dim);">管理本地大模型 (LM Studio / Ollama) 与云端 API 原子算力单元</span>
                </div>
                <div style="display: inline-flex; align-items: center; gap: 6px; background: rgba(0, 242, 255, 0.05); border: 1px solid rgba(0, 242, 255, 0.2); padding: 3px 10px; border-radius: 6px;">
                    <span style="font-size: 0.68rem; color: var(--text-dim);">可用单元:</span>
                    <span style="font-size: 0.74rem; font-weight: 700; color: var(--accent-secondary);">${Object.keys(nodes).length} 个节点</span>
                </div>
            </div>
            `}
            <div class="node-grid">
                ${Object.entries(nodes)
            .sort((a, b) => (b[1].last_updated || 0) - (a[1].last_updated || 0))
            .map(([id, node]) => `
                    <div class="node-unit ${node.enabled !== false ? 'active' : 'inactive'}" id="node-unit-${id}" style="position: relative; ${isAiDisabled ? 'opacity: 0.5; pointer-events: none;' : ''}">
                        ${(() => {
                            if (trans.strategy === 'concurrent') {
                                const concurrentNodes = Array.isArray(trans.concurrent_nodes) && trans.concurrent_nodes.length > 0
                                    ? trans.concurrent_nodes
                                    : [trans.primary_node, trans.fallback_node].filter(Boolean);
                                if (concurrentNodes.includes(id)) {
                                    return '<div class="role-badge" style="background: linear-gradient(135deg, rgba(255, 183, 0, 0.25), rgba(255, 77, 77, 0.25)); color: #ffb700; border: 1px solid rgba(255, 183, 0, 0.5); font-size: 0.62rem; font-weight: 800; padding: 2px 6px; border-radius: 4px; position: absolute; top: 12px; right: 12px; letter-spacing: 0.5px; box-shadow: 0 0 8px rgba(255, 183, 0, 0.3);">RACE 竞速</div>';
                                }
                            }
                            if (id === trans.primary_node) return '<div class="role-badge primary">PRIMARY</div>';
                            if (id === trans.fallback_node && trans.strategy !== 'single') return '<div class="role-badge fallback">FALLBACK</div>';
                            return '';
                        })()}
                        <div class="node-header">
                            <div class="node-identity">
                                <div class="node-icon-vessel">
                                    ${this.getNodeIcon(node.type)}
                                </div>
                                <div class="node-name-group">
                                <div class="node-name-vessel">
                                    <div class="node-name" title="${id}">${id}</div>
                                </div>
                                    <div class="node-meta-line">
                                        <div class="text-marquee-wrapper" style="max-width: 120px;">
                                            <span class="node-type" title="${node.provider_name || node.type?.toUpperCase()}">${node.provider_name || node.type?.toUpperCase()}</span>
                                        </div>
                                        <div class="protocol-badge ${node.protocol_family}">
                                            ${node.protocol_family === 'standard' ? 'V1' : node.protocol_family === 'anthropic' ? 'V2' : 'NATIVE'}
                                        </div>
                                    </div>
                                    <div class="node-model-line">
                                        <div class="model-marquee-vessel">
                                            ${(() => {
                                                const isEnabled = node.enabled !== false && node.is_enabled !== false;
                                                const isPrimary = id === trans.primary_node;
                                                const isFallback = id === trans.fallback_node && trans.strategy !== 'single';
                                                
                                                if (!isEnabled) {
                                                    return `
                                                        <span class="node-model-badge disabled-badge" title="算力单元已被禁用" style="opacity: 0.65; background: rgba(255,255,255,0.05); color: var(--text-dim);">
                                                            <span class="brain-icon">⚪</span>
                                                            <span class="model-name">单元未开启</span>
                                                        </span>
                                                    `;
                                                }
                                                
                                                if (node.model) {
                                                    return `
                                                        <span class="node-model-badge" title="节点专属指定模型: ${node.model}">
                                                            <span class="brain-icon">🧠</span>
                                                            <span class="model-name">${node.model}</span>
                                                        </span>
                                                    `;
                                                }

                                                if (isPrimary) {
                                                    return `
                                                        <span class="node-model-badge" title="未指定专属物理模型，自动继承品牌装帧层主力策略">
                                                            <span class="brain-icon">🧠</span>
                                                            <span class="model-name">继承品牌策略 (${trans.primary_model || 'qwen/qwen3.5-9b'})</span>
                                                        </span>
                                                    `;
                                                } else if (isFallback) {
                                                    return `
                                                        <span class="node-model-badge fallback-badge" title="未指定专属物理模型，自动继承品牌装帧层备用策略">
                                                            <span class="brain-icon">🧠</span>
                                                            <span class="model-name">继承备用策略 (${trans.fallback_model || trans.primary_model || 'qwen/qwen3.5-9b'})</span>
                                                        </span>
                                                    `;
                                                } else {
                                                    return `
                                                        <span class="node-model-badge standby-badge" title="当前节点处于待命状态，未与调度策略绑定" style="opacity: 0.75; background: rgba(255,255,255,0.04);">
                                                            <span class="brain-icon">⚪</span>
                                                            <span class="model-name">待命未连接</span>
                                                        </span>
                                                    `;
                                                }
                                            })()}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="node-actions">
                                <button class="tactical-btn" onclick="window.ComputeHandlers.probeNode('${id}')" title="全域脉冲探测">📡</button>
                                <button class="tactical-btn" onclick="window.ComputeHandlers.editNode('${id}')" title="单元参数修正">⚙️</button>
                            </div>
                        </div>

                        <!-- 📡 Telemetry Data -->
                        <div class="node-telemetry">
                            <div class="t-item">
                                <div class="label">健康分</div>
                                <div class="value ${node.health?.score > 80 ? 'healthy' : 'warning'}">${node.health?.score || 100}</div>
                            </div>
                            <div class="t-item">
                                <div class="label">平均延迟</div>
                                <div class="value">${node.health?.avg_latency || 0}ms</div>
                              </div>
                              <div class="t-item">
                                  <div class="label">成功率</div>
                                  <div class="value">${node.health?.success_rate || 100}%</div>
                              </div>
                              <div class="t-item">
                                  <div class="label">物理延迟</div>
                                  <div class="value" id="latency-${id}">-- ms</div>
                              </div>
                          </div>

                          <div class="node-meta-footer" style="display: flex; justify-content: space-between; font-size: 0.6rem; color: var(--text-dim); margin-bottom: 8px; opacity: 0.6; font-family: var(--font-mono);">
                              <span>最后同步: ${node.last_updated ? new Date(node.last_updated).toLocaleString() : '从未感应'}</span>
                          </div>
                          
                          <div class="node-status-line" id="probe-status-${id}">📡 物理链路待命，准备感应...</div>
                      </div>
                  `).join('')}
              </div>
          </div>
      `;
      container.innerHTML = html;
  };
