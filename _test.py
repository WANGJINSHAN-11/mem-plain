# -*- coding: utf-8 -*-
"""
本地自检脚本：在**临时目录**里起一份记忆，走一遍完整的 MCP 握手 + 四个工具。

为什么用临时目录：测试会写入 FACT / JOURNAL，绝不能在真实记忆目录上跑
（真记忆在 E:\\memory，测试跑完临时目录会被删掉）。

用法：
    .venv\\Scripts\\python.exe _test.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Windows 控制台默认 GBK，记忆里可能有 emoji —— 不换编码会直接 UnicodeEncodeError
for s in (sys.stdout, sys.stderr):
    try:
        s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).parent
PY = HERE / ".venv" / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")

tmp = Path(tempfile.mkdtemp(prefix="memory-mcp-test-"))
env = dict(os.environ, PYTHONIOENCODING="utf-8", MEMORY_DIR=str(tmp))
print(f"测试记忆目录：{tmp}")

p = subprocess.Popen(
    [str(PY), str(HERE / "server.py")],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    text=True, encoding="utf-8", env=env, bufsize=1,
)


def send(obj):
    p.stdin.write(json.dumps(obj, ensure_ascii=False) + "\n")
    p.stdin.flush()


def recv():
    line = p.stdout.readline()
    return json.loads(line) if line.strip() else None


def call(i, name, args):
    send({"jsonrpc": "2.0", "id": i, "method": "tools/call", "params": {"name": name, "arguments": args}})
    r = recv()
    if r and "result" in r:
        return r["result"]["content"][0]["text"]
    return f"[错误] {str(r)[:300]}"


try:
    send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
          "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                     "clientInfo": {"name": "memory-mcp-selftest", "version": "1"}}})
    r = recv()
    print("initialize ->", "OK" if r and "result" in r else r)
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    r = recv()
    names = [t["name"] for t in r["result"]["tools"]]
    print("tools/list ->", names)
    assert names == ["memory_read", "memory_update", "memory_append", "memory_search"], names

    # 1) 读一个还不存在的文件
    print("memory_read(空) ->", call(3, "memory_read", {"filename": "FACT.md"}))

    # 2) 写 FACT（旧文件不存在 ⇒ 应成功）。要写到 3KB 以上，缩水闸门才有得比
    print("memory_update ->", call(4, "memory_update", {"content": "第一条长期记忆，用来占位。\n" * 200}))

    # 3) 再写一次小内容（旧内容已 > 3KB ⇒ 应被缩水闸门拒绝）
    print("memory_update(缩水) ->", call(5, "memory_update", {"content": "x"}))

    # 4) 追加事件
    print("memory_append ->", call(6, "memory_append", {"text": "自检事件 🐟", "tags": ["test"]}))

    # 5) 搜索
    print("memory_search ->", call(7, "memory_search", {"query": "自检", "limit": 3}))

    # 6) 越权读取应被拒
    print("memory_read(越权) ->", call(8, "memory_read", {"filename": "../../secret.txt"}))

    print("\n全部断言通过 ✅")
finally:
    try:
        p.stdin.close()
    except Exception:
        pass
    p.terminate()
    err = p.stderr.read()
    if err.strip():
        print("\n[stderr]", err[:800])
    shutil.rmtree(tmp, ignore_errors=True)
    print("临时记忆目录已删除")
