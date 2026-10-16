#!/usr/bin/env python3
"""Build the HW2 deck from a final slide spec: a title slide, then every built item, each a build as in lecture 4.

    cd slides && DECK=snapshots/lecture6.rahul-2026-10-08.pptx SPEC=hw2/slides.hw2.json OUT=../lecture6-hw2.pptx BACK_LINKS=0 \
        uv run --no-project --python 3.12 --with python-pptx,pillow,pyyaml,lxml python hw2/build-hw2.py

A copy of the revision 2 builder (build-lecture6-r2.py). The base deck's 62 slides serve as templates (5 text, 10 code
window, 40 table, 57 and 58 question, 61 route, 62 divider) and are all dropped before the save. Slide 1 is the title
slide on the TITLE layout, as on Rahul's lecture6.pptx; the route item that follows it carries the HW2 title and its rows.
Figure stages are paths under slides/figures/, such as "hw2/two-agents-1.png".

The closing box sits 251381 EMU under its content. Text counts at its estimated height unless the build reads PowerPoint's
own layout of an earlier build of the same spec (lectures/CLAUDE.md: "PowerPoint is the measure"):

    DECK=../lecture6-hw2.pptx OUT=<scratch>/hw2.measures.json uv run --no-project --python 3.12 --with python-pptx,lxml \
        python tools-r3/measure-ppt.py
    MEASURED=../lecture6-hw2.pptx MEASURES=<scratch>/hw2.measures.json DECK=... SPEC=... OUT=... python hw2/build-hw2.py

MEASURED is the measured build (its .map.json says which slide holds each item); with it, plain text counts at the bottom of its
text as PowerPoint laid it out, and every other shape at its declared box.

Markup inside any text field of the spec (bullets, lead, closing, table cells; notes get the plain form):
  slide links    "slide ⟦s:6.2⟧" the last click of item 6.2 (its complete slide); ⟦sf:6.2⟧ its first click;
                 ⟦sk:4.2#7⟧ its click 7; ⟦o:1⟧ the title slide.
  ATLAS names    ⟦t:AML.T0110⟧ the technique's name from the ATLAS data, linked to atlas.mitre.org;
                 ⟦m:AML.M0030⟧ a mitigation, ⟦c:AML.CS0050⟧ a case study; "|text" overrides the shown words.
  other links    ⟦u:https://example.org|words⟧.

Steps: an item's clicks come from its content in this order unless it carries an explicit "steps" list:
bullets (one each), then figure stages, then table rows, then the closing box. Geometry never moves between clicks.
"""
import copy
import json
import os
import re

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Emu

DECK = os.environ["DECK"]
SPEC = os.environ["SPEC"]
OUT = os.environ["OUT"]
HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "figures")

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

EMU_PT = 12700
COL_L, COL_W = 320040, 6016752
BODY_TOP = 658368
CLOSE_TOP, CLOSE_H = 4370832, 429768
GAP = 186667
MIDDLE_FLOOR = CLOSE_TOP - GAP
# The closing box grows with its text, as on lecture 4's slides: one line sits at 4370832 and is 429768 tall;
# two lines (slides 24, 33, 41, 42) are 548640 tall, start at 4224528 and end at 4773168. The body floor follows
# the box, so content stops one GAP above it on every slide.
CLOSE_TWO_TOP, CLOSE_TWO_H, CLOSE_TWO_BOTTOM = 4224528, 548640, 4773168
CLOSE_SIZE_PT, CLOSE_INSET = 11.5, 137160
BOLD_TTF = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

prs = Presentation(DECK)
orig = list(prs.slides)
assert len(orig) == 62, f"expected the 62-slide lecture5.pptx, found {len(orig)}"


def S(n):
    return orig[n - 1]


T_TEXT, T_WINDOW, T_TABLE, T_Q, T_QR = S(5), S(10), S(40), S(57), S(58)
warnings = []
log = []


def warn(msg):
    warnings.append(msg)
    print("WARN", msg)


def note(msg):
    log.append(msg)
    print("  layout:", msg)


# ================================================================ cloning and shapes

def clone(src):
    """A new slide at the end of the deck with src's shapes, background, transition and media."""
    new = prs.slides.add_slide(src.slide_layout)
    tree = new.shapes._spTree
    for el in list(tree)[2:]:
        tree.remove(el)
    rid = {}
    for old_id, rel in src.part.rels.items():
        if rel.reltype in (RT.SLIDE_LAYOUT, RT.NOTES_SLIDE):
            continue
        if rel.is_external:
            rid[old_id] = new.part.relate_to(rel.target_ref, rel.reltype, is_external=True)
        else:
            rid[old_id] = new.part.relate_to(rel.target_part, rel.reltype)
    for el in list(src.shapes._spTree)[2:]:
        tree.append(copy.deepcopy(el))
    for el in tree.iter():
        for k, v in list(el.attrib.items()):
            if k.startswith("{%s}" % R) and v in rid:
                el.set(k, rid[v])
    bg = src._element.find(qn("p:cSld")).find(qn("p:bg"))
    if bg is not None:
        new._element.find(qn("p:cSld")).insert(0, copy.deepcopy(bg))
    for child in src._element:
        if child.tag.endswith("AlternateContent") or child.tag == qn("p:transition"):
            new._element.append(copy.deepcopy(child))
    return new


def shape(slide, name, nth=0):
    return [s for s in slide.shapes if s.name == name][nth]


def has(slide, name):
    return any(s.name == name for s in slide.shapes)


def drop(slide, name):
    for s in [s for s in slide.shapes if s.name == name]:
        s._element.getparent().remove(s._element)


def drop_pictures(slide):
    for s in [s for s in slide.shapes if s.shape_type == 13]:
        s._element.getparent().remove(s._element)


def import_shapes(dst, src, names):
    for s in src.shapes:
        if s.name in names:
            dst.shapes._spTree.append(copy.deepcopy(s._element))


def set_xfrm(sp, x=None, y=None, w=None, h=None):
    if x is not None:
        sp.left = x
    if y is not None:
        sp.top = y
    if w is not None:
        sp.width = w
    if h is not None:
        sp.height = h


# ================================================================ runs and paragraphs

def rpr(size, bold=None, color="000000", scheme=None, mono=False, baseline=None):
    el = etree.Element(qn("a:rPr"))
    el.set("lang", "en-US")
    el.set("sz", str(int(round(size * 100))))
    if bold is not None:
        el.set("b", "1" if bold else "0")
    if baseline:
        el.set("baseline", str(baseline))
    fill = etree.SubElement(el, qn("a:solidFill"))
    if scheme:
        etree.SubElement(fill, qn("a:schemeClr")).set("val", scheme)
    else:
        etree.SubElement(fill, qn("a:srgbClr")).set("val", color)
    if mono:
        etree.SubElement(el, qn("a:latin")).set("typeface", "Aptos Mono")
    return el


def run(text, props):
    r = etree.Element(qn("a:r"))
    r.append(copy.deepcopy(props))
    etree.SubElement(r, qn("a:t")).text = text
    return r


def para(ppr, runs):
    p = etree.Element(qn("a:p"))
    if ppr is not None:
        p.append(copy.deepcopy(ppr))
    for r in runs:
        p.append(r)
    etree.SubElement(p, qn("a:endParaRPr"))
    return p


def segments_to_runs(segs, size):
    out = []
    for kind, text in segs:
        if kind == "b":
            out.extend(runs_for(text, rpr(size, True)))
        elif kind == "r":
            out.extend(runs_for(text, rpr(size, False)))
        elif kind == "m":
            out.append(run(text, rpr(size, None, baseline=30000)))
        elif kind == "c":
            out.append(run(text, rpr(size, False, mono=True)))
        else:
            raise ValueError(kind)
    return out


