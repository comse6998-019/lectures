"""Finding 1 and 2 check: every technique label in the r6 sources names an ATLAS 2026.09 entry (exact name, or the lecture's
short name for it), no stale label survives, and every OpenShell sentence the sources quote is in OpenShell's docs at be7af99.
usage: uv run --no-project --python 3.12 --with pyyaml python check-strings.py . ../../../../../lecture-5--2026-10-07/slides/data/atlas-2026.09.yaml /Users/rkrsn/workspace/imputed/openshell"""
import re, subprocess, sys, yaml
SRC, ATLAS, OS = sys.argv[1:4]
T = yaml.safe_load(open(ATLAS))["techniques"]
coll = yaml.safe_load(open(ATLAS))["collection"]
print("ATLAS release", coll["version"], "modified", coll["modified-date"], "-", len(T), "techniques and sub-techniques")
def full(i):
    t = T[i]; p = t.get("subtechnique-of")
    return (T[p]["name"] + ": " if p else "") + t["name"]
# label as printed -> (figure, ATLAS id); exact names must equal the ATLAS name
LABELS = [
    ("bypass-places", "LLM Prompt Injection", "AML.T0051", True), ("bypass-places", "LLM Jailbreak", "AML.T0054", True),
    ("bypass-places", "Modify AI Agent Configuration", "AML.T0081", True), ("bypass-places", "{Escape to Host}", "AML.T0105", True),
    ("openshell-assets", "{Definition poisoning}", "AML.T0110.000", False),
    ("openshell-assets", "{Implementation poisoning}", "AML.T0110.001", False),
    ("openshell-assets", "{Runtime-response poisoning}", "AML.T0110.002", False),
    ("openshell-assets", "{Credentials from configuration}", "AML.T0083", False),
    ("openshell-assets", "{Exfiltration via tool invocation}", "AML.T0086", False),
    ("openshell-assets", "{Escape to Host}", "AML.T0105", True),
    ("entry-points", "{definition\\\\poisoning}", "AML.T0110.000", False),
    ("entry-points", "{runtime-response\\\\poisoning}", "AML.T0110.002", False),
    ("entry-points", "{exfiltration via\\\\tool invocation}", "AML.T0086", False),
    ("entry-points", "{implementation\\\\poisoning}", "AML.T0110.001", False),
    ("entry-points", "{credentials from configuration}", "AML.T0083", False),
    ("entry-points", "{Escape to Host}", "AML.T0105", True),
]
ok = True
body = {f: open(f"{SRC}/{f}.tikz").read().split("\\begin{tikzpicture}", 1)[1] for f in
        ("bypass-places", "openshell-assets", "entry-points", "policy-layers")}
for fig, label, i, exact in LABELS:
    present = label in body[fig]
    name_ok = (label.strip("{}") == T[i]["name"]) if exact else True
    ok &= present and name_ok and i in T
    print(f"{'ok ' if present and name_ok else 'BAD'} {fig:16} {label.strip('{}').replace(chr(92)*2, ' '):34} -> {i} {full(i)}{' (exact)' if exact else ''}")
for fig, stale in (("bypass-places", "no agent technique"), ("openshell-assets", "{Response poisoning}"),
                   ("entry-points", "arguments}"), ("entry-points", "{response\\\\poisoning}"), ("entry-points", "{escape to host}")):
    bad = stale in body[fig]; ok &= not bad
    print(f"{'BAD' if bad else 'ok '} {fig:16} stale label absent: {stale}")
ok &= "no agent-specific technique in release 2026.09" in body["bypass-places"]
head = subprocess.run(["git", "-C", OS, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
print("OpenShell repo at", head[:7]); ok &= head.startswith("be7af99")
QUOTES = [  # (docs file, sentence the figure sources rely on)
    ("docs/security/best-practices.mdx", "The agent receives an opaque placeholder, not the real API key or access token."),
    ("docs/about/overview.mdx", "Resolves opaque credential placeholders only at profile-authorized endpoints."),
    ("docs/about/architecture.mdx", "It checks requests against policy, supplies credentials, resolves DNS, opens approved connections"),
    ("docs/how-it-works/policies/network-rules.mdx", "`audit` allows the request and logs the violation. This is the default."),
    ("docs/how-it-works/policies/network-rules.mdx", "`enforce` blocks the request."),
    ("docs/security/best-practices.mdx", "The sandbox installs a mandatory Landlock baseline before running agent code."),
    ("docs/security/best-practices.mdx", "The blocked syscalls support container escape (`mount`, `pivot_root`, `move_mount`, namespace creation)"),
    ("docs/how-it-works/policies/schema.mdx", "| `filesystem_policy` | object | No | Startup | Paths the workload can read and write. |"),
    ("docs/how-it-works/policies/schema.mdx", "| `landlock` | object | No | Startup | Landlock enforcement behavior. |"),
    ("docs/how-it-works/policies/schema.mdx", "| `process` | object | No | Startup | User and group that the workload runs as. |"),
    ("docs/how-it-works/policies/schema.mdx", "| `network_policies` | map | No | Live | Which binaries can reach which network endpoints. |"),
    ("docs/how-it-works/policies/schema.mdx", "| `network_middlewares` | map | No | Live | Middleware applied to allowed traffic. |"),
    ("docs/how-it-works/policies/overview.mdx", "Filesystem, Landlock, and process settings are fixed once the sandbox starts."),
    ("docs/how-it-works/policies/overview.mdx", "Network rules and middleware can change while it runs"),
]
for f, q in QUOTES:
    text = re.sub(r"\s+", " ", open(f"{OS}/{f}").read())
    hit = q in text; ok &= hit
    print(f"{'ok ' if hit else 'BAD'} {f}: {q[:70]}")
print("ALL OK" if ok else "CHECK FAILED")
