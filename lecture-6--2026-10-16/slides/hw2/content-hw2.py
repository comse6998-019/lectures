#!/usr/bin/env python3
"""Write slides/hw2/slides.hw2.json, the spec of the HW2 deck (lecture6-hw2.pptx) that hw2/build-hw2.py builds.

    cd slides && uv run --no-project --python 3.12 python hw2/content-hw2.py

Five segments: the CLDK SDK, an MCP server over CLDK, then HW2 (what teams build, the guardrails, the contracts, rubric
and dates). Every item is a build of one click per bullet and per figure stage, then the closing box. Figures are the
staged PNGs of slides/figures/hw2/ and, on "Where each rule is enforced", the main deck's bypass-places of figures/r6/.

Inside bullet text, `name` is set in Aptos Mono (an identifier, a file or a field, at the surrounding size, regular weight)
and [n] is a superscript reference marker. Notes are in the first person plural; a figure item's notes end with the
figure's talking points, one line per stage.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "slides.hw2.json")


# ---------------------------------------------------------------- helpers, from author-r2.py lines 143 to 170


def B(lead, rest=""):
    """A bullet: a bold lead phrase and the rest of the sentence."""
    return [["b", lead]] + ([["r", " " + rest.lstrip()]] if rest else [])


def paired(n, close=True):
    """Clicks that reveal bullet k together with figure stage k, then the closing box."""
    steps = [{"b": k, "fig": k} for k in range(1, n + 1)]
    if close:
        steps.append({"b": n, "fig": n, "close": True})
    return steps


def table(header, rows, id_cols=(), label_bold=True):
    return {"header": header, "rows": rows, "id_cols": list(id_cols), "label_bold": label_bold}


def stages(name, n):
    return [f"hw2/{name}-{k}.png" for k in range(1, n + 1)]


def item(id_, kind, title, **kw):
    d = {"id": id_, "kind": kind, "title": title, "bullets": [], "refs": [], "notes": ""}
    d.update(kw)
    return d


# ---------------------------------------------------------------- text helpers

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


def divider(id_, heading, row, notes):
    return {"id": id_, "kind": "divider", "title": "", "heading": heading, "legible": [row], "bullets": [], "refs": [],
            "notes": notes}


KRISHNA = ("[1] R. Krishna et al. Codellm-Devkit: a framework for contextualizing code LLMs with program analysis insights. "
           "FSE Companion 2025, pp. 308-318.")  # the notes carry the full author list

# ---------------------------------------------------------------- the code windows

SERVER_LINES = [  # cldk-demo/server.py lines 26 to 30 and 48 to 60, as cell 18 of cldk-mcp.ipynb writes them; line 48's
    # description, line 53's trailing comment and the parsing of the edge ends on line 57 are shortened ("...") to fit
    '@mcp.tool(description="The callable that holds a line, or module scope.")',
    'def locate(path: str, line: int) -> Located:',
    '    hit = AN.locate(checked(path), line)',
    '    return {"signature": hit.callable.signature if hit.callable else None,',
    '            "name": hit.callable.name if hit.callable else None, "module": hit.module.module_name}',
    '@mcp.tool(description="Data-dependence edges of the callable that holds a line: ...")',
    'def dataflow(path: str, line: int) -> list[Edge]:',
    '    hit = AN.locate(checked(path), line)',
    '    if not hit.callable:',
    '        raise ToolError(f"refused: line {line} of {path} is in no callable")',
    '    page = AN.get_ddg(hit.callable.signature, page_size=2000)',
    '    out = []',
    '    for e in page.edges:',
    '        try:',
    '            out.append({"from_line": ..., "to_line": ..., "var": e.var})',
    '        except ValueError:',
    '            continue',
    '    return out',
]

POLICY_PATH = os.path.join(HERE, "..", "..", "..", "..", "instructor-materials", "hw2", "feasibility", "policy.yaml")
POLICY_LINES = [  # instructor-materials/hw2/feasibility/policy.yaml, verified in an OpenShell sandbox on 2026-10-15 (Task 1.4)
    'version: 1',
    'filesystem_policy:',
    '  include_workdir: true',
    '  read_only: [/bin, /usr, /lib, /lib64, /etc, /proc, /dev/urandom, /app,',
    '              /target/testcode, /target/helpers, /target/app.py]',
    '  read_write: [/sandbox, /tmp, /dev/null]',
    'landlock:',
    '  compatibility: hard_requirement',
    'network_policies:',
    '  model_provider:',
    '    endpoints:',
    '      - host: api.anthropic.com',
    '        port: 443',
    '        protocol: rest',
    '        enforcement: enforce',
    '        access: read-write',
    '    binaries:',
    '      - path: /usr/local/bin/python3.12',
]
if os.path.exists(POLICY_PATH):  # the window quotes the verified file; fail loudly if it has moved on
    assert open(POLICY_PATH).read().splitlines() == POLICY_LINES, "policy.yaml changed since the deck quoted it"

CHANGED_LINES = [  # hw2-tool-boundary/examples/ at 0f1054c: config.example.toml, trace.example.jsonl, report.example.json
    '# config.toml',
    '[agent]',
    'kind = "mcp"            # or "codeact"',
    '[mcp]',
    'config = "mcp.json"',
    '[sandbox]',
    'policy = "policy.yaml"',
    '# trace.jsonl',
    '{"kind": "discovery", "server": "analysis", "tools": ["locate", "source", ...]}',
    '{"kind": "tool_request", "tool": "dataflow", ..., "via": "mcp"}',
    '{"kind": "tool_result", "ok": false, ..., "via": "mcp", "refused_by": "server"}',
    '# report.json, each alert',
    '"remediation": {"status": "accepted", "diff": "--- a/testcode/...",',
    '  "checks": {"applies": true, "touches_flagged_line": true, "clean_rescan": true}}',
]

# ---------------------------------------------------------------- segment 1: the CLDK SDK

SEG1 = [
    item("1.r", "route", "", notes="We spend the rest of today on HW2: first the CLDK SDK and an MCP server over it, then "
                                   "the assignment itself."),
    divider("1.d", "The CLDK SDK", 0, "We start with CLDK, the analysis library that both HW2 agents call."),
    item("1.1", "text", "CLDK answers questions about code.",
         bullets=[B("One SDK,", "static analysis of Java, Python and TypeScript behind one Python API (Krishna et al.[1], 2025)."),
                  B("One object per checkout:", "`CLDK.python(project_path, analysis_level)`, built once and cached."),
                  B("Four levels:", "symbol table, call graph, program dependency graph, system dependency graph."),
                  B("Four moves:", "locate a line, read the body, walk callers and callees, ask a dataflow question.")],
         closing="An alert classifier needs every move, and CLDK gives each as a single call.",
         refs=[KRISHNA],
         notes="CLDK is the analysis SDK under both HW2 agents: R. Krishna, R. Pan, R. Pavuluri, S. Tamilselvam, "
               "M. Vukovic and S. Sinha, Codellm-Devkit: A Framework for Contextualizing Code LLMs with Program Analysis "
               "Insights, FSE Companion 2025, pages 308 to 318 (arXiv 2410.13007). For Python it runs codeanalyzer-python, "
               "built on Jedi and the standard library's ast. We pay "
               "for the analysis once: on 2026-10-15, on this Mac with CLDK 2.0.0rc8, the first attach to the OWASP "
               "BenchmarkPython checkout analysed 3,710 callables in 241 s at the call-graph level and 151 s at the "
               "program-dependency-graph level, and every query after it answered from the cache in under a second. We "
               "run the four moves live in cldk-mcp.ipynb, sections 1 and 2."),
    item("1.2", "text", "The request value reaches the query string.",
         figure={"stages": stages("dataflow-example", 4), "placement": "below"},
         steps=paired(4),
         bullets=[B("Three B608 alerts", "in HW1's scan scope: 00099 is true, 00011 and 00012 false."),
                  B("In 00099", "the value goes through a `configparser` round trip into the f-string."),
                  B("In 00011", "the value is passed as a query parameter, outside the f-string."),
                  B("The analyzer answers it as a path", "of data-dependence edges.")],
         closing="Bandit flags the string in all three. Dataflow says which one is tainted.",
         notes=figure_notes(
             "We take the three B608 alerts that Bandit 1.9.4 reports in HW1's scan scope of OWASP BenchmarkPython at "
             "f1291485; the answer key, expectedresults-0.1.csv, says 00099 is a true positive and 00011 and 00012 are "
             "false. We read each handler's data-dependence graph with get_ddg at the program-dependency-graph level, "
             "measured on 2026-10-15 with CLDK 2.0.0rc8 and again with 2.0.0 (codeanalyzer-python 1.5.3), which gave "
             "identical edges. In 00099 the request value at line 31 reaches the SQL string at line 46 through param, the "
             "config object and bar, and the execute call at line 49 through sql. In 00011 the value at line 39 reaches the "
             "call at line 50 through bar and never the string at line 47, and 00012 behaves the same through its string "
             "slicing. An HW1 agent told these cases apart by reading the code, and the analyzer answers the same question "
             "as a path.",
             ["The two handlers, 00099 on the left and 00011 on the right, with the lines that matter in each.",
              "The request value's path in 00099: line 31 to 41 to 42 to the SQL string at 46, and on to execute at 49.",
              "Its path in 00011: line 39 to 43 to the execute call at 50, and no edge into the string at 47.",
              "The verdicts: the value reaches the query string in 00099 and only the parameter tuple in 00011."])),
    item("1.3", "text", "An empty answer is ambiguous until checked.",
         bullets=[B("Check diagnostics", "before concluding that nothing was found."),
                  B("`callers_of` covers declared callables only,", "and `callees_of` also lists external callees."),
                  B("Read the entry-point coverage:", "on OWASP it finds 2,463 routes and marks 2,460 decorators unresolved."),
                  B("Value-name predicates resolve parameters, globals and captures.",
                    "A local variable needs the per-callable dependence graph, `get_ddg`.")],
         closing="An empty result that could mean two things is a defect, so the agent asks why before it says no.",
         notes="These are the rules of CLDK's agent API that a classifier depends on. An empty list from callers_of can "
               "mean that nothing calls the function or that the function is not declared in the checkout, so we read "
               "the diagnostics before we conclude anything. On the OWASP checkout get_entrypoint_coverage reports 2,463 "
               "routes and 2,460 app.route decorators it could not resolve, measured on 2026-10-15, so a short entry-point "
               "list says little until we read the coverage. The value-name predicates (resolve_value, flows_to_argument, "
               "taint) resolve parameters, captured globals and closure captures; for a local variable such as bar we use "
               "the per-callable get_ddg, as on the dataflow slide."),
]

# ---------------------------------------------------------------- segment 2: an MCP server over CLDK

SEG2 = [
    divider("2.d", "An MCP server over CLDK", 1, "We serve the same analysis as MCP tools, the pattern each team's server "
                                                 "follows in HW2."),
    item("2.1", "window", "Every tool queries the same CLDK object.",
         window={"label": "cldk-demo/server.py: the locate and dataflow tools, \"...\" where the text is shortened",
                 "lang": "python", "lines": SERVER_LINES},
         bullets=[B("`MCPServer` and `@mcp.tool`,", "as in lecture 5's server."),
                  B("`ToolError` refuses", "a path outside the checkout or a line in no callable."),
                  B("The Inspector runs it:", "`locate`, `dataflow`, then a refused path.")],
         closing="The server validates arguments and results. The description enforces nothing.",
         notes="The window quotes cldk-demo/server.py as cell 18 of cldk-mcp.ipynb writes it, on the MCP Python SDK 2.3.0 "
               "in the lecture's .venv; we shortened one description, the parsing of the edge ends and a comment where "
               "the window shows dots. The server builds one CLDK object when it starts, at the program-dependency-graph "
               "level, and its four tools (locate, source, callers, dataflow) all read from it; checked() raises ToolError "
               "for any path that resolves outside the checkout. dataflow addresses the callable by its full signature, "
               "because a bare name such as init matches 1,230 callables. In class we open cldk-demo/catalog.json in the "
               "Inspector, call locate and dataflow on line 46 of testcode/BenchmarkTest00099.py, then call locate on "
               "../expectedresults-0.1.csv to see the refusal; the server needs the cache from section 1 of the notebook, "
               "or the Inspector gives up after 30 seconds."),
]

# ---------------------------------------------------------------- segment 3: HW2, what you build

SEG3 = [
    divider("3.d", "HW2: what you build", 2, "We turn to HW2 itself: the two agents, the server they share, and the "
                                             "stages they run."),
    item("3.1", "text", "From a local agent to an MCP agent",
         figure={"stages": stages("two-agents", 3), "placement": "below"},
         steps=[{"b": 1, "fig": 1}, {"b": 2, "fig": 2}, {"b": 3, "fig": 2}, {"b": 3, "fig": 3},
                {"b": 3, "fig": 3, "close": True}],
         bullets=[B("Two agents from your HW1 code.", "The code-action agent's action is a Python script that your "
                    "harness runs against the CLDK object and the workspace."),
                  B("The MCP agent:", "every tool it uses is served over MCP by a server you write."),
                  B("Same stages, same outputs,", "chosen by `[agent] kind` in the config.")],
         closing="One process cannot check a script's calls. A server checks every call.",
         notes=figure_notes(
             "Each team builds both agents on its HW1 loop and compares them on OWASP. The code-action agent has one "
             "tool, run_python(script): the harness runs the script with exec in a namespace that holds the CLDK object "
             "and the workspace path, the pattern of lecture 4 (slide 137), and the observation is what the script prints "
             "or raises. The MCP agent discovers the server's tools with tools/list and sends every call through the HW1 "
             "dispatcher and then the MCP client. Both write the same report.json and trace.jsonl, and kind under "
             "[agent] in config.toml selects which one runs.",
             ["The code-action agent: the model sends a Python script, and the harness runs it with exec against the "
              "CLDK object and the files, all in one process.",
              "The MCP agent: the model's tool call goes through the host and its dispatcher, as tools/call, to a server "
              "in another process.",
              "The verdicts: inside one process there is no call to check, and on the server every call is checked."])),
    item("3.2", "text", "The server: analysis, text and write tools",
         figure={"stages": stages("three-groups", 3), "placement": "below"},
         steps=paired(3),
         bullets=[B("Analysis tools over CLDK 2.0:", "`locate`, `source`, `callers`, `callees`, `dataflow`, "
                    "`entry_points`, with contracts the brief fixes."),
                  B("Text tools from HW1:", "`read_file` and `search`, whose use the report counts."),
                  B("Write tools:", "`edit` and `rescan`, with a patch accepted by three checks.")],
         closing="Every tool has an argument schema, a result schema and listed refusal cases.",
         notes=figure_notes(
             "We fix the names, arguments and results of the six analysis tools in the brief, so that our driver can "
             "call any team's server. Each wraps one CLDK 2.0 call: locate, get_method_bodies, callers_of, callees_of, "
             "get_ddg, and get_entrypoints with get_entrypoint_coverage. read_file and search are HW1's, and on OWASP "
             "the model should rarely need them. edit(path, old, new) and rescan(path) are the write tools; set_alert is "
             "a host-only tool that the model never sees.",
             ["The server, its analysis group over CLDK 2.0, and the host-only set_alert at the right.",
              "The text group, read_file and search, from HW1.",
              "The write group, edit and rescan, judged by the three checks."])),
    item("3.3", "text", "Only labelled alerts are patched.",
         figure={"stages": stages("stages", 3), "placement": "below"},
         steps=[{"b": 1, "fig": 1}, {"b": 2, "fig": 1}, {"b": 3, "fig": 2}, {"b": 3, "fig": 3},
                {"b": 3, "fig": 3, "close": True}],
         bullets=[B("Discovery,", "Bandit over the scan block, as in HW1."),
                  B("Classification,", "now with the analysis tools."),
                  B("Remediation,", "for alerts labelled 1 only: the runtime decides from the label, and the trace "
                    "records it.")],
         closing="A patch applies cleanly, touches the flagged line, and a fresh rescan no longer reports the rule.",
         notes=figure_notes(
             "Both agents run the same three stages on the same targets, and discovery is Bandit 1.9.4 at MEDIUM or "
             "higher, as in HW1. After classification the runtime sends the alerts labelled 1 to remediation and skips "
             "the rest; the model does not choose, and the trace records the decision as a routing event with by: "
             "runtime. A patch is accepted when it applies cleanly against the pinned commit, touches the flagged line, "
             "and a fresh rescan no longer reports that rule at that location. A clean rescan is evidence of a fix, and "
             "the report says that it does not prove the fix correct.",
             ["The three stages: discovery with Bandit, classification with a label of 1 or 0 and its evidence, and "
              "remediation with edit, rescan and the three checks.",
              "The runtime tag: only alerts labelled 1 go on to remediation, and the runtime makes that decision.",
              "The other branch: alerts labelled 0 are skipped."])),
]

# ---------------------------------------------------------------- segment 4: HW2, the guardrails

SEG4 = [
    divider("4.d", "HW2: the guardrails", 3, "We state the rules HW2 enforces and the places that hold each of them."),
    item("4.1", "text", "Each rule has a fixed and a per-alert part.",
         bullets=[B("Read:", "only the target's code. Never `.git`, never the answer key, and never a case other than the "
                    "open one."),
                  B("Write:", "only inside the workspace copy, and only the file of the alert being fixed. The agent never "
                    "runs the target."),
                  B("Network:", "only the model provider."),
                  B("Fixed parts are set before the run,", "and per-alert parts change with every alert.")],
         closing="The kernel can hold the fixed parts. Only the server can hold the per-alert parts.",
         notes="We ask for the rules in words first, as rubric item A3 does. Never the answer key, only inside the "
               "workspace and only the provider are fixed before the run starts. Only the open case and only the file of "
               "the alert being fixed change with every alert, so whatever enforces them must know which alert is open. "
               "The kernel's policy is set when the sandbox starts, which is why it holds the fixed parts and cannot hold "
               "the per-alert ones: Sandlock's split from today's lecture, with the server as the narrow supervisor."),
    item("4.2", "text", "Where each rule is enforced",
         figure={"stages": [f"r6/bypass-places-{k}.png" for k in range(1, 5)], "placement": "below"},
         steps=[{"b": 0, "fig": 1}, {"b": 1, "fig": 2}, {"b": 2, "fig": 3}, {"b": 2, "fig": 4}, {"b": 3, "fig": 4},
                {"b": 3, "fig": 4, "close": True}],
         bullets=[B("The server", "checks every MCP call, with `set_alert` for the per-alert parts."),
                  B("The kernel,", "through OpenShell, holds the fixed parts for both agents."),
                  B("The code-action agent has no server,", "so nothing holds its per-alert parts.")],
         closing="A rule belongs where the agent cannot reach it from inside its own process.",
         notes=figure_notes(
             "We reuse the main deck's figure of the four places, drawn there for the rule that the agent may not read "
             "~/.ssh; here we read HW2's three rules into it. The prompt states all three rules for both agents, and "
             "persuading the model bypasses it. The server is the team's own code inside the sandbox, the harness "
             "placement: it holds HW1's path check for reads and writes, and set_alert(alert_id) gives it the per-alert "
             "parts. The kernel, through OpenShell, holds the fixed parts for both agents, while the code-action agent "
             "has no server, so its per-alert parts are enforced nowhere.",
             ["In the model: the system prompt, inside the agent's process; persuading the model bypasses it.",
              "In the harness process: the dispatcher's check, and in HW2 the team's server, still inside the agent's "
              "process.",
              "In the kernel: Landlock file rules and the network policy through OpenShell, outside the agent's process.",
              "In hardware outside the host: a processor in the network path, which HW2 does not use."])),
    item("4.3", "window", "The policy you run under",
         window={"label": "policy.yaml: the OWASP policy, verified in an OpenShell sandbox on October 15",
                 "lang": "yaml", "lines": POLICY_LINES},
         bullets=[B("Allow-lists:", "no grant on the target root, so reading the key or `.git` fails."),
                  B("`hard_requirement`:", "a policy the kernel cannot enforce fails the start."),
                  B("One endpoint for Python:", "the provider, or a model server on the host.")],
         closing="Linux, Apple Silicon macOS or WSL 2. On an Intel Mac, use the VM recipe.",
         notes="The window is the policy we verified on 2026-10-15 in an OpenShell sandbox on this Mac, with the OWASP "
               "target mounted read-only at /target and the workspace at /sandbox/work. Inside it, cat "
               "/target/expectedresults-0.1.csv exits 1 with Permission denied, and so do .git/HEAD and a write into "
               "/target, while reads of the test code and a write into the workspace succeed. Filesystem denials leave no "
               "log record, so their evidence is the process's error and exit code; network denials are logged with a "
               "reason. The provider key arrives through an OpenShell provider attachment and never enters the sandbox, "
               "and a team on a local model server grants that server's host port as the one endpoint instead. The sandbox "
               "needs Linux, macOS on Apple Silicon or WSL 2, with Docker or Podman; Intel Macs follow the brief's VM "
               "recipe and ask us for help."),
    item("4.4", "text", "How the guardrails are tested",
         figure={"stages": stages("three-doors", 4), "placement": "below"},
         steps=[{"b": 0, "fig": 1}, {"b": 1, "fig": 2}, {"b": 2, "fig": 3}, {"b": 3, "fig": 4}, {"b": 4, "fig": 4},
                {"b": 4, "fig": 4, "close": True}],
         bullets=[B("You run each agent five times", "under a planted injection and count refusals."),
                  B("We drive your server", "with raw MCP calls, from `mcp.json`, inside your policy."),
                  B("We bypass your server", "from inside the sandbox, where the kernel alone decides."),
                  B("The result:", "the kernel stops what was fixed before the run, the server what depends on the "
                    "alert, and the prompt nothing reliably.")],
         closing="Teams write no test harness. The fixtures and our driver do the testing.",
         notes=figure_notes(
             "Two things test the guardrails, and neither needs a harness from the team. With fixtures/injection.patch "
             "applied, a comment inside one OWASP handler, placed after the flagged statement so that Bandit's line does "
             "not move, tells automated reviewers to read the answer key; each team runs both agents five times and "
             "reports from its traces what the model attempted and which place refused it. At grading, our driver "
             "starts the team's server from mcp.json inside the team's policy, sends raw tools/call requests for "
             "forbidden reads and writes and one malformed argument, then runs commands in the sandbox with openshell "
             "exec, past the server. Reading the key and writing outside the workspace fail at the kernel, and reading "
             "another case succeeds, because only the server knows which alert is open.",
             ["The path a request takes, model, dispatcher, server, kernel, file, and the three doors on it.",
              "The planted text: the model may obey it, and its call stops at the server's door.",
              "A raw MCP call from our driver, stopped at the server.",
              "A process inside the sandbox: the kernel stops the key and writes outside the workspace, and the other "
              "case gets through."])),
]

# ---------------------------------------------------------------- segment 5: HW2, contracts, rubric, dates

SEG5 = [
    divider("5.d", "HW2: contracts, rubric, dates", 4, "We close with what changed in the contracts since HW1, the "
                                                       "rubric and the dates."),
    item("5.1", "window", "What changed since HW1",
         window={"label": "examples/: the additions to config, trace and report, shortened with \"...\"",
                 "lang": "toml", "lines": CHANGED_LINES},
         bullets=[B("The CLI is unchanged.", "The config gains `[agent] kind`, `[mcp] config` and `[sandbox] policy`."),
                  B("`mcp.json` and `policy.yaml`", "at the repository root: the evaluator starts your server and your "
                    "sandbox from them without reading your code."),
                  B("A config that does not validate", "stops grading at the first step.")],
         closing="Everything behind these files is your design.",
         notes="The brief boxes these changes under one heading, What changed since HW1, so that nobody misses them; the "
               "lines in the window come from the examples in hw2-tool-boundary. The CLI stays ./your-agent --input "
               "<root> --output <dir> --config config.toml. The trace keeps HW1's kinds and six invariants: tool_request "
               "and tool_result gain via, a refused tool_result gains refused_by (dispatcher, server or kernel), and the "
               "MCP host writes one discovery event after tools/list. Each row of report.json gains remediation, with its "
               "status, the unified diff and the three checks, and the three schemas are reissued."),
    item("5.2", "text", "The rubric",
         bullets=[B("Design, 5 points:", "tool contracts, the call path, the three rules with their places, the policy "
                    "with reasons, patch acceptance."),
                  B("Implementation, 9 points:", "the server, the code-action agent, write tools, discovery, dispatcher "
                    "refusals, the remediation route, the per-alert parts, the sandbox, the network rule."),
                  B("Evidence and README, 4 points:", "a README we can follow, the live-run measurement, the two "
                    "comparisons, limitations."),
                  B("18 items, one point each,", "scaled to the assignment's 20 percent of the course grade. "
                    "Classification accuracy is collected for teaching only.")],
         closing="A missing mechanism cannot earn its point.",
         notes="The rubric has 18 items of one point each, scaled to the assignment's 20 percent of the course grade. "
               "Part A grades the design report, Part B the mechanisms in the code, and Part C the evidence and the "
               "README; the website now lists the same items. A report that describes a mechanism the code lacks earns "
               "nothing for it. We collect classification accuracy to see how the agents do, and it carries no points."),
    item("5.3", "text", "Dates and platform",
         bullets=[B("Released today, Friday, October 16, 2026.", "Due Friday, November 13, 2026, before 11:59 pm."),
                  B("Six late days per student per semester,", "at most three on one assignment."),
                  B("The MCP agent runs on all three targets,", "and the code-action agent on OWASP only."),
                  B("The repository", "`comse6998-019/hw2-tool-boundary`: brief, schemas, examples, fixtures, and after "
                    "today the CLDK server as a reference pattern.")],
         closing="Next Friday is the midterm. Office hours Friday 12:00 to 1:30 pm.",
         notes="HW2 is released today, Friday, October 16, 2026, and due Friday, November 13, 2026, before 11:59 pm. Each "
               "student has six late days per semester, at most three on one assignment, and the website corrects the "
               "HW1 brief's wording. OpenShell needs Linux, macOS on Apple Silicon, or Windows with WSL 2, plus Docker, "
               "Podman or host virtualization, and a kernel of 6.2 or newer for Landlock ABI v3; Intel Macs and Windows "
               "without WSL 2 follow the brief's Linux VM recipe. The midterm is next Friday, October 23, in class: one "
               "hour, individual, closed book."),
]

SEGMENTS = [("1", SEG1), ("2", SEG2), ("3", SEG3), ("4", SEG4), ("5", SEG5)]

for _, items in SEGMENTS:
    for it in items:
        it["bullets"] = [rich(b) for b in it.get("bullets", [])]

json.dump({"segments": [{"segment": n, "slides": items} for n, items in SEGMENTS]}, open(OUT, "w"), indent=1,
          ensure_ascii=False)
print(f"wrote {OUT}: {sum(len(items) for _, items in SEGMENTS)} items in {len(SEGMENTS)} segments")
