#!/usr/bin/env python3
"""Write slides/openshell/slides.openshell.json, the spec of lecture 6's OpenShell segment rebuilt from first principles,
which openshell/build-openshell.py builds into a fragment deck for patch-r6c.py to splice into lecture6.pptx.

    cd slides && uv run --no-project --python 3.12 python openshell/content-openshell.py

Task 4.6, step 2 (plan docs/superpowers/plans/2026-10-15-week6-hw2.md). Rahul, 2026-10-15 22:20: the old segment was
"haphazard and not teaching ready"; he approved a first-principles sequence with a figure for every build. One segment, "7",
of fourteen builds: the brief's builds 1 to 10 and 12 to 15. Build 11, "Real credentials never enter the sandbox.", is
the kept build of the installed deck, which the splice moves in after build 10.

The running example is Cyberbird (Rahul, 22:40 and 22:50): every build shows the abstract mechanism first and then
Cyberbird as its instance, in the figure's last stage and in the last bullet, which opens "In Cyberbird's case,". The
captured lines come from the run of 2026-10-15 in instructor-materials/hw2/feasibility/cyberbird/ (OpenShell 0.1.4 on
Colima, Cyberbird reactive on alert bc284c6b with openai:qwen3.8-27b, ACCEPTED in 8 model calls).

Layout rule, measured: with the builder's estimator (fitted to PowerPoint, 1.38 em per line) a 16.5 by 5.8 cm figure stays
at or above 90 percent of the column only when the body holds four one-line paragraphs, so most builds carry four one-line
bullets and no lead-in, and the notes carry the full sentences the brief lists (rulings in the task report).

Inside bullet text, `name` is set in Aptos Mono and [n] is a superscript reference marker. Notes are in the first person
plural; every figure build's notes end with "The figure, stage by stage." and one line per stage, the window build's with
"Click by click.".
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "slides.openshell.json")
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
FEAS = os.path.join(ROOT, "instructor-materials", "hw2", "feasibility")


# ---------------------------------------------------------------- helpers, from hw2/content-hw2.py (author-r2.py lines 143 to 170)


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
    """Stage paths under slides/figures/, such as "r6c/three-needs-1.png"."""
    return [f"{name}-{k}.png" for k in range(1, n + 1)]


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


def steps(*clicks):
    """Explicit clicks, each (bullets shown, figure stage shown); the closing box is added as the last click."""
    out = [{"b": b, "fig": f} for b, f in clicks]
    out.append({"b": clicks[-1][0], "fig": clicks[-1][1], "close": True})
    return out


def guide(chapters):
    return ("[1] COMS E6998-019, OpenShell: Architecture, Enforcement, and Policy (the course's guide to commit be7af99), "
            f"{chapters}.")


REPO = "[2] NVIDIA. OpenShell, commit be7af99. https://github.com/NVIDIA/OpenShell"
SENTRY = "NVIDIA. Open Agent Safety Platform announcement, September 28, 2026. NVIDIA, 2026."
TIGERA = ("Tigera. NVIDIA OpenShell Secures the Agent. Who Governs the Fleet? 2026 (a vendor's reading of OpenShell's "
          "documentation).")

# ---------------------------------------------------------------- the policy the window quotes

POLICY_FILE = os.path.join(FEAS, "cyberbird-policy.yaml")
POLICY_LINES = [  # instructor-materials/hw2/feasibility/cyberbird-policy.yaml (commit c2ab5e3), its three comment lines left out
    'version: 1',
    'filesystem_policy:',
    '  include_workdir: true',
    '  read_only: [/bin, /usr, /lib, /etc, /proc, /dev/urandom, /app, /app/fixtures]',
    '  read_write: [/sandbox, /tmp, /dev/null, /app/runs]',
    'landlock:',
    '  compatibility: hard_requirement',
    'network_policies:',
    '  model_server:',
    '    endpoints:',
    '      - host: host.lima.internal',
    '        port: 8080',
    '        protocol: tcp',
    '    binaries:',
    '      - path: /usr/local/bin/python3.12',
]
if os.path.exists(POLICY_FILE):  # the window quotes the recorded run's policy; fail loudly if the file has moved on
    _src = [ln for ln in open(POLICY_FILE).read().splitlines() if not ln.lstrip().startswith("#")]
    assert _src == POLICY_LINES, "cyberbird-policy.yaml changed since the deck quoted it"

# ---------------------------------------------------------------- the segment

SEG = []

# 1 -------------------------------------------------------------------------------------------------- three-needs
SEG.append(item(
    "7.1", "text", "An agent works through the kernel.", title_marker="[1]",
    figure={"stages": stages("r6c/three-needs", 5), "placement": "below"},
    steps=steps((1, 1), (2, 2), (3, 3), (3, 4), (4, 5)),
    bullets=[B("Files:", "the agent reads a repository and must never read the key."),
             B("Processes:", "each shell, interpreter or scanner it starts has its authority."),
             B("Connections:", "it calls the model's API, GitHub, or any host on the network."),
             B("In Cyberbird's case,", "it reads a case, runs `bandit` and calls a model server.")],
    closing="A rule the kernel enforces holds whatever the model chooses.",
    refs=[guide("chapter 1")],
    notes=figure_notes(
        "We start from what an agent needs from the machine. An agent is a model that chooses an action and a program "
        "that carries it out, and the program runs as processes, a process being a running program with its own memory, "
        "open files and user identity. Every file it opens, every program it starts and every connection it makes is a "
        "system call, a request to the kernel, the part of Linux that grants or refuses it. On the fourth click we point "
        "at the dashed line: a rule placed there refuses the call even when the model has been talked into making it, "
        "which a prompt cannot do (the guide's exercise in chapter 1). Our running example for the whole section is "
        "Cyberbird, the course's reactive agent from lecture 2, working Bandit's SQL injection alert bc284c6b at "
        "testcode/BenchmarkTest00283.py line 46 of its OWASP fixture.\n\n"
        "We ran Cyberbird inside OpenShell 0.1.4 on October 15, 2026 (Colima on the instructor's Mac, model "
        "openai:qwen3.8-27b on the local llama-swap server): it read the case and helpers/db_sqlite.py in a disposable "
        "copy of the fixture, searched four times, edited the case, ran bandit when it submitted, and finished ACCEPTED "
        "after 8 model calls in 13.5 s. The captures are in instructor-materials/hw2/feasibility/cyberbird/.",
        ["Files: open(), read() and write() reach the repository, the key and the workspace. The other two arrows are "
         "reserved as ghosts.",
         "Processes: fork() and execve() start a shell, Python or a scanner, each a child with the agent's authority.",
         "Connections: connect() reaches the model's API, GitHub, or anything else on the network.",
         "The dashed line: a rule can sit below the program, where the kernel decides every request.",
         "In action: cyberbird works alert bc284c6b. It reads BenchmarkTest00283.py and helpers/ in its workspace copy, "
         "runs python and bandit, and connects to the model server."])))

# 2 -------------------------------------------------------------------------------------------------- components
SEG.append(item(
    "7.2", "text", "Each OpenShell component has its own job.", title_marker="[1]",
    figure={"stages": stages("r6c/components", 7), "placement": "below"},
    steps=steps((1, 1), (1, 2), (1, 3), (2, 4), (3, 5), (3, 6), (4, 7)),
    bullets=[B("The client, gateway and driver", "create, record and place sandboxes."),
             B("The sandbox runtime", "fences the agent's processes from inside the workload."),
             B("The trusted supervisor", "decides every connection from outside the workload."),
             B("In Cyberbird's case,", "Docker ran it, and only the model server was reachable.")],
    closing="The keys and the network decisions stay outside the agent's workload.",
    refs=[guide("chapters 2, 6 and 7")],
    notes=figure_notes(
        "We name the parts before we use them, on the guide's Figure 1. The client (the openshell CLI, the TUI or an SDK) "
        "sends management requests to OpenShell's gateway, the control plane that authenticates every caller, stores "
        "every sandbox record and hands configuration to drivers and supervisors. The compute driver turns a record into "
        "platform resources on Docker, Podman, Kubernetes or a microVM and decides placement, which is on which host or "
        "node the workload and its supervisor run. The untrusted workload is the agent with its tools and child "
        "processes, code we assume may be faulty or hostile, together with the sandbox runtime, the small OpenShell "
        "program inside it that launches processes, installs the kernel fences and pauses network calls for mediation. "
        "The trusted supervisor runs outside that boundary, holds the policy and the real credentials, decides each "
        "outbound connection, and talks to the runtime over the authenticated runtime channel, a private connection "
        "whose ends authenticate each other.\n\n"
        "On Docker the workload and the supervisor are separate containers joined by a private Unix socket, the "
        "workload's own network is removed, and the supervisor uses the host's network (guide, 6.3). In the recorded run "
        "the client was the instructor's terminal, the driver Docker on Colima, and the policy admitted one destination, "
        "the model server.",
        ["The client: the CLI, TUI or an SDK sends management requests. The agent and its tools in the untrusted "
         "workload are the frame.",
         "The gateway: identity and records, and the configuration it hands on.",
         "The compute driver provisions the workload and places the supervisor. The note defines placement.",
         "The sandbox runtime, inside the workload: process control and mediation.",
         "The trusted supervisor, outside: policy and credentials, the authenticated runtime channel from the runtime, "
         "and the control session it opens to the gateway.",
         "The approved external service: what remains reachable, through the supervisor.",
         "In action: Rahul's terminal, Docker on Colima, cyberbird and bandit in the workload, and a supervisor that "
         "admits only the model server."])))

# 3 -------------------------------------------------------------------------------------------------- lifecycle
SEG.append(item(
    "7.3", "text", "A sandbox is a record before a container.", title_marker="[1]",
    figure={"stages": stages("r6c/lifecycle", 6), "placement": "below"},
    steps=steps((1, 1), (2, 2), (2, 3), (3, 4), (3, 5), (4, 6)),
    bullets=[B("The record comes first:", "the gateway stores it before any driver runs."),
             B("The driver provisions,", "then the supervisor connects back and says hello."),
             B("Ready means the API can reach it,", "and it says nothing about the agent."),
             B("In Cyberbird's case,", "`sandbox list` showed it Ready within four seconds.")],
    closing="The gateway records each phase, so an interrupted create can be reconciled.",
    refs=[guide("chapter 4")],
    notes=figure_notes(
        "We follow one sandbox from request to deletion. The gateway checks the request (identity, workspace, names, "
        "template, policy) and persists the record before any container exists, with a UUID, an attachment epoch that "
        "stops a re-attached provider from reusing old evidence, and a runtime generation that stops a new run from "
        "inheriting old runtime credentials. The driver then provisions: Docker and the VM may answer early and keep "
        "preparing the image, Kubernetes reconciles, and a watch stream reports progress. Ready means the gateway "
        "considers the sandbox usable through its API, which it decides once the supervisor has connected back and said "
        "hello; Error, Deleting and Stopped still outrank it, so Ready says nothing about whether the agent works. Stop "
        "keeps the record and stops the compute, start runs it again, and delete removes it, with what is retained "
        "depending on the backend: Docker keeps the stopped container, Kubernetes its Sandbox resource, the VM its "
        "overlay.\n\n"
        "Captured for Cyberbird on October 15, 2026 (OpenShell 0.1.4, Colima): create printed \"Created sandbox: "
        "cyberbird\", \"[0.0s] Requesting compute...\", \"[0.0s] Sandbox allocated\" and \"[0.1s] Starting sandbox "
        "Container created\"; sandbox get showed \"Ready: True (DependenciesReady) - Supervisor session connected\", "
        "runtime-generation d1326079-66a5-44ab-9db3-51e13ac8dc46 and auth-epoch 1; sandbox list at 22:42:24 EDT printed "
        "\"cyberbird  2026-10-16 02:42:20  Ready\" (CREATED is UTC, so 22:42:20 EDT); delete printed \"✓ Sandbox "
        "cyberbird deletion accepted; cleanup is pending\".",
        ["The record persisted: the gateway's checks and what it stores, in the Provisioning phase.",
         "Provisioning: the driver creates the resources. Docker and the VM may return early.",
         "The supervisor's hello: it connects out to the gateway and opens the control stream that later carries "
         "exec's relay.",
         "Ready: usable through the API, as the gateway publishes it.",
         "The phases that leave or outrank Ready: Error from the driver, Stopped and Deleting by stop, start and delete. "
         "The note: Ready says the supervisor talked back, and nothing about the agent.",
         "In action: cyberbird's record, Docker on Colima with the image cyberbird:1, the captured condition, and the "
         "sandbox list row."])))

# 4 -------------------------------------------------------------------------------------------------- gateway-authority
SEG.append(item(
    "7.4", "text", "The gateway holds authority and records.", title_marker="[1]",
    figure={"stages": stages("r6c/gateway-authority", 5), "placement": "below"},
    steps=steps((1, 1), (2, 2), (2, 3), (3, 4), (4, 5)),
    bullets=[B("Who:", "a user's token or client key, or a supervisor's own credential."),
             B("What and which:", "the method's permission, then the workspace and object."),
             B("The store", "writes a record only if its version is still the one read."),
             B("In Cyberbird's case,", "Rahul's client key created `cyberbird` in `default`.")],
    closing="The gateway checks caller, method and object before a conditional write.",
    refs=[guide("chapter 5")],
    notes=figure_notes(
        "We open the gateway. Authentication establishes who is calling: an OIDC token, issued by an identity provider, "
        "or a client key over mutual TLS for people and tools, and runtime material bound at creation for a supervisor, "
        "which never reuses the user's token or key. Authorization runs twice: every RPC method declares the principal "
        "kind (user, sandbox or peer), the scope (an operation category such as sandbox:write) and the role (Platform "
        "Admin, Workspace Admin or Workspace User) it needs, and the gateway refuses to start if a method lacks the "
        "declaration; passing that check authorizes no particular object, so the handler then checks the workspace, the "
        "group that holds sandboxes and providers, and the object. The store writes by compare-and-swap on the resource "
        "version, a number that changes on every update, so a stale writer is rejected. A reconcile loop, run by one "
        "replica under a renewable lease, compares the records with what the backends report and sweeps the inventory "
        "every minute.\n\n"
        "For Cyberbird: openshell status on the instructor's gateway reported \"Authentication: Authenticated (mTLS "
        "transport)\"; CreateSandbox declares a user principal, scope sandbox:write and the workspace user role "
        "(proto/openshell.proto at be7af99); the CLI's workspace defaults to default; sandbox get showed \"Resource "
        "version: 14\" at Ready.",
        ["Who: gate 1 authenticates the request.",
         "What: gate 2, the method's declared permission.",
         "Which: gate 3, the workspace and the object.",
         "The store's conditional update, and the reconcile loop: desired against observed state, leases, the inventory "
         "sweep.",
         "In action: sandbox create cyberbird, the client key, CreateSandbox's declaration, workspace default, and the "
         "record at resource version 14. Its supervisor signs in with its own runtime material."])))

# 5 -------------------------------------------------------------------------------------------------- runtime-startup
SEG.append(item(
    "7.5", "text", "The agent starts with reduced privileges.", title_marker="[1]",
    figure={"stages": stages("r6b/runtime-startup", 4), "placement": "below"},
    steps=steps((1, 1), (1, 2), (2, 3), (3, 4), (4, 4)),
    bullets=[B("Each child drops privilege first:", "non-root IDs and no capabilities."),
             B("Landlock", "fences its files, above a baseline that guards the runtime."),
             B("Seccomp", "blocks risky calls and pauses `connect()` for the broker."),
             B("In Cyberbird's case,", "its user, uid 1000, could not list its own home directory.")],
    closing="The fences are in the kernel before the agent's first instruction runs.",
    refs=[guide("chapter 7")],
    notes=figure_notes(
        "We look inside the workload at start-up. The runtime's launcher thread starts every child, and the launch order "
        "is enforced by type state, Rust types that make it hard to start the agent before the boundary is confirmed. "
        "Each child first drops privilege: a capability is one slice of root's power, such as administering the network, "
        "and the child gives up all of them, takes non-root user and group IDs, and sets no_new_privs, a one-way flag "
        "that stops any later program from gaining privilege. Landlock is a Linux module that lets a process restrict "
        "its own and its children's file access: a mandatory baseline at Landlock ABI v3 (kernel 6.2 or newer) protects "
        "the runtime's private /.openshell files, and the policy's lists are layered on top, so an access must satisfy "
        "both. Seccomp filters system calls: it blocks tracing, mount changes, BPF and io_uring, and its "
        "user-notification mode pauses connect() and hands it to the broker, the part of the runtime that asks the "
        "supervisor.\n\n"
        "Cyberbird's run shows the result (October 15, 2026): id inside the sandbox printed \"uid=1000(agent) "
        "gid=1000(agent)\"; the supervisor logged \"Isolation boundary enforcement confirmed\" before \"Isolation "
        "boundary agent started\"; and ls /home/agent, the agent's own home directory, failed with \"Permission "
        "denied\", because no list in the policy names /home.",
        ["The operator's image runs unmodified. Once the boundary is provisioned, attached and confirmed and networking is "
         "prepared, the launcher thread starts each child.",
         "Each child gives up privilege first: non-root user and group IDs, every capability set dropped, and "
         "no_new_privs, a one-way setting.",
         "The Landlock baseline (ABI v3 or newer, which covers truncation) protects the private /.openshell hierarchy. "
         "The user's filesystem policy is layered above it, so an access must satisfy both.",
         "Seccomp: the network filter sits on the launcher thread and each child inherits it. The child adds its "
         "system-call and self-protection filters, then executes the agent's command, and the supervisor manages the "
         "running workload."])))

# 6 -------------------------------------------------------------------------------------------------- policy-pins
SEG.append(item(
    "7.6", "text", "A policy states a workload's authority.", title_marker="[1]",
    figure={"stages": stages("r6c/policy-pins", 6), "placement": "below"},
    steps=steps((1, 1), (1, 2), (2, 3), (3, 4), (3, 5), (4, 6)),
    bullets=[B("The kernel holds", "`filesystem_policy` and `landlock`, fixed at the start."),
             B("The runtime sets", "`process`, the workload's user and group, at creation."),
             B("The supervisor holds", "`network_policies` and `network_middlewares`."),
             B("In Cyberbird's case,", "one rule lets `python3.12` reach the model server.")],
    closing="File rules are fixed at the start, and network rules can change live.",
    refs=[guide("chapter 10")],
    notes=figure_notes(
        "We define a policy before we read one. A policy is the workload's authority written down: which files it may "
        "use, which destinations it may reach and which requests it may make, as a YAML document with version: 1 and up "
        "to five sections, each enforced by a component we have already drawn. filesystem_policy lists the paths the "
        "workload may read and write, and landlock says whether failing to enforce those lists fails the start "
        "(hard_requirement) or continues with a finding (best_effort); the kernel holds both, fixed when the sandbox "
        "starts. process names the user and group that run the workload, set at creation, and on Docker an omitted "
        "section means the image's USER. network_policies pairs binaries with endpoints, every binary of a rule reaching "
        "every endpoint of it, and network_middlewares adds processing after admission; the supervisor holds both, and "
        "both can change while the sandbox runs.\n\n"
        "Defaults depend on presence: omitting filesystem_policy grants the working directory, while an empty "
        "filesystem_policy object does not. Cyberbird's values come from cyberbird-policy.yaml and its effective form, "
        "openshell policy get cyberbird --full (version 2).",
        ["filesystem_policy, pinned on the sandbox runtime: kernel rules, fixed at start.",
         "landlock: required or best effort, fixed at start.",
         "process: the workload's identity, set at creation.",
         "network_policies, pinned on the trusted supervisor: live and reloadable.",
         "network_middlewares: processing after admission, also live. The note says which component holds which "
         "section.",
         "In action: Cyberbird's values. The read list ends in /app/fixtures and the write list in /app/runs, Landlock "
         "is a hard requirement, process is not set so the image's user, uid 1000, runs it, python3.12 reaches "
         "host.lima.internal:8080, and no middleware is set."])))

# 7 -------------------------------------------------------------------------------------------------- the policy, line by line
SEG.append(item(
    "7.7", "window", "Cyberbird's policy, line by line", title_marker="[1]",
    window={"label": "cyberbird-policy.yaml: the policy of the recorded run, its three comment lines left out",
            "lang": "yaml", "lines": POLICY_LINES},
    bullets=[B("As a document,", "a policy is parsed, validated, versioned and diffed."),
             B("The read list grants `/app`,", "so every case and the answer key stay readable."),
             B("One network rule", "lets `python3.12` open TCP to the model server's port.")],
    closing="Each grant covers everything beneath its path, the answer key included.",
    refs=[guide("chapter 10")],
    notes=click_notes(
        "The window is the policy of the run we recorded on October 15, 2026, "
        "instructor-materials/hw2/feasibility/cyberbird-policy.yaml, without its three comment lines, which say why the "
        "host is host.lima.internal: OpenShell 0.1.4 on Colima refuses host.docker.internal at policy DNS, and an IP "
        "literal is refused for protocol tcp. A policy is a document so that machines and people can check it: a bounded "
        "parser rejects unknown fields, duplicate keys and oversized input, the gateway validates and versions every "
        "revision, a reviewer diffs it, the supervisor loads it and the prover reads it. The read list grants /app, so "
        "inside the sandbox the sibling case BenchmarkTest00284.py and the answer key expectedresults-0.1.csv were both "
        "readable; only Cyberbird's own workspace code kept them out of the agent's copy, and the HW2 policy lists the "
        "target's code directories instead. protocol: tcp admits the connection with no request inspection, so the rule "
        "has no enforcement line; with --model anthropic:claude-opus-5 the rule would name api.anthropic.com port 443 "
        "with protocol: rest and enforcement: enforce, and the key would come through a provider attachment.\n\n"
        "The guide's quickstart policy (10.2) gives curl api.github.com:443 with protocol: rest, enforcement: enforce "
        "and access: read-only, which admits GET, HEAD and OPTIONS; without its enforcement line the mode is audit, "
        "which logs a violation and lets the request through. The effective policy the supervisor loaded, openshell "
        "policy get cyberbird --full, is version 2: OpenShell added /var/log to read_only and the name model_server to "
        "the rule.",
        ["As a document: parsed, validated, versioned, diffed, loaded and proved.",
         "The read list: /app makes the whole fixture readable, the answer key included. We also point at landlock: "
         "hard_requirement means lists the kernel cannot enforce fail the start, where best_effort would continue with "
         "a finding.",
         "The network rule: one binary, one host and port, TCP only.",
         "The closing box."])))

# 8 -------------------------------------------------------------------------------------------------- request-enforcement
SEG.append(item(
    "7.8", "text", "The supervisor checks connections first.", title_marker="[1]",
    figure={"stages": stages("r6b/request-enforcement", 4), "placement": "below"},
    steps=steps((1, 1), (2, 2), (2, 3), (2, 4), (3, 4)),
    bullets=[B("Connection admission", "checks the host, the port and the calling binary."),
             B("Each request", "then meets its rule, its credential binding and middleware."),
             B("In Cyberbird's case,", "`python3.12` passed admission, and `pypi.org` failed it.")],
    closing="Audit, the default, logs a request-rule violation and lets the request through.",
    refs=[guide("chapters 9 and 10")],
    notes=figure_notes(
        "We follow one request through the supervisor. Connection admission is the L4, transport-layer decision: the "
        "destination's host and port and the identity of the calling executable, whose ancestry counts, so a child of "
        "an authorized binary inherits its grant. A request rule is the L7, application-layer decision on an endpoint "
        "declared protocol: rest: it checks the method and the path in audit mode, which logs and lets through and is "
        "the default, or enforce mode, which blocks, and the read-only preset admits GET, HEAD and OPTIONS. Credential "
        "binding lets the supervisor substitute a provider's key only at the host, port and path the profile names, and "
        "middleware, an ordered chain of processors, runs before the key is supplied and forces a fresh evaluation when "
        "it changes what the policy depends on. Matching rules combine their grants, a deny beats an allow, and a "
        "provider's rules are appended under their own _provider_ keys.\n\n"
        "Cyberbird's sandbox log, October 15, 2026: each of the eight model calls shows \"NET:OPEN [INFO] ALLOWED "
        "/usr/local/bin/python3.12(0) -> host.lima.internal:8080 [policy:model_server engine:opa]\" and then "
        "\"HTTP:POST [INFO] ALLOWED POST http://host.lima.internal:8080/v1/chat/completions\" (the supervisor logs the "
        "method although a tcp endpoint has no request rule). pip, run with the same python3.12, was refused at "
        "admission: \"NET:OPEN [MED] DENIED /usr/local/bin/python3.12(0) -> pypi.org:443 "
        "[reason:transparent_tcp_policy_denied]\", with \"endpoint pypi.org:443 is not allowed by any policy\". curl to "
        "the model server was refused on its binary: \"binary '/usr/bin/curl' not allowed in policy 'model_server'\".",
        ["Connection admission: admit the destination and the executable.",
         "The request rule: parse and validate the application request, then evaluate the application policy. Audit "
         "logs a violation and lets the request through, enforce blocks it.",
         "Credential binding: resolve the endpoint-bound credential or sign the request, guarding the current policy and "
         "credential generations. Only the authorized host, port and path admit the substitution.",
         "Middleware runs before the credential is used, and a policy-relevant change is evaluated again. The request "
         "then goes upstream, for HTTPS over a separate verified TLS connection."])))

# 9 -------------------------------------------------------------------------------------------------- network-request
SEG.append(item(
    "7.9", "text", "Every connection passes the supervisor.", title_marker="[1]",
    figure={"stages": stages("r6b/network-request", 4), "placement": "below"},
    steps=steps((1, 1), (2, 2), (3, 3), (3, 4), (4, 4)),
    bullets=[B("The kernel pauses", "the program's `connect()` and hands it to the broker."),
             B("The supervisor admits it", "by host, port, binary and policy generation."),
             B("The supervisor connects upstream", "after substituting any credential."),
             B("In Cyberbird's case,", "eight model calls took this path with no key to substitute.")],
    closing="Each hop can stop a request, so each hop is a place to diagnose.",
    refs=[guide("chapters 2 and 8"), "[2] " + SENTRY],
    notes=figure_notes(
        "We draw the path of one allowed connection. The program calls connect(), and seccomp's user notification pauses "
        "the call and hands it to the sandbox broker, which checks the destination and the socket's identity. The "
        "supervisor, outside the sandbox, receives the destination with the socket and executable evidence and admits "
        "the TCP connection by host and port, binary and policy generation, the version of the policy in force; DNS has "
        "already given the program a synthetic address that the supervisor maps back to the approved hostname. If a "
        "provider credential applies, the supervisor substitutes or signs it and opens its own connection upstream. "
        "Sentry, NVIDIA's reference design announced with OpenShell on September 28, 2026 as the Open Agent Safety "
        "Platform, is a BlueField-4 processor on the network path outside the host that watches this traffic and can "
        "quarantine the agent; it never sees a local file read, and the course does not run it.\n\n"
        "Cyberbird's eight model calls took this path with OPENAI_API_KEY=none, so nothing was substituted; before each "
        "allowed connection the log shows \"Policy DNS mapped host.lima.internal resolved=192.168.5.2 "
        "synthetic=198.18.0.2 ports=8080\".",
        ["The workload tool calls connect(). The kernel pauses the call and hands it to the sandbox broker, inside the "
         "sandbox.",
         "The supervisor, outside the sandbox, receives the destination with the observed socket and executable evidence "
         "and admits the TCP connection by host and port, binary and policy generation.",
         "If credentials apply, the supervisor substitutes or signs them, and the connection goes upstream.",
         "Sentry, a BlueField-4 processor on the network path outside the host, watches that traffic and can quarantine "
         "the agent. It never sees a local file read. The figure draws the allowed path only."])))

# 10 ------------------------------------------------------------------------------------------------- command-provider
SEG.append(item(
    "7.10", "text", "A provider keeps the key at the gateway.", title_marker="[1]",
    figure={"stages": stages("r6c/command-provider", 5), "placement": "below"},
    steps=steps((1, 1), (1, 2), (2, 3), (3, 4), (3, 5), (4, 5)),
    bullets=[B("A provider instance", "holds one account's credential in the gateway's store."),
             B("Its name", "is what `sandbox create --provider` attaches to one sandbox."),
             B("Its profile", "names the key's variables, endpoints and permitted binaries."),
             B("In Cyberbird's case,", "the profile must name `python3.12`, as in HW2.")],
    closing="The sandbox sees a placeholder, and the supervisor holds the real key.",
    refs=[guide("chapter 11"), REPO],
    notes=figure_notes(
        "We take one command apart. A profile says how a service's credential may be used: its credential names, the "
        "environment variables that carry it, its endpoints and the binaries allowed to use it. A provider instance "
        "holds one account's values, encrypted in the gateway's credential store, and an attachment, made with sandbox "
        "create --provider, gives one sandbox that instance and nothing more. --from-existing reads the values from the "
        "variables the profile names at the moment we run the command, and it fails when they are unset. Inside the "
        "sandbox the variable holds an opaque placeholder, which the supervisor replaces with the real value only on a "
        "request to an endpoint the profile binds, so a base URL such as OPENAI_BASE_URL never carries a credential to "
        "another host, and an expired or unresolved reference fails closed.\n\n"
        "The figure's claude-code profile, in OpenShell's providers/ directory, names only the claude binaries, "
        "/usr/bin/claude and /usr/local/bin/claude, and a new gateway does not load that directory. For a Python SDK the "
        "actual Python executable must be authorized, so Cyberbird with --model anthropic:claude-opus-5 needs an "
        "imported profile that names /usr/local/bin/python3.12: HW2 imports the anthropic profile with its binaries "
        "edited (the brief, \"The sandbox image and the launch commands\"). No Cyberbird run used a provider. In a "
        "staff test sandbox with a provider attached, printenv ANTHROPIC_API_KEY | cut -c1-12 printed openshell:re, the "
        "start of the placeholder.",
        ["The shape: provider create with an instance's name, its profile, and where its values come from.",
         "openshell is the client, talking to the gateway. provider create makes an instance in this workspace.",
         "--name my-claude: the instance's name, which sandbox create --provider my-claude attaches.",
         "--type claude-code: the profile it follows, with its credential names, variables, endpoints and binaries.",
         "--from-existing: the values are read from those variables now, into the gateway's credential store, and the "
         "sandbox sees a placeholder. The note: Cyberbird with an Anthropic model, and the placeholder prefix a test "
         "sandbox printed. We add that Cyberbird's profile must name python3.12, as HW2's edited anthropic profile "
         "does."])))

# 12 ------------------------------------------------------------------------------------------------- policy-review
SEG.append(item(
    "7.12", "text", "A denied request becomes a proposal.", title_marker="[1]",
    figure={"stages": stages("r6b/policy-review", 4), "placement": "below"},
    steps=steps((1, 1), (2, 2), (3, 3), (3, 4), (4, 4)),
    bullets=[B("The denial is recorded,", "and the mapper drafts a narrow rule from it."),
             B("The gateway validates", "the candidate, and the prover reports new findings."),
             B("A reviewer approves it,", "or automatic approval does when nothing is flagged."),
             B("In Cyberbird's case,", "a denied `pip` left a pending rule for `pypi.org:443`.")],
    closing="A proposal adds network rules and leaves file and identity rules alone.",
    refs=[guide("chapter 12")],
    notes=figure_notes(
        "We follow a denial to a policy change. Proposals have two sources: the supervisor's mapper turns observed "
        "denials into draft rules, usually one host, port and binary, and the policy advisor, off by default, lets the "
        "agent itself propose through http://policy.local. The gateway composes the candidate effective policy, "
        "validates it and runs the prover, which models the policy before and after the change and reports new "
        "findings: link-local reach, credentialed reach for a binary that bypasses L7 inspection, credential reach "
        "expansion and capability expansion; a review token binds that evaluation to the state it saw. Review is manual "
        "by default, and automatic approval admits a proposal with no new finding and no destination flag, which can "
        "include a new public host with no credential in scope. A proposal can only add network rules: it cannot "
        "change the filesystem lists, the process identity or Landlock, and it takes effect when the supervisor loads "
        "the revision.\n\n"
        "In Cyberbird's sandbox on October 15, 2026, pip download requests, run with the image's python3.12, was denied "
        "pypi.org:443, and the supervisor logged \"Flushed denial analysis to gateway proposals=1\". openshell rule get "
        "cyberbird then showed the draft \"Rule: allow_pypi_org_443\", \"Binary: /usr/local/bin/python3.12\", "
        "\"Confidence: 65%\", \"Rationale: Allow python3.12 to connect to pypi.org:443 (HTTPS).\", \"Prover: prover: "
        "no new findings\", \"Status: pending\", \"Hits: 2\". We left it pending, and Cyberbird itself never asked for "
        "a package: the probe ran pip in its sandbox.",
        ["A request is denied, and a narrow rule is drafted, by the supervisor's mapper or through the policy advisor.",
         "The gateway validates the candidate effective policy and the prover reports any new findings. A review token "
         "binds this evaluation to the policy and provider state.",
         "The proposal waits for review, or automatic approval accepts it when there is no new finding and no "
         "destination flag. The approved revision is saved.",
         "The supervisor loads the revision and the workload retries the request. Approval and storage alone do not show "
         "that the revision is loaded."])))

# 13 ------------------------------------------------------------------------------------------------- diagnosis
SEG.append(item(
    "7.13", "text", "Diagnose by the boundary that failed.", title_marker="[1]", skip_to="7.14",
    lead="A failure shows an unresolved condition at one boundary.",
    figure={"stages": stages("r6b/diagnosis", 4), "placement": "below"},
    steps=steps((1, 1), (1, 2), (2, 3), (2, 4), (3, 4)),
    bullets=[B("A request can stop", "at any boundary, from its creation to the filesystem."),
             B("Each boundary records", "its own evidence: an error, an event or a result."),
             B("In Cyberbird's case,", "`Connection error.` was a denial the log named.")],
    closing="Diagnosis starts from the evidence of the boundary that failed.",
    refs=[guide("chapter 14")],
    notes=figure_notes(
        "Optional: we skip this build when the section runs long. A boundary here is a place on the request's path "
        "where a component can stop it, from creation to the filesystem. A failed request shows that some condition is "
        "unresolved, and a timeout alone names nothing, because it can arise at provisioning, DNS, admission, TLS, "
        "request policy, credential substitution or upstream. The procedure: identify the exact command and sandbox, "
        "read the phase and the effective policy, find the event at the boundary that failed, change the narrowest "
        "responsible configuration and repeat the same request. HW2 asks for the same discipline in the trace, where a "
        "refused tool result names the place that refused it in refused_by.\n\n"
        "Our real case, October 15, 2026: with the lecture's host.docker.internal in the policy and the base URL, "
        "Cyberbird printed \"MODEL →  thinking over 2 messages…\", then \"END      ERROR\" and "
        "\"openai.APIConnectionError: Connection error.\", which looks like a dead model server. The row \"connection "
        "denied\" sends us to the sandbox log, where openshell logs cyberbird --source sandbox showed \"NET:REFUSE [MED] "
        "DENIED host.docker.internal [reason:policy_dns_trusted_gateway_unavailable]\". The narrowest fix was the host "
        "name host.lima.internal in the policy and the base URL, and the run then completed.",
        ["The boundaries in the order a request meets them: creation and provisioning, connection admission, TLS and "
         "request policy, credential binding, the upstream service. The filesystem stands apart.",
         "What the operator sees at each: creation rejected or stuck in Provisioning, connection denied, a connection "
         "that opens while the HTTP operation fails, a saved policy with unchanged behaviour, a failed file write.",
         "The next evidence at each: the RPC error and the create handler; conditions, driver events and supervisor "
         "logs; the denial event and the effective rules; the HTTP event, policy mode and endpoint binding; the "
         "revision result and a fresh request; the path, process identity and creation policy.",
         "Change the narrowest responsible configuration, then repeat the same request."])))

# 14 ------------------------------------------------------------------------------------------------- openshell-assets
SEG.append(item(
    "7.14", "text", "What OpenShell does not cover.", title_marker="",
    figure={"stages": stages("r6/openshell-assets", 6), "placement": "below"},
    steps=steps((1, 1), (1, 2), (1, 3), (2, 4), (3, 5), (4, 6), (5, 6)),
    bullets=[B("A tool's definition and response", "reach the model as unchecked text[1]."),
             B("The agent holds a placeholder", "and has no identity of its own."),
             B("Governing agents across sandboxes", "lies outside its scope[2]."),
             B("Sentry[3],", "the watcher outside the host, runs on hardware the course lacks."),
             B("In Cyberbird's case,", "the model believes a case file OpenShell never reads.")],
    closing="The host must check what the model reads, since OpenShell cannot.",
    refs=[guide("chapter 1"), "[2] " + TIGERA, "[3] " + SENTRY],
    notes=figure_notes(
        "We end with what lies outside OpenShell. It constrains what a process may touch: the code on disk through the "
        "filesystem policy, the stored key through the provider attachment, outbound connections through the "
        "supervisor, and the kernel boundary through Landlock and seccomp. Text that reaches the model is outside it: a "
        "tool's definition and a tool's response arrive as words the model may believe, and only host-side checks, the "
        "harness or the server, can read them. Tigera's reading of the documentation, a vendor's analysis, puts agent "
        "identity, agent-to-agent governance and cross-sandbox communication outside OpenShell's scope, and the agent "
        "receives a placeholder, which is no identity of its own. Sentry watches from outside the host on BlueField-4 "
        "hardware, which the course does not run.\n\n"
        "Cyberbird read BenchmarkTest00283.py and believed it: a case file that told the model to read the answer key "
        "would pass every OpenShell check, and with this policy the read would succeed, since /app is readable. The "
        "columns name ATLAS techniques by their short names (release 2026.09): definition, implementation and "
        "runtime-response poisoning, credentials from configuration, exfiltration via tool invocation, escape to host.",
        ["Definition text: no OpenShell layer guards it, because the text reaches the model. Definition poisoning.",
         "Implementation: the filesystem policy keeps the tool's code read-only. Implementation poisoning.",
         "Response: no layer guards it either. Runtime-response poisoning.",
         "Stored credential: the provider attachment hands the agent a placeholder. Credentials from configuration.",
         "Outbound connection: the supervisor's network policy, with L7 enforce. Exfiltration via tool invocation.",
         "Kernel boundary: the Landlock and seccomp baseline. Escape to host."])))

# 15 ------------------------------------------------------------------------------------------------- command-hw2
SEG.append(item(
    "7.15", "text", "The commands HW2 uses.", title_marker="",
    figure={"stages": stages("r6c/command-hw2", 5), "placement": "below"},
    steps=steps((0, 1), (1, 2), (2, 3), (3, 4), (4, 5)),
    bullets=[B("Create:", "`--from` names the image and `--policy` the policy file."),
             B("Exec:", "`--no-login-shell --no-tty` keep an MCP stream clean."),
             B("Logs:", "`--source sandbox` shows its denials and policy loads."),
             B("Policy:", "`--full` prints the effective policy, provider rules included.")],
    closing="Flags before the double dash are the operator's. The sandbox list then read: cyberbird  2026-10-16 02:42:20  Ready.",
    notes=figure_notes(
        "We close the section with the commands HW2 uses, in the shape of sandbox create first and then the real "
        "commands of Cyberbird's run. Everything after the double dash is the workload's command, and everything before "
        "it is the operator's. sandbox create and sandbox exec appear in the brief's README section, \"The sandbox image "
        "and the launch commands\", and exec again in \"How the guardrails are tested\": the staff driver starts each "
        "team's MCP server with exec --no-login-shell --no-tty, because a login shell's start-up files can print to "
        "standard output and corrupt the JSON-RPC stream, whose first byte must be {. policy get --full appears in "
        "\"The guardrails\", where A4 asks for a reason for each grant, and the driver reads it to confirm the provider "
        "is the only network grant; logs is ours, the evidence of a denial. The effective policy is the authored document "
        "plus the rules that attached providers add.\n\n"
        "The commands ran on October 15, 2026 with OpenShell 0.1.4 (cyberbird/create.txt, run.txt, logs.txt, "
        "policy-full.txt): create idled the sandbox on sleep infinity and exec started Cyberbird. exec also passed --env "
        "OPENAI_BASE_URL and --env OPENAI_API_KEY, because 0.1.4 hands exec none of the image's ENV values except PATH. "
        "openshell sandbox list then printed \"cyberbird  2026-10-16 02:42:20  Ready\".",
        ["The shape of sandbox create: a name, an image, a policy, an optional provider, and after the double dash the "
         "workload's command.",
         "sandbox create for Cyberbird, and the lines it printed.",
         "sandbox exec: the sandbox, no login shell, no terminal, and Cyberbird's command, with the two lines the run "
         "ended on.",
         "logs: the sandbox's own events. python3.12 is denied pypi.org:443, curl is denied the model server, and "
         "python3.12 is allowed to it: a rule admits a binary together with a destination.",
         "policy get --full: the effective policy. With no provider attached it holds no provider rules."])))

# ---------------------------------------------------------------- checks and output

for it in SEG:
    it["bullets"] = [rich(b) for b in it.get("bullets", [])]
    t = it["title"]
    assert not re.search(r"\b(two|three|four|five|six|seven|eight)\b", t, re.I), f"count word in title {t!r}"
    assert ";" not in t and ";" not in it.get("closing", "") and ";" not in it.get("lead", ""), it["id"]
    for b in it["bullets"]:
        assert b[0][0] == "b", (it["id"], "every bullet opens with its bold lead")
        assert ";" not in "".join(x for _, x in b), (it["id"], b)
    if it.get("steps"):
        nb = len(it["bullets"])
        nf = len(it["figure"]["stages"]) if it.get("figure") else 0
        shown = [(s["b"], s["fig"]) for s in it["steps"]]
        assert shown[-1] == (nb, nf), (it["id"], "the last click shows every bullet and the last stage", shown[-1])
        assert all(a <= c and b <= d for (a, b), (c, d) in zip(shown, shown[1:])), (it["id"], "clicks only add")
        assert sorted({f for _, f in shown}) == list(range(1, nf + 1)), (it["id"], "every stage shown once in order")

json.dump({"segments": [{"segment": "7", "slides": SEG}]}, open(OUT, "w"), indent=1, ensure_ascii=False)
clicks = sum(len(it["steps"]) if it.get("steps") else len(it["bullets"]) + 1 for it in SEG)
print(f"wrote {OUT}: {len(SEG)} items, {clicks} clicks")
