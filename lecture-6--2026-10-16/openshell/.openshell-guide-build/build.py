from pathlib import Path
from html.parser import HTMLParser
from html import escape, unescape
import re
import json
import math
import base64
import xml.etree.ElementTree as ET

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

appendix = '''<section class="chapter" id="ch18" data-title="Repository map and source references">
<header class="chapter-head"><p class="eyebrow">18 / Source atlas</p><h2>Repository map and source references</h2><p class="lead">The repository separates management, enforcement, policy analysis, clients, and platform integration into distinct packages.</p></header>
<h3>Scope of the source study</h3>
<p>This account is based on the local checkout at the cited commit. The source study examined the major subsystems and traced their central implementation paths. Representative tests supplied examples of expected behavior. Deployed-system tests were not executed, and the study was not an exhaustive line-by-line audit.</p>
<p>Each code link identifies a fixed revision. A README states intent; current call paths and tests may establish different behavior or narrower support. Material disagreements are recorded below because they affect the interpretation of the system.</p>
<h3>The 38 Rust crates</h3>
<div class="table-wrap inventory"><table><thead><tr><th>Crate</th><th>Responsibility</th><th>Source entry</th></tr></thead><tbody>'''
for name,(area,description,entry) in sorted(inventory.items()):
    appendix += f'<tr><td><code>{name}</code><br><span class="footnote">{area}</span></td><td>{escape(description)}</td><td>{ref("crates/"+name+"/"+entry,"Read")}</td></tr>\n'
