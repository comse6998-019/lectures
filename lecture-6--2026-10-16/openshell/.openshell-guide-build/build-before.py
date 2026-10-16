from pathlib import Path
from html.parser import HTMLParser
from html import escape, unescape
import re
import json
import math

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent / 'openshell'
SHA = 'be7af99ff2eacba807d82b69adb0c3d4eaa32158'
BASE = f'https://github.com/NVIDIA/OpenShell/blob/{SHA}/'

class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]
    def handle_data(self, value):
        self.parts.append(value)

def plain(value):
    parser=Text(); parser.feed(value); return ' '.join(parser.parts)

def words(value):
    return len(re.findall(r"[\w][\w'/-]*", plain(value)))

def ref(path, label, line=1):
    return f'<a data-source="{escape(path)}:{line}">{escape(label)}</a>'

inventory = {
 'openshell-binary-identity': ('Runtime', 'Resolves live Linux executable and ancestor path-and-digest evidence.', 'README.md'),
 'openshell-bootstrap': ('Clients', 'Stores gateway registration metadata, authentication material, and local selection state.', 'src/lib.rs'),
 'openshell-cli': ('Clients', 'Parses commands, resolves a gateway, constructs API requests, and presents results.', 'src/main.rs'),
 'openshell-conformance': ('Verification', 'Portable CLI scenarios and command execution support shared across environments.', 'src/lib.rs'),
 'openshell-conformance-cli': ('Verification', 'Legacy local entry point for listing and running conformance scenarios.', 'src/main.rs'),
 'openshell-core': ('Shared', 'Common configuration, metadata, errors, generated protocol types, and transport helpers.', 'src/lib.rs'),
 'openshell-driver-db-credstore': ('Credentials', 'Encrypted credential envelopes and database persistence contract.', 'src/lib.rs'),
 'openshell-driver-docker': ('Compute', 'Docker provisioning, companion containers, lifecycle, fencing, and resource admission.', 'README.md'),
 'openshell-driver-kubernetes': ('Compute', 'Kubernetes Sandbox resources, supervisor Pods, fencing, credentials, and workspace integration.', 'README.md'),
 'openshell-driver-kubernetes-secrets': ('Credentials', 'Managed Kubernetes Secret storage with ownership and version checks.', 'src/lib.rs'),
 'openshell-driver-mxc': ('Compute', 'Windows MXC workload creation with an explicit, distinct capability set.', 'README.md'),
 'openshell-driver-podman': ('Compute', 'Native libpod integration, container pairs, user-namespace placement, and lifecycle.', 'README.md'),
 'openshell-driver-vault': ('Credentials', 'Vault-compatible KV storage and authentication.', 'src/lib.rs'),
 'openshell-driver-vm': ('Compute', 'Libkrun-based VM driver, embedded guest runtime, image preparation, and overlays.', 'README.md'),
 'openshell-extension-core': ('Extensions', 'Shared extension identities, bearer-token rotation, and TLS transport primitives.', 'README.md'),
 'openshell-gateway': ('Control plane', 'Gateway executable composition and selected first-party compute-driver registration.', 'src/lib.rs'),
 'openshell-gateway-interceptors': ('Extensions', 'Governance hooks for allowlisted unary gateway writes.', 'src/lib.rs'),
 'openshell-isolation-interface': ('Runtime', 'Typed contract for attaching, confirming, starting, and controlling an isolation boundary.', 'src/lib.rs'),
 'openshell-ocsf': ('Observability', 'Security event types, builders, readable formatting, and JSONL output.', 'src/lib.rs'),
 'openshell-otel': ('Observability', 'Shared trace export, context propagation, and instrumentation support.', 'src/lib.rs'),
 'openshell-otel-test-support': ('Verification', 'Loopback trace collector fixtures for instrumentation tests.', 'src/lib.rs'),
 'openshell-policy': ('Policy', 'Runtime adaptation, validation, composition, overlap checks, and policy merging.', 'src/lib.rs'),
 'openshell-policy-schema': ('Policy', 'Canonical authored YAML/JSON language, bounded parser, and pure semantics.', 'src/lib.rs'),
 'openshell-prover': ('Policy analysis', 'Z3 proposal-risk analysis and independent policy-containment checks.', 'README.md'),
 'openshell-prover-cli': ('Policy analysis', 'Local command-line containment checker and result formatting.', 'README.md'),
 'openshell-providers': ('Credentials', 'Profile-driven discovery, normalization, and provider profile handling.', 'src/lib.rs'),
 'openshell-sandbox': ('Runtime', 'Workload-side process server, kernel controls, network broker, and runtime self-protection.', 'src/main.rs'),
 'openshell-sandbox-backend': ('Runtime', 'Supervisor-side runtime backend and the private Sandbox Protocol.', 'README.md'),
 'openshell-sdk': ('Clients', 'Async Rust gateway client with curated operations and raw RPC access.', 'README.md'),
 'openshell-server': ('Control plane', 'Gateway API, identity, persistence, lifecycle reconciliation, sessions, and service routing.', 'src/lib.rs'),
 'openshell-server-macros': ('Historical helper', 'Procedural authorization helper present in the workspace; unused by the current server authorization path.', 'src/lib.rs'),
 'openshell-supervisor': ('Runtime', 'Policy and credential orchestration, backend startup, updates, and proposal coordination.', 'README.md'),
 'openshell-supervisor-middleware': ('Extensions', 'Middleware registration, remote integration, and bounded request/response chains.', 'src/lib.rs'),
 'openshell-supervisor-middleware-builtins': ('Extensions', 'First-party in-process middleware, including the example regex processor.', 'src/lib.rs'),
 'openshell-supervisor-network': ('Runtime', 'Connection policy, DNS, L7 inspection, credential injection, and upstream networking.', 'src/lib.rs'),
 'openshell-supervisor-process': ('Access plane', 'SSH, retained I/O, supervisor sessions, and access-plane support. Actual child spawning belongs to the sandbox.', 'src/lib.rs'),
 'openshell-tui': ('Clients', 'Terminal dashboard for gateways, sandboxes, providers, policy, proposals, and logs.', 'src/lib.rs'),
 'openshell-vfio': ('Compute support', 'PCI device discovery, IOMMU checks, passthrough binding, and recovery.', 'src/lib.rs'),
}
actual = {p.parent.name for p in (REPO/'crates').glob('*/Cargo.toml')}
assert actual == set(inventory), f'Crate inventory mismatch: {actual ^ set(inventory)}'

