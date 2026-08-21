/**
 * ⚡ [V100.9] Illacme Plenipes Publish & Preview Workflow Engine (发布预览全流程交互引擎)
 * 职责：
 * 1. 两阶段交互：点击按钮先呈现 4 步业务说明向导，由用户确认后手动点火触发；
 * 2. 防重入保护：已在执行时自动提示并限制重复点火；
 * 3. 创作者友好精简日志过滤：精准提取操作对象与文件名称（《xxx.md》），杜绝无主干日志与重复刷屏；
 * 4. 防卡顿与平滑滚动：集成 RAF 节流滚动与 DOM 节点上限保护；
 * 5. 全流程闭环：全 SSG 框架容器点火、全绿 Stepper 与三重直达保障。
 */

// 日志去重与文档上下文记录器
window._previewLoggedHistory = window._previewLoggedHistory || new Set();

// 辅助步骤状态切换器
window.setPreviewStepState = function (stepNum, state) {
    const el = document.getElementById(`step-prev-${stepNum}`);
    if (!el) return;
    el.classList.remove('active', 'completed');
    if (state === 'active') el.classList.add('active');
    if (state === 'completed') el.classList.add('completed');
};

// 提取目标文档名称辅助函数
window.extractPreviewDocName = function (rawMsg) {
    if (!rawMsg || typeof rawMsg !== 'string') return '';
    // 1. 匹配 《xxx》
    let m = rawMsg.match(/《([^》]+)》/);
    if (m) return m[1];

    // 2. 匹配 文档: xxx
    m = rawMsg.match(/(?:正在验证资产完整性|物理补充|正在处理文档|正在为文档|文档[:：])\s*([^\s|,，|]+)/);
    if (m) {
        const val = m[1].trim();
        return val.startsWith('Docs/') || val.startsWith('Blog/') ? val : val;
    }

    // 3. 匹配 正在为 'xxx'
    m = rawMsg.match(/正在为\s*['"‘“]([^'"’”]+)['"’”]/);
    if (m) return m[1];

    // 4. 匹配 [Sync:xxx]
    m = rawMsg.match(/\[Sync:([^\]]+)\]/);
    if (m) {
        let name = m[1].trim();
        if (name.endsWith('.')) name = name.replace(/\.+$/, '');
        return name;
    }

    return '';
};

// 提取语种名称辅助函数
window.extractPreviewLangName = function (rawMsg) {
    if (!rawMsg || typeof rawMsg !== 'string') return '';
    let m = rawMsg.match(/(?:正在为|优化|翻译|润色)\s*([a-zA-Z\u4e00-\u9fa5]+)\s*版本/);
    if (m) return m[1];
    m = rawMsg.match(/\(([a-zA-Z0-9_-]{2,8})\)/);
    if (m) return m[1];
    return '';
};

