/**
 * 🕹️ Illacme Compute Center - Modal Operations Shard (SOP-02 DECOUPLED)
 * 职责：管理模态框内交互控制，包括自定义下拉选项触发、算力渠道筛选、选项同步与字段校验提示。
 */

window.ComputeHandlers = window.ComputeHandlers || {};

(function() {
    const ModalOps = {
        /**
         * 🛰️ 全局下拉菜单控制
         */
        toggleSovereignDropdown(event, menuId, searchInputId) {
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }
            const menu = document.getElementById(menuId);
            if (!menu) return;

            document.querySelectorAll('.custom-dropdown-menu').forEach(m => {
                if (m.id !== menuId) m.classList.remove('show');
            });
            menu.classList.toggle('show');

            if (menu.classList.contains('show') && searchInputId) {
                setTimeout(() => {
                    const searchInput = document.getElementById(searchInputId);
                    if (searchInput) searchInput.focus();
                }, 50);
            }
        },

        /**
         * 🔍 算力渠道过滤
         */
        filterProtocols(term, listId) {
            const lowerTerm = term.toLowerCase();
            const items = document.querySelectorAll(`#${listId} .dropdown-item`);
            items.forEach(item => {
                const name = (item.getAttribute('data-name') || item.innerText || '').toLowerCase();
                item.style.display = name.includes(lowerTerm) ? 'flex' : 'none';
            });
        },

        /**
         * 🎯 选择算力渠道
         */
        selectProvider(id, name, defaultUrl) {
            const input = document.getElementById('swal-input-type');
            const tAdd = document.getElementById('provider-trigger-add');
            const tEdit = document.getElementById('provider-trigger-edit');
            const urlInput = document.getElementById('swal-input-url');

            const isSwitching = input && input.value !== id;

            if (input) input.value = id;
            if (tAdd) tAdd.innerText = name;
            if (tEdit) tEdit.innerText = name;

            document.querySelectorAll('.custom-dropdown-menu').forEach(m => m.classList.remove('show'));

            if (urlInput && defaultUrl && (isSwitching || urlInput.value === "")) {
                urlInput.value = defaultUrl;
            }
        },

        /**
         * ❌ 显示字段错误
         */
        showFieldError(fieldId, message) {
            const input = document.getElementById(`swal-input-${fieldId}`);
            if (input) {
                input.classList.add('shake-hint');
                setTimeout(() => input.classList.remove('shake-hint'), 500);
                input.focus();
            }
            // 清理对应字段旧的报错并展现新的
            const errorContainer = document.getElementById(`error-${fieldId}`);
            if (errorContainer) {
                errorContainer.innerText = `⚠️ ${message}`;
                errorContainer.style.display = 'block';
            } else {
                // 兜底使用右上角 Toast
                if (typeof showNotification === 'function') showNotification(message, 'error');
            }
        }
    };

    // 🚀 [V74.24] 物理挂载至全局总线
    Object.assign(window.ComputeHandlers, ModalOps);
})();
