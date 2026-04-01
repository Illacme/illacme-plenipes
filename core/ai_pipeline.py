#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Pipeline (LLM Orchestration)
模块职责：全权接管与外部大模型（OpenAI/Qwen/DeepSeek等）的通信。
云化前瞻：内置了企业级的 2^n 指数退避重试（Exponential Backoff）和长文切片防截断机制。
架构演进：已注入全局高并发连接池与切片级嵌套并发引擎，彻底榨干大模型集群吞吐极限。
极客内核：搭载基于 tiktoken 的高精度 Token 级文本切片引擎，精准压榨上下文窗口。
"""

import re
import time
import json
import html
import logging
import requests
import urllib.parse
import threading
import concurrent.futures
from requests.adapters import HTTPAdapter

# 🚀 引入工业级 Token 计算底层，并做优雅降级保护
try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False

logger = logging.getLogger("Illacme.plenipes")

class TranslatorFactory:
    """管理外部大模型请求、长文切片翻译与 SEO 元数据提取"""
    def __init__(self, config):
        self.cfg = config.get('translation', {})
        self.provider = self.cfg.get('provider', 'none').lower()
        self.base_url = self.cfg.get('base_url', '').rstrip('/')
        self.api_key = self.cfg.get('api_key', 'unused')
        self.model = self.cfg.get('model', 'gpt-4o')
        self.slug_mode = self.cfg.get('slug_mode', 'ai').lower()
        self.timeout = self.cfg.get('api_timeout', 120)
        self.max_retries = self.cfg.get('max_retries', 3)
        # 🚀 动态挂载字数阈值：该参数现已升级为 engine.py 调度层的“实质性内容拦截门槛”
        self.empty_threshold = self.cfg.get('empty_content_threshold', 15)
        
        # 🚀 架构升级：动态读取大模型的高级控制参数
        self.temperature = self.cfg.get('temperature', 0.1)
        self.max_chunk_size = self.cfg.get('max_chunk_size', 4000)
        
        self.prompts = self.cfg.get('custom_prompts', {})
        self.translate_sys_prompt = self.prompts.get('translate_system', "You are a professional technical translator.")
        self.seo_sys_prompt = self.prompts.get('seo_system', "You are an SEO expert.")

        # 🚀 架构跃迁：引入全局推理信号量 (Global LLM Semaphore)
        # 彻底剥离 CPU 并发与大模型 VRAM 并发，实现异构算力隔离
        self.llm_concurrency = self.cfg.get('llm_concurrency', 1)
        self._llm_semaphore = threading.Semaphore(self.llm_concurrency)

        # 架构升级：挂载全局 HTTP 长连接池，消除并发下的 TCP/TLS 握手风暴
        self.session = requests.Session()
        pool_size = config.get('system', {}).get('max_workers', 20) * 2 # 保证连接池容量充裕
        adapter = HTTPAdapter(pool_connections=pool_size, pool_maxsize=pool_size, max_retries=0)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _get_token_count(self, text):
        """核心探针：高精度 Token 数量估算器"""
        if HAS_TIKTOKEN:
            try:
                # 使用 cl100k_base 编码，这是目前通用性最高、对大多数模型边界最安全的估算基准
                encoding = tiktoken.get_encoding("cl100k_base")
                return len(encoding.encode(text, disallowed_special=()))
            except Exception:
                return len(text)
        # 如果未安装 tiktoken 库，安全降级回传统的字符长度计算
        return len(text)

    def ai_call(self, prompt, sys_prompt=None, is_dry_run=False):
        """核心网络请求器：内置 2^n 指数退避重试网络与 Keep-Alive 链路复用"""
        if is_dry_run: 
            return "[Dry-Run 模拟数据]"
        if self.provider == 'none' or not self.base_url: 
            return None
        
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        messages = []
        if sys_prompt: 
            messages.append({"role": "system", "content": sys_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # 🚀 将硬编码的 0.1 替换为动态配置的 temperature
        payload = {"model": self.model, "messages": messages, "temperature": self.temperature}
        
        for attempt in range(self.max_retries):
            try:
                # 🚀 获取全局推理防爆锁：所有到达此处的并发线程必须严格排队，绝对保护大模型显存
                with self._llm_semaphore:
                    # 统一复用 session 对象，大幅降低 I/O 阻滞
                    resp = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
                
                if resp.status_code == 200:
                    return resp.json()['choices'][0]['message']['content'].strip()
                elif resp.status_code == 429 or resp.status_code >= 500:
                    # 🚀 语义降维：将“触发防刷熔断”转化为排队提示
                    hint = " (💡 诊断: 若显存溢出，请将 config.yaml 的 llm_concurrency 降为 1)" if resp.status_code >= 500 else ""
                    logger.warning(f"⚠️ 进入 AI 保护排队模式，预计 {2**attempt}s 后重试...{hint}")
                    time.sleep(2 ** attempt)
                    continue
                break
            except (requests.exceptions.Timeout, Exception) as e:
                # 🚀 注入保姆级引导：明确告知用户可能是超时，并提供配置文件修改建议
                logger.warning(f"⚠️ AI 响应超时或通讯异常，正在重试... (💡 诊断: 若本地模型处理长文极慢，请在 config.yaml 中大幅调高 api_timeout 阈值) 底层报错: {e}")
                time.sleep(2 ** attempt)
        return None

    def generate_slug(self, title, is_dry_run=False):
        """返回元组 (slug_text, is_success) 用于探针追踪"""
        # 🚀 提取通用且原生支持中英文的本地 Slug 降级方案
        def _local_fallback(t):
            clean_t = re.sub(r'[^\w\u4e00-\u9fa5\-]', '', t.replace(' ', '-')).lower()
            return re.sub(r'-+', '-', clean_t).strip('-')

        if self.slug_mode == 'local': 
            return _local_fallback(title), True
            
        if is_dry_run: 
            return "dry-run-slug", True
            
        # 🚀 注入过程感知
        logger.info(f"   └── ⏳ 正在让 AI 为您构思文章 URL 链接...")
        prompt = f"Target: Create an English URL slug for '{title}'. Rule: Output ONLY the slug text, lowercase, hyphens only."
        res = self.ai_call(prompt)
        
        if res:
            res = re.sub(r'```.*?```', '', res, flags=re.DOTALL)
            clean_slug = re.sub(r'[^a-z0-9-]', '', res.replace(' ', '-').replace('"', '').replace("'", '')).lower()
            if clean_slug: # 防止 AI 返回空值
                return re.sub(r'-+', '-', clean_slug).strip('-'), True
                
        return _local_fallback(title), False
        
    def generate_seo_metadata(self, content, is_dry_run=False):
        """返回元组 (seo_dict, is_success) 用于探针追踪"""
        if is_dry_run: 
            return {"description": "Dry run desc", "keywords": "dry, run"}, True
            
        # 🚀 语义升级：针对实质性内容的二级拦截
        if len(content.strip()) < self.empty_threshold:
            logger.info("      └── 🍃 内容未达字数阈值，已跳过 SEO 提取以保护 AI 逻辑稳定。")
            return {}, True

        # 🚀 注入过程感知
        logger.info(f"   └── ⏳ 正在让 AI 深度分析文章，提取 SEO 摘要与关键词...")
        prompt = (
            "Read the following article and extract:\n"
            "1. A concise meta description (under 150 characters, plain text, strictly matching the language of the provided article).\n"
            "2. A list of 3-5 highly relevant SEO keywords (comma separated, strictly matching the language of the provided article).\n"
            "Output strictly in valid JSON format: {\"description\": \"...\", \"keywords\": \"...\"}\n\n"
            f"Article content: {content[:1500]}" 
        )
        res = self.ai_call(prompt, sys_prompt=self.seo_sys_prompt)
        if res:
            try:
                clean_json = re.sub(r'^```json\s*|\s*创意```$', '', res.strip(), flags=re.IGNORECASE)
                return json.loads(clean_json), True
            except Exception as e:
                logger.error(f"解析 SEO JSON 响应失败: {e}")
                pass
        return {}, False

    def translate_body(self, content, target_lang, is_dry_run=False):
        """返回元组 (translated_content, is_fully_successful) 用于长文探针追踪"""
        if is_dry_run: 
            return f"[Dry-Run Translated to {target_lang}]\n\n{content}", True
        
        # 🚀 语义升级：防范 AI 对极短内容的胡言乱语
        if len(content.strip()) < self.empty_threshold:
            logger.info(f"      └── 🍃 内容未达字数阈值，已跳过 ({target_lang}) 翻译以防范 AI 幻觉。")
            return content, True
            
        # 🚀 核心跃迁：计算当前全文本的 Token 规模
        content_tokens = self._get_token_count(content)
            
        # 🚀 将原来的字符长度判断替换为 Token 动态配置阈值判定
        if content_tokens <= self.max_chunk_size:
            # 🚀 注入过程感知
            logger.info(f"   └── ⏳ 正在让 AI 将正文翻译为 {target_lang}...")
            res = self._do_translate(content, target_lang)
            if res: return res, True
            return content, False
            
        # 🚀 语义降维
        logger.info(f"      └── 📦 文档超长 ({content_tokens} Tokens)，正在启动【安全切片引擎】分块翻译...")
        paragraphs = content.split('\n\n')
        chunks, current_chunk, current_tokens = [], [], 0
        
        for p in paragraphs:
            # 🚀 测算单个段落的 Token 量
            p_tokens = self._get_token_count(p)
            
            # 🚀 替换动态阈值判定为 Token 容量累加
            if current_tokens + p_tokens > self.max_chunk_size and current_chunk:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk, current_tokens = [p], p_tokens
            else:
                current_chunk.append(p)
                # 累加当前段落 Token，并补偿 \n\n 连接符约等于 2 个 Token 的消耗
                current_tokens += p_tokens + 2
                
        if current_chunk: 
            chunks.append('\n\n'.join(current_chunk))
            
        # 架构升级：引入切片级并发调度，彻底抹平长文 O(N) 耗时瓶颈
        translated_chunks = [None] * len(chunks)
        is_fully_successful = True
        
        def translate_chunk_task(idx, chunk_text):
            return idx, chunk_text, self._do_translate(chunk_text, target_lang)
            
        # 根据切片数量动态分配线程，上限锁定 10 以防单篇长文耗尽全局连接池
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(chunks), 10)) as executor:
            future_to_chunk = [executor.submit(translate_chunk_task, i, c) for i, c in enumerate(chunks)]
            for future in concurrent.futures.as_completed(future_to_chunk):
                try:
                    idx, original_text, res = future.result()
                    if res:
                        translated_chunks[idx] = res
                    else:
                        translated_chunks[idx] = original_text
                        is_fully_successful = False
                except Exception as exc:
                    logger.error(f"切片翻译引擎异常: {exc}")
                    is_fully_successful = False
            
        # 处理可能因崩溃导致的 None 值降级
        for i, chunk in enumerate(translated_chunks):
            if chunk is None:
                translated_chunks[i] = chunks[i]
                
        return '\n\n'.join(translated_chunks), is_fully_successful

    def _do_translate(self, content, target_lang):
        # 🚀 系统级防御：强制防幻觉指令注入
        anti_hallucination_rules = (
            "4. CRITICAL: The user is actively typing live. If the text contains meaningless keystroke debris "
            "(e.g., '发撒发', 'sdfasd', '测试 12345'), random alphabet strings, or severely incomplete sentence fragments "
            "lacking semantic logic, YOU MUST NOT attempt a literal translation. You must either keep the original "
            "characters intact or ignore the debris. Never hallucinate forced meaning."
        )
        
        prompt = (
            f"Translate the following Markdown content to {target_lang}.\n"
            "STRICT RULES:\n"
            "1. Keep all [[STB_MASK_n]] placeholders exactly unchanged.\n"
            "2. Keep the original Markdown structure intact.\n"
            "3. Output ONLY the translated text.\n"
            f"{anti_hallucination_rules}\n\n"
            f"{content}"
        )
        res = self.ai_call(prompt, sys_prompt=self.translate_sys_prompt)
        if res:
            res = re.sub(r'^```[a-zA-Z]*\n', '', res)
            res = re.sub(r'\n```$', '', res)
            return html.unescape(res).strip()
        return None