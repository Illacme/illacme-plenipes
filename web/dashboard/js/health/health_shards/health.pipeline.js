/**
 * 🩺 [V55.0] Illacme Plenipes Governance Diagnostics - Pipeline Senses Shard
 * 职责：6 节点因果出版流水线（文库、翻译、主题、网址、托管、社交）全景状态感知、胶囊回填与快照持久化
 * 架构：由 health.context.js 拆分而来 (SOP-02 模块拆分标准)
 */

window.renderPipelineSenses = function (data, s, pubMode, currentModeMeta) {
    if (!data || data.error) return;

    // ══════════════════════════════════════════════════════════════
    // 🗺️ [6 节点因果出版流水线] 全景状态感知与左边栏胶囊数据回填
    // ══════════════════════════════════════════════════════════════

    // 阶段 1: 原稿文库
    const pipeValVault = document.getElementById('pipe-val-vault');
    const pipeDotVault = document.getElementById('pipe-dot-vault');
    const pipeCapVault = document.getElementById('pipe-cap-vault');
    if (pipeValVault && data.vault) {
        let docCount = 0;
        if (window.realManuscriptCache && window.realManuscriptCache.length > 0) {
            docCount = window.realManuscriptCache.length;
        } else if (typeof data.vault.doc_count === 'number') {
            docCount = data.vault.doc_count;
        }
        const hasVault = Boolean(data.vault.root);
        pipeValVault.innerText = hasVault ? (docCount > 0 ? `${docCount} 篇原稿` : '文库空空如也') : '未配置文库';
        if (pipeDotVault) pipeDotVault.className = hasVault && docCount > 0 ? 'pipe-dot healthy' : (hasVault ? 'pipe-dot warning' : 'pipe-dot offline');
        if (pipeCapVault) {
            pipeCapVault.title = `📂 1. 原稿文库 (Manuscript Library)\n────────────────────────\n• 收录原稿：${docCount} 篇 Markdown 文稿\n• 解析方言：${data.vault.dialect || 'Standard CommonMark'}\n• 物理文库：${data.vault.root || '暂未绑定'}\n\n💡 点击一键直达文库管理与原稿创作`;
        }
    }

    // 阶段 2: 多语言翻译
    const pipeValI18n = document.getElementById('pipe-val-i18n');
    const pipeDotI18n = document.getElementById('pipe-dot-i18n');
    const pipeCapI18n = document.getElementById('pipe-cap-i18n');
    if (pipeValI18n && data.i18n) {
        const sourceLang = data.i18n.source || 'zh';
        const targets = data.i18n.targets || [];
        const aiProvider = data.ai?.provider || 'AI';
        const isAiOnline = data.ai_status !== 'degraded' && data.ai_status !== 'offline';

        if (pubMode === 'basic') {
            pipeValI18n.innerText = `母语 (${sourceLang}) · 基础物理离线`;
            if (pipeDotI18n) pipeDotI18n.className = 'pipe-dot standby';
        } else if (pubMode === 'enhanced') {
            pipeValI18n.innerText = `母语 (${sourceLang}) · 智能 SEO 增强`;
            if (pipeDotI18n) pipeDotI18n.className = isAiOnline ? 'pipe-dot healthy' : 'pipe-dot warning';
        } else {
            pipeValI18n.innerText = targets.length > 0 ? `母语 (${sourceLang}) ➔ ${targets.length} 目标语种` : `母语 (${sourceLang}) · 全球分发待命`;
            if (pipeDotI18n) pipeDotI18n.className = isAiOnline ? 'pipe-dot healthy' : 'pipe-dot warning';
        }

        if (pipeCapI18n) {
            pipeCapI18n.title = `🌍 2. 多语言翻译 (Multilingual Translation)\n────────────────────────\n• 出版模式：${currentModeMeta.icon} ${currentModeMeta.title} (${currentModeMeta.en})\n• 母语言：${sourceLang.toUpperCase()}\n• 目标语种：${targets.length > 0 ? targets.join(', ').toUpperCase() : '未配置目标语种 (仅母语出版)'}\n• 算力基座：${aiProvider} (${isAiOnline ? '🟢 在线' : '🟡 待命'})\n\n💡 点击一键直达多语种治理与翻译风格配置`;
        }
    }

    // 阶段 3: 网站主题
    const pipeValTheme = document.getElementById('pipe-val-theme');
    const pipeDotTheme = document.getElementById('pipe-dot-theme');
    const pipeCapTheme = document.getElementById('pipe-cap-theme');
    if (pipeValTheme) {
        const rawTheme = data.theme || s.active_theme || 'Sovereign';
        const cleanTheme = rawTheme.replace(/\s*\([^)]*\)/g, '').trim();
        const cleanThemeName = (window.getThemeDisplayName ? window.getThemeDisplayName(cleanTheme || rawTheme) : cleanTheme) || 'Sovereign';
        pipeValTheme.innerText = `${cleanThemeName} · ${currentModeMeta.short}`;
        if (pipeDotTheme) pipeDotTheme.className = 'pipe-dot healthy';

        // 动态解析当前模式下的 SEO 策略
        const seoStrategy = s.governance?.seo_strategy || (pubMode === 'basic' ? 'heuristic' : (pubMode === 'enhanced' ? 'ai_alignment' : 'ai_sync'));
        const strategyLabels = {
            'ai_sync': 'AI 翻译同步 (精确语义翻译)',
            'ai_localized': 'AI 区域搜索对齐 (本地化检索优化)',
            'ai_alignment': 'AI 标题与点击率调优 (提升 CTR)',
            'ai_authority': 'AI 核心概念标记 (权威实体提取)',
            'heuristic': '结构化提取 (H1与正文规则抓取)',
            'protocol': '社交协议增强 (JSON-LD / Open Graph)'
        };
        const strategyDesc = strategyLabels[seoStrategy] || seoStrategy;

        if (pipeCapTheme) {
            pipeCapTheme.title = `🎭 3. 网站主题 (Visual Theme & Layout)\n────────────────────────\n• 装帧主题：${cleanThemeName} ${rawTheme.toLowerCase().includes('default') ? '(系统默认)' : ''}\n• 出版模式：${currentModeMeta.icon} ${currentModeMeta.title} (${currentModeMeta.en})\n• SEO 策略：${strategyDesc}\n\n💡 点击一键直达视觉主题与出版模式设置`;
        }
    }

    // 阶段 4: 网址路径
    const pipeValRouting = document.getElementById('pipe-val-routing');
    const pipeDotRouting = document.getElementById('pipe-dot-routing');
    const pipeCapRouting = document.getElementById('pipe-cap-routing');
    if (pipeValRouting) {
        const dirMode = s.translation?.slug_dir_mode || 'nested';
        const slugMode = s.translation?.slug_mode || 'ai';
        const dirLabels = { 'flat': '极简根目录', 'prefix': 'SEO 语言前缀', 'nested': '文库目录树' };
        const slugLabels = { 'ai': 'AI 语义 Slug', 'filename': '原文件名清洗' };
        pipeValRouting.innerText = `${dirLabels[dirMode] || '极简根目录'} · ${slugLabels[slugMode] || 'AI 语义'}`;
        if (pipeDotRouting) pipeDotRouting.className = 'pipe-dot healthy';
        if (pipeCapRouting) {
            const sampleUrl = dirMode === 'prefix' ? '/en/hello-world' : '/hello-world';
            pipeCapRouting.title = `🧭 4. 网址路径 (URL Routing & Slug)\n────────────────────────\n• 路径结构：${dirLabels[dirMode] || dirMode}\n• 生成法则：${slugLabels[slugMode] || slugMode}\n• 访问范例：https://yourdomain.com${sampleUrl}\n\n💡 点击一键直达网址路径定制与全息沙盒`;
        }
    }

    // 阶段 5 & 阶段 6: 独立站托管与社交分发感应 (由 health.pipeline_egress.js 供给)
    if (typeof window.renderPipelineEgressSenses === 'function') {
        window.renderPipelineEgressSenses(data, s);
    }
    const pipeValHosting = document.getElementById('pipe-val-hosting');
    const pipeDotHosting = document.getElementById('pipe-dot-hosting');
    const pipeValSyndication = document.getElementById('pipe-val-syndication');
    const pipeDotSyndication = document.getElementById('pipe-dot-syndication');


    // 💾 [Zero-Flicker 状态快照缓存]
    try {
        const pipelineSnapshot = {
            vault: { val: pipeValVault?.innerText, dot: pipeDotVault?.className },
            i18n: { val: pipeValI18n?.innerText, dot: pipeDotI18n?.className },
            theme: { val: pipeValTheme?.innerText, dot: pipeDotTheme?.className },
            routing: { val: pipeValRouting?.innerText, dot: pipeDotRouting?.className },
            hosting: { val: pipeValHosting?.innerText, dot: pipeDotHosting?.className },
            syndication: { val: pipeValSyndication?.innerText, dot: pipeDotSyndication?.className }
        };
        sessionStorage.setItem('_illacme_pipe_cache', JSON.stringify(pipelineSnapshot));
    } catch (_) {}

    // 兼容旧版选择器回填 (如有)
    const aiEl = document.getElementById('ctx-ai');
    const i18nEl = document.getElementById('ctx-i18n');
    const dialectEl = document.getElementById('ctx-dialect');
    if (dialectEl && data.vault) dialectEl.innerText = data.vault.dialect || '-';
    if (aiEl && data.ai) aiEl.innerText = `${data.ai.provider || 'AI'} / ${data.ai.model || 'READY'}`;
    if (i18nEl && data.i18n) i18nEl.innerText = `${data.i18n.source || 'zh'} ➔ ${(data.i18n.targets || []).join(', ') || 'NONE'}`;

    // 🚀 [V52.11] 依赖安装自动化
    if (data.needs_install && typeof triggerThemeInstall === 'function') {
        triggerThemeInstall();
    }
};
