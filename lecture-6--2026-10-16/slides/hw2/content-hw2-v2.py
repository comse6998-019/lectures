#!/usr/bin/env python3
"""Write slides/hw2/slides.hw2.json, the spec of the HW2 deck (lecture6-hw2.pptx) as a CLDK primer, which hw2/build-hw2.py
builds. It replaces content-hw2.py, whose spec is kept as slides.hw2.v1.json.

    cd slides && uv run --no-project --python 3.12 python hw2/content-hw2-v2.py

Rahul, 2026-10-15 23:15: "HW2 must quite simply teach CLDK's bare essentials for HW's python projects so that the students
can write an MCP over CLDK's APIs and call that. The students then also do codeact over CLDK's APIs. The rest of HW2 will be
me walking through the brief." Five segments: CLDK essentials, the moves on the analysis object, an MCP server over CLDK,
the two agents that call it, and the hand-over to the brief.

Every code window quotes a real file and every output window a real capture:
  - code comes from cldk-mcp.ipynb (found by the start of its cell), cldk-demo/server.py (found by its first and last line)
    and the scripts in hw2/captures/ (levels.py, client.py, codeact.py), read at generation time;
  - a line longer than the window holds at 8 pt (WIDTH characters of Aptos Mono) is shown broken inside its brackets, or
    with its trailing comment on the line above, and the shown lines must parse to the same Python syntax tree as the
    source lines (same_code), so the window shows the program that ran;
  - outputs come from hw2/captures/*.txt, written by captures/capture.py and captures/levels.py; a printed line longer than
    WIDTH wraps at a space with a two-space hanging indent, and tabs are set four columns wide.

Inside bullet text, `name` is set in Aptos Mono and [n] is a superscript reference marker. Notes are in the first person
plural; every build's notes end with "Click by click." (or, on a figure build, "The figure, stage by stage.") and one line
per click.
"""
import ast
import glob
import json
import os
import re
import textwrap
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LECTURE = os.path.abspath(os.path.join(HERE, "..", ".."))
CAP = os.path.join(HERE, "captures")
OUT = os.path.join(HERE, "slides.hw2.json")
WIDTH = 93  # Aptos Mono at 8 pt in the 5724144 EMU code box: 5724144 / 12700 / (0.6 x 8) characters


# ---------------------------------------------------------------- helpers, from content-hw2.py (author-r2.py lines 143 to 170)


def B(lead, rest=""):
    """A bullet: a bold lead phrase and the rest of the sentence."""
    return [["b", lead]] + ([["r", " " + rest.lstrip()]] if rest else [])


def paired(n, close=True):
    """Clicks that reveal bullet k together with figure stage k, then the closing box."""
    steps = [{"b": k, "fig": k} for k in range(1, n + 1)]
    if close:
        steps.append({"b": n, "fig": n, "close": True})
    return steps


def stages(name, n):
    return [f"hw2/{name}-{k}.png" for k in range(1, n + 1)]


def item(id_, kind, title, **kw):
    d = {"id": id_, "kind": kind, "title": title, "bullets": [], "refs": [], "notes": ""}
    d.update(kw)
    return d


CODE_OR_MARKER = re.compile(r"`([^`]+)`|(\[\d+\])")


def rich(bullet):
    """Split each bold or regular segment at `code` spans and [n] markers: code becomes a "c" run (Aptos Mono, regular, as
    lectures/CLAUDE.md sets identifiers), a marker an "m" run (superscript)."""
    out = []
    for kind, text in bullet:
        pos = 0
        for m in CODE_OR_MARKER.finditer(text):
            if m.start() > pos:
                out.append([kind, text[pos:m.start()]])
            out.append(["c", m.group(1)] if m.group(1) else ["m", m.group(2)])
            pos = m.end()
        if pos < len(text):
            out.append([kind, text[pos:]])
    return out


def figure_notes(text, per_stage):
    """Notes that end with the figure's talking points, one numbered line per stage (lectures/CLAUDE.md, Figure slide)."""
    lines = "\n".join(f"{k}. {line}" for k, line in enumerate(per_stage, start=1))
    return f"{text}\n\nThe figure, stage by stage.\n{lines}"


def click_notes(text, per_click):
    """Notes that end with what to say on each click of the build, one numbered line per click."""
    lines = "\n".join(f"{k}. {line}" for k, line in enumerate(per_click, start=1))
    return f"{text}\n\nClick by click.\n{lines}"


def divider(id_, heading, row, notes):
    return {"id": id_, "kind": "divider", "title": "", "heading": heading, "legible": [row], "bullets": [], "refs": [],
            "notes": notes}


def steps(*clicks):
    """Explicit clicks: each a (bullets shown, output window shown) pair; the closing box is added as the last click."""
    out = [{"b": b, "out": o} for b, o in clicks]
    out.append({"b": clicks[-1][0], "out": clicks[-1][1], "close": True})
    return out


KRISHNA = ("[1] R. Krishna et al. Codellm-Devkit: a framework for contextualizing code LLMs with program analysis insights. "
           "FSE Companion 2025, pp. 308-318.")  # the notes carry the full author list


# ---------------------------------------------------------------- the sources the windows quote

NB = json.load(open(os.path.join(LECTURE, "cldk-mcp.ipynb")))
SERVER = open(os.path.join(LECTURE, "cldk-demo", "server.py")).read().splitlines()
CATALOG = open(os.path.join(LECTURE, "cldk-demo", "catalog.json")).read().splitlines()


def cell(prefix):
    """The source lines of the one code cell of cldk-mcp.ipynb that starts with prefix."""
    found = [c for c in NB["cells"] if c["cell_type"] == "code" and "".join(c["source"]).startswith(prefix)]
    assert len(found) == 1, (prefix, len(found))
    return "".join(found[0]["source"]).splitlines()


