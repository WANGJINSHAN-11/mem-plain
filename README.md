# memory-mcp

> 把**长期记忆**做成你自己磁盘上的纯文本文件，再用一个 MCP 服务器把它开放给任何 AI 客户端。
> Plain-text long-term memory, exposed to any MCP client.

---

## 它解决什么问题

每个 AI 客户端（Cherry Studio、DeepSeek Harness、Claude Desktop、Cursor…）都有自己的"记忆"，
但记忆数据往往锁在平台里：**换个客户端，记忆就断了**；导出是一堆看不懂的 JSON；同步全靠平台。

这个项目的思路只有一条：

- **记忆 = 几个纯文本文件**（`.md` / `.jsonl`），放在你自己的磁盘上；
- **工具 = 一个 MCP 服务器**，只负责读写这些文件；
- **任何支持 MCP 的客户端**接上它，就共享同一份记忆。

**代码公开，数据私有。** 这个仓库里只有代码；记忆文件永远留在本机。

---

## 特性

| 工具 | 作用 |
|---|---|
| `memory_read(filename="FACT.md", tail=0)` | 读记忆文件；`tail=N` 只读末尾 N 行，省 token |
| `memory_update(content)` | 整篇覆盖 `FACT.md`；**写入前自动备份** + **缩水保护** |
| `memory_append(text, tags=[])` | 往 `JOURNAL.jsonl` 追加一条事件（自动带时间戳） |
| `memory_search(query, limit=20)` | 在 JOURNAL 里搜关键词（大小写不敏感），返回最近 N 条 |

另外还有：

- 🪶 **零重型依赖**：只有 Python + `mcp`，没有数据库、没有向量库、没有云服务
- 📖 **可读可改**：出问题直接打开文件就能看；能进 git、能 grep
- 🔁 **跨客户端**：同一份记忆同时喂给多个 AI 客户端
- 🛡 **写入有闸门**：自动备份 + 缩水保护，防一次误写毁掉全部记忆（详见"安全设计"）

---

## 记忆文件格式

目录结构（默认 `E:\memory`，用环境变量 `MEMORY_DIR` 可改到任意位置）：

```
<MEMORY_DIR>\
├── FACT.md        长期记忆：身份、项目、环境、约定……（整篇覆盖）
├── JOURNAL.jsonl  事件日志：每行一条 JSON（只追加）
├── SOUL.md        人格定义（只读）
└── USER.md        用户档案（只读）
```

`JOURNAL.jsonl` 每行格式（时间戳统一 **UTC、`Z` 结尾、毫秒**，方便跨机器合并排序）：

```json
{"ts":"2026-10-19T06:59:54.413Z","tags":["项目","进度"],"text":"一句话结论，不抄原文。"}
```

`templates/` 里有一份空的 FACT 骨架和 JOURNAL 示例，可以先照着抄。

---

## 安装

```bash
git clone https://github.com/WANGJINSHAN-11/memory_mcp.git
cd memory_mcp

python -m venv .venv

# Windows:
.venv\Scripts\pip install -r requirements.txt
# macOS / Linux:
# .venv/bin/pip install -r requirements.txt

# 自检（在临时目录里跑，不会碰你的真实记忆）
.venv\Scripts\python.exe _test.py
```

要求：**Python 3.10+**（实测 3.13.3）、**mcp >= 2.3.0**。
⚠️ 本版用的是 mcp 2.x 的 `McpServer` 接口，**mcp 1.x 的 `FastMCP` 写法不兼容**。

---

## 接入客户端

所有客户端都填同样的三要素：

| 字段 | 值 |
|---|---|
| 命令 | `<项目路径>/.venv/Scripts/python.exe`（macOS/Linux 用 `.venv/bin/python`） |
| 参数 | `<项目路径>/server.py` |
| 环境变量 | `MEMORY_DIR=<你的记忆目录>`（可选，默认 `E:\memory`） |

`examples/` 里给了三个现成的配置文件：

<details>
<summary>Cherry Studio（<code>examples/cherry-studio.json</code>）</summary>

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
<summary>DeepSeek Harness（<code>examples/deepseek-harness.patch.yml</code>）</summary>

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

<details>
<summary>Claude Desktop（<code>examples/claude-desktop.json</code>）</summary>

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

> ⚠️ **多个客户端同时开时**：`memory_update` 是整篇覆盖 FACT，两个客户端同时写会互相覆盖。
> 约定同一时间只让一个客户端写长期记忆；`memory_append` 是追加，可以随便并发。

---

## 工具怎么用（给模型看的习惯）

| 想做的事 | 调用 |
|---|---|
| 读长期记忆 | `memory_read()` |
| 只读 FACT 末尾几节（省 token） | `memory_read(tail=50)` |
| 记一条事件（当场记，只写结论） | `memory_append(text="...", tags=["项目"])` |
| 找以前记过的事 | `memory_search(query="关键词")` |
| 重写整篇 FACT（谨慎） | `memory_update(content="...")` |

---

## 安全设计

1. 🔒 **缩水保护**：`memory_update` 若发现新内容不足 1KB、且旧内容是它的 **3 倍以上**，直接拒绝——防一次误写/截断毁掉全部记忆。
   真要整篇覆盖，请直接编辑文件（记得先备份）。
2. 💾 **自动备份**：每次覆盖写入前，旧文件先备份成 `FACT.md.bak-<时间戳>`。
3. 📖 **读取白名单**：`memory_read` 只能读 FACT / JOURNAL / SOUL / USER 四个文件，`../../secret.txt` 这类越权路径会被拒。
4. 🏠 **数据不出本机**：服务器只读写本地文件，没有任何网络请求。
5. 🔧 **路径不写死**：`MEMORY_DIR` 环境变量，换机器只改一处。

---

## 项目结构

```
memory-mcp/
├── server.py                    MCP 服务器主体（127 行，中文注释，可当源码读）
├── requirements.txt             依赖（只有 mcp）
├── _test.py                     本地自检：临时目录 + 完整握手 + 四个工具 + 越权断言
├── README.md
├── CHANGELOG.md
├── LICENSE                      MIT
├── .gitignore                   ⚠️ 挡死所有记忆数据
├── examples/                    三个客户端的接入配置示例
│   ├── cherry-studio.json
│   ├── deepseek-harness.patch.yml
│   └── claude-desktop.json
└── templates/                   记忆文件骨架
    ├── FACT.md.example
    └── JOURNAL.jsonl.example
```

---

## 设计取舍：为什么不用数据库 / 向量库

- **可读**：出问题打开文件就能看，不用工具、不用查询语句
- **可迁移**：换机器拷一个目录就完事，没有导出/导入格式
- **可版本化**：`git diff` 能看见记忆是怎么长出来的
- **便宜**：一个进程、零 embedding、零索引，不额外烧 token
- **缺点**：`memory_search` 只是关键词子串匹配，没有语义检索；FACT 变大后要配合 `tail` 分页读

这些缺点是有意接受的——记忆量在"几千条事件、几十 KB 正文"这个量级时，纯文本完全够用，而可读、可改、可迁移的价值远大于语义检索。

---

## 版本

见 [CHANGELOG.md](CHANGELOG.md)。当前 **v0.2.0**（2026-10-19）。

## 许可

MIT，见 [LICENSE](LICENSE)。

## PS

如果嫌麻烦，可以直接把仓库丢给你的 agent，让它照 README 接上。
