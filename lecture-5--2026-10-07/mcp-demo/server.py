import time
from pathlib import Path
from typing import TypedDict

from mcp.server import MCPServer                                # <-- The SDK's main server class
from mcp.server.mcpserver.exceptions import ToolError           # <-- Exception raised when a tool errors out
from mcp.types import ToolAnnotations                           # <-- Used to provide metadata about the tool

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE / "workspace"

mcp = MCPServer("workspace")


class EditResult(TypedDict):
    path: str
    replaced: int


@mcp.tool(
    name="edit",
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

    # If the target is not within the workspace, refuse the operation
    if not target.is_relative_to(WORKSPACE):
        raise ToolError(f"refused: {path} is outside the workspace")

    text = target.read_text()

    # If the old string does not appear exactly once, refuse the operation
    if text.count(old) != 1:
        raise ToolError(f"refused: old appears {text.count(old)} times in {path}")

    # Perform the replacement and return the result
    target.write_text(text.replace(old, new, 1))
    return {"path": path, "replaced": 1}


@mcp.tool()
def slow(seconds: int) -> str:
    """Block for the given number of seconds, then report."""
    time.sleep(seconds)
    (HERE / "slow.done").write_text(f"slept {seconds} s\n")
    return f"slept {seconds} s"


if __name__ == "__main__":
    mcp.run()
