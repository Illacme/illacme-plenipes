# 🔒 Illacme Plenipes 隐私与遥测声明 (Privacy Policy & Telemetry Disclosure)

**版本**：V1.0  
**生效日期**：2026年08月17日  

---

## 核心原则：默认不上传、极简透明

**Illacme Plenipes** 坚守隐私即权利的准则。本软件绝不将用户内容用作 AI 训练数据，绝不上传私有文稿，绝不追踪用户的创作灵感。

---

## 1. 我们收集什么与不收集什么

### 🚫 我们绝对不收集：
1. **您的原稿内容**：Markdown 正文、Frontmatter 敏感数据、本地图片与多媒体。
2. **您的私有密钥**：API Key、GitHub Token、S3 Secret Key 等凭据仅存留在本地配置或加密存储区，绝不上报。
3. **您的个人隐私信息**：设备通讯录、个人位置或非软件运行相关的操作系统数据。

### 📊 极简技术信息（仅在用户显式开启遥测时）：
1. **操作系统环境**：OS 类型（macOS / Linux / Windows）、Python 运行时版本、Node 运行时版本（用于排查兼容性问题）。
2. **崩溃堆栈信息**：匿名化的未捕获异常堆栈（已剥离文件绝对路径中的用户名与私有文本）。
3. **版本更新检查**：向官方版本服务器请求最新发布号（仅包含当前软件版本号）。

---

## 2. 遥测控制权与可审计性

2.1 **默认关闭**：系统的遥测与匿名崩溃上报在安装后默认为关闭状态。  
2.2 **用户主权开关**：创作者可在 `治理中心 -> 基础配置与运维 -> 运行基座` 中随时开启或关闭遥测日志采集。  
2.3 **本地日志透明可读**：所有系统运行日志（如 `plenipes.log`、`plenipes_api.log`）均明文保存在本地 `logs/` 目录中，用户可随时审查。  

---

## 3. 联系方式与隐私权利

如果您对本软件的数据处理实践有任何疑问，或需要请求协助，请联系官方维护团队：
- 官方仓库：[https://github.com/Illacme/illacme-plenipes](https://github.com/Illacme/illacme-plenipes)
- 漏洞报告：请参阅 [SECURITY.md](file:///Volumes/Notebook/omni-hub/illacme-plenipes/SECURITY.md)

---

*Illacme Plenipes 隐私与合规组*
