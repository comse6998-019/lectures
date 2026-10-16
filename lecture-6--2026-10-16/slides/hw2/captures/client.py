"""The MCP agent's side of the call: start cldk-demo/server.py over stdio, list its tools, call locate and dataflow on
the B608 line of BenchmarkTest00099.py, then ask for a path outside the checkout. client.txt is what it prints.

    cd lecture-6--2026-10-16 && SYSTEM_PYTHON=$(uv python find 3.12) .venv/bin/python slides/hw2/captures/client.py
"""
import asyncio
from mcp import Client
from mcp.client.stdio import StdioServerParameters

SERVER = StdioServerParameters(command=".venv/bin/python", args=["cldk-demo/server.py"])
CASE = {"path": "testcode/BenchmarkTest00099.py", "line": 46}


async def main():
    async with Client(SERVER) as c:
        print([t.name for t in (await c.list_tools()).tools])
        print((await c.call_tool("locate", CASE)).structured_content["name"])
        edges = (await c.call_tool("dataflow", CASE)).structured_content["result"]
        from31 = [(e["to_line"], e["var"]) for e in edges if e["from_line"] == 31]
        print(len(edges), "edges; line 31 flows to", from31)
        bad = await c.call_tool("locate", {"path": "../expectedresults-0.1.csv", "line": 1})
        print(bad.is_error, bad.content[0].text)


asyncio.run(main())
