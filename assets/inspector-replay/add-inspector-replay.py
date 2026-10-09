"""Insert the six-click replay of the MCP Inspector exploit (CVE-2025-49596) in front of slide 101 ("The Inspector itself had a critical flaw.").
usage: SRC=in.pptx OUT=out.pptx FIG=<folder with inspector-replay-1..6.png> uv run --no-project --with python-pptx,lxml python3 add-inspector-replay.py
Slides after the insertion move by 6: link texts follow their targets, and plain 'slide N' in notes and text shifts when N >= 101."""
import copy, io, os, re
from pptx import Presentation
from pptx.util import Emu
from pptx.oxml.ns import qn

SRC, OUT, FIG = os.environ["SRC"], os.environ["OUT"], os.environ["FIG"]
AT, N = 101, 6
TITLE = "Replay of the Inspector exploit"
BOX = ("One missing check on the proxy turned a visit to a public web page into code running on the developer's machine, "
       "and the fix added three.")
NOTES = ("The replay follows GitHub advisory GHSA-7f8r-222p-6f5g (CVE-2025-49596, published June 13, 2025) and Oligo Security's write-up of June 27, 2025. "
         "The figure, stage by stage. 1. The developer runs mcp dev: the Inspector's web client talks to a backend proxy on port 6277, which starts the MCP server over stdio; "
         "before version 0.14.1 the proxy listened on 0.0.0.0 and asked for no authentication. 2. The developer visits a public web page that the adversary controls; its script runs in the browser. "
         "3. The script sends a cross-site request to 0.0.0.0:6277/sse that names a command; the browser reaches the developer's own machine through the 0.0.0.0 address (the quirk Oligo calls the 0.0.0.0-day). "
         "DNS rebinding was an alternative route. 4. The proxy checks neither a token nor the origin, so it starts the named command as a stdio process. "
         "5. The command runs with the developer's rights: remote code execution from one page visit. 6. Version 0.14.1 added a session token and origin checks and bound the proxy to localhost, "
         "so the same request stops at the proxy. The weakness class is CWE-306, Missing Authentication for Critical Function. The command on the slide is not shown: any command the page names would run. "
         "The next slides give the identifiers and the numbers.")

prs = Presentation(SRC)
slides = list(prs.slides)
tmpl = slides[AT - 1 + 4]            # slide 105: title, body, banner, citations
assert tmpl.shapes[0].text_frame.text.startswith("The Inspector itself"), tmpl.shapes[0].text_frame.text
layout = tmpl.slide_layout
cit = next(sh for sh in tmpl.shapes if sh.name == "Citations")
box_src = next(sh for sh in tmpl.shapes if sh.name == "Rectangle 4")

new = []
for k in range(1, N + 1):
    s = prs.slides.add_slide(layout)
    tree = s.shapes._spTree
    for el in list(tree):
        if el.tag not in (qn("p:nvGrpSpPr"), qn("p:grpSpPr")):
            tree.remove(el)
    for sh in tmpl.shapes:
        if sh.name == "Title 1" or sh.name == "Citations":
            tree.append(copy.deepcopy(sh._element))
    t = next(sh for sh in s.shapes if sh.name == "Title 1")
    runs = t.text_frame.paragraphs[0].runs
    runs[0].text = TITLE
    for r in runs[1:]:
        r._r.getparent().remove(r._r)
    png = open(os.path.join(FIG, f"inspector-replay-{k}.png"), "rb").read()
    w = 6152752
    from PIL import Image
    iw, ih = Image.open(io.BytesIO(png)).size
    h = int(w * ih / iw)
    pic = s.shapes.add_picture(io.BytesIO(png), Emu(250147), Emu(760000), Emu(w), Emu(h))
    pic.name = "Replay figure"
    bottom = 760000 + h
    if k == N:
        b = copy.deepcopy(box_src._element)
        tree.append(b)
        sp = next(sh for sh in s.shapes if sh.name == "Rectangle 4")
        sp.text_frame.paragraphs[0].runs[0].text = BOX
        sp.top, sp.height = Emu(bottom + 251381), Emu(548640)
    s.notes_slide.notes_text_frame.text = NOTES
    new.append(s)

lst = prs.slides._sldIdLst
els = list(lst)
mine = els[-N:]
for e in mine:
    lst.remove(e)
for i, e in enumerate(mine):
    lst.insert(AT - 1 + i, e)

# renumber
allslides = list(prs.slides)
index_of = {s.part: i + 1 for i, s in enumerate(allslides)}
linked = 0
for s in allslides:
    for h in s._element.iter(qn("a:hlinkClick")):
        if h.get("action", "").startswith("ppaction://hlinksldjump"):
            tgt = s.part.rels[h.get(qn("r:id"))].target_part
            r = h.getparent().getparent()
            t = r.find(qn("a:t"))
            if t is not None and t.text and t.text.strip().isdigit():
                t.text = str(index_of[tgt]); linked += 1
NUM = re.compile(r"(?i)\b(slides?)(\s+)(\d+)((?:\s*(?:,|and|to|–|-|&)\s*\d+)*)")
def bump(m):
    word, sp, n, rest = m.groups()
    f = lambda x: str(int(x) + N) if int(x) >= AT else x
    return f"{word}{sp}{f(n)}" + re.sub(r"\d+", lambda k: f(k.group(0)), rest)
shifted = 0
for s in allslides:
    if s in new:
        continue
    if s.has_notes_slide:
        for t in s.notes_slide.notes_text_frame._txBody.iter(qn("a:t")):
            if t.text and NUM.search(t.text):
                nt = NUM.sub(bump, t.text)
                if nt != t.text:
                    t.text = nt; shifted += 1
prs.save(OUT)
print(f"inserted {N} slides at {AT}; {linked} link texts rewritten, {shifted} note runs shifted; total {len(prs.slides)}")
