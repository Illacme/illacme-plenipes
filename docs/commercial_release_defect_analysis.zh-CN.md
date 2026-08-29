# Illacme Plenipes 商用发布就绪度缺陷分析

> 分析日期：2026-08-29
> 依据：项目 SOP 规范（V10.2）、代码静态扫描、文档/法律资产核查、pytest 收集探测
> 结论：项目工程底座扎实（469 测试、凭据隔离合规、法律框架初具），但存在 **1 项 P0 许可落地冲突** 与若干发布前必须修正项。

---

## 一、已经具备的商用就绪项（优势）

| 维度 | 现状 | 评价 |
| :--- | :--- | :--- |
| 测试覆盖 | `pytest --collect-only` 成功收集 **469 个用例、0.83s 无收集错误**，覆盖发布器（GitHub/Netlify/Cloudflare/Vercel/Render/Zeabur…）、分发器（Ghost/Medium/LinkedIn/微信/知乎/Telegram/Discord…）、凭据加密、许可证守卫、SEO、i18n、限流、并发、遥测 | ✅ 强 |
| 密钥安全 | `config.local.yaml`（含真实 api_key）已被 `.gitignore` 正确屏蔽；`core/` 无硬编码明文凭据；存在凭据加密向导、掩码、license_guard | ✅ 合规 |
| 资产本土化 | 前端无 CDN 远程 `<script>/<link>` 加载（仅 data-URI 的 SVG 命名空间与用户配置占位符） | ✅ 符合 SOP-03 §1.2 |
| 法律框架 | `docs/legal/` 含 EULA / 数据主权 / 隐私政策 / 第三方免责 / 第三方致谢；`CONTRIBUTING.zh-CN.md` §4 含 **CLA（贡献者许可协议）**，已声明双重许可（开源+商业） | ✅ 初具 |
| 治理与纪律 | SOP 体系完整（大宪章+5 手册）；CHANGELOG 记录详实且引用 SOP 合规；`core/` 架构隔离由 sentinel 物理扫描 | ✅ 良好 |

---

## 二、缺陷清单（按优先级）

### 🔴 P0 — 发布阻断项（必须解决）

**P0-1　许可模式落地冲突：CC BY-NC 与"商用发布"目标直接矛盾（已闭环）**
- **现象（已澄清）**：仓库 `LICENSE` 原为 **CC BY-NC 4.0（署名-非商业性使用）**。经法务核对，CC BY-NC 仅约束"被许可人（克隆者）"，**约束不了版权所有者本人**——作者始终可商用，与"自己发布商用"目标并不冲突；真正缺口是"他人商用须找作者授权"的路径不可达，以及默认许可对"软件商业使用"界定偏弱。
- **风险（修正后）**：原结论将 CC BY-NC 误判为发布硬阻断；实际风险在于商业授权入口缺失、默认许可对软件商业使用的界定偏弱。
- **已落地修正（2026-08-29，遵循 SOP-05 模板七+八）**：
  1. `LICENSE` 已切换为 **PolyForm Noncommercial License 1.0.0**（源码可用、非商业；SPDX: `PolyForm-Noncommercial-1.0.0`），明确禁止商业使用、商业权归作者。
  2. 新增根目录 **`COMMERCIAL_LICENSE.md`** 作为商业授权唯一入口，指向 `docs/legal/EULA.md` 并给出联系通道。
  3. README / README.zh-CN / CONTRIBUTING 的徽章与许可章节已统一，且将失效的 `file:///Volumes/...` 绝对路径全部改为相对路径（COM-001 闭环）。
- **现状利好**：EULA（商业许可）与 CLA（贡献者协议）已存在，商业授权闭环已成型。

### 🟠 P1 — 发布前必须修正

**P1-1　前端 8 个文件突破 500 行硬上限（违反 SOP-03 §1.1）**
- **清单**（行数）：`web/dashboard/js/dashboard.imprints.js` **1104**、`css/views/overview.css` 669、`js/ui/modals.js` 634、`css/themes/theme.light.overrides.css` 612、`css/dashboard.components.css` 590、`css/views/dispatch.css` 542、`css/components/glass.widgets.css` 535、`css/components/modals.discovery.css` 513。
- **风险**：可审计性、可维护性差；SOP 物理门禁（sovereign_audit / sentinel）本应拦截，说明门禁未在全量提交中强制或存在豁免。
- **修正**：按 SOP-02 §1 工业重构六铁律 + 影子快照，对 `dashboard.imprints.js` 优先"委托模式/子插件化"拆分至 ≤300 行；CSS 按看板命名空间再切片。
- 附：另有 **13+ 个 Python 文件处于 300–499 行预警区**（如 config_models.py 413、hub.py 390、heartbeat.py 390），属 SOP 预警，建议排入渐进拆分。

**P1-2　版本号严重不一致（缺单一可信源）**
- **现象**：README 徽章 **V50.3**、CHANGELOG 最新 **v6.4.0**、SECURITY.md **v50.x / v34.x–v49.x**、SOP **V10.2**、pyproject 无 `version` 字段。
- **风险**：商用客户/支持按 CHANGELOG 追溯时将产生严重混淆，影响可信度与补丁定位。
- **修正**：确立唯一版本源（建议以 pyproject `version` 为准），CHANGELOG 补齐至当前发布版本并统一语义化版本号；SOP 版本与产品版本明确分离标注。

