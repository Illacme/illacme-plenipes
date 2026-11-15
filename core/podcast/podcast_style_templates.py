# -*- coding: utf-8 -*-
"""
🎙️ Podcast Style Templates & Conversational Patterns
职责：提供深度剖析 (tech_deep)、通俗快讯 (casual_brief)、观点交锋 (debate) 的多语言对话模板与台词构建器。
🛡️ [SOP-01] 物理行数严格保持在 300 行以内。
"""

from typing import Dict, Any, List
from .podcast_models import DialogueTurn


TOPIC_MAP = {
    "tech_deep": {"zh": "深度工程", "en": "Deep Architecture", "ja": "技術アーキテクチャ深掘り"},
    "casual_brief": {"zh": "极速快讯", "en": "Tech Flash Brief", "ja": "テクノロジースピード解説"},
    "debate": {"zh": "观点交锋", "en": "Architectural Debate", "ja": "視点の対立と議論"},
    "solo_read": {"zh": "全文伴读", "en": "Article Narration", "ja": "記事全文朗読"}
}


def build_intro_turns(title: str, summary: str, lang: str, style: str, names: Dict[str, str]) -> List[DialogueTurn]:
    """构建不同风格与语种的开场台词"""
    ha, hb = names["host_a"], names["host_b"]
    s = style if style in ("tech_deep", "casual_brief", "debate", "solo_read") else "tech_deep"

    if s == "solo_read":
        if lang == "zh":
            t1 = f"大家好，欢迎收听《{title}》有声精读。接下来由我为您全文朗读本篇技术原稿。"
        elif lang == "ja":
            t1 = f"皆さんこんにちは。「{title}」の音声朗読へようこそ。それでは本文を順にお届けします。"
        else:
            t1 = f"Hello and welcome to the audio narration of '{title}'. Let's walk through the full article."
        return [DialogueTurn(speaker="host_a", speaker_name=ha, text=t1, intent="intro")]

    if s == "casual_brief":
        if lang == "zh":
            t1 = f"哈喽大家好，欢迎来到技术轻快讯！我是 {ha}。今天带大家速览一份新鲜内容：《{title}》！"
            t2 = f"嗨大家好，我是 {hb}！听说这次干货满满而且非常实用。{summary[:60] + '...' if summary else '赶紧跟我们划划重点吧！'}"
        elif lang == "ja":
            t1 = f"皆さんこんにちは！サクッとわかるテクノロジー速報、{ha}です！今日は「{title}」の要点をスピーディーにお届けします！"
            t2 = f"アシスタントの{hb}です！忙しい方でもすぐ理解できる実践的なトピックですね。{summary[:60] + '...' if summary else '早速ダイジェストで教えてください！'}"
        else: # en
            t1 = f"Hey everyone, welcome to the Tech Quick Brief! I'm {ha}. Today we're taking a fast tour through '{title}'!"
            t2 = f"Hey there, {hb} here! I love topics that give us immediate takeaways. {summary[:70] + '...' if summary else 'Give us the quick highlight reel!'}"
    elif s == "debate":
        if lang == "zh":
            t1 = f"欢迎收听《观点交锋》。我是 {ha}。今天我们聚焦一个充满思辨的硬核议题：《{title}》。"
            t2 = f"我是反方观察员 {hb}。坦白讲，看到这个方案时我心里打了不少问号。{summary[:60] + '...' if summary else '我们真的有必要把事情搞得这么复杂吗？'}"
        elif lang == "ja":
            t1 = f"「視点交錯」へようこそ！{ha}です。本日は賛否や議論が分かれるテーマ、「{title}」を徹底的に戦わせます。"
            t2 = f"{hb}です。率直に言って、このアプローチにはいくつか疑問があります。{summary[:60] + '...' if summary else '本当にここまで厳格に構築する必要があるのでしょうか？'}"
        else: # en
            t1 = f"Welcome to Architectural Debate. I'm {ha}. Today we're tackling a highly contested topic: '{title}'."
            t2 = f"I'm {hb}, playing devil's advocate today. Frankly, I have skepticism about this approach. {summary[:70] + '...' if summary else 'Is all this complexity really justified?'}"
    else: # tech_deep (默认)
        if lang == "zh":
            t1 = f"大家好，欢迎收听本期技术播客！我是 {ha}。今天我们要聚焦探讨的是：《{title}》。"
            t2 = f"我是 {hb}！看到这个架构主题我特别期待。{summary[:60] + '...' if summary else '在当前复杂的工程体系下，这确实是非常关键的痛点。'} 你觉得这次最亮眼的核心是什么？"
        elif lang == "ja":
            t1 = f"皆さんこんにちは！{ha}です。今回の技術ポッドキャストでは、「{title}」について深掘りしていきます。"
            t2 = f"パートナーの{hb}です！このテーマは今まさに現場で議論されている重要トピックですね。具体的にはどこが一番のポイントでしょうか？"
        else: # en
            t1 = f"Hello and welcome back to our tech podcast. I'm {ha}, and today we're unpacking '{title}'."
            t2 = f"Hey everyone, {hb} here! I've been really looking forward to this topic. {summary[:80] + '...' if summary else 'It addresses some crucial engineering challenges.'} What stood out most to you?"

    return [
        DialogueTurn(speaker="host_a", speaker_name=ha, text=t1, intent="intro"),
        DialogueTurn(speaker="host_b", speaker_name=hb, text=t2, intent="question")
    ]


