/**
 * 🛰️ [V105.0] Illacme Plenipes Plugin Editor - Step Wizard Definitions & Header Shard
 * 职责：复杂平台分类感知 3 步引导配置向导步骤名称映射提取器与 Header 卡片渲染。
 */

(function () {
    // 🚀 [V105.0] 复杂平台分类感知 3 步引导配置向导步骤名称映射提取器
    window.getPluginWizardSteps = (pluginId, category = '') => {
        const specificStepsMap = {
            'email': ['1. SMTP 主机与端口', '2. 账号与发信授权码', '3. 发信测试与保存'],
            'sms': ['1. 服务商与签名配置', '2. 密钥凭据与模板 ID', '3. 握手测试与保存'],
            'app_push': ['1. 推送平台与设备 Key', '2. 提示音效与消息分组', '3. 极速推送与保存'],
            'generic_webhook': ['1. 物理 Webhook 地址', '2. 签名防伪 Secret', '3. 连通测试与保存'],
            'devto': ['1. 个人 API Key 凭据', '2. 默认发布偏好模式', '3. 连通测试与保存'],
            'dev_to': ['1. 个人 API Key 凭据', '2. 默认发布偏好模式', '3. 连通测试与保存'],
            'wordpress': ['1. API 端点与应用密码', '2. 默认文章发布状态', '3. 连通测试与保存'],
            'medium': ['1. Integration Token 凭据', '2. 默认状态与发布偏好', '3. 连通测试与保存'],
            'hashnode': ['1. GraphQL API Token 凭据', '2. Publication 专栏绑定', '3. 连通测试与保存'],
            'ghost': ['1. Admin API Key & URL', '2. 模板与装帧偏好设置', '3. 连通测试与保存'],
            'wechat': ['1. 公众号 AppID/Secret 凭据', '2. 独立代理与图文设置', '3. 连通测试与保存'],
            'zhihu': ['1. 个人 Token / 专栏 ID', '2. 独立代理与发布偏好', '3. 连通测试与保存'],
            'telegram': ['1. Bot Token 机器人凭据', '2. 目标 Chat ID 频道参数', '3. 连通测试与保存'],
            'discord': ['1. Webhook 授权回调地址', '2. 广播与独立代理参数', '3. 连通测试与保存'],
            'github_pages': ['1. 鉴权身份凭据', '2. 目标仓库与分支', '3. 高级参数 (可选)'],
            'gitee_pages': ['1. 鉴权身份凭据', '2. 目标仓库与分支', '3. 高级参数 (可选)'],
            'gitlab_pages': ['1. 鉴权身份凭据', '2. 目标仓库与分支', '3. 高级参数 (可选)'],
            'sftp': ['1. 服务器主机与登录凭据', '2. 远程部署目录与域名', '3. 连通测试与保存'],
            'vercel': ['1. Vercel Access Token 凭据', '2. 项目名称与组织 ID 参数', '3. 生产部署与代理参数'],
            'netlify': ['1. Netlify Access Token 凭据', '2. Site ID 与部署分支参数', '3. 生产部署与代理参数'],
            'cloudflare_pages': ['1. Cloudflare API Token 凭据', '2. 项目名称与账号 ID 参数', '3. 部署分支与代理参数'],
            'firebase': ['1. Firebase CI Token 凭据', '2. 项目 ID 与 Site ID 参数', '3. 代理与部署测试'],
            'railway': ['1. Deploy Hook 触发地址', '2. 关联 Git 部署拓展参数', '3. 触发测试与保存'],
            'render': ['1. Deploy Hook 触发地址', '2. API Key 与代理拓展参数', '3. 触发测试与保存'],
            'zeabur': ['1. Deploy Hook 触发地址', '2. API Token 与代理拓展参数', '3. 触发测试与保存'],
            's3': ['1. AccessKey 身份凭据', '2. Bucket 存储桶与访问域名', '3. Endpoint 与 ACL 扩展参数'],
            'qiniu': ['1. 七牛云 AK/SK 密钥凭据', '2. 存储空间 Bucket 与访问域名', '3. 连通测试与保存'],
            'upyun': ['1. 操作员账号与授权密码', '2. 服务名称 Bucket 与访问域名', '3. 连通测试与保存']
        };

        const cat = (category || '').toLowerCase();
        const pid = (pluginId || '').toLowerCase();

        let steps = specificStepsMap[pid];
        if (!steps) {
            if (cat === 'hosting') {
                steps = ['1. 平台 API Token 凭据', '2. 仓库与域名扩展参数', '3. 测试连通与保存'];
            } else if (cat === 'image_hosting') {
                steps = ['1. 存储 Key/密钥凭据', '2. 存储桶 Bucket 与访问域名', '3. 测试连通与保存'];
            } else if (cat === 'notification') {
                steps = ['1. 消息端点/授权凭据', '2. 提醒与样式偏好参数', '3. 测试连通与保存'];
            } else if (cat === 'publisher') {
                steps = ['1. 访问 Token/密钥凭据', '2. 默认发布偏好参数', '3. 测试连通与保存'];
            } else if (cat === 'protocol' || pid.includes('ai') || pid.includes('llm')) {
                steps = ['1. API Key 与服务端点', '2. 采样与提示词策略', '3. 校验模型与保存'];
            } else if (cat === 'ssg' || cat === 'theme') {
                steps = ['1. 基础全局设置', '2. 视觉样式与装帧配置', '3. 预览生成与保存'];
            } else {
                steps = ['1. 账号与授权凭据', '2. 选项与存储参数', '3. 测试连通与保存'];
            }
        }
        return steps;
    };

    // 🚀 [V105.0] 复杂平台分类感知 3 步引导配置向导 Header Component
    window.renderPluginStepWizardHeader = (pluginId, category = '') => {
        const steps = window.getPluginWizardSteps(pluginId, category);

        return `
            <div class="plugin-wizard-header" style="margin-bottom: 16px; padding: 12px 14px; background: rgba(0, 242, 255, 0.04); border: 1px solid rgba(0, 242, 255, 0.25); border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 0.82rem; font-weight: 700; color: var(--neon-cyan);">🧙 3 步极简向导 (Step Wizard)</span>
                    <span style="font-size: 0.68rem; color: var(--neon-cyan); opacity: 0.8; font-weight: 600;">👉 点击步骤节点直达表单位置</span>
                </div>
                <div class="wizard-steps-container" style="display: flex; gap: 6px; font-size: 0.72rem; margin-bottom: 8px;">
                    <div class="wiz-step active" data-step="0" onclick="window.handleWizardStepClick(0, '${pluginId}', '${category}', this)" style="flex: 1; padding: 6px; border-radius: 6px; background: rgba(0, 242, 255, 0.18); color: var(--neon-cyan); text-align: center; font-weight: 700; border: 1px solid var(--neon-cyan); cursor: pointer; transition: all 0.2s;">${steps[0]}</div>
                    <div class="wiz-step" data-step="1" onclick="window.handleWizardStepClick(1, '${pluginId}', '${category}', this)" style="flex: 1; padding: 6px; border-radius: 6px; background: rgba(255, 255, 255, 0.04); color: var(--text-dim); text-align: center; font-weight: 500; border: 1px solid rgba(255, 255, 255, 0.1); cursor: pointer; transition: all 0.2s;">${steps[1]}</div>
                    <div class="wiz-step" data-step="2" onclick="window.handleWizardStepClick(2, '${pluginId}', '${category}', this)" style="flex: 1; padding: 6px; border-radius: 6px; background: rgba(255, 255, 255, 0.04); color: var(--text-dim); text-align: center; font-weight: 500; border: 1px solid rgba(255, 255, 255, 0.1); cursor: pointer; transition: all 0.2s;">${steps[2]}</div>
                </div>
                <div id="wiz-mission-banner" style="font-size: 0.75rem; color: #00ff88; background: rgba(0, 255, 136, 0.06); border: 1px dashed rgba(0, 255, 136, 0.3); padding: 6px 10px; border-radius: 6px; font-weight: 600; display: flex; align-items: center; gap: 6px;">
                    <span>🎯 当前步骤 [1/3]：请在下方填写凭据 Token/Key 或使用一键复用</span>
                </div>
            </div>
        `;
    };
})();
