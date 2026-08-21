---
title: 4 端口物理单例锁与高可用容错自愈网关
layout: page
slug: process-lock-resilience-gateway
route_prefix: showcase
date: 2026-08-21
author: Illacme Sovereign Press
description: 探索 Illacme Plenipes 针对后台进程唯一性、FastAPI Web 网关、向导与预览服务划分的 4 端口单例锁体系，以及守护进程故障自动熔断与健康自愈机制。
tags: [Showcase, SingletonLock, Architecture, HighAvailability, Gateway, Resilience]
---

# 🔒 4 端口物理单例锁与高可用容错自愈网关

> [!TIP]
> **物理单例占位，进程永不冲突，故障秒级自愈**：在后台长期运行的守护系统中，最危险的隐患是多个进程重复拉起导致数据库锁死、文件账本损坏或端口冲突。Illacme Plenipes 设计了严格的 4 端口物理职责划分与单例锁（Singleton Lock）守门体系。

---

## ⚡ 4 端口物理规划与架构矩阵

<div class="stats-matrix" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1.5rem; margin: 2rem 0;">
    <div class="stat-card" style="padding: 1.25rem 1.5rem; background: var(--card-bg); border-radius: 16px; border: 1px solid var(--border-color);">
        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 4px;">🔒 43210 单例锁端口</div>
        <div style="font-size: 1.15rem; font-weight: 700; color: #ff5252;">进程唯一性占位锁</div>
    </div>
    <div class="stat-card" style="padding: 1.25rem 1.5rem; background: var(--card-bg); border-radius: 16px; border: 1px solid var(--border-color);">
        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 4px;">🔌 43212 Web API 网关</div>
        <div style="font-size: 1.15rem; font-weight: 700; color: #00f2fe;">FastAPI 控制中枢 · 毫秒响应</div>
    </div>
    <div class="stat-card" style="padding: 1.25rem 1.5rem; background: var(--card-bg); border-radius: 16px; border: 1px solid var(--border-color);">
        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 4px;">🧙 43211 可视化向导</div>
        <div style="font-size: 1.15rem; font-weight: 700; color: #ffb300;">安装引导与配置向导服务</div>
    </div>
    <div class="stat-card" style="padding: 1.25rem 1.5rem; background: var(--card-bg); border-radius: 16px; border: 1px solid var(--border-color);">
        <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 4px;">🌐 43213 本地预览服务</div>
        <div style="font-size: 1.15rem; font-weight: 700; color: #00ff88;">零跨域静态站即时热呈现</div>
    </div>
</div>

---

## 🛠️ 单例锁机制与自愈架构

```mermaid
graph TD
    UserLaunch[启动 plenipes.py] --> ProbeLock{绑定 43210 单例锁?}
    
    ProbeLock -- 绑定失败 --> Conflict[检测到已有实例在运行 -> 优雅拦截并提示]
    ProbeLock -- 绑定成功 --> Init[创建进程级单例实例]
    
    Init --> Gateway[拉起 43212 FastAPI Web API 治理网关]
    Init --> Preview[拉起 43213 本地静态预览服务]
    
    Gateway --> Watchdog[守护进程健康心跳与熔断自愈]
    Watchdog --> Health[内存泄露防范 · AI 超时自动降级 · 异步 I/O 隔离]
```

### 1. 🔒 43210 物理单例锁（Singleton Process Lock）
* 系统启动时首先尝试在 `127.0.0.1:43210` 创建独占式 Socket 绑定；
* 若端口已被占用，系统立即拦截二次启动，并给出清晰提示，**物理根绝了后台多进程竞争导致的指纹账本破坏与 SQLite 文件写入死锁**。

### 2. 🔌 43212 FastAPI 治理网关与物理隔离
* 负责承载全站治理中心（Dashboard）的所有 RESTful API 与实时 WebSocket 广播；
* 与本地预览服务（`43213`）严格物理隔离，即便静态站点在编译或刷新，也不会阻塞治理中心的操作与遥测指标采集。

### 3. 🛡️ 异常熔断与健康自愈（Resilience & Fault-Tolerance）
* **AI 算力超时熔断**：当云端大模型接口或本地 Ollama 出现网络 hang 住时，自愈网关自动触发超时保护并降级至段落影子缓存或备用算力管道；
* **非交互子进程保护**：所有后台外部 CLI 调用均强制附加 `--yes` / `-y` 与非交互标志，彻底避免因等待用户输入而导致后台挂起。
