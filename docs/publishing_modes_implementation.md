# 出版模式 (Publishing Modes) 前后端优化改造方案

> 基于 `publishing_modes_design.md` 设计白皮书，对当前项目整体架构进行评估并确定改造路径。

---

## 一、现状评估 (As-Is Analysis)

### 1.1 后端架构现状

#### 配置层 (`core/config/`)
| 文件 | 现状 | 差距 |
|------|------|------|
| [config_models.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/config/config_models.py) | `SeoSettings` 仅有 4 个布尔开关（enabled, generate_description 等） | **缺少** `publishing_mode` 枚举字段和 `seo_strategy` 分级字段 |
| [models/ai.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/config/models/ai.py) | `TranslationSettings.enable_ai` 作为全局 AI 开关 | 与"出版模式"未联动，需要根据模式自动启禁 |
| [models/governance.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/config/models/governance.py) | 仅 16 行，只有预算和自动修复设置 | **缺少** 出版模式定义及其关联的 SEO 策略枚举 |

#### 加工管线层 (`core/editorial/`)
| 文件 | 现状 | 差距 |
|------|------|------|
| [standard_steps.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/editorial/standard_steps.py) | `AISlugAndSEOStep` 中 Slug 生成已有 `slug_mode` 分支（ai/物理兜底） | SEO 元数据生成**尚未**实现基于模式的策略分流 |
| [router.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/editorial/router.py) | `RouteManager` 依赖 `translator_factory` 做目录翻译 | 基础模式下需跳过 AI 调用，直接走物理规则 |

#### AI 层 (`core/logic/ai/`)
| 文件 | 现状 | 差距 |
|------|------|------|
| [ai_factory.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/logic/ai/ai_factory.py) | 硬编码加载提示词，无条件初始化 AI 节点 | 基础模式下应**完全跳过**工厂初始化 |
| [ai_logic_hub.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/logic/ai/ai_logic_hub.py) | 集中处理 Slug 清洗、SEO 生成 | 需要增加"算法对齐"和"实体增强"两种 AI SEO 策略 |

#### SEO 层
| 文件 | 现状 | 差距 |
|------|------|------|
| [sitemap_engine.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/logic/sitemap_engine.py) | 已实现 Sitemap + Hreflang 矩阵生成 | 属于"协议工程"方式的一部分，可复用 |
| **缺失** | 无独立的 SEO 处理器模块 | **需新建** `core/logic/seo/` 模块，实现策略模式 |

#### 引擎启动层 (`core/runtime/`)
| 文件 | 现状 | 差距 |
|------|------|------|
| [engine_preflight.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/runtime/engine_preflight.py) | 品牌合并时未读取 `publishing_mode` | 需要在预检阶段感知出版模式并注入上下文 |

#### API 层 (`core/api/routes/`)
| 文件 | 现状 | 差距 |
|------|------|------|
| [system.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/api/routes/system.py) | `/api/system/context` 返回品牌和 AI 信息 | **缺少** `/api/system/mode/switch` 模式切换端点 |
| [governance.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/api/routes/governance.py) | 品牌管理 API 完善 | 需要将模式切换纳入治理路由 |

### 1.2 前端架构现状

#### 仪表盘 (`core/api/static/`)
| 文件 | 现状 | 差距 |
|------|------|------|
| [index.html](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/api/static/index.html) | 5 个导航入口（全息态势/原稿金库/AI 实验室/插件矩阵/系统治理） | "AI 实验室"入口需要根据模式动态显隐 |
| [dashboard.js](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/api/static/dashboard.js) | `renderSettingsCategory` 中有品牌管理和语言策略 | **缺少** 模式选择器 UI 和联动逻辑 |

---

## 二、改造方案 (To-Be Design)

### 2.1 后端改造

#### 阶段 1：配置模型扩展 (Config Layer)

##### [MODIFY] [models/governance.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/config/models/governance.py)
新增出版模式和 SEO 策略的枚举定义：

```python
from enum import Enum

class PublishingMode(str, Enum):
    BASIC = "basic"           # 基础出版（无 AI）
    ENHANCED = "enhanced"     # 智能增强（AI SEO，无翻译）
    GLOBAL = "global"         # 全球矩阵（全量 AI）

class SeoStrategy(str, Enum):
    # 基础模式专用
    HEURISTIC = "heuristic"           # 结构化启发提取
    PROTOCOL = "protocol"             # 全维协议工程 (JSON-LD/OG/Sitemap)
    # 智能模式专用
    AI_ALIGNMENT = "ai_alignment"     # AI 算法对齐（CTR + 热词）
    AI_AUTHORITY = "ai_authority"     # AI 实体增强（Schema.org + 内链）
    # 全球模式专用
    AI_SYNC = "ai_sync"              # AI 翻译同步 SEO
    AI_LOCALIZED = "ai_localized"    # AI 本地化策略 SEO

class GovernanceSettings(BaseModel):
    publishing_mode: PublishingMode = PublishingMode.BASIC
    seo_strategy: SeoStrategy = SeoStrategy.HEURISTIC
    # ...（保留现有字段）
```

