/**
 * 🛰️ [V108.0] Illacme Plenipes Plugin Editor - Step Wizard Definitions & Header Shard
 * 职责：复杂平台分类感知 2~4 步认知向导步骤名称映射提取器与自适应 Header 卡片渲染。
 * 遵循「我是谁 (Step 1) → 去哪里 (Step 2) → 怎么做 (Step 3 可选) → 连通测试与保存 (终闭环)」标准架构。
 */

(function () {
    // 🚀 [V108.0] 复杂平台分类感知自适应向导步骤名称映射提取器
    window.getPluginWizardSteps = (pluginId, category = '') => {
        const cat = (category || '').toLowerCase();
        const pid = (pluginId || '').toLowerCase();

        // 1. 图床存储专属映射 (Image Hosting)
        if (cat === 'image_hosting') {
            const imageHostingMap = {
                's3': ['1. AccessKey 身份凭据', '2. 存储桶与区域域名', '3. 路径前缀与 ACL (可选)', '4. 上传测试与保存'],
                'aliyun_oss': ['1. AccessKey 身份凭据', '2. 存储空间与接入点', '3. 存储路径与加速 (可选)', '4. 上传测试与保存'],
                'tencent_cos': ['1. 密钥 ID 与 SecretKey', '2. 存储桶与所属地域', '3. 存储路径与加速 (可选)', '4. 上传测试与保存'],
                'upyun_uss': ['1. 操作员账号与授权密码', '2. 服务名称与外链域名', '3. 存储路径前缀 (可选)', '4. 上传测试与保存'],
                'qiniu': ['1. 七牛云 AK/SK 凭据', '2. 存储空间与访问域名', '3. 路径前缀 (可选)', '4. 上传测试与保存'],
                'qiniu_kodo': ['1. 七牛云 AK/SK 凭据', '2. 存储空间与访问域名', '3. 路径前缀 (可选)', '4. 上传测试与保存'],
                'github': ['1. 访问令牌凭据', '2. 仓库与 CDN 加速域名', '3. 存储路径 (可选)', '4. 上传测试与保存'],
                'sm_ms': ['1. SM.MS 访问密钥 (Token)', '2. 独立代理参数 (可选)', '3. 上传测试与保存'],
                'imgur': ['1. Client ID 与授权凭据', '2. 独立代理参数 (可选)', '3. 上传测试与保存'],
                'telegraph': ['1. API 端点设置', '2. 独立代理参数 (可选)', '3. 上传测试与保存'],
                'loli_io': ['1. API Token 凭据', '2. 接口端点与代理 (可选)', '3. 上传测试与保存'],
                'superbed': ['1. API Token 凭据', '2. 接口端点与代理 (可选)', '3. 上传测试与保存'],
                'lsky_pro': ['1. 鉴权 Token 凭据', '2. 实例接口端点 (Endpoint)', '3. 相册与策略 (可选)', '4. 上传测试与保存']
            };
            if (imageHostingMap[pid]) return imageHostingMap[pid];
            return ['1. 存储 Key/密钥凭据', '2. 存储空间与访问域名', '3. 高级调参 (可选)', '4. 上传测试与保存'];
        }

        // 2. 社媒分发专属映射 (Publisher)
        if (cat === 'publisher') {
            const publisherMap = {
                // 4 步模式：凭据 -> 目标/偏好 -> 代理 -> 测试保存
                'wordpress': ['1. API 端点与管理员认证', '2. 文章默认发布状态', '3. 独立代理参数 (可选)', '4. 连通测试与保存'],
                'zhihu': ['1. 个人 Token 凭据', '2. 专栏 ID (Column ID)', '3. 独立代理参数 (可选)', '4. 连通测试与保存'],
                'devto': ['1. 个人 API Key 凭据', '2. 默认发布偏好 (草稿/公开)', '3. 独立代理参数 (可选)', '4. 连通测试与保存'],
                'dev_to': ['1. 个人 API Key 凭据', '2. 默认发布偏好 (草稿/公开)', '3. 独立代理参数 (可选)', '4. 连通测试与保存'],
                'csdn': ['1. Token 或 Cookie 凭据', '2. 默认存为草稿偏好', '3. 独立代理参数 (可选)', '4. 连通测试与保存'],
                'cnblogs': ['1. Bearer Token 凭据', '2. 博客标识 (Blog App)', '3. 独立代理参数 (可选)', '4. 连通测试与保存'],
                'toutiao': ['1. Access Token 或 Cookie 凭据', '2. 默认存为草稿偏好', '3. 独立代理参数 (可选)', '4. 连通测试与保存'],
                'segmentfault': ['1. Token 或 Cookie 凭据', '2. 默认存为草稿偏好', '3. 独立代理参数 (可选)', '4. 连通测试与保存'],
                'oschina': ['1. OpenAPI Access Token 凭据', '2. 默认存为草稿偏好', '3. 独立代理参数 (可选)', '4. 连通测试与保存'],
                'linkedin': ['1. OAuth2 Access Token 凭据', '2. 作者指纹 URN', '3. 独立代理参数 (可选)', '4. 连通测试与保存'],
                'telegram': ['1. Bot Token 机器人凭据', '2. 目标 Chat ID 频道参数', '3. 独立代理参数 (可选)', '4. 连通测试与保存'],

                // 3 步模式：全套凭据 -> 代理 -> 测试保存
                'substack': ['1. 主页 URL 与 Cookie/API Key', '2. 独立代理参数 (可选)', '3. 连通测试与保存'],
                'medium': ['1. Integration Token 凭据', '2. 独立代理参数 (可选)', '3. 连通测试与保存'],
                'ghost': ['1. 站点 URL 与 Admin API Key', '2. 独立代理参数 (可选)', '3. 连通测试与保存'],
                'hashnode': ['1. GraphQL API Token 凭据', '2. 独立代理参数 (可选)', '3. 连通测试与保存'],
                'wechat': ['1. 公众号 AppID/Secret 凭据', '2. 独立代理参数 (可选)', '3. 连通测试与保存'],
                'juejin': ['1. Cookie 或 API Token 凭据', '2. 独立代理参数 (可选)', '3. 连通测试与保存'],
                'bilibili': ['1. SESSDATA 与 bili_jct 凭据', '2. 独立代理参数 (可选)', '3. 连通测试与保存'],
                'xiaohongshu': ['1. Access Token 或 Cookie 凭据', '2. 独立代理参数 (可选)', '3. 连通测试与保存'],
                'red': ['1. Access Token 或 Cookie 凭据', '2. 独立代理参数 (可选)', '3. 连通测试与保存'],
                'discord': ['1. 社区频道 Webhook 地址', '2. 独立代理参数 (可选)', '3. 连通测试与保存']
            };
            if (publisherMap[pid]) return publisherMap[pid];
            return ['1. 访问 Token/密钥凭据', '2. 独立代理参数 (可选)', '3. 连通测试与保存'];
        }

        // 3. 全局通用与全站托管映射
        const specificStepsMap = {
            // === 全站托管 (Hosting) ===
            'github_pages': ['1. 鉴权身份凭据', '2. 目标仓库与分支', '3. 高级参数 (可选)', '4. 连通测试与保存'],
            'gitee_pages': ['1. 鉴权身份凭据', '2. 目标仓库与分支', '3. 高级参数 (可选)', '4. 连通测试与保存'],
            'gitlab_pages': ['1. 鉴权身份凭据', '2. 目标仓库与分支', '3. 高级参数 (可选)', '4. 连通测试与保存'],
            's3': ['1. AccessKey 身份凭据', '2. 存储桶与区域', '3. 高级调参 (可选)', '4. 连通测试与保存'],
            'cloudflare_pages': ['1. API Token 与账号 ID', '2. 项目绑定与分支', '3. 高级参数 (可选)', '4. 连通测试与保存'],
            'vercel': ['1. 访问令牌与免密授权', '2. 项目绑定与组织 ID', '3. 行为参数 (可选)', '4. 连通测试与保存'],
            'netlify': ['1. 访问令牌与免密授权', '2. 站点绑定 (Site ID)', '3. 行为参数 (可选)', '4. 连通测试与保存'],
            'firebase': ['1. Firebase CLI 凭据', '2. 项目 ID 与站点 ID', '3. 代理参数 (可选)', '4. 连通测试与保存'],
            'sftp': ['1. 服务器主机与登录认证', '2. 远程部署目录与域名', '3. 代理调参 (可选)', '4. 连通测试与保存'],
            'aliyun_oss': ['1. AccessKey 身份凭据', '2. 存储桶与接入点', '3. 静态托管与加速 (可选)', '4. 连通测试与保存'],
            'tencent_cos': ['1. 密钥 ID 与 SecretKey', '2. 存储桶与所属地域', '3. 静态托管与加速 (可选)', '4. 连通测试与保存'],
            'upyun_uss': ['1. 操作员账号与授权密码', '2. 服务名称 (Bucket)', '3. 静态托管与加速 (可选)', '4. 连通测试与保存'],
            'railway': ['1. Git 访问令牌 (可选)', '2. Deploy Hook 触发地址', '3. 独立代理参数 (可选)', '4. 连通测试与保存'],
            'render': ['1. API Key 身份凭据 (可选)', '2. Deploy Hook 触发地址', '3. 独立代理参数 (可选)', '4. 连通测试与保存'],
            'zeabur': ['1. API Token 凭据 (可选)', '2. Deploy Hook 触发地址', '3. 独立代理参数 (可选)', '4. 连通测试与保存'],

            // === 消息通知 (Notification) ===
            'email': ['1. SMTP 认证与发信身份', '2. 接收者与发件人偏好', '3. 触发事件订阅 (可选)', '4. 发信测试与保存'],
            'sms': ['1. 服务商与密钥凭据', '2. 签名模板与目标手机', '3. 告警事件策略 (可选)', '4. 握手测试与保存'],
            'app_push': ['1. 推送平台与设备凭据', '2. 提示音效与分组偏好', '3. 触发事件订阅 (可选)', '4. 极速推送测试与保存'],
            'feishu': ['1. 飞书机器人 Webhook 与密钥', '2. 生命周期事件订阅 (可选)', '3. 连通测试与保存'],
            'dingtalk': ['1. 钉钉机器人 Webhook 与加签', '2. 生命周期事件订阅 (可选)', '3. 连通测试与保存'],
            'wecom': ['1. 企业微信 Webhook 地址', '2. 生命周期事件订阅 (可选)', '3. 连通测试与保存'],
            'wework': ['1. 企业微信 Webhook 地址', '2. 生命周期事件订阅 (可选)', '3. 连通测试与保存'],
            'wechat_work': ['1. 企业微信 Webhook 地址', '2. 生命周期事件订阅 (可选)', '3. 连通测试与保存'],
            'generic_webhook': ['1. 物理 Webhook 与签名 Secret', '2. 生命周期事件订阅 (可选)', '3. 连通测试与保存'],
            'webhook_dispatch': ['1. CI/CD 触发 Hook 地址', '2. 信号验证密钥与策略 (可选)', '3. 连通测试与保存']
        };

        let steps = specificStepsMap[pid];
        if (!steps) {
            if (cat === 'hosting') {
                steps = ['1. 平台 API Token 凭据', '2. 目标仓库与项目绑定', '3. 高级参数 (可选)', '4. 连通测试与保存'];
            } else if (cat === 'notification') {
                steps = ['1. 消息端点与授权凭据', '2. 生命周期事件订阅 (可选)', '3. 连通测试与保存'];
            } else if (cat === 'protocol' || pid.includes('ai') || pid.includes('llm')) {
                steps = ['1. API Key 与服务端点', '2. 目标模型与降级策略', '3. 采样调参 (可选)', '4. 校验模型与保存'];
            } else if (cat === 'ssg' || cat === 'theme') {
                steps = ['1. 基础全局设置', '2. 视觉样式与装帧配置', '3. 编译参数 (可选)', '4. 预览生成与保存'];
            } else {
                steps = ['1. 账号与授权凭据', '2. 选项与存储参数', '3. 连通测试与保存'];
            }
        }
        return steps;
    };

    // 🚀 [V108.0] 复杂平台分类感知自适应向导 Header Component (Sticky 吸顶高档毛玻璃置顶设计)
    window.renderPluginStepWizardHeader = (pluginId, category = '') => {
        const steps = window.getPluginWizardSteps(pluginId, category);
        const totalSteps = steps.length;

        const stepsHtml = steps.map((stepTitle, idx) => {
            const isActive = idx === 0;
            return `<div class="wiz-step ${isActive ? 'active' : ''}" data-step="${idx}" onclick="window.handleWizardStepClick(${idx}, '${pluginId}', '${category}', this)" style="flex: 1; padding: 6px 4px; border-radius: 6px; text-align: center; cursor: pointer; transition: all 0.2s; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${stepTitle}">${stepTitle}</div>`;
        }).join('');

        return `
            <div class="plugin-wizard-header" style="position: sticky; top: -30px; z-index: 100; margin: -30px -30px 18px -30px; padding: 14px 24px; background: rgba(13, 17, 23, 0.96); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(0, 242, 255, 0.25); border-top: none; border-radius: 0 0 10px 10px; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.45);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 0.82rem; font-weight: 700; color: var(--neon-cyan);">🧙 ${totalSteps} 步极简向导 (Step Wizard)</span>
                    <span style="font-size: 0.68rem; color: var(--neon-cyan); opacity: 0.8; font-weight: 600;">👉 点击步骤节点直达表单位置</span>
                </div>
                <div class="wizard-steps-container" style="display: flex; gap: 6px; font-size: 0.72rem; margin-bottom: 8px; overflow-x: auto;">
                    ${stepsHtml}
                </div>
                <div id="wiz-mission-banner" style="font-size: 0.75rem; color: #00ff88; background: rgba(0, 255, 136, 0.06); border: 1px dashed rgba(0, 255, 136, 0.3); padding: 6px 10px; border-radius: 6px; font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>🎯 当前步骤 [1/${totalSteps}]：请在下方填写凭据 Token/Key 或使用一键免密/感应</span>
                </div>
            </div>
        `;
    };
})();
