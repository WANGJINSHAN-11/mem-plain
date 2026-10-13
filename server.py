#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
memory-mcp —— 从零写的一个"长期记忆"MCP 服务器

作用：把一组纯文本记忆文件（FACT / JOURNAL / SOUL / USER）暴露成 MCP 工具，
      任何支持 MCP 的客户端（Cherry Studio、DeepSeek Harness、Claude 等）接上就能读写。

记忆位置：默认 E:\\memory，可用环境变量 MEMORY_DIR 覆盖。
传输方式：stdio（客户端启动本进程，通过标准输入输出收发 JSON-RPC）。

⚠️ 数据永远不离开本机 —— 本文件可以公开，记忆文件绝不上传。
"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from mcp.server.mcpserver import MCPServer

# ─────────────────────────── 配置 ───────────────────────────
MEMORY_DIR = Path(os.environ.get("MEMORY_DIR", r"E:\memory"))

FACT_FILE = MEMORY_DIR / "FACT.md"          # 长期记忆（整篇覆盖）
JOURNAL_FILE = MEMORY_DIR / "JOURNAL.jsonl"  # 事件日志（逐行追加）

# 允许通过 memory_read 读的文件白名单（防越权读别的文件）
READABLE = {"FACT.md", "JOURNAL.jsonl", "SOUL.md", "USER.md"}

# 缩水闸门：新 FACT 小于 1KB 且旧的大于它 3 倍时，拒绝覆盖（防写坏/截断）
MIN_FACT_BYTES = 1024
SHRINK_RATIO = 3

mcp = MCPServer("memory")


def _now() -> str:
    """当前时间（带时区），ISO 格式。"""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _backup(path: Path) -> str | None:
    """写入前先备份（文件名带日期）。返回备份路径，没写成功返回 None。"""
    if not path.exists():
        return None
    bak = path.with_suffix(path.suffix + f".bak-{datetime.now():%Y%m%d-%H%M%S}")
    shutil.copy2(path, bak)
    return str(bak)


# ─────────────────────────── 工具 ───────────────────────────

@mcp.tool(description=(
    "读取记忆文件。filename 默认 FACT.md；可传 SOUL.md / USER.md / JOURNAL.jsonl。"
    "tail>0 时只返回最后 tail 行（读大文件时用，省 token）。"
))
def memory_read(filename: str = "FACT.md", tail: int = 0) -> str:
    name = Path(filename).name
    if name not in READABLE:
        return f"拒绝：只能读 {sorted(READABLE)}，收到的是 {filename!r}"
    path = MEMORY_DIR / name
    if not path.exists():
        return f"文件不存在：{path}"
    text = path.read_text(encoding="utf-8", errors="replace")
    if tail > 0:
        lines = text.splitlines()
        text = "\n".join(lines[-tail:])
    return text


@mcp.tool(description=(
    "覆盖写入 FACT.md（长期记忆）。写入前会自动备份，并有缩水保护："
    "若新内容不足 1KB 且旧内容的三倍以上，则拒绝（防写坏）。"
))
def memory_update(content: str) -> str:
    old = FACT_FILE.read_text(encoding="utf-8") if FACT_FILE.exists() else ""
    if len(content.encode("utf-8")) < MIN_FACT_BYTES and len(old.encode("utf-8")) > MIN_FACT_BYTES * SHRINK_RATIO:
        return (f"拒绝写入：新内容太小（{len(content.encode('utf-8'))} 字节），"
                f"旧内容有 {len(old.encode('utf-8'))} 字节，疑似写坏/截断。"
                f"确实要覆盖，请直接编辑文件或用 FORCE。")
    bak = _backup(FACT_FILE)
    FACT_FILE.write_text(content, encoding="utf-8")
    return f"已写入 FACT.md（{len(content.encode('utf-8'))} 字节）" + (f"，备份：{bak}" if bak else "")


@mcp.tool(description="往 JOURNAL.jsonl 追加一条事件记录。tags 可选，是标签列表。")
def memory_append(text: str, tags: list[str] | None = None) -> str:
    entry = {"ts": _now(), "tags": tags or [], "text": text}
    line = json.dumps(entry, ensure_ascii=False)
    with JOURNAL_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    return f"已追加到 JOURNAL（当前共 {sum(1 for _ in JOURNAL_FILE.open(encoding='utf-8'))} 条）"


@mcp.tool(description="在 JOURNAL 里搜索关键词（大小写不敏感），返回最近匹配的若干条。")
def memory_search(query: str, limit: int = 20) -> str:
    if not JOURNAL_FILE.exists():
        return "JOURNAL 文件不存在"
    q = query.lower()
    hits = []
    for line in JOURNAL_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
        if q in line.lower():
            hits.append(line)
    hits = hits[-limit:]  # 取最近的
    if not hits:
        return f"没找到含 {query!r} 的记录"
    out = [f"找到 {len(hits)} 条（显示最近 {len(hits)} 条）："]
    for h in hits:
        try:
            e = json.loads(h)
            out.append(f"[{e.get('ts','')}] {e.get('text','')}")
        except json.JSONDecodeError:
            out.append(h)
    return "\n".join(out)


def main() -> None:
    if not MEMORY_DIR.exists():
        print(f"警告：记忆目录不存在 {MEMORY_DIR}", file=sys.stderr)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
