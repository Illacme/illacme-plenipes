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

## 4. 获取帮助

如果您对架构有疑问，请先阅读 **[技术规格书 (SPECIFICATION)](./docs/SPECIFICATION.zh-CN.md)**。

---
> [!TIP]
> **商业授权说明**：本项目采用 CC BY-NC 4.0 协议。任何旨在商业化的修改或二次分发，请务必提前与核心维护者联系。
