# 接入示例

本仓库是**源码方式**接入：先把仓库克隆到本地、建好 venv，再让客户端指向那个 venv 的 Python 和仓库里的 `server.py`。
（暂未发布 PyPI，所以没有 `uvx` / `pip install` 这种装法。）

## 三要素

| 字段 | 值 |
|---|---|
| 命令 | `<仓库路径>\.venv\Scripts\python.exe`（macOS/Linux：`<仓库路径>/.venv/bin/python`） |
| 参数 | `<仓库路径>\server.py`（Windows）或 `<仓库路径>/server.py` |
| 环境变量 | `MEMORY_DIR=<你的记忆目录>`，例子里写的是 `E:\memory`，改成你自己的 |

## 三个客户端

| 客户端 | 文件 | 填在哪 |
|---|---|---|
| Cherry Studio | `cherry-studio.json` | 设置 → MCP 服务器 → 添加（可从 JSON 导入） |
| Claude Desktop | `claude-desktop.json` | 合并进 `claude_desktop_config.json`（Windows：`%APPDATA%\Claude\claude_desktop_config.json`） |
| DeepSeek Harness | `deepseek-harness.patch.yml` | 合并进 profile 的 `cordis.patch.yml` |

先把三个文件里的 `E:\memory-mcp` 换成你克隆到的实际路径。

## 注意

- Windows 的 JSON 路径：反斜杠要转义成 `\\`；YAML 用单引号可原样写。
- 多个客户端同时用，请只让**一个**客户端调 `memory_update`（整篇覆盖会打架）；`memory_append` 可以并发。
- 客户端里看到工具名长这样：`memory_read` / `memory_update` / `memory_append` / `memory_search`。