def build_discussion_turns(
    sections: List[Dict[str, Any]], lang: str, style: str, names: Dict[str, str], max_turns: int
) -> List[DialogueTurn]:
    """构建多轮交替探讨（深度/快讯/辩论）"""
    turns: List[DialogueTurn] = []
    ha, hb = names["host_a"], names["host_b"]
    s = style if style in ("tech_deep", "casual_brief", "debate", "solo_read") else "tech_deep"

    for idx, sec in enumerate(sections):
        if len(turns) >= max_turns:
            break
        h_text = sec["heading"]
        snippets = sec["body"]
        main_p = snippets[0] if snippets else ""
        sub_p = snippets[1] if len(snippets) > 1 else ""

        if s == "solo_read":
            if lang == "ja":
                p_text = f"続いて「{h_text}」についてです。{main_p}" if idx > 0 else f"まず「{h_text}」についてです。{main_p}"
            elif lang == "en":
                p_text = f"Moving to: {h_text}. {main_p}" if idx > 0 else f"First, looking at: {h_text}. {main_p}"
            else:
                p_text = f"章节：{h_text}。{main_p}" if idx > 0 else f"第一部分：{h_text}。{main_p}"
            turns.append(DialogueTurn(speaker="host_a", speaker_name=ha, text=p_text, intent="explanation"))
            if sub_p and len(turns) < max_turns:
                turns.append(DialogueTurn(speaker="host_a", speaker_name=ha, text=sub_p, intent="explanation"))
            continue

        if s == "casual_brief":
            a_speech, b_speech, a_ans = _casual_brief_dialogue(idx, h_text, main_p, sub_p, lang)
        elif s == "debate":
            a_speech, b_speech, a_ans = _debate_dialogue(idx, h_text, main_p, sub_p, lang)
        else:
            a_speech, b_speech, a_ans = _tech_deep_dialogue(idx, h_text, main_p, sub_p, lang)

        turns.append(DialogueTurn(speaker="host_a", speaker_name=ha, text=a_speech, intent="explanation"))
        if sub_p and b_speech and len(turns) < max_turns:
            turns.append(DialogueTurn(speaker="host_b", speaker_name=hb, text=b_speech, intent="question"))
            if a_ans and len(turns) < max_turns:
                turns.append(DialogueTurn(speaker="host_a", speaker_name=ha, text=a_ans, intent="explanation"))

    return turns


