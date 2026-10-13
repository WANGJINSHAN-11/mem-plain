# memory_mcp
一个通用的全局记忆的mcp插件
> 一个从零写的**长期记忆 MCP 服务器** —— 把一组纯文本记忆文件，变成任何 AI 客户端都能调用的工具。
>
> A from-scratch MCP server that exposes plain-text memory files as tools for any AI client.

---

## 为什么做这个

现在每个 AI 客户端（Cherry Studio、DeepSeek Harness、Claude Desktop…）都有自己的"记忆"方案，
但记忆数据往往**锁在某个平台里**——换个客户端，记忆就断了。

这个项目的思路很简单：

- **记忆 = 几个纯文本文件**（`.md` / `.jsonl`），放在你自己的磁盘上
- **工具 = 一个 MCP 服务器**，读写这些文件
- **任何支持 MCP 的客户端**接上它，就共享同一份记忆

**代码公开，数据私有。** 本仓库只有代码；你的记忆文件永远留在本机。

---

## 功能

| 工具 | 说明 |
|---|---|
| `memory_read` | 读取记忆文件。默认 `FACT.md`；`tail=N` 只读末尾 N 行（省 token） |
| `memory_update` | 覆盖写入 `FACT.md`。**写入前自动备份** + **缩水保护**（防写坏） |
| `memory_append` | 往 `JOURNAL.jsonl` 追加一条事件（带时间戳、可选标签） |
| `memory_search` | 在 JOURNAL 里搜关键词，返回最近匹配 |

## 记忆文件

目录结构（默认 `E:\memory`，可用环境变量 `MEMORY_DIR` 改）：

```
E:\memory\
├── FACT.md        长期记忆（整篇覆盖；核心事实、项目、约定…）
├── JOURNAL.jsonl  事件日志（每行一条 JSON：{"ts":…, "tags":[…], "text":…}）
├── SOUL.md        人格定义（只读）
└── USER.md        用户档案（只读）
```

## 安装

```bash
git clone <https://github.com/WANGJINSHAN-11/memory-mcp.git>
cd memory-mcp

python -m venv .venv
# Windows:
.venv\Scripts\pip install -r requirements.txt
# macOS / Linux:
# source .venv/bin/activate && pip install -r requirements.txt
```

## 接入客户端

在客户端的 MCP 设置里加一个 **stdio** 服务器：

| 字段 | 值 |
|---|---|
| 命令 | `<项目路径>\.venv\Scripts\python.exe` |
| 参数 | `<项目路径>\server.py` |
| 环境变量 | `MEMORY_DIR=<你的记忆目录>`（可选，默认 `E:\memory`） |

<details>
<summary>Cherry Studio 配置示例（JSON）</summary>

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
</details>

<details>
<summary>DeepSeek Harness 配置示例（cordis patch YAML）</summary>

```yaml
- insert:
    - id: mcp-memory
      name: '@deepseek-ai/dsh-mcp-client'
      config:
        transport: stdio
        serverName: memory
        command: 'E:\memory-mcp\.venv\Scripts\python.exe'
        args: ['E:\memory-mcp\server.py']
        env:
          MEMORY_DIR: 'E:\memory'
```
</details>

## 安全设计

- 🔒 **缩水保护**：`memory_update` 若检测到新内容不足 1KB、且旧内容是它的 3 倍以上，直接拒绝，防止一次误写毁掉全部记忆
- 💾 **自动备份**：每次覆盖写入前，旧文件会先备份成 `*.bak-<时间戳>`
- 📖 **读取白名单**：`memory_read` 只能读那几个记忆文件，防止越权
- 🔧 **路径不写死**：用 `MEMORY_DIR` 环境变量，换机器只需改一处

## 项目结构

```
memory-mcp/
├── server.py           MCP 服务器主体（含中文注释，可当源码读）
├── requirements.txt   依赖（只有 mcp）
├── _test.py           本地测试脚本（模拟客户端握手 + 调用）
├── README.md
└── .gitignore         ⚠️ 挡死所有记忆数据
```

## 测试

```bash
.venv\Scripts\python.exe _test.py
```

会模拟一次完整的 MCP 握手（initialize → tools/list → 逐个调用工具），并打印结果。


## 许可

MIT

## PS
如果嫌麻烦，可以直接交给你的agant
