/**
 * 🖼️ [V122.0] Illacme Plenipes Image Policy Module
 * 职责：治理中心-品牌外观-图像策略二级子标签渲染与持久化。
 * 遵循 SOP-01 规范与 Sovereign 赛博毛玻璃视觉体系。
 */

(function () {
    window.renderImagePolicyCategory = () => {
        const policy = (window.settingsData && window.settingsData.image_policy) || {};
        const currentStrategy = policy.default_strategy || 'auto';
        const currentRatio = policy.aspect_ratio || '16:9';
        const enableWatermark = policy.enable_watermark !== false;
        const unsplashQuery = policy.unsplash_query || 'technology,minimalist';

        const strategies = [
            { id: 'auto', name: '智能阶梯自愈 (推荐)', icon: '⚡', desc: '优先动态 OG 卡片，遇到长难文本或异常自动按母本轮巡与极简徽章优雅降级。' },
            { id: 'og_card', name: '动态 OG 技术卡片', icon: '💻', desc: '基于文章标题、作者、分类自动生成高质感暗夜赛博排版封面 (对标 Vercel / GitHub)。' },
            { id: 'brand_presets', name: '品牌母本图库轮巡', icon: '🎨', desc: '基于文章 Slug 哈希确定性挑选高质感流体渐变底图，100% 离线、零 API 消耗。' },
            { id: 'minimal_badge', name: '极简首字文字徽章', icon: '🏷️', desc: '提取文章首字符在色环互补色背景上渲染巨幅艺术徽标，极简典雅 (对标 Notion / GitLab)。' },
            { id: 'unsplash', name: 'Unsplash 免版权摄影', icon: '📷', desc: '自动根据文章技术标签从全球免版税摄影图库匹配高清插画并自动合规署名。' },
            { id: 'ai_generator', name: 'AI 智能文生图', icon: '🔮', desc: '调用设计中心配置的模型提炼 Prompt 自动绘制专属插画 (仅推荐在抽屉中按篇精细触发)。' }
        ];

        let strategyCardsHtml = strategies.map(s => {
            const isSelected = s.id === currentStrategy;
            return `
                <div class="strategy-option-card glass-panel ${isSelected ? 'active-strategy' : ''}" 
                     onclick="window.selectImageStrategy('${s.id}')"
                     style="padding: 14px 16px; border-radius: 10px; border: ${isSelected ? '2px solid var(--accent-secondary, #00f2fe)' : '1px solid var(--glass-border)'}; background: ${isSelected ? 'rgba(var(--accent-secondary-rgb, 0, 242, 255), 0.08)' : 'rgba(255, 255, 255, 0.02)'}; box-shadow: ${isSelected ? '0 0 0 3px var(--neon-cyan-20), 0 12px 30px var(--shadow-glow)' : 'none'}; cursor: pointer; transition: all 0.25s ease; display: flex; flex-direction: column; gap: 6px;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <span style="font-size: 0.95rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 8px;">
                            <span>${s.icon}</span> ${s.name}
                        </span>
                        <input type="radio" name="image_strategy_radio" value="${s.id}" ${isSelected ? 'checked' : ''} style="cursor: pointer;">
                    </div>
                    <div style="font-size: 0.78rem; color: var(--text-muted); line-height: 1.45;">
                        ${s.desc}
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div class="node-unit-container" style="display: flex; flex-direction: column; gap: 20px;">
                <!-- 1. 策略选择卡片网格 -->
                <div class="glass-panel" style="padding: 20px; border-radius: 12px; border: 1px solid var(--glass-border);">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
                        <div>
                            <h3 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: var(--text-main);">🖼️ 默认封面生成策略</h3>
                            <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: var(--text-muted);">当文稿内容不含图片时，自动化出版管线与社媒分发所采用的默认封面供给模式。</p>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 12px;">
                        ${strategyCardsHtml}
                    </div>
                </div>

                <!-- 2. 比例与规格设置 -->
                <div class="glass-panel" style="padding: 20px; border-radius: 12px; border: 1px solid var(--glass-border); display: flex; flex-direction: column; gap: 16px;">
                    <h3 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: var(--text-main);">📐 画幅规范与品牌水印</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px;">
                        <div class="form-group" style="display: flex; flex-direction: column; gap: 6px;">
                            <label style="font-size: 0.82rem; font-weight: 600; color: var(--text-dim);">默认画幅基准比例</label>
                            <select id="select-cover-ratio" class="glass-input setting-input" style="padding: 8px 12px; border-radius: 6px; border: 1px solid var(--glass-border);">
                                <option value="16:9" ${currentRatio === '16:9' ? 'selected' : ''}>16:9 现代宽屏 (博客 / Dev.to / 知乎专栏)</option>
                                <option value="2.35:1" ${currentRatio === '2.35:1' ? 'selected' : ''}>2.35:1 微信头条 (900x383 微信官方规范)</option>
                                <option value="3:4" ${currentRatio === '3:4' ? 'selected' : ''}>3:4 移动海报 (小红书 / 竖屏图文卡片)</option>
                            </select>
                            <span style="font-size: 0.72rem; color: var(--text-muted);">系统已内置居中安全区算法，各平台裁切时核心信息永不截断。</span>
                        </div>
                        <div class="form-group" style="display: flex; flex-direction: column; gap: 6px;">
                            <label style="font-size: 0.82rem; font-weight: 600; color: var(--text-dim);">品牌视觉水印</label>
                            <label style="display: flex; align-items: center; gap: 8px; font-size: 0.85rem; color: var(--text-bright); cursor: pointer; margin-top: 6px;">
                                <input type="checkbox" id="check-cover-watermark" ${enableWatermark ? 'checked' : ''} style="cursor: pointer;">
                                <span>在自动生成的封面右下角叠加品牌专属主权徽标</span>
                            </label>
                        </div>
                    </div>
                </div>

                <!-- 3. 操作按钮组 -->
                <div style="display: flex; align-items: center; justify-content: flex-end; gap: 12px; margin-top: 10px;">
                    <button type="button" class="secondary-btn" onclick="window.testCoverPreviewDemo()" style="padding: 8px 16px; font-size: 0.82rem;">
                        <span>🎨 实时预览效果</span>
                    </button>
                    <button type="button" class="primary-btn glow-btn" onclick="window.saveImagePolicyConfig()" style="padding: 8px 20px; font-size: 0.82rem; font-weight: 700;">
                        <span>💾 保存图像策略</span>
                    </button>
                </div>
            </div>
        `;
    };

    window.selectImageStrategy = (stratId) => {
        const radios = document.querySelectorAll('input[name="image_strategy_radio"]');
        radios.forEach(r => {
            r.checked = (r.value === stratId);
        });
        const cards = document.querySelectorAll('.strategy-option-card');
        cards.forEach(c => {
            if (c.getAttribute('onclick')?.includes(stratId)) {
                c.classList.add('active-strategy');
                c.style.border = '2px solid var(--accent-secondary, #00f2fe)';
                c.style.background = 'rgba(var(--accent-secondary-rgb, 0, 242, 255), 0.08)';
                c.style.boxShadow = '0 0 0 3px var(--neon-cyan-20), 0 12px 30px var(--shadow-glow)';
            } else {
                c.classList.remove('active-strategy');
                c.style.border = '1px solid var(--glass-border)';
                c.style.background = 'rgba(255, 255, 255, 0.02)';
                c.style.boxShadow = 'none';
            }
        });
        if (!window.settingsData) window.settingsData = {};
        if (!window.settingsData.image_policy) window.settingsData.image_policy = {};
        window.settingsData.image_policy.default_strategy = stratId;
        if (typeof window.updateLayoutStatusBadge === 'function') {
            window.updateLayoutStatusBadge('image_policy');
        }
    };

    window.saveImagePolicyConfig = async () => {
        const checkedRadio = document.querySelector('input[name="image_strategy_radio"]:checked');
        const strategy = checkedRadio ? checkedRadio.value : 'auto';
        const ratioEl = document.getElementById('select-cover-ratio');
        const watermarkEl = document.getElementById('check-cover-watermark');

        const payload = {
            default_strategy: strategy,
            aspect_ratio: ratioEl ? ratioEl.value : '16:9',
            enable_watermark: watermarkEl ? watermarkEl.checked : true,
            unsplash_query: 'technology,minimalist'
        };

        const fetchFunc = window.apiFetch || fetch;
        try {
            const resp = await fetchFunc('/api/gov/image-policy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await resp.json();
            if (data && data.success) {
                if (typeof window.showToast === 'function') {
                    window.showToast('✅ 品牌图像策略已成功持久化并实时生效！', 'success');
                }
                if (!window.settingsData) window.settingsData = {};
                window.settingsData.image_policy = payload;
            } else {
                alert('保存图像策略失败: ' + (data.detail || '未知错误'));
            }
        } catch (e) {
            console.error('[ImagePolicy Save Error]:', e);
            alert('保存图像策略网络异常: ' + e.message);
        }
    };

    window.testCoverPreviewDemo = async () => {
        const checkedRadio = document.querySelector('input[name="image_strategy_radio"]:checked');
        const strategy = checkedRadio ? checkedRadio.value : 'auto';
        const ratioEl = document.getElementById('select-cover-ratio');
        const ratio = ratioEl ? ratioEl.value : '16:9';

        const fetchFunc = window.apiFetch || fetch;
        try {
            const resp = await fetchFunc('/api/design/cover/preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    doc_id: 'Docs/architecture.md',
                    title: '物理隔离架构与分发技术原理',
                    strategy: strategy,
                    aspect_ratio: ratio
                })
            });
            const res = await resp.json();
            if (res && res.cover_url) {
                // 弹出模态框展示预览
                const modalHtml = `
                    <div id="cover-preview-modal" style="position: fixed; inset: 0; background: rgba(0,0,0,0.85); backdrop-filter: blur(10px); z-index: 99999; display: flex; align-items: center; justify-content: center; padding: 20px;">
                        <div class="glass-panel" style="max-width: 760px; width: 100%; border-radius: 12px; border: 1px solid var(--accent-secondary, #00f2fe); padding: 20px; display: flex; flex-direction: column; gap: 14px;">
                            <div style="display: flex; align-items: center; justify-content: space-between;">
                                <span style="font-weight: 700; color: #fff; font-size: 1rem;">🎨 图像策略实时生成预览 (${res.strategy_used})</span>
                                <button type="button" onclick="document.getElementById('cover-preview-modal').remove()" style="background: none; border: none; color: #aaa; font-size: 1.2rem; cursor: pointer;">✕</button>
                            </div>
                            <div style="width: 100%; border-radius: 8px; overflow: hidden; border: 1px solid var(--glass-border); background: #000;">
                                <img src="${res.cover_url}?_t=${Date.now()}" style="width: 100%; height: auto; display: block;" alt="Cover Preview">
                            </div>
                            <div style="font-size: 0.78rem; color: var(--text-muted); display: flex; justify-content: space-between;">
                                <span>画幅: ${res.aspect_ratio}</span>
                                <span>文件大小: ${(res.size_bytes / 1024).toFixed(1)} KB</span>
                            </div>
                        </div>
                    </div>
                `;
                document.body.insertAdjacentHTML('beforeend', modalHtml);
            }
        } catch (e) {
            alert('预览生成异常: ' + e.message);
        }
    };
})();