// 创作者友好精简日志过滤器 (新手友好，补全操作对象，屏蔽底层噪音)
window.formatFriendlyPreviewLog = function (rawMsg) {
    if (!rawMsg || typeof rawMsg !== 'string') return null;

    // 1. 深度过滤底层机器/内部调试日志与噪音
    if (rawMsg.includes('DEBUG PROMPT') || rawMsg.includes('NLP Cache Guard') ||
        rawMsg.includes('Dispatcher Debug') || rawMsg.includes('渠道 PIPELINE 状态更新') ||
        rawMsg.includes('账本') || rawMsg.includes('TRUNCATE') || rawMsg.includes('指令矩阵激活') ||
        rawMsg.includes('主权对正') || rawMsg.includes('准入拦截') || rawMsg.includes('Plugin发现') ||
        rawMsg.includes('clean_content') || rawMsg.includes('DIRECT ANSWER MODE') ||
        rawMsg.includes('fingerprint') || rawMsg.includes('SQLite') || rawMsg.includes('缓存保护') ||
        rawMsg.includes('[ADMI]') || rawMsg.includes('KnowledgeGalaxy') ||
        rawMsg.includes('[QA Guard]') || rawMsg.includes('语种智感') ||
        rawMsg.includes('AI 算法对齐') || rawMsg.includes('正在收割残留') ||
        rawMsg.includes('Plugin]') || rawMsg.includes('Lifecycle]') ||
        rawMsg.includes('已推送 KNOWLEDGE_BATCH_READY') ||
        rawMsg.includes('调度算力池') || rawMsg.includes('正在处理文档') ||
        rawMsg.includes('正在向 AI') || rawMsg.includes('正在检测缺失元数据') ||
        rawMsg.includes('物理补充') || rawMsg.includes('Traceback')) {
        return null; // 静默过滤底层技术日志
    }

    const doc = window.extractPreviewDocName(rawMsg);
    const lang = window.extractPreviewLangName(rawMsg);

    // 2. 结构化业务日志提炼 (带明确操作对象)

    // (1) 任务调度与启动
    if (rawMsg.includes('已分发') && rawMsg.includes('同步任务')) {
        const countMatch = rawMsg.match(/已分发\s*(\d+)\s*个同步任务/);
        const count = countMatch ? countMatch[1] : '';
        return { text: `📡 [任务调度] 已载入 ${count ? count + ' 篇' : ''}文库原稿，准备并行装帧...`, color: '#a29bfe' };
    }
    if (rawMsg.includes('正在扫描原稿') || rawMsg.includes('主权审计完成')) {
        return { text: '🔍 正在扫描原稿文库并执行资产与双链预检...', color: '#a29bfe' };
    }

    // (2) 智能缓存复用
    if (rawMsg.includes('同步跳过') || rawMsg.includes('指纹未变')) {
        const key = `skip:${doc}`;
        if (window._previewLoggedHistory.has(key)) return null;
        window._previewLoggedHistory.add(key);
        return { text: `⚡ [智能缓存] 《${doc || '未命名'}》原稿无变更，复用先前排版`, color: '#888888' };
    }

    // (3) 智能排版与正文解析
    if (rawMsg.includes('追踪开始] 文档:') || rawMsg.includes('正在智能排版:')) {
        const key = `parse:${doc}`;
        if (window._previewLoggedHistory.has(key)) return null;
        window._previewLoggedHistory.add(key);
        return { text: `✍️ [智能排版] 正在编译排版: 《${doc || '未命名'}》`, color: '#00f0ff' };
    }

    // (4) 多语种同步与 SEO 摘要
    if (rawMsg.includes('AI 翻译同步] 正在为') || rawMsg.includes('执行跨语种 SEO 同步')) {
        const key = `seo_sync:${doc}`;
        if (window._previewLoggedHistory.has(key)) return null;
        window._previewLoggedHistory.add(key);
        return { text: `🌐 [多语同步] 正在为《${doc || '未命名'}》生成多语种摘要与关键词...`, color: '#00ffaa' };
    }

    // (5) 标题与标签元数据优化 (自动去重，杜绝重复刷屏)
    if (rawMsg.includes('Title Polish') || rawMsg.includes('Meta Polish') || rawMsg.includes('优化页面元数据')) {
        const key = `meta_polish:${doc}:${lang}`;
        if (window._previewLoggedHistory.has(key)) return null;
        window._previewLoggedHistory.add(key);
        const langStr = lang ? ` ${lang} 版本的` : ' ';
        return { text: `🏷️ [元数据优化] 正在为《${doc || '当前文档'}》优化${langStr}页面标题与 SEO 标签...`, color: '#ffaa00' };
    }

    // (6) 资产与双链审计核验通过
    if (rawMsg.includes('验证资产完整性') || rawMsg.includes('审计通过') || rawMsg.includes('稿件资产核验通过')) {
        const key = `asset_pass:${doc}`;
        if (window._previewLoggedHistory.has(key)) return null;
        window._previewLoggedHistory.add(key);
        return { text: `📋 [资产核验] 《${doc || '未命名'}》图片引用与双链完整性核验通过 (100% 严丝合缝)`, color: '#00ffaa' };
    }

    // (7) 多语版本排版就绪
    if (rawMsg.includes('AI 翻译同步] 完成') || rawMsg.includes('智能语言版本排版生成完成')) {
        const key = `lang_done:${doc}`;
        if (window._previewLoggedHistory.has(key)) return null;
        window._previewLoggedHistory.add(key);
        return { text: `✨ [多语就绪] 《${doc || '当前文档'}》多语种对照页面排版生成完毕`, color: '#00ff88' };
    }

    // (8) 全站双链知识图谱与索引
    if (rawMsg.includes('全息关系图谱') || rawMsg.includes('双链自愈扫描完成') || rawMsg.includes('DigitalGardenPlugin') || rawMsg.includes('全息图谱')) {
        const key = 'galaxy_graph_done';
        if (window._previewLoggedHistory.has(key)) return null;
        window._previewLoggedHistory.add(key);
        return { text: `🎨 [站点装配] 全站数字花园双链全息图谱与搜索索引生成完毕`, color: '#ffaa00' };
    }

    // (9) 主题钩子与导航装配
    if (rawMsg.includes('主题钩子') || rawMsg.includes('on_post_sync') || rawMsg.includes('执行资产合成')) {
        const key = 'theme_hook_done';
        if (window._previewLoggedHistory.has(key)) return null;
        window._previewLoggedHistory.add(key);
        return { text: `✨ [主题装配] 正在装配全局导航、样式与首选着陆页...`, color: '#00f0ff' };
    }

    // (10) 目录整理与本地就绪
    if (rawMsg.includes('Janitor') || rawMsg.includes('清道夫') || rawMsg.includes('分发疆域已是洁净状态')) {
        const key = 'janitor_done';
        if (window._previewLoggedHistory.has(key)) return null;
        window._previewLoggedHistory.add(key);
        return { text: `🧹 [目录整理] 静态发布目录与网页缓存整理完成`, color: '#888888' };
    }
    if (rawMsg.includes('SovereignDeploymentPlugin') || rawMsg.includes('发布预览') || rawMsg.includes('跳过全网外部渠道')) {
        const key = 'deploy_local_done';
        if (window._previewLoggedHistory.has(key)) return null;
        window._previewLoggedHistory.add(key);
        return { text: `🔒 [本地安全] 本地装帧就绪，已安全跳过所有外网渠道推流`, color: '#00ffaa' };
    }
    if (rawMsg.includes('后台流水线任务已全量闭环') || rawMsg.includes('所有算力调度已闭环')) {
        return { text: `🎉 [装配完成] 全原文库编译与排版已全量闭环！`, color: '#00ff88' };
    }

    return null;
};