appendix = '''<section class="chapter" id="ch18" data-title="Use the complete repository map">
<header class="chapter-head"><p class="eyebrow">18 / Source atlas</p><h2>Use the complete repository map</h2><p class="lead">Every crate has an owner and a reason to exist. Use this atlas to find the right level before editing or diagnosing.</p></header>
<h3>Read the evidence at the correct scope</h3>
<p>This document is based on the local checkout at the pinned commit. The study covered all major subsystem surfaces and traced central implementation paths. Representative tests supplied examples of expected behavior. The work did not execute deployed-system tests or constitute an exhaustive line-by-line audit.</p>
<p>The code links below pin the revision, so later changes on the default branch do not silently change the evidence. A README states intent; current call paths and tests can reveal limits or newer behavior. The document calls out material disagreements rather than merging incompatible descriptions.</p>
<h3>Find each of the 38 Rust crates</h3>
<div class="table-wrap inventory"><table><thead><tr><th>Crate</th><th>Responsibility</th><th>Source entry</th></tr></thead><tbody>'''
for name,(area,description,entry) in sorted(inventory.items()):
    appendix += f'<tr><td><code>{name}</code><br><span class="footnote">{area}</span></td><td>{escape(description)}</td><td>{ref("crates/"+name+"/"+entry,"Read")}</td></tr>\n'
