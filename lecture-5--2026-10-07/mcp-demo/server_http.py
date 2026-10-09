import asyncio
import random
import time
from pathlib import Path
from typing import TypedDict

from mcp.server import MCPServer
from mcp.server.mcpserver import Context                                # <-- The SDK's main server class
from mcp.server.mcpserver.exceptions import ToolError           # <-- Exception raised when a tool errors out
from mcp.types import ToolAnnotations                           # <-- Used to provide metadata about the tool

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE / "workspace"

mcp = MCPServer("workspace")


class EditResult(TypedDict):
    path: str
    replaced: int


@mcp.tool(
    name="edit (http)",
    title="Edit a workspace file",
    description="Replace one exact occurrence of old with new.",
    annotations=ToolAnnotations(
        title="Edit a workspace file",
        read_only_hint=False, destructive_hint=True,
        idempotent_hint=False, open_world_hint=False),
    meta={"course": "COMS 6998-019"},
    structured_output=True,
)
def edit(path: str, old: str, new: str) -> EditResult:
    target = (WORKSPACE / path).resolve()
    if not target.is_relative_to(WORKSPACE):
        raise ToolError(f"refused: {path} is outside the workspace")
    text = target.read_text()
    if text.count(old) != 1:
        raise ToolError(f"refused: old appears {text.count(old)} times in {path}")
    target.write_text(text.replace(old, new, 1))
    return {"path": path, "replaced": 1}


@mcp.tool(name="progress_bar", description="Report progress in steps, pausing a random time between steps.")
async def progress_bar(ctx: Context, steps: int = 10, max_gap: float = 1.5) -> str:
    for i in range(1, steps + 1):
        await asyncio.sleep(random.uniform(0.1, max_gap))             # random time gap
        bar = "#" * i + "." * (steps - i)
        await ctx.report_progress(i, steps, f"[{bar}] {i}/{steps}")   # progress notification
    return f"done in {steps} steps"


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)   # http://127.0.0.1:8000/mcp