appendix += '''</tbody></table></div>
<h3>Other repository directories</h3>
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
<h3>Differences between documentation and implementation</h3>
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
<h3>Evidence and the scope of conclusions</h3>
<p>A source test specifies an expected result under a fixture. A passing local run establishes a result in that test environment. A production observation concerns a particular deployment and configuration. These forms of evidence support conclusions at different scopes.</p>
<p>A later revision requires renewed examination of interface definitions, startup selection, defaults, validation branches, and failure handling. The conceptual distinctions in this account identify what must be checked; they do not establish that an implementation remained unchanged.</p>
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

# Replace schematic text and the earlier CSS diagram with compiled TikZ figures.
figure_specs=json.loads((HERE/'figures.json').read_text())
figure_root=HERE.parent/'openshell-figures'
for name,spec in figure_specs.items():
    if 'original' not in spec:continue
    def replace_flow(m):
        return f'<figure data-tikz="{name}"></figure>' if unescape(m.group(1))==spec['original'] else m.group(0)
    content=re.sub(r'<pre><code(?:\s[^>]*)?>(.*?)</code></pre>',replace_flow,content,flags=re.S)
content,n=re.subn(r'<figure class="architecture">.*?</figure>', '<figure data-tikz="architecture"></figure>',content,flags=re.S)
assert n==1
start=content.index('id="ch08"')
end=content.index('</header>',start)+len('</header>')
content=content[:end]+'\n<figure data-tikz="network-request"></figure>'+content[end:]
figure_number=0
def figure(m):
    global figure_number
    figure_number+=1
    name=m.group(1);spec=figure_specs[name]
    svg=(figure_root/(name+'.svg')).read_bytes()
    root=ET.fromstring(svg)
    width=round(float(root.attrib['width'].removesuffix('pt'))*1.65)
    height=round(float(root.attrib['height'].removesuffix('pt'))*1.65)
    image_data=base64.b64encode(svg).decode()
    tex=(figure_root/'standalone-style.tex').read_text()+'\n'+r'\begin{document}'+'\n'+(figure_root/(name+'.tikz')).read_text()+r'\end{document}'+'\n'
    source_data=base64.b64encode(tex.encode()).decode()
    alt=spec.get('alt','Sequence: '+'; then '.join(spec.get('steps',[]))+'.')
    caption=escape(spec['caption'])
    transcript=''
    if spec.get('steps'):
        transcript='<details class="diagram-transcript"><summary>Text of the sequence</summary><ol>'+''.join('<li>'+escape(t)+'</li>' for t in spec['steps'])+'</ol></details>'
    return f'<figure class="tikz-figure" id="fig-{name}" data-figure="{name}"><div class="diagram-scroll" tabindex="0" role="region" aria-label="Figure {figure_number}; scroll horizontally on narrow screens"><img src="data:image/svg+xml;base64,{image_data}" alt="{escape(alt,quote=True)}" width="{width}" height="{height}"></div><figcaption><strong>Figure {figure_number}.</strong> {caption}</figcaption><p class="figure-source"><a href="data:text/plain;base64,{source_data}" download="openshell-{name}.tex">TikZ source</a></p>{transcript}</figure>'
content=re.sub(r'<figure data-tikz="([^"<>]+)"></figure>',figure,content)
assert figure_number==8,figure_number

chapter_matches = list(re.finditer(r'<section class="chapter" id="(ch\d+)" data-title="([^"]+)">',content))
assert len(chapter_matches)==18
chapters=[]
for i,m in enumerate(chapter_matches):
    end=chapter_matches[i+1].start() if i+1<len(chapter_matches) else len(content)
    body=content[m.start():end]
    chapters.append({'id':m.group(1),'title':unescape(m.group(2)),'words':words(body),'minutes':max(1,math.ceil(words(body)/220))})
# Generate stable subsection anchors and the numbered academic contents.
nav='<ol>'
for index in range(len(chapter_matches)-1,-1,-1):
    match=chapter_matches[index]
    end=chapter_matches[index+1].start() if index+1<len(chapter_matches) else len(content)
    body=content[match.start():end]
    number=index+1
    title_match=re.search(r'<h2>(.*?)</h2>',body,re.S)
    title=plain(title_match.group(1))
    chapters[index]['title']=title
    body=re.sub(r'<p class="eyebrow">.*?</p>', '', body, flags=re.S)
    body=body.replace('<header class="chapter-head">','<header class="chapter-head"><hr>',1)
    body=body.replace('<h2>',f'<h2><span class="section-number">{number}</span>',1).replace('</h2>','</h2><hr>',1)
    sections=[]
    def subsection(m):
        n=len(sections)+1
        anchor=f'{match.group(1)}-s{n}'
        sections.append((anchor,plain(m.group(1))))
        return f'<h3 id="{anchor}"><span class="section-number">{number}.{n}</span>{m.group(1)}</h3>'
    body=re.sub(r'<h3>(.*?)</h3>',subsection,body,flags=re.S)
    chapters[index]['subsections']=sections
    closing=body.rfind('</section>')
    body=body[:closing]+'<p class="chapter-return"><a href="#contents">Contents</a></p>\n'+body[closing:]
    content=content[:match.start()]+body+content[end:]
for number,ch in enumerate(chapters,1):
    nav+=f'<li><a class="toc-link" href="#{ch["id"]}">{number}&nbsp; {escape(ch["title"])}</a>'
    if ch['subsections']:
        nav+='<ol>'
        for subnumber,(anchor,title) in enumerate(ch['subsections'],1):
            nav+=f'<li><a href="#{anchor}">{number}.{subnumber}&nbsp; {escape(title)}</a></li>'
        nav+='</ol>'
    nav+='</li>'
nav+='</ol>'

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
assert len(audit.resources)==8 and all(r.startswith('data:image/svg+xml;base64,') for r in audit.resources), 'Expected eight embedded TikZ figures'
assert not audit.errors,audit.errors
assert not audit.stack,audit.stack
summary={'file':str(out),'bytes':out.stat().st_size,'words':total,'chapters':chapters,'sources':len(sources),'tikz_figures':figure_number,'exercises':len(re.findall('class="exercise"',content)),'structural_checks':'passed: balanced markup, unique IDs, internal anchors, source paths/lines, no external assets'}
(HERE/'build-report.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
