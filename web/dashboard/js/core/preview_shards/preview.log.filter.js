/**
 * ⚡ [V100.9] Illacme Plenipes Preview Log Filter & Stepper Driver
 * 职责：
 * 1. 日志去重与文档上下文记录器；
 * 2. 创作者友好精简日志过滤与对象提取（《xxx.md》）；
 * 3. 驱动 4 步 Stepper 步骤条状态机推进。
 * 🛡️ [SOP-02 模块拆分 / AEL-Iter-v10.3 基因克隆]
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
