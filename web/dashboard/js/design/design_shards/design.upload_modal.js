/**
 * 🎨 [V1.0] Illacme Plenipes Design Studio - Asset Upload Modal Shard
 * 职责：提供高规格暗黑毛玻璃本地图片上传弹窗，支持文件拖拽、实时预览、元数据登记与资产库联动。
 * 🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
 * 🛡️ [SOP-03] 商业级毛玻璃视觉与微交互反馈。
 */

(function () {
    let _selectedUploadFile = null;

    window.openAssetUploadModal = function () {
        const existing = document.getElementById('asset-upload-modal');
        if (existing) existing.remove();
        _selectedUploadFile = null;

        const modalHtml = `
            <div id="asset-upload-modal" class="modal-overlay active" style="z-index:10000; display:flex; align-items:center; justify-content:center; background:rgba(0,0,0,0.8); backdrop-filter:blur(10px); position:fixed; inset:0; padding:16px;">
                <div class="glass-panel" style="width:580px; max-width:94vw; max-height:88vh; border-radius:14px; border:1px solid rgba(0,242,254,0.35); display:flex; flex-direction:column; overflow:hidden; box-shadow:0 24px 60px rgba(0,0,0,0.9);">
                    <!-- 顶栏 -->
                    <div style="padding:16px 20px; border-bottom:1px solid rgba(255,255,255,0.08); display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.02);">
                        <div style="font-weight:700; color:#fff; font-size:0.95rem; display:flex; align-items:center; gap:8px;">
                            <span>📤</span>
                            <span>上传本地图片至媒体资产库</span>
                        </div>
                        <button type="button" class="mini-btn" style="padding:4px 8px; font-size:0.8rem;" onclick="document.getElementById('asset-upload-modal').remove()">✕</button>
                    </div>

                    <!-- 内容区 -->
                    <div style="padding:20px; overflow-y:auto; display:flex; flex-direction:column; gap:16px;">
                        <!-- 拖拽上传核心区域 -->
                        <div id="upload-drop-zone" style="border:2px dashed rgba(0,242,254,0.35); background:rgba(0,242,254,0.03); border-radius:10px; padding:28px 20px; text-align:center; cursor:pointer; transition:all 0.2s cubic-bezier(0.16,1,0.3,1);"
                             onclick="document.getElementById('asset-upload-file-input').click()"
                             ondragover="event.preventDefault(); this.style.borderColor='#00f2fe'; this.style.background='rgba(0,242,254,0.1)';"
                             ondragleave="event.preventDefault(); this.style.borderColor='rgba(0,242,254,0.35)'; this.style.background='rgba(0,242,254,0.03)';"
                             ondrop="window.handleAssetDrop(event)">
                            <input type="file" id="asset-upload-file-input" accept="image/png,image/jpeg,image/webp,image/svg+xml,image/gif" style="display:none;" onchange="window.handleAssetFileSelect(this)" />
                            <div id="upload-drop-prompt" style="display:flex; flex-direction:column; align-items:center; gap:8px;">
                                <span style="font-size:2.4rem; opacity:0.85;">🖼️</span>
                                <div style="font-size:0.88rem; font-weight:600; color:var(--text-bright);">点击选择图片，或将图片文件直接拖拽至此</div>
                                <div style="font-size:0.72rem; color:var(--text-dim);">支持 PNG、JPG、JPEG、WebP、SVG、GIF 格式 (自动哈希去重)</div>
                            </div>
                            <div id="upload-file-preview-area" style="display:none; flex-direction:column; align-items:center; gap:10px;">
                                <img id="upload-img-preview" src="" style="max-height:160px; max-width:100%; object-fit:contain; border-radius:6px; border:1px solid rgba(0,242,254,0.4); box-shadow:0 4px 15px rgba(0,0,0,0.5);" />
                                <div style="font-size:0.76rem; color:var(--accent-secondary);" id="upload-file-meta"></div>
                                <span style="font-size:0.68rem; color:var(--text-dim); text-decoration:underline;">点击重新选择其他图片</span>
                            </div>
                        </div>

                        <!-- 资产描述与备注输入 -->
                        <div style="display:flex; flex-direction:column; gap:6px;">
                            <label style="font-size:0.75rem; color:var(--text-dim);">资产备注与提示说明 (可选)</label>
                            <input type="text" id="asset-upload-prompt-input" placeholder="例如：手绘官方架构图、极简科技封面、实战演练截屏..." style="width:100%; padding:9px 12px; border-radius:6px; background:rgba(0,0,0,0.4); border:1px solid rgba(255,255,255,0.15); color:#fff; font-size:0.8rem; box-sizing:border-box;" />
                        </div>
                    </div>

                    <!-- 底栏操作 -->
                    <div style="padding:14px 20px; border-top:1px solid rgba(255,255,255,0.08); background:rgba(0,0,0,0.3); display:flex; justify-content:flex-end; gap:10px;">
                        <button type="button" class="mini-btn" style="padding:6px 14px; font-size:0.76rem;" onclick="document.getElementById('asset-upload-modal').remove()">取消</button>
                        <button type="button" class="mini-btn glow-btn" id="btn-submit-asset-upload" style="padding:6px 20px; font-size:0.78rem; background:var(--accent-secondary, #00f2fe); color:#000; font-weight:700; border:none;" onclick="window.dispatchSubmitAssetUpload()">
                            🚀 立即上传入库
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    };

    window.handleAssetDrop = function (e) {
        e.preventDefault();
        const dropZone = document.getElementById('upload-drop-zone');
        if (dropZone) {
            dropZone.style.borderColor = 'rgba(0,242,254,0.35)';
            dropZone.style.background = 'rgba(0,242,254,0.03)';
        }
        if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            window.processSelectedUploadFile(e.dataTransfer.files[0]);
        }
    };

    window.handleAssetFileSelect = function (input) {
        if (input && input.files && input.files.length > 0) {
            window.processSelectedUploadFile(input.files[0]);
        }
    };

    window.processSelectedUploadFile = function (file) {
        if (!file || !file.type.startsWith('image/')) {
            if (window.showToast) window.showToast('⚠️ 请选择合规的图片文件', 'warning');
            return;
        }
        _selectedUploadFile = file;

        const promptArea = document.getElementById('upload-drop-prompt');
        const previewArea = document.getElementById('upload-file-preview-area');
        const imgPreview = document.getElementById('upload-img-preview');
        const fileMeta = document.getElementById('upload-file-meta');
        const promptInput = document.getElementById('asset-upload-prompt-input');

        if (promptArea) promptArea.style.display = 'none';
        if (previewArea) previewArea.style.display = 'flex';

        const sizeKb = (file.size / 1024).toFixed(1);
        if (fileMeta) fileMeta.textContent = `📁 ${file.name} (${sizeKb} KB)`;
        if (promptInput && !promptInput.value.trim()) {
            promptInput.value = file.name.replace(/\.[^/.]+$/, '');
        }

        const reader = new FileReader();
        reader.onload = function (e) {
            if (imgPreview) imgPreview.src = e.target.result;
        };
        reader.readAsDataURL(file);
    };

    window.dispatchSubmitAssetUpload = async function () {
        if (!_selectedUploadFile) {
            if (window.showToast) window.showToast('⚠️ 请先选择要上传的图片文件', 'warning');
            return;
        }

        const btn = document.getElementById('btn-submit-asset-upload');
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-gear">⚙️</span> 正在上传入库...';
        }

        const promptInput = document.getElementById('asset-upload-prompt-input');
        const promptVal = promptInput ? promptInput.value.trim() : '';

        const formData = new FormData();
        formData.append('file', _selectedUploadFile);
        if (promptVal) formData.append('prompt', promptVal);

        const fetchApi = window.apiFetch || (async (u, o) => (await fetch(u, o)).json());
        try {
            const res = await fetchApi('/api/design/assets/upload', {
                method: 'POST',
                body: formData
            });

            if (res && res.success) {
                if (window.showToast) window.showToast(`✨ ${res.message || '本地图片已成功入库！'}`, 'success');
                const modal = document.getElementById('asset-upload-modal');
                if (modal) modal.remove();

                // 自动刷新媒体资产网格
                if (typeof window.loadAndRenderDesignAssets === 'function') {
                    const root = document.getElementById('design-center-root');
                    window.loadAndRenderDesignAssets(root);
                }
            } else {
                throw new Error((res && res.message) || (res && res.detail) || '上传失败');
            }
        } catch (e) {
            if (window.showToast) window.showToast(`🛑 上传失败: ${e.message}`, 'error');
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '🚀 立即上传入库';
            }
        }
    };
})();