def span(lines, first, last):
    """The lines from the one line that starts with first to the next line that starts with last, both included."""
    i = [k for k, line in enumerate(lines) if line.startswith(first)]
    assert len(i) == 1, (first, i)
    j = next(k for k in range(i[0], len(lines)) if lines[k].startswith(last))
    return lines[i[0]:j + 1]


def script(name):
    return open(os.path.join(CAP, name)).read().splitlines()


def codeact_script():
    """The SCRIPT string of captures/codeact.py, the code-action script the kernel runs."""
    tree = ast.parse(open(os.path.join(CAP, "codeact.py")).read())
    value = next(n.value.value for n in tree.body if isinstance(n, ast.Assign) and n.targets[0].id == "SCRIPT")
    return value.strip("\n").splitlines()


def capture(name):
    return open(os.path.join(CAP, name)).read().rstrip("\n").split("\n")


def same_code(source, shown):
    """The shown lines parse to the same syntax tree as the source lines: a window may break a line, never change it."""
    def tree(lines):
        return ast.dump(ast.parse(textwrap.dedent("\n".join(lines))))
    assert tree(source) == tree(shown), f"window differs from its source:\n{chr(10).join(shown)}"


# Lines longer than WIDTH, as shown: broken inside their brackets, an implicit string concatenation, or a trailing comment
# moved to its own line above. same_code checks every window that uses them.
SHOWN = {
    'print(len(an.callers_of("get_safe_value")), "callers of the helper HW1\'s false positives share")':
        ['print(len(an.callers_of("get_safe_value")),',
         '      "callers of the helper HW1\'s false positives share")'],
    '        g.add_edge(e.src.split("@")[-1].split(":")[0], e.dst.split("@")[-1].split(":")[0], var=e.var)':
        ['        g.add_edge(e.src.split("@")[-1].split(":")[0],',
         '                   e.dst.split("@")[-1].split(":")[0], var=e.var)'],
    '            "name": hit.callable.name if hit.callable else None, "module": hit.module.module_name}':
        ['            "name": hit.callable.name if hit.callable else None,',
         '            "module": hit.module.module_name}'],
    '@mcp.tool(description="Data-dependence edges of the callable that holds a line: from-line, to-line, variable.")':
        ['@mcp.tool(description="Data-dependence edges of the callable that holds a line: "',
         '                      "from-line, to-line, variable.")'],
    '    page = AN.get_ddg(hit.callable.signature, page_size=2000)  # full signature: a bare name like init matches 1,230 callables':
        ['    # full signature: a bare name like init matches 1,230 callables',
         '    page = AN.get_ddg(hit.callable.signature, page_size=2000)'],
    '            out.append({"from_line": int(e.src.split("@")[-1].split(":")[0]), "to_line": int(e.dst.split("@")[-1].split(":")[0]), "var": e.var})':
        ['            out.append({"from_line": int(e.src.split("@")[-1].split(":")[0]),',
         '                        "to_line": int(e.dst.split("@")[-1].split(":")[0]), "var": e.var})'],
    'for level in ["symbol_table", "call_graph", "program_dependency_graph", "system_dependency_graph"]:':
        ['for level in ["symbol_table", "call_graph", "program_dependency_graph",',
         '              "system_dependency_graph"]:'],
    '    fresh = shutil.copytree("cldk-demo/owasp", f"{out}/{level}", ignore=shutil.ignore_patterns(".codeanalyzer", ".git"))':
        ['    fresh = shutil.copytree("cldk-demo/owasp", f"{out}/{level}",',
         '                            ignore=shutil.ignore_patterns(".codeanalyzer", ".git"))'],
    '    print(f"{level:<25} {len(ans[level].get_callables_overview())} callables {time.time() - t:4.0f} s", flush=True)':
        ['    print(f"{level:<25} {len(ans[level].get_callables_overview())} callables "',
         '          f"{time.time() - t:4.0f} s", flush=True)'],
}


def code(source, python=True, keep_blank=False):
    """The lines a code window shows for these source lines: long lines as SHOWN gives them, blank lines dropped."""
    shown = []
    for line in source:
        if not line.strip() and not keep_blank:
            continue
        shown.extend(SHOWN.get(line, [line]))
    if python:
        same_code(source, shown)
    long = [line for line in shown if len(line) > WIDTH]
    assert not long, f"lines longer than {WIDTH}: {long}"
    return shown


def output(lines):
    """Printed lines as an output window shows them: tabs four columns wide, a line longer than WIDTH wrapped at a space with a
    two-space hanging indent."""
    shown = []
    for line in lines:
        line = line.expandtabs(4)
        while len(line) > WIDTH:
            cut = line.rfind(" ", 0, WIDTH)
            assert cut > 2, line
            shown.append(line[:cut])
            line = "  " + line[cut + 1:]
        shown.append(line)
    return shown


def window(label, lines, out_label=None, out_lines=None, lang="python"):
    w = {"label": label, "lang": lang, "lines": lines}
    if out_lines is not None:
        w["output"] = {"label": out_label, "lines": out_lines}
    return w


def version(pkg):
    meta = glob.glob(os.path.join(LECTURE, ".venv", "lib", "python3.12", "site-packages", f"{pkg}-*.dist-info", "METADATA"))
    assert len(meta) == 1, (pkg, meta)
    return next(line.split(": ", 1)[1].strip() for line in open(meta[0]) if line.startswith("Version: "))