# ================================================================ markup, ATLAS names and links

ATLAS_YAML = os.environ.get("ATLAS", os.path.join(HERE, "..", "data", "atlas-2026.09.yaml"))
ATLAS_URL = "https://atlas.mitre.org"
_atlas = {}
MARK = re.compile(r"⟦(\w+):([^⟧|]*)(?:\|([^⟧]*))?⟧")
NUMBERS = {"new_first": {}, "new_last": {}, "old_new": {}}  # filled once the deck order is planned
HL_EXT_URI = "{A12FA001-AC4F-418D-AE19-62706E023703}"
HL_EXT_NS = "http://schemas.microsoft.com/office/drawing/2018/hyperlinkcolor"


def atlas():
    if not _atlas:
        import yaml
        _atlas.update(yaml.safe_load(open(ATLAS_YAML)))
    return _atlas


def atlas_record(kind, ident):
    table = {"t": "techniques", "m": "mitigations", "c": "case-studies"}[kind]
    return atlas()[table][ident]


def atlas_url(kind, ident):
    return ATLAS_URL + "/" + {"t": "techniques", "m": "mitigations", "c": "studies"}[kind] + "/" + ident


def resolve_marker(kind, arg, shown):
    """(display text, link) for one marker. link is ('slide', number), ('url', address) or None."""
    if kind in ("s", "sf", "sk", "o"):
        if kind == "o":
            n = NUMBERS["old_new"].get(int(arg))
        elif kind == "sk":  # "4.2#7": the slide at click 7 of item 4.2
            item, k = arg.split("#")
            n = NUMBERS["new_first"].get(item)
            n = n + int(k) - 1 if n else None
        else:
            n = (NUMBERS["new_last"] if kind == "s" else NUMBERS["new_first"]).get(arg)
        if n is None:
            warn(f"slide reference {kind}:{arg} has no slide")
            return shown or arg, None
        return shown or str(n), ("slide", n)
    if kind in ("t", "m", "c"):
        try:
            name = atlas_record(kind, arg)["name"]
        except KeyError:
            warn(f"unknown ATLAS id {arg}")
            return shown or arg, None
        return shown or name, ("url", atlas_url(kind, arg))
    if kind == "u":
        return shown or arg, ("url", arg)
    raise ValueError(f"marker {kind}")


def plain(text):
    """The text without markup, for notes and for measuring."""
    if not isinstance(text, str):
        return text
    return MARK.sub(lambda m: resolve_marker(m.group(1), m.group(2), m.group(3))[0], text)


def pieces(text):
    """Split text into [(string, link or None)] at its markers."""
    out, pos = [], 0
    for m in MARK.finditer(text):
        if m.start() > pos:
            out.append((text[pos:m.start()], None))
        shown, link = resolve_marker(m.group(1), m.group(2), m.group(3))
        out.append((shown, link))
        pos = m.end()
    if pos < len(text):
        out.append((text[pos:], None))
    return out


def link_rpr(props, link):
    """A copy of props that carries a hyperlink placeholder, resolved once the deck is assembled. The link keeps the
    run's own colour (PowerPoint's hyperlinkClr extension) and is underlined."""
    el = copy.deepcopy(props)
    el.set("u", "sng")
    h = etree.SubElement(el, qn("a:hlinkClick"))
    h.set("data-" + link[0], str(link[1]))
    ext_lst = etree.SubElement(h, qn("a:extLst"))
    ext = etree.SubElement(ext_lst, qn("a:ext"))
    ext.set("uri", HL_EXT_URI)
    clr = etree.SubElement(ext, "{%s}hlinkClr" % HL_EXT_NS, nsmap={"ahyp": HL_EXT_NS})
    clr.set("val", "tx")
    return el


def runs_for(text, props):
    """Runs for a string that may hold markers; each marker becomes a linked run in props' colour and size."""
    out = []
    for piece, link in pieces(text):
        out.append(run(piece, link_rpr(props, link) if link else props))
    return out


BACK_LINKS = os.environ.get("BACK_LINKS", "1") == "1"


def add_back_links(slides):
    """A small "back" in the right margin of every slide that a slide reference points to, so the lecturer can return to where
    the click came from (PowerPoint's Last Slide Viewed action). The link sits on every click of the target's build, so it does not
    appear or vanish while the slide builds, and it stays clear of the reference line at the foot."""
    def title_of(sl):
        t = sl.shapes.title
        return t.text_frame.text.strip() if t is not None else None
    targets = sorted({int(h.get("data-slide")) for sl in slides for h in sl._element.iter(qn("a:hlinkClick")) if h.get("data-slide") is not None})
    marked = set()
    for n in targets:
        lo = hi = n - 1
        t = title_of(slides[lo])
        if t:
            while lo > 0 and title_of(slides[lo - 1]) == t:
                lo -= 1
            while hi < len(slides) - 1 and title_of(slides[hi + 1]) == t:
                hi += 1
        for k in range(lo, hi + 1):
            sl = slides[k]
            if k in marked or any(sp.name == "Back link" for sp in sl.shapes):
                continue
            marked.add(k)
            tb = sl.shapes.add_textbox(Emu(6420000), Emu(4500000), Emu(400000), Emu(150000))
            tb.name = "Back link"
            tf = tb.text_frame
            tf.word_wrap = False
            tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
            props = link_rpr(rpr(7, False, "5B6673"), ("back", "lastslideviewed"))
            set_paragraphs(tb, [para(None, [run("\u2039 back", props)])])
    return targets


def resolve_links(slides):
    """Turn every link placeholder into a relationship from its slide: a jump to another slide or an external address."""
    for sl in slides:
        for h in list(sl._element.iter(qn("a:hlinkClick"))):
            if h.get("data-slide") is not None:
                target = slides[int(h.attrib.pop("data-slide")) - 1]
                h.set(qn("r:id"), sl.part.relate_to(target.part, RT.SLIDE))
                h.set("action", "ppaction://hlinksldjump")
            elif h.get("data-url") is not None:
                h.set(qn("r:id"), sl.part.relate_to(h.attrib.pop("data-url"), RT.HYPERLINK, is_external=True))
            elif h.get("data-back") is not None:
                h.attrib.pop("data-back")
                h.set(qn("r:id"), "")
                h.set("action", "ppaction://hlinkshowjump?jump=lastslideviewed")


def set_paragraphs(sp, paras):
    body = sp.text_frame._txBody
    for p in body.findall(qn("a:p")):
        body.remove(p)
    for p in paras:
        body.append(p)


BULLET_PPR = copy.deepcopy(shape(T_TEXT, "Content Placeholder 2").text_frame._txBody.find(qn("a:p")).find(qn("a:pPr")))
LEAD_PPR = etree.Element(qn("a:pPr"))
LEAD_PPR.set("marL", "0")
LEAD_PPR.set("indent", "0")
etree.SubElement(LEAD_PPR, qn("a:buNone"))
etree.SubElement(LEAD_PPR, qn("a:defRPr"))


def numbered_ppr():
    """The bullet paragraph without its glyph, for a list whose items carry their own numbers."""
    ppr = copy.deepcopy(BULLET_PPR)
    ppr.set("marL", "285750")
    ppr.set("indent", "-285750")
    for tag in ("a:buClr", "a:buSzPts", "a:buFont", "a:buChar"):
        for el in ppr.findall(qn(tag)):
            ppr.remove(el)
    ppr.insert(list(ppr).index(ppr.find(qn("a:defRPr"))), etree.Element(qn("a:buNone")))
    return ppr


NUM_PPR = numbered_ppr()


