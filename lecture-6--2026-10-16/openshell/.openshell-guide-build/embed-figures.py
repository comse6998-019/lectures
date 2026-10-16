from pathlib import Path
p=Path('.openshell-guide-build/build.py')
s=p.read_text().replace('import math','import math\nimport base64\nimport xml.etree.ElementTree as ET')
marker='chapter_matches = list('
pos=s.index(marker)
insert='''# Replace schematic text and the earlier CSS diagram with compiled TikZ figures.
figure_specs=json.loads((HERE/'figures.json').read_text())
figure_root=HERE.parent/'openshell-figures'
for name,spec in figure_specs.items():
    if 'original' not in spec:continue
    def replace_flow(m):
        return f'<figure data-tikz="{name}"></figure>' if unescape(m.group(1))==spec['original'] else m.group(0)
    content=re.sub(r'<pre><code(?:\\s[^>]*)?>(.*?)</code></pre>',replace_flow,content,flags=re.S)
content,n=re.subn(r'<figure class="architecture">.*?</figure>', '<figure data-tikz="architecture"></figure>',content,flags=re.S)
assert n==1
start=content.index('id="ch08"')
end=content.index('</header>',start)+len('</header>')
content=content[:end]+'\\n<figure data-tikz="network-request"></figure>'+content[end:]
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
    tex=(figure_root/'standalone-style.tex').read_text()+'\\n'+r'\\begin{document}'+'\\n'+(figure_root/(name+'.tikz')).read_text()+r'\\end{document}'+'\\n'
    source_data=base64.b64encode(tex.encode()).decode()
    alt=spec.get('alt','Sequence: '+'; then '.join(spec.get('steps',[]))+'.')
    caption=escape(spec['caption'])
    transcript=''
    if spec.get('steps'):
        transcript='<details class="diagram-transcript"><summary>Text of the sequence</summary><ol>'+''.join('<li>'+escape(t)+'</li>' for t in spec['steps'])+'</ol></details>'
    return f'<figure class="tikz-figure" id="fig-{name}" data-figure="{name}"><div class="diagram-scroll" tabindex="0" role="region" aria-label="Figure {figure_number}; scroll horizontally on narrow screens"><img src="data:image/svg+xml;base64,{image_data}" alt="{escape(alt,quote=True)}" width="{width}" height="{height}"></div><figcaption><strong>Figure {figure_number}.</strong> {caption}</figcaption><p class="figure-source"><a href="data:text/plain;base64,{source_data}" download="openshell-{name}.tex">TikZ source</a></p>{transcript}</figure>'
content=re.sub(r'<figure data-tikz="([^"<>]+)"></figure>',figure,content)
assert figure_number==8,figure_number

'''
s=s[:pos]+insert+s[pos:]
s=s.replace('assert not audit.resources,audit.resources',"assert len(audit.resources)==8 and all(r.startswith('data:image/svg+xml;base64,') for r in audit.resources), 'Expected eight embedded TikZ figures'")
s=s.replace("'sources':len(sources)","'sources':len(sources),'tikz_figures':figure_number")
p.write_text(s)
