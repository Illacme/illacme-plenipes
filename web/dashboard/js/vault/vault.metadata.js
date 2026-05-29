/**
 * 📝 [V87.0] Illacme Plenipes Modal Editor - Metadata Shard
 */

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
