/**
 * ⚙️ [V1.0] Illacme Plenipes Plugins - Domestic Publishing Platforms Shard
 * 职责：国内社交与技术社区分发平台 (小红书, 今日头条, CSDN, 博客园, Bilibili, SegmentFault, 开源中国) 的配置表单渲染。
 */

(function () {
    'use strict';

    var renderSettingsItem = window.renderSettingsItem || (() => "");

    window.renderDomesticPublisherConfig = function (id, cfg) {
        if (id === 'xiaohongshu' || id === 'red') {
            return `
                <div class="api-token-helper">
                    <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                        <span>💡 小红书创作者服务平台直达</span>
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 2px;">
                        <a href="https://creator.xiaohongshu.com" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达小红书创作者平台</a>
                    </div>
                </div>
                ${renderSettingsItem('访问令牌 (Access Token)', `syndication.xiaohongshu.token`, cfg.token, 'password', { placeholder: "请输入小红书创作者服务 Access Token (二选一)", optional: true })}
                ${renderSettingsItem('登录 Cookie (Cookie)', `syndication.xiaohongshu.cookie`, cfg.cookie, 'textarea', { placeholder: "请输入小红书网页端登录 Cookie (二选一)", rows: 2, optional: true })}
                ${window.renderPlatformAdvancedGroup('高级代理参数', `
                    ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.xiaohongshu.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                `)}
            `;
        } else if (id === 'toutiao') {
            return `
                <div class="api-token-helper">
                    <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                        <span>💡 今日头条创作者平台直达</span>
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 2px;">
                        <a href="https://mp.toutiao.com/profile_v4/graphic/publish" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达头条号发布管理中心</a>
                    </div>
                </div>
                ${renderSettingsItem('头条号访问令牌 (Access Token)', `syndication.toutiao.access_token`, cfg.access_token || cfg.token, 'password', { placeholder: "请输入头条号开放平台 Access Token (二选一)", optional: true })}
                ${renderSettingsItem('登录 Cookie (Cookie)', `syndication.toutiao.cookie`, cfg.cookie, 'textarea', { placeholder: "请输入今日头条创作者中心登录 Cookie (二选一)", rows: 2, optional: true })}
                ${renderSettingsItem('默认存为草稿', `syndication.toutiao.save_as_draft`, cfg.save_as_draft !== false, 'checkbox', { description: "勾选表示同步后暂存为头条号草稿箱；取消勾选表示直接公开分发。" })}
                ${window.renderPlatformAdvancedGroup('高级代理参数', `
                    ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.toutiao.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                `)}
            `;
        } else if (id === 'csdn') {
            return `
                <div class="api-token-helper">
                    <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                        <span>💡 CSDN 创作中心直达</span>
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 2px;">
                        <a href="https://mp.csdn.net" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达 CSDN 创作者中心</a>
                    </div>
                </div>
                ${renderSettingsItem('用户 Token (X-CSDN-Token)', `syndication.csdn.token`, cfg.token, 'password', { placeholder: "请输入 CSDN 访问令牌 (二选一)", description: "CSDN 开放平台或创作者接口专属 Token（与下方 Cookie 二选一）。", optional: true })}
                ${renderSettingsItem('登录 Cookie (Cookie)', `syndication.csdn.cookie`, cfg.cookie, 'textarea', { placeholder: "请输入 CSDN 登录 Cookie 凭据 (二选一)", rows: 2, description: "网页登录 CSDN 后包含 UserName 与 UserToken 的 Cookie 字符串凭证。", optional: true })}
                ${renderSettingsItem('默认存为草稿', `syndication.csdn.save_as_draft`, cfg.save_as_draft !== false, 'checkbox', { description: "勾选表示保存至 CSDN 草稿箱；取消勾选表示直接公开发布。" })}
                ${window.renderPlatformAdvancedGroup('高级代理参数', `
                    ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.csdn.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                `)}
            `;
        } else if (id === 'cnblogs') {
            return `
                <div class="api-token-helper">
                    <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                        <span>💡 博客园 API 令牌获取向导</span>
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 2px;">
                        <a href="https://i.cnblogs.com/settings" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达博客园设置页</a>
                    </div>
                </div>
                ${renderSettingsItem('访问令牌 (Bearer Token)', `syndication.cnblogs.token`, cfg.token || cfg.bearer_token, 'password', { placeholder: "请输入博客园 Personal Access Token", description: "登录博客园个人后台 -> 设置 -> 申请 Personal Access Token 并粘贴至此。" })}
                ${renderSettingsItem('博客标识 (Blog App)', `syndication.cnblogs.blog_app`, cfg.blog_app, 'text', { placeholder: "例如: your-blog-name (博客园后缀标识)", description: "您的博客园个人主页后缀标识（例如 cnblogs.com/xxx 中的 xxx）。" })}
                ${renderSettingsItem('默认存为草稿', `syndication.cnblogs.save_as_draft`, cfg.save_as_draft !== false, 'checkbox', { description: "勾选表示保存为未发布的草稿文章。" })}
                ${window.renderPlatformAdvancedGroup('高级代理参数', `
                    ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.cnblogs.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                `)}
            `;
        } else if (id === 'bilibili') {
            return `
                <div class="api-token-helper">
                    <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                        <span>💡 Bilibili 专栏与免密嗅探说明</span>
                    </div>
                    <div style="font-size: 0.8rem; color: var(--text-muted, #94a3b8); margin-top: 4px; line-height: 1.45;">
                        若本地 Chrome 已登录 B 站，点击下方免密嗅探可全自动提取 SESSDATA 与 bili_jct 并完成身份绑定！
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 6px; flex-wrap: wrap;">
                        <button type="button" class="helper-btn" onclick="window.autoSniffLocalCookie('bilibili', this)" style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); color: #10B981; font-weight: 600;">🔑 本地 Chrome 免密嗅探并填入</button>
                        <a href="https://member.bilibili.com/platform/article-up" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达 B 站专栏投稿页面</a>
                    </div>
                </div>
                ${renderSettingsItem('SESSDATA (Cookie 核心凭据)', `syndication.bilibili.sessdata`, cfg.sessdata, 'password', { placeholder: "请输入 B 站登录凭据 SESSDATA (可通过免密嗅探自动填入)", description: "浏览器登录 bilibili.com 后 Cookie 中的 SESSDATA 身份凭据。" })}
                ${renderSettingsItem('CSRF 校验值 (bili_jct)', `syndication.bilibili.bili_jct`, cfg.bili_jct, 'password', { placeholder: "请输入 B 站 bili_jct 校验值 (可通过免密嗅探自动填入)", description: "浏览器登录 bilibili.com 后 Cookie 中的 bili_jct 防跨站请求伪造令牌。" })}
                ${window.renderPlatformAdvancedGroup('高级代理参数', `
                    ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.bilibili.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                `)}
            `;
        } else if (id === 'segmentfault') {
            return `
                <div class="api-token-helper">
                    <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                        <span>💡 SegmentFault 开发者设置直达</span>
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 2px;">
                        <a href="https://segmentfault.com/user/settings" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达思否个人设置页</a>
                    </div>
                </div>
                ${renderSettingsItem('访问令牌 (API Token)', `syndication.segmentfault.token`, cfg.token, 'password', { placeholder: "请输入 SegmentFault 访问令牌 (二选一)", description: "用于调用 SegmentFault 专栏发布 API 的 Token（与下方 Cookie 二选一）。", optional: true })}
                ${renderSettingsItem('登录 Cookie (Cookie)', `syndication.segmentfault.cookie`, cfg.cookie, 'textarea', { placeholder: "请输入 SegmentFault 登录 Cookie (二选一)", rows: 2, description: "网页登录思否社区后的 Cookie 身份凭据字符串。", optional: true })}
                ${renderSettingsItem('默认存为草稿', `syndication.segmentfault.save_as_draft`, cfg.save_as_draft !== false, 'checkbox', { description: "勾选表示保存至思否草稿箱；取消勾选直接发布。" })}
                ${window.renderPlatformAdvancedGroup('高级代理参数', `
                    ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.segmentfault.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                `)}
            `;
        } else if (id === 'oschina') {
            return `
                <div class="api-token-helper">
                    <div style="font-weight: 600; display: flex; align-items: center; gap: 6px;">
                        <span>💡 开源中国 OpenAPI 授权直达</span>
                    </div>
                    <div style="display: flex; gap: 10px; margin-top: 2px;">
                        <a href="https://www.oschina.net/openapi" target="_blank" class="helper-btn" onmouseover="this.style.background='rgba(0, 242, 254, 0.3)'" onmouseout="this.style.background='rgba(0, 242, 254, 0.15)'">🔗 一键直达开源中国开放平台</a>
                    </div>
                </div>
                ${renderSettingsItem('开放平台令牌 (Access Token)', `syndication.oschina.access_token`, cfg.access_token || cfg.token, 'password', { placeholder: "请输入开源中国 OpenAPI Access Token", description: "在开源中国开放平台申请并通过 OAuth 授权获得的 Access Token。" })}
                ${renderSettingsItem('默认存为草稿', `syndication.oschina.save_as_draft`, cfg.save_as_draft !== false, 'checkbox', { description: "勾选表示暂存为草稿；取消勾选直接公开。" })}
                ${window.renderPlatformAdvancedGroup('高级代理参数', `
                    ${renderSettingsItem('独立代理地址 (Proxy)', `syndication.oschina.proxy`, cfg.proxy, 'text', { placeholder: "例如: http://127.0.0.1:10809 或 direct", description: "可选。针对当前渠道配置独立代理，填写 direct 表示强制直连。" })}
                `)}
            `;
        }
        return '';
    };

})();