def _tech_deep_dialogue(idx: int, h: str, main_p: str, sub_p: str, lang: str):
    is_spec = any(kw in sub_p for kw in (":", "：", "如", "包括", "例如", "支持", "矩阵", "配置", "例", "such as", "including", "config"))
    if lang == "zh":
        a = f"首先来看它的第一道基石：{h}。{main_p}" if idx == 0 else f"这直接引出了下一核心模块：{h}。{main_p}"
        b = "理解了。那在这一模块中，相关的具体规约与细分项又是如何落地的呢？" if is_spec else "很有意思！那在面对复杂的工程落地场景时，这套架构是如何保证高可用与健壮性的呢？"
        ans = f"在具体的规约定义上：{sub_p}" if is_spec else f"关键就在于其设计遵循了低耦合与防御性机制。{sub_p}"
    elif lang == "ja":
        a = f"まず注目すべきは「{h}」です。{main_p}" if idx == 0 else f"続いての重要なポイントは「{h}」です。{main_p}"
        b = "なるほど。具体的にはどのような仕様や設定項目が定められているのでしょうか？" if is_spec else "なるほど！そうすると実際の運用や拡張性という点では、どのように信頼性を担保しているのでしょうか？"
        ans = f"詳細な仕様と定義内容については：{sub_p}" if is_spec else f"重要なのは、疎結合かつ堅牢な防御的設計に従っている点です。{sub_p}"
    else:
        a = f"Let's dive into the core foundation first: {h}. Specifically, {main_p}" if idx == 0 else f"That brings us to another critical piece: {h}. Specifically, {main_p}"
        b = "Understood. How are the specific configurations and concrete specifications structured here?" if is_spec else "That makes total sense! How does the architecture maintain stability and efficiency in complex production scenarios?"
        ans = f"Looking at the concrete parameters and specification details: {sub_p}" if is_spec else f"The secret lies in its decoupled, defensive design. {sub_p}"
    return a, b, ans


def _casual_brief_dialogue(idx: int, h: str, main_p: str, sub_p: str, lang: str):
    if lang == "zh":
        a = f"咱们直奔主题！首先最值得关注的亮点就是：{h}。通俗来说呢：{main_p}" if idx == 0 else f"再来看另一个超实用的地方：{h}。简单来说：{main_p}"
        b = "哇，听起来省事多了！那对于实际使用来说，最大的好处到底是什么？"
        ans = f"简单一句话：少走弯路、效率倍增。你看：{sub_p}"
    elif lang == "ja":
        a = f"それでは早速行きましょう！まず押さえておきたい目玉は「{h}」です。分かりやすく言うと：{main_p}" if idx == 0 else f"続いてもうひとつの便利ポイントは「{h}」です。要するに：{main_p}"
        b = "おお、それはかなり楽になりますね！実際に使う人にとって一番嬉しいメリットは何でしょうか？"
        ans = f"ズバリ、手間の削減と圧倒的なスピード感です。例えば：{sub_p}"
    else:
        a = f"Straight to the point! The first big highlight is: {h}. In plain terms, {main_p}" if idx == 0 else f"Next up, another super handy highlight: {h}. Basically, {main_p}"
        b = "Wow, that sounds so much easier! What's the single biggest win for everyday users?"
        ans = f"In one word: pure productivity without friction. Check this out: {sub_p}"
    return a, b, ans


def _debate_dialogue(idx: int, h: str, main_p: str, sub_p: str, lang: str):
    is_spec = any(kw in sub_p for kw in (":", "：", "如", "包括", "例如", "支持", "矩阵", "配置"))
    if lang == "zh":
        a = f"我们先看它的核心立论：{h}。其背后的设计取向是：{main_p}" if idx == 0 else f"不仅如此，更关键的争议点在于下一层：{h}。其机制在于：{main_p}"
        b = "等等！这里列出的细项看似规整，但实际工程中真有必要定义得这么严密吗？会不会限制了业务灵活性？" if is_spec else "等等！我必须提出异议。现实中自建这套规范的学习与维护成本有多大？直接用现成的外部工具不好吗？"
        ans = f"看似约束，实则是跨团队协同与规模化发行时不踩坑的防波堤。你看：{sub_p}" if is_spec else f"外部方案看似省事，但这正是要区分'短期便利'与'长期架构主权'的关键。你看：{sub_p}"
    elif lang == "ja":
        a = f"まず主張の根幹となる「{h}」から見ていきましょう。その論拠は明確です：{main_p}" if idx == 0 else f"さらに議論の焦点となるのが次のレイヤー、「{h}」です。メカニズムは：{main_p}"
        b = "ちょっと待ってください！現実的に学習や運用のコストが高すぎませんか？既存の外部ツールで十分では？"
        ans = f"短期的な手軽さと、長期的なデータと配信の主権の確保は明確に区別すべきです。実際：{sub_p}"
    else:
        a = f"Let's examine the foundational premise: {h}. The underlying stance is: {main_p}" if idx == 0 else f"Furthermore, a critical point of contention lies in the next piece: {h}. Specifically: {main_p}"
        b = "Hold on, I have to challenge that! Isn't the maintenance overhead too high? Why not just use existing third-party platforms?"
        ans = f"Third-party setups look convenient upfront, but that conflates short-term ease with long-term sovereignty. Notice: {sub_p}"
    return a, b, ans