def set_title(slide, text, marker=None):
    body = slide.shapes.title.text_frame._txBody
    for p in body.findall(qn("a:p")):
        body.remove(p)
    p = etree.SubElement(body, qn("a:p"))
    r = etree.SubElement(p, qn("a:r"))
    etree.SubElement(r, qn("a:t")).text = text
    if marker:
        r2 = etree.SubElement(p, qn("a:r"))
        etree.SubElement(r2, qn("a:rPr")).set("baseline", "30000")
        etree.SubElement(r2, qn("a:t")).text = marker
    etree.SubElement(p, qn("a:endParaRPr"))


def set_single_run(sp, text):
    """Replace a box's text, keeping its first run's properties."""
    body = sp.text_frame._txBody
    first = body.find(qn("a:p"))
    ppr = first.find(qn("a:pPr"))
    props = first.find(".//" + qn("a:rPr"))
    set_paragraphs(sp, [para(ppr, [run(text, props)])])


def set_rich_run(sp, text):
    """Replace a box's text, keeping its first run's properties; markers in text become linked runs."""
    body = sp.text_frame._txBody
    first = body.find(qn("a:p"))
    ppr = first.find(qn("a:pPr"))
    props = first.find(".//" + qn("a:rPr"))
    set_paragraphs(sp, [para(ppr, runs_for(text, props))])


def clean_notes(text):
    """Speaker notes keep sources, provenance and answers. Production cues ("Build: ...") are for
    the builder and stay out of the deck."""
    paras = [p for p in (text or "").split("\n\n") if p.strip() and not p.strip().startswith("Build:")]
    return "\n\n".join(paras)


def set_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = clean_notes(plain(text))


# ================================================================ layout estimates (Arial)

