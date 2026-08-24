/**
 * 🛰️ [V105.0] Illacme Plenipes Plugin Editor - Form Cards Physical Grouping Shard
 * 职责：物理结构分组大卡片包装器 (全能力与授权向导全量无死角适配 + 严格 DOM 安全防环断言与空高级折叠块清理)。
 */

(function () {
    window.groupDrawerFormIntoStepCards = (drawerBody) => {
        if (!drawerBody || drawerBody.querySelector('.wiz-step-card')) return;

        const pluginId = drawerBody.getAttribute('data-plugin-id') || '';
        const category = drawerBody.getAttribute('data-plugin-category') || '';
        const steps = window.getPluginWizardSteps ? window.getPluginWizardSteps(pluginId, category) : ['1. 鉴权身份凭据', '2. 目标仓库与分支', '3. 测试连通与保存'];
        const step0Title = steps[0].replace(/^[0-9]+\.\s*/, '');
        const step1Title = steps[1].replace(/^[0-9]+\.\s*/, '');

        // 安全断言：判断一个 div 是否是合法的向导卡片（严禁包含主容器节点，避免循环嵌套崩溃）
        const isSafeGuideCard = (div) => {
            if (!div || div.nodeType !== 1) return false;
            if (div.classList.contains('settings-grid') || div.classList.contains('wiz-cards-wrapper') || div.classList.contains('plugin-wizard-header') || div.classList.contains('hosting-role-banner')) return false;
            if (div.id === 'plugin-drawer' || div.id === 'p-drawer-body' || div.id === 'sandbox-console-wrapper') return false;
            // 如果内部包含了全局总开关或包含了主配置网格，绝对不能当作向导卡片移动
            if (div.querySelector('#drawer-global-driver-toggle, .settings-grid, .wiz-cards-wrapper')) return false;
            // 如果不是专门的 api-token-helper，且内部包含了多个 setting-row，不能当成向导卡片
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

        // 2. 收集所有配置行节点
        const rows = Array.from(drawerBody.querySelectorAll('.setting-row, .setting-item, .setting-group'));
        if (rows.length === 0 && guideCards.length === 0) return;

        const step0Rows = [];
        const step1Rows = [];

        // 🚀 将全量寻找出来的授权向导卡片，首优先注入 Step 0 列表（Step 1 卡片内部头部）
        guideCards.forEach(card => {
            if (!step0Rows.includes(card)) {
                step0Rows.push(card);
            }
        });

        rows.forEach(row => {
            // 如果是全局总开关行或已经在卡片内的元素，跳过
            if (row.querySelector('#drawer-global-driver-toggle') || row.closest('.wiz-step-card')) return;
            // 如果是向导卡片本身，避免重复添加
            if (guideCards.includes(row)) return;

            const inputs = row.querySelectorAll('input, select, textarea');
            let isStep0 = false;

            inputs.forEach(inp => {
                const path = (inp.getAttribute('data-path') || inp.name || '').toLowerCase();
                // git_user (git_user_name / git_user_email) 属于身份凭据，与 Token 同属 Step 0
                if (path.includes('token') || path.includes('access_key') || path.includes('secret_key') || path.includes('api_key') || path.includes('git_user') || inp.type === 'password') {
                    isStep0 = true;
                }
            });

            // 查找配置行内是否有带有 Token 申请 / 授权向导链接的元素
            if (row.querySelector('a[href*="token"], a[href*="api"], [class*="magic-link"], [class*="guide"]')) {
                isStep0 = true;
            }

            if (isStep0) {
                step0Rows.push(row);
            } else {
                step1Rows.push(row);
            }
        });

        if (step0Rows.length === 0 && step1Rows.length === 0) return;

        const firstRow = guideCards[0] || step0Rows[0] || step1Rows[0];
        if (!firstRow || !firstRow.parentElement) return;
        const parentContainer = firstRow.parentElement;

        // 在 firstRow 原物理位置插入一个占位 Marker，确保即使 firstRow 被移走，Marker 依然固定在 parentContainer 内
        const marker = document.createElement('span');
        marker.style.display = 'none';
        parentContainer.insertBefore(marker, firstRow);

        // 创建卡片组专属 Wrapper 容器，避免 Node.insertBefore 参照点脱离 DOM 树
        const cardsWrapper = document.createElement('div');
        cardsWrapper.className = 'wiz-cards-wrapper';

        // 1. 创建 Step 1 物理大卡片
        if (step0Rows.length > 0) {
            const card0 = document.createElement('div');
            card0.className = 'wiz-step-card wiz-card-step-0 active';
            card0.id = 'wiz-card-step-0';
            card0.style.cssText = `
                margin-bottom: 16px;
                padding: 14px;
                background: rgba(0, 242, 255, 0.04);
                border: 1.5px solid var(--neon-cyan);
                border-radius: 10px;
                transition: all 0.3s ease;
                box-shadow: 0 0 15px rgba(0, 242, 255, 0.15);
            `;
            card0.innerHTML = `
                <div style="font-size: 0.78rem; font-weight: 700; color: var(--neon-cyan); margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
                    <span>🔑 步骤 1：${step0Title}</span>
                    <span class="card-status-tag" style="font-size: 0.65rem; padding: 2px 8px; background: rgba(0, 242, 254, 0.2); color: var(--neon-cyan); border-radius: 4px; font-weight: 600;">聚焦配置中</span>
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

        // 2. 创建 Step 2 物理大卡片
        if (step1Rows.length > 0) {
            const card1 = document.createElement('div');
            card1.className = 'wiz-step-card wiz-card-step-1';
            card1.id = 'wiz-card-step-1';
            card1.style.cssText = `
                margin-bottom: 16px;
                padding: 14px;
                background: rgba(255, 255, 255, 0.02);
                border: 1px dashed rgba(255, 255, 255, 0.15);
                border-radius: 10px;
                transition: all 0.3s ease;
            `;
            card1.innerHTML = `
                <div style="font-size: 0.78rem; font-weight: 700; color: var(--text-dim); margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
                    <span>⚙️ 步骤 2：${step1Title}</span>
                    <span class="card-status-tag" style="font-size: 0.65rem; padding: 2px 8px; background: rgba(255, 255, 255, 0.05); color: var(--text-dim); border-radius: 4px; font-weight: 600; display: none;">聚焦配置中</span>
                </div>
                <div class="card-content"></div>
            `;
            const content = card1.querySelector('.card-content');
            step1Rows.forEach(r => {
                if (r !== card1 && !r.contains(card1) && !card1.contains(r)) {
                    content.appendChild(r);
                }
            });
            cardsWrapper.appendChild(card1);
        }

        // 🚀 [V105.1] 物理清理：如果存在任何内部不含输入配置项的空高级参数折叠块，直接清理剔除以节省上下空间
        const emptyBlocks = drawerBody.querySelectorAll('.advanced-settings-block, details');
        emptyBlocks.forEach(b => {
            if (b.querySelectorAll('input, select, textarea').length === 0) {
                b.remove();
            }
        });

        // 将 cardsWrapper 完美插入在预先固定的 marker 位置，然后移除 marker
        parentContainer.insertBefore(cardsWrapper, marker);
        marker.remove();
    };
})();
