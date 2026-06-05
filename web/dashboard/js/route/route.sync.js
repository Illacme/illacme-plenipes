/**
 * 🛣️ [V75.0] Advanced Channel Routing - Sync & Action Module
 * 职责：处理路由矩阵的前端交互表单与后端接口同步。
 */

window.addRouteMatrixRow = () => {
    const isLicensed = window.settingsData._is_licensed || false;
    if (!isLicensed) return;

    const themeSlots = window.settingsData._theme_slots || {};
    const hasSlots = Object.keys(themeSlots).length > 0;

    const tbody = document.getElementById('route-matrix-body');
    const emptyState = tbody.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    const newIdx = tbody.querySelectorAll('.route-item').length;
    
    const rowHtml = `
        <div class="matrix-row route-item" data-idx="${newIdx}" style="display: grid; grid-template-columns: 1.5fr 1.5fr 1.5fr 1fr 60px; gap: 15px; padding: 12px 10px; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.03); transition: background 0.2s;">
            <div>
                ${(() => {
                    const directories = window.settingsData._directories || [];
                    const hasDirs = directories.length > 0;
                    let html = '';
                    if (hasDirs) {
                        html += `<select class="setting-input source-select" style="width: 100%;" onchange="if(this.value === '_custom') { this.style.display='none'; this.nextElementSibling.style.display='block'; this.nextElementSibling.value=''; this.nextElementSibling.focus(); } else { this.nextElementSibling.value=this.value; }">`;
                        html += `<option value="" selected>-- 选择文库目录 --</option>`;
                        directories.forEach(d => {
                            if(d) html += `<option value="${d}">📁 ${d}</option>`;
                        });
                        html += `<option value="_custom">✏️ 自定义输入...</option>`;
                        html += `</select>`;
                    }
                    html += `<input type="text" class="setting-input source-input" value="" placeholder="例如: journal" style="width: 100%; display: ${!hasDirs ? 'block' : 'none'};">`;
                    return html;
                })()}
            </div>
            <div>
                <input type="text" class="setting-input prefix-input" value="" placeholder="例如: /blog/" style="width: 100%; color: var(--accent-secondary); font-family: monospace;">
            </div>
            <div>
                ${(() => {
                    let html = '';
                    if (hasSlots) {
                        html += `<select class="setting-input slot-select" style="width: 100%;" onchange="if(this.value === '_custom') { this.style.display='none'; this.nextElementSibling.style.display='block'; this.nextElementSibling.value=''; this.nextElementSibling.focus(); } else { this.nextElementSibling.value=this.value; }">`;
                        html += `<option value="" selected>-- 选择网页模板 --</option>`;
                        Object.entries(themeSlots).forEach(([k, v]) => {
                            html += `<option value="${k}">${v.label || k}</option>`;
                        });
                        html += `<option value="_custom">✏️ 自定义输入...</option>`;
                        html += `</select>`;
                    }
                    html += `<input type="text" class="setting-input slot-input" value="" placeholder="例如: custom_template" style="width: 100%; display: ${!hasSlots ? 'block' : 'none'};">`;
                    return html;
                })()}
            </div>
            <div>
                <select class="setting-input style-input" style="width: 100%;">
                    <option value="">继承全局默认</option>
                    <option value="professional">💼 商务严谨</option>
                    <option value="casual">☕ 随性自然</option>
                    <option value="literal">⚖️ 精准直译</option>
                </select>
            </div>
            <div style="text-align: center;">
                <button class="mini-btn" onclick="removeRouteMatrixRow(this)" style="background: rgba(255,50,50,0.1); border: 1px solid rgba(255,50,50,0.3); color: #ff5555; height: 32px; width: 32px; padding: 0; border-radius: 6px; cursor: pointer; transition: all 0.2s;" title="删除此规则">×</button>
            </div>
        </div>
    `;
    
    tbody.insertAdjacentHTML('beforeend', rowHtml);
    
    // Smooth scroll to bottom
    const container = document.querySelector('.view-panel.active .tab-content-area');
    if (container) {
        container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
    }
};

window.removeRouteMatrixRow = (btn) => {
    const isLicensed = window.settingsData._is_licensed || false;
    if (!isLicensed) return;
    
    const row = btn.closest('.route-item');
    if (row) {
        row.style.opacity = '0';
        row.style.transform = 'translateY(-10px)';
        setTimeout(() => {
            row.remove();
            
            const tbody = document.getElementById('route-matrix-body');
            if (tbody.querySelectorAll('.route-item').length === 0) {
                tbody.innerHTML = `
                    <div class="empty-state" style="padding: 40px; text-align: center; color: var(--text-dim);">
                        暂无路由策略。您的全部文件目前均按照原始物理路径进行映射发布。
                    </div>
                `;
            }
        }, 200);
    }
};

window.saveRouteMatrix = async () => {
    const isLicensed = window.settingsData._is_licensed || false;
    if (!isLicensed) return;

    if (typeof window.addAudit === 'function') {
        window.addAudit("🛣️ 正在打包聚合全新路由策略...");
    }

    const btn = document.getElementById('btn-save-route-matrix');
    if (btn) {
        btn.disabled = true;
        btn.innerText = '💾 保存中...';
    }

    const routeItems = document.querySelectorAll('.route-item');
    const newRouteMatrix = [];

    routeItems.forEach(item => {
        const source = item.querySelector('.source-input').value.trim();
        const prefix = item.querySelector('.prefix-input').value.trim();
        const target_slot = item.querySelector('.slot-input').value.trim();
        const style = item.querySelector('.style-input').value;

        // Skip empty sources
        if (!source) return;

        newRouteMatrix.push({
            source: source,
            prefix: prefix || null,
            target_slot: target_slot || null,
            style: style || null
        });
    });

    const payload = {
        'route_matrix': newRouteMatrix
    };

    const res = await window.apiFetch('/api/config/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res && res.status === 'success') {
        if (typeof window.addAudit === 'function') {
            window.addAudit("✅ 高级路由矩阵固化完成。", "success");
        }
        window.settingsData.route_matrix = newRouteMatrix;
        
        // Ensure to redraw the view so the internal dataset index bindings stay clean
        if (typeof window.renderSettingsCategory === 'function') {
            window.renderSettingsCategory('route_matrix');
        }
    } else {
        if (typeof window.addAudit === 'function') {
            window.addAudit(`❌ 路由规则保存失败: ${res ? res.error : '未知链路错误'}`, "error");
        }
    }

    if (btn) {
        btn.disabled = false;
        btn.innerHTML = '💾 保存全量路由';
    }
};
