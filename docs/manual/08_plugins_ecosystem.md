# 🧩 08. 插件生态与分发网络 (Plugins Ecosystem)

### 功能概述
**插件中心** 承载系统的全域连接能力，将各种异构平台标准化封装为轻量级适配器。所有插件严格遵循中央凭据判决（SSOT）机制，拒绝虚假就绪与配置混乱。

---

### 全域生态矩阵

#### 1. 全站静态托管平台 (10 大驱动)
*   **平台列表**：GitHub Pages、Vercel、Netlify、Cloudflare Pages、GitLab Pages、Gitee Pages、Firebase Hosting、Railway、Render、Zeabur、本地私有 SFTP/SSH。
*   **极简免密体验**：支持检测本机已有 CLI（如 `gh`、`vercel`），一键免密授权，自动识别并回填账号与仓库。

#### 2. 社交媒体与技术博客分发 (20+ 渠道)
*   **国内主流渠道**：
    *   **微信公众号**：自动将 Markdown 转为精美微信排版，原生插入微信草稿箱，插图自动转存至永久素材库；
    *   **知乎 / 掘金 / 博客园 / CSDN / 思否 / 开源中国 / 今日头条 / Bilibili / 小红书**。
*   **海外技术社区**：
    *   **Dev.to / Hashnode / Medium / Ghost / Substack / WordPress / LinkedIn / Discord / Telegram**。
    *   原生注入 `canonical_url` 指向您的独立主站，避免搜索权重分散。

#### 3. 图像图床网络 (14 大适配器)
*   **云存储服务**：阿里云 OSS、腾讯云 COS、七牛云 Kodo、Cloudflare R2、AWS S3、又拍云。
*   **公共图床**：ImgBB、Imgur、GitHub、Lsky Pro、Catbox、Superbed、Telegraph 等。
*   **防盗链自愈**：在分发时自动检测外链有效性，支持在推流前将本地插图安全转存并替换链接。
