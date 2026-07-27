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
            <div class="tactical-info-pod glass-panel" style="padding: 20px; margin-bottom: 25px; border-left: 4px solid var(--neon-red, #ff4d4d); background: rgba(255, 77, 77, 0.05);">
                <div class="pod-label" style="font-size: 0.65rem; font-weight: 900; color: var(--neon-red, #ff4d4d); letter-spacing: 2px; margin-bottom: 8px;">⚠️ 算力总控已关闭 (COMPUTE DISABLED)</div>
                <div class="pod-desc" style="font-size: 0.85rem; color: var(--text-bright, #ffffff); line-height: 1.5;">
                    检测到 AI 算力总控处于关闭状态，下方配置的所有底座算力单元均处于不活跃待命状态。如需使用，请前往 <a href="javascript:void(0)" onclick="window.ComputeHandlers.switchComputeTab('strategy')" style="color: var(--accent-primary); text-decoration: underline;">调度策略</a> 页面开启。
                </div>
            </div>
            ` : `
            <div class="tactical-info-pod glass-panel" style="padding: 20px; margin-bottom: 25px; border-left: 4px solid var(--accent-secondary); background: rgba(0, 242, 255, 0.02);">
                <div class="pod-label" style="font-size: 0.65rem; font-weight: 900; color: var(--accent-secondary); letter-spacing: 2px; margin-bottom: 8px;">全域算力单元 (COMPUTE UNITS)</div>
                <div class="pod-desc" style="font-size: 0.85rem; color: var(--text-dim); line-height: 1.5;">
                    管理核心的算力供应资源，包括本地大模型、云端 API 等原子生产力单元。在此处定义的单元可被调度策略引用。
                </div>
            </div>
            `}
            <div class="node-grid">
                ${Object.entries(nodes)
            .sort((a, b) => (b[1].last_updated || 0) - (a[1].last_updated || 0))
            .map(([id, node]) => `
                    <div class="node-unit ${node.enabled !== false ? 'active' : 'inactive'}" id="node-unit-${id}" style="position: relative; ${isAiDisabled ? 'opacity: 0.5; pointer-events: none;' : ''}">
                        ${id === trans.primary_node ? '<div class="role-badge primary">PRIMARY</div>' : (id === trans.fallback_node && trans.strategy !== 'single') ? '<div class="role-badge fallback">FALLBACK</div>' : ''}
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
                                            <span class="node-model-badge" title="${node.model ? '节点专属指定模型: ' + node.model : '未指定物理模型，自动继承品牌装帧层策略: ' + (id === trans.primary_node ? (trans.primary_model || 'qwen/qwen3.5-9b') : (trans.fallback_model || trans.primary_model || 'qwen/qwen3.5-9b'))}">
                                                <span class="brain-icon">🧠</span>
                                                <span class="model-name">${node.model ? node.model : (id === trans.primary_node ? `继承品牌策略 (${trans.primary_model || 'qwen/qwen3.5-9b'})` : (id === trans.fallback_node ? `继承备用策略 (${trans.fallback_model || trans.primary_model || 'qwen/qwen3.5-9b'})` : `自适应品牌策略 (${trans.primary_model || 'qwen/qwen3.5-9b'})`))}</span>
                                            </span>
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