CLDK_V, ANALYZER_V, MCP_V = version("cldk"), version("codeanalyzer_python"), version("mcp")
CAPTURED = time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(os.path.join(CAP, "attach.txt"))))
LEVELS_ON = time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(os.path.join(CAP, "levels.txt"))))
ENV = f"the lecture's .venv (Python 3.12, cldk {CLDK_V}, codeanalyzer-python {ANALYZER_V}, mcp {MCP_V})"
RUN = f"captured on {CAPTURED} by hw2/captures/capture.py, which executes the notebook headless in {ENV}"
RUN_SCRIPT = f"run on {CAPTURED} by hw2/captures/capture.py in {ENV}"

# ---------------------------------------------------------------- numbers the slides and notes quote, read from the captures

ATTACH = capture("attach.txt")[0]                              # "3710 callables, 8 s"
CALLABLES, WARM_S = re.fullmatch(r"(\d+) callables, (\d+) s", ATTACH).groups()
LEVEL_ROWS = [line for line in capture("levels.txt") if re.match(r"\w+\s+\d+ callables\s+\d+ s$", line)]
assert len(LEVEL_ROWS) == 4, LEVEL_ROWS
LEVEL_S = {line.split()[0]: int(line.split()[-2]) for line in LEVEL_ROWS}
REFUSAL = [line for line in capture("levels.txt") if line.startswith("CodeanalyzerUsageException")]
assert len(REFUSAL) == 1 and "Returning an empty result would be indistinguishable" in REFUSAL[0], REFUSAL
LEVELS_EARLIER = ""
if os.path.exists(os.path.join(CAP, "levels.run1.txt")):
    _early = [line.split() for line in capture("levels.run1.txt") if re.match(r"\w+\s+\d+ callables\s+\d+ s$", line)]
    LEVELS_EARLIER = ("An earlier run the same evening, also with other work on the machine, gave "
                      + ", ".join(f"{row[-2]} s" for row in _early) + " for the same four levels. ")
COVERAGE = capture("coverage.txt")[0]
EPS, UNRESOLVED = re.match(r"(\d+) entry points;.*'app\.route': (\d+)", COVERAGE).groups()
CALLERS = capture("callers.txt")[0]
N_CALLERS = re.match(r"(\d+) callers", CALLERS).group(1)
CLIENT = capture("client.txt")
assert CLIENT[0] == "['locate', 'source', 'callers', 'dataflow']" and CLIENT[3].startswith("True "), CLIENT
N_EDGES = re.match(r"(\d+) edges", CLIENT[2]).group(1)
CODEACT = capture("codeact.txt")
assert CODEACT == ["BenchmarkTest00099_post ['31', '41', '42', '46']", "BenchmarkTest00011_post False"], CODEACT
REACHES = capture("reaches.txt")
assert "(['31', '41', '42', '46']" in REACHES[0] and "(None, None)" in REACHES[2], REACHES
CHECKS = capture("checks.txt")


def check(prefix):
    line = next(line for line in CHECKS if line.startswith(prefix))
    return line[len(prefix):].strip()


def checked(text):
    """A phrase the notes quote from checks.txt, asserted to be there."""
    assert any(text in line for line in CHECKS), text
    return text


EXTERNAL_ERR = check("callers_of('execute'):")


def thousands(n):
    return f"{int(n):,}"


# ---------------------------------------------------------------- the code windows

ATTACH_CODE = code(cell("import time\nfrom cldk import CLDK"))
LEVELS_CODE = code(span(script("levels.py"), "for level in", "    print("))
REFUSAL_CODE = code(span(script("levels.py"), "try:", "    print("))
LOCATE_CODE = code(cell("hit = an.locate("))
BODY_CODE = code(cell("print(an.get_method_bodies("))
MOVE3_CODE = code(cell("for c in an.callees_of("))
REACHES_CODE = code(cell("import networkx as nx\ndef reaches(")[1:9])      # the function, without the import and the prints
assert REACHES_CODE[0].startswith("def reaches(") and REACHES_CODE[-1] == "    return None, None", REACHES_CODE
COVERAGE_CODE = code(cell("cov = an.get_entrypoint_coverage()"))
TOOL_CODE = code(span(SERVER, 'mcp = MCPServer("cldk")', '            "name": hit.callable.name'))
DATAFLOW_CODE = code(span(SERVER, '@mcp.tool(description="Data-dependence', "    return out"))
CATALOG_CODE = json.dumps(json.loads("\n".join(CATALOG)), indent=1).splitlines()  # the file at one-space indent, to fit
assert json.loads("\n".join(CATALOG_CODE)) == json.loads("\n".join(CATALOG)) and max(map(len, CATALOG_CODE)) <= WIDTH
INSPECTOR = "npx @modelcontextprotocol/inspector --web --catalog cldk-demo/catalog.json"
assert INSPECTOR in "".join(c for cl in NB["cells"] for c in cl["source"]), "the notebook no longer gives this command"
CLIENT_CODE = code(span(script("client.py"), "async def main():", "        print(bad.is_error"))
CODEACT_CODE = code(codeact_script())

# ---------------------------------------------------------------- segment 1: CLDK essentials

