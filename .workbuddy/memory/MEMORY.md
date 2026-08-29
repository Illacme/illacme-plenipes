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