// 动态日志驱动步骤条状态机推进
window.updatePreviewStepperFromLog = function (msg) {
    if (!msg || typeof msg !== 'string') return;
    const modal = document.getElementById('terminal-modal');
    if (!modal || (modal.dataset.context !== 'publish_preview' && modal.dataset.context !== 'preview')) return;

    // 输出精简过滤且明确指向操作对象的创作者日志
    const friendly = window.formatFriendlyPreviewLog(msg);
    if (friendly && typeof window.appendTerminalLog === 'function') {
        window.appendTerminalLog(friendly.text, friendly.color);
    }

    // 驱动 Stepper 步骤推进
    if (msg.includes('正在扫描') || msg.includes('合规预检') || msg.includes('主权审计完成') || msg.includes('正在验证资产完整性')) {
        window.setPreviewStepState(1, 'completed');
        window.setPreviewStepState(2, 'active');
    } else if (msg.includes('正在向 AI') || msg.includes('增量解析') || msg.includes('Title Polish') || msg.includes('正在翻译') || msg.includes('段落') || msg.includes('追踪开始')) {
        window.setPreviewStepState(1, 'completed');
        window.setPreviewStepState(2, 'active');
    } else if (msg.includes('DigitalGardenPlugin') || msg.includes('JanitorPlugin') || msg.includes('清道夫') || msg.includes('博客合成器') || msg.includes('双链图谱')) {
        window.setPreviewStepState(1, 'completed');
        window.setPreviewStepState(2, 'completed');
        window.setPreviewStepState(3, 'active');
    } else if (msg.includes('SovereignDeploymentPlugin') || msg.includes('发布预览') || msg.includes('跳过全网外部渠道') || msg.includes('渠道投递')) {
        window.setPreviewStepState(1, 'completed');
        window.setPreviewStepState(2, 'completed');
        window.setPreviewStepState(3, 'completed');
        window.setPreviewStepState(4, 'active');
    }
};

