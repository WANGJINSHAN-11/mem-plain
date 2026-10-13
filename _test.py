# -*- coding: utf-8 -*-
"""本地测试：逐个发送 JSON-RPC，逐个读回应，验证每个工具。"""
import json, subprocess, os, sys
from pathlib import Path

HERE = Path(__file__).parent
PY = str(HERE / ".venv" / "Scripts" / "python.exe")
env = dict(os.environ, PYTHONIOENCODING="utf-8")

p = subprocess.Popen([PY, str(HERE / "server.py")],
                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                     text=True, encoding="utf-8", env=env, bufsize=1)


def send(obj):
    p.stdin.write(json.dumps(obj, ensure_ascii=False) + "\n")
    p.stdin.flush()


def recv():
    line = p.stdout.readline()
    return json.loads(line) if line.strip() else None


send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
      "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                 "clientInfo": {"name": "t", "version": "1"}}})
r = recv(); print("initialize ->", "OK" if r and "result" in r else r)

send({"jsonrpc": "2.0", "method": "notifications/initialized"})

send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
r = recv(); print("tools/list ->", [t["name"] for t in r["result"]["tools"]])

for i, (name, args) in enumerate([
    ("memory_read", {"filename": "FACT.md", "tail": 2}),
    ("memory_search", {"query": "记忆", "limit": 2}),
    ("memory_update", {"content": "x"}),   # 应该被缩水闸门拒绝
], start=3):
    send({"jsonrpc": "2.0", "id": i, "method": "tools/call",
          "params": {"name": name, "arguments": args}})
    r = recv()
    if r and "result" in r:
        print(f"{name} ->", r["result"]["content"][0]["text"][:150].replace("\n", " | "))
    else:
        print(f"{name} ->", str(r)[:200])

p.stdin.close()
p.terminate()
err = p.stderr.read()
if err.strip():
    print("\n[stderr]", err[:500])