SEG1 = [
    item("1.r", "route", "",
         notes="We spend the rest of today on HW2. We learn the CLDK calls that answer questions about a Python project, wrap "
               "them as MCP tools, call them from the MCP agent and from a code-action script, and then walk through the "
               "brief."),
    divider("1.d", "CLDK essentials", 0,
            "We start with what CLDK is, how it attaches to a checkout, and what each analysis level can answer."),
    item("1.1", "window", "CLDK answers questions about Python code.",
         bullets=[B("One Python API", "runs static analysis over Java, Python and TypeScript code (Krishna et al.[1], 2025)."),
                  B("`pip install cldk`", "installs it on Python 3.11 or newer."),
                  B("For Python,", "the engine is `codeanalyzer-python`, built on Jedi and the standard library's `ast`."),
                  B("HW2's project", "is the OWASP BenchmarkPython checkout that HW1 scanned.")],
         window=window("cldk-mcp.ipynb, section 1: attach the analysis to the checkout", ATTACH_CODE,
                       "output: a warm attach, read from the cache in cldk-demo/owasp/.codeanalyzer", output([ATTACH])),
         steps=steps((1, False), (2, False), (3, False), (4, True)),
         closing="Every question is a method on one cached object per checkout.",
         refs=[KRISHNA],
         notes=click_notes(
             "CLDK is R. Krishna, R. Pan, R. Pavuluri, S. Tamilselvam, M. Vukovic and S. Sinha, Codellm-Devkit: A Framework "
             "for Contextualizing Code LLMs with Program Analysis Insights, FSE Companion 2025, pages 308 to 318 (arXiv "
             f"2410.13007). We use cldk {CLDK_V} from PyPI, whose package metadata requires Python 3.11 or newer; for a "
             f"Python project it runs codeanalyzer-python {ANALYZER_V}. The window is section 1 of cldk-mcp.ipynb, and its "
             f"output was {RUN}: {CALLABLES} callables in {WARM_S} s, read from the cache that the first attach left in "
             "cldk-demo/owasp/.codeanalyzer. The checkout is OWASP BenchmarkPython at f1291485, the commit HW1 used.",
             ["CLDK is one Python API over static analysis of three languages, from the paper by Krishna and colleagues "
              "at FSE 2025.",
              "Installing it is one pip command, and it needs Python 3.11 or newer.",
              "For a Python project the analyzer is codeanalyzer-python: Jedi resolves the names and ast gives the "
              "structure.",
              f"The project is HW1's OWASP checkout. The output arrives: {thousands(CALLABLES)} callables, attached from "
              f"the cache in {WARM_S} seconds.",
              "The closing: one object per checkout, and every question we ask is a method call on it."])),
    item("1.2", "window", "The analysis level sets what CLDK answers.",
         bullets=[B("`symbol_table`", "knows what is declared, and `call_graph` who calls whom."),
                  B("`program_dependency_graph`", "adds flow inside each callable, and `system_dependency_graph` "
                    "adds flow across them.")],
         window=window("levels.py: the first attach at each level, each on a fresh copy of the checkout", LEVELS_CODE,
                       f"output: the first attach at each level on this Mac, {LEVELS_ON}", output(LEVEL_ROWS)),
         steps=steps((1, False), (2, True)),
         closing="Choose the level your questions need, and pay for it once.",
         notes=click_notes(
             "levels.py is in slides/hw2/captures. For each level it copies cldk-demo/owasp without its analysis cache and "
             f"attaches once, so each row is a first attach. Measured on {LEVELS_ON} on this Mac with cldk {CLDK_V} and "
             f"codeanalyzer-python {ANALYZER_V}: symbol table {LEVEL_S['symbol_table']} s, call "
             f"graph {LEVEL_S['call_graph']} s, program dependency graph {LEVEL_S['program_dependency_graph']} s, system "
             f"dependency graph {LEVEL_S['system_dependency_graph']} s, {thousands(CALLABLES)} callables at every level. "
             f"{LEVELS_EARLIER}On this project the levels differ less than their names suggest; every first attach "
             "also creates a virtualenv for the analyzer inside the copy's cache folder. The specification's earlier measurement, with 2.0.0rc8, was 241 s "
             f"at call-graph level and 151 s at the dependency level. From the cache an attach takes seconds ({WARM_S} s "
             "on the previous slide). The notebook and HW2's server use program_dependency_graph, the lowest level with "
             "dataflow.",
             ["The two cheap levels: the symbol table knows what is declared, and the call graph knows who calls whom.",
              "The two dependency levels add flow, inside a callable and across callables. The output arrives: every first "
              "attach took minutes on this Mac, the system dependency graph the longest.",
              "The closing: choose the level the questions need, pay once, and read the cache after that."])),
    item("1.3", "window", "A question above the level raises an error.",
         bullets=[B("`get_ddg` on a symbol-table analysis", "raises `CodeanalyzerUsageException`, which names both levels."),
                  B("An empty answer there", "would look like a callable with no data dependence, so CLDK refuses to "
                    "give one.")],
         window=window("levels.py, continued: a dataflow question to the symbol-table analysis", REFUSAL_CODE,
                       "output", output(REFUSAL)),
         steps=steps((1, True), (2, True)),
         closing="Below the level it needs, a question raises an error.",
         notes=click_notes(
             "The same run of levels.py, after the four attaches, asks the symbol-table analysis for the data-dependence "
             "graph of BenchmarkTest00099_post. The window shows the exception exactly as it printed; its message is "
             "CLDK's own. This is the rule the agent API follows everywhere: an answer that could mean two things is "
             "refused, and the refusal says what to do instead.",
             ["get_ddg needs the program dependency graph. Asked of a symbol-table analysis, it raises, and the message "
              "names the level asked for and the level built.",
              "Why it raises: an empty list would look exactly like a callable with no dependence, so the library refuses "
              "rather than mislead.",
              "The closing: below the level a question needs, the answer is an error, never an empty result."])),
]

# ---------------------------------------------------------------- segment 2: the moves on the analysis object