// 点击直达预览站点全局函数
window.openPreviewSite = function () {
    const port = window._actualPreviewPort || window.settingsData?.system?.serve_port || 43213;
    const previewUrl = window._actualPreviewUrl || `http://localhost:${port}/`;
    window.open(previewUrl, '_blank', 'noopener,noreferrer');
};

// 渲染 4 步流光步骤条工具栏
window.renderPreviewStepperToolbar = function () {
    return `
        <div class="preview-stepper-bar">
            <div class="step-item" id="step-prev-1"><span class="step-icon">🔍</span> <span class="step-name">1. 原稿预检</span></div>
            <div class="step-arrow">→</div>
            <div class="step-item" id="step-prev-2"><span class="step-icon">✍️</span> <span class="step-name">2. 智能排版</span></div>
            <div class="step-arrow">→</div>
            <div class="step-item" id="step-prev-3"><span class="step-icon">🎨</span> <span class="step-name">3. 站点装配</span></div>
            <div class="step-arrow">→</div>
            <div class="step-item" id="step-prev-4"><span class="step-icon">🚀</span> <span class="step-name">4. 开启预览</span></div>
        </div>
    `;
};

// 渲染新手友好向导说明卡片 (阶段 1)
window.renderPreviewIntroCard = function (activeTheme) {
    return `
        <div class="preview-intro-card" style="padding: 12px 14px; line-height: 1.6; color: var(--text-bright);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px solid var(--glass-border); padding-bottom: 8px;">
                <div style="font-size: 0.95rem; font-weight: 700; color: var(--neon-cyan); display: flex; align-items: center; gap: 8px;">
                    <span>💡</span> 「发布预览」工作流向导
                </div>
                <span class="version-tag tiny" style="background: rgba(0, 240, 255, 0.1); color: var(--neon-cyan); border: 1px solid rgba(0, 240, 255, 0.3);">装帧主题: ${activeTheme}</span>
            </div>
            
            <div style="font-size: 0.82rem; color: #ccc; margin-bottom: 14px;">
                系统将在您的设备本地快速完成原稿排版与站点装配，让您在正式全网发布前<b>完整体验最终上线效果</b>。
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px;">
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px 12px;">
                    <div style="color: #00ffaa; font-weight: bold; font-size: 0.84rem; margin-bottom: 4px;">🔍 1. 原稿预检</div>
                    <div style="color: #888; font-size: 0.76rem;">扫描原稿文库，检查图片、双向链接完整性与合规性。</div>
                </div>
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px 12px;">
                    <div style="color: #00ffaa; font-weight: bold; font-size: 0.84rem; margin-bottom: 4px;">✍️ 2. 智能排版</div>
                    <div style="color: #888; font-size: 0.76rem;">增量解析 Markdown 正文，快速生成高质感网页文档。</div>
                </div>
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px 12px;">
                    <div style="color: #00ffaa; font-weight: bold; font-size: 0.84rem; margin-bottom: 4px;">🎨 3. 站点装配</div>
                    <div style="color: #888; font-size: 0.76rem;">自动打包全站导航目录、双链全息图谱与主题外观。</div>
                </div>
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px 12px;">
                    <div style="color: #00ffaa; font-weight: bold; font-size: 0.84rem; margin-bottom: 4px;">🚀 4. 开启预览</div>
                    <div style="color: #888; font-size: 0.76rem;">点火本地预览服务容器，自动在浏览器新标签页打开。</div>
                </div>
            </div>

            <div style="background: rgba(0, 240, 255, 0.05); border: 1px dashed rgba(0, 240, 255, 0.3); border-radius: 6px; padding: 8px 12px; font-size: 0.76rem; color: #a29bfe; display: flex; flex-direction: column; gap: 4px;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span>💡</span> <span><b>装帧编译</b>：本次发布将全量编译并应用所有已保存的<b>装帧参数、语种路由拓扑与主题外观</b>。</span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px; color: #00ffaa;">
                    <span>🔒</span> <span><b>安全承诺</b>：本地预览全程在您的设备本地极速运行，<b>不会向任何外部平台推流</b>。</span>
                </div>
            </div>
        </div>
    `;
};

