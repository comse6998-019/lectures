"""Move 3 of the HW2 deck (item 2.3): what the B608 handler of BenchmarkTest00099.py calls, and who calls get_safe_value.
move3.txt is what it prints; capture.py splits it into callees.txt and callers.txt.

    cd lecture-6--2026-10-16 && SYSTEM_PYTHON=$(uv python find 3.12) .venv/bin/python slides/hw2/captures/move3.py

The attach and the locate are section 1 and 2 of cldk-mcp.ipynb, and the for line is its move 3 cell verbatim. The print
line asks the cell's second question with a label that says what the count is. The notebook's own label, "callers of the
helper HW1's false positives share", is wrong: the 74 callers are the _post handlers of BenchmarkTest01103 to 01230, and
HW1 scanned only testcode/BenchmarkTest000*.py, where no case calls the helper.
"""
from cldk import CLDK

an = CLDK.python(project_path="cldk-demo/owasp", analysis_level="program_dependency_graph")
hit = an.locate("testcode/BenchmarkTest00099.py", 46)
for c in an.callees_of(hit.callable.name): print(c.file, c.line, c.callable)
print(len(an.callers_of("get_safe_value")), "callers of get_safe_value, which returns the constant 'bar'")
