/**
 * 🧰 [V57.5] Illacme Plenipes System Settings Cache Manager Component
 * 职责：分层缓存（BlockCache、AI元数据、指纹账本、构建镜像）盘点、自愈重建与精细化管理。
 * 🛡️ [SOP-01 Compliant]：单文件严格控制在 300 行以内。
 */

(function() {
    window.refreshCacheStats = async () => {
        const elBlockCount = document.getElementById('cache-stats-count');
        const elBlockSize = document.getElementById('cache-stats-size');
        const elMetaCount = document.getElementById('cache-stats-meta-count');
        const elBuildSize = document.getElementById('cache-stats-build-size');
        if (elBlockCount) elBlockCount.innerText = '正在统计...';
        if (elBlockSize) elBlockSize.innerText = '正在统计...';
        if (elMetaCount) elMetaCount.innerText = '正在统计...';
        if (elBuildSize) elBuildSize.innerText = '正在统计...';
        
        try {
            const stats = await apiFetch('/api/system/cache/stats');
            if (stats) {
                if (elBlockCount) elBlockCount.innerText = (stats.file_count || 0) + ' 个段落';
                const sizeMB = ((stats.size_bytes || 0) / (1024 * 1024)).toFixed(2);
                if (elBlockSize) elBlockSize.innerText = sizeMB + ' MB';
                if (elMetaCount) elMetaCount.innerText = (stats.meta_file_count || 0) + ' 篇镜像';
                const buildMB = ((stats.build_size_bytes || 0) / (1024 * 1024)).toFixed(2);
                if (elBuildSize) elBuildSize.innerText = buildMB + ' MB';
            }
        } catch (err) {
            if (elBlockCount) elBlockCount.innerText = '获取失败';
            if (elBlockSize) elBlockSize.innerText = '获取失败';
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
            icon: 'info', showCancelButton: true,
            background: 'hsla(236, 37%, 8%, 0.95)', color: 'var(--text-bright, #ffffff)',
            confirmButtonText: '立即迁移', cancelButtonText: '取消',
            customClass: { popup: 'glass-panel', confirmButton: 'primary-btn glow-btn', cancelButton: 'danger-btn' }
        });
        
        if (result.isConfirmed) {
            addAudit("🚚 正在手动触发段落缓存迁移任务...");
            const res = await apiFetch('/api/governance/cache/migrate', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ old_levels: oldShardLevels, new_levels: newShardLevels, old_dir: oldCacheDir, new_dir: newCacheDir })
            });
            if (res && res.status === 'success') {
                Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: '缓存迁移完成', showConfirmButton: false, timer: 3000 });
                addAudit("✅ 段落缓存物理迁移已成功完成。", 'success');
                await window.refreshCacheStats();
            } else {
                Swal.fire('迁移失败', res ? res.message : '未知原因', 'error');
            }
        }
    };

    // ⚡ 1. 仅重置文件增量指纹 (0 LLM 算力消耗重编译)
    window.resetFingerprintsOnly = async () => {
        if (typeof Swal === 'undefined') return;
        const result = await Swal.fire({
            title: '⚡ 仅重置文件增量指纹',
            html: `清空数据库中的文档变更哈希指纹：<br><br>` +
                  `• <b>保留资产</b>：正文段落译文 (Block Cache)、AI 别名/SEO、发布日期及图谱拓扑 100% 完整保留<br>` +
                  `• <b>0 次大模型调用</b>：下一次发布跳过“未修改跳过”限制，直接复用已有资产秒级重新排版组装<br><br>` +
                  `<span style="color: #00f2ff; font-size: 0.85em;">适合修改了模板主题、样式、排版规则或调整了分发设置后的全量重新部署。</span>`,
            icon: 'info', showCancelButton: true,
            background: 'hsla(236, 37%, 8%, 0.95)', color: 'var(--text-bright, #ffffff)',
            confirmButtonText: '⚡ 确定重置指纹', cancelButtonText: '取消',
            customClass: { popup: 'glass-panel', confirmButton: 'primary-btn glow-btn', cancelButton: 'danger-btn' }
        });

        if (result.isConfirmed) {
            addAudit("⚡ 正在重置全站文档增量指纹...");
            const res = await apiFetch('/api/governance/ledger/reset-fingerprints', { method: 'POST' });
            if (res && res.status === 'success') {
                Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: '指纹已重置 (全部资产已保留)', showConfirmButton: false, timer: 3000 });
                addAudit("✅ 文档指纹已清空，AI 资产完整保留，下次发布将 0 算力全速重编译。", 'success');
                const activeId = window.settingsData?._active_imprint || 'default';
                localStorage.removeItem('sync_completed');
                localStorage.removeItem(`sync_completed_${activeId}`);
            } else {
                Swal.fire('重置失败', res ? (res.message || res.detail) : '未知原因', 'error');
            }
        }
    };

    // 🩹 2. 从本地物理元信息快照自愈重建账本
    window.rebuildLedgerFromCache = async () => {
        if (typeof Swal === 'undefined') return;
        const result = await Swal.fire({
            title: '🩹 物理快照自愈重建账本',
            html: `扫描 <code>cache/metadata/</code> 目录下的物理 JSON 快照：<br><br>` +
                  `• <b>无损回填</b>：将历史沉淀的 AI Slug、SEO 摘要、多语种状态、发布日期及审校锁定注回 SQLite 账本<br>` +
                  `• <b>0 算力开销</b>：无需向大模型发送任何请求，纯本地秒级恢复<br><br>` +
                  `<span style="color: #00ff88; font-size: 0.85em;">用于数据库文件损坏、跨设备迁移后或误清空账本后的秒级自愈。</span>`,
            icon: 'question', showCancelButton: true,
            background: 'hsla(236, 37%, 8%, 0.95)', color: 'var(--text-bright, #ffffff)',
            confirmButtonText: '🩹 开始自愈重建', cancelButtonText: '取消',
            customClass: { popup: 'glass-panel', confirmButton: 'primary-btn glow-btn', cancelButton: 'danger-btn' }
        });

        if (result.isConfirmed) {
            addAudit("🩹 正在从物理快照自愈重建账本...");
            const res = await apiFetch('/api/governance/ledger/rebuild-from-cache', { method: 'POST' });
            if (res && res.status === 'success') {
                Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: `成功自愈恢复 ${res.count || 0} 篇文档`, showConfirmButton: false, timer: 3000 });
                addAudit(`✅ 账本自愈完成，已从物理文件恢复 ${res.count || 0} 篇文档记录。`, 'success');
                await window.refreshCacheStats();
            } else {
                Swal.fire('自愈失败', res ? (res.message || res.detail) : '未知原因', 'error');
            }
        }
    };

    // 🧱 3. 清空段落翻译缓存
    window.clearBlockCacheAll = async () => {
        if (typeof Swal === 'undefined') return;
        const result = await Swal.fire({
            title: '🧱 清空段落翻译缓存',
            html: `物理删除 <code>cache/blocks/</code> 下所有语言与风格的段落翻译文本文件：<br><br>` +
                  `• <b>清理范围</b>：仅清空正文段落翻译文本缓存<br>` +
                  `• <b>保留资产</b>：文档发布账本、原稿 Markdown、AI Slug 与 SEO 元数据完好保留<br>` +
                  `• <b>影响</b>：下次发布时正文将重新请求大模型进行全量翻译（耗费 Token 与时间）<br><br>` +
                  `<span style="color: #ffb800; font-size: 0.85em;">适用场景：更换了翻译模型、大幅调整了系统提示词或翻译风格。</span>`,
            icon: 'warning', showCancelButton: true,
            background: 'hsla(236, 37%, 8%, 0.95)', color: 'var(--text-bright, #ffffff)',
            confirmButtonText: '💥 确定清空段落缓存', cancelButtonText: '取消',
            customClass: { popup: 'glass-panel', confirmButton: 'danger-btn glow-btn', cancelButton: 'primary-btn' }
        });
        
        if (result.isConfirmed) {
            addAudit("🗑️ 正在清空段落翻译缓存...");
            const res = await apiFetch('/api/governance/cache/clear', { method: 'POST' });
            if (res && res.status === 'success') {
                Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: '段落缓存已成功清空', showConfirmButton: false, timer: 3000 });
                addAudit("✅ 全量段落翻译缓存已被安全物理移除。", 'success');
                await window.refreshCacheStats();
            } else {
                Swal.fire('清理失败', res ? res.message : '未知原因', 'error');
            }
        }
    };

    // 🏷️ 4. 重置 AI 元数据缓存
    window.clearAIMetadataCache = async () => {
        if (typeof Swal === 'undefined') return;
        const result = await Swal.fire({
            title: '🏷️ 重置 AI 元数据缓存',
            html: `清空由大模型推导衍生的网址别名 (Slug) 与 SEO 描述：<br><br>` +
                  `• <b>重置范围</b>：仅清空 AI 衍生的 Slug 网址别名与 SEO 摘要数据<br>` +
                  `• <b>保留资产</b>：正文段落翻译 (Block Cache)、物理原稿笔记、发布时间等 100% 完好保留<br>` +
                  `• <b>影响</b>：下次发布仅向大模型重新请求推导 Slug 与 SEO（极低 Token 消耗）<br><br>` +
                  `<span style="color: #a371f7; font-size: 0.85em;">适用场景：调整了网址命名策略或想重新生成全站 SEO 摘要。</span>`,
            icon: 'warning', showCancelButton: true,
            background: 'hsla(236, 37%, 8%, 0.95)', color: 'var(--text-bright, #ffffff)',
            confirmButtonText: '🏷️ 确定重置元数据', cancelButtonText: '取消',
            customClass: { popup: 'glass-panel', confirmButton: 'danger-btn glow-btn', cancelButton: 'primary-btn' }
        });

        if (result.isConfirmed) {
            addAudit("🏷️ 正在重置 AI Slug 与 SEO 元数据...");
            const res = await apiFetch('/api/governance/cache/ai-meta/clear', { method: 'POST' });
            if (res && res.status === 'success') {
                Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: 'AI 元数据已清空', showConfirmButton: false, timer: 3000 });
                addAudit("✅ AI Slug 与 SEO 元数据已清空，正文译文已保留。", 'success');
                await window.refreshCacheStats();
            } else {
                Swal.fire('重置失败', res ? res.message : '未知原因', 'error');
            }
        }
    };

    // 🧹 5. 清理构建源码镜像与增量产物
    window.clearBuildCache = async () => {
        if (typeof Swal === 'undefined') return;
        const result = await Swal.fire({
            title: '🧹 清理构建产物与源码镜像',
            html: `清理 <code>cache/sources/</code> 与 <code>cache/build/</code> 目录下的编译碎片：<br><br>` +
                  `• <b>清理范围</b>：SSG 主题源码中间镜像、增量编译缓存与运行时临时文件<br>` +
                  `• <b>保留资产</b>：段落翻译 (Block Cache)、物理元数据镜像与 SQLite 账本不受任何影响<br><br>` +
                  `<span style="color: #88a4e6; font-size: 0.85em;">适用场景：切换主题框架 (SSG)、排查静态构建遗留碎片或释放磁盘空间。</span>`,
            icon: 'info', showCancelButton: true,
            background: 'hsla(236, 37%, 8%, 0.95)', color: 'var(--text-bright, #ffffff)',
            confirmButtonText: '🧹 立即清理', cancelButtonText: '取消',
            customClass: { popup: 'glass-panel', confirmButton: 'primary-btn glow-btn', cancelButton: 'danger-btn' }
        });

        if (result.isConfirmed) {
            addAudit("🧹 正在清理构建缓存与源码镜像...");
            const res = await apiFetch('/api/governance/cache/build/clear', { method: 'POST' });
            if (res && res.status === 'success') {
                Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: '构建缓存清理完成', showConfirmButton: false, timer: 3000 });
                addAudit("✅ 构建产物与源码镜像缓存已安全清除。", 'success');
                await window.refreshCacheStats();
            } else {
                Swal.fire('清理失败', res ? res.message : '未知原因', 'error');
            }
        }
    };

    // 💣 6. 清空文档账本与元信息镜像
    window.resetLedgerOnly = async () => {
        if (typeof Swal === 'undefined') return;
        const result = await Swal.fire({
            title: '💣 彻底清空文档账本与元信息镜像',
            html: `清空全站文档 SQLite 账本与 <code>cache/metadata/</code> 物理镜像：<br><br>` +
                  `• <b>保留段落翻译缓存</b>：磁盘上的正文翻译文本（Block Cache）完好保留，无需从头重译正文<br>` +
                  `• <b>保护原稿物理文件</b>：文库中的 Markdown 笔记受绝对保护，绝不修改<br>` +
                  `• <b>清空内容</b>：清空 SQLite 数据库（文档/多语言/发布状态表）与物理镜像，下次发布将重新建立元信息索引<br><br>` +
                  `<span style="color: #ff4d4d; font-size: 0.85em;">适用场景：文库大范围重命名、清空全部发布历史与路由映射。</span>`,
            icon: 'warning', showCancelButton: true,
            background: 'hsla(236, 37%, 8%, 0.95)', color: 'var(--text-bright, #ffffff)',
            confirmButtonText: '💣 确定清空账本', cancelButtonText: '取消',
            customClass: { popup: 'glass-panel', confirmButton: 'danger-btn glow-btn', cancelButton: 'primary-btn' }
        });

        if (result.isConfirmed) {
            addAudit("💣 正在彻底重置全域账本与元信息镜像...");
            const res = await apiFetch('/api/governance/ledger/reset', { method: 'POST' });
            if (res && res.status === 'success') {
                Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: '账本与元信息已彻底重置', showConfirmButton: false, timer: 3000 });
                addAudit("✅ 全域文档指纹账本与元信息镜像已被完全归零。", 'success');
                const activeId = window.settingsData?._active_imprint || 'default';
                localStorage.removeItem('sync_completed');
                localStorage.removeItem(`sync_completed_${activeId}`);
                await window.refreshCacheStats();
            } else {
                Swal.fire('重置失败', res ? (res.message || res.detail) : '未知原因', 'error');
            }
        }
    };

    window.resetLedgerAndSyncAll = window.resetFingerprintsOnly;
})();