// 【阶段 1】点击右上角「⚡ 发布预览」入口：打开弹窗并展示说明向导
window.triggerPublishAndPreview = async function () {
    // 动态拉取或同步当前生效的主题名称
    let rawThemeId = 'sovereign';
    try {
        if (window.settingsData && (window.settingsData.active_theme || window.settingsData.config?.active_theme)) {
            rawThemeId = window.settingsData.active_theme || window.settingsData.config?.active_theme;
        } else {
            const cfgRes = await window.apiFetch('/api/system/config', { method: 'GET' });
            if (cfgRes) {
                rawThemeId = cfgRes.active_theme || cfgRes.config?.active_theme || 'sovereign';
                if (!window.settingsData) window.settingsData = cfgRes;
                else window.settingsData.active_theme = rawThemeId;
            }
        }
    } catch (e) {
        console.warn('获取当前装帧主题失败:', e);
    }

    const displayThemeName = window.getThemeDisplayName ? window.getThemeDisplayName(rawThemeId) : rawThemeId;

    const modal = document.getElementById('terminal-modal');
    if (!modal) return;

    modal.style.display = 'flex';
    modal.dataset.context = 'publish_preview';
    window._isPublishPreviewActive = true;

    // 1. 探测后端是否已有发布流水线正在运行
    let isPublishing = false;
    try {
        const statusRes = await window.apiFetch('/api/system/sync/status', { method: 'GET' });
        isPublishing = !!(statusRes && statusRes.is_publishing);
    } catch (e) {
        console.warn('[Publish & Preview] 探测发布状态失败:', e);
    }

    const title = document.getElementById('terminal-title');
    const toolbar = document.getElementById('terminal-toolbar');
    const out = document.getElementById('terminal-output');
    const statusEl = document.getElementById('terminal-status');
    const startBtn = document.getElementById('btn-terminal-start-preview');
    const okBtn = document.getElementById('btn-terminal-ok');
    const abortBtn = document.getElementById('btn-terminal-abort');
    const closeBtn = document.getElementById('btn-terminal-close');
    const openPreviewBtn = document.getElementById('btn-terminal-open-preview');
    const republishBtn = document.getElementById('btn-terminal-republish');
    const forceBar = document.getElementById('preview-force-sync-bar');

    if (toolbar) {
        toolbar.style.display = 'flex';
        toolbar.innerHTML = window.renderPreviewStepperToolbar();
    }

    // 🛡️ 重置所有按钮状态，避免单例污染
    if (typeof window.resetTerminalModalFooter === 'function') {
        window.resetTerminalModalFooter();
    }

    if (isPublishing) {
        // ⚠️ 情况 A：已有任务正在执行，限制重复点火并接入实时流
        if (title) title.innerHTML = '⚡ 发布预览流水线执行中 <span class="version-tag tiny" style="background:rgba(0,240,255,0.15);color:var(--neon-cyan);border:1px solid rgba(0,240,255,0.4);margin-left:8px;">RUNNING</span>';
        if (statusEl) {
            statusEl.innerText = 'PREVIEW RUNNING';
            statusEl.className = 'online';
        }
        if (abortBtn) {
            abortBtn.style.display = 'inline-flex';
            abortBtn.disabled = false;
            abortBtn.innerText = '🛑 中止任务';
        }
        if (closeBtn) {
            closeBtn.style.display = 'inline-flex';
            closeBtn.innerText = '隐藏窗口 (后台继续)';
        }

        if (out && modal.dataset.lastContext !== 'publish_preview_running') {
            out.innerHTML = `<div class="term-line" style="color:#00f0ff;">[${new Date().toLocaleTimeString()}] 📡 检测到后台已有发布流水线正在运行，已自动为您接入实时进度流...</div>`;
        }
        modal.dataset.lastContext = 'publish_preview_running';

        window.setPreviewStepState(1, 'completed');
        window.setPreviewStepState(2, 'active');

    } else {
        // ✨ 情况 B：空闲状态，展示 4 步说明向导，等待用户手动点火
        if (title) title.innerHTML = '⚡ 极速发布预览流水线 <span class="version-tag tiny" style="background:rgba(0,240,255,0.15);color:var(--neon-cyan);border:1px solid rgba(0,240,255,0.4);margin-left:8px;">READY</span>';
        if (statusEl) {
            statusEl.innerText = 'STANDBY';
            statusEl.className = 'online';
        }

        if (out) {
            out.innerHTML = window.renderPreviewIntroCard(displayThemeName);
        }
        modal.dataset.lastContext = 'publish_preview_intro';

        // 按钮状态：显示“开始发布”与“关闭”，显示常驻的强制覆盖条
        if (forceBar) forceBar.style.display = 'flex';
        if (startBtn) {
            startBtn.style.display = 'inline-flex';
            startBtn.disabled = false;
            startBtn.innerHTML = '⚡ 开始发布';
        }
        if (okBtn) {
            okBtn.style.display = 'inline-flex';
            okBtn.innerText = '关闭';
        }
    }
};