SEG2 = [
    divider("2.d", "Moves on the analysis object", 1,
            "We take one Bandit alert, B608 at line 46 of BenchmarkTest00099.py, through the moves a classifier needs: "
            "locate, read, callers and callees, and dataflow."),
    item("2.1", "window", "Move 1: locate the callable that holds a line.",
         bullets=[B("In:", "a `path` and a `line`, which is what a Bandit alert gives."),
                  B("Out:", "`callable.signature`, `callable.name` and `module`, and the callable's text in `source`."),
                  B("Outside any callable,", "`callable` is `None` and a diagnostic names the case: `module_scope`, or "
                    "`file_not_in_graph` for a file the analyzer never saw.")],
         window=window("cldk-mcp.ipynb, section 2: the callable that holds line 46", LOCATE_CODE,
                       "output: the signature, then the first lines of source", output(capture("locate.txt"))),
         steps=steps((1, False), (2, True), (3, True)),
         closing="Locate turns an alert's file and line into a callable's name.",
         notes=click_notes(
             f"The window is section 2 of cldk-mcp.ipynb, {RUN}. Bandit 1.9.4 reports B608 at line 46 of "
             "testcode/BenchmarkTest00099.py, the f-string that builds the SQL query, and locate returns the enclosing "
             "handler with its full signature. The two other outcomes come from hw2/captures/checks.py, run the same day: "
             "line 1 of app.py gives callable None and the diagnostic module_scope, "
             f"\"{checked('line 1 is at module scope in app.py.')}\", and a file that does not exist gives callable None "
             f"and file_not_in_graph, \"{checked('is not covered by any analysed module')}\". The result also carries node_id, "
             "the statement's own id, which the next slide uses.",
             ["The input is exactly what a scanner alert carries: a path relative to the checkout and a line number.",
              "The output arrives: the full signature, testcode.BenchmarkTest00099.init.BenchmarkTest00099_post, because "
              "the handler is nested in init, and the source starts at its def line.",
              "Outside any callable the answer is still unambiguous: callable is None, and a diagnostic says module scope "
              "or file not in the graph.",
              "The closing: an alert's file and line become the name that the rest of the API takes."])),
    item("2.2", "window", "Move 2: read the body by signature.",
         bullets=[B("`get_method_bodies`", "maps each signature to its body."),
                  B("A signature with no body", "is absent, so test `key in result`."),
                  B("`get_source(node_id)`", "returns one statement, such as line 46.")],
         window=window("cldk-mcp.ipynb, section 2: the body of the handler, by its signature", BODY_CODE,
                       "output: the first eight lines of the body", output(capture("body.txt"))),
         steps=steps((1, True), (2, True), (3, True)),
         closing="The agent reads the one function the alert names.",
         notes=click_notes(
             f"The window is section 2 of cldk-mcp.ipynb, {RUN}; the output is the first eight of the body's 28 lines, and "
             "the SQL string is line 19 of the body, line 46 of the file. From hw2/captures/checks.py, the same day: "
             f"get_method_bodies of an unknown signature returns {check('get_method_bodies of an unknown signature:')}, an "
             f"empty dict, and get_source with the node_id that locate returned gives {check('get_source(node_id):')}. "
             "The body is what the agent should read: HW1's read rule allows the open case and no other, and the whole "
             "file would also carry the GET handler.",
             ["get_method_bodies is a bulk call: a list of signatures in, a dict keyed by signature out. The output shows "
              "the handler's first lines.",
              "A signature without a body is left out of the dict rather than mapped to None, so the agent tests "
              "membership first.",
              "Below the callable, get_source with the node id from locate returns the single statement, here the f-string "
              "at line 46.",
              "The closing: the agent reads the function the alert names and nothing else, which is HW1's read rule."])),
    item("2.3", "window", "Move 3: callers and callees by name.",
         bullets=[B("`callers_of` covers declared callables,", "and `callees_of` adds externals."),
                  B("An ambiguous name", "raises `AmbiguousName`, and `in_module=` narrows it.")],
         window=window("cldk-mcp.ipynb, section 2: what the handler calls, and who calls a helper", MOVE3_CODE,
                       "output: file, line and callee, then the callers of get_safe_value",
                       output(capture("callees.txt") + capture("callers.txt"))),
         steps=steps((1, True), (2, True)),
         closing="One call lists the 74 handlers that use the constant helper.",
         notes=click_notes(
             f"The window is section 2 of cldk-mcp.ipynb, {RUN}. callees_of lists what BenchmarkTest00099_post calls: an "
             "external callee comes back with an empty file and line 0, and the two in the checkout carry their file and "
             f"line. {N_CALLERS} callables call get_safe_value, the helper in helpers/separate_request.py that returns the "
             "constant \"bar\", so a case that takes its value from it is safe. From hw2/captures/checks.py, the same day: "
             f"callers_of('execute') raises {EXTERNAL_ERR}, and callers_of('init') "
             "raises AmbiguousName because 1,230 callables match, with the hint to narrow by in_module or more of the "
             "dotted path.",
             ["callers_of answers for callables declared in the checkout, and an external name raises. callees_of includes "
              "externals: Cursor.execute is the sink Bandit worried about. Then the callers line: 74 handlers call the helper.",
              "A bare name such as init matches 1,230 callables, one per case, so CLDK raises with the candidates instead "
              "of picking one.",
              "The closing: one call tells the agent which cases depend on the constant helper."])),
    item("2.4", "text", "Move 4: dataflow answers the taint question.",
         figure={"stages": stages("dataflow-example", 4), "placement": "below"},
         steps=paired(4),
         bullets=[B("Bandit flags B608", "on 00099, 00011 and 00012, and only 00099 is true."),
                  B("In 00099", "the request value reaches the f-string through `configparser`."),
                  B("In 00011", "it reaches only the parameter tuple of `cur.execute`."),
                  B("`get_ddg`", "gives the edges by line, and a path search answers it.")],
         closing="Bandit flags the string in all three. Dataflow says which one is tainted.",
         notes=figure_notes(
             "We take the three B608 alerts that Bandit 1.9.4 reports in HW1's scan scope of OWASP BenchmarkPython at "
             "f1291485; the answer key, expectedresults-0.1.csv, marks 00099 true and 00011 and 00012 false. The edges in "
             "the figure are those of get_ddg at the program-dependency-graph level, measured on 2026-10-15 with CLDK "
             "2.0.0rc8 and again with 2.0.0 (codeanalyzer-python 1.5.3), which gave identical edges "
             "(slides/figures/hw2/src/check-dataflow.py asserts them). In 00099 the request value at line 31 reaches the "
             "SQL string at line 46 through param, the config object and bar, and the execute call at line 49 through sql. "
             "In 00011 the value at line 39 reaches the call at line 50 through bar and never the string at line 47; 00012 "
             "behaves the same through its string slicing. The next slide is the code that finds these paths.",
             ["The two handlers, 00099 on the left and 00011 on the right, with the lines that matter in each.",
              "The request value's path in 00099: line 31 to 41 to 42 to the SQL string at 46, and on to execute at 49.",
              "Its path in 00011: line 39 to 43 to the execute call at 50, and no edge into the string at 47.",
              "The verdicts: the value reaches the query string in 00099 and only the parameter tuple in 00011."])),
    item("2.5", "window", "The reaches helper finds a path in the edges.",
         bullets=[B("Node ids end in `@line:col`,", "so the helper keys the graph by line."),
                  B("For a local such as `bar`,", "`get_ddg` is the dependable call.")],
         window=window("cldk-mcp.ipynb, sections 2 and 3: reaches, a path over a handler's dependence edges", REACHES_CODE,
                       "output: the calls that ask whether the request reaches the SQL string",
                       output([REACHES[0], REACHES[2]])),
         steps=steps((1, False), (1, True), (2, True)),
         closing="The classifier's question becomes a path search over the edges.",
         notes=click_notes(
             f"The window is the reaches function of cldk-mcp.ipynb, section 2; the output is its four calls in sections 2 "
             f"and 3, {RUN}. Each DDG edge names a source node and a target node, whose ids end in @line:col, and the "
             "variable that flows; reaches keeps the line, builds a networkx DiGraph and asks for a path. The four calls "
             f"printed: {'; '.join(REACHES)}. The window shows the two that ask about the SQL string. CLDK's value-name predicates (resolve_value, flows_to_argument, taint) "
             "resolve parameters, captured globals and closure captures, so for a local variable such as bar the "
             "per-callable get_ddg is the dependable call. CLDK's own reaches method answers a different question, whether "
             "one callable can call another.",
             ["The code: the helper takes a handler and two lines, keys the dependence edges by line, and asks networkx for "
              "a path.",
              "The output arrives: 00099 has a path from the request to the SQL string, 00011 has none, and both reach "
              "their execute call.",
              "Why not a higher-level predicate: resolve_value and flows_to_argument resolve parameters, globals and "
              "captures, and bar is a local.",
              "The closing: the classifier's question is a path search, and only the true positive has the path."])),
    item("2.6", "window", "An empty answer is ambiguous until checked.",
         bullets=[B("On this checkout", f"`get_entrypoints` finds {thousands(EPS)} entry points, and the coverage marks "
                    f"{thousands(UNRESOLVED)} `app.route` decorators unresolved."),
                  B("Read the diagnostics", "before concluding that nothing was found."),
                  B("Check `has_resolution_edges`", "before reading a `None` callee from `get_callsites_for` as "
                    "unresolved.")],
         window=window("cldk-mcp.ipynb, section 4: the entry points and the report on how they were found", COVERAGE_CODE,
                       "output", output([COVERAGE])),
         steps=steps((1, True), (2, True), (3, True)),
         closing="An empty result that could mean two things is a defect, so the agent asks why.",
         notes=click_notes(
             f"The window is section 4 of cldk-mcp.ipynb, {RUN}. get_entrypoints returns {thousands(EPS)} entry points, "
             f"and get_entrypoint_coverage reports the frameworks it detected, click and flask, and {thousands(UNRESOLVED)} "
             "app.route decorators it could not resolve; its own docstring says the detection pass under-approximates by "
             "design, so silence is its failure mode. An empty list from get_entrypoints cannot tell \"none\" from "
             "\"missed\", and the coverage can. has_resolution_edges says whether get_callsites_for can resolve call "
             f"sites on this backend; checks.py prints {check('has_resolution_edges:')} on the local backend, and the "
             "flag is false only on a Neo4j graph built below the level where resolution runs.",
             ["The output: thousands of entry points, and nearly as many route decorators left unresolved, so a short list "
              "would say little.",
              "The rule: read the diagnostics and the coverage before an empty answer becomes a no.",
              "The same rule for call sites: has_resolution_edges explains a None callee before the agent reads it as "
              "unresolved.",
              "The closing: an answer that could mean two things is a defect, so the agent asks which."])),
]

