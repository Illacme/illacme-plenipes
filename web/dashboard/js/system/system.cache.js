/**
 * 🧰 [V57.4] Illacme Plenipes System Settings Cache Manager Component
 * 职责：段落翻译缓存的统计盘点、分级目录物理迁移与一键清空。
 * 对应重构拆分协议：SOP-02/SOP-05 模板一合规物理平移。
 */

(function() {
    window.refreshCacheStats = async () => {
        const elCount = document.getElementById('cache-stats-count');
        const elSize = document.getElementById('cache-stats-size');
        if (!elCount || !elSize) return;
        
        elCount.innerText = '正在统计...';
        elSize.innerText = '正在统计...';
        
        try {
            const stats = await apiFetch('/api/system/cache/stats');
            if (stats) {
                elCount.innerText = (stats.file_count || 0) + ' 个缓存段落';
                const sizeMB = ((stats.size_bytes || 0) / (1024 * 1024)).toFixed(2);
                elSize.innerText = sizeMB + ' MB';
            }
        } catch (err) {
            elCount.innerText = '获取失败';
            elSize.innerText = '获取失败';
            console.error('获取缓存统计失败:', err);
        }
    };

    window.manualMigrateCache = async () => {
        if (typeof Swal === 'undefined') return;
        
        const initialObj = window.initialSettingsState ? JSON.parse(window.initialSettingsState) : {};
        const oldShardLevels = initialObj['block_cache_shard_levels'] ?? 1;
        const newShardLevels = window.settingsData.block_cache_shard_levels ?? 1;
        const oldCacheDir = initialObj['block_cache_dir'] ?? null;
        const newCacheDir = window.settingsData.block_cache_dir ?? null;

        const result = await Swal.fire({
            title: '🚚 手动触发段落缓存物理迁移',
            html: `系统将根据当前的配置状态，将缓存从旧分级搬移到新分级中：<br><br>` +
                  `• 旧配置：<b>${oldCacheDir || '默认'}</b> (L<b>${oldShardLevels}</b>)<br>` +
                  `• 新配置：<b>${newCacheDir || '默认'}</b> (L<b>${newShardLevels}</b>)<br><br>` +
                  `此操作将立即执行，请确认是否继续？`,
            icon: 'info',
            showCancelButton: true,
            background: 'hsla(236, 37%, 8%, 0.95)',
            color: 'var(--text-bright, #ffffff)',
            confirmButtonText: '立即迁移',
            cancelButtonText: '取消',
            customClass: {
                popup: 'glass-panel',
                confirmButton: 'primary-btn glow-btn',
                cancelButton: 'danger-btn'
            }
        });
        
        if (result.isConfirmed) {
            addAudit("🚚 正在手动触发段落缓存迁移任务...");
            const res = await apiFetch('/api/governance/cache/migrate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    old_levels: oldShardLevels,
                    new_levels: newShardLevels,
                    old_dir: oldCacheDir,
                    new_dir: newCacheDir
                })
            });
            if (res && res.status === 'success') {
                Swal.fire({
                    toast: true,
                    position: 'top-end',
                    icon: 'success',
                    title: '缓存迁移完成',
                    showConfirmButton: false,
                    timer: 3000
                });
                addAudit("✅ 段落缓存物理迁移已成功完成。", 'success');
                await window.refreshCacheStats();
            } else {
                Swal.fire('迁移失败', res ? res.message : '未知原因', 'error');
            }
        }
    };

    window.clearBlockCacheAll = async () => {
        if (typeof Swal === 'undefined') return;
        
        const result = await Swal.fire({
            title: '🗑️ 危险：清空段落缓存',
            text: '确定要物理删除所有翻译后的段落缓存文件吗？这会导致下一次翻译时，所有段落均需重新请求大模型进行翻译！',
            icon: 'warning',
            showCancelButton: true,
            background: 'hsla(236, 37%, 8%, 0.95)',
            color: 'var(--text-bright, #ffffff)',
            confirmButtonText: '💥 确定清空 (不保留备份)',
            cancelButtonText: '取消',
            customClass: {
                popup: 'glass-panel',
                confirmButton: 'danger-btn glow-btn',
                cancelButton: 'primary-btn'
            }
        });
        
        if (result.isConfirmed) {
            addAudit("🗑️ 正在清空段落翻译缓存...");
            const res = await apiFetch('/api/governance/cache/clear', { method: 'POST' });
            if (res && res.status === 'success') {
                Swal.fire({
                    toast: true,
                    position: 'top-end',
                    icon: 'success',
                    title: '段落缓存已成功清空',
                    showConfirmButton: false,
                    timer: 3000
                });
                addAudit("✅ 全量段落翻译缓存已被安全物理移除。", 'success');
                await window.refreshCacheStats();
            } else {
                Swal.fire('清理失败', res ? res.message : '未知原因', 'error');
            }
        }
    };
})();
