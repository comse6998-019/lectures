"""The answers the slides state without a window: locate outside a callable and on a file the analyzer never saw, a body
node's source, a signature with no body, an ambiguous and an undeclared name, and the resolution flag. checks.txt is what
it prints; the speaker notes quote it.

    cd lecture-6--2026-10-16 && SYSTEM_PYTHON=$(uv python find 3.12) .venv/bin/python slides/hw2/captures/checks.py
"""
from cldk import CLDK

an = CLDK.python(project_path="cldk-demo/owasp", analysis_level="program_dependency_graph")
hit = an.locate("testcode/BenchmarkTest00099.py", 46)
for path, line in [("app.py", 1), ("testcode/NoSuchFile.py", 3)]:
    miss = an.locate(path, line)
    print(f"locate({path!r}, {line}):", miss.callable, [(d.code, d.message) for d in miss.diagnostics])
print("get_source(node_id):", an.get_source(hit.node_id))
print("get_method_bodies of an unknown signature:", an.get_method_bodies(["testcode.no_such_callable"]))
for name in ["init", "execute"]:
    try:
        an.callers_of(name)
    except Exception as e:
        print(f"callers_of({name!r}): {type(e).__name__}: {str(e)[:150]}")
print("callers_of('init', in_module='testcode/BenchmarkTest00099.py'):",
      [c.callable for c in an.callers_of("init", in_module="testcode/BenchmarkTest00099.py")])
print("has_resolution_edges:", an.has_resolution_edges)
