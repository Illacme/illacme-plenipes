/**
 * 🛰️ [V105.0] Illacme Plenipes Plugin Editor - Form Cards Physical Grouping Shard
 * 职责：物理结构分组大卡片包装器 (全能力与授权向导全量无死角适配 + 严格 DOM 安全防环断言与空高级折叠块清理)。
 */

(function () {
    window.groupDrawerFormIntoStepCards = (drawerBody) => {
        if (!drawerBody || drawerBody.querySelector('.wiz-step-card')) return;

        const pluginId = (drawerBody.getAttribute('data-plugin-id') || '').toLowerCase();
        const category = (drawerBody.getAttribute('data-plugin-category') || '').toLowerCase();
        const steps = window.getPluginWizardSteps ? window.getPluginWizardSteps(pluginId, category) : ['1. 鉴权身份凭据', '2. 目标仓库与分支', '3. 测试连通与保存'];
        const totalSteps = steps.length;
        const step0Title = (steps[0] || '').replace(/^[0-9]+\.\s*/, '');
        const step1Title = (steps[1] || '').replace(/^[0-9]+\.\s*/, '');
        const step2Title = (steps[2] || '').replace(/^[0-9]+\.\s*/, '');

        // 安全断言：判断一个 div 是否是合法的向导卡片（严禁包含主容器节点，避免循环嵌套崩溃）
        const isSafeGuideCard = (div) => {
            if (!div || div.nodeType !== 1) return false;
            if (div.classList.contains('settings-grid') || div.classList.contains('wiz-cards-wrapper') || div.classList.contains('plugin-wizard-header') || div.classList.contains('hosting-role-banner')) return false;
            if (div.id === 'plugin-drawer' || div.id === 'p-drawer-body' || div.id === 'sandbox-console-wrapper') return false;
            if (div.querySelector('#drawer-global-driver-toggle, .settings-grid, .wiz-cards-wrapper')) return false;
            if (!div.classList.contains('api-token-helper') && !div.classList.contains('cross-plugin-reuse-guide') && div.querySelectorAll('.setting-row, .setting-item').length > 0) return false;
            return true;
        };

        // 1. 搜集所有合法的授权向导卡片
        const guideCards = [];
        const helperCards = Array.from(drawerBody.querySelectorAll('.api-token-helper, .cross-plugin-reuse-guide, .clip-sense-card, .reuse-helper-card, [class*="api-token"]'));

        helperCards.forEach(div => {
            if (isSafeGuideCard(div) && !div.closest('.wiz-step-card') && !guideCards.includes(div)) {
                guideCards.push(div);
            }
        });

        // 2. 搜集高级参数折叠块与事件订阅中枢卡片
        const advBlocks = Array.from(drawerBody.querySelectorAll('.advanced-settings-block, details.plugin-advanced-group, details')).filter(b => !b.closest('.wiz-step-card'));
        const lifecycleCards = Array.from(drawerBody.querySelectorAll('.lifecycle-subscription-card')).filter(c => !c.closest('.wiz-step-card'));

        // 3. 收集所有配置行节点（严禁收集已在高级参数块内部的子行，保持高级参数块结构完整）
        const rows = Array.from(drawerBody.querySelectorAll('.setting-row, .setting-item, .setting-group')).filter(row => {
            if (row.querySelector('#drawer-global-driver-toggle') || row.closest('.wiz-step-card')) return false;
            if (guideCards.includes(row)) return false;
            if (row.closest('.advanced-settings-block, details.plugin-advanced-group, details, .lifecycle-subscription-card')) return false;
            return true;
        });

        if (rows.length === 0 && guideCards.length === 0 && advBlocks.length === 0 && lifecycleCards.length === 0) return;

        const step0Rows = [];
        const step1Rows = [];
        const step2Rows = [];

        // 🚀 将全量寻找出来的授权向导卡片，首优先注入 Step 0 列表（Step 1 卡片内部头部）
        guideCards.forEach(card => {
            if (!step0Rows.includes(card)) {
                step0Rows.push(card);
            }
        });

        rows.forEach(row => {
            const inputs = row.querySelectorAll('input, select, textarea');
            let isStep0 = false;

            // 🚀 [V108.0] 全景身份凭据判定：Token, AK/SK, 账号, 操作员, Client ID, 密码, SSH 私钥, Git 凭据, 主机端点等
            inputs.forEach(inp => {
                const path = (inp.getAttribute('data-path') || inp.name || '').toLowerCase();
                const isCredentialField = (
                    path.includes('token') ||
                    path.includes('access_key') ||
                    path.includes('secret_key') ||
                    path.includes('api_key') ||
                    path.includes('git_user') ||
                    path.includes('username') ||
                    path.includes('operator') ||
                    path.includes('account_id') ||
                    path.includes('smtp_user') ||
                    path.includes('smtp_pass') ||
                    path.includes('smtp_host') ||
                    path.includes('smtp_port') ||
                    path.includes('use_ssl') ||
                    path.includes('app_id') ||
                    path.includes('app_secret') ||
                    path.includes('secret_id') ||
                    path.includes('client_id') ||
                    path.includes('sessdata') ||
                    path.includes('bili_jct') ||
                    path.includes('device_key') ||
                    path.includes('sendkey') ||
                    path.includes('auth_token') ||
                    path.includes('private_key') ||
                    path.includes('passphrase') ||
                    path.includes('cookie') ||
                    path.includes('application_password') ||
                    path.includes('base_url') ||
                    // 平台特定连接端点（作为鉴权连接第一步的核心）：
                    path.includes('substack.url') ||
                    path.includes('ghost.url') ||
                    path.includes('wordpress.api_url') ||
                    path.includes('telegraph.endpoint') ||
                    path.includes('webhook_endpoints.') && path.includes('.url') ||
                    path.includes('webhook_endpoints.') && path.includes('.secret') ||
                    inp.type === 'password'
                );
                if (isCredentialField) {
                    isStep0 = true;
                }
            });

            // 查找配置行内是否有带有 Token 申请 / 授权向导链接 / 凭据帮助的元素
            if (row.querySelector('a[href*="token"], a[href*="api"], a[href*="key"], [class*="magic-link"], [class*="guide"], [class*="helper"]')) {
                isStep0 = true;
            }

            if (isStep0) {
                step0Rows.push(row);
            } else {
                step1Rows.push(row);
            }
        });

        // 4. 分配高级参数块与事件订阅卡片
        if (totalSteps === 4) {
            // 4 步流程：Step 3 (Step 2 卡片) 收集高级参数折叠块与事件订阅卡片
            advBlocks.forEach(b => {
                b.open = true; // 在卡片内展开展示
                step2Rows.push(b);
            });
            lifecycleCards.forEach(c => step2Rows.push(c));
        } else if (totalSteps === 3) {
            // 3 步流程：Step 2 (Step 1 卡片) 收集事件订阅卡片或高级代理参数
            if (lifecycleCards.length > 0) {
                lifecycleCards.forEach(c => step1Rows.push(c));
            }
            if (advBlocks.length > 0) {
                advBlocks.forEach(b => {
                    b.open = true; // 在卡片内展开展示
                    step1Rows.push(b);
                });
            }
        }

        const firstRow = guideCards[0] || step0Rows[0] || step1Rows[0] || step2Rows[0];
        if (!firstRow || !firstRow.parentElement) return;
        const parentContainer = firstRow.parentElement;

        // 在 firstRow 原物理位置插入一个占位 Marker
        const marker = document.createElement('span');
        marker.style.display = 'none';
        parentContainer.insertBefore(marker, firstRow);

        // 创建卡片组专属 Wrapper 容器
        const cardsWrapper = document.createElement('div');
        cardsWrapper.className = 'wiz-cards-wrapper';

        // 1. 创建 Step 1 物理大卡片 (#wiz-card-step-0)
        if (step0Rows.length > 0) {
            const card0 = document.createElement('div');
            card0.className = 'wiz-step-card wiz-card-step-0 active';
            card0.id = 'wiz-card-step-0';
            card0.style.cssText = `margin-bottom: 16px; padding: 14px; border-radius: 10px; transition: all 0.3s ease;`;
            card0.innerHTML = `
                <div style="font-size: 0.78rem; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
                    <span class="step-title-text">🔑 步骤 1：${step0Title}</span>
                    <span class="card-status-tag" style="font-size: 0.65rem; padding: 2px 8px; border-radius: 4px; font-weight: 600;">聚焦配置中</span>
                </div>
                <div class="card-content"></div>
            `;
            const content = card0.querySelector('.card-content');
            step0Rows.forEach(r => {
                if (r !== card0 && !r.contains(card0) && !card0.contains(r)) {
                    content.appendChild(r);
                }
            });
            cardsWrapper.appendChild(card0);
        }

        // 2. 创建 Step 2 物理大卡片 (#wiz-card-step-1)
        if (step1Rows.length > 0) {
            const card1 = document.createElement('div');
            card1.className = 'wiz-step-card wiz-card-step-1';
            card1.id = 'wiz-card-step-1';
            card1.style.cssText = `margin-bottom: 16px; padding: 14px; border-radius: 10px; transition: all 0.3s ease;`;
            const icon = totalSteps === 3 && lifecycleCards.length > 0 ? '🔔' : '🌐';
            card1.innerHTML = `
                <div style="font-size: 0.78rem; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
                    <span class="step-title-text">${icon} 步骤 2：${step1Title}</span>
                    <span class="card-status-tag" style="font-size: 0.65rem; padding: 2px 8px; border-radius: 4px; font-weight: 600; display: none;">聚焦配置中</span>
                </div>
                <div class="card-content" style="display: flex; flex-direction: column; gap: 12px;"></div>
            `;
            const content = card1.querySelector('.card-content');
            step1Rows.forEach(r => {
                if (r !== card1 && !r.contains(card1) && !card1.contains(r)) {
                    content.appendChild(r);
                }
            });
            cardsWrapper.appendChild(card1);
        }

        // 3. 创建 Step 3 物理大卡片 (#wiz-card-step-2)（当存在第 3 步且有高级参数或事件订阅时）
        if (totalSteps === 4 && step2Rows.length > 0) {
            const card2 = document.createElement('div');
            card2.className = 'wiz-step-card wiz-card-step-2';
            card2.id = 'wiz-card-step-2';
            card2.style.cssText = `margin-bottom: 16px; padding: 14px; border-radius: 10px; transition: all 0.3s ease;`;
            const icon = lifecycleCards.length > 0 ? '🔔' : '⚙️';
            card2.innerHTML = `
                <div style="font-size: 0.78rem; font-weight: 700; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
                    <span class="step-title-text">${icon} 步骤 3：${step2Title}</span>
                    <span class="card-status-tag" style="font-size: 0.65rem; padding: 2px 8px; border-radius: 4px; font-weight: 600; display: none;">聚焦配置中</span>
                </div>
                <div class="card-content" style="display: flex; flex-direction: column; gap: 12px;"></div>
            `;
            const content = card2.querySelector('.card-content');
            step2Rows.forEach(r => {
                if (r !== card2 && !r.contains(card2) && !card2.contains(r)) {
                    content.appendChild(r);
                }
            });
            cardsWrapper.appendChild(card2);
        }

        // 将 cardsWrapper 完美插入在预先固定的 marker 位置，然后移除 marker
        parentContainer.insertBefore(cardsWrapper, marker);
        marker.remove();
    };
})();
