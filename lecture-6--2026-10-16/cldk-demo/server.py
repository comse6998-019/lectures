import os, subprocess
from pathlib import Path
from typing import TypedDict
from mcp.server import MCPServer                                # the SDK's main server class
from mcp.server.mcpserver.exceptions import ToolError           # raised when a tool refuses
from cldk import CLDK

# Directory holding this file; the checkout to analyse lives next to it
HERE = Path(__file__).resolve().parent

# CLDK needs to know which Python interpreter to analyse with; keep a caller-provided value if set
os.environ.setdefault("SYSTEM_PYTHON", subprocess.run(["uv", "python", "find", "3.12"], capture_output=True, text=True).stdout.strip())

# The codebase we serve; resolved so the containment check in `checked` is reliable
target = (HERE / "owasp").resolve()

# Attach once at startup. This reads the cache built in section 1;
# without that cache the first start takes minutes
an = CLDK.python(project_path=str(target), analysis_level="program_dependency_graph")

# The MCP server instance that the tools below register on
mcp = MCPServer("cldk")


def checked(path: str) -> str:
    """Validate that `path` is a real file inside the target; return it relative to the target."""
    p = (target / path).resolve()  # resolve also collapses ".." segments
    # Refuse anything that escapes the checkout or is not a file
    if not p.is_relative_to(target) or not p.is_file():
        raise ToolError(f"refused: {path} is not a file of the target")
    return p.relative_to(target).as_posix()


class Located(TypedDict):
    """Result shape of the `locate` tool."""
    signature: str | None  # full signature, None at module scope
    name: str | None       # short name, None at module scope
    module: str            # module that holds the line


@mcp.tool(description="The callable that holds a line, or module scope.")
def locate(path: str, line: int) -> Located:
    # Map (file, line) to the enclosing callable
    hit = an.locate(checked(path), line)
    return {"signature": hit.callable.signature if hit.callable else None,
            "name": hit.callable.name if hit.callable else None, "module": hit.module.module_name}


@mcp.tool(description="The source text of a callable, by signature.")
def source(signature: str) -> str:
    # get_method_bodies returns a dict keyed by signature; a missing key means unknown callable
    bodies = an.get_method_bodies([signature])
    if signature not in bodies:
        raise ToolError(f"refused: no body for {signature}")
    return bodies[signature]


@mcp.tool(description="Callers of a callable by name, with file and line.")
def callers(name: str) -> list[dict]:
    # One entry per call site found in the call graph
    return [{"file": c.file, "line": c.line, "callable": c.callable} for c in an.callers_of(name)]


class Edge(TypedDict):
    """One data-dependence edge, expressed in source lines."""
    from_line: int  # line where the value is defined
    to_line: int    # line where the value is used
    var: str        # variable carrying the value


@mcp.tool(description="Data-dependence edges of the callable that holds a line: from-line, to-line, variable.")
def dataflow(path: str, line: int) -> list[Edge]:
    # Find the callable that holds the line; module scope has no DDG
    hit = an.locate(checked(path), line)
    if not hit.callable:
        raise ToolError(f"refused: line {line} of {path} is in no callable")
    # Use the full signature: a bare name like init matches 1,230 callables
    page = an.get_ddg(hit.callable.signature, page_size=2000)
    out = []
    for e in page.edges:
        try:
            # Node ids look like "<...>@<line>:<col>"; keep only the line number
            out.append({"from_line": int(e.src.split("@")[-1].split(":")[0]),
                        "to_line": int(e.dst.split("@")[-1].split(":")[0]),
                        "var": e.var})
        except ValueError:
            # Skip nodes whose id carries no numeric line (e.g. parameters, externals)
            continue
    return out


if __name__ == "__main__":
    # Serve over stdio, as the Inspector catalog in section 6 expects
    mcp.run()
