#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - Payload Syndicator (全域内容分发矩阵)
支持矩阵：Dev.to, Medium, Hashnode, WordPress, Ghost, LinkedIn
架构原则：颗粒度开关管控、绝对非阻塞、SEO 原创权重保护、统一草稿防灾机制。
🚀 [V14.3 架构升级]：引入 ThreadPoolExecutor 漏斗限流池，彻底终结 Fire-and-Forget 模式在批量同步时引发的并发雪崩与 OS 句柄耗尽灾难。
"""

import json
import time
import logging
import threading
import re
import hashlib
import requests
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor # 🚀 新增：导入工业级线程池调度器


# 🚀 动态挂载 JWT 引擎 (专供 Ghost Admin API 使用)
try:
    import jwt
    from datetime import datetime
    HAS_JWT = True
except ImportError:
    HAS_JWT = False

logger = logging.getLogger("Illacme.plenipes")

class ContentSyndicator:
    def __init__(self, syndication_cfg, site_url, sys_tuning_cfg=None):
        self.enabled = syndication_cfg.get('enabled', False)
        self.platforms = syndication_cfg.get('platforms', {})
        self.site_url = site_url.rstrip('/') if site_url else ""
        self.timeout = syndication_cfg.get('timeout', 15.0)
        
        # 🚀 抽取硬编码：动态接管线程池并发上限
        sys_tuning = sys_tuning_cfg or {}
        max_workers = sys_tuning.get('max_concurrent_workers', 5)
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def _push_devto(self, api_key, payload):
        url = "https://dev.to/api/articles"
        headers = {"api-key": api_key, "Content-Type": "application/json"}
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if resp.status_code == 201: logger.info(f"🚀 [Dev.to 分发成功] 预览: {resp.json().get('url')}")
            else: logger.warning(f"⚠️ [Dev.to 异常] 状态码 {resp.status_code}: {resp.text}")
        except Exception as e: logger.error(f"🛑 [Dev.to 失败]: {e}")

    def _push_medium(self, token, author_id, payload):
        url = f"https://api.medium.com/v1/users/{author_id}/posts"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if resp.status_code in [200, 201]: logger.info(f"🚀 [Medium 分发成功] 预览: {resp.json().get('data', {}).get('url')}")
            else: logger.warning(f"⚠️ [Medium 异常] 状态码 {resp.status_code}: {resp.text}")
        except Exception as e: logger.error(f"🛑 [Medium 失败]: {e}")

    def _push_hashnode(self, token, payload):
        url = "https://gql.hashnode.com/"
        headers = {"Authorization": token, "Content-Type": "application/json"}
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if resp.status_code == 200 and "errors" not in resp.json():
                logger.info("🚀 [Hashnode 分发成功] (请前往草稿箱查看)")
            else: logger.warning(f"⚠️ [Hashnode 异常]: {resp.text}")
        except Exception as e: logger.error(f"🛑 [Hashnode 失败]: {e}")

    def _push_wordpress(self, endpoint, username, app_password, payload):
        try:
            resp = requests.post(endpoint, json=payload, auth=HTTPBasicAuth(username, app_password), timeout=self.timeout)
            if resp.status_code == 201: logger.info(f"🚀 [WordPress 分发成功] 预览: {resp.json().get('link')}")
            else: logger.warning(f"⚠️ [WordPress 异常] {resp.status_code}: {resp.text}")
        except Exception as e: logger.error(f"🛑 [WordPress 失败]: {e}")

    # ==========================================
    # 🌟 [通道 5] Ghost Admin API
    # ==========================================
    def _push_ghost(self, api_url, api_key, payload):
        if not HAS_JWT:
            logger.error("🛑 [Ghost 分发拦截] 缺少 PyJWT 依赖。请执行: pip install PyJWT")
            return
            
        try:
            # 1. 工业级 Ghost JWT 动态签名
            key_id, secret = api_key.split(':')
            iat = int(datetime.now().timestamp())
            header = {'alg': 'HS256', 'typ': 'JWT', 'kid': key_id}
            jwt_payload = {'iat': iat, 'exp': iat + 5 * 60, 'aud': '/admin/'}
            token = jwt.encode(jwt_payload, bytes.fromhex(secret), algorithm='HS256', headers=header)
            
            # 2. 发射 Payload
            url = f"{api_url.rstrip('/')}/ghost/api/admin/posts/"
            headers = {"Authorization": f"Ghost {token}", "Content-Type": "application/json"}
            
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if resp.status_code == 201:
                logger.info(f"🚀 [Ghost 分发成功] 文章已落入草稿箱！")
            else:
                logger.warning(f"⚠️ [Ghost 分发异常] 状态码 {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"🛑 [Ghost 投递失败]: {e}")

    # ==========================================
    # 🌟 [通道 6] LinkedIn UGC API (流量反哺模式)
    # ==========================================
    def _push_linkedin(self, access_token, person_urn, payload):
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            if resp.status_code == 201:
                logger.info(f"🚀 [LinkedIn 分发成功] 动态已发布至您的 LinkedIn 时间线！")
            else:
                logger.warning(f"⚠️ [LinkedIn 分发异常] 状态码 {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"🛑 [LinkedIn 投递失败]: {e}")

    def syndicate(self, fm_dict, final_body, url_path):
        if not self.enabled or not self.platforms: return

        title = fm_dict.get('title', 'Untitled')
        desc = fm_dict.get('description', f"✨ 我刚刚发布了一篇关于 {title} 的新文章，点击阅读全文！")
        tags = fm_dict.get('tags', [])
        if isinstance(tags, str): tags = [t.strip() for t in tags.split(',') if t.strip()]

        # 🚀 物理消灭双斜杠，同时保护 http(s):// 协议头不被误杀
        canonical_url = f"{self.site_url}/{url_path}".replace('//', '/').replace('https:/', 'https://').replace('http:/', 'http://')

        # 🚀 [补丁加载] 静态资产“绝对路径劫持” (Asset URL Resolution)
        if self.site_url:
            final_body = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', self._resolve_img_url, final_body)

        # 🚀 [调度层重构] 彻底废弃无序的 Thread.start() 游离线程，全部推入 executor 漏斗池统一排队执行
        
        # 1. Dev.to
        dev_cfg = self.platforms.get('devto', {})
        if dev_cfg.get('enabled', False) and dev_cfg.get('api_key'):
            payload = {"article": {"title": title, "body_markdown": final_body, "published": False, "tags": tags[:4], "canonical_url": canonical_url}}
            self.executor.submit(self._push_devto, dev_cfg['api_key'], payload)

        # 2. Medium
        med_cfg = self.platforms.get('medium', {})
        if med_cfg.get('enabled', False) and med_cfg.get('token') and med_cfg.get('author_id'):
            payload = {"title": title, "contentFormat": "markdown", "content": final_body, "tags": tags[:5], "publishStatus": "draft", "canonicalUrl": canonical_url}
            self.executor.submit(self._push_medium, med_cfg['token'], med_cfg['author_id'], payload)

        # 3. Hashnode
        hn_cfg = self.platforms.get('hashnode', {})
        if hn_cfg.get('enabled', False) and hn_cfg.get('token') and hn_cfg.get('publication_id'):
            query = "mutation PublishPost($input: PublishPostInput!) { publishPost(input: $input) { post { url } } }"
            payload = {"query": query, "variables": {"input": {"title": title, "contentMarkdown": final_body, "publicationId": hn_cfg['publication_id'], "originalArticleUrl": canonical_url}}}
            self.executor.submit(self._push_hashnode, hn_cfg['token'], payload)

        # 4. WordPress
        wp_cfg = self.platforms.get('wordpress', {})
        if wp_cfg.get('enabled', False) and wp_cfg.get('url') and wp_cfg.get('username') and wp_cfg.get('app_password'):
            endpoint = f"{wp_cfg['url'].rstrip('/')}/wp-json/wp/v2/posts"
            payload = {"title": title, "content": final_body, "status": "draft", "format": "standard"}
            self.executor.submit(self._push_wordpress, endpoint, wp_cfg['username'], wp_cfg['app_password'], payload)

        # 5. Ghost CMS
        ghost_cfg = self.platforms.get('ghost', {})
        if ghost_cfg.get('enabled', False) and ghost_cfg.get('url') and ghost_cfg.get('admin_api_key'):
            mobiledoc = json.dumps({
                "version": "0.3.1",
                "markups": [], "atoms": [], "sections": [[10, 0]],
                "cards": [["markdown", {"cardName": "markdown", "markdown": final_body}]]
            })
            payload = {
                "posts": [{
                    "title": title,
                    "status": "draft",
                    "mobiledoc": mobiledoc,
                    "tags": [{"name": t} for t in tags],
                    "canonical_url": canonical_url
                }]
            }
            self.executor.submit(self._push_ghost, ghost_cfg['url'], ghost_cfg['admin_api_key'], payload)

        # 6. LinkedIn 流量引流
        li_cfg = self.platforms.get('linkedin', {})
        if li_cfg.get('enabled', False) and li_cfg.get('access_token') and li_cfg.get('person_urn') and canonical_url:
            payload = {
                "author": f"urn:li:person:{li_cfg['person_urn']}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": f"✨ 新技术文章发布：{title}\n\n{desc[:100]}...\n\n点击阅读全文 👇"
                        },
                        "shareMediaCategory": "ARTICLE",
                        "media": [{
                            "status": "READY",
                            "originalUrl": canonical_url,
                            "title": {"text": title},
                            "description": {"text": desc[:100]}
                        }]
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
            }
            self.executor.submit(self._push_linkedin, li_cfg['access_token'], li_cfg['person_urn'], payload)
            

        # -----------------------------------------------------------
        # 7. 🚀 Universal Webhook (工业级健壮版)
        # -----------------------------------------------------------
        webhook_cfg = self.platforms.get('universal_webhook', {})
        if webhook_cfg.get('enabled', False) and webhook_cfg.get('url'):
            
            # 1. 生成可直接发微博/朋友圈的纯文本摘要
            safe_excerpt = self._generate_safe_excerpt(final_body, max_length=400)
            # 2. 生成跨平台兼容的纯正 Markdown 正文
            pure_markdown = self._purify_markdown(final_body)
            
            content_hash = hashlib.md5(final_body.encode('utf-8')).hexdigest()
            
            payload = {
                "event": "illacme.article.published",
                "timestamp": int(time.time()),
                "idempotency_key": content_hash,
                "metadata": {
                    "title": title,
                    "description": desc,
                    "tags": tags,
                    "canonical_url": canonical_url,
                    "author": fm_dict.get('author', 'Illacme Engine'),
                    "word_count": len(pure_markdown) # 使用净化后的字数更准确
                },
                "content": {
                    "markdown": pure_markdown,      # 👈 核心修复：这里现在是纯正、干净的 Markdown
                    "raw_mdx": final_body,       # 附带一个保留源格式的备份，供高级工作流备用
                    "safe_excerpt": safe_excerpt 
                }
            }
            self.executor.submit(self._push_universal_webhook, webhook_cfg['url'], payload, webhook_cfg.get('auth_token'))
        
    def _generate_safe_excerpt(self, markdown_text, max_length=500):
        """
        🛡️ 语义级纯文本提取与安全截断 (终极防腐版)
        严格遵循 AST 降维的正则执行优先级，物理隔离所有前端代码与杂音。
        """
        if not markdown_text:
            return ""
            
        text = markdown_text
        
        # ==========================================
        # 优先级 1: 块级代码与前端组件物理歼灭
        # ==========================================
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL) # 剔除代码块
        text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE) # 物理剥离 CSS 样式块
        text = re.sub(r'^import\s+.*?;?\s*$', '', text, flags=re.MULTILINE) # 剔除 ESM 导入
        
        # ==========================================
        # 优先级 2: 标签与注释清洗 (必须在 Markdown 符号清洗前！)
        # ==========================================
        text = re.sub(r'\{/\*.*?\*/\}', '', text, flags=re.DOTALL) # 剔除 JSX 注释
        text = re.sub(r'', '', text, flags=re.DOTALL) # 剔除 HTML 注释
        text = re.sub(r'<[^>]+>', ' ', text) # 物理剥离所有 HTML 标签
        
        # ==========================================
        # 优先级 3: Markdown 核心语义降维
        # ==========================================
        text = re.sub(r'#+\s', '', text) # 剔除标题 Hash
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text) # 剔除图片
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text) # 剥离链接，保留锚文本 (如 [点击这里](url) -> 点击这里)
        text = re.sub(r'^\s*>\s+', '', text, flags=re.MULTILINE) # 安全剔除 Blockquote 引用符号
        text = re.sub(r'[*_`~|]', '', text) # 剔除加粗、斜体等内联符号 (此时 HTML 的 > 已经被剥离了，安全！)
        
        # ==========================================
        # 优先级 4: 空间压缩与安全边界截断
        # ==========================================
        text = re.sub(r'\s+', ' ', text).strip() # 将所有连续换行、缩进压缩为单个空格
        
        if len(text) <= max_length:
            return text
            
        truncated = text[:max_length]
        # 寻找最近的句子结尾作为截断点
        safe_boundary = max(truncated.rfind('。'), truncated.rfind('. '), truncated.rfind('，'), truncated.rfind(' '))
        
        if safe_boundary > (max_length * 0.7):
            return truncated[:safe_boundary] + "..."
        return truncated + "..."

    def _purify_markdown(self, raw_md):
        """
        🚀 全域标准 Markdown 净化器
        将含有前端组件 (MDX/HTML/CSS) 的源文件，降维清洗为所有 CMS (知乎/Medium) 都能安全渲染的纯正 Markdown。
        """
        if not raw_md: return ""
        text = raw_md

        # 1. 物理歼灭前端专属代码块 (CSS, JS, 模块导入)
        text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'^import\s+.*?;?\s*$', '', text, flags=re.MULTILINE)

        # 2. 剥离注释 (HTML 与 JSX)
        text = re.sub(r'', '', text, flags=re.DOTALL)
        text = re.sub(r'\{/\*.*?\*/\}', '', text, flags=re.DOTALL)

        # 3. 智能剥离 HTML 标签
        # 对于块级结构 (div, section)，脱壳后补充换行符，防止不同段落的文字粘连
        text = re.sub(r'</?(div|section|article|aside|nav|header|footer)[^>]*>', '\n\n', text, flags=re.IGNORECASE)
        # 对于其它内联标签 (span, a)，直接脱壳
        text = re.sub(r'<[^>]+>', '', text)

        # 4. 修复 Markdown 格式断层 (清理多余的连续空白行，最多保留一个空行)
        text = re.sub(r'\n{3,}', '\n\n', text).strip()

        return text

    def _push_universal_webhook(self, webhook_url, payload, auth_token=None):
        """
        🚀 工业级万向推流阀 (Universal Webhook with Resilience)
        搭载 urllib3 指数退避重试池，免疫 502/503/429 网络风暴。
        """
        # 构建防断流会话池
        session = requests.Session()
        retries = Retry(
            total=3,  # 最多重试 3 次
            backoff_factor=1.5,  # 1.5, 3.0, 4.5 秒的指数级避让
            status_forcelist=[429, 500, 502, 503, 504], # 遇到这些网关级错误时强制重试
            allowed_methods=["POST"]
        )
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))

        headers = {'Content-Type': 'application/json'}
        if auth_token:
            headers['Authorization'] = f"Bearer {auth_token}"
            
        try:
            # logger.debug(f"   └── 📡 [全域推流] 正在向网关发射数据包...")
            resp = session.post(webhook_url, json=payload, headers=headers, timeout=self.timeout)
            resp.raise_for_status() # 拦截 4xx 业务错误
            logger.info("   └── ✨ [全域推流] 信号送达！下游自动化工作流已接管。")
        except requests.exceptions.RetryError:
            logger.error(f"   └── 🛑 [全域推流] 目标节点持续崩溃 (已耗尽 3 次重试池)。")
        except requests.exceptions.RequestException as e:
            logger.error(f"   └── ⚠️ [全域推流] 发射中断: {e}")
        finally:
            session.close() # 严格释放系统 Socket 句柄

    def _resolve_img_url(self, match):
        """
        🚀 资产 URL 劫持核心逻辑：将相对路径转化为带域名的绝对物理路径。
        """
        alt_text = match.group(1)
        img_src = match.group(2)
        if img_src.startswith(('http://', 'https://', 'data:image')):
            return match.group(0)
        
        clean_src = '/' + img_src.lstrip('./') 
        absolute_url = f"{self.site_url}{clean_src}"
        
        logger.debug(f"🔍 [资产劫持] 转化图片路径: {img_src} -> {absolute_url}")
        return f"![{alt_text}]({absolute_url})"