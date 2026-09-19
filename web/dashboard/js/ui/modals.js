/**
 * 🧩 [V76.0] Illacme Plenipes UI Modals Component
 * 职责：作为全局弹窗中枢协调者，承载向导主外壳与 Step 1/2，并聚合 system、wizard_step3、wizard_success 子分片 HTML。
 * 对应重构拆分协议：SOP-01/SOP-02 模块化物理拆分。
 */

(function () {
    'use strict';

    /**
     * 🏛️ 出版品牌创建向导主外壳与 Step 1 / Step 2
     */
    window.getImprintWizardModalHTML = () => {
        const step3HTML = typeof window.getWizardStep3ModalHTML === 'function' ? window.getWizardStep3ModalHTML() : (typeof window.getWizardStep3HTML === 'function' ? window.getWizardStep3HTML() : '');

        return `
        <!-- 🏛️ Imprint Setup Wizard Modal (出版品牌创建向导) -->
        <div id="imprint-wizard-modal" class="modal-overlay" style="display: none;">
            <div class="glass-panel modal-content" style="max-width: 630px; width: 92%; height: auto; max-height: 90vh; display: flex; flex-direction: column; overflow: hidden; padding: 14px 18px;">
                <div class="modal-header" style="margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 1.25rem;">🏛️</span>
                        <h2 style="margin: 0; font-size: 1.1rem; letter-spacing: 0.5px; color: var(--accent-primary);">出版品牌创建向导 <span class="version-tag tiny">WIZARD</span></h2>
                    </div>
                    <button class="close-btn" onclick="closeImprintWizard()" style="position: static; margin-left: auto;">×</button>
                </div>
                
                <!-- 向导进度条标示 (1.文库 ➔ 2.品牌装帧 ➔ 3.算力分发) -->
                <div class="wizard-steps-indicator" style="display: flex; justify-content: space-between; margin-bottom: 10px; position: relative;">
                    <div class="step-line" style="position: absolute; top: 11px; left: 0; right: 0; height: 2px; background: rgba(255,255,255,0.08); z-index: 1;"></div>
                    <div class="step-line-active" id="wiz-progress-line" style="position: absolute; top: 11px; left: 0; width: 0%; height: 2px; background: var(--accent-primary); transition: width 0.3s ease; z-index: 2;"></div>
                    
                    <div class="wiz-step-node active" id="wiz-node-1" style="display: flex; flex-direction: column; align-items: center; z-index: 3; flex: 1;">
                        <div class="circle" style="width: 22px; height: 22px; border-radius: 50%; background: var(--card-bg); border: 2px solid var(--accent-primary); color: var(--text-bright); display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: bold; transition: all 0.3s;">1</div>
                        <span style="font-size: 0.68rem; color: var(--text-bright); margin-top: 3px; font-weight: bold;">关联原稿文库</span>
                    </div>
                    <div class="wiz-step-node" id="wiz-node-2" style="display: flex; flex-direction: column; align-items: center; z-index: 3; flex: 1;">
                        <div class="circle" style="width: 22px; height: 22px; border-radius: 50%; background: var(--card-bg); border: 2px solid rgba(255,255,255,0.1); color: var(--text-dim); display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: bold; transition: all 0.3s;">2</div>
                        <span style="font-size: 0.68rem; color: var(--text-dim); margin-top: 3px; font-weight: bold;">品牌名称与装帧</span>
                    </div>
                    <div class="wiz-step-node" id="wiz-node-3" style="display: flex; flex-direction: column; align-items: center; z-index: 3; flex: 1;">
                        <div class="circle" style="width: 22px; height: 22px; border-radius: 50%; background: var(--card-bg); border: 2px solid rgba(255,255,255,0.1); color: var(--text-dim); display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: bold; transition: all 0.3s;">3</div>
                        <span style="font-size: 0.68rem; color: var(--text-dim); margin-top: 3px; font-weight: bold;">算力底座与分发</span>
                    </div>
                </div>

                <div class="modal-body" style="flex: 1; overflow-y: auto; padding-right: 2px; margin-bottom: 8px;">
                    <!-- Step 1: 📂 关联原稿文库 -->
                    <div id="wiz-step-1" class="wizard-pane fade-in">
                        <div class="sovereign-memo glass-panel" style="margin-bottom: 10px; padding: 7px 12px; border-left: 3px solid var(--accent-secondary); background: rgba(0, 242, 255, 0.04); border-radius: 6px;">
                            <p style="font-size: 0.76rem; color: var(--text-dim); margin: 0; line-height: 1.4;">
                                💡 <b>内容文库 (Vault)</b> 是存放手稿 Markdown 笔记的本地物理文件夹。支持选取已有目录或自动新建：
                            </p>
                        </div>
                        <!-- 💡 自定义品牌配额前置感知友好提示卡片 -->
                        <div id="wiz-quota-notice" class="glass-panel" style="display: none; margin-bottom: 10px; padding: 8px 12px; border-left: 3px solid #f59e0b; background: rgba(245, 158, 11, 0.08); border-radius: 6px; color: #fbbf24; font-size: 0.73rem; line-height: 1.4;">
                            <div style="display: flex; align-items: flex-start; gap: 7px;">
                                <span style="font-size: 0.9rem; line-height: 1.2;">💡</span>
                                <div id="wiz-quota-msg" style="flex: 1;"></div>
                            </div>
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 10px;">
                            <div class="wiz-form-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 8px; padding: 10px 14px; display: flex; flex-direction: column; gap: 4px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <label style="font-weight: 600; font-size: 0.84rem; color: var(--text-bright); margin: 0;">内容文库绝对物理路径</label>
                                    <span class="tier-tag tier-local" style="font-size: 0.62rem; padding: 1px 5px;">本地物理路径</span>
                                </div>
                                <p style="font-size: 0.72rem; color: var(--text-dim); margin: 0; line-height: 1.3;">选择您本地电脑的笔记文件夹路径。留空将自动创建专属独立文库。</p>
                                <div style="display: flex; gap: 8px; margin-top: 4px;">
                                    <input type="text" id="wiz-vault-path" class="setting-input" placeholder="例如: /Users/username/Documents/MyVault (留空将自动新建专属文库)" style="flex: 1; font-family: var(--font-mono); font-size: 0.78rem; padding: 6px 10px; border-radius: 6px;">
                                    <button type="button" id="btn-pick-wizard-vault" class="secondary-btn" onclick="window.pickWizardVaultDirectory()" style="padding: 6px 12px; font-size: 0.75rem; white-space: nowrap;">📁 选择文件夹</button>
                                </div>
                                <div id="wiz-error-path" class="glass-panel" style="display: none; margin-top: 6px; padding: 6px 10px; border-left: 3px solid #ff4d6a; background: rgba(255, 77, 106, 0.08); border-radius: 6px; color: #ff859b; font-size: 0.74rem; line-height: 1.3;"></div>
                                <!-- 💡 文库复用与已绑定品牌温和提示卡片 (不阻断用户继续创建) -->
                                <div id="wiz-vault-bound-notice" class="glass-panel" style="display: none; margin-top: 6px; padding: 7px 12px; border-left: 3px solid #f59e0b; background: rgba(245, 158, 11, 0.08); border-radius: 6px; color: #fbbf24; font-size: 0.73rem; line-height: 1.4;">
                                    <div style="display: flex; align-items: flex-start; gap: 7px;">
                                        <span style="font-size: 0.88rem; line-height: 1.2;">💡</span>
                                        <div id="wiz-vault-bound-msg" style="flex: 1;"></div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="wiz-form-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 8px; padding: 8px 12px; display: flex; align-items: center; gap: 8px;">
                                <input type="checkbox" id="wiz-bootstrap-vault" style="margin: 0; transform: scale(1.1); cursor: pointer;">
                                <label for="wiz-bootstrap-vault" style="font-size: 0.74rem; color: var(--text-dim); cursor: pointer; line-height: 1.3;">
                                    自动注入中英双语演示手稿与资产目录结构 (推荐新手勾选)
                                </label>
                            </div>
                        </div>
                    </div>

                    <!-- Step 2: 🏷️ 品牌标识与装帧主题 -->
                    <div id="wiz-step-2" class="wizard-pane fade-in" style="display: none;">
                        <div class="sovereign-memo glass-panel" style="margin-bottom: 8px; padding: 6px 12px; border-left: 3px solid var(--accent-primary); background: rgba(163, 76, 255, 0.04); border-radius: 6px;">
                            <p style="font-size: 0.74rem; color: var(--text-dim); margin: 0; line-height: 1.35;">
                                💡 <b>品牌名与装帧</b>：品牌 ID 将作为物理文件夹名；装帧主题决定网站的视觉与静态渲染框架。
                            </p>
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 6px;">
                            <!-- 品牌名称与品牌 ID 同排紧凑布局 (带精准错误提示) -->
                            <div class="wiz-form-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 8px; padding: 8px 12px; display: flex; flex-direction: column; gap: 4px;">
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                                    <div>
                                        <label style="font-weight: 600; font-size: 0.78rem; color: var(--text-bright); display: block; margin-bottom: 2px;">出版品牌名称</label>
                                        <input type="text" id="wiz-brand-name" class="setting-input" placeholder="例如: 钛媒体精选 / DevHub" oninput="window.syncBrandNameToId()" style="width: 100%; font-size: 0.76rem; padding: 5px 8px; border-radius: 5px;">
                                    </div>
                                    <div>
                                        <label style="font-weight: 600; font-size: 0.78rem; color: var(--text-bright); display: block; margin-bottom: 2px;">品牌唯一标识 (ID)</label>
                                        <input type="text" id="wiz-brand-id" class="setting-input" placeholder="例如: devhub (英数横杠)" oninput="window.validateBrandIdInput()" style="width: 100%; font-family: var(--font-mono); font-size: 0.76rem; padding: 5px 8px; border-radius: 5px;">
                                    </div>
                                </div>
                                <div id="wiz-error-brand-id" class="glass-panel" style="display: none; margin-top: 4px; padding: 4px 8px; border-left: 3px solid #ff4d6a; background: rgba(255, 77, 106, 0.08); border-radius: 5px; color: #ff859b; font-size: 0.72rem; line-height: 1.3;"></div>
                            </div>

                            <!-- 挑选装帧主题 (6 大官方主题) -->
                            <div class="wiz-form-card" style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 8px; padding: 8px 12px; display: flex; flex-direction: column; gap: 6px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <label style="font-weight: 600; font-size: 0.78rem; color: var(--text-bright); margin: 0;">挑选装帧主题</label>
                                    <span style="font-size: 0.65rem; color: var(--text-dim);">可随时在控制台热切换</span>
                                </div>
                                
                                <div class="theme-grid-mini" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px;">
                                    <!-- Sovereign -->
                                    <div class="wiz-theme-card active" data-theme="sovereign" id="wiz-theme-sovereign" onclick="window.selectWizardTheme('sovereign')" style="padding: 6px 8px; font-size: 0.72rem; border-radius: 6px; border: 1px solid var(--accent-primary); background: rgba(163, 76, 255, 0.08); cursor: pointer; text-align: center; transition: all 0.2s;">
                                        <div style="font-weight: 700; color: var(--accent-primary);">👑 Sovereign</div>
                                        <div style="font-size: 0.6rem; color: var(--text-dim); transform: scale(0.9);">高阶双链哲学</div>
                                    </div>
                                    <!-- Universal -->
                                    <div class="wiz-theme-card" data-theme="universal" id="wiz-theme-universal" onclick="window.selectWizardTheme('universal')" style="padding: 6px 8px; font-size: 0.72rem; border-radius: 6px; border: 1px solid var(--glass-border); background: rgba(255,255,255,0.02); cursor: pointer; text-align: center; transition: all 0.2s;">
                                        <div style="font-weight: 600;">🌌 Universal</div>
                                        <div style="font-size: 0.6rem; color: var(--text-dim); transform: scale(0.9);">通用极简美学</div>
                                    </div>
                                    <!-- Docusaurus -->
                                    <div class="wiz-theme-card" data-theme="docusaurus" id="wiz-theme-docusaurus" onclick="window.selectWizardTheme('docusaurus')" style="padding: 6px 8px; font-size: 0.72rem; border-radius: 6px; border: 1px solid var(--glass-border); background: rgba(255,255,255,0.02); cursor: pointer; text-align: center; transition: all 0.2s;">
                                        <div style="font-weight: 600;">🦖 Docusaurus</div>
                                        <div style="font-size: 0.6rem; color: var(--text-dim); transform: scale(0.9);">工业文档旗舰</div>
                                    </div>
                                    <!-- Starlight -->
                                    <div class="wiz-theme-card" data-theme="starlight" id="wiz-theme-starlight" onclick="window.selectWizardTheme('starlight')" style="padding: 6px 8px; font-size: 0.72rem; border-radius: 6px; border: 1px solid var(--glass-border); background: rgba(255,255,255,0.02); cursor: pointer; text-align: center; transition: all 0.2s;">
                                        <div style="font-weight: 600;">🌟 Starlight</div>
                                        <div style="font-size: 0.6rem; color: var(--text-dim); transform: scale(0.9);">Astro极致轻快</div>
                                    </div>
                                    <!-- Nextra -->
                                    <div class="wiz-theme-card" data-theme="nextra" id="wiz-theme-nextra" onclick="window.selectWizardTheme('nextra')" style="padding: 6px 8px; font-size: 0.72rem; border-radius: 6px; border: 1px solid var(--glass-border); background: rgba(255,255,255,0.02); cursor: pointer; text-align: center; transition: all 0.2s;">
                                        <div style="font-weight: 600;">📐 Nextra</div>
                                        <div style="font-size: 0.6rem; color: var(--text-dim); transform: scale(0.9);">Next.js架构生态</div>
                                    </div>
                                    <!-- VitePress -->
                                    <div class="wiz-theme-card" data-theme="vitepress" id="wiz-theme-vitepress" onclick="window.selectWizardTheme('vitepress')" style="padding: 6px 8px; font-size: 0.72rem; border-radius: 6px; border: 1px solid var(--glass-border); background: rgba(255,255,255,0.02); cursor: pointer; text-align: center; transition: all 0.2s;">
                                        <div style="font-weight: 600;">⚡ VitePress</div>
                                        <div style="font-size: 0.6rem; color: var(--text-dim); transform: scale(0.9);">Vue现代文档</div>
                                    </div>
                                </div>
                                <input type="hidden" id="wiz-selected-theme" value="sovereign">
                            </div>
                        </div>
                    </div>

                    ${step3HTML}
                </div>

                <div class="modal-footer" style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--glass-border); padding-top: 12px; margin-top: auto;">
                    <button class="secondary-btn" id="btn-wiz-prev" onclick="window.navigateWizard(-1)" style="visibility: hidden; font-size: 0.78rem; padding: 6px 14px;">上一步</button>
                    <button class="primary-btn glow-btn" id="btn-wiz-next" onclick="window.navigateWizard(1)" style="min-width: 110px; font-size: 0.78rem; padding: 6px 16px;">下一步 →</button>
                </div>
            </div>
        </div>
        `;
    };

    /**
     * 🌐 核心聚合入口：按序拼装全局所有弹窗组件 HTML
     */
    window.getUIModalsHTML = () => {
        const sys = typeof window.getSystemModalsHTML === 'function' ? window.getSystemModalsHTML() : '';
        const wiz = typeof window.getImprintWizardModalHTML === 'function' ? window.getImprintWizardModalHTML() : '';
        const succ = typeof window.getWizardSuccessModalHTML === 'function' ? window.getWizardSuccessModalHTML() : '';
        return sys + wiz + succ;
    };

})();