appendix += '''</tbody></table></div>
<h3>Place the non-crate directories</h3>
<div class="table-wrap"><table><thead><tr><th>Directory</th><th>Role</th></tr></thead><tbody>
<tr><td><code>proto/</code></td><td>Public and internal service contracts, messages, authorization annotations, and generation inputs.</td></tr>
<tr><td><code>python/</code>, <code>sdk/go/</code>, <code>sdk/typescript/</code></td><td>Language clients, generated bindings, examples, and client tests.</td></tr>
<tr><td><code>providers/</code>, <code>examples/</code></td><td>Reviewable provider profiles and worked integrations. Some examples retain older assumptions.</td></tr>
<tr><td><code>deploy/</code>, <code>snap/</code>, packaging files</td><td>Containers, Helm, manifests, service units, package assets, and installed gateway configuration.</td></tr>
<tr><td><code>tasks/</code>, <code>scripts/</code>, <code>nix/</code>, <code>.github/</code></td><td>Build and release tasks, tool wrappers, reproducible environments, CI, security checks, and distribution.</td></tr>
<tr><td><code>tests/</code>, <code>e2e/</code></td><td>Installed-system qualification, test machines, runtime matrices, and end-to-end scenarios.</td></tr>
<tr><td><code>docs/</code>, <code>fern/</code>, <code>rfc/</code>, <code>telemetry/</code></td><td>Published explanations, documentation-site configuration, design history, and aggregate usage reports.</td></tr>
<tr><td><code>skills/</code>, <code>.agents/</code>, <code>.claude/</code></td><td>Public operating workflows and internal contributor tooling. These files are not the runtime security boundary.</td></tr>
</tbody></table></div>
<h3>Recognize material documentation drift</h3>
<div class="table-wrap"><table><thead><tr><th>Description to question</th><th>What this revision implements</th></tr></thead><tbody>
<tr><td>Sandbox Protocol described as mutual certificate TLS</td><td>Server-authenticated TLS plus per-request sandbox JWT. Both-direction authentication is not the same as mTLS.</td></tr>
<tr><td>All networking described as an old veth/CONNECT path</td><td>The standard startup selects a remote sandbox backend with kernel-mediated TCP/DNS and supplied executable evidence.</td></tr>
<tr><td>Provider README says credentials are injected into child processes</td><td>Current provider-managed paths give workload processes opaque references; the supervisor resolves real values for admitted requests.</td></tr>
<tr><td>Built-in provider catalogue or managed inference routing assumed</td><td>Profiles are imported explicitly. Applications use native inference endpoints.</td></tr>
<tr><td>RFC workspace model described as future work</td><td>Workspace-scoped resources and memberships are already present.</td></tr>
<tr><td>SQL enum read as enforced SQL support</td><td>Enforced SQL configuration is rejected; a SQL relay branch alone does not supply an SQL request parser.</td></tr>
<tr><td>Policy-advisor example grants private IPs automatically</td><td>The mechanistic mapper does not add <code>allowed_ips</code>. Private-address trust needs separate deliberate configuration.</td></tr>
</tbody></table></div>
<p class="sources">Compare <a data-source="crates/openshell-sandbox-backend/src/runtime.rs:269">TLS client setup</a>, <a data-source="crates/openshell-supervisor/src/backend_setup.rs:80">backend selection</a>, <a data-source="docs/how-it-works/inference.mdx:228">native inference migration</a>, <a data-source="crates/openshell-supervisor-network/src/l7/mod.rs:1483">SQL validation</a>, and <a data-source="crates/openshell-supervisor/src/mechanistic_mapper.rs:52">private-address proposal behavior</a>.</p>
<h3>Keep claims tied to their evidence</h3>
<p>A source test establishes what a fixture expects. A passing local run establishes what happened in that test environment. A production observation establishes behavior under a particular deployment and configuration. Keep those claims separate when you review a change or explain an incident.</p>
<p>For a future revision, repeat the narrow source trace first. Check interface definitions, startup selection, default values, validation branches, and failure handling. Reuse the chapter structure as a set of questions rather than assuming every implementation detail stayed fixed.</p>
<h3>Source ledger</h3><p>The following references appear throughout the course. Each URL names the exact commit and source line.</p>
{{LEDGER}}
</section>'''

fragments = [(HERE/name).read_text() for name in ['foundations.html','gateway.html','runtime.html','policy.html','practice.html']]
content = '\n'.join(fragments)+'\n'+appendix
sources = []
for match in re.finditer(r'<a\s+data-source="([^"]+)"[^>]*>(.*?)</a>',content,re.S):
    source, label = match.groups()
    if not any(s[0]==source for s in sources): sources.append((source,plain(label)))

