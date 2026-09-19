/**
 * 🎨 [V1.0] Illacme Plenipes System Settings - Granular Cache Hub Render Component
 * 职责：渲染系统设置中“存储适配”子面板下的“🧰 分层缓存与双轨容灾治理中枢 (Granular Cache Hub)”。
 * 对应重构拆分协议：SOP-01/SOP-02 模板一合规物理平移。
 */

(function () {
    'use strict';

    window.renderGranularCacheHub = function () {
        return `
            <div class="settings-group mt-large">
                <h4>🧰 分层缓存与双轨容灾治理中枢 (Granular Cache Hub)</h4>
                <p class="section-desc" style="font-size: 0.85rem; opacity: 0.85; margin-bottom: 16px;">细粒度独立管理大模型算力资产、文件指纹账本与构建产物缓存，支持 0 算力开销全量重编与物理冷备自愈。</p>
                
                <!-- 📊 状态盘点面板 -->
                <div style="background: rgba(0, 242, 255, 0.03); border: 1px solid var(--glass-border, rgba(255,255,255,0.08)); padding: 16px 20px; border-radius: 10px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="font-size: 1.3rem;">🧱</div>
                            <div>
                                <div style="font-size: 0.75rem; opacity: 0.75;">段落翻译缓存</div>
                                <div style="display: flex; gap: 8px; align-items: center;">
                                    <span style="font-size: 0.95rem; font-weight: bold; color: var(--accent-primary, #00f2ff);" id="cache-stats-count">正在统计...</span>
                                    <span style="opacity: 0.3;">/</span>
                                    <span style="font-size: 0.95rem; font-weight: bold; color: #00ff88;" id="cache-stats-size">正在统计...</span>
                                </div>
                            </div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="font-size: 1.3rem;">📂</div>
                            <div>
                                <div style="font-size: 0.75rem; opacity: 0.75;">物理元信息镜像</div>
                                <span style="font-size: 0.95rem; font-weight: bold; color: #ffb800;" id="cache-stats-meta-count">正在统计...</span>
                            </div>
                        </div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <div style="font-size: 1.3rem;">⚡</div>
                            <div>
                                <div style="font-size: 0.75rem; opacity: 0.75;">构建与镜像产物</div>
                                <span style="font-size: 0.95rem; font-weight: bold; color: #a371f7;" id="cache-stats-build-size">正在统计...</span>
                            </div>
                        </div>
                    </div>
                    <button type="button" class="sub-tab-btn" onclick="window.refreshCacheStats()" style="padding: 6px 14px; font-size: 0.75rem; white-space: nowrap; word-break: keep-all;">🔄 重新盘点</button>
                </div>

                <!-- 🛠️ 分层功能操作网格 (2列 x 3排 黄金比例布局) -->
                <div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px;">
                    <!-- 第一排-左：0 算力开销仅重置指纹 -->
                    <div style="background: rgba(0, 242, 255, 0.03); border: 1px solid rgba(0, 242, 255, 0.22); padding: 14px; border-radius: 10px; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; box-shadow: 0 4px 16px rgba(0, 242, 255, 0.04);">
                        <div>
                            <div style="display: flex; align-items: center; justify-content: space-between; gap: 6px; margin-bottom: 8px;">
                                <span style="font-size: 0.86rem; font-weight: 600; color: #00f2ff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 5px;">⚡ 仅重置增量指纹</span>
                                <span class="badge" style="font-size: 0.65rem; background: rgba(0,242,255,0.12); color: #00f2ff; border: 1px solid rgba(0,242,255,0.3); padding: 1px 6px; border-radius: 4px; white-space: nowrap; flex-shrink: 0; font-weight: 500;">0 算力开销</span>
                            </div>
                            <p style="font-size: 0.77rem; opacity: 0.85; line-height: 1.4; margin: 0; color: var(--text-bright, #e0e6ed);">清空文件指纹解除跳过限制。<b>正文译文、AI别名/SEO及拓扑元数据完整保留</b>，下次发布 0 算力全速重新组装。</p>
                        </div>
                        <button type="button" class="primary-btn glow-btn" onclick="event.preventDefault(); event.stopPropagation(); window.resetFingerprintsOnly()" style="padding: 6px 12px; font-size: 0.78rem; height: 32px; width: 100%; justify-content: center; font-weight: 500;">⚡ 仅重置指纹</button>
                    </div>

                    <!-- 第一排-右：物理快照自愈重建账本 -->
                    <div style="background: rgba(0, 255, 136, 0.025); border: 1px solid rgba(0, 255, 136, 0.22); padding: 14px; border-radius: 10px; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; box-shadow: 0 4px 16px rgba(0, 255, 136, 0.04);">
                        <div>
                            <div style="display: flex; align-items: center; justify-content: space-between; gap: 6px; margin-bottom: 8px;">
                                <span style="font-size: 0.86rem; font-weight: 600; color: #00ff88; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 5px;">🩹 物理快照自愈</span>
                                <span class="badge" style="font-size: 0.65rem; background: rgba(0,255,136,0.12); color: #00ff88; border: 1px solid rgba(0,255,136,0.3); padding: 1px 6px; border-radius: 4px; white-space: nowrap; flex-shrink: 0; font-weight: 500;">冷备自愈</span>
                            </div>
                            <p style="font-size: 0.77rem; opacity: 0.85; line-height: 1.4; margin: 0; color: var(--text-bright, #e0e6ed);">从本地 <code>cache/metadata/</code> 镜像无损恢复 SQLite 账本。<b>0 算力开销</b>，秒级还原历史沉淀的全部元数据。</p>
                        </div>
                        <button type="button" class="sub-tab-btn" onclick="event.preventDefault(); event.stopPropagation(); window.rebuildLedgerFromCache()" style="padding: 6px 12px; font-size: 0.78rem; height: 32px; width: 100%; justify-content: center; border-color: rgba(0,255,136,0.4); color: #00ff88; font-weight: 500;">🩹 自愈重建账本</button>
                    </div>

                    <!-- 第二排-左：清空段落翻译缓存 -->
                    <div style="background: rgba(255, 184, 0, 0.025); border: 1px solid rgba(255, 184, 0, 0.22); padding: 14px; border-radius: 10px; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; box-shadow: 0 4px 16px rgba(255, 184, 0, 0.04);">
                        <div>
                            <div style="display: flex; align-items: center; justify-content: space-between; gap: 6px; margin-bottom: 8px;">
                                <span style="font-size: 0.86rem; font-weight: 600; color: #ffb800; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 5px;">🧱 清空段落翻译</span>
                                <span class="badge" style="font-size: 0.65rem; background: rgba(255,184,0,0.12); color: #ffb800; border: 1px solid rgba(255,184,0,0.3); padding: 1px 6px; border-radius: 4px; white-space: nowrap; flex-shrink: 0; font-weight: 500;">正文重译</span>
                            </div>
                            <p style="font-size: 0.77rem; opacity: 0.85; line-height: 1.4; margin: 0; color: var(--text-bright, #e0e6ed);">物理清空 <code>cache/blocks/</code> 文本库。<b>下次发布时各段落将重新调用大模型翻译</b>（耗费 Token 与时间）。</p>
                        </div>
                        <button type="button" class="danger-btn" onclick="event.preventDefault(); event.stopPropagation(); window.clearBlockCacheAll()" style="padding: 6px 12px; font-size: 0.78rem; height: 32px; width: 100%; justify-content: center; font-weight: 500;">🧱 清空段落缓存</button>
                    </div>

                    <!-- 第二排-右：重置 AI 元数据缓存 -->
                    <div style="background: rgba(163, 113, 247, 0.025); border: 1px solid rgba(163, 113, 247, 0.22); padding: 14px; border-radius: 10px; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; box-shadow: 0 4px 16px rgba(163, 113, 247, 0.04);">
                        <div>
                            <div style="display: flex; align-items: center; justify-content: space-between; gap: 6px; margin-bottom: 8px;">
                                <span style="font-size: 0.86rem; font-weight: 600; color: #a371f7; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 5px;">🏷️ 重置 AI 元数据</span>
                                <span class="badge" style="font-size: 0.65rem; background: rgba(163,113,247,0.12); color: #a371f7; border: 1px solid rgba(163,113,247,0.3); padding: 1px 6px; border-radius: 4px; white-space: nowrap; flex-shrink: 0; font-weight: 500;">元数据重塑</span>
                            </div>
                            <p style="font-size: 0.77rem; opacity: 0.85; line-height: 1.4; margin: 0; color: var(--text-bright, #e0e6ed);">仅清空 AI 衍生的网址别名与 SEO 摘要。<b>正文段落译文完好保留</b>，下次发布仅重新推导这些元数据。</p>
                        </div>
                        <button type="button" class="sub-tab-btn" onclick="event.preventDefault(); event.stopPropagation(); window.clearAIMetadataCache()" style="padding: 6px 12px; font-size: 0.78rem; height: 32px; width: 100%; justify-content: center; border-color: rgba(163,113,247,0.4); color: #a371f7; font-weight: 500;">🏷️ 重置 AI 元数据</button>
                    </div>

                    <!-- 第三排-左：清理构建与源码镜像缓存 -->
                    <div style="background: rgba(136, 164, 230, 0.025); border: 1px solid rgba(136, 164, 230, 0.22); padding: 14px; border-radius: 10px; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; box-shadow: 0 4px 16px rgba(136, 164, 230, 0.04);">
                        <div>
                            <div style="display: flex; align-items: center; justify-content: space-between; gap: 6px; margin-bottom: 8px;">
                                <span style="font-size: 0.86rem; font-weight: 600; color: #88a4e6; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 5px;">🧹 清理构建产物</span>
                                <span class="badge" style="font-size: 0.65rem; background: rgba(136,164,230,0.12); color: #88a4e6; border: 1px solid rgba(136,164,230,0.3); padding: 1px 6px; border-radius: 4px; white-space: nowrap; flex-shrink: 0; font-weight: 500;">构建排障</span>
                            </div>
                            <p style="font-size: 0.77rem; opacity: 0.85; line-height: 1.4; margin: 0; color: var(--text-bright, #e0e6ed);">清理 <code>cache/sources/</code> 与 <code>build/</code> 遗留编译产物。<b>不影响任何 AI 译文、元数据或指纹账本</b>。</p>
                        </div>
                        <button type="button" class="sub-tab-btn" onclick="event.preventDefault(); event.stopPropagation(); window.clearBuildCache()" style="padding: 6px 12px; font-size: 0.78rem; height: 32px; width: 100%; justify-content: center; border-color: rgba(136,164,230,0.4); color: #88a4e6; font-weight: 500;">🧹 清理构建产物</button>
                    </div>

                    <!-- 第三排-右：全量归零重置 -->
                    <div style="background: rgba(255, 77, 77, 0.025); border: 1px solid rgba(255, 77, 77, 0.22); padding: 14px; border-radius: 10px; display: flex; flex-direction: column; justify-content: space-between; gap: 12px; box-shadow: 0 4px 16px rgba(255, 77, 77, 0.04);">
                        <div>
                            <div style="display: flex; align-items: center; justify-content: space-between; gap: 6px; margin-bottom: 8px;">
                                <span style="font-size: 0.86rem; font-weight: 600; color: #ff4d4d; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: flex; align-items: center; gap: 5px;">💣 彻底清空账本</span>
                                <span class="badge" style="font-size: 0.65rem; background: rgba(255,77,77,0.12); color: #ff4d4d; border: 1px solid rgba(255,77,77,0.3); padding: 1px 6px; border-radius: 4px; white-space: nowrap; flex-shrink: 0; font-weight: 500;">账本归零</span>
                            </div>
                            <p style="font-size: 0.77rem; opacity: 0.85; line-height: 1.4; margin: 0; color: var(--text-bright, #e0e6ed);">清空 SQLite 账本与元信息镜像。<b>段落翻译缓存（Block Cache）与原稿文件完好保留</b>，但元数据需重新扫描建立。</p>
                        </div>
                        <button type="button" class="danger-btn" onclick="event.preventDefault(); event.stopPropagation(); window.resetLedgerOnly()" style="padding: 6px 12px; font-size: 0.78rem; height: 32px; width: 100%; justify-content: center; font-weight: 500;">💣 清空文档账本</button>
                    </div>
                </div>
            </div>
        `;
    };
})();
