# Boot Sequence Injection (启动链指令强注) 设计方案

## 背景痛点
AI 智能体在跨会话重启后，虽然项目根目录下的 `.antigravityrules` 和 `.cursorrules` 写着"请包含 `.plenipes/rules.md`"，但 AI 天然具备"阅读惰性"——它认为自己已经知道了，实际上并没有物理调用工具去读取。导致每次新会话开局都像个"愣头青"，完全不知道项目有哪些纪律。

## 实施路径
1. 改写 `.antigravityrules`：从温和的路径指引升级为不可违逆的 API 动作指令（必须调用 `view_file`）。
2. 改写 `.cursorrules`：在头部追加 `BOOT SEQUENCE` 强制段落。
3. 改写全局知识库 `protocols.md`：写入跨项目持久化的 BSR (Boot Sequence Reflex) 协议。
