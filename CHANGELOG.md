# 更新日志

## v0.4.0 — 2026-10-24

### server.py
- **`memory_search` 支持情境线索召回**：新增 `tag`（多个用逗号分隔，任一命中）、`after` / `before`（`YYYY-MM-DD`，本地日期，含当天）三个参数；`query` 改为可选，留空即"只按 tag/日期列出事件"。返回结果带上该条的 tags。
- **`memory_append` 支持「巩固」**：新增 `merge=True` 参数。写入前回看最近 500 行、只看今天，用 `difflib` 比对归一化文本；相似度 ≥90%（或新内容被旧条目包含）时不新增条目，而是把新信息用「；」并进那条、tags 取并集，并原子重写 JOURNAL（先自动备份）。`merge=False` 可强制新增。
- 新增内部工具：`_norm()`（归一化比对）、`_day_of()`（UTC 时间戳→本地日期）、`_parse_day()`、`_merge_into_today()`；常量 `MERGE_SIMILARITY = 0.90`。
- 原有四个工具的参数保持向后兼容（`memory_search` 的 `query` 仍是第一个参数）。

### _test.py
- 新增断言：重复追加必须走合并而非新增、tag 过滤、日期过滤（今天查得到/明天起查不到）

### 文档
- README：工具表与用法示例补上 `tag` / `after` / `before` / `merge`
- 版本号 0.3.0 → 0.4.0

## v0.3.0 — 2026-10-24

### server.py
- 新增第五个工具 **`memory_stats()`（只读"记忆体检"）**：返回 FACT / USER / SOUL / JOURNAL 的体积、行数/条数、最后修改时间与距今天数；JOURNAL 的首末时间与今日新增条数；备份文件个数与总占用；超阈值（FACT > 60 KB、JOURNAL > 400 KB）给整理提示。
- 设计取舍：**不做**搜索命中记账、**不做**自动归档。命中数据反映的是"谁搜过什么"，不等于记忆价值，且会多一个含 query 原文的敏感日志文件；归档是破坏性操作，留给人工判断。

### _test.py
- 工具清单断言改为五个，新增 `memory_stats` 断言（输出里必须含 `FACT.md` 与 `JOURNAL.jsonl`）

### 文档
- README：工具表与"给模型用的习惯"补上 `memory_stats`；自检说明改五个工具；"缺点"一节指向 `memory_stats`
- 版本号 0.2.0 → 0.3.0

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
