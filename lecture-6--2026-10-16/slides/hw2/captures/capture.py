"""Write the captures the HW2 deck's code windows quote, one text file per window, from real runs.

    cd lecture-6--2026-10-16 && SYSTEM_PYTHON=$(uv python find 3.12) .venv/bin/python slides/hw2/captures/capture.py <scratch dir>

1. Executes cldk-mcp.ipynb headless (jupyter-execute, as Task 3.1's check runs it) into <scratch dir>, then writes each
   code cell's printed output, trimmed to what a code window holds at 8 pt, to attach.txt (section 1), locate.txt (the
   signature and the first four source lines), body.txt (the first eight lines of the body), callees.txt and callers.txt
   (the action 3 cell: what the handler calls, then the callers count of get_safe_value), reaches.txt (the four reaches
   lines of sections 2 and 3) and coverage.txt (section 4).
2. Runs client.py, codeact.py and checks.py from this folder and writes what each prints to client.txt, codeact.txt and
   checks.txt.
levels.txt is levels.py's output; it analyses four fresh copies of the checkout and takes many minutes, so it runs on its
own (see levels.py). Tabs in the printed source are kept; content-hw2-v2.py sets them four columns wide.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LECTURE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
scratch = sys.argv[1]
os.makedirs(scratch, exist_ok=True)
env = dict(os.environ)
python = os.path.join(LECTURE, ".venv", "bin", "python")
executed = os.path.join(scratch, "cldk-mcp.executed.ipynb")
subprocess.run([python, os.path.join(LECTURE, ".venv", "bin", "jupyter-execute"), "cldk-mcp.ipynb", "--output", executed],
               cwd=LECTURE, env=env, check=True)


def stdout_of(prefix):
    """The printed output of the one code cell whose source starts with prefix."""
    cells = [c for c in json.load(open(executed))["cells"] if c["cell_type"] == "code" and "".join(c["source"]).startswith(prefix)]
    assert len(cells) == 1, (prefix, len(cells))
    return "".join("".join(o["text"]) for o in cells[0]["outputs"] if o.get("output_type") == "stream" and o["name"] == "stdout")


def write(name, lines):
    with open(os.path.join(HERE, name), "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"{name}: {len(lines)} lines")


write("attach.txt", stdout_of("import time\nfrom cldk import CLDK").splitlines())
write("locate.txt", stdout_of('hit = an.locate(').splitlines()[:5])
write("body.txt", stdout_of("print(an.get_method_bodies(").splitlines()[:8])
action3 = stdout_of("for c in an.callees_of(").splitlines()
write("callees.txt", action3[:-1])
write("callers.txt", action3[-1:])
write("reaches.txt", stdout_of("import networkx as nx\ndef reaches(").splitlines() + stdout_of('print("00011:').splitlines())
write("coverage.txt", stdout_of("cov = an.get_entrypoint_coverage()").splitlines())
for script in ["client", "codeact", "checks"]:
    run = subprocess.run([python, os.path.join(HERE, script + ".py")], cwd=LECTURE, env=env, check=True, capture_output=True,
                         text=True)
    write(script + ".txt", run.stdout.splitlines())