def lines_for(chars, width_emu, size_pt, factor=0.52):
    per_line = max(10, int(width_emu / (size_pt * factor * EMU_PT)))
    return max(1, -(-chars // per_line))


def bullets_height(bullets, width_emu, size):
    h = 0
    for segs in bullets:
        chars = sum(len(plain(t)) for _, t in segs)
        h += lines_for(chars, width_emu - 342900, size) * size * 1.2 * EMU_PT + 6 * EMU_PT
    return int(h + 91440)


def lead_height(lead, width_emu, size=14):
    return int(lines_for(len(plain(lead)), width_emu, size, 0.55) * size * 1.25 * EMU_PT + 80000)


# ================================================================ code window

WINDOW_PARTS = ["CodeWindow", "WinBar", "WinDot 0", "WinDot 1", "WinDot 2", "TextBox 8", "TextBox 7"]
OFF = {"WinBar": 265176, "WinDot 0": 82296, "WinDot 1": 82296, "WinDot 2": 82296, "TextBox 8": 41148, "TextBox 7": 329184}
LIGHT_PLUS = {"key": "0451A5", "str": "A31515", "num": "098658", "kw": "0000FF", "com": "008000", "plain": "000000", "raw": "1F1F1F"}


def yaml_tokens(line):
    if line.lstrip().startswith("#"):
        return [(line, "com")]
    out, pos = [], 0
    for m in re.finditer(r'([A-Za-z_][\w/-]*)(:)|("[^"]*")|((?<![\w./])\d+(?![\w./]))|([\[\]{},]|(?<!\S)-(?=\s))', line):
        if m.start() > pos:
            out.append((line[pos:m.start()], "str"))
        if m.group(1):
            out.append((m.group(1), "key"))
            out.append((m.group(2), "plain"))
        elif m.group(3):
            out.append((m.group(3), "str"))
        elif m.group(4):
            out.append((m.group(4), "num"))
        else:
            out.append((m.group(5), "plain"))
        pos = m.end()
    if pos < len(line):
        out.append((line[pos:], "str"))
    return [(t, "plain" if role == "str" and not t.strip() else role) for t, role in out]


def window_height(n_lines, size):
    return int(329184 + n_lines * size * 1.221 * EMU_PT + 90000)


def add_window(slide, top, label, lines, size, lang):
    tokenizer = yaml_tokens if lang == "yaml" else (lambda line: [(line, "raw")])
    import_shapes(slide, T_WINDOW, WINDOW_PARTS)
    height = window_height(len(lines), size)
    set_xfrm(shape(slide, "CodeWindow"), y=top, h=height)
    for name, off in OFF.items():
        set_xfrm(shape(slide, name), y=top + off)
    set_single_run(shape(slide, "TextBox 8"), label)
    paras = []
    for line in lines:
        runs = [run(t, rpr(size, False, LIGHT_PLUS[role], mono=True)) for t, role in tokenizer(line)] or [run(" ", rpr(size, False, mono=True))]
        paras.append(para(None, runs))
    code = shape(slide, "TextBox 7")
    set_paragraphs(code, paras)
    set_xfrm(code, h=int(len(lines) * size * 1.221 * EMU_PT + 20000))
    return top + height


# ================================================================ table

def column_widths(header, rows, size, total=COL_W):
    """Weights from average text length, floored at the longest word of each column so that no
    word breaks mid-cell."""
    cols = len(header)
    mins, weights = [], []
    for c in range(cols):
        cells = [header[c]] + [r[c] for r in rows]
        longest = max(len(w) for cell in cells for w in re.split(r"[\s/;,]+", cell) if w)
        mins.append(int(longest * size * 0.6 * EMU_PT) + 190500)
        avg = sum(len(x) for x in cells) / len(cells)
        weights.append(max(6.0, min(avg, 60.0)) ** 0.75)
    sw = sum(weights)
    widths = [int(total * w / sw) for w in weights]
    for _ in range(12):
        short = [max(0, m - w) for w, m in zip(widths, mins)]
        if not any(short):
            break
        slack = [max(0, w - m) for w, m in zip(widths, mins)]
        ss = sum(slack)
        if ss <= 0:
            break
        need = sum(short)
        widths = [m if w < m else int(w - need * s / ss) for w, m, s in zip(widths, mins, slack)]
    widths[-1] += total - sum(widths)
    return widths


ARIAL_TTF = "/System/Library/Fonts/Supplemental/Arial.ttf"
_fonts = {}


def _arial(size_pt, bold):
    from PIL import ImageFont
    key = (round(size_pt * 20), bold)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(BOLD_TTF if bold else ARIAL_TTF, int(round(size_pt * 20)))
    return _fonts[key]


def wrapped_lines(text, size_pt, bold, avail_pt):
    """Lines the text takes at this size, broken greedily at spaces with real Arial widths. Falls back to the
    average-width estimate on a machine without Arial."""
    try:
        font = _arial(size_pt, bold)
    except OSError:
        return lines_for(len(text), int(avail_pt * EMU_PT), size_pt, 0.55)
    lines, cur = 1, ""
    for word in text.split():
        trial = (cur + " " + word) if cur else word
        if font.getlength(trial) / 20.0 <= avail_pt or not cur:
            cur = trial
        else:
            lines, cur = lines + 1, word
    return lines


HEADER_ROW_H = 300000  # the house header row; body rows are written with height 0 and shrink to their content


def row_heights(header, rows, widths, size, margin=47625, label_bold=True):
    """What PowerPoint will draw for each row: its wrapped text plus the cell margins, and for the header at least the
    nominal header height. Lines are 1.2 x the size, a little more than Arial's 1.15, so the estimate errs tall."""
    out = []
    for ri, r in enumerate([header] + rows):
        lines = max(wrapped_lines(v, size, ri == 0 or (ci == 0 and label_bold), (w - 190500) / EMU_PT)
                    for ci, (v, w) in enumerate(zip(r, widths)))
        content = int(lines * size * 1.2 * EMU_PT + 2 * margin)
        out.append(max(content, HEADER_ROW_H if ri == 0 else 0) + 6350)
    return out


def table_height(header, rows, widths, size, margin=47625, label_bold=True):
    return sum(row_heights(header, rows, widths, size, margin, label_bold))


ROW_HEIGHTS = {}  # item id -> estimated height of each row of its table, header first


def optimise_widths(header, rows, size, margin, label_bold=True):
    """Start from the weighted widths and move width between columns, in steps of 47625 EMU, while the table
    gets shorter. A column never goes below its longest word, so no word breaks mid-cell."""
    cols = len(header)
    mins = []
    for c in range(cols):
        best = 0.0
        for ri, r in enumerate([header] + rows):
            font = _arial(size, ri == 0 or (c == 0 and label_bold))
            for w in r[c].split():
                best = max(best, font.getlength(w) / 20.0)
        mins.append(int(best * EMU_PT) + 190500 + 6350)
    widths = column_widths(header, rows, size)
    widths = [max(w, m) for w, m in zip(widths, mins)]
    widths[-1] += COL_W - sum(widths)
    if sum(mins) > COL_W or min(widths) < 0:
        return column_widths(header, rows, size)
    best = table_height(header, rows, widths, size, margin, label_bold)
    improved = True
    while improved:
        improved = False
        for delta in (190500, 95250, 47625):
            for i in range(cols):
                for j in range(cols):
                    if i == j or widths[i] - delta < mins[i]:
                        continue
                    trial = list(widths)
                    trial[i] -= delta
                    trial[j] += delta
                    h = table_height(header, rows, trial, size, margin, label_bold)
                    if h < best:
                        widths, best, improved = trial, h, True
    return widths


# (size, vertical cell margin) in order of preference: the house margin first, then a tighter one
TABLE_CANDIDATES = [(10.0, 47625), (9.5, 47625), (9.0, 47625), (8.5, 47625),
                    (9.0, 25400), (8.5, 25400), (8.0, 25400), (7.5, 25400)]


def fit_table(header, rows, avail, label_bold=True):
    for size, margin in TABLE_CANDIDATES:
        widths = optimise_widths(header, rows, size, margin, label_bold)
        h = table_height(header, rows, widths, size, margin, label_bold)
        if os.environ.get("FIT_DEBUG"):
            print(f"    fit {header[0][:24]!r} at {size} pt, margin {margin}: {h / EMU_PT:.0f} pt of {avail / EMU_PT:.0f} pt")
        if h <= avail:
            return size, margin, widths, h
    return size, margin, widths, h


LAST_ROWS = []


def add_table(slide, top, header, rows, label_bold, floor):
    size, margin, widths, h = fit_table([plain(c) for c in header], [[plain(c) for c in r] for r in rows], floor - top, label_bold)
    if h > floor - top:
        warn(f"{slide.shapes.title.text_frame.text!r}: table overflows by {(h - (floor - top)) / EMU_PT:.0f} pt at {size} pt")
    if size < 10 or margin != 47625:
        print(f"  table at {size} pt, row margin {margin}: {slide.shapes.title.text_frame.text[:50]}")
    import_shapes(slide, T_TABLE, ["Ledger table"])
    gf = shape(slide, "Ledger table")
    tbl = gf._element.find(".//" + qn("a:tbl"))
    grid = tbl.find(qn("a:tblGrid"))
    cols = grid.findall(qn("a:gridCol"))
    trs = tbl.findall(qn("a:tr"))
    head_tr, body_tr = trs[0], trs[1]
    for tr in trs:
        tbl.remove(tr)
    while len(grid.findall(qn("a:gridCol"))) < len(widths):
        grid.append(copy.deepcopy(cols[-1]))
    for extra in grid.findall(qn("a:gridCol"))[len(widths):]:
        grid.remove(extra)
    for gc, w in zip(grid.findall(qn("a:gridCol")), widths):
        gc.set("w", str(w))

    def make_row(template, values, is_header):
        tr = copy.deepcopy(template)
        tr.set("h", str(HEADER_ROW_H if is_header else 0))
        tcs = tr.findall(qn("a:tc"))
        while len(tcs) < len(values):
            tr.insert(list(tr).index(tcs[-1]) + 1, copy.deepcopy(tcs[-1]))
            tcs = tr.findall(qn("a:tc"))
        for extra in tcs[len(values):]:
            tr.remove(extra)
        for i, (tc, val) in enumerate(zip(tr.findall(qn("a:tc")), values)):
            p = tc.find(".//" + qn("a:p"))
            ppr = p.find(qn("a:pPr"))
            if is_header:
                props = rpr(size, True, scheme="tx1")
            elif i == 0 and label_bold:
                props = rpr(size, True, "28285E")
            else:
                props = rpr(size, False, scheme="tx1")
            body = tc.find(qn("a:txBody"))
            for old in body.findall(qn("a:p")):
                body.remove(old)
            body.append(para(ppr, runs_for(val, props)))
            tcpr = tc.find(qn("a:tcPr"))
            tcpr.set("marT", str(margin))
            tcpr.set("marB", str(margin))
        return tr

    rows_xml = [make_row(head_tr, header, True)] + [make_row(body_tr, r, False) for r in rows]
    for k, tr in enumerate(rows_xml):
        for rid in tr.iter("{http://schemas.microsoft.com/office/drawing/2014/main}rowId"):
            rid.set("val", str(10000 + k))
        tbl.append(tr)
    set_xfrm(gf, x=COL_L, y=top, w=sum(widths), h=h)
    LAST_ROWS[:] = row_heights([plain(c) for c in header], [[plain(c) for c in r] for r in rows], widths, size, margin, label_bold)
    return top + h


# ================================================================ figures and the year chart

def add_figure(slide, png, left, top, width=None, height=None):
    from PIL import Image
    w_px, h_px = Image.open(png).size
    if width is None:
        width = int(height * w_px / h_px)
    if height is None:
        height = int(width * h_px / w_px)
    return slide.shapes.add_picture(png, left, top, width, height)


def native_rect(slide, x, y, w, h, fill, name):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Emu(int(x)), Emu(int(y)), Emu(int(max(w, 1))), Emu(int(max(h, 1))))
    sp.fill.solid()
    sp.fill.fore_color.rgb = RGBColor.from_string(fill)
    sp.line.fill.background()
    sp.shadow.inherit = False
    sp.name = name
    return sp


def native_label(slide, x, y, w, h, text, size, bold, color, name, align="ctr"):
    tb = slide.shapes.add_textbox(Emu(int(x)), Emu(int(y)), Emu(int(w)), Emu(int(h)))
    tb.name = name
    tf = tb.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    ppr = etree.Element(qn("a:pPr"))
    ppr.set("algn", align)
    set_paragraphs(tb, [para(ppr, [run(text, rpr(size, bold, color))])])
    body_pr = tf._txBody.find(qn("a:bodyPr"))
    body_pr.set("anchor", "ctr")
    return tb


# ================================================================ slide builders

def is_numbered(bullets):
    return bool(bullets) and all(b and b[0][0] == "b" and re.fullmatch(r"\d+\.", b[0][1]) for b in bullets)


def body_block(slide, spec, body_width, max_bottom):
    """Fill the content placeholder with the lead and the bullets; return its bottom. Steps the
    bullets down from 12 to 11 pt only when they would cross max_bottom, and says so."""
    ph = shape(slide, "Content Placeholder 2")
    lead, bullets = spec.get("lead"), spec.get("bullets", [])
    size = 12.0
    while True:
        h = (lead_height(lead, body_width) if lead else 0) + (bullets_height(bullets, body_width, size) if bullets else 0)
        if BODY_TOP + h <= max_bottom or size <= 11.0:
            break
        size -= 0.5
    if (lead or bullets) and BODY_TOP + h > max_bottom + 30000:
        warn(f"{spec['title']!r}: text crosses the floor by {(BODY_TOP + h - max_bottom) / EMU_PT:.0f} pt at {size} pt")
    if size < 12:
        print(f"  bullets at {size} pt: {spec['title'][:50]}")
    paras = []
    if lead:
        runs = []
        for piece in re.split(r"(\[\d+\])", lead):
            if not piece:
                continue
            if re.fullmatch(r"\[\d+\]", piece):
                runs.append(run(piece, rpr(14, True, "28285E", baseline=30000)))
            else:
                runs.extend(runs_for(piece, rpr(14, True, "28285E")))
        paras.append(para(LEAD_PPR, runs))
    ppr = NUM_PPR if is_numbered(bullets) else BULLET_PPR
    paras += [para(ppr, segments_to_runs(b, size)) for b in bullets]
    if not paras:
        ph._element.getparent().remove(ph._element)
        return BODY_TOP
    set_paragraphs(ph, paras)
    set_xfrm(ph, x=COL_L, y=BODY_TOP, w=body_width, h=int(h))
    return BODY_TOP + int(h)


def closing_lines(text):
    """Lines the closing text takes in the box at 11.5 pt bold, measured with Arial Bold when this machine has it."""
    text = plain(text)
    avail_pt = (COL_W - 2 * CLOSE_INSET) / EMU_PT
    try:
        from PIL import ImageFont
        font = ImageFont.truetype(BOLD_TTF, int(CLOSE_SIZE_PT * 20))
        width = lambda t: font.getlength(t) / 20.0
    except OSError:
        return lines_for(len(text), COL_W - 2 * CLOSE_INSET, CLOSE_SIZE_PT, 0.55)
    lines, cur = 1, ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if width(trial) <= avail_pt or not cur:
            cur = trial
        else:
            lines, cur = lines + 1, word
    return lines


def closing_box(text):
    """(top, height) of the closing box for this text."""
    n = closing_lines(text)
    if n <= 1:
        return CLOSE_TOP, CLOSE_H
    h = CLOSE_TWO_H + (n - 2) * 182880
    if n > 2:
        warn(f"closing box takes {n} lines at {CLOSE_SIZE_PT} pt: {text[:60]!r}")
    return CLOSE_TWO_BOTTOM - h, h


def closing_floor(text):
    return closing_box(text)[0] - GAP


# The closing box of lecture 5 revision 3 (lectures/CLAUDE.md, Rahul's slide 95): the magenta tint, and its top 251381 EMU
# under the lowest edge of the content above it. It never ends below 4800600, and content is fitted above closing_floor,
# so the box keeps at least GAP (186667) from its content.
UNDER_CONTENT, BOX_FLOOR = 251381, 4800600
NOT_CONTENT = ("Rectangle 4", "Citations", "Skip link", "Back link")


def scheme_clr(val, tint=False):
    c = etree.Element(qn("a:schemeClr"))
    c.set("val", val)
    if tint:
        etree.SubElement(c, qn("a:lumMod")).set("val", "20000")
        etree.SubElement(c, qn("a:lumOff")).set("val", "80000")
    return c


def magenta_box(sp):
    """The base deck's lilac box in the magenta tint: fill accent4 at lumMod 20000 and lumOff 80000, outline and text accent4."""
    sppr = sp._element.find(qn("p:spPr"))
    for fill, tint in ((sppr.find(qn("a:solidFill")), True), (sppr.find(qn("a:ln")).find(qn("a:solidFill")), False)):
        for c in list(fill):
            fill.remove(c)
        fill.append(scheme_clr("accent4", tint))
    for fill in sp._element.find(qn("p:txBody")).iter(qn("a:solidFill")):
        if fill.getparent().tag in (qn("a:rPr"), qn("a:endParaRPr"), qn("a:defRPr")):
            for c in list(fill):
                fill.remove(c)
            fill.append(scheme_clr("accent4"))


for _template in (T_TEXT, T_WINDOW, T_QR):
    magenta_box(shape(_template, "Rectangle 4"))


def plain_text_shape(sp):
    """A shape whose visible bottom is the bottom of its text: a text body with no fill and no outline of its own (the body
    placeholder, a note under a figure). A filled or outlined shape (a code window, a card) shows its whole box."""
    el = sp._element
    if el.tag != qn("p:sp") or not sp.has_text_frame:
        return False
    sppr = el.find(qn("p:spPr"))
    fills = (qn("a:solidFill"), qn("a:gradFill"), qn("a:blipFill"), qn("a:pattFill"))
    return sppr is None or (not any(sppr.find(f) is not None for f in fills) and sppr.find(qn("a:ln")) is None)


def shape_keys(slide):
    """(shape, (name, occurrence of that name on the slide)) in z-order, so a shape is found again in another build."""
    seen = {}
    for sp in slide.shapes:
        k = seen.get(sp.name, 0)
        seen[sp.name] = k + 1
        yield sp, (sp.name, k)


# PowerPoint's own layout of an earlier build (MEASURED, measured by tools-r3/measure-ppt.py into MEASURES): for each item,
# {(name, occurrence): (text, text bottom in EMU)} of every plain text shape on its complete slide. The text is kept so that
# a shape whose words changed since that build falls back to its estimated height.
MEASURED = {}
if os.environ.get("MEASURES"):
    _meas = json.load(open(os.environ["MEASURES"]))
    _first = Presentation(os.environ["MEASURED"])
    for _item, _nums in json.load(open(os.environ["MEASURED"] + ".map.json"))["positions"].items():
        _sl = _first.slides[_nums[-1] - 1]
        _m = _meas.get(str(_nums[-1]), {})
        MEASURED[_item] = {key: (sp.text_frame.text, int(round((_m[str(k)]["ttop"] + _m[str(k)]["theight"]) * EMU_PT)))
                           for k, (sp, key) in enumerate(shape_keys(_sl), start=1)
                           if plain_text_shape(sp) and _m.get(str(k), {}).get("theight")}
    print(f"measures: {len(MEASURED)} items of {os.environ['MEASURED']}")


def content_bottom(slide, measured=None):
    """The lowest edge of the content: every shape but the title, the closing box and the foot of the slide. A shape in
    measured ({key: text bottom}) counts at the bottom of its text as PowerPoint laid it out; everything else at its box."""
    title = slide.shapes.title
    bottoms = [(measured or {}).get(key, sp.top + sp.height) for sp, key in shape_keys(slide)
               if sp.name not in NOT_CONTENT and (title is None or sp._element is not title._element)]
    return max(bottoms, default=BODY_TOP)


def add_skip_link(slide, target_id):
    """A small "skip" at the foot of an optional item's slides, linked to the first slide after the optional run."""
    n = NUMBERS["new_first"].get(target_id)
    if n is None:
        warn(f"skip target {target_id} has no slide")
        return
    tb = slide.shapes.add_textbox(Emu(6420000), Emu(4660000), Emu(400000), Emu(150000))
    tb.name = "Skip link"
    tf = tb.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    set_paragraphs(tb, [para(None, [run("skip \u203a", link_rpr(rpr(7, False, "5B6673"), ("slide", n)))])])


def finish(slide, spec):
    if spec.get("skip_to"):
        add_skip_link(slide, spec["skip_to"])
    if spec.get("closing"):
        box = shape(slide, "Rectangle 4")
        set_rich_run(box, spec["closing"])
        h = closing_box(spec["closing"])[1]
        if MEASURED and spec["id"] not in MEASURED:
            warn(f"{spec['id']}: not in the measured build; its text counts at its estimated height")
        measured = MEASURED.get(spec["id"], {})
        stale = [key for sp, key in shape_keys(slide) if key in measured and measured[key][0] != sp.text_frame.text]
        if stale:
            warn(f"{spec['id']}: text changed since the measured build in {stale}; it counts at its estimated height")
        bottom = content_bottom(slide, {key: m[1] for key, m in measured.items() if key not in stale})
        top = min(bottom + UNDER_CONTENT, BOX_FLOOR - h)
        if top - bottom < GAP:
            warn(f"{spec['title']!r}: closing box {(top - bottom) / EMU_PT:.0f} pt under its content")
        set_xfrm(box, y=top, h=h)
    else:
        drop(slide, "Rectangle 4")
    if spec.get("refs"):
        set_single_run(shape(slide, "Citations"), "   ".join(spec["refs"]))
    else:
        drop(slide, "Citations")
    set_notes(slide, spec.get("notes", ""))


FIG_ROOT = FIG  # stage paths such as "hw2/two-agents-1.png" resolve under slides/figures/
PLACEHOLDERS = []


def stage_path(rel):
    """Path of a figure stage; a stage not drawn yet gets a grey placeholder so that the rest of the deck can be checked."""
    path = os.path.join(FIG_ROOT, rel)
    if os.path.exists(path):
        return path
    from PIL import Image, ImageDraw
    os.makedirs(os.path.join(FIG_ROOT, "_placeholder"), exist_ok=True)
    out = os.path.join(FIG_ROOT, "_placeholder", rel.replace("/", "_"))
    if not os.path.exists(out):
        im = Image.new("RGB", (1581, 600), "#EEEEF6")
        ImageDraw.Draw(im).text((40, 40), "NOT DRAWN YET: " + rel, fill="#C73561")
        im.save(out)
    PLACEHOLDERS.append(rel)
    return out
FIG_GEOM = {}  # id(final slide) -> (left, top, width, height) of its figure, so every stage lands in the same place


def stage_files(spec):
    f = spec.get("figure")
    if not f:
        return []
    return list(f.get("stages") or ([f["file"]] if f.get("file") else []))


def plan_steps(spec):
    """The clicks of an item, each {'b': bullets shown, 'fig': figure stage shown (0 = none), 'rows': table rows shown,
    'close': closing box shown}. An explicit "steps" list in the spec wins; otherwise bullets come first, one per click,
    then figure stages, then table rows, then the closing box. A single figure is on screen from the first click."""
    nb = len(spec.get("bullets", []))
    stages = len(stage_files(spec))
    t = spec.get("table")
    nr = len(t["rows"]) if t else 0
    if spec.get("steps"):
        out = []
        for st in spec["steps"]:
            out.append({"b": st.get("b", nb), "fig": st.get("fig", stages), "rows": st.get("rows", nr), "close": bool(st.get("close", False))})
        return out
    steps = []
    single = stages == 1
    for i in range(nb):
        steps.append({"b": i + 1, "fig": 1 if single else 0, "rows": 0, "close": False})
    if stages > 1 or (stages == 1 and nb == 0):
        for k in range(1, stages + 1):
            steps.append({"b": nb, "fig": k, "rows": 0, "close": False})
    for r in range(1, nr + 1):
        steps.append({"b": nb, "fig": stages, "rows": r, "close": False})
    if spec.get("closing"):
        if steps:
            last = steps[-1]
            steps.append({"b": last["b"], "fig": last["fig"], "rows": last["rows"], "close": True})
        else:
            steps.append({"b": nb, "fig": stages, "rows": nr, "close": True})
    if not steps:
        steps.append({"b": nb, "fig": stages, "rows": nr, "close": False})
    return steps


def n_steps(spec):
    if spec["kind"] == "poll":
        return 1 if spec["poll"]["answer"] < 0 else 2
    if spec["kind"] in ("route", "divider"):
        return 1
    return len(plan_steps(spec))


def whiten(paragraph):
    """Hidden until its click, as in lecture 4: transparent white text and no bullet glyph; the paragraph keeps its place."""
    for el in list(paragraph.iter(qn("a:rPr"))) + list(paragraph.iter(qn("a:endParaRPr"))):
        for f in el.findall(qn("a:solidFill")):
            el.remove(f)
        fill = etree.Element(qn("a:solidFill"))
        clr = etree.SubElement(fill, qn("a:srgbClr"))
        clr.set("val", "FFFFFF")
        etree.SubElement(clr, qn("a:alpha")).set("val", "0")
        el.insert(0, fill)
    ppr = paragraph.find(qn("a:pPr"))
    if ppr is not None:
        bu = ppr.find(qn("a:buChar"))
        if bu is not None:
            ppr.replace(bu, etree.Element(qn("a:buNone")))


def show_step(slide, spec, step, final_geom):
    """Cut a copy of the complete slide back to what this click shows."""
    ph = [s_ for s_ in slide.shapes if s_.name == "Content Placeholder 2"]
    if ph and spec.get("bullets"):
        paras = ph[0].text_frame._txBody.findall(qn("a:p"))
        first = len(paras) - len(spec["bullets"])
        for j, p_ in enumerate(paras[first:], start=1):
            if j > step["b"]:
                whiten(p_)
    stages = stage_files(spec)
    if stages and final_geom:
        drop_pictures(slide)
        if step["fig"] > 0:
            l, t, w, h = final_geom
            add_figure(slide, stage_path(stages[step["fig"] - 1]), l, t, w, h)
    if spec.get("table"):
        gf = [s_ for s_ in slide.shapes if s_.name == "Ledger table"][0]
        tbl = gf._element.find(".//" + qn("a:tbl"))
        trs = tbl.findall(qn("a:tr"))
        if step["rows"] <= 0:
            gf._element.getparent().remove(gf._element)
        else:
            kept = trs[:1 + step["rows"]]
            for tr in trs[1 + step["rows"]:]:
                tbl.remove(tr)
            est = ROW_HEIGHTS.get(spec["id"])
            if est:
                gf.height = sum(est[:1 + step["rows"]])
    if not step["close"]:
        drop(slide, "Rectangle 4")


def build_final(spec):
    """The complete slide of an item, with every shape, and the geometry of its figure."""
    kind = spec["kind"]
    s = clone(T_WINDOW if kind == "window" else T_TEXT)
    drop_pictures(s)
    if kind == "window":
        for name in WINDOW_PARTS:
            drop(s, name)
    set_title(s, spec["title"], spec.get("title_marker") or None)
    floor = closing_floor(spec["closing"]) if spec.get("closing") else 4720000
    geom = None
    stages = stage_files(spec)
    if kind == "text" and not stages:
        body_block(s, spec, COL_W, floor)
    elif kind == "table":
        t = spec["table"]
        ph_, pr_ = [plain(c) for c in t["header"]], [[plain(c) for c in r] for r in t["rows"]]
        reserve = int(table_height(ph_, pr_, optimise_widths(ph_, pr_, 8.0, 25400, t.get("label_bold", True)), 8.0, 25400, t.get("label_bold", True)))
        bottom = body_block(s, spec, COL_W, floor - reserve - 120000)
        top = bottom + 120000 if bottom > BODY_TOP else 777240
        add_table(s, top, t["header"], t["rows"], t.get("label_bold", True), floor)
        ROW_HEIGHTS[spec["id"]] = list(LAST_ROWS)
    elif kind == "window":
        w = spec["window"]
        n_lines = len(w["lines"])
        h_bul = (lead_height(spec["lead"], COL_W) if spec.get("lead") else 0) + bullets_height(spec.get("bullets", []), COL_W, 11.0)
        size = 8.0
        for cand in (8.0, 7.5, 7.0):
            size = cand
            if BODY_TOP + h_bul + 150000 + window_height(n_lines, cand) <= floor:
                break
        bottom = body_block(s, spec, COL_W, floor - window_height(len(w["lines"]), size) - 150000)
        end = add_window(s, bottom + 150000, w["label"], w["lines"], size, w["lang"])
        if size < 8.0:
            print(f"  window at {size} pt: {spec['title'][:50]}")
        if end > floor + 40000:
            warn(f"{spec['title']!r}: window ends {(end - floor) / EMU_PT:.0f} pt below the floor at {size} pt")
    elif kind in ("figure", "text") and stages:
        from PIL import Image
        f = spec["figure"]
        png = stage_path(stages[0])
        sizes = {Image.open(stage_path(x)).size for x in stages}
        assert len(sizes) == 1, f"{spec['id']}: figure stages differ in size {sizes}"
        w_px, h_px = sizes.pop()
        placement = f.get("placement", "below")
        has_text = bool(spec.get("bullets") or spec.get("lead"))
        if placement == "right":
            body_block(s, spec, 3400000, floor)
            set_xfrm(shape(s, "Content Placeholder 2"), h=floor - BODY_TOP)
            h = floor - 760000 - 100000
            w = int(h * w_px / h_px)
            if w > 2600000:
                w, h = 2600000, int(2600000 * h_px / w_px)
            geom = (int(3720040 + (6336792 - 3720040 - w) / 2), 760000, w, h)
        elif placement == "full":
            top = (body_block(s, spec, COL_W, floor - 1200000) + 80000) if has_text else BODY_TOP + 60000
            h = floor - top - 60000
            w = int(h * w_px / h_px)
            if w > COL_W:
                w, h = COL_W, int(COL_W * h_px / w_px)
            geom = (int(COL_L + (COL_W - w) / 2), top + int((floor - top - 60000 - h) / 2), w, h)
        else:
            ar = h_px / w_px
            width = COL_W
            while True:
                fig_h = int(width * ar)
                bullets_bottom = floor - fig_h - 90000
                fits = False
                for size in (12.0, 11.5, 11.0):
                    h_text = (lead_height(spec["lead"], COL_W) if spec.get("lead") else 0) + bullets_height(spec.get("bullets", []), COL_W, size)
                    if BODY_TOP + h_text <= bullets_bottom:
                        fits = True
                        break
                if fits or width <= int(COL_W * 0.62):
                    break
                width -= 80000
            fig_h = int(width * ar)
            if width < 0.9 * COL_W:
                warn(f"{spec['id']}: figure scaled to {100 * width / COL_W:.0f}% of the column to fit; its labels shrink with it")
            bottom = body_block(s, spec, COL_W, floor - fig_h - 90000) if has_text else BODY_TOP
            top = bottom + max(60000, (floor - bottom - fig_h) // 2)   # centred in the free band under the bullets
            geom = (int(COL_L + (COL_W - width) / 2), top, width, fig_h)
        if not has_text:
            drop(s, "Content Placeholder 2")
        add_figure(s, png, *geom)
    else:
        raise ValueError(kind)
    FIG_GEOM[id(s)] = geom
    finish(s, spec)
    return s


def build_item(spec):
    """Every click of an item as a slide, the complete slide last. Notes are the same on every click."""
    final = build_final(spec)
    steps = plan_steps(spec)
    geom = FIG_GEOM.get(id(final))
    out = []
    for st in steps[:-1]:
        c = clone(final)
        show_step(c, spec, st, geom)
        set_notes(c, spec.get("notes", ""))
        out.append(c)
    show_step(final, spec, steps[-1], geom)
    out.append(final)
    return out


def poll_slide(spec):
    p = spec["poll"]
    q = clone(T_Q)
    set_title(q, spec["title"], spec.get("title_marker") or None)
    boxes = ["Rounded Rectangle 3", "Rounded Rectangle 6", "Rounded Rectangle 9", "Rounded Rectangle 12"]
    ovals = ["Oval 4", "Oval 7", "Oval 10", "Oval 13"]
    texts = ["TextBox 5", "TextBox 8", "TextBox 11", "TextBox 14"]
    plain_txt = copy.deepcopy(shape(T_QR, "TextBox 5")._element.find(".//" + qn("a:rPr")))
    set_rich_run(shape(q, "Content Placeholder 2"), p["lead"])
    for i, text in enumerate(p["options"]):
        tb = shape(q, texts[i])
        ppr = tb.text_frame._txBody.find(qn("a:p")).find(qn("a:pPr"))
        set_paragraphs(tb, [para(ppr, [run(text, plain_txt)])])
    set_notes(q, spec.get("notes", ""))
    if p["answer"] < 0:
        return [q]
    rv = clone(T_QR)
    set_title(rv, spec["title"], spec.get("title_marker") or None)
    set_rich_run(shape(rv, "Content Placeholder 2"), p["lead"])
    reveal_box = copy.deepcopy(shape(T_QR, "Rounded Rectangle 12")._element.find(".//" + qn("a:solidFill")))
    plain_box = copy.deepcopy(shape(T_QR, "Rounded Rectangle 3")._element.find(".//" + qn("a:solidFill")))
    reveal_oval = copy.deepcopy(shape(T_QR, "Oval 13")._element.find(".//" + qn("a:solidFill")))
    plain_oval = copy.deepcopy(shape(T_QR, "Oval 4")._element.find(".//" + qn("a:solidFill")))
    reveal_txt = copy.deepcopy(shape(T_QR, "TextBox 14")._element.find(".//" + qn("a:rPr")))
    for i, text in enumerate(p["options"]):
        on = i == p["answer"]
        for name, fill in ((boxes[i], reveal_box if on else plain_box), (ovals[i], reveal_oval if on else plain_oval)):
            sppr = shape(rv, name)._element.find(qn("p:spPr"))
            sppr.replace(sppr.find(qn("a:solidFill")), copy.deepcopy(fill))
        tb = shape(rv, texts[i])
        ppr = tb.text_frame._txBody.find(qn("a:p")).find(qn("a:pPr"))
        set_paragraphs(tb, [para(ppr, [run(text, reveal_txt if on else plain_txt)])])
    set_rich_run(shape(rv, "Rectangle 4"), spec["closing"])
    set_notes(rv, spec.get("notes", ""))
    return [q, rv]


def build(spec):
    if spec["kind"] == "poll":
        return poll_slide(spec)
    if spec["kind"] in ("route", "divider"):
        return [segment_slide(spec)]
    return build_item(spec)


# ================================================================ route and dividers

LECTURE_TITLE = "HW2: two agents over CLDK"
ROUTE_ROWS = ["The CLDK SDK", "An MCP server over CLDK", "HW2: what you build", "HW2: the guardrails", "HW2: contracts, rubric, dates"]
ROW_TOP = {0: 2045919, 1: 2521407, 2: 2996896, 3: 3472383, 4: 3947872}
ROW_H = 338553


def rows_by_y(slide):
    return sorted([sp for sp in slide.shapes if sp.name == "TextBox 12"], key=lambda sp: sp.top)


def set_rows(slide):
    for sp, text in zip(rows_by_y(slide), ROUTE_ROWS):
        set_single_run(sp, text)


def overlay(slide, covered):
    """Dim the route rows listed in covered; each contiguous run of rows gets one overlay picture."""
    pics = [sp for sp in slide.shapes if sp.shape_type == 13]
    keep = pics[0]
    for extra in pics[1:]:
        extra._element.getparent().remove(extra._element)
    groups, cur = [], []
    for r_ in sorted(covered):
        if cur and r_ == cur[-1] + 1:
            cur.append(r_)
        else:
            if cur:
                groups.append(cur)
            cur = [r_]
    if cur:
        groups.append(cur)
    if not groups:
        keep._element.getparent().remove(keep._element)
        return
    for k, rr in enumerate(groups):
        if k == 0:
            pic = keep
        else:
            el = copy.deepcopy(keep._element)
            keep._element.getparent().append(el)
            pic = [sp for sp in slide.shapes if sp._element is el][0]
        top = ROW_TOP[rr[0]] - 173510
        bottom = ROW_TOP[rr[-1]] + ROW_H + 77655
        set_xfrm(pic, x=822960, y=top, w=5733288, h=bottom - top)


def segment_slide(spec):
    """A route slide (every row legible) or a divider (the segment's own row legible) for a new segment of the lecture."""
    if spec["kind"] == "route":
        sl = clone(S(61))
        set_single_run(shape(sl, "TextBox 2"), LECTURE_TITLE)
    else:
        sl = clone(S(62))
        overlay(sl, [r_ for r_ in range(5) if r_ not in spec["legible"]])
        set_single_run(shape(sl, "TextBox 2"), spec["heading"])
        set_xfrm(shape(sl, "TextBox 2"), x=612648, y=278037, w=5645663, h=1310999)
    set_rows(sl)
    set_notes(sl, spec.get("notes", ""))
    return sl


# ================================================================ title slide

# Rahul's title slide (lecture6.pptx slide 1 as saved 2026-10-15, lecture 4's slide 1 with the number changed): two
# placeholders of the TITLE layout with bare bold runs, so the layout supplies the type, the colour and the place.
TITLE_PARTS = [("Title 1", 'type="ctrTitle"', '<a:r><a:rPr lang="en-US" b="1"/><a:t>Designing Production Agentic Systems</a:t></a:r>'),
               ("Subtitle 2", 'type="subTitle" idx="1"',
                '<a:r><a:rPr b="1"/><a:t>Columbia · Fall 2026 · Lecture </a:t></a:r><a:r><a:rPr lang="en-US" b="1"/><a:t>6</a:t></a:r>')]
TITLE_SP = ('<p:sp xmlns:a="{A}" xmlns:p="{P}"><p:nvSpPr><p:cNvPr id="{id}" name="{name}"/><p:cNvSpPr><a:spLocks noGrp="1"/>'
            '</p:cNvSpPr><p:nvPr><p:ph {ph}/></p:nvPr></p:nvSpPr><p:spPr bwMode="auto"/><p:txBody><a:bodyPr/><a:lstStyle/><a:p>'
            '<a:pPr><a:defRPr/></a:pPr>{runs}<a:endParaRPr b="1"/></a:p></p:txBody></p:sp>')
TITLE_NOTES = "HW2 release: the CLDK SDK, the MCP server over it, and the assignment."


def title_slide():
    """Slide 1: the course title and 'Columbia · Fall 2026 · Lecture 6' on the TITLE layout (lectures/CLAUDE.md, Recap)."""
    sl = prs.slides.add_slide(next(lo for lo in prs.slide_layouts if lo.name == "TITLE"))
    tree = sl.shapes._spTree
    for el in list(tree)[2:]:
        tree.remove(el)
    for k, (name, ph, runs) in enumerate(TITLE_PARTS, start=2):
        tree.append(etree.fromstring(TITLE_SP.format(A=A, P=P, id=k, name=name, ph=ph, runs=runs)))
    set_notes(sl, TITLE_NOTES)
    return sl


TITLE = title_slide()

# ================================================================ order, numbers and assembly

spec = json.load(open(SPEC))
segs = {seg["segment"]: seg["slides"] for seg in spec["segments"]}
for items_ in segs.values():
    for it_ in items_:
        it_.setdefault("bullets", [])


def plan_order(segs):
    """Deck order: ('old', 1) for the title slide, which ⟦o:1⟧ names, then ('new', id, clicks) for each built item, segment by
    segment."""
    def items(n):
        return [("new", sl["id"], n_steps(sl)) for sl in segs.get(n, [])]

    order = [("old", 1)]
    for n in sorted(segs):
        order += items(n)
    return order


def positions(order):
    pos, old_new, first, last = 0, {}, {}, {}
    for it in order:
        if it[0] == "old":
            pos += 1
            old_new[it[1]] = pos
        else:
            first[it[1]] = pos + 1
            pos += it[2]
            last[it[1]] = pos
    return old_new, first, last, pos


order = plan_order(segs)
old_new, new_first, new_last, total = positions(order)
NUMBERS.update({"old_new": old_new, "new_first": new_first, "new_last": new_last})

RAW_ID = re.compile(r"\bAML\.(?:T|M|CS|TA)\d{3,4}(?:\.\d{3})?\b|(?<![\w.])[TM]\d{4}(?:\.\d{3})?\b")


def check_prose(sl):
    """Rahul: 'I hate seeing these tags'. Raw identifiers belong in a table's ID column only."""
    texts = [sl.get("title", ""), sl.get("lead", ""), sl.get("closing", "")]
    texts += [t for b in sl.get("bullets", []) for _, t in b]
    if sl.get("table"):
        idc = set(sl["table"].get("id_cols", []))
        texts += [c for ci, c in enumerate(sl["table"]["header"]) if ci not in idc]
        texts += [c for r in sl["table"]["rows"] for ci, c in enumerate(r) if ci not in idc]
    for t in texts:
        for m_ in RAW_ID.finditer(plain(t) or ""):
            warn(f"{sl['id']}: raw identifier {m_.group(0)!r} in prose")


built = {}
for seg_id in sorted(segs):
    for sl in segs[seg_id]:
        check_prose(sl)
        print(f"building {sl['id']} ({n_steps(sl)}): {sl.get('title') or sl.get('heading') or sl['kind']}")
        built[sl["id"]] = build(sl)

final = []
for it in order:
    if it[0] == "old":
        assert it[1] == 1, it
        final.append(TITLE)
    else:
        group = built[it[1]]
        assert len(group) == it[2], (it, len(group))
        final.extend(group)
assert len(final) == total == len(set(id(x) for x in final)), (len(final), total)

for group in built.values():
    for sl in group:
        for k, el in enumerate(sl.shapes._spTree.iter(qn("p:cNvPr")), start=1):
            el.set("id", str(k))

lst = prs.slides._sldIdLst
els = []
for sl in final:
    for el in lst:
        if prs.part.related_part(el.rId) is sl.part:
            els.append(el)
            break
orphan_els = [el for el in lst if el not in els]  # the base deck's 62 slides, used only as templates
for el in list(lst):
    lst.remove(el)
for el in els:
    lst.append(el)
for el in orphan_els:
    prs.part.drop_rel(el.rId)  # unreachable now, so the save leaves out the slide, its notes and any media no kept slide uses

if BACK_LINKS:
    back_targets = add_back_links(final)
    print(f"back links on {len(back_targets)} slides: {back_targets}")
resolve_links(final)
prs.save(OUT)
positions_out = {sid: [final.index(x) + 1 for x in group] for sid, group in built.items()}
json.dump({"positions": positions_out, "old_to_new": old_new, "warnings": warnings, "layout": log}, open(OUT + ".map.json", "w"), indent=1)
if PLACEHOLDERS:
    print("PLACEHOLDERS:", sorted(set(PLACEHOLDERS)))
print(f"saved {OUT}: {len(final)} slides (title and {len(final) - 1} built); {len(warnings)} warnings; map in {OUT}.map.json")