# ---------------------------------------------------------------- segment 3: an MCP server over CLDK

SEG3 = [
    divider("3.d", "An MCP server over CLDK", 2,
            "We serve the same moves as MCP tools, the pattern each team's server follows in HW2."),
    item("3.1", "window", "A tool is a function with a contract.",
         bullets=[B("`MCPServer` and `@mcp.tool`", "publish each tool's name, description and argument schema, and the "
                    "result schema from `Located`."),
                  B("`ToolError`", "is a refusal that the client receives as an error result.")],
         window=window("cldk-demo/server.py: the server, the path check and the locate tool", TOOL_CODE),
         steps=[{"b": 1}, {"b": 2}, {"b": 2, "close": True}],
         closing="The server checks shapes, and the description enforces nothing.",
         notes=click_notes(
             f"The window is cldk-demo/server.py as section 5 of cldk-mcp.ipynb writes it, on the MCP Python SDK {MCP_V} "
             "(MCPServer from mcp.server, ToolError from mcp.server.mcpserver.exceptions), blank lines left out. The "
             "server builds one CLDK object, AN, when it starts. checked() resolves a path against the checkout and "
             "raises ToolError for anything outside it or not a file. The SDK derives the input schema from the "
             "signature (path a string, line an integer) and, because the return type is the TypedDict Located, an "
             "output schema titled Located; tools/list carries both, as the Inspector shows. "
             "Lecture 5's rule holds: only argument and result shapes are enforced, and the description is text for the "
             "model.",
             ["MCPServer and the decorator: the function's name, its description string and its typed signature become "
              "the tool's contract, and Located becomes the result schema.",
              "ToolError: the path check refuses a path outside the checkout, and the client sees an error result instead "
              "of a crash.",
              "The closing: the server checks shapes, and nothing checks what the description promises."])),
    item("3.2", "window", "The dataflow tool returns edges by line.",
         bullets=[B("Each dependence edge", "becomes `from_line`, `to_line` and `var`, the fields of `Edge`."),
                  B("A line in no callable", "is a refusal.")],
         window=window("cldk-demo/server.py: the dataflow tool", DATAFLOW_CODE),
         steps=[{"b": 1}, {"b": 2}, {"b": 2, "close": True}],
         closing="Every tool reads the same analysis object, and every answer traces to a line.",
         notes=click_notes(
             "The window is the dataflow tool of cldk-demo/server.py; the Edge TypedDict above it in the file has the "
             "three fields the bullet names, so the output schema lists them. The tool addresses the callable by its full "
             "signature because a bare name such as init matches 1,230 callables. An edge whose end has no line, such as "
             f"the entry node, is skipped. Called on line 46 of 00099 it returns {N_EDGES} edges (hw2/captures/client.py, "
             "next segment). The agent does the path search over them, as reaches did, or a team adds a reaches tool on "
             "the same edges.",
             ["The tool: locate, then get_ddg by the full signature, one page of up to 2,000 edges, then each edge "
              "flattened to two line numbers and the variable, the three fields of the Edge TypedDict.",
              "Refusals: a line outside any callable raises ToolError. The search for a path stays with the agent, or with "
              "a tool you add.",
              "The closing: the four tools share one analysis object, and every answer points at lines of the checkout."])),
    item("3.3", "window", "The Inspector runs the server from a catalog.",
         bullets=[B("The catalog", "names the interpreter and the server script."),
                  B("`tools/list`", "shows each tool's contract, and a path outside the checkout comes back as an error "
                    "result.")],
         window=window("cldk-demo/catalog.json, written by section 6 of the notebook", CATALOG_CODE,
                       "terminal: start the Inspector", [INSPECTOR], lang="toml"),
         steps=steps((1, True), (2, True)),
         closing="What the Inspector shows is what your agent's host sees.",
         notes=click_notes(
             "This is the live demonstration. Run section 1 of the notebook first: the server attaches when it starts, "
             f"from the cache section 1 builds, in seconds, and the Inspector gives up on a server that "
             "takes longer than 30 seconds to answer (Inspector 2.10.1, its default connectionTimeout, checked on "
             "2026-10-15). The catalog holds this Mac's absolute paths, which is why it is not committed. In the Inspector: "
             "tools/list, then locate on testcode/BenchmarkTest00099.py line 46, dataflow on the same line, and locate on "
             "../expectedresults-0.1.csv, which returns an error result with \"refused: ../expectedresults-0.1.csv is not "
             "a file of the target\". That path leaves the checkout. The answer key inside the checkout, "
             "expectedresults-0.1.csv, passes this demo's check; in HW2 the team's server refuses it under the read rule, "
             "and the sandbox policy makes it unreadable.",
             ["The catalog: one stdio server, the lecture's Python and server.py. The second window is the command.",
              "tools/list shows the four tools with their input and output schemas, locate on line 46 returns the "
              "handler, and the refused path comes back as an error result, which is what the model would see.",
              "The closing: the Inspector is a host, so what it shows is what our agent's host gets."])),
]

