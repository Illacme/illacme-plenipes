# 🛡️ Illacme Plenipes | 物理主权治理协议 (Sovereignty Protocol)

## 1. 物理红线：端口锁定 (Port Sovereignty Lock)
本协议定义了引擎运行的物理基石。**严禁任何 AI 助理或自动化脚本在未获得人类用户明确指令的情况下修改以下参数：**

| 参数项 | 标准端口 | 职责描述 | 治理优先级 |
| :--- | :--- | :--- | :--- |
| `system.singleton_port` | **43210** | 进程单例防抖锁，确保全库数据一致性。 | **最高 (CRITICAL)** |
| `system.wizard_port` | **43211** | 零配置自举向导 (Magic Onboarding) 专用端口。 | **高 (HIGH)** |
| `system.api_port` | **43212** | 治理控制台 (Dashboard) 及实时事件流后端。 | **最高 (CRITICAL)** |
| `system.serve_port` | **43213** | 本地静态资源预览容器。 | **高 (HIGH)** |

## 2. 冲突解决准则 (Conflict Resolution)
如果系统启动提示端口被占用：
- 43212: Governance API (API/仪表盘)
- 43213: Preview Serve (本地预览)
- **配置分层协议**：必须严格执行 `Local > Imprint > Base` 的优先级，严禁将 API Keys、端口号、物理路径写入 `config.yaml`。
- **冲突解决**：遇到端口占用，优先执行 pkill -9 -f python 清理残留进程，或通过 `lsof -i :PORT` 手动干预。

## 3. 配置文件保护 (Config Integrity)
`config.yaml` 中的 `system` 段落受此协议物理保护。任何导致端口变动的 `sed` 或 `replace` 操作均视为违背主权治理原则。

## 4. 配置分层治理协议 (Config Layering Protocol)
为确保系统具备工业级可移植性与物理安全性，必须严格执行以下三层叠加规则：

| 配置层级 | 物理文件 | 职责范围 | 优先级 |
| :--- | :--- | :--- | :--- |
| **本地层 (Local)** | `config.local.yaml` | 物理指纹：端口号、API Keys、本地绝对路径、环境开关。 | **1 (Highest)** |
| **版图层 (Imprint)** | `imprints/*/configs/config.imprint.yaml` | 业务主权：版图名、语种矩阵、翻译策略、SSG 路径。 | **2** |
| **基础层 (Base)** | `config.yaml` | 架构模板：全域默认值、无环境依赖的通用设置。 | **3 (Lowest)** |

**【强制动作】**：严禁在 `config.yaml` 中写入属于“本地层”的私有参数。严禁在“版图层”硬编码属于“物理层”的端口号。

---
**Protocol Status: [LOCKED]**
**Compliance Level: Industrial Grade**