##### [MODIFY] [config_models.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/config/config_models.py)
在 `Configuration` 主模型中导出新字段，确保 API 和 Preflight 可访问：

```python
from .models.governance import PublishingMode, SeoStrategy
# governance 字段已存在，无需新增顶层字段
```

---

#### 阶段 2：SEO 处理器工厂 (SEO Engine Layer)

##### [NEW] `core/logic/seo/__init__.py`
##### [NEW] `core/logic/seo/base.py` — SEO 处理器基类

```python
class BaseSeoProcessor:
    """SEO 处理器抽象基类"""
    def process(self, ctx) -> dict:
        """返回 {description, keywords, og_title, og_image, ...}"""
        raise NotImplementedError
```

##### [NEW] `core/logic/seo/heuristic.py` — 结构化启发提取
- 从 H1 提取 title（已有逻辑，需从 `standard_steps.py` 中抽离）
- 从首段 160 字提取 description
- 从文件名/文件夹名提取 keywords

##### [NEW] `core/logic/seo/protocol.py` — 全维协议工程
- 生成 JSON-LD (Article, Breadcrumb, FAQPage)
- 生成 Open Graph 标签
- 生成 Twitter Card 标签
- 复用现有 `sitemap_engine.py` 能力

##### [NEW] `core/logic/seo/ai_alignment.py` — AI 算法对齐
- CTR 优化标题生成
- 高热词分析与埋点
- 调用 AI Provider 的 SEO Prompt

##### [NEW] `core/logic/seo/ai_authority.py` — AI 实体增强
- 知识实体提取（人/事/物）
- Schema.org 结构化数据生成
- 内链建议生成

##### [NEW] `core/logic/seo/ai_sync.py` — AI 翻译同步 SEO
- 将原稿 SEO 元信息 1:1 翻译至目标语种

##### [NEW] `core/logic/seo/ai_localized.py` — AI 本地化策略
- 针对不同语种差异化 SEO 生成

##### [NEW] `core/logic/seo/factory.py` — SEO 工厂

```python
class SeoProcessorFactory:
    @staticmethod
    def create(mode: PublishingMode, strategy: SeoStrategy) -> BaseSeoProcessor:
        mapping = {
            (PublishingMode.BASIC, SeoStrategy.HEURISTIC): HeuristicSeoProcessor,
            (PublishingMode.BASIC, SeoStrategy.PROTOCOL): ProtocolSeoProcessor,
            (PublishingMode.ENHANCED, SeoStrategy.AI_ALIGNMENT): AIAlignmentProcessor,
            (PublishingMode.ENHANCED, SeoStrategy.AI_AUTHORITY): AIAuthorityProcessor,
            (PublishingMode.GLOBAL, SeoStrategy.AI_SYNC): AISyncProcessor,
            (PublishingMode.GLOBAL, SeoStrategy.AI_LOCALIZED): AILocalizedProcessor,
        }
        cls = mapping.get((mode, strategy))
        if not cls:
            raise ValueError(f"不支持的模式-策略组合: {mode}/{strategy}")
        return cls()
```

---

#### 阶段 3：管线集成 (Pipeline Integration)

##### [MODIFY] [standard_steps.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/editorial/standard_steps.py) — `AISlugAndSEOStep`
在 SEO 处理阶段，根据当前 `publishing_mode` 和 `seo_strategy` 选择对应的处理器：

```python
# 原有逻辑: 直接调用 AI 或物理兜底
# 新逻辑:
from core.logic.seo.factory import SeoProcessorFactory

mode = ctx.engine.config.governance.publishing_mode
strategy = ctx.engine.config.governance.seo_strategy
processor = SeoProcessorFactory.create(mode, strategy)
seo_result = processor.process(ctx)
ctx.seo_data.update(seo_result)
```

##### [MODIFY] [ai_factory.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/logic/ai/ai_factory.py)
在基础模式下跳过 AI 初始化：

```python
@staticmethod
def create(trans_cfg):
    # 新增: 模式感知
    if not trans_cfg.enable_ai:
        tlog.info("📜 [基础模式] AI 算力网关已离线，使用物理规则引擎")
        return None
    # ...原有逻辑
```

##### [MODIFY] [engine_preflight.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/runtime/engine_preflight.py)
在预检阶段读取并应用出版模式：

```python
# 在品牌配置合并后，同步出版模式
if imprint_raw.get("publishing_mode"):
    config.governance.publishing_mode = imprint_raw["publishing_mode"]
if imprint_raw.get("seo_strategy"):
    config.governance.seo_strategy = imprint_raw["seo_strategy"]

# 联动: 基础模式自动禁用 AI
if config.governance.publishing_mode == "basic":
    config.translation.enable_ai = False
```