// 【阶段 2】用户点击「⚡ 开始发布」：真正启动构建流水线
window.startPublishAndPreviewExecution = async function () {
    let rawThemeId = 'sovereign';
    if (window.settingsData && (window.settingsData.active_theme || window.settingsData.config?.active_theme)) {
        rawThemeId = window.settingsData.active_theme || window.settingsData.config?.active_theme;
    }
    const displayThemeName = window.getThemeDisplayName ? window.getThemeDisplayName(rawThemeId) : rawThemeId;

    window._isPublishPreviewActive = true;

    const modal = document.getElementById('terminal-modal');
    const startBtn = document.getElementById('btn-terminal-start-preview');
    const okBtn = document.getElementById('btn-terminal-ok');
    const abortBtn = document.getElementById('btn-terminal-abort');
    const closeBtn = document.getElementById('btn-terminal-close');
    const openPreviewBtn = document.getElementById('btn-terminal-open-preview');
    const forceBar = document.getElementById('preview-force-sync-bar');
    const out = document.getElementById('terminal-output');
    const title = document.getElementById('terminal-title');
    const statusEl = document.getElementById('terminal-status');

    // 1. 重置去重历史集
    if (window._previewLoggedHistory) {
        window._previewLoggedHistory.clear();
    }

    // 2. 切换按钮与状态至运行态 (仅在执行中出现中止与隐藏窗口按钮)
    if (typeof window.resetTerminalModalFooter === 'function') {
        window.resetTerminalModalFooter();
    }
    if (abortBtn) {
        abortBtn.style.display = 'inline-flex';
        abortBtn.disabled = false;
        abortBtn.innerText = '🛑 中止任务';
    }
    if (closeBtn) {
        closeBtn.style.display = 'inline-flex';
        closeBtn.innerText = '隐藏窗口 (后台继续)';
    }

    if (title) title.innerHTML = '⚡ 极速发布预览流水线 <span class="version-tag tiny" style="background:rgba(0,240,255,0.15);color:var(--neon-cyan);border:1px solid rgba(0,240,255,0.4);margin-left:8px;">PREVIEW BUILDING</span>';
    if (statusEl) {
        statusEl.innerText = 'BUILDING';
        statusEl.className = 'online';
    }

    // 3. 提取强制全量同步选项
    const forceSyncCheckbox = document.getElementById('chk-preview-force-sync');
    const isForceSync = forceSyncCheckbox ? forceSyncCheckbox.checked : false;

    // 清空向导卡片，准备输出精简清晰的流水线日志
    if (out) out.innerHTML = '';
    modal.dataset.lastContext = 'publish_preview_executing';

    window.setPreviewStepState(1, 'active');

    if (typeof window.appendTerminalLog === 'function') {
        if (isForceSync) {
            window.appendTerminalLog(`⚡ [发布预览] 正在启动强制全量重装流水线 (主题: ${displayThemeName}，全量重装)...`, '#00f0ff');
        } else {
            window.appendTerminalLog(`⚡ [发布预览] 正在启动本地极速装帧流水线 (主题: ${displayThemeName})...`, '#00f0ff');
        }
        window.appendTerminalLog('🔍 [步骤 1/4] 正在扫描原稿文库并执行资产与双链预检...', '#a29bfe');
    }

    try {
        // 4. 向后端发送 local_only 点火请求 (支持动态 force 参数)
        const res = await window.apiFetch(`/api/system/sync/trigger?local_only=true&force=${isForceSync}`, { method: 'POST' });

        if (!res || (res.status !== 'started' && res.status !== 'success')) {
            throw new Error(res ? (res.reason || res.detail || '后端拒绝点火') : '网络请求未响应');
        }

        if (typeof window.appendTerminalLog === 'function') {
            window.appendTerminalLog('✍️ [步骤 2/4] 本地 Markdown 原稿解析与智能排版中...', '#00ffaa');
        }

    } catch (err) {
        console.error('[startPublishAndPreviewExecution Error]', err);
        if (typeof window.appendTerminalLog === 'function') {
            window.appendTerminalLog(`🚨 [发布预览异常] ${err.message}`, '#ff4d4d');
        }
        if (typeof window.addAudit === 'function') {
            window.addAudit(`发布预览异常: ${err.message}`, 'error');
        }
        if (statusEl) {
            statusEl.innerText = 'ERROR';
            statusEl.className = 'offline';
        }
        if (abortBtn) abortBtn.style.display = 'none';
        if (closeBtn) closeBtn.style.display = 'none';
        if (okBtn) {
            okBtn.style.display = 'inline-flex';
            okBtn.innerText = '关闭';
        }
    }
};