def build_outro_turns(title: str, lang: str, style: str, names: Dict[str, str]) -> List[DialogueTurn]:
    """构建不同风格与语种的收束台词"""
    ha, hb = names["host_a"], names["host_b"]
    s = style if style in ("tech_deep", "casual_brief", "debate", "solo_read") else "tech_deep"

    if s == "solo_read":
        if lang == "zh":
            t1 = f"以上便是《{title}》的全部内容。完整图文、架构细节与代码范例，欢迎前往文库查阅。感谢您的收听！"
        elif lang == "ja":
            t1 = f"以上、「{title}」の全編をお届けしました。図解やコードの詳細については、公式サイトをご覧ください。ご清聴ありがとうございました！"
        else:
            t1 = f"That concludes the reading of '{title}'. For code samples and details, please refer to the written article. Thanks for listening!"
        return [DialogueTurn(speaker="host_a", speaker_name=ha, text=t1, intent="outro")]

    if s == "casual_brief":
        if lang == "zh":
            t1 = f"短短几分钟，是不是已经对《{title}》有了一个全面而清晰的速览？"
            t2 = "确实，信息量很足而且完全不枯燥！更多完整图文欢迎前往我们的独立站查阅。感谢大家的收听，下期再见！"
        elif lang == "ja":
            t1 = f"あっという間でしたが、「{title}」の要点がギュッと掴めましたね！"
            t2 = "はい、短時間で本質がよく分かりました！詳細はぜひ公式サイトをチェックしてくださいね。ではまた！"
        else: # en
            t1 = f"In just a few minutes, that wraps up our quick-fire tour of '{title}'!"
            t2 = "Awesome, packed with value and straight to the point! Check out our website for full details, and see you next time!"
    elif s == "debate":
        if lang == "zh":
            t1 = f"一番交锋下来，相信大家对《{title}》背后的架构取舍已经有了自己的判断。没有完美的方案，只有契合长远目标的抉择。"
            t2 = "虽然我依然保留部分质疑，但这套设计在自主可控上的硬功夫确实值得思考。欢迎在评论区留下你的立场，我们下期辩论见！"
        elif lang == "ja":
            t1 = f"白熱した議論を経て、「{title}」のトレードオフが浮き彫りになりました。目的に適したアーキテクチャの選択こそが本質ですね。"
            t2 = "懸念点はあるものの、自律的な主権性を守る徹底した設計思想には納得です。皆さんはどう思われましたか？それではまた次回！"
        else: # en
            t1 = f"After this debate, the trade-offs behind '{title}' are crystal clear. There are no silver bullets, only architectural decisions aligned with long-term goals."
            t2 = "While I still have my reservations, the engineering dedication to true sovereignty here is impressive. Where do you stand? See you in the next debate!"
    else: # tech_deep
        if lang == "zh":
            t1 = f"聊到这里，整个《{title}》的脉络就非常清晰了。核心就是通过系统化工程把复杂性收敛在底层。"
            t2 = "没错！非常过瘾的一次深度复盘。想要查看本文的完整图文与代码实现，欢迎前往我们的独立站查阅。感谢大家的收听，我们下期见！"
        elif lang == "ja":
            t1 = f"これで「{title}」の全体像がはっきりと見えてきましたね。"
            t2 = "はい、非常に実践的な洞察が得られました！詳細なコードや図解はぜひ公式サイトをご覧ください。それではまた次回お会いしましょう！"
        else: # en
            t1 = f"Wrapping it all up, the key takeaway from '{title}' is how disciplined engineering abstracts away system complexity."
            t2 = "Absolutely! A fantastic breakdown today. You can explore the complete article and reference implementations on our website. Thanks for tuning in, and see you next time!"

    return [
        DialogueTurn(speaker="host_a", speaker_name=ha, text=t1, intent="summary"),
        DialogueTurn(speaker="host_b", speaker_name=hb, text=t2, intent="outro")
    ]
