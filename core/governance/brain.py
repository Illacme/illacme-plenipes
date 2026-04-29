import os
import json
import logging
from datetime import datetime

from core.utils.tracing import tlog

class KnowledgeService:
    """🧠 [V11.0] 知识沉淀中心：自动化教训累积与自愈经验管理"""

    # 💊 [V11.0] 语义转换器：将技术黑话翻译成用户价值
    USER_LABELS = {
        "MASK_INTEGRITY": "AI 幻觉拦截 & 格式自愈",
        "SOVEREIGNTY_SHIELD": "核心资产/品牌标签保护",
        "SEO_ALIGNMENT": "SEO 权重对齐与精度优化"
    }

    # 💊 [V10.4] 专家级自愈指令集 (Structured Remedy Library)
    REMEDY_MAP = {
        "MASK_INTEGRITY": """
### EXPERT GUIDELINE: MASK PROTECTION ###
* NEGATIVE: AI modified or removed [[STB_MASK_n]] placeholders.
* MANDATE: You MUST preserve all [[STB_MASK_n]] tags exactly as they appear in the source. Do not translate or modify them.
""",
        "SOVEREIGNTY_SHIELD": """
### EXPERT GUIDELINE: BRAND SOVEREIGNTY ###
* NEGATIVE: Critical sovereignty tags like [[AEL-Iter-ID]] were lost.
* MANDATE: You MUST include the [[AEL-Iter-ID: {iter_id}]] tag in your response.
""",
        "SEO_ALIGNMENT": """
### EXPERT GUIDELINE: SEO PRECISION ###
* NEGATIVE: Metadata structure was corrupted or inconsistent.
* MANDATE: Ensure JSON keys are lowercase and keywords are provided as a list of strings.
"""
    }
    def __init__(self, engine):
        self.engine = engine
        self.brain_root = engine._resolve_path("metadata/brain")

        os.makedirs(self.brain_root, exist_ok=True)
        self.lessons_path = os.path.join(self.brain_root, "lessons_learned.json")
        self._load_lessons()

    def _load_lessons(self):
        if os.path.exists(self.lessons_path):
            try:
                with open(self.lessons_path, 'r', encoding='utf-8') as f:
                    self.lessons = json.load(f)
            except Exception:
                self.lessons = []
        else:
            self.lessons = []

    def log_lesson(self, category, error_msg, context_data=None):
        """记录一个新教训，避免系统在未来重复同样的错误"""
        lesson = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "error": error_msg,
            "context": context_data or {},
            "iter_id": getattr(self.engine, 'ael_iter_id', 'V11.0')
        }

        # 简单去重：如果最近有相同的错误，则只更新时间
        if self.lessons and self.lessons[-1]["error"] == error_msg:
            self.lessons[-1]["timestamp"] = lesson["timestamp"]
        else:
            self.lessons.append(lesson)
            # 保持最近 100 条教训
            if len(self.lessons) > 100:
                self.lessons = self.lessons[-100:]

        self._save_lessons()
        tlog.info(f"🧠 [知识沉淀] 已记录新教训: {category} - {error_msg[:50]}...")

    def _save_lessons(self):
        try:
            with open(self.lessons_path, 'w', encoding='utf-8') as f:
                json.dump(self.lessons, f, indent=2, ensure_ascii=False)
        except Exception as e:
            tlog.error(f"⚠️ [知识中心] 存储教训失败: {e}")

    def get_summary(self):
        """获取教训汇总，用于仪表盘展示"""
        return {
            "total_lessons": len(self.lessons),
            "recent_failures": [l["error"] for l in self.lessons[-5:]],
            "categories": list(set(l["category"] for l in self.lessons))
        }

    def get_remedy(self, category):
        """根据错误类别获取补救指令"""
        return self.REMEDY_MAP.get(category)
