/**
 * 🎙️ [V1.0] Illacme Plenipes Plugins - Podcast Platforms Configuration Shard
 * 职责：渲染全网播客发行枢纽 (Podcast Hub)、小宇宙 (Xiaoyuzhou)、Apple Podcasts、Spotify 配置抽屉与向导。
 * 🛡️ [SOP-01] 物理行数严格收敛于 300 行以内。
 */

var renderSettingsItem = window.renderSettingsItem || (() => "");

window.copyPodcastFeedUrl = function (btn) {
    const feedUrl = `${(window.location && window.location.origin) || ''}/api/podcast/feed/${window.currentImprintId || 'default'}?lang=zh`;
    navigator.clipboard?.writeText(feedUrl).then(() => {
        if (typeof window.showToast === 'function') window.showToast('📋 标准播客 RSS 2.0 订阅链接已复制至剪贴板！', 'success');
        if (btn) { const orig = btn.innerText; btn.innerText = '✅ 已复制'; setTimeout(() => { btn.innerText = orig; }, 1800); }
    });
};

window.renderPodcastPlatformConfig = (id, cfg = {}) => {
    const origin = (window.location && window.location.origin) ? window.location.origin : '';
    const activeImprint = window.currentImprintId || 'default';
    const feedUrl = `${origin}/api/podcast/feed/${activeImprint}?lang=zh`;

    if (id === 'podcast_tts_engines') {
        const grp = (title, open, body) => `<details ${open ? 'open' : ''} style="margin-bottom:10px;border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:8px 12px;background:rgba(255,255,255,0.02);"><summary style="cursor:pointer;font-size:0.84rem;font-weight:600;color:#e2e8f0;">${title}</summary><div style="margin-top:8px;">${body}</div></details>`;
        return `
            <div class="api-token-helper" style="margin-bottom: 14px; padding: 12px 14px; border-radius: 10px; border: 1px dashed rgba(168, 85, 247, 0.4); background: rgba(168, 85, 247, 0.05);">
                <h4 style="margin: 0; color: #c084fc;">🎙️ 播客语音合成引擎配置 (按引擎分组)</h4>
                <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: var(--text-dim);">默认使用 <b>Edge TTS (免费免配)</b>；展开对应引擎按需填写凭据即可。</p>
            </div>
            ${renderSettingsItem('默认语音引擎', 'podcast.podcast_tts_engines.default_provider', cfg.default_provider || 'edge', 'select', { options: [{ value: 'edge', label: 'Edge TTS (免费免配)' }, { value: 'openai', label: 'OpenAI TTS' }, { value: 'elevenlabs', label: 'ElevenLabs' }, { value: 'fish_audio', label: 'Fish Audio' }, { value: 'cosyvoice', label: '本地 CosyVoice / 克隆' }] })}
            ${grp('🤖 OpenAI TTS', cfg.default_provider === 'openai', renderSettingsItem('API Key', 'podcast.podcast_tts_engines.openai_api_key', cfg.openai_api_key || '', 'password', { placeholder: 'sk-...' }) + renderSettingsItem('Base URL', 'podcast.podcast_tts_engines.openai_base_url', cfg.openai_base_url || 'https://api.openai.com/v1', 'text'))}
            ${grp('✨ ElevenLabs', cfg.default_provider === 'elevenlabs', renderSettingsItem('API Key', 'podcast.podcast_tts_engines.elevenlabs_api_key', cfg.elevenlabs_api_key || '', 'password', { placeholder: 'xi-api-key...' }) + renderSettingsItem('主讲 Voice ID (女)', 'podcast.podcast_tts_engines.elevenlabs_voice_a', cfg.elevenlabs_voice_a || '', 'text') + renderSettingsItem('搭档 Voice ID (男)', 'podcast.podcast_tts_engines.elevenlabs_voice_b', cfg.elevenlabs_voice_b || '', 'text'))}
            ${grp('🐟 Fish Audio', cfg.default_provider === 'fish_audio', renderSettingsItem('API Key', 'podcast.podcast_tts_engines.fish_audio_api_key', cfg.fish_audio_api_key || '', 'password') + renderSettingsItem('参考音色 ID A', 'podcast.podcast_tts_engines.fish_audio_ref_a', cfg.fish_audio_ref_a || '', 'text') + renderSettingsItem('参考音色 ID B', 'podcast.podcast_tts_engines.fish_audio_ref_b', cfg.fish_audio_ref_b || '', 'text'))}
            ${grp('🏠 本地 CosyVoice / 克隆', cfg.default_provider === 'cosyvoice', renderSettingsItem('服务地址 (Base URL)', 'podcast.podcast_tts_engines.cosyvoice_base_url', cfg.cosyvoice_base_url || 'http://127.0.0.1:9880/v1', 'text'))}
        `;
    }

    if (id === 'podcast_hub') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 14px; border-radius: 10px; border: 1px dashed rgba(168, 85, 247, 0.4); background: rgba(168, 85, 247, 0.05);">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <h4 style="margin: 0; color: #c084fc; display: flex; align-items: center; gap: 6px;">
                            <span>🎙️</span> 播客全网发行 RSS 2.0 枢纽 (Zero-Config)
                        </h4>
                        <p style="margin: 4px 0 0 0; font-size: 0.82rem; color: var(--text-dim); line-height: 1.4;">
                            基于标准 RSS 2.0 与 Apple iTunes 播客命名空间，向全球播客客户端提供标准音频流。
                        </p>
                    </div>
                    <button type="button" class="mini-btn glow-btn" onclick="window.copyPodcastFeedUrl(this)" style="background: linear-gradient(135deg, #a855f7, #6366f1); color: #fff; padding: 4px 12px; font-size: 0.78rem;">
                        📋 复制本站 RSS 订阅流
                    </button>
                </div>
                <div style="margin-top: 10px; padding: 8px 12px; background: rgba(0,0,0,0.3); border-radius: 6px; font-size: 0.76rem; color: #94a3b8; word-break: break-all; border: 1px solid rgba(255,255,255,0.06);">
                    <span style="color: #c084fc; font-weight: 600;">Feed 地址：</span><code>${feedUrl}</code>
                </div>
                <div style="margin-top: 10px; display: flex; gap: 8px; flex-wrap: wrap;">
                    <a href="https://podcastsconnect.apple.com" target="_blank" rel="noopener" class="mini-btn" style="background: rgba(255,255,255,0.06); font-size: 0.72rem; text-decoration: none; color: #e2e8f0; display: inline-flex; align-items: center; gap: 4px;">
                        🍏 提交至 Apple Podcasts
                    </a>
                    <a href="https://podcasters.spotify.com" target="_blank" rel="noopener" class="mini-btn" style="background: rgba(255,255,255,0.06); font-size: 0.72rem; text-decoration: none; color: #e2e8f0; display: inline-flex; align-items: center; gap: 4px;">
                        🟢 认领至 Spotify
                    </a>
                    <a href="https://podcaster.xiaoyuzhoufm.com" target="_blank" rel="noopener" class="mini-btn" style="background: rgba(255,255,255,0.06); font-size: 0.72rem; text-decoration: none; color: #e2e8f0; display: inline-flex; align-items: center; gap: 4px;">
                        🪐 导入至小宇宙
                    </a>
                </div>
            </div>
            ${renderSettingsItem('播客专辑标题 (Show Title)', 'podcast.podcast_hub.title', cfg.title || '', 'text', { placeholder: "例如: 创作者指南 · 技术对谈", description: "播客在 Apple Podcasts / Spotify / 小宇宙等全网客户端展示的总专辑名称。" })}
            ${renderSettingsItem('专辑总简介 (Show Notes)', 'podcast.podcast_hub.description', cfg.description || '', 'textarea', { placeholder: "介绍本播客的核心主旨、涉猎领域与更新频率...", description: "播客频道的全局介绍文本，会被各大客户端索引为节目总括。" })}
            ${renderSettingsItem('主播/团队名称 (Author)', 'podcast.podcast_hub.author', cfg.author || '', 'text', { placeholder: "例如: Illacme Plenipes Team", description: "节目制作人或出版机构署名。" })}
            ${renderSettingsItem('官方所有者邮箱 (Owner Email)', 'podcast.podcast_hub.email', cfg.email || '', 'text', { placeholder: "podcast@yourdomain.com", description: "Apple Podcasts Connect 与 Spotify 认领所有权验证时所需的联络邮箱。" })}
            ${renderSettingsItem('iTunes 官方大分类 (Category)', 'podcast.podcast_hub.category', cfg.category || 'Technology', 'select', {
                options: [
                    { value: 'Technology', label: 'Technology (科技/互联网)' },
                    { value: 'Education', label: 'Education (教育/知识)' },
                    { value: 'News', label: 'News (资讯/快讯)' },
                    { value: 'Business', label: 'Business (商业/创业)' },
                    { value: 'Science', label: 'Science (科学/工程)' },
                    { value: 'Arts', label: 'Arts (艺术/设计)' }
                ],
                description: "符合 Apple Podcasts 国际标准一级分类目录。"
            })}
            ${renderSettingsItem('iTunes 官方子分类 (Sub-Category)', 'podcast.podcast_hub.sub_category', cfg.sub_category || 'Software How-To', 'select', {
                options: [
                    { value: 'Software How-To', label: 'Software How-To (软件开发与架构)' },
                    { value: 'Tech News', label: 'Tech News (科技动态)' },
                    { value: 'Courses', label: 'Courses (深度课程)' },
                    { value: 'Careers', label: 'Careers (职场与实践)' }
                ],
                description: "符合 Apple Podcasts 国际标准二级子分类。"
            })}
            ${renderSettingsItem('播客主视觉封面图 (Cover Art)', 'podcast.podcast_hub.cover_url', cfg.cover_url || '', 'text', { placeholder: "https://.../podcast-cover.jpg", description: "建议尺寸为 3000×3000 像素的正方形高清图片 (JPG/PNG)，各大平台强校验此标准。" })}
            ${renderSettingsItem('敏感内容标识 (Explicit Content)', 'podcast.podcast_hub.explicit', !!cfg.explicit, 'checkbox', { description: "勾选后将在 RSS 标记 itunes:explicit，若含有成人/敏感言论需开启合规标示。" })}
        `;
    }

    if (id === 'podcast_xiaoyuzhou') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 14px; border-radius: 10px; border: 1px dashed rgba(56, 189, 248, 0.4); background: rgba(56, 189, 248, 0.05);">
                <h4 style="margin: 0; color: #38bdf8;">🪐 小宇宙 Studio 极简分发向导</h4>
                <p style="margin: 4px 0 0 0; font-size: 0.82rem; color: var(--text-dim); line-height: 1.4;">
                    国内领先的中文播客社区。可直接将本站 RSS 地址导入小宇宙创作者后台，或配置 Token 开启单集同步。
                </p>
                <div style="margin-top: 10px;">
                    <a href="https://podcaster.xiaoyuzhoufm.com" target="_blank" rel="noopener" class="mini-btn glow-btn" style="background: #0284c7; color: #fff; font-size: 0.78rem; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;">
                        🔗 前往小宇宙创作者后台 (Xiaoyuzhou Studio)
                    </a>
                </div>
            </div>
            ${renderSettingsItem('启用小宇宙通道', 'podcast.podcast_xiaoyuzhou.enabled', !!cfg.enabled, 'checkbox', { description: "激活小宇宙播客分发能力。" })}
            ${renderSettingsItem('小宇宙节目 ID (Podcast ID)', 'podcast.podcast_xiaoyuzhou.podcast_id', cfg.podcast_id || '', 'text', { placeholder: "例如: 63f123456789...", description: "在小宇宙创作者后台 URL 中获取的节目唯一 ID。" })}
            ${renderSettingsItem('创作者凭证 (Auth Token / Cookie)', 'podcast.podcast_xiaoyuzhou.token', cfg.token || '', 'password', { placeholder: "小宇宙后台 Cookie 或开放平台 Token", description: "用于自动化同步单集 Show Notes 与时间戳。" })}
            ${renderSettingsItem('单集 Show Notes 自动同步', 'podcast.podcast_xiaoyuzhou.sync_shownotes', cfg.sync_shownotes !== false, 'checkbox', { description: "在合成技术播客时，自动将双人对谈纲要同步为小宇宙单集介绍。" })}
        `;
    }

    if (id === 'podcast_apple') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 14px; border-radius: 10px; border: 1px dashed rgba(255, 255, 255, 0.3); background: rgba(255, 255, 255, 0.04);">
                <h4 style="margin: 0; color: #f8fafc;">🍏 Apple Podcasts Connect 提交向导</h4>
                <p style="margin: 4px 0 0 0; font-size: 0.82rem; color: var(--text-dim); line-height: 1.4;">
                    全球基准播客索引目录。提交至 Apple Podcasts 后，Overcast、Pocket Casts、Castro 等各大播客客户端将全自动收录。
                </p>
                <div style="margin-top: 10px;">
                    <a href="https://podcastsconnect.apple.com" target="_blank" rel="noopener" class="mini-btn" style="background: rgba(255,255,255,0.12); color: #fff; font-size: 0.78rem; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;">
                        🔗 前往 Apple Podcasts Connect 提交 RSS
                    </a>
                </div>
            </div>
            ${renderSettingsItem('启用 Apple Podcasts 渠道', 'podcast.podcast_apple.enabled', !!cfg.enabled, 'checkbox', { description: "激活 Apple Podcasts 分发状态追踪。" })}
            ${renderSettingsItem('Apple 节目编号 (Apple ID)', 'podcast.podcast_apple.apple_id', cfg.apple_id || '', 'text', { placeholder: "例如: 1688899999", description: "过审后 Apple Podcasts 分配的 10 位数字节目 ID。" })}
            ${renderSettingsItem('节目公开主页 (Podcast URL)', 'podcast.podcast_apple.podcast_url', cfg.podcast_url || '', 'text', { placeholder: "https://podcasts.apple.com/podcast/id...", description: "Apple Podcasts 公开收听主页直达链接。" })}
        `;
    }

    if (id === 'podcast_r2_storage') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 14px; border-radius: 10px; border: 1px dashed rgba(249, 115, 22, 0.4); background: rgba(249, 115, 22, 0.05);">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <h4 style="margin: 0; color: #fb923c;">☁️ 播客专有音频 CDN 托管 (Cloudflare R2 / S3)</h4>
                        <p style="margin: 4px 0 0 0; font-size: 0.82rem; color: var(--text-dim); line-height: 1.4;">
                            专为高码率技术播客单轨 MP3 设计。首选 Cloudflare R2，享 0 出口流量费与全网边缘缓存加速。
                        </p>
                    </div>
                    <a href="https://dash.cloudflare.com/?to=/:account/r2" target="_blank" rel="noopener" class="mini-btn glow-btn" style="background: #ea580c; color: #fff; font-size: 0.78rem; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;">
                        🔑 获取 R2 API 凭证
                    </a>
                </div>
            </div>
            ${renderSettingsItem('启用专有音频 CDN 托管', 'podcast.podcast_r2_storage.enabled', !!cfg.enabled, 'checkbox', { description: "激活后，生成的 RSS 订阅流与播放器音频链接将自动替换为全球 CDN 域名。" })}
            ${renderSettingsItem('云存储服务商 (Provider)', 'podcast.podcast_r2_storage.provider', cfg.provider || 'cloudflare_r2', 'select', {
                options: [
                    { value: 'cloudflare_r2', label: 'Cloudflare R2 (推荐 · 0 出口流量费)' },
                    { value: 'aws_s3', label: 'Amazon AWS S3' },
                    { value: 'tencent_cos', label: '腾讯云 COS' },
                    { value: 'aliyun_oss', label: '阿里云 OSS' },
                    { value: 'custom_s3', label: '自建 MinIO / 自定义 S3' }
                ],
                description: "存储服务商协议类型。"
            })}
            ${renderSettingsItem('存储桶名称 (Bucket Name)', 'podcast.podcast_r2_storage.bucket', cfg.bucket || '', 'text', { placeholder: "例如: my-podcast-bucket", description: "用于存放播客音频 MP3 的专有存储桶名称。" })}
            ${renderSettingsItem('Cloudflare 账户 ID (Account ID)', 'podcast.podcast_r2_storage.account_id', cfg.account_id || '', 'text', { placeholder: "例如: a1b2c3d4e5f6...", description: "使用 Cloudflare R2 时必填，系统据此自动合成端点地址。" })}
            ${renderSettingsItem('访问密钥 ID (Access Key ID)', 'podcast.podcast_r2_storage.access_key_id', cfg.access_key_id || cfg.access_key || '', 'text', { placeholder: "R2 或 S3 访问密钥 ID", description: "具有该存储桶读写权限的凭据公钥。" })}
            ${renderSettingsItem('安全私钥 (Secret Access Key)', 'podcast.podcast_r2_storage.secret_access_key', cfg.secret_access_key || cfg.secret_key || '', 'password', { placeholder: "R2 或 S3 访问密钥私钥", description: "用于签名文件上传请求的安全私钥。" })}
            ${renderSettingsItem('公开加速域名 (Public CDN Base URL)', 'podcast.podcast_r2_storage.public_cdn_url', cfg.public_cdn_url || '', 'text', { placeholder: "例如: https://audio.yourdomain.com", description: "存储桶绑定的公开域名或 CDN 加速域名（末尾不带斜杠）。" })}
            ${renderSettingsItem('存储路径前缀 (Path Prefix)', 'podcast.podcast_r2_storage.path_prefix', cfg.path_prefix || 'podcasts', 'text', { placeholder: "例如: podcasts", description: "文件上传至存储桶时的子目录名称。" })}
            ${renderSettingsItem('音频合成后自动转储', 'podcast.podcast_r2_storage.auto_offload', cfg.auto_offload !== false, 'checkbox', { description: "勾选后，播客工坊每次合成完音频将自动推向云端存储桶。" })}
        `;
    }

    if (id === 'podcast_spotify') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 14px; border-radius: 10px; border: 1px dashed rgba(34, 197, 94, 0.4); background: rgba(34, 197, 94, 0.05);">
                <h4 style="margin: 0; color: #4ade80;">🟢 Spotify for Podcasters 认领向导</h4>
                <p style="margin: 4px 0 0 0; font-size: 0.82rem; color: var(--text-dim); line-height: 1.4;">
                    覆盖全球 Spotify 用户的流媒体音频网络。在 Spotify 创作者平台填入本站 RSS 地址即可完成一键认领。
                </p>
                <div style="margin-top: 10px;">
                    <a href="https://podcasters.spotify.com" target="_blank" rel="noopener" class="mini-btn glow-btn" style="background: #16a34a; color: #fff; font-size: 0.78rem; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;">
                        🔗 前往 Spotify for Podcasters 认领节目
                    </a>
                </div>
            </div>
            ${renderSettingsItem('启用 Spotify 渠道', 'podcast.podcast_spotify.enabled', !!cfg.enabled, 'checkbox', { description: "激活 Spotify 分发状态追踪。" })}
            ${renderSettingsItem('Spotify 节目编号 (Show ID)', 'podcast.podcast_spotify.show_id', cfg.show_id || '', 'text', { placeholder: "例如: 4rOoJ6Egrf8K...", description: "Spotify 分配的 22 位节目唯一识别码。" })}
            ${renderSettingsItem('节目公开主页 (Show URL)', 'podcast.podcast_spotify.show_url', cfg.show_url || '', 'text', { placeholder: "https://open.spotify.com/show/...", description: "Spotify 公开收听主页直达链接。" })}
        `;
    }

    if (id === 'podcast_youtube') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 14px; border-radius: 10px; border: 1px dashed rgba(239, 68, 68, 0.4); background: rgba(239, 68, 68, 0.05);">
                <h4 style="margin: 0; color: #f87171;">▶️ YouTube Podcasts (Studio) 绑定向导</h4>
                <p style="margin: 4px 0 0 0; font-size: 0.82rem; color: var(--text-dim); line-height: 1.4;">
                    Google 官方主力播客网络。在 YouTube Studio 中选择「新建播客 -> 提交 RSS 源」，即可全自动将每期音频与封面转为播客视频列表。
                </p>
                <div style="margin-top: 10px;">
                    <a href="https://studio.youtube.com" target="_blank" rel="noopener" class="mini-btn glow-btn" style="background: #dc2626; color: #fff; font-size: 0.78rem; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;">
                        🔗 前往 YouTube Studio 绑定 RSS
                    </a>
                </div>
            </div>
            ${renderSettingsItem('启用 YouTube Podcasts 渠道', 'podcast.podcast_youtube.enabled', !!cfg.enabled, 'checkbox', { description: "激活 YouTube Podcasts 分发状态追踪。" })}
            ${renderSettingsItem('播客播放列表 ID (Playlist ID)', 'podcast.podcast_youtube.playlist_id', cfg.playlist_id || '', 'text', { placeholder: "例如: PLxxxxxxxxxxxx", description: "YouTube 自动创建的播客专属播放列表 ID。" })}
            ${renderSettingsItem('节目公开主页 (Podcast URL)', 'podcast.podcast_youtube.podcast_url', cfg.podcast_url || '', 'text', { placeholder: "https://www.youtube.com/playlist?list=...", description: "YouTube Podcasts 公开收听播放列表链接。" })}
        `;
    }

    if (id === 'podcast_netease') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 14px; border-radius: 10px; border: 1px dashed rgba(225, 29, 72, 0.4); background: rgba(225, 29, 72, 0.05);">
                <h4 style="margin: 0; color: #fb7185;">🎵 网易云音乐播客 (创作者中心) 认领向导</h4>
                <p style="margin: 4px 0 0 0; font-size: 0.82rem; color: var(--text-dim); line-height: 1.4;">
                    国内年轻一代与技术人文核心音频阵地。在网易云音乐创作者中心选择「主播电台 -> RSS 托管认领」，填入本站 RSS 源即可自动同步更新。
                </p>
                <div style="margin-top: 10px;">
                    <a href="https://music.163.com/st/creator" target="_blank" rel="noopener" class="mini-btn glow-btn" style="background: #e11d48; color: #fff; font-size: 0.78rem; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;">
                        🔗 前往网易云音乐创作者中心
                    </a>
                </div>
            </div>
            ${renderSettingsItem('启用网易云音乐播客', 'podcast.podcast_netease.enabled', !!cfg.enabled, 'checkbox', { description: "激活网易云音乐播客分发通道。" })}
            ${renderSettingsItem('网易云播客电台 ID (Radio ID)', 'podcast.podcast_netease.radio_id', cfg.radio_id || '', 'text', { placeholder: "例如: 796001234", description: "网易云音乐分配的播客电台唯一数字编号。" })}
            ${renderSettingsItem('创作者凭证 (Cookie / Token)', 'podcast.podcast_netease.token', cfg.token || '', 'password', { placeholder: "可选：MUSIC_U Cookie 或开放凭证", description: "用于状态核验与单集介绍同步（RSS 托管模式下可选填）。" })}
        `;
    }

    if (id === 'podcast_ximalaya') {
        return `
            <div class="api-token-helper" style="margin-bottom: 16px; padding: 14px; border-radius: 10px; border: 1px dashed rgba(249, 115, 22, 0.4); background: rgba(249, 115, 22, 0.05);">
                <h4 style="margin: 0; color: #fb923c;">📻 喜马拉雅 (主播工作台) 接入向导</h4>
                <p style="margin: 4px 0 0 0; font-size: 0.82rem; color: var(--text-dim); line-height: 1.4;">
                    国内综合体量最大的音频流媒体网络。支持在喜马拉雅主播工作台创建有声专辑并通过 RSS 订阅源或音频直传分发。
                </p>
                <div style="margin-top: 10px;">
                    <a href="https://studio.ximalaya.com" target="_blank" rel="noopener" class="mini-btn glow-btn" style="background: #ea580c; color: #fff; font-size: 0.78rem; text-decoration: none; display: inline-flex; align-items: center; gap: 4px;">
                        🔗 前往喜马拉雅主播工作台
                    </a>
                </div>
            </div>
            ${renderSettingsItem('启用喜马拉雅渠道', 'podcast.podcast_ximalaya.enabled', !!cfg.enabled, 'checkbox', { description: "激活喜马拉雅播客专辑分发追踪。" })}
            ${renderSettingsItem('喜马拉雅专辑 ID (Album ID)', 'podcast.podcast_ximalaya.album_id', cfg.album_id || '', 'text', { placeholder: "例如: 51234567", description: "喜马拉雅主播后台分配的专辑唯一 ID。" })}
            ${renderSettingsItem('创作者凭证 (Cookie / Token)', 'podcast.podcast_ximalaya.token', cfg.token || '', 'password', { placeholder: "可选：喜马拉雅创作者授权 Cookie", description: "用于专辑状态追踪与 Show Notes 同步。" })}
        `;
    }

    return '';
};

const _TTS_ENGINE_FIELDS = {
    openai: [['openai_api_key', 'OpenAI API Key', 'password', 'sk-...'], ['openai_base_url', 'Base URL', 'text', 'https://api.openai.com/v1']],
    elevenlabs: [['elevenlabs_api_key', 'ElevenLabs API Key', 'password', 'xi-api-key...'], ['elevenlabs_voice_a', '主讲 Voice ID (女)', 'text', '可选'], ['elevenlabs_voice_b', '搭档 Voice ID (男)', 'text', '可选']],
    fish_audio: [['fish_audio_api_key', 'Fish Audio API Key', 'password', 'Token...'], ['fish_audio_ref_a', '参考音色 ID A', 'text', '可选'], ['fish_audio_ref_b', '参考音色 ID B', 'text', '可选']],
    cosyvoice: [['cosyvoice_base_url', 'CosyVoice 服务地址', 'text', 'http://127.0.0.1:9880/v1']]
};

window.refreshPodcastInlineEngineConfig = function (provider) {
    const panel = document.getElementById('podcast-engine-inline-config');
    if (!panel || panel.style.display === 'none') return;
    const p = provider || (document.getElementById('podcast-tts-provider') || {}).value || 'edge';
    const fields = _TTS_ENGINE_FIELDS[p];
    const tCfg = (((window.settingsData || {}).podcast || {}).podcast_tts_engines) || {};
    if (!fields) {
        panel.innerHTML = `<div style="display:flex;align-items:center;justify-content:space-between;gap:8px;"><span style="font-size:0.78rem;color:#94a3b8;">✅ <b>Edge TTS</b> 为免费免配神经语音引擎，无需填写密钥，开箱即用。</span><button type="button" class="mini-btn" onclick="window.togglePodcastInlineEngineConfig()" style="font-size:0.74rem;">收起</button></div>`;
        return;
    }
    const inputs = fields.map(([k, lbl, tp, ph]) => `<label style="display:flex;flex-direction:column;gap:3px;min-width:170px;flex:1;"><span style="font-size:0.7rem;color:#94a3b8;">${lbl}</span><input data-tts-key="${k}" type="${tp}" value="${String(tCfg[k] || '').replace(/"/g, '&quot;')}" placeholder="${ph || ''}" style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.14);border-radius:6px;padding:5px 8px;color:#f8fafc;font-size:0.76rem;"></label>`).join('');
    panel.innerHTML = `<div style="display:flex;flex-wrap:wrap;gap:8px;align-items:flex-end;">${inputs}<button type="button" class="mini-btn glow-btn" onclick="window.savePodcastInlineEngineConfig('${p}')" style="background:#8b5cf6;color:#fff;padding:5px 12px;font-size:0.75rem;">💾 保存配置</button><button type="button" class="mini-btn" onclick="window.togglePodcastInlineEngineConfig()" style="padding:5px 10px;font-size:0.75rem;">收起</button></div>`;
};

window.togglePodcastInlineEngineConfig = function () {
    const panel = document.getElementById('podcast-engine-inline-config');
    if (!panel) return;
    const isHidden = panel.style.display === 'none' || !panel.style.display;
    panel.style.display = isHidden ? 'block' : 'none';
    if (isHidden) window.refreshPodcastInlineEngineConfig();
};

window.savePodcastInlineEngineConfig = async function (provider) {
    const panel = document.getElementById('podcast-engine-inline-config');
    if (!panel) return;
    const payload = { 'podcast.podcast_tts_engines.default_provider': provider };
    window.settingsData = window.settingsData || {};
    window.settingsData.podcast = window.settingsData.podcast || {};
    window.settingsData.podcast.podcast_tts_engines = window.settingsData.podcast.podcast_tts_engines || { default_provider: provider };
    panel.querySelectorAll('input[data-tts-key]').forEach((inp) => {
        const k = inp.getAttribute('data-tts-key'), v = inp.value.trim();
        payload[`podcast.podcast_tts_engines.${k}`] = v;
        window.settingsData.podcast.podcast_tts_engines[k] = v;
    });
    try {
        const r = await fetch('/api/config/update', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` }, body: JSON.stringify(payload) });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        if (typeof window.showToast === 'function') window.showToast(`✅ ${provider} 引擎配置已保存，可继续合成播客`, 'success');
        panel.style.display = 'none';
    } catch (e) { if (typeof window.showToast === 'function') window.showToast(`保存失败: ${e.message}`, 'error'); }
};
