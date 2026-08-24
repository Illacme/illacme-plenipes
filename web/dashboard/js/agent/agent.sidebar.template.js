/**
 * 🚀 Illacme Plenipes UI - Right Copilot Sidebar Template Shard
 * 职责：右侧 Sovereign Copilot 智能体交互、思维链设置、模型能力面板、指令推荐与实时审计流 DOM 动态挂载。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
 */

window.ensureRightSidebarMounted = function () {
    const sidebar = document.getElementById('right-sidebar');
    if (!sidebar || sidebar.children.length > 0) return;

    sidebar.innerHTML = `
        <!-- 🧠 Agent Sovereign Copilot Pod -->
        <div class="sidebar-pod agent-pod">
            <div class="pod-header"
                style="display: flex; align-items: center; justify-content: space-between; padding: 12px 15px 8px 15px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="pod-title">SOVEREIGN COPILOT</span>
                    <span class="version-tag tiny" id="agent-status-tag">🟢 待命</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <button id="agent-settings-toggle-btn" class="icon-btn" title="算力思维链配置"
                        style="background: none; border: none; color: var(--text-dim); cursor: pointer; font-size: 0.95rem; width: 20px; height: 20px; padding: 0; outline: none; transition: all 0.2s ease; display: flex; align-items: center; justify-content: center;">⚙️</button>
                    <button id="agent-widescreen-toggle-btn" class="icon-btn" title="切换宽屏大屏模式"
                        style="background: none; border: none; color: var(--text-dim); cursor: pointer; font-size: 0.95rem; width: 20px; height: 20px; padding: 0; outline: none; transition: all 0.2s ease; display: flex; align-items: center; justify-content: center; margin-left: 2px;">⛶</button>
                </div>
            </div>
            <!-- 🧠 算力及自治控制面板 (V76.1) -->
            <div class="agent-engine-settings" style="display: flex; flex-direction: column; gap: 8px;">
                <!-- 🆕 模型能力标签面板 (V76.2) -->
                <div class="model-capability-panel">
                    <div
                        style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px;">
                        <span style="font-size: 0.6rem; color: var(--text-dim); letter-spacing: 0.5px;">AI 助手大模型:</span>
                        <span id="active-model-name"
                            style="font-size: 0.6rem; font-family: var(--font-mono); color: var(--accent-secondary); font-weight: bold; background: var(--neon-cyan-05); padding: 1px 5px; border-radius: 3px; border: 1px solid var(--neon-cyan-15);">加载中...</span>
                    </div>
                    <div style="display: flex; gap: 4px; flex-wrap: wrap;">
                        <span id="badge-cot" class="cap-badge disabled" title="支持原生思维链逻辑或深度推理 (Reasoning CoT)"><span
                                class="dot"></span>CoT 推理</span>
                        <span id="badge-tools" class="cap-badge disabled" title="已打通本地文件读写、指令执行等工具权限"><span
                                class="dot"></span>工具自治</span>
                        <span id="badge-stream" class="cap-badge disabled" title="支持高吞吐、零延迟 SSE 流式响应"><span
                                class="dot"></span>流式极速</span>
                        <span id="badge-vision" class="cap-badge disabled" title="当前模型不支持图像或多模态输入">视觉模态</span>
                    </div>
                </div>
                <div class="settings-row"
                    style="display: flex; align-items: center; justify-content: space-between; width: 100%; gap: 10px;">
                    <div class="setting-item">
                        <span title="开启后使用 SSE 打字机流式增量输出，关闭后回退完整同步输出"><span class="setting-icon">⚡</span>流式极速</span>
                        <label class="switch-container">
                            <input type="checkbox" id="agent-stream-toggle" checked>
                            <span class="switch-slider"></span>
                        </label>
                    </div>
                </div>
                <div class="settings-row"
                    style="display: flex; align-items: center; justify-content: space-between; width: 100%; gap: 10px;">
                    <div class="setting-item">
                        <span><span class="setting-icon">🧠</span>思维链</span>
                        <label class="switch-container">
                            <input type="checkbox" id="agent-reasoning-toggle">
                            <span class="switch-slider"></span>
                        </label>
                    </div>
                    <div class="setting-item" id="agent-reasoning-depth-container"
                        title="针对云端/标准模型调控推理深度(Low/Medium/High)；本地模型(LMStudio/Ollama)由洗涤网关自动转译对准">
                        <span>深度:</span>
                        <select id="agent-reasoning-depth">
                            <option value="medium">Medium</option>
                            <option value="low">Low</option>
                            <option value="high">High</option>
                        </select>
                    </div>
                </div>
                <div class="settings-row"
                    style="display: flex; align-items: center; justify-content: space-between; width: 100%; gap: 10px;">
                    <div class="setting-item">
                        <span title="启用后，Agent 将自动执行 Write/Commit 等写操作，无需人工物理审批"><span
                                class="setting-icon">🤖</span>自动驾驶</span>
                        <label class="switch-container">
                            <input type="checkbox" id="agent-autopilot-toggle">
                            <span class="switch-slider autopilot-slider"></span>
                        </label>
                    </div>
                    <div class="setting-item">
                        <span>上限:</span>
                        <select id="agent-max-iterations">
                            <option value="5">5 轮</option>
                            <option value="10" selected>10 轮</option>
                            <option value="15">15 轮</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="agent-feed-container scroll-container scanline-overlay" id="agent-feed">
                <div class="agent-msg system-msg" id="agent-default-welcome"
                    style="border-left: 2px solid var(--accent-secondary); background: var(--neon-cyan-03); padding: 10px 12px; border-radius: 8px; font-style: normal; display: flex; flex-direction: column; gap: 6px; box-shadow: var(--shadow-glow);">
                    <div
                        style="font-weight: bold; color: var(--accent-secondary); font-size: 0.72rem; display: flex; align-items: center; gap: 6px; letter-spacing: 0.5px;">
                        🤖 SOVEREIGN COPILOT 已就绪</div>
                    <p style="margin: 0; line-height: 1.45; color: var(--text-dim); font-size: 0.68rem;">我是你的 AI
                        协同助手，已打通本地算力与工具箱，可以协助你管理这套数字出版系统。</p>
                    <div
                        style="font-size: 0.65rem; color: var(--text-dim); line-height: 1.5; margin-top: 4px; display: flex; flex-direction: column; gap: 8px;">
                        <span
                            style="display: block; font-weight: bold; color: var(--neon-amber); font-size: 0.68rem;">💡
                            点击推荐指令直接交互：</span>

                        <div>
                            <span
                                style="display: block; font-weight: 700; color: var(--text-bright); margin-bottom: 2px;">🔍
                                智能文库检索与分析：</span>
                            • <code class="clickable-suggestion"
                                style="color: var(--accent-secondary); background: var(--neon-cyan-06); padding: 2px 6px; border-radius: 4px; cursor: pointer; border: 1px solid var(--neon-cyan-12); font-size: 0.62rem; display: inline-block; margin: 2px 0; transition: all 0.2s ease;">在文稿库中搜索“大宪章”</code>
                            (全局搜索)<br />
                            • <code class="clickable-suggestion"
                                style="color: var(--accent-secondary); background: var(--neon-cyan-06); padding: 2px 6px; border-radius: 4px; cursor: pointer; border: 1px solid var(--neon-cyan-12); font-size: 0.62rem; display: inline-block; margin: 2px 0; transition: all 0.2s ease;">阅读 README.md</code>
                            (直接读取首页)
                        </div>

                        <div>
                            <span
                                style="display: block; font-weight: 700; color: var(--text-bright); margin-bottom: 2px;">🛠️
                                高效增量修改 (安全避开 4096 截断)：</span>
                            • <code class="clickable-suggestion"
                                style="color: var(--accent-secondary); background: var(--neon-cyan-06); padding: 2px 6px; border-radius: 4px; cursor: pointer; border: 1px solid var(--neon-cyan-12); font-size: 0.62rem; display: inline-block; margin: 2px 0; transition: all 0.2s ease;">在 README.md 的物理主权演进存证里追加一条 v31.2 迭代记录</code>
                            (触发 patch_document 局部微创修补，体验一键撤销)
                        </div>

                        <div>
                            <span
                                style="display: block; font-weight: 700; color: var(--text-bright); margin-bottom: 2px;">🎭
                                治理大宪章 SOP-05 协作模板：</span>
                            • <code class="clickable-suggestion"
                                style="color: var(--accent-secondary); background: var(--neon-cyan-06); padding: 2px 6px; border-radius: 4px; cursor: pointer; border: 1px solid var(--neon-cyan-12); font-size: 0.62rem; display: inline-block; margin: 2px 0; transition: all 0.2s ease;">使用【模板三：UI样式调整】优化 dashboard.agent.css 中的微型 diff 卡片间隙</code>
                            (像素级对齐)<br />
                            • <code class="clickable-suggestion"
                                style="color: var(--accent-secondary); background: var(--neon-cyan-06); padding: 2px 6px; border-radius: 4px; cursor: pointer; border: 1px solid var(--neon-cyan-12); font-size: 0.62rem; display: inline-block; margin: 2px 0; transition: all 0.2s ease;">系统启动报错，请启动【模板四：系统重启】进行故障诊断</code>
                            (自动检测与自愈)
                        </div>

                        <div>
                            <span
                                style="display: block; font-weight: 700; color: var(--text-bright); margin-bottom: 2px;">📡
                                系统状态与遥测监视：</span>
                            • <code class="clickable-suggestion"
                                style="color: var(--accent-secondary); background: var(--neon-cyan-06); padding: 2px 6px; border-radius: 4px; cursor: pointer; border: 1px solid var(--neon-cyan-12); font-size: 0.62rem; display: inline-block; margin: 2px 0; transition: all 0.2s ease;">系统当前负载怎么样？底层的各项微服务在线吗？</code>
                            (状态审计)
                        </div>
                    </div>
                </div>
            </div>
            <div class="agent-input-wrapper">
                <input type="text" id="agent-command-input" placeholder="输入指令，如“系统状态” (Cmd+K)..."
                    autocomplete="off">
            </div>
        </div>

        <!-- 📑 Intelligence Feed Pod: SIGNAL INTELLIGENCE (默认物理隐藏，可点击状态栏动态切换) -->
        <div class="sidebar-pod feed-pod" id="audit-feed-pod"
            style="display: none; height: 180px; flex-shrink: 0; margin-top: 10px;">
            <div class="pod-header" style="display: flex; justify-content: space-between; align-items: center;">
                <span class="pod-title">SIGNAL INTELLIGENCE</span>
                <span class="version-tag tiny"
                    style="color: var(--accent-secondary); border-color: var(--neon-cyan-20); background: none; font-size: 0.58rem;">LIVE
                    AUDIT</span>
            </div>
            <div id="audit-feed" class="scroll-container scanline-overlay"
                style="flex: 1; overflow-y: auto; padding: 8px 10px; font-family: var(--font-mono); font-size: 0.65rem; display: flex; flex-direction: column; gap: 6px;">
                <!-- Dynamic Audit Entries -->
            </div>
        </div>
    `;
};

// 自动挂载右侧边栏
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.ensureRightSidebarMounted);
} else {
    window.ensureRightSidebarMounted();
}
