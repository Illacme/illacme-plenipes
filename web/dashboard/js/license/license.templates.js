/**
 * 💎 Illacme Plenipes License & Help Center Templates Module
 * 职责：治理中心“💎 授权帮助” Sub-Tab 界面模版与对比表格渲染。
 * 遵循 SOP-01 单文件 300 行红线拆分。
 */

(function () {
    const licenseSubDescs = {
        activation: '💡 查看当前设备的硬件标识 (机器指纹)，或拖拽/粘贴许可证文件激活专业版功能。',
        comparison: '💡 查看免费社区版与高级专业版的核心功能对比说明。',
        docs: '💡 查阅快速上手教程、Obsidian 金库配置规范及常见问题排错指南。'
    };

    window.renderLicenseCategoryHTML = function (activeSub) {
        return `
            <div class="category-header-banner" style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px; padding: 18px 22px; background: rgba(0, 242, 255, 0.03); border: 1px solid var(--glass-border); border-radius: 12px; backdrop-filter: blur(10px);">
                <div style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <h2 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: var(--text-main); letter-spacing: 0.5px;">💎 授权与帮助中心</h2>
                    </div>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <button type="button" class="action-btn" id="btn-refresh-lic-status" onclick="if(typeof window.refreshLicenseStatusWithFeedback==='function'){window.refreshLicenseStatusWithFeedback();}else if(typeof window.fetchLicenseDataAndUpdateDOM==='function'){window.fetchLicenseDataAndUpdateDOM();}" style="padding: 4px 12px; font-size: 0.78rem; cursor: pointer; transition: all 0.25s;">🔄 刷新授权状态</button>
                    </div>
                </div>

                <div class="sub-tab-navigation-bar" id="license-sub-tab-bar" style="display: flex; gap: 8px; margin-top: 10px; border-bottom: 1px solid var(--glass-border); padding-bottom: 10px;">
                    <button type="button" class="sub-tab-btn ${activeSub === 'activation' ? 'active' : ''}" onclick="window.switchLicenseSubTab('activation', this)" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">🔑 激活授权</button>
                    <button type="button" class="sub-tab-btn ${activeSub === 'comparison' ? 'active' : ''}" onclick="window.switchLicenseSubTab('comparison', this)" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">📊 版本对比</button>
                    <button type="button" class="sub-tab-btn ${activeSub === 'docs' ? 'active' : ''}" onclick="window.switchLicenseSubTab('docs', this)" style="padding: 6px 14px; font-size: 0.82rem; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;">📖 使用指南</button>
                </div>

                <div id="lic-sub-tab-desc" style="font-size: 0.82rem; color: var(--text-muted); margin-top: 4px;">
                    ${licenseSubDescs[activeSub] || ''}
                </div>
            </div>

            <div class="tab-sub-content-wrapper">
                <div id="lic-panel-activation" style="display: ${activeSub === 'activation' ? 'block' : 'none'};">
                    <div class="settings-grid" style="display: flex; flex-direction: column; gap: 16px;">
                        <div class="setting-row level-global" style="flex-direction: column; align-items: stretch; padding: 18px 22px; border-radius: 12px; gap: 14px;">
                            <div style="display: flex; align-items: flex-start; gap: 16px; width: 100%;">
                                <div id="lic-emblem-container" style="width: 52px; height: 52px; min-width: 52px; border-radius: 12px; background: rgba(0, 242, 255, 0.08); border: 1px solid rgba(0, 242, 255, 0.25); display: flex; align-items: center; justify-content: center; font-size: 1.6rem; transition: all 0.3s ease;">
                                    🌱
                                </div>
                                
                                <div class="setting-info" style="margin: 0; flex: 1;">
                                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; width: 100%;">
                                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: nowrap; white-space: nowrap;">
                                            <span style="font-size: 0.98rem; font-weight: 800; color: var(--text-main); white-space: nowrap;">出版引擎版本</span>
                                            <span class="tier-tag tier-local" id="lic-tier-badge" style="font-size: 0.75rem; padding: 2px 8px; font-weight: 700; white-space: nowrap;">免费社区版</span>
                                            <span class="tier-tag tier-global" id="lic-version-badge" style="font-size: 0.72rem; padding: 2px 8px; font-weight: 600; opacity: 0.85; white-space: nowrap;">v11.2</span>
                                        </div>
                                        <button type="button" class="primary-btn" id="btn-revoke-license" onclick="window.revokeCurrentLicense(event)" style="display:none; background: rgba(255,50,50,0.15); border-color: rgba(255,50,50,0.3); color: #ff6b6b; padding: 3px 10px; font-size: 0.75rem;">🔓 解绑授权</button>
                                    </div>
                                    <div class="setting-desc" id="lic-banner-desc" style="font-size: 0.82rem; line-height: 1.4; color: var(--text-muted);">
                                        ✨ 免费社区版已包含完整 AI 创作润色、Obsidian 双链全息图谱与全自动静态出版引擎。激活专业版可进一步解封无限品牌隔离、50+ 语种并行矩阵分发与子目录频道映射。
                                    </div>
                                </div>
                            </div>

                            <div id="lic-feature-pills" style="display: flex; gap: 6px; flex-wrap: wrap; width: 100%; border-top: 1px solid var(--glass-border); padding-top: 12px; margin-top: 2px;">
                                <span class="lic-pill-unlocked">✓ 工业级 AI 出版引擎</span>
                                <span class="lic-pill-unlocked">✓ Obsidian 双链全息图谱</span>
                                <span class="lic-pill-unlocked">✓ 创作中心灵感润色</span>
                                <span class="lic-pill-unlocked">✓ 算力节点灵活对接</span>
                                <span class="lic-pill-unlocked">✓ 单品牌全渠道分发</span>
                                <span class="lic-pill-locked">🔒 无限品牌独立隔离 (专业版)</span>
                                <span class="lic-pill-locked">🔒 50+语种矩阵分发 (专业版)</span>
                                <span class="lic-pill-locked">🔒 子目录频道映射 (专业版)</span>
                                <span class="lic-pill-locked">🔒 频道专属方言风格 (专业版)</span>
                                <span class="lic-pill-locked">🔒 算力集群自动容灾 (专业版)</span>
                            </div>
                        </div>

                        <div class="setting-row level-local" style="flex-direction: column; align-items: stretch; padding: 16px 20px; border-radius: 10px;">
                            <div class="setting-info" style="margin-bottom: 10px;">
                                <div class="setting-label" style="font-size: 0.92rem;">
                                    <b>💻 设备唯一标识 (机器指纹)</b>
                                </div>
                                <div class="setting-desc" style="font-size: 0.8rem;">此标识基于当前设备的硬件特征生成，用于绑定专属授权证书。</div>
                            </div>
                            <div style="display: flex; gap: 10px; align-items: center; width: 100%;">
                                <input type="text" id="input-machine-fingerprint" class="setting-input" value="读取中..." readonly style="flex: 1; font-family: monospace; letter-spacing: 1.5px; font-weight: bold; font-size: 0.92rem; padding: 8px 12px;">
                                <button type="button" class="primary-btn glow-btn" id="btn-copy-fp" onclick="window.copyMachineFingerprint()" style="white-space: nowrap; padding: 8px 16px; font-weight: bold; font-size: 0.82rem;">📋 复制设备标识</button>
                            </div>
                        </div>

                        <div class="setting-row level-global" style="flex-direction: column; align-items: stretch; padding: 16px 20px; border-radius: 10px;">
                            <div class="setting-info" style="margin-bottom: 10px;">
                                <div class="setting-label" style="font-size: 0.92rem;">
                                    <b>🔑 导入授权文件 / 激活码</b>
                                </div>
                                <div class="setting-desc" style="font-size: 0.8rem;">将官方发放的 <code>.lic</code> 许可证文本粘贴至下方，或直接将 <code>.lic</code> 文件拖拽至此区域。</div>
                            </div>
                            <div style="display: flex; flex-direction: column; gap: 12px; width: 100%;">
                                <textarea id="license-text-input" class="setting-input" rows="4" placeholder="请粘贴官方 .lic 密钥内容，或拖拽 .lic 文件到此处..." style="width: 100%; box-sizing: border-box; font-family: monospace; resize: vertical; padding: 12px; border-style: dashed; border-width: 1.5px; transition: all 0.25s;"></textarea>
                                <div style="display: flex; justify-content: flex-end; align-items: center; width: 100%;">
                                    <button type="button" class="primary-btn glow-btn" id="btn-activate-license" onclick="window.submitLicenseActivation()" style="padding: 8px 22px; font-size: 0.85rem; font-weight: bold;">🚀 验证并激活</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div id="lic-panel-comparison" style="display: ${activeSub === 'comparison' ? 'block' : 'none'};">
                    <div class="settings-grid">
                        <div class="setting-row level-global" style="flex-direction: column; align-items: stretch; padding: 18px 22px; border-radius: 10px;">
                            <div style="overflow-x: auto; width: 100%;">
                                <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.85rem;">
                                    <thead>
                                        <tr style="border-bottom: 2px solid rgba(0, 242, 255, 0.4);">
                                            <th style="padding: 14px 10px; font-size: 0.95rem; font-weight: 800; color: var(--text-main); letter-spacing: 0.5px;">核心功能特性</th>
                                            <th style="padding: 14px 10px; width: 22%; font-size: 0.92rem; font-weight: 800; color: var(--text-muted); letter-spacing: 0.5px;">🌱 免费社区版</th>
                                            <th style="padding: 14px 10px; width: 26%; font-size: 0.95rem; font-weight: 800; color: var(--neon-cyan, #00f2fe); letter-spacing: 0.5px; text-shadow: 0 0 8px rgba(0,242,254,0.2);">🚀 基础增强版</th>
                                            <th style="padding: 14px 10px; width: 26%; font-size: 0.98rem; font-weight: 800; color: var(--accent-secondary, #00f2fe); letter-spacing: 0.5px; text-shadow: 0 0 10px rgba(0,242,255,0.3);">💎 旗舰专业版</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr style="border-bottom: 1px solid var(--glass-border);">
                                            <td style="padding: 12px 10px;"><b>多品牌独立管理</b><br><span style="font-size: 0.75rem; color: var(--text-muted);">独立文库与全套样式隔离</span></td>
                                            <td style="padding: 12px 10px; color: var(--text-muted);">仅限 1 个主品牌 (default)</td>
                                            <td style="padding: 12px 10px; color: var(--neon-cyan); font-weight: 600;">✓ 3 个独立出版品牌</td>
                                            <td style="padding: 12px 10px;" class="lic-table-pro-feature">✓ ♾️ 无限独立品牌</td>
                                        </tr>
                                        <tr style="border-bottom: 1px solid var(--glass-border);">
                                            <td style="padding: 12px 10px;"><b>多语种自动翻译</b><br><span style="font-size: 0.75rem; color: var(--text-muted);">全语种多线程并行翻译分发</span></td>
                                            <td style="padding: 12px 10px; color: var(--text-muted);">仅限 1 个目标语种</td>
                                            <td style="padding: 12px 10px; color: var(--neon-cyan); font-weight: 600;">✓ 3~5 个主流语种</td>
                                            <td style="padding: 12px 10px;" class="lic-table-pro-feature">✓ 🌐 50+ 语种并行翻译分发</td>
                                        </tr>
                                        <tr style="border-bottom: 1px solid var(--glass-border);">
                                            <td style="padding: 12px 10px;"><b>子目录频道映射</b><br><span style="font-size: 0.75rem; color: var(--text-muted);">金库子目录精准频道路由</span></td>
                                            <td style="padding: 12px 10px; color: var(--text-muted);">仅根目录全局映射</td>
                                            <td style="padding: 12px 10px; color: var(--neon-cyan); font-weight: 600;">✓ 📂 多子目录精准频道映射</td>
                                            <td style="padding: 12px 10px;" class="lic-table-pro-feature">✓ 📂 多子目录精准频道映射</td>
                                        </tr>
                                        <tr style="border-bottom: 1px solid var(--glass-border);">
                                            <td style="padding: 12px 10px;"><b>装帧主题排版</b><br><span style="font-size: 0.75rem; color: var(--text-muted);">多 SSG 引擎换装与定制</span></td>
                                            <td style="padding: 12px 10px; color: var(--text-muted);">全量主题自由切换</td>
                                            <td style="padding: 12px 10px; color: var(--neon-cyan); font-weight: 600;">✓ 全量主题 + 自定义样式注入</td>
                                            <td style="padding: 12px 10px;" class="lic-table-pro-feature">✓ 全量主题 + 专属装帧母本克隆</td>
                                        </tr>
                                        <tr style="border-bottom: 1px solid var(--glass-border);">
                                            <td style="padding: 12px 10px;"><b>多风格润色方言</b><br><span style="font-size: 0.75rem; color: var(--text-muted);">按语种/目录独立润色风格</span></td>
                                            <td style="padding: 12px 10px; color: var(--text-muted);">标准统一润色</td>
                                            <td style="padding: 12px 10px; color: var(--text-muted);">标准统一润色</td>
                                            <td style="padding: 12px 10px;" class="lic-table-pro-feature">✓ 🎭 专属多维润色风格库</td>
                                        </tr>
                                        <tr style="border-bottom: 1px solid var(--glass-border);">
                                            <td style="padding: 12px 10px;"><b>AI 算力联合调度</b><br><span style="font-size: 0.75rem; color: var(--text-muted);">云端与本地节点并发负载均衡</span></td>
                                            <td style="padding: 12px 10px; color: var(--text-muted);">单节点手动切换</td>
                                            <td style="padding: 12px 10px; color: var(--neon-cyan); font-weight: 600;">✓ ⚡ 双节点主备自动容灾</td>
                                            <td style="padding: 12px 10px;" class="lic-table-pro-feature">✓ ☁️ 混合算力多节点自动容灾</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                            <div style="margin-top: 16px; text-align: center; border: 1px dashed var(--glass-border); border-radius: 8px; padding: 12px;">
                                <span style="font-size: 0.85rem; color: var(--text-main);">需要解锁 3 个出版品牌或 50+ 语种并行翻译矩阵？</span>
                                <button type="button" class="primary-btn glow-btn" onclick="window.switchLicenseSubTab('activation')" style="margin-left: 12px; padding: 5px 16px; font-size: 0.82rem;">🔑 立即激活授权</button>
                            </div>
                        </div>
                    </div>
                </div>

                <div id="lic-panel-docs" style="display: ${activeSub === 'docs' ? 'block' : 'none'};">
                    <div class="settings-grid" style="display: flex; flex-direction: column; gap: 14px;">
                        <div class="setting-row level-imprint" style="padding: 16px 20px; border-radius: 10px;">
                            <div class="setting-info">
                                <div class="setting-label" style="font-size: 0.92rem;">🚀 1. 新手快速入门 <span class="tier-tag tier-imprint">指南</span></div>
                                <div class="setting-desc" style="margin-top: 4px;">将您的 Obsidian 物理笔记目录连接至系统，点击全域发布，即可自动经过 AI 润色翻译并推送至目标频道。</div>
                            </div>
                        </div>
                        <div class="setting-row level-imprint" style="padding: 16px 20px; border-radius: 10px;">
                            <div class="setting-info">
                                <div class="setting-label" style="font-size: 0.92rem;">📂 2. Obsidian 金库融合规范 <span class="tier-tag tier-imprint">指南</span></div>
                                <div class="setting-desc" style="margin-top: 4px;">支持标准的 Obsidian WikiLinks 语法 <code>[[文档标题]]</code> 与 YAML Frontmatter 元数据块。自动建立双链图谱。</div>
                            </div>
                        </div>
                        <div class="setting-row level-imprint" style="padding: 16px 20px; border-radius: 10px;">
                            <div class="setting-info">
                                <div class="setting-label" style="font-size: 0.92rem;">🧠 3. AI 算力节点配置 <span class="tier-tag tier-imprint">指南</span></div>
                                <div class="setting-desc" style="margin-top: 4px;">可在【算力中心】自由绑定 LMStudio, Ollama 或 OpenAI/Claude API 密钥，支持容灾备用自动切换。</div>
                            </div>
                        </div>
                        <div class="setting-row level-imprint" style="padding: 16px 20px; border-radius: 10px;">
                            <div class="setting-info">
                                <div class="setting-label" style="font-size: 0.92rem;">❓ 4. 常见排错与 FAQ <span class="tier-tag tier-imprint">指南</span></div>
                                <div class="setting-desc" style="margin-top: 4px;">若发布中断，可检查【治理中心 -> 系统安全】中的操作账本，或使用【算力中心 -> 节点探针】自检连通性。</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    };
})();
