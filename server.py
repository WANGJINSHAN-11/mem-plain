"""兼容层：`python server.py` 等价于 `python -m plaintext_memory_mcp`。

保留这个文件，是为了让**已有的接入配置**（命令里 args 指向 .../server.py 的那些）
不用改就能继续跑。
"""

from plaintext_memory_mcp.server import main

if __name__ == "__main__":
    main()