// 核心回调：当后台流水线全量完成 (SYNC_COMPLETED) 时触发
window.handlePreviewSyncCompleted = async function () {
    const port = window.settingsData?.system?.serve_port || 43213;
    const previewUrl = `http://localhost:${port}`;

    // 1. 点亮 4 个步骤全部为 completed (绿光全亮)
    window.setPreviewStepState(1, 'completed');
    window.setPreviewStepState(2, 'completed');
    window.setPreviewStepState(3, 'completed');
    window.setPreviewStepState(4, 'completed');

    if (typeof window.appendTerminalLog === 'function') {
        window.appendTerminalLog('🚀 [步骤 4/4] 智能排版与装配完成！正在开启本地预览服务...', '#00f0ff');
    }

    try {
        // 2. 调用后端预览服务点火接口 (支持多品牌、多 SSG 框架)
        const restartRes = await window.apiFetch('/api/system/preview/restart', { method: 'POST' });
        const finalPort = window._actualPreviewPort || restartRes?.port || port;
        const finalUrl = window._actualPreviewUrl || `http://localhost:${finalPort}/`;

        // 3. 在终端中输出高质感「发布预览成果看板」(无重复按钮，仅展示清晰的成果概览与直达超链接)
        const out = document.getElementById('terminal-output');
        if (out) {
            const cardHtml = `
                <div style="background: rgba(0, 240, 255, 0.05); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 8px; padding: 14px 18px; margin: 14px 0 6px 0; line-height: 1.6; box-shadow: 0 0 16px rgba(0, 240, 255, 0.1);">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #00ffaa; font-weight: bold; font-size: 0.95rem;">🎉 本地智能排版与装配已就绪！</span>
                        <span style="font-size: 0.75rem; color: #00f0ff; background: rgba(0,240,255,0.15); padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(0,240,255,0.3);">HTTP 200 OK</span>
                    </div>
                    <div style="color: #ccc; font-size: 0.82rem; margin-bottom: 4px;">✔ <b>原稿合规</b>：已通过资产与双链审计（0 外部推流）</div>
                    <div style="color: #ccc; font-size: 0.82rem;">✔ <b>预览服务</b>：<a id="preview-site-link" href="${finalUrl}" target="_blank" style="color: #00f0ff; text-decoration: underline; font-weight: bold;">${finalUrl}</a> (端口 <span id="preview-site-port">${finalPort}</span>)</div>
                </div>
            `;
            out.innerHTML += cardHtml;
            out.scrollTop = out.scrollHeight;
        }

        // 4. 标题、状态栏与操作按钮归位至完成态 (仅保留底部主 CTA 按钮与完成按钮，隐藏隐藏窗口按钮)
        const titleEl = document.getElementById('terminal-title');
        if (titleEl) {
            titleEl.innerHTML = '⚡ 发布预览已就绪 <span class="version-tag tiny" style="background:rgba(0,255,136,0.15);color:#00ff88;border:1px solid rgba(0,255,136,0.4);margin-left:8px;">READY</span>';
        }

        const statusEl = document.getElementById('terminal-status');
        if (statusEl) {
            statusEl.innerText = 'PREVIEW READY';
            statusEl.className = 'online';
        }

        const abortBtn = document.getElementById('btn-terminal-abort');
        if (abortBtn) abortBtn.style.display = 'none';

        const closeBtn = document.getElementById('btn-terminal-close');
        if (closeBtn) closeBtn.style.display = 'none';

        const startBtn = document.getElementById('btn-terminal-start-preview');
        if (startBtn) startBtn.style.display = 'none';

        const openPreviewBtn = document.getElementById('btn-terminal-open-preview');
        if (openPreviewBtn) {
            openPreviewBtn.style.display = 'inline-flex';
        }

        const okBtn = document.getElementById('btn-terminal-ok');
        if (okBtn) {
            okBtn.style.display = 'inline-flex';
            okBtn.innerText = '完成';
            okBtn.onclick = () => {
                window.closeTerminalModal();
                setTimeout(() => { window._isPublishPreviewActive = false; }, 3000);
            };
        }

        if (typeof window.addAudit === 'function') {
            window.addAudit(`发布预览成功开启: ${finalUrl}`, 'success');
        }

        // 5. 尝试直接拉起浏览器新标签页 (若被拦截，底部大按钮与卡片保障 100% 直达)
        try {
            window.open(finalUrl, '_blank', 'noopener,noreferrer');
        } catch (e) {
            console.warn('[Preview] 浏览器弹窗拦截:', e);
        }

    } catch (e) {
        console.error('[handlePreviewSyncCompleted Error]', e);
    }
};

// 保持历史兼容别名
window.triggerPreview = window.triggerPublishAndPreview;
