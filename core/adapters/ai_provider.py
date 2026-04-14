#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Illacme-plenipes Core - AI Provider Universal Gateway (全域算力网关)
职责：彻底解耦 AI 接口。支持声明式挂载所有主流大模型，并支持自由组合备援、分流策略。
🚀 [V15.3 架构升级]：
1. [State Alignment] 修复 Fallback/SmartRouting 策略类缺失 empty_threshold 导致的崩溃。
2. [Hardcoded Base] 将翻译与 SEO 的技术性硬约束从配置移回代码，保障工业级鲁棒性。
3. [Contextual Prompting] 引入 context_type 感知，自动为不同场景注入特定的 AI 律令。
"""

import re
import json
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("Illacme.plenipes")

# ==========================================
# 🛡️ 工业级网络池基建 (Enterprise Network Session)
# ==========================================
def build_resilient_session(retries=3, backoff_factor=1.0):
    session = requests.Session()
    retry_strategy = Retry(
        total=retries, read=retries, connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST", "GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# ==========================================
# 🧱 协议解析基座 (Protocol Adapters)
# ==========================================
class BaseTranslator:
    def __init__(self, cfg, global_timeout, global_retries, ai_tuning, custom_prompts=None):
        """
        🚀 基础适配器构造：注入全域配置属性
        """
        self.cfg = cfg or {}
        self.timeout = global_timeout
        self.session = build_resilient_session(retries=global_retries, backoff_factor=1.0)
        
        # 算力参数注入
        self.temperature = ai_tuning.get('temperature', 0.2)
        self.max_tokens = ai_tuning.get('max_tokens', 8192)
        
        # 🚀 [V15.3 关键修复]：确保所有子类策略都能访问此阈值
        self.empty_threshold = self.cfg.get('empty_content_threshold', 15)
        
        # 🚀 夺回控制权：捕获并挂载提示词矩阵
        self.prompts = custom_prompts or {}

    def get_system_prompt(self, source_lang, target_lang):
        """动态生成系统指令 (该方法现主要用于原始 API 调用)"""
        if target_lang in ["JSON Metadata", "URL Slug", "Image Alt Generation"]:
            return None
            
        default_prompt = "You are a professional translator. Keep all Markdown formatting intact. Output ONLY the translated text."
        sys_prompt = self.prompts.get('translate_system', default_prompt)
        return f"{sys_prompt}\n\n[CRITICAL TASK: Translate from {source_lang} to {target_lang}]"

    def translate(self, text, source_lang, target_lang, context_type="body"):
        """
        🚀 强化版翻译引擎：物理级硬核规则注入 (融合旧版 V14.9 专家经验)
        """
        if not text or len(text.strip()) < self.empty_threshold:
            return text

        # 1. 从配置文件读取用户的“语气/人设”
        user_personality = self.prompts.get('translate_system', "You are a professional technical translator.")
        
        # 2. 🚀 [架构护盾] 重新注入老版本代码中的“钢铁律令”
        # 这些规则由代码硬核保障，用户无法轻易通过配置搞坏
        technical_constraints = [
            "=== ARCHITECTURAL CONSTRAINTS (DO NOT VIOLATE) ===",
            "1. PROTECT MASKS: Keep all [[STB_MASK_n]] placeholders exactly unchanged. This is critical for post-processing.",
            "2. MDX/JSX GUARD: Keep ALL HTML tags, Astro/React components (e.g., <Card>, <Aside>), and 'import/export' statements 100% intact.",
            "3. TRANSLATION BOUNDARY: ONLY translate human-readable text and string attributes like title=\"...\", description=\"...\", alt=\"...\".",
            "4. ATTRIBUTE PROTECTION: DO NOT translate system attributes like icon=\"...\", href=\"...\", class=\"...\", or anything inside curly braces {}.",
            "5. FRAGMENT SAFETY: If you see unclosed tags, DO NOT close them. Maintain the structure exactly as provided.",
            "6. NO WRAPPERS: Output ONLY the translated content. NO code fences (```), NO 'Here is the translation', NO conversational filler.",
            "7. ANTI-HALLUCINATION: If the input contains random keystrokes or meaningless debris, keep it as-is. Never hallucinate."
            # 🚀 终极杀招：彻底封杀语言泄漏与中英夹杂
            "8. ZERO LANGUAGE LEAKAGE: You MUST translate EVERY SINGLE Chinese character into the target language. DO NOT leave mixed-language terms like 'Asset争夺' (translate fully to 'Asset Contention' or 'Struggle'). The final output MUST be 100% pure target language."
        ]

        # 3. 针对不同场景动态微调律令
        if context_type == "body":
            technical_constraints.insert(3, "4. IMAGE ALT: Pay special attention to Markdown image alt text ![Translate This](...), ensure it is translated.")

        # 4. 最终合成系统提示词
        enhanced_sys_prompt = f"{user_personality}\n\n" + "\n".join(technical_constraints)

        # 5. 执行调用
        prompt = f"Translate the following {context_type} content from {source_lang} to {target_lang}:\n\n{text}"
        res = self.ai_call(prompt, sys_prompt=enhanced_sys_prompt)

        # 6. 后处理清洗 (物理级斩断大模型可能自带的代码块围栏)
        if res:
            res = re.sub(r'^```[a-zA-Z]*\n', '', res)
            res = re.sub(r'\n```$', '', res)
            import html
            return html.unescape(res).strip()
        return text

    def generate_seo_metadata(self, text, lang_name="English", is_dry_run=False):
        """
        🚀 工业级 SEO 提取引擎 (回迁旧版 V14.9 鲁棒性逻辑)
        """
        if is_dry_run: 
            return {"description": "Dry run summary", "keywords": "test, chaos"}, True
            
        # 1. [旧版回归] 字数拦截与语义窗口截断
        if not text or len(text.strip()) < self.empty_threshold:
            return {}, True
        
        # 仅取前 1500 字符，保护上下文窗口并提升摘要精准度
        semantic_context = text[:1500] 

        # 2. [架构注入] 用户语气 + 物理级约束
        user_seo_personality = self.prompts.get('seo_system', "You are a senior SEO expert.")
        
        technical_rules = [
            f"1. LANGUAGE: All output MUST be in {lang_name}.",
            "2. FORMAT: Output ONLY a valid JSON object. No markdown fences, no notes.",
            "3. DESCRIPTION: Concise, CTR-focused, 120-160 characters.",
            "4. KEYWORDS: 3-8 high-value phrases, comma-separated."
        ]
        
        full_sys_prompt = f"{user_seo_personality}\n\n" + "\n".join(technical_rules)
        
        # 3. 执行调用
        prompt = f"Analyze this article and extract JSON SEO metadata:\n\n{semantic_context}"
        raw_res = self.ai_call(prompt, sys_prompt=full_sys_prompt)
        
        if raw_res:
            try:
                # [旧版进阶] 物理级除垢正则
                clean_json = re.sub(r'^```json\s*|\s*```$', '', raw_res.strip(), flags=re.IGNORECASE)
                # 针对某些模型可能在 JSON 前后加废话的极限兼容
                match = re.search(r'\{.*\}', clean_json, re.DOTALL)
                if match:
                    import json
                    return json.loads(match.group(0)), True
            except Exception as e:
                logger.error(f"❌ SEO JSON 解析失败: {e}")
        return {}, False

    def generate_slug(self, text, is_dry_run=False):
        """
        🚀 兼容老版本路由引擎的 Slug 极速生成器 (融合 V15 架构与旧版清洗防线)
        """
        def _hardcore_english_fallback(t):
            import hashlib
            import re
            english_only = re.sub(r'[^a-z0-9\-]', '', t.lower().replace(' ', '-'))
            clean_slug = re.sub(r'-+', '-', english_only).strip('-')
            if not clean_slug:
                return f"doc-{hashlib.md5(t.encode('utf-8')).hexdigest()[:6]}"
            return clean_slug

        if is_dry_run: return f"dry-run-{hash(text)}", True
            
        try:
            logger.debug(f"   └── ⏳ 正在呼叫算力网关为您构思英文 URL 链接...")
            prompt = f"Target: Create a highly readable English URL slug for '{text}'. Rule: Output ONLY the slug text, lowercase, hyphens only."
            raw_res = self.translate(prompt, "Auto", "URL Slug", context_type="slug")
            
            if raw_res:
                import re
                res = re.sub(r'```.*?```', '', raw_res, flags=re.DOTALL)
                clean_slug = re.sub(r'[^a-z0-9-]', '', res.replace(' ', '-').replace('"', '').replace("'", '')).lower()
                if clean_slug:
                    return re.sub(r'-+', '-', clean_slug).strip('-'), True
            return _hardcore_english_fallback(text), False
        except Exception as e:
            logger.warning(f"⚠️ [Slug 引擎] 大模型生成永久链接失败 ({e})，正在触发本地哈希降级...")
            return _hardcore_english_fallback(text), False

# ==========================================
# 🧱 具体协议实现 (Concrete Translators)
# ==========================================

class OllamaTranslator(BaseTranslator):
    """🟢 本地协议"""
    def __init__(self, cfg, global_timeout, global_retries, ai_tuning, custom_prompts=None):
        super().__init__(cfg, global_timeout, global_retries, ai_tuning, custom_prompts)
        self.endpoint = cfg.get('url', 'http://localhost:11434/api/generate')
        self.model = cfg.get('model', 'qwen2.5:7b')

    def ai_call(self, prompt, sys_prompt=None):
        full_prompt = f"{sys_prompt}\n\n{prompt}" if sys_prompt else prompt
        payload = {
            "model": self.model, "prompt": full_prompt, "stream": False,
            "options": {"temperature": self.temperature, "num_predict": self.max_tokens}
        }
        resp = self.session.post(self.endpoint, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json().get('response', "")

class OpenAICompatibleTranslator(BaseTranslator):
    """🔵 OpenAI 兼容协议 (支持自动路径纠偏)"""
    def __init__(self, cfg, global_timeout, global_retries, ai_tuning, custom_prompts=None):
        super().__init__(cfg, global_timeout, global_retries, ai_tuning, custom_prompts)
        
        # 🚀 专家级路径纠偏：自动检测并补全缺失的 /v1
        raw_url = cfg.get('base_url', 'https://api.openai.com/v1').rstrip('/')
        if not raw_url.endswith('/v1') and 'openai.com' not in raw_url:
            # 针对本地网关（如 LM Studio, Ollama 兼容层）自动补全版本号
            raw_url = f"{raw_url}/v1"
            
        self.endpoint = f"{raw_url}/chat/completions"
        self.api_key = cfg.get('api_key')
        self.model = cfg.get('model', 'gpt-4o')

    def ai_call(self, prompt, sys_prompt=None):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        messages = []
        if sys_prompt:
            messages.append({"role": "system", "content": sys_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {"model": self.model, "temperature": self.temperature, "messages": messages}
        
        try:
            resp = self.session.post(self.endpoint, json=payload, headers=headers, timeout=self.timeout)
            
            # 🚀 增加状态码校验
            if resp.status_code != 200:
                logger.error(f"🛑 API 返回异常状态码: {resp.status_code} | 响应内容: {resp.text[:200]}")
                return ""

            data = resp.json()
            
            # 🚀 增加健壮性校验：不再直接读取 choices，而是用 get()
            choices = data.get('choices')
            if choices and len(choices) > 0:
                return choices[0].get('message', {}).get('content', "")
            
            logger.error(f"⚠️ API 响应格式不完整 (缺少 choices): {data}")
            return ""
            
        except Exception as e:
            # 捕获网络、SSL 或 JSON 解析异常，交由上层 FallbackStrategy 处理
            logger.warning(f"⚠️ AI 调用链路异常: {e}")
            raise  # 抛给 FallbackStrategy 切换备用节点

class GeminiTranslator(BaseTranslator):
    """☁️ Google 原生协议"""
    def __init__(self, cfg, global_timeout, global_retries, ai_tuning, custom_prompts=None):
        super().__init__(cfg, global_timeout, global_retries, ai_tuning, custom_prompts)
        self.api_key = cfg.get('api_key')
        self.model = cfg.get('model', 'gemini-1.5-pro')
        self.endpoint = f"[https://generativelanguage.googleapis.com/v1beta/models/](https://generativelanguage.googleapis.com/v1beta/models/){self.model}:generateContent?key={self.api_key}"

    def ai_call(self, prompt, sys_prompt=None):
        full_msg = f"{sys_prompt}\n\n{prompt}" if sys_prompt else prompt
        payload = {
            "contents": [{"parts": [{"text": full_msg}]}],
            "generationConfig": {"temperature": self.temperature, "maxOutputTokens": self.max_tokens}
        }
        resp = self.session.post(self.endpoint, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        candidates = resp.json().get('candidates', [])
        return candidates[0]['content']['parts'][0]['text'] if candidates else ""

class AnthropicTranslator(BaseTranslator):
    """🟣 Claude 原生协议"""
    def __init__(self, cfg, global_timeout, global_retries, ai_tuning, custom_prompts=None):
        super().__init__(cfg, global_timeout, global_retries, ai_tuning, custom_prompts)
        self.endpoint = "[https://api.anthropic.com/v1/messages](https://api.anthropic.com/v1/messages)"
        self.api_key = cfg.get('api_key')
        self.model = cfg.get('model', 'claude-3-5-sonnet-20240620')

    def ai_call(self, prompt, sys_prompt=None):
        headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        payload = {
            "model": self.model, "temperature": self.temperature, "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        }
        if sys_prompt: payload["system"] = sys_prompt
        resp = self.session.post(self.endpoint, json=payload, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()['content'][0]['text']

# ==========================================
# 🧠 战术编排层 (Strategy Orchestrators)
# ==========================================
class FallbackStrategy(BaseTranslator):
    def __init__(self, primary_node, fallback_node):
        """
        🚀 备援策略：从主节点继承物理属性，确保状态一致性
        """
        self.primary = primary_node
        self.fallback = fallback_node
        # 🚀 [V15.3 修复点]：将子节点的属性同步至包装器，防止 engine.py 调用时发生 AttributeError
        self.empty_threshold = primary_node.empty_threshold
        self.prompts = primary_node.prompts

    def translate(self, text, source_lang, target_lang, context_type="body"):
        try:
            return self.primary.translate(text, source_lang, target_lang, context_type)
        except Exception as e:
            logger.warning(f"⚠️ [算力路由] 主节点故障 ({e})，正在静默切换至备用节点...")
            return self.fallback.translate(text, source_lang, target_lang, context_type)

    def generate_seo_metadata(self, text, lang_name="English", is_dry_run=False):
        try:
            return self.primary.generate_seo_metadata(text, lang_name, is_dry_run)
        except Exception:
            return self.fallback.generate_seo_metadata(text, lang_name, is_dry_run)

    def generate_slug(self, text, is_dry_run=False):
        try:
            return self.primary.generate_slug(text, is_dry_run)
        except Exception:
            return self.fallback.generate_slug(text, is_dry_run)

class SmartRoutingStrategy(BaseTranslator):
    def __init__(self, light_node, heavy_node, threshold=1000):
        self.light_node = light_node
        self.heavy_node = heavy_node
        self.threshold = threshold
        # 🚀 [V15.3 修复点]：属性对齐
        self.empty_threshold = light_node.empty_threshold
        self.prompts = light_node.prompts

    def translate(self, text, source_lang, target_lang, context_type="body"):
        if len(text) < self.threshold:
            return self.light_node.translate(text, source_lang, target_lang, context_type)
        return self.heavy_node.translate(text, source_lang, target_lang, context_type)

    def generate_seo_metadata(self, text, lang_name="English", is_dry_run=False):
        if len(text) < self.threshold:
            return self.light_node.generate_seo_metadata(text, lang_name, is_dry_run)
        return self.heavy_node.generate_seo_metadata(text, lang_name, is_dry_run)

    def generate_slug(self, text, is_dry_run=False):
        if len(text) < self.threshold:
            return self.light_node.generate_slug(text, is_dry_run)
        return self.heavy_node.generate_slug(text, is_dry_run)

# ==========================================
# 🏭 工厂与中枢总线 (Gateway Factory)
# ==========================================
class TranslatorFactory:
    @classmethod
    def _build_node(cls, node_name, providers_cfg, global_timeout, global_retries, ai_tuning, custom_prompts):
        cfg = providers_cfg.get(node_name)
        if not cfg: raise ValueError(f"未找到节点配置: {node_name}")
        ptype = cfg.get('type')
        if ptype == 'ollama': return OllamaTranslator(cfg, global_timeout, global_retries, ai_tuning, custom_prompts)
        if ptype == 'openai-compatible': return OpenAICompatibleTranslator(cfg, global_timeout, global_retries, ai_tuning, custom_prompts)
        if ptype == 'gemini': return GeminiTranslator(cfg, global_timeout, global_retries, ai_tuning, custom_prompts)
        if ptype == 'anthropic': return AnthropicTranslator(cfg, global_timeout, global_retries, ai_tuning, custom_prompts)
        raise ValueError(f"不支持的算力协议: {ptype}")

    @staticmethod
    def create(cfg, sys_tuning_cfg=None):
        providers = cfg.get('providers', {})
        strategy = cfg.get('strategy', 'single')
        global_timeout = cfg.get('api_timeout', 600.0)
        global_retries = cfg.get('max_retries', 3)
        ai_tuning = (sys_tuning_cfg or {}).get('ai_translation', {})
        custom_prompts = cfg.get('custom_prompts', {})
        
        try:
            primary_name = cfg.get('primary_node')
            fallback_name = cfg.get('fallback_node')
            if strategy == 'single':
                return TranslatorFactory._build_node(primary_name, providers, global_timeout, global_retries, ai_tuning, custom_prompts)
            elif strategy == 'fallback':
                return FallbackStrategy(
                    TranslatorFactory._build_node(primary_name, providers, global_timeout, global_retries, ai_tuning, custom_prompts),
                    TranslatorFactory._build_node(fallback_name, providers, global_timeout, global_retries, ai_tuning, custom_prompts)
                )
            elif strategy == 'smart_routing':
                threshold = cfg.get('routing_threshold', 1000)
                return SmartRoutingStrategy(
                    TranslatorFactory._build_node(primary_name, providers, global_timeout, global_retries, ai_tuning, custom_prompts),
                    TranslatorFactory._build_node(fallback_name, providers, global_timeout, global_retries, ai_tuning, custom_prompts),
                    threshold
                )
        except Exception as e:
            logger.error(f"🛑 算力网关初始化失败: {e}")
            raise