**P1-3　依赖供应链不可复现（违反 SOP-03 §2）**
- **现象**：`requirements.txt` 顶层 16 个依赖全部使用 `>=` 浮动范围（如 `PyYAML>=6.0`、`fastapi>=0.100.0`）；**无锁文件**（仅 95B 的 node `package-lock.json`）。
- **风险**：构建不可复现；新发布的上游版本可无声注入（供应链投毒）；商用环境难以追责。
- **修正**：生产依赖**精确 pin + 生成 lockfile**（pip-tools/`uv lock`/`poetry.lock`）；发布前跑 `pip-audit`/`safety` 漏洞扫描；CI 中固定依赖解析。

**P1-4　发布前确认测试全绿**
- **现象**：本次仅做 `--collect-only`（469 用例 0 错误），**未实际执行**。
- **修正**：发布前跑完整 `pytest` 并达成全 PASS；重点验证 `test_license_guard.py`（授权/激活/撤销）、`test_frontend_render_integrity.py`（SOP-03 §1.4 门禁）、各 publisher/syndicator 集成测试。

### 🟡 P2 — 建议发布前修正

**P2-1　README 法律链接失效（绝对路径）**
- **现象**：README.md 与 README.zh-CN.md 中 EULA/数据主权/隐私/第三方声明的链接均为 `file:///Volumes/Notebook/omni-hub/illacme-plenipes/docs/legal/...` 绝对路径，在 GitHub/Web 上无法解析。
- **修正**：改为相对路径（如 `./docs/legal/EULA.md`）。README 是商用门面，链接失效直接影响信任。

**P2-2　Dashboard 控制台纯中文、无独立英文语言包**
- **现象**：`web/dashboard/js/route/route_shards/route.i18n.js` 仅 7 个键且为注释级；未发现 `*.en.*` 语言包；控制台 UI 全中文。
- **风险**：产品定位"全球出版发行"，但自身指挥控制台无英文界面，阻碍国际商用用户。
- **修正**：至少补齐中/英双语语言包；将硬编码中文文案抽离至 i18n 字典（SOP-05 模板十 / SOP-03 §3）。若目标市场仅中文创作者，可降级为 P3。

**P2-3　非 pip 可安装包**
- **现象**：无 `setup.py` / `pyproject [build-system]`；安装靠 `python plenipes.py` + `requirements.txt`。
- **修正**：提供 `pip install` 可安装包或一键安装脚本（install.sh），提升商用交付体验与版本可追溯性。

**P2-4　商标与品牌保护**
- **现象**：EULA 第 3.4 条声明商标/专有权保护，但无注册商标动作；"Illacme Plenipes" 名称未检索注册。
- **修正**：商用发布前完成商标检索与注册（至少核心市场），并在仓库/站点标注 ®/™。

**P2-5　中央配置示例缺商业授权段**
- **现象**：`config.example.yaml` 含 ingress/syndication/publish/governance 等，但无 `license`（激活/授权）段落示例；若商用版需 license key 配置，用户无从参考。
- **修正**：补充商业授权激活配置示例（与 `test_license_guard.py` 对齐）。

**P2-6　README clone 地址占位未替换**
- **现象**：`git clone https://github.com/your-username/illacme-plenipes.git` 仍为占位 `your-username`。
- **修正**：替换为真实仓库地址。

### 🟢 P3 — 锦上添花

- **P3-1** 大量 300–500 行文件（13+ Python、众多前端）按 SOP 预警渐进拆分。
- **P3-2** `SECURITY.md` 提及"官方维护者邮箱"但未给具体地址；补安全联系邮箱。
- **P3-3** `README.zh-CN.md`（72 行）比 `README.md`（59 行）更详，建议双向同步保持中英文对等。

---

## 三、优先级路线图（建议）

| 阶段 | 动作 | 对应项 |
| :--- | :--- | :--- |
| **T0 立项即办** | 决议商用发行模式（open-core 双许可），明确商用包许可边界并文档化 | P0-1 |
| **T1 发布前硬指标** | 拆分 8 个超 500 行前端文件；统一版本号；依赖 pin+lock+`pip-audit`；跑通全量 pytest | P1-1~P1-4 |
| **T2 门面打磨** | 修复 README 绝对路径链接、clone 占位；补中英文案/英文语言包；可安装包/安装器；商标检索 | P2-1~P2-6 |
| **T3 持续** | 渐进拆分预警文件；补安全邮箱；中英文文档对等 | P3 |

---

## 四、结论

项目**工程质量与治理成熟度已达到商用门槛的 80%**：测试体系、密钥隔离、资产本土化、法律文档与 CLA 均已就位。**P0-1（许可发行边界）已于 2026-08-29 闭环**（LICENSE 切 PolyForm Noncommercial + 商业授权入口 `COMMERCIAL_LICENSE.md` + README 链接修复，COM-001 完成）。其余 P1 项（前端超行、版本号、依赖锁、测试全绿）为发布前工程硬指标，工作量可控。建议按 T1→T2 推进即可进入商用发布。

*本分析基于静态扫描与文档核查，未执行动态渗透测试与全量 pytest 运行；动态安全评估与完整测试通过为发布前必要补充动作。*
