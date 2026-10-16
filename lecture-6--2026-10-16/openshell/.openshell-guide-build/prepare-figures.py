from pathlib import Path
from html import unescape
import re,json,textwrap
root=Path('.openshell-guide-build');out=Path('openshell-figures')
flow_specs=[
('creation','gateway.html','User requests a sandbox','Sandbox creation and readiness. The durable resource precedes platform provisioning; usable access requires the subsequent runtime and configuration steps.'),
('interceptors','gateway.html','authenticate','Gateway interception of an allowlisted write operation. Modification and validation precede the ordinary handler; post-commit observation follows it.'),
('runtime-startup','runtime.html','driver provisions resources','Runtime startup. Confirmation of enforcement and identity precedes the launch of agent code.'),
('request-enforcement','runtime.html','admit destination and executable','Request processing in the supervisor. Policy-relevant transformations require renewed evaluation before endpoint-bound credentials are supplied.'),
('credential-substitution','policy.html','workload environment:','Managed static credential substitution. The workload supplies an opaque reference; the supervisor supplies the real value only for a request that passes the applicable checks.'),
('policy-review','policy.html','denied request','From denial to an applied policy revision. Approval and storage do not by themselves establish that the supervisor has loaded the revision.')]

def tex_escape(text):
 return ''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}'}.get(c,c) for c in text)
manifest={}
for name,filename,start,caption in flow_specs:
 s=(root/filename).read_text()
 matches=[m for m in re.finditer(r'<pre><code(?:\s[^>]*)?>(.*?)</code></pre>',s,re.S) if unescape(m.group(1)).startswith(start)]
 assert len(matches)==1,(name,len(matches))
 raw=unescape(matches[0].group(1));steps=[]
 for line in raw.splitlines():
  label=line.strip().lstrip('→↓').strip()
  if label:steps.append(label)
 lines=[r'\begin{tikzpicture}[node distance=7mm, every node/.append style={text=ibmfg}]']
 for i,label in enumerate(steps):
  text=r'\\'.join(tex_escape(v) for v in textwrap.wrap(label,width=43,break_long_words=False,break_on_hyphens=False))
  kind='mnode' if any(v in label.lower() for v in ['validat','admi','policy','credential','enforcement','confirm']) else 'rnode'
  lines.append(r'  \node['+kind+', text width=62mm'+(f', below=of n{i-1}' if i else '')+f'] (n{i}) '+'{'+text+'};')
  if i:lines.append(f'  \\draw[flow] (n{i-1}) -- (n{i});')
 lines.append(r'\end{tikzpicture}')
 (out/(name+'.tikz')).write_text('\n'.join(lines)+'\n')
 manifest[name]={'fragment':filename,'original':raw,'steps':steps,'caption':caption}
manifest['architecture']={'caption':'Component placement on the standard Linux path. The gateway manages resources. The supervisor holds policy and credentials outside the workload boundary and mediates traffic to external services. Compute drivers provision the workload and supervisor placement.','alt':'The client calls the gateway, which uses a compute driver. The workload contains agent tools and the sandbox runtime. The runtime communicates with the trusted supervisor, which communicates with approved external services. A supervisor session connects back to the gateway.'}
manifest['network-request']={'caption':'An illustrative mediated TCP and HTTP exchange. Connection admission and request-level inspection are separate decisions. Managed credentials, where applicable, remain on the supervisor side. Arrows group protocol events; precise scheduling depends on the transport path. DNS and transport recovery are omitted.','alt':'A workload tool attempts a connection. The kernel pauses it and the sandbox broker reports socket and executable evidence to the supervisor. After connection admission, the supervisor inspects applicable HTTP requests and credential bindings, sends permitted traffic upstream, and relays the response.'}
(root/'figures.json').write_text(json.dumps(manifest,indent=2))
