# 更新日志

## v0.2.0 — 2026-10-19

### server.py
- 升级到 **mcp 2.x 的 `McpServer` 接口**（`from mcp.server.mcpserver import MCPServer`），要求 `mcp >= 2.3.0`
- JOURNAL 时间戳统一为 **UTC、`Z` 结尾、毫秒**（`2026-10-19T06:59:54.413Z`），多端合并排序不会错位
- 缩水闸门拒绝文案去掉不存在的 `FORCE` 提示（原来会让模型以为有个开关）
- `memory_append` 统计条数改用 `with` 上下文，修掉一次文件句柄泄漏
- 启动时记忆目录不存在：提示后会**自动创建空目录**（原来是直接报错，append 时才炸）

### _test.py
- 改为**在临时目录里跑**：不再碰真实记忆（旧版会往真 FACT/JOURNAL 里写东西）
- 补齐四个工具的断言 + 越权读取断言（旧版只测了 3 个）
- 修 Windows 控制台 GBK 编码问题：记忆里有 emoji 时旧版会直接 `UnicodeEncodeError` 崩溃

### 打包与分发
- 新增 `pyproject.toml`（hatchling）：**打包配置先留着，暂未发布 PyPI**；README 与 examples 里不提供 `uvx` 装法，统一走源码方式
- 代码移入 `plaintext_memory_mcp/` 包，新增 `python -m plaintext_memory_mcp` 入口与 `plaintext-memory-mcp` 命令
- 根目录 `server.py` 改为**兼容层**：老配置里 args 指向 `server.py` 的照旧能跑（行为不变，自检已过）

### 文档
- README 首屏重构：30 秒看懂 → 克隆安装步骤 → 客户端三要素 → 常见问题
- 新增 `examples/README.md`（三个客户端的路径填法对照）
- README 重写：记忆文件格式、三个客户端的接入示例、安全设计、设计取舍
- 新增 `examples/`（Cherry Studio / DeepSeek Harness / Claude Desktop）、`templates/`（FACT 骨架、JOURNAL 示例）
- 新增 `LICENSE`（MIT）与本文件
- `.gitignore` 补上 `*.zip`、`/dist/`、`.DS_Store`

## v0.1.0 — 2026-10-13

- 首个版本：`server.py`（4 个工具 + 缩水闸门 + 自动备份 + 读取白名单）、`_test.py`、`requirements.txt`、`.gitignore`、README
