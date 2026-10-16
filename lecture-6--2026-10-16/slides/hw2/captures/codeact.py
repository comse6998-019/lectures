"""The code-action agent's side: lecture 4's CodeAct kernel (kernel.py, lecture 4 slide 137) with the CLDK analysis object
in its namespace, running one script of the kind the model writes. codeact.txt is what the kernel returns.

    cd lecture-6--2026-10-16 && SYSTEM_PYTHON=$(uv python find 3.12) .venv/bin/python slides/hw2/captures/codeact.py
"""
import io, traceback
from contextlib import redirect_stdout
from cldk import CLDK

an = CLDK.python(project_path="cldk-demo/owasp", analysis_level="program_dependency_graph")
namespace = {"an": an}


def run(script: str) -> str:  # lecture 4's kernel.py, unchanged
    out = io.StringIO()
    try:
        with redirect_stdout(out):
            exec(script, namespace)
    except Exception:
        out.write(traceback.format_exc())
    return out.getvalue()


SCRIPT = """
import networkx as nx
line = lambda node: node.split("@")[-1].split(":")[0]
CASES = [("testcode/BenchmarkTest00099.py", "31", "46"),
         ("testcode/BenchmarkTest00011.py", "39", "47")]
for path, src, dst in CASES:
    hit = an.locate(path, int(dst))
    g = nx.DiGraph()
    for e in an.get_ddg(hit.callable.signature, page_size=500).edges:
        g.add_edge(line(e.src), line(e.dst))
    print(hit.callable.name, nx.has_path(g, src, dst) and nx.shortest_path(g, src, dst))
"""

print(run(SCRIPT), end="")