# ---------------------------------------------------------------- segment 4: the MCP agent and the code-action agent

SEG4 = [
    divider("4.d", "The MCP and code-action agents", 3,
            "We call the same API from the two agents HW2 asks for: through an MCP client, and from a script."),
    item("4.1", "window", "The MCP agent calls tools through a client.",
         bullets=[B("The host", "starts the server from `mcp.json` and lists its tools."),
                  B("Every call", "passes the HW1 dispatcher, and a refusal sets `is_error`.")],
         window=window("client.py: list the tools, call locate and dataflow, send a refused path", CLIENT_CODE,
                       "output", output(CLIENT)),
         steps=steps((1, False), (2, True)),
         closing="Your HW1 dispatcher stays, and the MCP client sits behind it.",
         notes=click_notes(
             f"The window is hw2/captures/client.py, which starts cldk-demo/server.py over stdio with the SDK's Client "
             f"(mcp {MCP_V}), {RUN_SCRIPT}. It is the four-call check the server was tested with on 2026-10-15, printing "
             f"its answers: the four tool names, the callable locate returns, {N_EDGES} dataflow edges of which two leave "
             "line 31, and the refused path with is_error True (isError on the wire). In HW2 the MCP agent's host reads "
             "the same command from mcp.json, records a discovery event after tools/list, offers the model the list "
             "minus host-only tools such as set_alert, and sends every call through the HW1 dispatcher before the client.",
             ["The host side: mcp.json says how to start the server, and tools/list, minus the host-only tools, is what "
              "the model is offered.",
              "Every call goes through the dispatcher, then the client. The output arrives: names, the located handler, "
              "the edges from line 31, and the refusal as an error result.",
              "The closing: nothing of HW1's dispatcher is thrown away, and the client sits behind it."])),
    item("4.2", "text", "The code-action agent acts in one process.",
         figure={"stages": stages("two-agents", 3), "placement": "below"},
         steps=paired(3),
         bullets=[B("The code-action agent's action", "is a script, run with `exec`."),
                  B("The MCP agent's action", "is a tool call, sent as `tools/call`."),
                  B("Only the server", "sees each call, so only it can check one.")],
         closing="A tool call crosses a boundary that can check it.",
         notes=figure_notes(
             "Each team builds both agents on its HW1 loop. The code-action agent has one tool, run_python(script): the "
             "harness runs the script with exec in a namespace that holds the CLDK object and the workspace path, the "
             "kernel of lecture 4 (slide 137), and the observation is what the script prints or raises. The MCP agent "
             "sends every call through the HW1 dispatcher and then the MCP client to the server, which runs in another "
             "process. The figure leaves out the MCP client and the sandbox on purpose.",
             ["The code-action agent: the model sends a Python script, and the harness runs it with exec against the "
              "CLDK object and the files, all in one process.",
              "The MCP agent: the model's tool call goes through the host and its dispatcher, as tools/call, to a server "
              "in another process.",
              "The verdicts: inside one process there is no call to check, and on the server every call is checked."])),
    item("4.3", "window", "The script asks the same dataflow question.",
         bullets=[B("No dispatcher", "sees the calls inside one script."),
                  B("The sandbox", "is the only fence, as lecture 4 found (slide 154)."),
                  B("The read, write and network rules", "apply to both agents.")],
         window=window("the model's script, run by lecture 4's kernel with namespace {\"an\": an}", CODEACT_CODE,
                       "observation: what the script printed", output(CODEACT)),
         steps=steps((1, True), (2, True), (3, True)),
         closing="Nothing checks a script's calls, so both agents run in OpenShell.",
         notes=click_notes(
             "hw2/captures/codeact.py holds lecture 4's kernel (kernel.py, lecture 4 slide 137: exec with stdout "
             "redirected, a traceback on error) with namespace {\"an\": an}, the analysis object of the notebook, and runs "
             f"this script through it ({RUN_SCRIPT}). The script locates both alerts, builds each "
             "handler's dependence graph by line and asks for a path: 00099 prints the same path as reaches, "
             "['31', '41', '42', '46'], and 00011 prints False. Our first draft converted the node ids to integers and the "
             "kernel returned a ValueError traceback on the node 'entry'; that is the observation a model would have read "
             "and fixed. Lecture 4, slide 154, asked where CodeAct can confine writes, and the answer was the operating "
             "system.",
             ["The harness sees one script, so none of the calls inside it passes a dispatcher. The observation arrives: "
              "the path for 00099 and False for 00011.",
              "The only place left to confine the script is below the interpreter, the sandbox, as lecture 4 concluded.",
              "The brief's rules, read, write and network, bind both agents, and only the MCP agent has a server to hold "
              "the per-alert parts.",
              "The closing: a script cannot be checked call by call, so both agents run inside OpenShell."])),
]

