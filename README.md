# 🌉 Illacme-plenipes (v34.5 Flagship Edition)

[🇨🇳 简体中文](./README.zh-CN.md) | 🇬🇧 English

![Version](https://img.shields.io/badge/version-v34.5--flagship-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![Architecture](https://img.shields.io/badge/architecture-Industrial%20Grade%20/%20Anti--Pruning-success.svg)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)


### 1. 🛡️ OS-Level Singleton Mutex
Preempts high-level ports (default `43210`) at the operating system's lowest layer using `socket.bind()`, rendering it physically immune to dual-instance launch disasters. If the process dies unexpectedly, the kernel instantly releases the port, perfectly protecting the underlying metadata from concurrent pollution.

### 2. ⚡️ Asynchronous State Machine & Write-Behind Cache (Atomic Write)
- **O(1) Dirty Marking**: The core pipeline simply marks `self._dirty = True` and instantly releases the lock, yielding extremely high throughput.
- **Background Heartbeat Daemon**: An independent Flusher thread silently writes snapshots to disk based on the configured heartbeat interval without blocking the main thread.
- **Anti-Tearing Mechanism**: Transactional writes based on `os.replace`. Even if a physical power outage occurs at the exact moment of writing, the MD5 fingerprint database remains 100% intact.

### 3. 🧠 Token-Level High-Precision LLM Orchestration
Fully integrates OpenAI's industrial-grade `tiktoken` library to precisely squeeze computing boundaries.
- **Precise Calculation**: Perfectly adapts to DeepSeek, Qwen, OpenAI, and **OpenClaw (Little Lobster)** models.
- **Anti-OOM Truncation**: Automatically slices extremely long documents into concurrent sub-tasks based on the Token-level `max_chunk_size`, completely eliminating time-consuming bottlenecks.

### 4. 🧵 Thread Pool Dispatcher (Full Domain Concurrency)
- **Image Compression Pipeline**: Mounts file-level fine-grained concurrency locks to prevent multiple threads from processing the same 8K massive image and blowing up VRAM, supporting ultra-fast WebP transcoding.
- **Multi-Language Matrix**: The target language array executes entirely concurrently. The total translation time is determined solely by the slowest single language, rather than linear stacking.

### 5. 🕷️ Dynamic AST Down-scaling & Anti-Infinite-Loop Transclusion
- Dynamically depth-controlled (`max_depth`) physical expansion for bidirectional links (Transclusion).
- Built-in Double-Checked Locking (DCL) memory-level caching to block repeated disk I/O trampling.
- Zero-intrusion adaptive down-scaling of Markdown-specific syntax into native components of the target frontend.

---

## ⚙️ Installation & Quick Start

### 1. Install Core Dependencies

```bash
# Image processing, YAML parsing, networking, and watchdog
pip install Pillow PyYAML requests watchdog 

# [Highly Recommended] Install the Token-level high-precision chunking foundation
pip install tiktoken
```

### 2. Configure the Master Bus

Copy the `config.yaml.example` file in the root directory to `config.yaml`. All underlying magic numbers (concurrency limits, inference temperature, heartbeat intervals, SEO layout weights) have been 100% hoisted to this configuration file, achieving zero-code-intrusion orchestration.

```YAML
# Core Path Configuration Example
vault_root: "/Users/YourName/Documents/Obsidian-Vault" 
frontend_dir: "../my-astro-site"
```

(⚠️ **Security Warning**: Do not commit the `config.yaml` containing your real API Key to a public repository. Ensure it is added to your `.gitignore`!)

### 3. Drive the Engine (CLI Dispatching)

Illacme-plenipes offers four industrial-grade execution modes:

```bash
# 1. Sync Mode - Incremental sync combined with MD5 hash checks, compiling only modified files
python plenipes.py --sync

# 2. Daemon Watch Mode - Millisecond-level hot-reload monitoring
python plenipes.py --watch

# 3. Dry-Run Mode - Prints routing telemetry logs only, blocking physical disk writes and API billing
python plenipes.py --sync --dry-run

# 4. Force Mode - Tears down MD5 state fingerprints, forcing a complete override recompilation of the entire vault
python plenipes.py --sync --force
```

---

## 🔌 NPM Integration

It is highly recommended to mount the **Illacme-plenipes** daemon directly into your frontend project. Inject the following scripts into your frontend project's `package.json`:

```JSON
"scripts": {
  "plenipes:sync": "cd ../.. && python plenipes.py --sync",
  "plenipes:watch": "cd ../.. && python plenipes.py --watch",
  "dev:i": "npm run plenipes:sync && concurrently -k -p \"[{name}]\" -n \"Illacme,Astro\" -c \"blue.bold,green.bold\" \"npm run plenipes:watch\" \"npm run dev\""
}
```

_Note: Requires the concurrent executor to be installed beforehand: `npm install -g concurrently`_


---

## 🛠 Advanced Tuning

|**Parameter**|**Domain**|**Tuning Recommendation**|
|---|---|---|
|`max_workers`|`system`|`20-50` for cloud APIs; MUST be `1` for local models (without queueing); `8` for image-intensive tasks.|
|`auto_save_interval`|`system`|Default is `2.0`s. Can be increased to `5.0`s for extremely high-frequency modification scenarios.|
|`temperature`|`translation`|Strictly bind to `0.1` for translation; can be raised to `0.6-0.8` for divergent or creative tasks.|
|`max_chunk_size`|`translation`|Unit: Tokens. Recommend `2000` for local small models; maximize to `8000` for top-tier long-context APIs.|

---

## 📜 License

The code and architecture of this project are licensed under the [CC BY-NC 4.0 (Creative Commons Attribution-NonCommercial 4.0 International)](https://creativecommons.org/licenses/by-nc/4.0/) License.

**You are free to:**
- Download, clone, and modify the source code of this project.
- Use this project to build personal blogs, knowledge bases, academic research sites, and other non-profit scenarios.

**You may not:**
- Use this project (including the engine logic and theme architecture) for any **commercial or profit-making purposes** (including but not limited to: selling it as a paid SaaS service, or integrating it into platforms with mandatory commercial advertisements).

> For commercial use or custom development authorization, please contact the author via GitHub Issues or email.