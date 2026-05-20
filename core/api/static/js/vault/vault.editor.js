/**
 * 📝 [V87.0] Illacme Plenipes Modal Editor & Marked Parser Module
 * 职责：文稿编辑器交互、YAML Frontmatter 智能解析注入、Markdown 双链附件解析与 Wiki 联动、以及同步滚动渲染。
 */

// 4. 全量物理编辑器 (Modal)
window.openEditor = async (docId) => {
    window.activeDocId = docId;
    const modal = document.getElementById('editor-modal');
    const body = document.getElementById('editor-body');
    const title = document.getElementById('editor-title');
    const mTitle = document.getElementById('editor-meta-title');
    const mSlug = document.getElementById('editor-meta-slug');

    title.innerText = "EXTRACTING PHYSICAL ASSET...";
    if (body) body.placeholder = "等待数据载入...";
    const status = document.getElementById('save-status');
    if (status) status.innerText = ""; // 🚀 状态对齐：清除上一个文档的残留状态
    modal.style.display = 'flex';

    const doc = await apiFetch(`/ledger/document/${encodeURIComponent(docId)}`);
    if (doc) {
        title.innerText = `EDITOR: ${doc.title || docId}`;
        if (body) {
            body.placeholder = "在此处输入文稿内容（支持 Markdown 语法）...";
            body.value = doc.content || "";
        }
        if (mTitle) mTitle.value = doc.title || "";
        if (mSlug) mSlug.value = doc.slug || "";
        
        // 🚀 [V68.0] 动态元数据注入
        renderDynamicMetadata(doc.frontmatter || {});
        
        // 🌓 [V87.0] 初始化编辑器模式为源码模式，并预渲染预览内容
        setEditorMode('source');
        updateEditorPreview();
        initSyncScroll();
    }
};

