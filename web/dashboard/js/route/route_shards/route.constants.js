/**
 * 🛣️ [V100.9] Illacme Plenipes Route Matrix - Constants & Core Shard Hub
 * 演进版本：🚀 [V100.9] -> [V106.0] -> [V106.1] -> [V107.0] -> [V107.5] -> [V107.6]
 * 架构职责：分发路由与频道映射核心常数、字典与子分片门面控制器 (SOP-02 物理拆分微步演进)
 * 
 * 分片拓扑：
 * 1. route.i18n.dict.js       - 图标调色盘 EMOJI_PALETTE、50 语种导航字典 COMMON_SLOT_I18N、DEFAULT_THEME_SLOTS
 * 2. route.style.selector.js  - 语种元数据解析 getProductLanguageMeta、译文风格下拉 buildTranslationStyleSelectHtml
 * 3. route.source.options.js  - 树形文库目录扁平化、目录树缩进、原稿篇数统计 buildSourceDatalistOptions / getSourcePickerItems
 * 4. route.source.picker.js   - 毛玻璃 Combobox 输入框与浮层 UI 渲染 buildSourcePickerHtml / openSourceDropdown / toggleSourceDropdown
 * 5. route.source.events.js   - 键盘上下键选中、回车高亮、实时搜索与失焦同步 handleSourceInput*
 * 6. route.path.badges.js     - 实时产物路径推演 getLivePathTooltip、原稿命中统计 calculateRouteHitCount、失效自愈 autoHealOrphanSource
 */

(function () {
    const shardFiles = [
        "route.i18n.dict.js",
        "route.style.selector.js",
        "route.source.options.js",
        "route.source.picker.js",
        "route.source.events.js",
        "route.path.badges.js"
    ];

    // 🛡️ Node.js 测试沙箱环境下的子分片自动装配 (防单测孤立 eval)
    if (typeof require === 'function' || typeof fs !== 'undefined') {
        try {
            const _fs = (typeof fs !== 'undefined') ? fs : require('fs');
            const _path = (typeof path !== 'undefined') ? path : (typeof require === 'function' ? require('path') : null);
            const dir = (typeof __dirname !== 'undefined') ? __dirname : 'web/dashboard/js/route/route_shards';
            shardFiles.forEach(s => {
                const target = _path ? _path.join(dir, s) : `${dir}/${s}`;
                if (_fs.existsSync(target)) {
                    eval(_fs.readFileSync(target, 'utf8'));
                }
            });
        } catch (e) {
            // 静默忽略非 Node/fs 环境
        }
    }

    // 🌐 核心命名空间门面 (向后兼容与集中索引)
    window.RouteConstantsHub = {
        version: "107.6",
        shards: shardFiles,
        isLoaded: function () {
            return !!(
                window.EMOJI_PALETTE &&
                window.COMMON_SLOT_I18N &&
                window.buildTranslationStyleSelectHtml &&
                window.buildSourcePickerHtml &&
                window.handleSourceInputChange &&
                window.getLivePathTooltip
            );
        }
    };

    // 💡 调试与完整性感知
    if (typeof console !== 'undefined' && console.debug) {
        console.debug('[RouteConstantsHub] Sub-shards topology successfully initialized.');
    }
})();
