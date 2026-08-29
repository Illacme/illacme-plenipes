# 项目长期记忆 (Illacme Plenipes)

## 许可与版权
- 默认许可证：PolyForm Noncommercial License 1.0.0（他人克隆后仅可非商业使用；商业使用须取得版权所有者单独书面授权）。
- 版权所有者：**Eason.Bai**；商业授权联系邮箱：**wqbyc@msn.com**（见 `LICENSE` 第 1 行 Required Notice 与 `COMMERCIAL_LICENSE.md` “如何取得商业授权”一节）。
- 商业授权 EULA 全文：`docs/legal/EULA.md`。
- 注意：用户 AI 自媒体人设（markdown 账号）不公开真实姓名；但“Eason.Bai / wqbyc@msn.com”是代码仓库的法定版权所有者信息，已公开写入 LICENSE，属授权范围内的合法披露。

## 治理门禁要点
- 提交门禁是 `.githooks/pre-commit`（非 `scripts/sovereign_audit.py`）；红线豁免依赖 `exemption_loader.load_redline_exemptions()`。
- 钩子运行环境（托管 python 3.13.12）**无 PyYAML**，`exemption_loader.py` 已内置降级解析器兜底，豁免白名单不会静默失效。
- `.plenipes/` 整目录 gitignored，属本地治理基建（exemptions.yaml / sentinel_matrix.py / exemption_loader.py / SESSION_SNAPSHOT.md 均不入库）。
- `scripts/` 也被 gitignore，`sovereign_audit.py` 等属本地治理工具，改动不入库。

## 设计系统陷阱（dashboard CSS / SOP-03）
- `dashboard.tokens.css` 的 `--color-white`/`--color-black` 是**语义令牌且按主题反转**：`:root`(默认深色) 下 `--color-white:#fff`、`--color-black:#000`；`[data-theme="light"]` 下 `--color-white:#000`、`--color-black:#fff`。即**白天模式下 `--color-white` 实际是黑色**。
- 因此 SOP-03"禁止硬编码 #fff/#000"在本仓库 dashboard 里是**误报**：白字/白底在品牌色按钮与白天覆盖层必须用字面量 #fff/#000（设计系统无"始终白色"令牌）。机械把 #fff 换成 var(--color-white) 会让白天模式的 `background` 变黑。
- 硬编码色豁免清单：`.githooks/pre-commit` 的 `EXEMPT_CSS_SUFFIXES` 与 `scripts/sovereign_audit.py` 的 `EXEMPT_CSS` 已含 7 个 dashboard CSS 文件（tour/discovery/components/overrides/header/strategy/overview）。**新增白/黑字面量时勿再"修复"成令牌**。
- 预存项：`theme.light.overrides.css:34` 的 `[data-theme=light] .review-input { background: var(--color-white) }` 是改动前即存在的白天黑底输入框，非回归，单独待议。
