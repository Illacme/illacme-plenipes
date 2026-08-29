# 🤝 Illacme-plenipes 贡献指南 (CONTRIBUTING)

感谢您关注 Illacme-plenipes！作为一个工业级的知识同步引擎，我们欢迎任何形式的贡献，包括功能建议、代码修复、文档优化或架构改进。

## 1. 核心治理准则 (Governance)

由于本项目对**代码稳定性**和**文档完整性**有极高要求，所有贡献者必须遵守以下准则：

1.  **注释优先**：所有核心逻辑修改必须附带详尽的中文注释。
2.  **防御性设计**：严禁移除现有的错误处理逻辑。
3.  **规则绑定**：本项目使用 `.antigravityrules` 进行自动化质量治理，任何 PR 都必须通过该规则集的完整性校验。

## 2. 开发者环境配置

1.  **克隆仓库**：
    ```bash
    git clone https://github.com/Illacme/illacme-plenipes.git
    cd illacme-plenipes
    ```
2.  **安装依赖**：
    ```bash
    pip install -r requirements.txt
    ```
3.  **运行测试**：
    我们在 `tests/` 目录下提供了一系列测试脚本。在提交 PR 前，请确保：
    ```bash
    python3 -m unittest discover tests
    ```

## 3. 代码提交规范 (PR Flow)

1.  **Fork 并创建分支**：建议分支命名格式为 `feature/your-feature` 或 `fix/your-patch`。
2.  **保持原子提交**：每一个提交（Commit）应只解决一个具体问题。
3.  **更新文档**：如果您修改了用户界面、配置参数或核心逻辑，请**务必**同步更新 `docs/` 下的对应文档。

## 4. 贡献者许可约定 (Contributor License Terms)

通过向本项目提交 Pull Request、Issue 或补丁代码，您即表示同意：
1. 您所提交的代码与文档为您原创，或您拥有合法再授权之权利；
2. 您授予本项目维护团队对您的贡献内容进行合并、修改、发布以及在双重许可（开源许可与商业许可）模式下进行商业分发的永久性、全球性许可；
3. 本项目核心开源代码库严格遵循 [PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0/) 协议。

## 5. 获取帮助

如果您对架构有疑问，请先阅读 **[技术规格书 (SPECIFICATION)](./docs/SPECIFICATION.zh-CN.md)**。

---
> [!TIP]
> **商业授权说明**：开源版本仅供非商业学习与个人使用。任何用于商业运营、闭源分发或企业级部署的需求，请参阅 **[商业最终用户许可协议 (EULA)](./docs/legal/EULA.md)** 或与核心维护团队联系。

