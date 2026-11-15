/**
 * 🏷️ [V1.0] Illacme Plenipes Vault - Frontmatter Micro Pills & Quick Switch Shard
 * 职责：原稿文库列表行内属性微胶囊渲染与轻量级原子开关 (播客/草稿/精选)。
 * 🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
 */

(function () {
    const _esc = (s) => (s === null || s === undefined ? '' : String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'));

    /**
     * 判断文档是否属于文档 (Docs) 或博客 (Blog) 范畴
     * 仅文档与博客详情页支持读者消费端伴读播客播放器，排除关于页、首页单页与案例橱窗
     */
    function isDocOrBlog(m) {
        if (!m) return false;
        const slot = (m.target_slot || '').toLowerCase();
        const prefix = (m.route_prefix || '').toLowerCase();
        const rel = (m.rel_path || '').replace(/\\/g, '/').toLowerCase();
        const layout = (m.layout || '').toLowerCase();

        // 1. 显式匹配 docs / blog / posts 槽位或路由前缀
        if (['docs', 'blog', 'posts'].includes(slot) || ['docs', 'blog', 'posts'].includes(prefix)) {
            return true;
        }
        // 2. 物理路径归属于 Docs/ 或 Blog/
        if (/^(docs|blog|posts)\//i.test(rel)) {
            return true;
        }
        // 3. 显式声明了 doc/blog 模板布局
        if (['doc', 'docs', 'blog', 'post', 'posts'].includes(layout)) {
            return true;
        }
        return false;
    }

    /**
     * 构建文章标题下方的微胶囊药丸 (Frontmatter Micro Pills)
     * @param {Object} m 文稿元数据对象
     * @param {String} escapedRelPath 转义后的相对路径
     * @returns {String} HTML 字符串
     */
    window.buildVaultPillsHtml = function (m, escapedRelPath) {
        if (!m) return '';
        const pills = [];

        // 1. 出版发布开关 (Publish / Draft Switch)
        if (m.draft === true) {
            pills.push(
                `<button type="button" class="vault-pill-badge pill-draft draft" ` +
                `onclick="window.toggleVaultDraft('${escapedRelPath}', false, event)" ` +
                `title="出版状态：草稿 (静态网站发布时跳过，点击切换为已发布)">` +
                `<span class="pill-dot"></span>🟡 草稿</button>`
            );
        } else {
            pills.push(
                `<button type="button" class="vault-pill-badge pill-draft published" ` +
                `onclick="window.toggleVaultDraft('${escapedRelPath}', true, event)" ` +
                `title="出版状态：已发布 (点击切换为草稿)">` +
                `<span class="pill-dot"></span>🟢 已发布</button>`
            );
        }

        // 2. 首页精选开关 (Featured Pill)
        const isFeatured = m.featured === true || m.pin === true || m.pinned === true;
        if (isFeatured) {
            pills.push(
                `<button type="button" class="vault-pill-badge pill-featured active" ` +
                `onclick="window.toggleVaultFeatured('${escapedRelPath}', false, event)" ` +
                `title="首页精选：已置顶/精选 (点击取消精选)">` +
                `⭐ 精选</button>`
            );
        } else {
            pills.push(
                `<button type="button" class="vault-pill-badge pill-featured normal" ` +
                `onclick="window.toggleVaultFeatured('${escapedRelPath}', true, event)" ` +
                `title="首页精选：普通稿件 (点击设为首页精选)">` +
                `☆ 精选</button>`
            );
        }

        // 3. 伴读播客详情页开关 (Podcast Pill - 仅对文档与博客页面有效)
        if (isDocOrBlog(m)) {
            const hasAudio = !!m.has_podcast_audio;
            const isPodcastExplicitlyOff = m.podcast === false;
            const isPodcastOn = (m.podcast === true) || (!isPodcastExplicitlyOff && hasAudio);

            if (isPodcastOn) {
                if (hasAudio) {
                    pills.push(
                        `<button type="button" class="vault-pill-badge pill-podcast active" ` +
                        `onclick="window.toggleVaultPodcast('${escapedRelPath}', false, event)" ` +
                        `title="详情页伴读播客：已开启且音频已就绪 (点击关闭详情页播放器)">` +
                        `<span class="pill-dot"></span>🎧 播客已开</button>`
                    );
                } else {
                    pills.push(
                        `<button type="button" class="vault-pill-badge pill-podcast pending" ` +
                        `onclick="window.toggleVaultPodcast('${escapedRelPath}', false, event)" ` +
                        `title="详情页伴读播客：已开启但尚未合成音频 (需在右侧操作【...】->【伴读工坊】合成后发布生效，点击关闭)">` +
                        `<span class="pill-dot"></span>🎙️ 待合成音频</button>`
                    );
                }
            } else {
                const offTitle = hasAudio
                    ? "详情页伴读播客：已关闭 (物理音频已存在，点击即可在详情页开启播放器)"
                    : "详情页伴读播客：已关闭 (点击开启，开启后需通过伴读工坊合成音频)";
                pills.push(
                    `<button type="button" class="vault-pill-badge pill-podcast disabled" ` +
                    `onclick="window.toggleVaultPodcast('${escapedRelPath}', true, event)" ` +
                    `title="${offTitle}">` +
                    `<span class="pill-dot"></span>🚫 播客已关</button>`
                );
            }
        }

        return pills.join('');
    };

    /**
     * 原子化轻量 Patch 原稿 Frontmatter 字段并同步文库与物理磁盘
     */
    window.patchDocumentFrontmatter = async function (relPath, patch, successMsg) {
        if (!relPath || !patch) return false;

        // 🚀 1. 乐观就地更新 (Optimistic In-Place Update)：零抖动、零骨架屏、零滚动跳顶
        const escapedPath = relPath.replace(/'/g, "\\'");
        const tr = document.querySelector(`#vault-list tr[data-rel-path="${escapedPath}"]`) ||
            Array.from(document.querySelectorAll('#vault-list tr')).find(r => r.getAttribute('data-rel-path') === relPath);
        const pillsRow = tr ? tr.querySelector('.vault-pills-row') : null;

        const cachedItem = (window.vaultCurrentManuscripts || []).find(m => m.rel_path === relPath);
        const prevValues = {};

        if (cachedItem) {
            for (const k in patch) {
                prevValues[k] = cachedItem[k];
                cachedItem[k] = patch[k];
            }
            if (pillsRow && typeof window.buildVaultPillsHtml === 'function') {
                pillsRow.innerHTML = window.buildVaultPillsHtml(cachedItem, escapedPath);
            }
        }

        try {
            const res = await apiFetch('/api/vault/patch-frontmatter', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rel_path: relPath, patch: patch })
            });
            if (res && res.success) {
                if (typeof window.showToast === 'function' && successMsg) {
                    window.showToast(successMsg, 'success');
                }
                // 🚀 后台静默保活同步，100% 保持当前滚动条位置
                if (typeof window.loadVault === 'function') {
                    window.loadVault(null, null, { keepScroll: true, silent: true });
                }
                return true;
            } else {
                // 回滚乐观更新
                if (cachedItem) {
                    for (const k in prevValues) cachedItem[k] = prevValues[k];
                    if (pillsRow && typeof window.buildVaultPillsHtml === 'function') {
                        pillsRow.innerHTML = window.buildVaultPillsHtml(cachedItem, escapedPath);
                    }
                }
                const err = (res && (res.detail || res.error || res.message)) || '操作失败';
                if (typeof window.showToast === 'function') window.showToast(`❌ ${err}`, 'error');
                return false;
            }
        } catch (e) {
            // 回滚乐观更新
            if (cachedItem) {
                for (const k in prevValues) cachedItem[k] = prevValues[k];
                if (pillsRow && typeof window.buildVaultPillsHtml === 'function') {
                    pillsRow.innerHTML = window.buildVaultPillsHtml(cachedItem, escapedPath);
                }
            }
            if (typeof window.showToast === 'function') window.showToast(`❌ 网络异常: ${e.message}`, 'error');
            return false;
        }
    };

    /**
     * 快捷切换详情页伴读播客开关
     */
    window.toggleVaultPodcast = async function (relPath, enable, event) {
        if (event) {
            event.stopPropagation();
            if (event.preventDefault) event.preventDefault();
        }
        const msg = enable
            ? '🎙️ 已开启伴读播客 (提示：若尚未合成音频，需在【伴读工坊】生成音频后发布生效)'
            : '🚫 已在该文稿详情页关闭伴读播客';
        await window.patchDocumentFrontmatter(relPath, { podcast: enable }, msg);
    };

    /**
     * 快捷切换文稿草稿状态
     */
    window.toggleVaultDraft = async function (relPath, makeDraft, event) {
        if (event) {
            event.stopPropagation();
            if (event.preventDefault) event.preventDefault();
        }
        const msg = makeDraft ? '🟡 已将文稿设为内部草稿' : '🟢 已将文稿设为正式发布状态';
        await window.patchDocumentFrontmatter(relPath, { draft: makeDraft }, msg);
    };

    /**
     * 快捷切换首页精选状态
     */
    window.toggleVaultFeatured = async function (relPath, makeFeatured, event) {
        if (event) {
            event.stopPropagation();
            if (event.preventDefault) event.preventDefault();
        }
        const msg = makeFeatured ? '⭐ 已将文稿设为首页精选' : '☆ 已取消文稿首页精选';
        await window.patchDocumentFrontmatter(relPath, { featured: makeFeatured }, msg);
    };
})();