ledger='<ol class="source-ledger">'
for source,label in sources:
    path,number=source.rsplit(':',1);number=int(number)
    file=REPO/path
    assert file.is_file(), f'Missing source {path}'
    count=len(file.read_text(errors='replace').splitlines())
    assert 1<=number<=count, f'Bad line {source}, file has {count}'
    url=BASE+path+f'#L{number}'
    ledger+=f'<li><a href="{escape(url)}" target="_blank" rel="noopener noreferrer">{escape(label)}</a><br><code>{escape(source)}</code></li>\n'
ledger+='</ol>'
content=content.replace('{{LEDGER}}',ledger)

def resolve(match):
    source=unescape(match.group(1));path,number=source.rsplit(':',1)
    return f'data-source="{escape(source)}" href="{BASE+escape(path)}#L{number}" target="_blank" rel="noopener noreferrer" title="{escape(source)} · commit be7af99ff"'
content=re.sub(r'data-source="([^"]+)"',resolve,content)

chapter_matches = list(re.finditer(r'<section class="chapter" id="(ch\d+)" data-title="([^"]+)">',content))
assert len(chapter_matches)==18
chapters=[]
for i,m in enumerate(chapter_matches):
    end=chapter_matches[i+1].start() if i+1<len(chapter_matches) else len(content)
    body=content[m.start():end]
    chapters.append({'id':m.group(1),'title':unescape(m.group(2)),'words':words(body),'minutes':max(1,math.ceil(words(body)/220))})
for ch in reversed(chapters):
    start=content.index(f'id="{ch["id"]}"')
    header_end=content.index('</header>',start)
    meter=f'<p class="chapter-meter">CHAPTER {ch["id"][2:]} · ABOUT {ch["minutes"]} MIN</p>'
    content=content[:header_end]+meter+content[header_end:]

groups=[('Start here',0,3),('Control and infrastructure',3,6),('Runtime enforcement',6,9),('Policy and credentials',9,12),('Practice and diagnosis',12,16),('Reference',16,18)]
nav=''
for group,start,end in groups:
    nav+=f'<div class="toc-group"><h3>{group}</h3><ol>'
    for ch in chapters[start:end]:
        nav+=f'<li><a class="toc-link" href="#{ch["id"]}"><span class="num">{ch["id"][2:]}</span><span>{escape(ch["title"])}</span></a></li>'
    nav+='</ol></div>'

total=words(content)
html=(HERE/'template.html').read_text().replace('{{NAV}}',nav).replace('{{CONTENT}}',content).replace('{{WORD_COUNT}}',f'{total:,}').replace('{{READ_TIME}}',str(math.ceil(total/220)))
assert not re.search(r'\{\{[A-Z_]+\}\}',html), 'Unresolved template marker'
out=HERE.parent/'openshell-guide.html'
out.write_text(html)

class Audit(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.hrefs=[];self.resources=[];self.stack=[];self.errors=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if 'href' in a:self.hrefs.append(a['href'])
        if 'src' in a:self.resources.append(a['src'])
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:self.stack.append(tag)
    def handle_endtag(self,tag):
        if not self.stack or self.stack[-1]!=tag:self.errors.append((tag,self.stack[-5:]))
        else:self.stack.pop()

audit=Audit();audit.feed(html)
dupes=sorted({x for x in audit.ids if audit.ids.count(x)>1})
assert not dupes,dupes
bad=[h for h in audit.hrefs if h.startswith('#') and h[1:] not in audit.ids]
assert not bad,bad
assert not audit.resources,audit.resources
assert not audit.errors,audit.errors
assert not audit.stack,audit.stack
summary={'file':str(out),'bytes':out.stat().st_size,'words':total,'chapters':chapters,'sources':len(sources),'exercises':len(re.findall('class="exercise"',content)),'structural_checks':'passed: balanced markup, unique IDs, internal anchors, source paths/lines, no external assets'}
(HERE/'build-report.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
