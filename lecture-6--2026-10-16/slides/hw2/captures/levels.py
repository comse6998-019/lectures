"""The first attach at each analysis level, each on a fresh copy of the OWASP checkout with no analysis cache, then a
dataflow question asked of the symbol-table analysis. Writes what it prints; captures/levels.txt is that output.

    cd lecture-6--2026-10-16 && SYSTEM_PYTHON=$(uv python find 3.12) .venv/bin/python slides/hw2/captures/levels.py <scratch dir>
"""
import shutil, sys, time
from cldk import CLDK

out, ans = sys.argv[1], {}
for level in ["symbol_table", "call_graph", "program_dependency_graph", "system_dependency_graph"]:
    fresh = shutil.copytree("cldk-demo/owasp", f"{out}/{level}", ignore=shutil.ignore_patterns(".codeanalyzer", ".git"))
    t = time.time()
    ans[level] = CLDK.python(project_path=fresh, analysis_level=level)
    print(f"{level:<25} {len(ans[level].get_callables_overview())} callables {time.time() - t:4.0f} s", flush=True)
try:
    ans["symbol_table"].get_ddg("BenchmarkTest00099_post")
except Exception as e:
    print(f"{type(e).__name__}: {e}")
