"""Check dataflow-example against CLDK and the OWASP checkout: every arrow the figure draws is a direct edge of the handler's
data-dependence graph, the request value reaches the SQL string in 00099 and never in 00011 or 00012, the boxed lines say
what the boxes say, and the key gives 00099 true and 00011 and 00012 false.
The analyzer writes its cache into the project folder, so run it on a clean copy of the checkout at f1291485, not on HW1's:
    git -C <owasp clone> archive f1291485808b66e20ddb6b01b10dc71b3df8c8ba | tar -x -C <scratch>/owasp
    SYSTEM_PYTHON=$(uv python find 3.12) uv run --no-project --python 3.12 --with cldk==2.0.0,networkx python check-dataflow.py <scratch>/owasp
(for the version the spec measured: --prerelease=allow --with cldk==2.0.0rc8,networkx). The first attach takes about 200 s."""
import csv, os, subprocess, sys, importlib.metadata as md
import networkx as nx
os.environ.setdefault("SYSTEM_PYTHON", subprocess.run(["uv", "python", "find", "3.12"], capture_output=True, text=True).stdout.strip())
from cldk import CLDK

ROOT = sys.argv[1]
# case: (request line, SQL string line, execute line, the arrows the figure draws with their variables, text each boxed line holds)
CASES = {
    "00099": (31, 46, 49, [(31, 41, "param"), (41, 42, "conf52528"), (42, 46, "bar"), (46, 49, "sql")],
              {31: "request.form.get(", 41: "conf52528.set(", 42: "bar = conf52528.get(", 46: "{bar}", 49: "cur.execute(sql)"}),
    "00011": (39, 47, 50, [(39, 43, "param"), (43, 50, "bar")],
              {39: "request.cookies.get(", 43: "bar = param", 47: "= ?'", 50: "cur.execute(sql, (bar,))"}),
    "00012": (39, 48, 51, [], {39: "request.cookies.get(", 48: "= ?'", 51: "cur.execute(sql, (bar,))"}),
}
KEY = {"00099": "true", "00011": "false", "00012": "false"}

print("cldk", md.version("cldk"), "codeanalyzer-python", md.version("codeanalyzer-python"))
an = CLDK.python(project_path=ROOT, analysis_level="program_dependency_graph")
line = lambda node: int(node.split("@")[-1].split(":")[0])
ok = True
for n, (src, string, call, arrows, text) in CASES.items():
    path = f"testcode/BenchmarkTest{n}.py"
    lines = open(os.path.join(ROOT, path)).read().splitlines()
    for k, want in text.items():
        if want not in lines[k - 1]:
            print(f"{n} line {k}: {lines[k - 1].strip()!r} lacks {want!r}"); ok = False
    hit = an.locate(path, string)
    g = nx.DiGraph()
    for e in an.get_ddg(hit.callable.signature, page_size=2000).edges:
        try:
            a, b = line(e.src), line(e.dst)
        except ValueError:
            continue
        g.add_edge(a, b)
        g[a][b].setdefault("vars", set()).add(e.var)
    reach = lambda a, b: a in g and b in g and nx.has_path(g, a, b)
    for a, b, var in arrows:
        has = g.has_edge(a, b) and var in g[a][b]["vars"]
        print(f"{n} edge {a} -> {b} via {var}: {has}"); ok &= has
    to_string, to_call = reach(src, string), reach(src, call)
    print(f"{n} {hit.callable.signature}: request {src} reaches string {string}: {to_string}, call {call}: {to_call}")
    ok &= to_string == (n == "00099") and to_call
key = {r[0]: r[2] for r in csv.reader(open(os.path.join(ROOT, "expectedresults-0.1.csv"))) if r and r[0].startswith("BenchmarkTest")}
for n, want in KEY.items():
    print(f"key BenchmarkTest{n}: {key.get('BenchmarkTest' + n)}"); ok &= key.get("BenchmarkTest" + n) == want
print("ALL OK" if ok else "CHECK FAILED")
sys.exit(0 if ok else 1)