# ---------------------------------------------------------------- segment 5: the brief

SEG5 = [
    divider("5.d", "The brief", 4, "We close the HW2 part by walking through the brief, released today."),
    item("5.1", "text", "The brief, section by section",
         bullets=[B("What you build:", "the code-action agent and the MCP agent, the server with its analysis, text and "
                    "write tools, and the stages both agents run."),
                  B("The guardrails:", "the read, write and network rules, the prompt, server and kernel that hold them, "
                    "and the policy you run under."),
                  B("How they are tested:", "your five live runs under a planted injection, and our driver against your "
                    "server and sandbox."),
                  B("Contracts, rubric and dates:", "18 rubric items, one point each. Due Friday, November 13, 2026, before "
                    "11:59 pm, with six late days per student per semester, at most three on one assignment.")],
         closing="HW2 is released today in comse6998-019/hw2-tool-boundary, with the brief, schemas, examples and fixtures.",
         notes=click_notes(
             "We now walk through the PDF. HW2 is released Friday, October 16, 2026, and due Friday, November 13, 2026, "
             "before 11:59 pm. Six late days per student per semester, at most three on one assignment. "
             "The rubric has 18 items, one point each, scaled to the assignment's 20 percent of the course grade. The "
             "sections follow the HW2 specification, section 3: what teams build (the two agents, the server and its tool "
             "groups, the stages), the guardrails (the three rules, the places that hold them, the OpenShell policy), how "
             "they are tested (the team's live runs under fixtures/injection.patch and the staff driver), the report, "
             "the contracts, the rubric, and the dates and platform. After class the repository also gets "
             "cldk-mcp.ipynb and cldk-demo/server.py as the reference pattern.",
             ["What you build: both agents from your HW1 loop, the server with its three tool groups, and discovery, "
              "classification and remediation.",
              "The guardrails: read, write and network, each held at the prompt, the server or the kernel, and the policy "
              "file.",
              "How they are tested: five runs of each agent under the planted injection, and our driver on your server "
              "and inside your sandbox.",
              "Contracts, rubric and dates, verbatim: 18 items of one point, November 13 before 11:59 pm, six late days "
              "and at most three per assignment.",
              "The closing: the repository is released today, and we open the PDF."])),
]

SEGMENTS = [("1", SEG1), ("2", SEG2), ("3", SEG3), ("4", SEG4), ("5", SEG5)]

for _, items in SEGMENTS:
    for it in items:
        it["bullets"] = [rich(b) for b in it.get("bullets", [])]

json.dump({"segments": [{"segment": n, "slides": items} for n, items in SEGMENTS]}, open(OUT, "w"), indent=1,
          ensure_ascii=False)
print(f"wrote {OUT}: {sum(len(items) for _, items in SEGMENTS)} items in {len(SEGMENTS)} segments")
