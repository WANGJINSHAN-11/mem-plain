# 接入示例

三种客户端、两种装法。**推荐 uvx**（不用管 Python 环境）。

## 1) uvx 方式（推荐）

需要先有 [uv](https://docs.astral.sh/uv/)（一条命令装好，Windows 也能用）。

| 客户端 | 文件 | 命令 | 参数 |
|---|---|---|---|
| Cherry Studio | `cherry-studio.json` | `uvx` | `plaintext-memory-mcp` |
| Claude Desktop | `claude-desktop.json` | `uvx` | `plaintext-memory-mcp` |
| DeepSeek Harness | `deepseek-harness.patch.yml` | `uvx` | `plaintext-memory-mcp` |

三者都要设 `MEMORY_DIR`（例子里是 `E:\memory`，改成你自己的记忆目录）。

Cherry Studio：设置 → MCP 服务器 → 添加 → 从 JSON 导入。
Claude Desktop：把 `mcpServers` 那段合并进 `claude_desktop_config.json`（Windows 在
`%APPDATA%\Claude\claude_desktop_config.json`）。
DeepSeek Harness：把 patch 内容合并进 profile 的 `cordis.patch.yml`。

## 2) 源码方式（不装包，直接指向仓库）

参数改成仓库里的 `server.py` 绝对路径，命令改成该仓库 venv 的 Python：

```json
{
  "mcpServers": {
    "memory": {
      "command": "E:\\memory-mcp\\.venv\\Scripts\\python.exe",
      "args": ["E:\\memory-mcp\\server.py"],
      "env": { "MEMORY_DIR": "E:\\memory" }
    }
  }
}
```

macOS / Linux 把路径换成 `/path/to/memory_mcp/.venv/bin/python` 和 `/path/to/memory_mcp/server.py`。

## 注意

- Windows 的 JSON 路径：反斜杠要转义成 `\\`；YAML 用单引号可原样写。
- 多个客户端同时用，请只让**一个**客户端调 `memory_update`（整篇覆盖会打架）。
- 客户端里看到工具名长这样：`memory_read` / `memory_update` / `memory_append` / `memory_search`。
