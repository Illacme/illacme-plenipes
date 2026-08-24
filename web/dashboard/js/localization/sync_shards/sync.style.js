/**
 * 🌍 [V55.5] Illacme Plenipes Localization Sync - Translation Style Shard
 * 职责：翻译风格预设回填、8 个 Prompt 文本框只读/编辑态切换、以及自定义模板匹配检测。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3]
 */

const promptMapping = {
    'prompt-preview-translate-system': 'translate_system',
    'prompt-preview-translate-user': 'translate_user',
    'prompt-preview-title-system': 'title_system',
    'prompt-preview-title-user': 'title_user',
    'prompt-preview-meta-system': 'metadata_system',
    'prompt-preview-meta-user': 'metadata_user',
    'prompt-preview-slug-system': 'slug_system',
    'prompt-preview-slug-user': 'slug_user',
    'prompt-preview-seo-system': 'seo_system',
    'prompt-preview-seo-user': 'seo_user'
};

window.updateStylePreview = (styleKey) => {
    const style = window.translationStyles?.[styleKey];
    const descEl = document.getElementById('style-description-box');

    if (!style) {
        // 自定义 Prompt 处理
        if (descEl) {
            descEl.innerHTML = `<span style="background: var(--accent-secondary, #00f2ff); color: var(--bg-solid, #000); padding: 2px 6px; border-radius: 4px; font-weight: 800; font-size: 0.7rem;">自定义</span> <p style="margin: 0; font-weight: 500;">正在使用专属于该品牌的个性化翻译 Prompt 模板。</p>`;
        }

        const prompts = window.settingsData?.translation?.prompts || {};

        // 移出只读限制，展现可编辑样式，并将内存中的值回填到输入框中
        Object.entries(promptMapping).forEach(([domId, propName]) => {
            const ta = document.getElementById(domId);
            if (!ta) return;
            ta.value = prompts[propName] || '';
            ta.removeAttribute('readonly');
            ta.style.background = 'var(--bg-agent-input)';
            ta.style.borderColor = 'rgba(var(--accent-primary-rgb), 0.25)';
            ta.style.cursor = 'text';
        });
        return;
    }

    // 更新描述卡片并触发平滑发光淡入动画
    if (descEl) {
        descEl.innerHTML = `
            <span style="background: var(--accent-secondary, #00f2ff); color: var(--bg-solid, #000); padding: 2px 6px; border-radius: 4px; font-weight: 800; font-size: 0.7rem;">${style.badge}</span>
            <p style="margin: 0; font-weight: 500;">${style.desc}</p>
        `;
    }

    // 动态回填 8 个 Prompt 预览文本框，并设置为只读且淡化样式，同时更新内存中的 settingsData
    Object.entries(promptMapping).forEach(([domId, propName]) => {
        const ta = document.getElementById(domId);
        const val = style[propName] || '';
        if (ta) {
            ta.value = val;
            ta.setAttribute('readonly', 'true');
            ta.style.background = 'rgba(var(--bg-modal-solid-rgb, 13, 14, 28), 0.5)';
            ta.style.borderColor = 'var(--glass-border)';
            ta.style.cursor = 'default';
        }
        // 同步修改内存配置
        if (typeof window.updateConfigField === 'function') {
            window.updateConfigField(`translation.prompts.${propName}`, val);
        }
    });
};

window.checkStyleMatch = () => {
    const selector = document.getElementById('style-selector');
    if (!selector) return;

    let matchKey = 'custom';

    const vals = {};
    Object.entries(promptMapping).forEach(([domId, propName]) => {
        const ta = document.getElementById(domId);
        vals[propName] = ta ? ta.value : '';
    });

    if (window.translationStyles) {
        for (const [key, tpl] of Object.entries(window.translationStyles)) {
            const isMatch = (
                (tpl.translate_system || '') === (vals.translate_system || '') &&
                (tpl.translate_user || '') === (vals.translate_user || '') &&
                (tpl.title_system || '') === (vals.title_system || '') &&
                (tpl.title_user || '') === (vals.title_user || '') &&
                (tpl.metadata_system || '') === (vals.metadata_system || '') &&
                (tpl.metadata_user || '') === (vals.metadata_user || '') &&
                (tpl.slug_system || '') === (vals.slug_system || '') &&
                (tpl.slug_user || '') === (vals.slug_user || '')
            );
            if (isMatch) {
                matchKey = key;
                break;
            }
        }
    }

    selector.value = matchKey;

    const descEl = document.getElementById('style-description-box');
    if (descEl) {
        if (matchKey === 'custom') {
            descEl.innerHTML = `
                <span style="background: var(--accent-secondary, #00f2ff); color: var(--bg-solid, #000); padding: 2px 6px; border-radius: 4px; font-weight: 800; font-size: 0.7rem;">自定义</span>
                <p style="margin: 0; font-weight: 500;">正在使用专属于该品牌的个性化翻译 Prompt 模板。</p>
            `;
        } else if (window.translationStyles?.[matchKey]) {
            const style = window.translationStyles[matchKey];
            descEl.innerHTML = `
                <span style="background: var(--accent-secondary, #00f2ff); color: var(--bg-solid, #000); padding: 2px 6px; border-radius: 4px; font-weight: 800; font-size: 0.7rem;">${style.badge}</span>
                <p style="margin: 0; font-weight: 500;">${style.desc}</p>
            `;
        }
    }
};
