# -*- coding: utf-8 -*-
"""
🎙️ Podcast AI Script Writer
职责：调用主权算力中心大模型，将 Markdown 文章深度重构为极具临场感与对话张力的双人播客剧本。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

import json
import re
from typing import Dict, Any, List, Optional
from core.utils.tracing import tlog
from .podcast_models import DialogueTurn, PodcastScript
from .podcast_style_templates import TOPIC_MAP
from core.adapters.ai.payload_manager import PayloadManager


class PodcastAIWriter:
    """大模型双人播客剧本深度重构器"""

    DEFAULT_NAMES = {
        "zh": {"host_a": "晓晓", "host_b": "云希"},
        "en": {"host_a": "Jenny", "host_b": "Guy"},
        "ja": {"host_a": "七海", "host_b": "圭太"}
    }

    @classmethod
    def generate_script(
        cls,
        engine: Any,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        lang: str = "zh",
        style: str = "tech_deep",
        max_turns: int = 10,
        focus_prompt: Optional[str] = None,
        host_a_name: Optional[str] = None,
        host_b_name: Optional[str] = None,
    ) -> PodcastScript:
        """主入口：调用大模型推理生成结构化播客剧本"""
        meta = metadata or {}
        lang_code = (lang or "zh").lower()
        if not lang_code.startswith(("zh", "en", "ja")):
            lang_code = "zh"

        if not engine:
            raise ValueError("引擎未初始化")
        ai_cfg = getattr(engine.config, "translation", None) if hasattr(engine, "config") else None
        enable_ai = getattr(ai_cfg, "enable_ai", True) if ai_cfg else True
        if getattr(engine, "no_ai", False) or not enable_ai:
            raise ValueError("算力中心 AI 算力当前处于关闭状态，请前往「算力中心」开启。")

        adapter = getattr(engine, "translator", None)
        if not adapter:
            raise ValueError("算力中心未检测到可用的主模型节点，请先在「算力中心」激活模型。")

        names = dict(cls.DEFAULT_NAMES.get(lang_code, cls.DEFAULT_NAMES["zh"]))
        if host_a_name and host_a_name.strip():
            names["host_a"] = host_a_name.strip()
        if host_b_name and host_b_name.strip():
            names["host_b"] = host_b_name.strip()
        title = meta.get("title") or "技术对谈"

        system_prompt = cls._build_system_prompt(lang_code, style, names, max_turns)
        user_prompt = cls._build_user_prompt(title, content, lang_code, style, focus_prompt=focus_prompt)

        tlog.info(f"🎙️ 正在调用大模型 ({getattr(adapter, 'node_name', 'LLM')}) 深度重写播客剧本: {title} ({lang_code}/{style})")

        payload = PayloadManager.prepare_payload(
            adapter,
            system_prompt=system_prompt,
            user_content=user_prompt,
            is_json=True
        )

        raw_resp = adapter.ask_ai_with_retry(payload)
        parsed_data = cls._parse_ai_json(raw_resp)

        turns: List[DialogueTurn] = []
        for t in parsed_data.get("turns", []):
            if not isinstance(t, dict):
                continue
            speaker = t.get("speaker", "host_a")
            text = str(t.get("text", "")).strip()
            if not text:
                continue
            s_name = names["host_a"] if speaker == "host_a" else names["host_b"]
            turns.append(DialogueTurn(
                speaker=speaker,
                speaker_name=t.get("speaker_name") or s_name,
                text=text,
                intent=t.get("intent", "dialogue")
            ))

        if not turns:
            raise ValueError("大模型未返回有效的对话轮次，请重试或切换为规则提取")

        total_len = sum(len(t.text) for t in turns)
        est_sec = max(30, int(total_len / (3.5 if lang_code == "zh" else 2.5)))
        default_topic = TOPIC_MAP.get(style, TOPIC_MAP["tech_deep"]).get(lang_code, "Engineering")

        return PodcastScript(
            title=parsed_data.get("title") or title,
            topic=parsed_data.get("topic") or meta.get("category") or default_topic,
            lang=lang_code,
            style=style,
            turns=turns[:max_turns],
            summary=parsed_data.get("summary") or meta.get("description") or "",
            estimated_duration_sec=est_sec
        )

    @classmethod
    def _build_system_prompt(cls, lang: str, style: str, names: Dict[str, str], max_turns: int) -> str:
        ha, hb = names["host_a"], names["host_b"]
        style_desc = {
            "tech_deep": "深度剖析：Host A 为资深架构讲师，深入剖析系统底层机制、低耦合与防御性权衡；Host B 为敏锐技术搭档，紧扣生产落地瓶颈与极端边界追问。",
            "casual_brief": "通俗快讯：Host A 风格轻松活泼，用生活化通俗比喻拆解技术；Host B 代表大众开发者，划重点、产生共鸣，突出免踩坑与效率收益。",
            "debate": "观点交锋：Host A 拥护自主可控与长远架构规范；Host B 担任犀利反方观察员，尖锐质疑自建成本与复杂度，质疑为何不用现成商业工具，双方展开精彩思辨。"
        }.get(style, "深度剖析")

        lang_instruction = {
            "zh": "全篇台词必须使用地道自然、口语化的中文对话。",
            "en": "All dialogue must be spoken in authentic, engaging, modern English conversational podcast style.",
            "ja": "全編のセリフは極めて自然で流暢な日本語の会話口調で記述してください。"
        }.get(lang, "使用地道口语对话。")

        return (
            f"你是一位拥有千万级听众的技术播客金牌制作人与编剧导演。\n"
            f"你的任务是将输入的技术文章深度改编为真实的双人对话播客剧本。\n"
            f"【角色设定】：Host A 名为 '{ha}'，Host B 名为 '{hb}'。\n"
            f"【对话风格】：{style_desc}\n"
            f"【语言要求】：{lang_instruction}\n"
            f"【写作规则】：\n"
            f"1. 严禁死板机械地念稿或转述段落，必须像两个真实的工程师在录音棚里自然交谈、有眼神交汇、有反应词和情绪起伏；\n"
            f"2. 严禁在台词中包含任何 Markdown 符号（如 '|' 表格、'```' 代码块、'#' 标题、'*' 强调符）；\n"
            f"3. 控制对话轮次在 8 到 {max_turns} 轮之间，轮流交替，开场有引人入胜的寒暄，结尾有精炼有力的收束；\n"
            f"4. 必须输出严格合法的 JSON 对象，不要输出任何额外的思考过程或外层解释，格式如下：\n"
            f'{{"title": "...", "topic": "...", "summary": "...", "turns": [{{"speaker": "host_a", "speaker_name": "{ha}", "text": "...", "intent": "intro"}}]}}'
        )

    @classmethod
    def _build_user_prompt(cls, title: str, content: str, lang: str, style: str, focus_prompt: Optional[str] = None) -> str:
        clipped = content[:4500] if len(content) > 4500 else content
        focus_block = f"\n【创作者特别聚焦指令】：{focus_prompt.strip()}\n" if focus_prompt and focus_prompt.strip() else ""
        return (
            f"请将以下技术稿件深度编排为双人对话播客剧本：\n"
            f"【文章标题】：{title}\n"
            f"【目标风格】：{style}\n"
            f"【目标语种】：{lang}{focus_block}\n"
            f"【文章正文摘要与核心】：\n"
            f"{clipped}\n\n"
            f"请以符合该风格和语种的 JSON 格式输出完整剧本。"
        )

    @classmethod
    def _parse_ai_json(cls, text: str) -> Dict[str, Any]:
        """防御性解析大模型返回的 JSON"""
        if not text:
            return {}
        cleaned = text.strip()
        m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned, re.DOTALL)
        if m:
            cleaned = m.group(1).strip()
        else:
            first_brace = cleaned.find('{')
            last_brace = cleaned.rfind('}')
            if first_brace != -1 and last_brace != -1:
                cleaned = cleaned[first_brace:last_brace + 1]
        try:
            return json.loads(cleaned)
        except Exception as e:
            tlog.warning(f"Failed to parse AI podcast JSON: {e}, text snippet: {text[:200]}")
            return {}

