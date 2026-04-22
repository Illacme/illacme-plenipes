# Boot Sequence Injection 验收报告

## 核心改造
将三层上下文入口（`.antigravityrules`、`.cursorrules`、全局 KI `protocols.md`）从"温柔的暗示型提示"升级为"强制 API 动作型命令"。

未来任何 AI 智能体进入 Illacme-plenipes 工程时，无论是 Antigravity、Cursor、还是其他兼容代理，都将在第一回合被迫执行 `view_file .plenipes/rules.md`，从而彻底杜绝"愣头青"式的无脑开局。

## 三层防线拓扑
1. **项目层 `.antigravityrules`**：Antigravity 专属入口，写有最高裁量级 WARNING。
2. **项目层 `.cursorrules`**：Cursor IDE 专属入口，同样强制读盘。
3. **全局层 KI `protocols.md`**：跨项目持久记忆，写有 BSR 协议第十章，确保即使项目文件被跳过，全局记忆也会触发条件反射。

这是一次针对 AI 认知层面的根本性改造：从"相信 AI 会自觉"到"强制 AI 必须执行"。
