/**
 * ⚙️ [V87.0] Illacme Plenipes Plugins - Platforms Facade Hub
 * 🚀 SOP-02 拆分完成门面文件
 * 职责：作为主入口聚合分片模块，代理导出 19 个 window 全局 API 与事件处理 Handlers。
 * 对应物理分片：
 *   1. platforms_shards/platforms.links.js (Portal 字典与向导)
 *   2. platforms_shards/platforms.hosting.js (托管与存储服务 Form)
 *   3. platforms_shards/platforms.publishers.js (社交媒体与出版渠道 Form)
 *   4. platforms_shards/platforms.image_hosting.js (图床与对象存储 Form)
 *   5. platforms_shards/platforms.oauth_handlers.js (CLI 授权与凭据感应 Handlers)
 */

// 校验并确认所有分片挂载已正常载入
(function verifyPlatformsShards() {
    const requiredWindowApis = [
        'PLATFORM_PORTAL_LINKS',
        'renderPlatformPortalGuide',
        'renderPlatformAdvancedGroup',
        'rawRenderPlatformConfig',
        'renderPlatformConfig',
        'rawRenderPublisherConfig',
        'rawRenderImageHostingConfig',
        'renderImageHostingConfig',
        'triggerGithubSSHCheck',
        'triggerFirebaseOAuthLogin',
        'triggerCloudflareOAuthLogin',
        'triggerNetlifyOAuthLogin',
        'triggerVercelOAuthLogin',
        'applyCloudflareProjectSelection',
        'triggerAWSCredentialsSense',
        'triggerSFTPSensing',
        'triggerGitCredentialsSense',
        'applyProxyPreset',
        'renderProxyPresetsHtml',
        'focusErrorField'
    ];

    const missing = requiredWindowApis.filter(api => typeof window[api] === 'undefined');
    if (missing.length > 0) {
        console.warn(`[Plenipes Platforms Hub] ⚠️ 警告：检测到分片未全量就绪 (缺失: ${missing.join(', ')})`);
    } else {
        console.log('[Plenipes Platforms Hub] ✅ 全量平台分片模块已被成功挂载就绪！');
    }
})();
