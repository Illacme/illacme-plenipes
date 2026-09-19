/**
 * 🧩 [V76.0] Illacme Plenipes UI Modals - Wizard Step 3 Sub-Shard
 * 职责：提供品牌建站向导 Step 3（算力引擎与全域分发）HTML 结构。
 * 对应重构拆分协议：SOP-01/SOP-02 模块化物理拆分。
 */
(function() {
    window.getWizardStep3ModalHTML = window.getWizardStep3HTML = () => {
        return `

                    <!-- Step 3: 🤖 算力底座与全域分发赋能 (渐进式紧凑呈现架构) -->
                    <div id="wiz-step-3" class="wizard-pane fade-in" style="display: none;">
                        <input type="hidden" id="wiz-ai-provider" value="deepseek">
                        <input type="hidden" id="wiz-dispatch-platform" value="local_preview">

                        <!-- 🌟 默认极简开箱态 (Default Streamlined State) -->
                        <div id="wiz-step3-streamlined-view" style="display: flex; flex-direction: column; gap: 10px;">
                            <div class="sovereign-memo glass-panel" style="padding: 8px 12px; border-left: 3px solid var(--accent-secondary); background: rgba(0, 242, 255, 0.04); border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
                                <div style="font-size: 0.76rem; color: var(--text-dim); line-height: 1.4;">
                                    ⚡ <b>智能装配就绪</b>：系统已根据您的运行环境全自动预设最佳发行底座，可即刻极速建站：
                                </div>
                                <button type="button" class="secondary-btn" onclick="window.toggleWizardAdvancedConfig(true)" style="padding: 3px 8px; font-size: 0.7rem; white-space: nowrap; border-color: rgba(0, 242, 255, 0.3); color: var(--accent-secondary);">⚙️ 自定义配置</button>
                            </div>

                            <!-- 两张精美预设赋能卡片 -->
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                                <!-- 预设算力卡片 -->
                                <div class="wiz-form-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 8px; padding: 12px; display: flex; flex-direction: column; justify-content: space-between; gap: 8px;">
                                    <div>
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                            <span style="font-weight: 700; font-size: 0.8rem; color: var(--text-bright);">🤖 翻译算力与语种</span>
                                            <span id="wiz-summary-compute-badge" class="tier-tag tier-imprint" style="font-size: 0.58rem; padding: 1px 5px;">智能推荐</span>
                                        </div>
                                        <div id="wiz-summary-compute-title" style="font-size: 0.82rem; font-weight: 700; color: var(--accent-secondary); margin-bottom: 2px;">
                                            🐋 DeepSeek (deepseek-chat)
                                        </div>
                                        <div id="wiz-summary-compute-desc" style="font-size: 0.68rem; color: var(--text-dim); line-height: 1.35;">
                                            官方推荐高性价比极速模型 · 默认发行 🇺🇸 English
                                        </div>
                                    </div>
                                    <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px; display: flex; justify-content: space-between; align-items: center;">
                                        <span style="font-size: 0.64rem; color: var(--text-dim);">免密钥即刻体验</span>
                                        <a href="javascript:void(0)" onclick="window.toggleWizardAdvancedConfig(true)" style="font-size: 0.68rem; color: var(--accent-secondary); text-decoration: none;">切换模型/语种 ⚙️</a>
                                    </div>
                                </div>

                                <!-- 预设分发网络卡片 -->
                                <div class="wiz-form-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 8px; padding: 12px; display: flex; flex-direction: column; justify-content: space-between; gap: 8px;">
                                    <div>
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                            <span style="font-weight: 700; font-size: 0.8rem; color: var(--text-bright);">🚀 网站托管与在线发布</span>
                                            <span class="tier-tag tier-global" style="font-size: 0.58rem; padding: 1px 5px;">0 门槛</span>
                                        </div>
                                        <div id="wiz-summary-dispatch-title" style="font-size: 0.82rem; font-weight: 700; color: var(--accent-secondary); margin-bottom: 2px;">
                                            📦 本地全功能离线预览
                                        </div>
                                        <div id="wiz-summary-dispatch-desc" style="font-size: 0.68rem; color: var(--text-dim); line-height: 1.35;">
                                            独立静态服务器 (43213 端口) · 稍后随时一键发布到全网
                                        </div>
                                    </div>
                                    <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px; display: flex; justify-content: space-between; align-items: center;">
                                        <span style="font-size: 0.64rem; color: var(--text-dim);">全站托管随时扩展</span>
                                        <a href="javascript:void(0)" onclick="window.toggleWizardAdvancedConfig(true)" style="font-size: 0.68rem; color: var(--accent-secondary); text-decoration: none;">配置在线托管 ⚙️</a>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 🛠️ 详细定制配置区 (紧凑流式/无滚动溢出) -->
                        <div id="wiz-step3-custom-view" style="display: none; flex-direction: column; gap: 6px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 3px 6px; background: rgba(255,255,255,0.03); border-radius: 6px;">
                                <span style="font-size: 0.72rem; font-weight: 700; color: var(--accent-secondary);">🛠️ 自定义高级配置面板</span>
                                <button type="button" class="secondary-btn" onclick="window.toggleWizardAdvancedConfig(false)" style="padding: 2px 8px; font-size: 0.66rem;">↩️ 折叠为默认预设</button>
                            </div>

                            <!-- 模块 A: 🤖 AI 翻译算力底座 -->
                            <div class="wiz-form-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 6px; padding: 6px 8px; display: flex; flex-direction: column; gap: 4px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <label style="font-weight: 600; font-size: 0.76rem; color: var(--text-bright); margin: 0;">🤖 AI 翻译算力底座</label>
                                    <span id="wiz-probe-badge" class="tier-tag tier-imprint" style="font-size: 0.56rem; padding: 1px 5px;">🔍 探测中</span>
                                </div>
                                
                                <!-- 算力服务商单选卡片组 (4 选 1) -->
                                <div class="wiz-provider-grid" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px;">
                                    <!-- 本地免密算力 -->
                                    <div class="wiz-provider-card" data-provider="lmstudio" onclick="window.selectWizardComputeProvider('lmstudio')" style="padding: 4px 6px;">
                                        <div style="font-weight: 700; font-size: 0.7rem; color: var(--text-bright); white-space: nowrap;">💻 本地模型</div>
                                        <div style="font-size: 0.58rem; color: var(--text-dim);">LM Studio/Ollama</div>
                                    </div>
                                    <!-- DeepSeek -->
                                    <div class="wiz-provider-card" data-provider="deepseek" onclick="window.selectWizardComputeProvider('deepseek')" style="padding: 4px 6px;">
                                        <div style="font-weight: 700; font-size: 0.7rem; color: var(--accent-secondary); white-space: nowrap;">🐋 DeepSeek</div>
                                        <div style="font-size: 0.58rem; color: var(--text-dim);">官方推荐直连</div>
                                    </div>
                                    <!-- SiliconFlow 硅基流动 -->
                                    <div class="wiz-provider-card" data-provider="siliconflow" onclick="window.selectWizardComputeProvider('siliconflow')" style="padding: 4px 6px;">
                                        <div style="font-weight: 700; font-size: 0.7rem; color: var(--text-bright); white-space: nowrap;">⚡ 硅基流动</div>
                                        <div style="font-size: 0.58rem; color: var(--text-dim);">全网模型/海量赠送</div>
                                    </div>
                                    <!-- 暂不接入 -->
                                    <div class="wiz-provider-card" data-provider="none" onclick="window.selectWizardComputeProvider('none')" style="padding: 4px 6px;">
                                        <div style="font-weight: 700; font-size: 0.7rem; color: var(--text-bright); white-space: nowrap;">⏸️ 稍后配置</div>
                                        <div style="font-size: 0.58rem; color: var(--text-dim);">纯静态建站</div>
                                    </div>
                                </div>

                                <!-- ① 🔑 API Key 输入框 (置于模型选择上方，支持在线/本地安全鉴权) -->
                                <div id="wiz-ai-key-container" style="display: flex; flex-direction: column; gap: 2px;">
                                    <div style="display: flex; justify-content: space-between; align-items: center;">
                                        <label id="wiz-key-label" style="font-size: 0.68rem; color: var(--text-dim); margin: 0;">🔑 API 密钥 (Key):</label>
                                        <span id="wiz-key-hint" style="font-size: 0.58rem; color: var(--text-dim);">输入后失焦或点击 🔄 真实拉取模型</span>
                                    </div>
                                    <div style="position: relative; display: flex; align-items: center;">
                                        <input type="password" id="wiz-ai-key" class="setting-input" placeholder="sk-... (选填/如启用鉴权则输入)" style="width: 100%; box-sizing: border-box; font-family: var(--font-mono); font-size: 0.72rem; padding: 3px 24px 3px 6px; border-radius: 4px;" onblur="window.onWizardKeyBlur()" onkeydown="if(event.key==='Enter'){event.preventDefault();window.refreshWizardModelList();}">
                                        <span onclick="window.toggleWizardKeyVisibility()" style="position: absolute; right: 6px; cursor: pointer; font-size: 0.7rem; opacity: 0.7;">👁️</span>
                                    </div>
                                </div>

                                <!-- ② 🎯 模型选择与首要语种单选并排布局 (标准 select 展开全量列表) -->
                                <div style="display: grid; grid-template-columns: 1.15fr 1fr; gap: 8px; align-items: start;">
                                    <!-- 左侧：标准全量模型下拉与真实拉取 -->
                                    <div id="wiz-ai-model-container" style="display: flex; flex-direction: column; gap: 2px;">
                                        <div style="display: flex; justify-content: space-between; align-items: center;">
                                            <label style="font-size: 0.68rem; color: var(--text-dim); margin: 0;">🎯 翻译引擎模型 (Model):</label>
                                            <span id="wiz-model-status" style="font-size: 0.58rem; color: var(--accent-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 130px;"></span>
                                        </div>
                                        <div style="display: flex; gap: 4px; align-items: center;">
                                            <select id="wiz-ai-model-select" class="setting-input" style="flex: 1; font-size: 0.72rem; padding: 3px 6px; border-radius: 4px;" onchange="window.onWizardModelSelected(this.value)">
                                                <option value="">-- 点击 🔄 真实拉取模型 --</option>
                                            </select>
                                            <input type="text" id="wiz-ai-model-custom" class="setting-input" placeholder="输入模型名，如 deepseek-chat" style="display: none; flex: 1; font-size: 0.72rem; padding: 3px 6px; border-radius: 4px;" oninput="window.updateWizardSummaryView()" onblur="window.onWizardCustomModelBlur()">
                                            <button type="button" class="secondary-btn" onclick="window.refreshWizardModelList()" title="向服务商/本地发起真实连通性测试并拉取完整模型列表" style="padding: 2px 6px; font-size: 0.66rem;">🔄</button>
                                        </div>
                                    </div>

                                    <!-- 右侧：首要目标语种单选 -->
                                    <div style="display: flex; flex-direction: column; gap: 2px;">
                                        <div style="display: flex; justify-content: space-between; align-items: center;">
                                            <label style="font-size: 0.68rem; color: var(--text-dim); margin: 0;">🌍 首要目标语种:</label>
                                            <span style="font-size: 0.58rem; color: var(--text-dim);">可随时扩展</span>
                                        </div>
                                        <select id="wiz-primary-lang-select" class="setting-input" style="width: 100%; box-sizing: border-box; font-size: 0.72rem; padding: 3px 6px; border-radius: 4px;" onchange="window.onWizardPrimaryLangSelected(this.value)">
                                            <option value="en" data-lang="en" selected>🇺🇸 English (英语 · 推荐)</option>
                                            <option value="ja" data-lang="ja">🇯🇵 日本語 (日语)</option>
                                            <option value="de" data-lang="de">🇩🇪 Deutsch (德语)</option>
                                            <option value="fr" data-lang="fr">🇫🇷 Français (法语)</option>
                                            <option value="es" data-lang="es">🇪🇸 Español (西班牙语)</option>
                                            <option value="ru" data-lang="ru">🇷🇺 Русский (俄语)</option>
                                            <option value="zh" data-lang="zh">🇨🇳 简体中文 (单语源站)</option>
                                        </select>
                                    </div>
                                </div>

                                <!-- 灵活扩展友好提示条 -->
                                <div style="font-size: 0.64rem; color: var(--text-dim); line-height: 1.35; padding: 3px 6px; background: rgba(255,255,255,0.015); border-radius: 4px; border: 1px dashed rgba(255,255,255,0.06);">
                                    💡 <b>自由扩展提示</b>：算力渠道、多语种翻译、全站托管及社媒分发平台均可在品牌创建完成后随时扩展。
                                </div>
                            </div>

                            <!-- 模块 B: 🚀 网站托管与在线发布 (全站托管平台) -->
                            <div class="wiz-form-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 6px; padding: 6px 8px; display: flex; flex-direction: column; gap: 4px; margin-top: 4px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <label style="font-weight: 600; font-size: 0.76rem; color: var(--text-bright); margin: 0;">🚀 网站托管与在线发布</label>
                                    <span class="tier-tag tier-global" style="font-size: 0.56rem; padding: 1px 5px;">全站托管</span>
                                </div>
                                
                                <!-- 3 选 1 分发渠道卡片 -->
                                <div class="wiz-dispatch-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px;">
                                    <div class="wiz-dispatch-card active" data-dispatch="local_preview" onclick="window.selectWizardDispatchPlatform('local_preview')" style="padding: 4px 6px;">
                                        <div style="font-weight: 700; font-size: 0.7rem; color: var(--text-bright);">📦 本地预览优先</div>
                                        <div style="font-size: 0.58rem; color: var(--text-dim);">纯离线 0 门槛</div>
                                    </div>
                                    <div class="wiz-dispatch-card" data-dispatch="github_pages" onclick="window.selectWizardDispatchPlatform('github_pages')" style="padding: 4px 6px;">
                                        <div style="font-weight: 700; font-size: 0.7rem; color: var(--accent-secondary);">🌐 GitHub Pages</div>
                                        <div style="font-size: 0.58rem; color: var(--text-dim);">开源免费托管</div>
                                    </div>
                                    <div class="wiz-dispatch-card" data-dispatch="cloudflare_pages" onclick="window.selectWizardDispatchPlatform('cloudflare_pages')" style="padding: 4px 6px;">
                                        <div style="font-weight: 700; font-size: 0.7rem; color: var(--text-bright);">⚡ Cloudflare</div>
                                        <div style="font-size: 0.58rem; color: var(--text-dim);">超快全球 CDN</div>
                                    </div>
                                </div>

                                <!-- 🌐 GitHub Pages 面板 -->
                                <div id="wiz-dispatch-github-pane" style="display: none; flex-direction: column; gap: 4px; padding: 4px 6px; background: rgba(0, 242, 255, 0.03); border: 1px dashed rgba(0, 242, 255, 0.2); border-radius: 4px;">
                                    <div style="display: grid; grid-template-columns: 1.5fr 1fr; gap: 4px;">
                                        <div>
                                            <label style="font-size: 0.66rem; color: var(--text-dim); margin-bottom: 1px; display: block;">🏷️ 仓库全名 (Repository):</label>
                                            <input type="text" id="wiz-gh-repo" class="setting-input" placeholder="username/repo-name" style="width: 100%; box-sizing: border-box; font-size: 0.7rem; padding: 2px 5px; border-radius: 4px;">
                                        </div>
                                        <div>
                                            <label style="font-size: 0.66rem; color: var(--text-dim); margin-bottom: 1px; display: block;">🌿 分支:</label>
                                            <select id="wiz-gh-branch" class="setting-input" style="width: 100%; box-sizing: border-box; font-size: 0.7rem; padding: 2px 4px; border-radius: 4px;">
                                                <option value="gh-pages" selected>gh-pages</option>
                                                <option value="main">main</option>
                                                <option value="docs">docs</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div>
                                        <label style="font-size: 0.66rem; color: var(--text-dim); margin-bottom: 1px; display: block;">🔑 GitHub Token (选填/可稍后免密授权):</label>
                                        <input type="password" id="wiz-gh-token" class="setting-input" placeholder="ghp_xxxx 或建站后一键免密授权" style="width: 100%; box-sizing: border-box; font-family: var(--font-mono); font-size: 0.7rem; padding: 2px 5px; border-radius: 4px;">
                                    </div>
                                </div>

                                <!-- ⚡ Cloudflare Pages 面板 -->
                                <div id="wiz-dispatch-cloudflare-pane" style="display: none; flex-direction: column; gap: 4px; padding: 4px 6px; background: rgba(255, 184, 0, 0.03); border: 1px dashed rgba(255, 184, 0, 0.2); border-radius: 4px;">
                                    <div style="display: grid; grid-template-columns: 1.5fr 1fr; gap: 4px;">
                                        <div>
                                            <label style="font-size: 0.66rem; color: var(--text-dim); margin-bottom: 1px; display: block;">🏷️ 项目名称:</label>
                                            <input type="text" id="wiz-cf-project" class="setting-input" placeholder="project-name" style="width: 100%; box-sizing: border-box; font-size: 0.7rem; padding: 2px 5px; border-radius: 4px;">
                                        </div>
                                        <div>
                                            <label style="font-size: 0.66rem; color: var(--text-dim); margin-bottom: 1px; display: block;">🌿 生产分支:</label>
                                            <input type="text" id="wiz-cf-branch" class="setting-input" value="main" style="width: 100%; box-sizing: border-box; font-size: 0.7rem; padding: 2px 5px; border-radius: 4px;">
                                        </div>
                                    </div>
                                    <div>
                                        <label style="font-size: 0.66rem; color: var(--text-dim); margin-bottom: 1px; display: block;">🔑 Cloudflare API Token (选填):</label>
                                        <input type="password" id="wiz-cf-token" class="setting-input" placeholder="API Token (选填)" style="width: 100%; box-sizing: border-box; font-family: var(--font-mono); font-size: 0.7rem; padding: 2px 5px; border-radius: 4px;">
                                    </div>
                                </div>

                                <!-- 📦 本地离线预览面板 -->
        `;
    };
})();
