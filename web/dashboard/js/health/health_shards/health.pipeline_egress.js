/**
 * 🩺 [V55.0] Illacme Plenipes Governance Diagnostics - Pipeline Egress Senses Shard
 * 职责：出版流水线阶段 5（独立站托管主备识别与凭据感知）与阶段 6（社交媒体全域分发矩阵）状态感知与胶囊回填。
 */

(function () {
    'use strict';

    window.renderPipelineEgressSenses = function (data, s) {
        if (!data || !s) return;

        // 阶段 5: 独立站托管 (优先于社媒分发)
        const pipeValHosting = document.getElementById('pipe-val-hosting');
        const pipeDotHosting = document.getElementById('pipe-dot-hosting');
        const pipeCapHosting = document.getElementById('pipe-cap-hosting');
        if (pipeValHosting) {
            const platforms = s.platforms || {};
            const egress = s.egress || {};
            const direct = s.publish_control?.direct_upload || {};

            const activeHostingPlatforms = [];
            const hostingLabels = {
                'github_pages': 'GitHub Pages',
                'gitee_pages': 'Gitee Pages',
                'cloudflare_pages': 'Cloudflare Pages',
                'netlify': 'Netlify',
                'vercel': 'Vercel',
                'render': 'Render',
                'railway': 'Railway',
                'sftp': 'SFTP / SSH',
                's3': 'AWS S3',
                'gitlab_pages': 'GitLab Pages',
                'firebase': 'Firebase Hosting',
                'zeabur': 'Zeabur'
            };

            // 1. 优先以插件中心/当前品牌的激活态 (is_in_use) 为准
            if (Array.isArray(data.plugins) && data.plugins.length > 0) {
                data.plugins.filter(p => p.category === 'hosting' && p.is_in_use === true).forEach(p => {
                    const cfg = p.cfg || direct[p.id] || platforms[p.id] || egress[p.id] || {};
                    activeHostingPlatforms.push({
                        id: p.id,
                        name: p.name || hostingLabels[p.id] || p.id,
                        cfg: cfg,
                        is_primary: Boolean(p.is_primary)
                    });
                });
            } else {
                // 2. 兜底从当前品牌的配置直读 (仅当 data.plugins 尚未就绪时)
                Object.entries(hostingLabels).forEach(([id, label]) => {
                    const dCfg = direct[id];
                    const pCfg = platforms[id];
                    const eCfg = egress[id];
                    if ((dCfg && dCfg.enabled === true) || (pCfg && pCfg.enabled === true) || (eCfg && eCfg.enabled === true)) {
                        activeHostingPlatforms.push({
                            id: id,
                            name: label,
                            cfg: dCfg || pCfg || eCfg || {},
                            is_primary: false
                        });
                    }
                });
            }

            if (activeHostingPlatforms.length > 0) {
                // 计算各平台的凭据与部署目标
                activeHostingPlatforms.forEach(p => {
                    let isReady = false;
                    let credLabel = '凭据就绪';
                    let detail = '';
                    if (window.isPluginCredentialReady) {
                        const cred = window.isPluginCredentialReady(p.id, 'hosting', p.cfg);
                        isReady = cred.ready;
                        credLabel = cred.label || (isReady ? '凭据就绪' : '待填凭据');
                    } else {
                        const hasCredentials = Boolean(p.cfg.token || p.cfg.repo || p.cfg.host || p.cfg.access_key_id || p.cfg.api_key || p.cfg.api_token);
                        isReady = hasCredentials;
                        credLabel = isReady ? '凭据就绪' : '待填凭据';
                    }

                    if (p.cfg.repo || p.cfg.repo_url) detail = `部署目标：${p.cfg.repo || p.cfg.repo_url}`;
                    else if (p.cfg.project_name) detail = `项目：${p.cfg.project_name}`;
                    else if (p.cfg.host) detail = `主机：${p.cfg.host}`;

                    p.isReady = isReady;
                    p.credLabel = credLabel;
                    p.detail = detail;
                });

                // 🏠 主备识别：优先匹配配置中的 primary_hosting_id 或插件的 is_primary
                const configuredPrimary = s.publish_control?.primary_hosting_id || direct.primary_hosting_id || '';
                let primaryIndex = activeHostingPlatforms.findIndex(p => p.id === configuredPrimary || p.is_primary === true);
                if (primaryIndex === -1) {
                    primaryIndex = 0; // 兜底默认首个激活平台为主站
                }

                const primaryPlatform = activeHostingPlatforms[primaryIndex];
                const mirrorPlatforms = activeHostingPlatforms.filter((_, idx) => idx !== primaryIndex);

                const allReady = activeHostingPlatforms.every(p => p.isReady);
                if (pipeDotHosting) pipeDotHosting.className = allReady ? 'pipe-dot healthy' : 'pipe-dot warning';

                if (activeHostingPlatforms.length === 1) {
                    pipeValHosting.innerText = `${primaryPlatform.name} · ${primaryPlatform.credLabel}`;
                } else {
                    if (mirrorPlatforms.length === 1) {
                        pipeValHosting.innerText = `${primaryPlatform.name} (主) · ${mirrorPlatforms[0].name} (备)`;
                    } else {
                        pipeValHosting.innerText = `${primaryPlatform.name} (主) + ${mirrorPlatforms.length} 镜像 (备)`;
                    }
                }

                if (pipeCapHosting) {
                    const readyCount = activeHostingPlatforms.filter(p => p.isReady).length;
                    if (activeHostingPlatforms.length === 1) {
                        pipeCapHosting.title = `🌐 5. 独立站托管 (Static Site Hosting)\n────────────────────────\n• 官方主站 (主)：${primaryPlatform.name}\n• 鉴权状态：${primaryPlatform.isReady ? `✅ ${primaryPlatform.credLabel}` : '⚠️ 待填凭据 (请补全 Token 或仓库配置)'}\n${primaryPlatform.detail ? `• ${primaryPlatform.detail}\n` : ''}\n💡 点击一键直达独立站全站托管与部署配置`;
                    } else {
                        const lines = [
                            `🌐 5. 独立站托管 (Static Site Hosting)`,
                            `────────────────────────`,
                            `• 已启用托管：${activeHostingPlatforms.length} 个平台 (${readyCount}/${activeHostingPlatforms.length} 凭据就绪)`,
                            `• 官方主站 (主)：${primaryPlatform.name} ${primaryPlatform.isReady ? '✅' : '⚠️'} (${primaryPlatform.credLabel})${primaryPlatform.detail ? ` [${primaryPlatform.detail}]` : ''}`,
                            `• 备用镜像 (备)：${mirrorPlatforms.map(m => `${m.name} ${m.isReady ? '✅' : '⚠️'} (${m.credLabel})${m.detail ? ` [${m.detail}]` : ''}`).join('、')}`,
                            `• 分发策略：Canonical 权威主站优先投递 + 备用镜像并行同步`,
                            ``,
                            `💡 点击一键直达独立站全站托管与部署配置`
                        ];
                        pipeCapHosting.title = lines.join('\n');
                    }
                }
            } else {
                pipeValHosting.innerText = '未开启独立站托管';
                if (pipeDotHosting) pipeDotHosting.className = 'pipe-dot offline';
                if (pipeCapHosting) {
                    pipeCapHosting.title = `🌐 5. 独立站托管 (Static Site Hosting)\n────────────────────────\n• 平台状态：暂未开启任何主站托管服务\n• 能力说明：开启后，系统在编译完成后自动将全语种独立站同步发布至云端。\n\n💡 点击一键前往插件中心开启托管平台`;
                }
            }
        }

        // 阶段 6: 社交平台同步 (独立站上线后全网广播)
        const pipeValSyndication = document.getElementById('pipe-val-syndication');
        const pipeDotSyndication = document.getElementById('pipe-dot-syndication');
        const pipeCapSyndication = document.getElementById('pipe-cap-syndication');
        if (pipeValSyndication) {
            const synd = s.syndication || {};
            const activePlatforms = [];
            const platformNames = {
                'devto': 'Dev.to',
                'hashnode': 'Hashnode',
                'medium': 'Medium',
                'x_twitter': 'X (Twitter)',
                'linkedin': 'LinkedIn',
                'zhihu': '知乎',
                'juejin': '稀土掘金',
                'ghost': 'Ghost'
            };

            // 1. 严格检查当前品牌 settingsData 中的显式启用状态
            Object.keys(platformNames).forEach(k => {
                const pCfg = synd[k];
                if (pCfg && pCfg.enabled === true) {
                    const hasToken = Boolean(pCfg.api_key || pCfg.token || pCfg.access_token);
                    activePlatforms.push({ id: k, name: platformNames[k], ready: hasToken });
                }
            });

            // 2. 联动感知 data.plugins 矩阵 (严格且仅匹配当前品牌激活状态 is_in_use === true)
            if (Array.isArray(data.plugins)) {
                data.plugins.filter(p => p.category === 'publisher' && p.is_in_use === true).forEach(p => {
                    if (!activePlatforms.some(a => a.id === p.id)) {
                        activePlatforms.push({ id: p.id, name: p.name || platformNames[p.id] || p.id, ready: p.status === 'READY' || Boolean(p.cfg?.token || p.cfg?.api_key) });
                    }
                });
            }

            if (activePlatforms.length > 0) {
                const names = activePlatforms.map(p => p.name).join(', ');
                const allReady = activePlatforms.every(p => p.ready);
                pipeValSyndication.innerText = `${names} (${activePlatforms.length} 渠道就绪)`;
                if (pipeDotSyndication) pipeDotSyndication.className = allReady ? 'pipe-dot healthy' : 'pipe-dot warning';
            } else {
                pipeValSyndication.innerText = '未开启社交分发';
                if (pipeDotSyndication) pipeDotSyndication.className = 'pipe-dot offline';
            }

            if (pipeCapSyndication) {
                if (activePlatforms.length > 0) {
                    const readyCount = activePlatforms.filter(p => p.ready).length;
                    pipeCapSyndication.title = `🚀 6. 社交平台同步 (Social Media Syndication)\n────────────────────────\n• 已启用平台：${activePlatforms.map(p => p.name).join(', ')} (共 ${activePlatforms.length} 个)\n• 凭据齐备数：${readyCount} / ${activePlatforms.length} 个渠道\n• 同步策略：Canonical 原创版权保护 + 社交平台自动化广播\n\n💡 点击一键唤起多平台社交媒体同步与广播中枢`;
                } else {
                    pipeCapSyndication.title = `🚀 6. 社交平台同步 (Social Media Syndication)\n────────────────────────\n• 渠道状态：暂未开启任何社交媒体同步渠道\n• 能力说明：开启后，单篇文稿可一键多语言分发至 Dev.to / Medium / 知乎等社交平台。\n\n💡 点击一键前往插件中心开启社交分发平台`;
                }
            }
        }
    };

})();