window.renderDynamicMetadata = (metadata) => {
    const container = document.getElementById('dynamic-metadata-container');
    if (!container) return;
    container.innerHTML = "";

    // 过滤掉已经在上方固定显示的 title 和 slug
    const keys = Object.keys(metadata).filter(k => k !== 'title' && k !== 'slug');
    
    if (keys.length === 0) {
        container.innerHTML = `<div style="font-size:0.7rem; opacity:0.3; text-align:center; padding:10px;">(未发现扩展元数据)</div>`;
        return;
    }

    keys.forEach(key => {
        const val = metadata[key];
        const item = document.createElement('div');
        item.className = 'drawer-item';
        
        // 渲染项结构标头
        item.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <label class="tiny-label">${key.toUpperCase()}</label>
                <button class="mini-action-btn" onclick="this.parentElement.parentElement.remove()" title="删除该字段" style="font-size:0.6rem; padding:2px 5px; opacity:0.5;">×</button>
            </div>
        `;
        
        // 探测是否为日期/时间字段（包含 date, time, created, updated 或符合 ISO 日期时间正则）
        const isDateField = key.toLowerCase().includes('date') || 
                            key.toLowerCase().includes('time') || 
                            key.toLowerCase().includes('created') || 
                            key.toLowerCase().includes('updated') ||
                            (typeof val === 'string' && /^\d{4}-\d{2}-\d{2}(T|\s)\d{2}:\d{2}/.test(val));

        // 采用编程式属性注入，完美防范 JSON 字符串单双引号及特殊符号引起的 HTML 解析截断与混淆
        if (typeof val === 'boolean') {
            const input = document.createElement('input');
            input.type = 'checkbox';
            input.className = 'metadata-input';
            input.setAttribute('data-key', key);
            input.checked = val;
            input.style.width = 'auto';
            input.style.marginLeft = '10px';
            item.firstElementChild.appendChild(input);
        } else if (isDateField) {
            // 🚀 [V87.3] 尊贵日期微端交互：采用 HTML5 本地化日期选择器
            const input = document.createElement('input');
            input.type = 'datetime-local';
            input.className = 'metadata-input setting-input';
            input.setAttribute('data-key', key);
            input.setAttribute('data-is-date', 'true');
            
            // 将输入值标准化为 YYYY-MM-DDTHH:mm 格式以加载到 datetime-local 控件中
            let displayVal = "";
            if (val) {
                const dateObj = new Date(val);
                if (!isNaN(dateObj.getTime())) {
                    const y = dateObj.getFullYear();
                    const m = String(dateObj.getMonth() + 1).padStart(2, '0');
                    const d = String(dateObj.getDate()).padStart(2, '0');
                    const hh = String(dateObj.getHours()).padStart(2, '0');
                    const mm = String(dateObj.getMinutes()).padStart(2, '0');
                    displayVal = `${y}-${m}-${d}T${hh}:${mm}`;
                } else {
                    // 若日期不可解析，则作为普通字符串回退显示
                    displayVal = val;
                }
            }
            input.value = displayVal;
            item.appendChild(input);
        } else {
            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'metadata-input setting-input';
            input.setAttribute('data-key', key);
            
            if (Array.isArray(val)) {
                // 检查数组中是否包含对象类型（复杂结构，如 HREFLANGS）
                const hasObject = val.some(item => item !== null && typeof item === 'object');
                if (hasObject) {
                    input.value = JSON.stringify(val);
                    input.placeholder = "JSON 数组格式";
                } else {
                    input.value = val.join(', ');
                    input.placeholder = "逗号分隔列表";
                }
            } else if (val !== null && typeof val === 'object') {
                // 复杂键值对结构（如 dict）
                input.value = JSON.stringify(val);
                input.placeholder = "JSON 对象格式";
            } else {
                input.value = val || '';
            }
            item.appendChild(input);
        }
        
        container.appendChild(item);
    });
};

window.setEditorMode = (mode) => {
    const body = document.getElementById('editor-body');
    const preview = document.getElementById('editor-preview');
    const btnSource = document.getElementById('mode-source');
    const btnPreview = document.getElementById('mode-preview');
    const btnSplit = document.getElementById('mode-split');

    if (!body || !preview) return;

    [btnSource, btnPreview, btnSplit].forEach(b => b?.classList.remove('active'));

    if (mode === 'source') {
        body.style.display = 'block';
        preview.style.display = 'none';
        btnSource?.classList.add('active');
    } else if (mode === 'preview') {
        body.style.display = 'none';
        preview.style.display = 'block';
        btnPreview?.classList.add('active');
        updateEditorPreview();
        initSyncScroll();
    } else if (mode === 'split') {
        body.style.display = 'block';
        preview.style.display = 'block';
        btnSplit?.classList.add('active');
        updateEditorPreview();
        initSyncScroll();
    }
};

window.closeEditor = () => {
    document.getElementById('editor-modal').style.display = 'none';
    const configTabs = document.getElementById('config-tabs');
    if (configTabs) configTabs.style.display = 'none';
};

window.saveDocument = async () => {
    const content = document.getElementById('editor-body').value;
    const titleEl = document.getElementById('editor-meta-title');
    const slugEl = document.getElementById('editor-meta-slug');
    const status = document.getElementById('save-status');
    status.innerText = "💾 正在写入磁道...";

    // 🚀 [V68.0] 收集动态元数据
    const frontmatter = {};
    const metaInputs = document.querySelectorAll('.metadata-input');
    metaInputs.forEach(input => {
        const key = input.getAttribute('data-key');
        if (input.type === 'checkbox') {
            frontmatter[key] = input.checked;
        } else {
            const val = input.value.trim();
            
            // 🚀 [V87.3] 智能日期时区反向对准与重塑
            if (input.getAttribute('data-is-date') === 'true') {
                if (!val) {
                    frontmatter[key] = "";
                    return;
                }
                const dateObj = new Date(val);
                if (!isNaN(dateObj.getTime())) {
                    const pad = (n) => String(n).padStart(2, '0');
                    const offset = -dateObj.getTimezoneOffset();
                    const sign = offset >= 0 ? '+' : '-';
                    const tz = sign + pad(Math.floor(Math.abs(offset) / 60)) + ':' + pad(Math.abs(offset) % 60);
                    
                    const y = dateObj.getFullYear();
                    const m = pad(dateObj.getMonth() + 1);
                    const d = pad(dateObj.getDate());
                    const hh = pad(dateObj.getHours());
                    const mm = pad(dateObj.getMinutes());
                    const ss = pad(dateObj.getSeconds());
                    
                    frontmatter[key] = `${y}-${m}-${d}T${hh}:${mm}:${ss}${tz}`;
                    return;
                }
            }
            
            // 🚀 [V87.2] 智能解析 JSON 数组与复杂对象，防止结构混淆与二次破坏
            if ((val.startsWith('{') && val.endsWith('}')) || (val.startsWith('[') && val.endsWith(']'))) {
                try {
                    frontmatter[key] = JSON.parse(val);
                    return; // 成功解析为 JSON，跳过后续 standard 处理
                } catch (e) {
                    console.warn(`Failed to parse metadata field "${key}" as JSON, fallback to raw string:`, e);
                }
            }
            
            // 简单处理：如果包含逗号，尝试转为数组（对应用户对列表的支持要求）
            if (val.includes(',')) {
                frontmatter[key] = val.split(',').map(v => v.trim()).filter(v => v !== "");
            } else {
                frontmatter[key] = val;
            }
        }
    });

    const payload = { content, frontmatter };
    if (titleEl) payload.title = titleEl.value;
    if (slugEl) payload.slug = slugEl.value;

    const res = await apiFetch(`/ledger/document/${encodeURIComponent(window.activeDocId)}/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res && res.success) {
        status.innerText = "✅ 写入成功";
        addAudit(`📄 资产 ${window.activeDocId.substring(0, 8)} 已完成物理变更。`);
        setTimeout(closeEditor, 800);
        if (typeof currentView !== 'undefined' && window.currentView === 'overview') {
            if (typeof refreshGalaxy === 'function') refreshGalaxy();
        }
        if (typeof loadVault === 'function') {
            loadVault(window.vaultCurrentQuery, window.vaultCurrentPage);
        }
    } else {
        status.innerText = "❌ 写入失败";
        if (res && res.error) console.error(res.error);
    }
};
