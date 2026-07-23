/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Render Facade Hub
 * 🚀 SOP-02 拆分完成门面文件
 * 职责：作为主入口聚合分片模块，代理导出全局渲染与交互 Handlers。
 * 对应物理分片：
 *   1. render_shards/plugins.render.cards.js (Pod 卡片构建、Tab 侧边栏与矩阵网格渲染)
 *   2. render_shards/plugins.render.fast_test.js (快捷测试连通性与演练 Log 终端)
 *   3. render_shards/plugins.render.diagnostics.js (跨插件诊断、剪贴板感应与配置备份算子)
 */

// 校验并确认所有分片挂载已正常载入
(function verifyRenderShards() {
    const requiredWindowApis = [
        'getPinnedPlugins',
        'togglePinPlugin',
        'filterPluginsBySearch',
        'exportConfigBackup',
        'importConfigBackup',
        'loadPlugins',
        'isPluginConfigurable',
        'checkPluginConfiguredStatus',
        'renderPlugins',
        'buildPluginPodHtml',
        'fastTestPluginConnectivity',
        'showPluginLogDrawer',
        'copyLogTerminalContent',
        'senseClipboardCredentials',
        'init3DHoverPhysics',
        'runCrossPluginDiagnostics',
        'autoReuseSameOriginCredential'
    ];

    const missing = requiredWindowApis.filter(api => typeof window[api] === 'undefined');
    if (missing.length > 0) {
        console.warn(`[Plenipes Render Hub] ⚠️ 警告：检测到分片未全量就绪 (缺失: ${missing.join(', ')})`);
    } else {
        console.log('[Plenipes Render Hub] ✅ 全量能力矩阵渲染分片模块已被成功挂载就绪！');
    }
})();