---

#### 阶段 4：API 扩展

##### [MODIFY] [system.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/api/routes/system.py) 或 [governance.py](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/api/routes/governance.py)

新增模式切换端点：

```python
@router.post("/api/system/mode/switch")
async def switch_publishing_mode(req: dict):
    """切换出版模式并热重载引擎"""
    mode = req.get("mode")        # basic / enhanced / global
    strategy = req.get("strategy") # heuristic / protocol / ai_alignment / ...
    # 1. 校验模式-策略组合的合法性
    # 2. 更新运行时配置
    # 3. 持久化到 config.imprint.yaml
    # 4. 触发引擎组件热重载
    return {"success": True, "mode": mode, "strategy": strategy}
```

新增模式查询端点（扩展 `/api/system/context`）：

```python
# 在现有 context 返回中追加:
"publishing_mode": config.governance.publishing_mode,
"seo_strategy": config.governance.seo_strategy,
```

---

### 2.2 前端改造

#### 阶段 1：模式选择器 UI

##### [MODIFY] [dashboard.js](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/api/static/dashboard.js)

在 `renderSettingsCategory` 的 `case 'imprints'` 之前（或新增 `case 'modes'`），增加"出版模式"选择卡片：

```
┌──────────────────────────────────────────────────────────────────┐
│  出版模式 (Publishing Modes)                                      │
│                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ 📜 基础出版    │  │ 🛰️ 智能增强   │  │ 🌍 全球矩阵   │             │
│  │  Basic        │  │  Enhanced    │  │  Global      │             │
│  │              │  │              │  │              │             │
│  │ 无 AI 介入    │  │ AI SEO 加速  │  │ AI 翻译+SEO  │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                    │
│  SEO 增强方式:                                                     │
│  ┌────────────────────┐  ┌────────────────────┐                   │
│  │ 🔘 [方式 A 名称]     │  │ ○  [方式 B 名称]     │                   │
│  │    方式 A 简介       │  │    方式 B 简介       │                   │
│  └────────────────────┘  └────────────────────┘                   │
└──────────────────────────────────────────────────────────────────┘
```

#### 阶段 2：导航联动

##### [MODIFY] [index.html](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/api/static/index.html)
- 为 `nav-compute`（AI 实验室）添加 `data-requires-ai="true"` 属性

##### [MODIFY] [dashboard.js](file:///Volumes/Notebook/omni-hub/illacme-plenipes/core/api/static/dashboard.js)
在 `refreshGovernanceContext` 中增加模式联动逻辑：

```javascript
// 模式联动: 根据 publishing_mode 显隐 AI 实验室
const aiLabNav = document.getElementById('nav-compute');
if (aiLabNav) {
    aiLabNav.style.display = (data.publishing_mode === 'basic') ? 'none' : 'flex';
}
```

#### 阶段 3：状态常驻

在侧边栏底部增加当前模式指示器：

```html
<div id="mode-indicator" class="context-card glass-panel small">
    <div class="metric-label">📋 出版模式</div>
    <div class="metric-value mono" id="ctx-mode">BASIC</div>
</div>
```

---

## 三、改造优先级与排期建议

| 优先级 | 改造项 | 涉及文件 | 复杂度 |
|--------|--------|----------|--------|
| P0 | 配置模型扩展（枚举 + 字段） | `models/governance.py`, `config_models.py` | 低 |
| P0 | SEO 处理器基类 + 工厂 | `core/logic/seo/` (新建) | 中 |
| P1 | 结构化提取 + 协议工程处理器 | `core/logic/seo/heuristic.py`, `protocol.py` | 中 |
| P1 | 管线集成（standard_steps 分流） | `standard_steps.py` | 中 |
| P1 | 前端模式选择器 UI | `dashboard.js` | 中 |
| P2 | AI SEO 处理器（算法对齐 + 实体增强） | `core/logic/seo/ai_*.py` | 高 |
| P2 | API 模式切换端点 | `governance.py` / `system.py` | 低 |
| P2 | 引擎预检模式感知 | `engine_preflight.py` | 低 |
| P3 | 前端导航联动与状态常驻 | `index.html`, `dashboard.js` | 低 |
| P3 | 全球模式 SEO 处理器 | `core/logic/seo/ai_sync.py`, `ai_localized.py` | 高 |

---

## 四、风险与约束

1. **300 行文件限制**：新建的 SEO 处理器每个文件需控制在 300 行以内，复杂逻辑应拆分为子模块。
2. **向后兼容**：`publishing_mode` 默认值设为 `basic`，确保未配置该字段的老用户无感升级。
3. **AI 熔断**：即使在 Enhanced/Global 模式下，AI 调用失败时必须自动回退至 Heuristic 方式，确保出版流程不中断。
4. **配置持久化**：模式切换后需同步写入 `imprints/<id>/configs/config.imprint.yaml`，确保引擎重启后状态一致。
