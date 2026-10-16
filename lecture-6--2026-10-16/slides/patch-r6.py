#!/usr/bin/env python3
"""Lecture 6 (2026-10-16): a patch applied to Rahul's saved cut of the lecture 5 deck. The deck is never rebuilt.

His save (143 slides) is the title slide, the "Lecture 5 Recap" leader, the enforcement divider and slides 276 to 416 of the 416-slide
lecture5.pptx. The patch
  1. copies four recap builds of lecture5.pptx (20 slides) after the leader,
  2. replaces the five table builds with the stage figures of figures/r6 (a build whose PNGs are missing keeps its table); "Limits of
     OpenShell enforcement", whose figure the build before it completes, keeps two clicks: the figure, then the figure and its box,
  3. rewrites the closing build ("Next Friday is the midterm.") and adds the midterm-scope build after the poll, one bullet per click and
     its closing box on the last (six clicks),
  4. renumbers: every slide-jump link text follows its target, and every slide number in the notes, written against lecture5.pptx,
     names the slide's place in this deck or the lecture 5 slide that this deck no longer carries.
From his 143 slides it makes 166: 143 + 20 recap + 6 midterm - 3 Limits clicks.

usage:  SRC=<his save> L5=<416-slide lecture5.pptx> MAP=<json from tools-r6/verify-r6.py> OUT=<patched deck> \
        [MEASURES=<json from tools-r3/measure-ppt.py of a previous OUT>] \
        uv run --no-project --python 3.12 --with python-pptx,lxml python patch-r6.py
Without MEASURES the figures sit at the tables' tops (the first pass); with PowerPoint's measurements of the first pass's output, a second
run places each figure under its lead-in and each closing box under its content. Both runs start from SRC.

        MODE=fix1 SRC=<a deck that already carries the first patch> OUT=<patched deck> uv run ... python patch-r6.py
The first patch (164 slides, installed as lecture6.pptx on 2026-10-15 at 22:07) showed the midterm scope on one click and kept five Limits
clicks of which three changed nothing. MODE=fix1 applies the same two corrections to any later save of that deck, and to the output of
patch-r6.py's companion patch-r6b.py (pass two), since it finds every build by its title: it turns the one
midterm slide into the six-click build, keeps the first and last Limits clicks, rewrites the two notes that cite the early ~/.ssh poll,
and moves every slide-jump link text and every slide number in the notes to the new positions. Its output equals a full run from SRC.
"""
import copy
import io
import json
import os
import re
import struct

from lxml import etree
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn

SRC = os.environ["SRC"]
MODE = os.environ.get("MODE", "full")      # full: Rahul's 143-slide save; fix1: a deck that already carries the first patch
assert MODE in ("full", "fix1"), MODE
L5 = os.environ["L5"] if MODE == "full" else None                                # the 416-slide lecture5.pptx
MAP = json.load(open(os.environ["MAP"])) if MODE == "full" else {}               # Rahul's slide -> old number, from verify-r6.py
OUT = os.environ["OUT"]
MEASURES = json.load(open(os.environ["MEASURES"])) if os.environ.get("MEASURES") else None
FIG6 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures", "r6")
LOG = []


def log(msg):
    LOG.append(msg)
    print(msg)


# ----------------------------------------------------------------------------------------------- constants (EMU)
GAP = 251381          # closing box top minus content bottom on Rahul's lecture 5 slide 95
MIN_GAP = 186667      # lectures/CLAUDE.md: never closer than this
EMU_PT = 12700
FLOOR = 4800600       # no closing box ends below this
TEXT_GAP = 38100      # least space between the bottom of a text box and the figure below it (3 pt)
COL_LEFT, COL_WIDTH = 320040, 6016752
COL_AXIS = COL_LEFT + COL_WIDTH // 2      # 3328416: a narrowed figure is centred here (lectures/CLAUDE.md)
MIN_SCALE = 0.9       # a figure shrinks to 90 percent at the least before the box gap does

NAVY, LILAC = "28285E", "CACAE5"


# ----------------------------------------------------------------------------------------------- helpers (from patch-r3.py)
def title_of(slide):
    for sh in slide.shapes:
        if sh.is_placeholder and sh.placeholder_format.type is not None and "TITLE" in str(sh.placeholder_format.type):
            return sh.text_frame.text.strip()
    for sh in slide.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip():
            return sh.text_frame.text.strip()
    return ""


def drop(shape):
    shape._element.getparent().remove(shape._element)


def named(slide, name):
    return [sh for sh in slide.shapes if sh.name == name]


def set_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def set_first_run(shape, text):
    paras = shape.text_frame.paragraphs
    runs = paras[0].runs
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def copy_slide(dst, src_slide):
    """Copy a slide of another deck into dst, appended at the end: shapes, images, hyperlinks, transition and show attributes."""
    layout = next(l for l in dst.slide_layouts if l.name == src_slide.slide_layout.name)
    new = dst.slides.add_slide(layout)
    tree = new.shapes._spTree
    for el in list(tree):
        if el.tag not in (qn("p:nvGrpSpPr"), qn("p:grpSpPr")):
            tree.remove(el)
    for el in src_slide.shapes._spTree:
        if el.tag not in (qn("p:nvGrpSpPr"), qn("p:grpSpPr")):
            tree.append(copy.deepcopy(el))
    for blip in tree.iter(qn("a:blip")):
        rid = blip.get(qn("r:embed"))
        if rid:
            part = src_slide.part.related_part(rid)
            _, new_rid = new.part.get_or_add_image_part(io.BytesIO(part.blob))
            blip.set(qn("r:embed"), new_rid)
    # every other relationship a copied shape refers to is an external hyperlink (an ATLAS name, a source); anything else would be a
    # dangling id in the new slide, so it stops the patch
    for el in tree.iter():
        rid = el.get(qn("r:id"))
        if rid:
            rel = src_slide.part.rels[rid]
            assert rel.is_external and rel.reltype == RT.HYPERLINK, ("unexpected relationship in a copied slide", rel.reltype)
            el.set(qn("r:id"), new.part.relate_to(rel.target_ref, RT.HYPERLINK, is_external=True))
    for attr in ("showMasterPhAnim",):
        if src_slide._element.get(attr) is not None:
            new._element.set(attr, src_slide._element.get(attr))
    for alt in src_slide._element.findall("{http://schemas.openxmlformats.org/markup-compatibility/2006}AlternateContent"):
        new._element.append(copy.deepcopy(alt))
    # a copied slide must not carry a link to a slide of the other deck
    for h in tree.iter(qn("a:hlinkClick")):
        assert not h.get("action", "").startswith("ppaction://hlinksldjump"), "slide jump in a copied slide"
    return new


def move_to(prs, slides_in_order, start):
    """Move the given slides (already in the deck) so that they occupy positions start, start+1, ... (0-based)."""
    lst = prs.slides._sldIdLst
    ids = {s.slide_id: el for s, el in zip(prs.slides, list(lst))}
    els = [ids[s.slide_id] for s in slides_in_order]
    for el in els:
        lst.remove(el)
    for k, el in enumerate(els):
        lst.insert(start + k, el)


def fill_key(sh):
    sp = sh._element.find(qn("p:spPr"))
    if sp is None:
        return None
    sf = sp.find(qn("a:solidFill"))
    if sf is None or not len(sf):
        return None
    c = sf[0]
    if c.tag == qn("a:srgbClr"):
        return c.get("val").upper()
    if c.tag == qn("a:schemeClr") and c.get("val") == "accent4" and any(m.tag == qn("a:lumMod") for m in c):
        return "MAGENTA"
    return None


def is_banner(sh):
    el = sh._element
    if el.tag != qn("p:sp") or sh.is_placeholder or not sh.has_text_frame or not sh.text_frame.text.strip():
        return False
    pg = el.find(qn("p:spPr")).find(qn("a:prstGeom"))
    if pg is None or pg.get("prst") != "rect":
        return False
    return (5900000 <= sh.width <= 6100000 and 400000 <= sh.height <= 1000000
            and fill_key(sh) in (NAVY, LILAC, "MAGENTA"))


def scheme(val, lum=False):
    c = etree.Element(qn("a:schemeClr"))
    c.set("val", val)
    if lum:
        etree.SubElement(c, qn("a:lumMod")).set("val", "20000")
        etree.SubElement(c, qn("a:lumOff")).set("val", "80000")
    return c


def retheme(sh):
    """Lilac closing box -> Rahul's slide 95: fill accent4 tint, outline and text accent4."""
    sp = sh._element
    spPr = sp.find(qn("p:spPr"))
    fill = spPr.find(qn("a:solidFill"))
    for c in list(fill):
        fill.remove(c)
    fill.append(scheme("accent4", lum=True))
    ln = spPr.find(qn("a:ln"))
    lnfill = ln.find(qn("a:solidFill"))
    for c in list(lnfill):
        lnfill.remove(c)
    lnfill.append(scheme("accent4"))
    body = sp.find(qn("p:txBody"))
    for sf in body.iter(qn("a:solidFill")):
        parent = sf.getparent()
        if parent.tag in (qn("a:rPr"), qn("a:endParaRPr"), qn("a:defRPr")):
            for c in list(sf):
                sf.remove(c)
            sf.append(scheme("accent4"))


def box_height(lines):
    return 429768 if lines <= 1 else 548640 + (lines - 2) * 182880


# ----------------------------------------------------------------------------------------------- helpers (new)
def build(prs, title):
    """Indices (0-based) of the one run of consecutive slides with this title."""
    idx = [i for i, s in enumerate(prs.slides) if title_of(s) == title]
    assert idx and idx == list(range(idx[0], idx[-1] + 1)), (title, idx)
    return idx


def body_of(slide):
    return next((sh for sh in slide.shapes if sh.name == "Content Placeholder 2"), None)


def title_shape(slide):
    return next(sh for sh in slide.shapes if sh.is_placeholder and sh.placeholder_format.idx == 0)


def banners(slide):
    return sorted([sh for sh in slide.shapes if is_banner(sh)], key=lambda sh: sh.top)


def next_id(slide):
    return max(int(x) for x in slide._element.xpath("//p:cNvPr/@id")) + 1


def measured(prs, slide, shape):
    """PowerPoint's record for a shape of this deck (slide and shape order equal those of the measured previous run), or None."""
    if MEASURES is None:
        return None
    sidx = list(prs.slides).index(slide) + 1
    k = list(slide.shapes).index(shape) + 1
    return MEASURES.get(str(sidx), {}).get(str(k))


def text_bottom(prs, slide, shape):
    m = measured(prs, slide, shape)
    if m and m.get("theight") is not None:
        return int(round((m["ttop"] + m["theight"]) * EMU_PT))
    return None


def drop_if_unused(slide, rid):
    """Remove a relationship of the slide once no element of the slide refers to it."""
    if rid and not slide._element.xpath(f"//*[@r:id='{rid}']"):
        slide.part.drop_rel(rid)


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    assert head[:8] == b"\x89PNG\r\n\x1a\n", path
    return struct.unpack(">II", head[16:24])


def clean_title(t):
    return re.sub(r"\[\d+\]", "", t).strip()


def copy_notes(dst, src):
    """dst's notes become a copy of src's, runs and formatting included (a build carries identical notes on every click)."""
    a, b = src.notes_slide.notes_placeholder._element, dst.notes_slide.notes_placeholder._element
    body = copy.deepcopy(a.find(qn("p:txBody")))
    assert not body.xpath(".//@r:id"), "a relationship in the notes"
    b.replace(b.find(qn("p:txBody")), body)


def look(slide):
    """What a click shows: every shape's kind, name, place, size and text, and a picture's image."""
    out = []
    for sh in slide.shapes:
        el = sh._element
        img = None
        if el.tag == qn("p:pic"):
            img = slide.part.related_part(el.find(".//" + qn("a:blip")).get(qn("r:embed"))).sha1
        out.append((etree.QName(el).localname, sh.name, sh.left, sh.top, sh.width, sh.height,
                    sh.text_frame.text if sh.has_text_frame else None, img))
    return out


def retarget_links(prs, moved):
    """Every slide-jump link whose target part is a key of moved points at the value instead."""
    n = 0
    for s in prs.slides:
        for h in s._element.iter(qn("a:hlinkClick")):
            rid = h.get(qn("r:id"))
            if rid and h.get("action", "").startswith("ppaction://hlinksldjump") and s.part.rels[rid].target_part in moved:
                h.set(qn("r:id"), s.part.relate_to(moved[s.part.rels[rid].target_part], RT.SLIDE))
                drop_if_unused(s, rid)
                n += 1
    return n


def drop_slides(prs, slides):
    """Remove slides from the deck: the sldId and the presentation's relationship; python-pptx then saves only the parts still reachable.
    lectures/CLAUDE.md: no kept slide may link to a dropped one (retarget_links first)."""
    gone = {s.part for s in slides}
    for s in prs.slides:
        if s.part in gone:
            continue
        for h in s._element.iter(qn("a:hlinkClick")):
            rid = h.get(qn("r:id"))
            assert not (rid and h.get("action", "").startswith("ppaction://hlinksldjump") and s.part.rels[rid].target_part in gone), \
                ("a kept slide links to a dropped one", title_of(s))
    lst = prs.slides._sldIdLst
    for sid in [s.slide_id for s in slides]:
        el = next(e for e in lst if int(e.get("id")) == sid)
        rid = el.get(qn("r:id"))
        lst.remove(el)
        prs.part.drop_rel(rid)
        assert rid not in prs.part.rels, rid


# ----------------------------------------------------------------------------------------------- 1. the recap
RECAP5 = [  # (title in the 416-slide deck, first, last, notes)
    ("MCP client–server connection model", 36, 38,
     "Recap of lecture 5. A host holds one client per server; the client speaks the protocol, the server offers tools, resources and prompts. "
     "The host converts the tools for its model. HW2 makes your agent this host."),
    ("Only argument and result shapes are enforced.", 56, 62,
     "Recap of lecture 5. Of a tool contract's five parts, the server validates arguments and results; the description and the effect annotations "
     "enforce nothing; execution constraints live in the host's and the server's code. The enforcement point today asks whose code."),
    ("Incident analysis with OWASP and ATLAS", 136, 140,
     "Recap of lecture 5. OWASP classifies an incident by risk category; ATLAS maps its steps to techniques and tactics. The techniques name "
     "what to restrict and never which process enforces it."),
    ("Failed controls sat in the agent's runtime.", 263, 267,
     "Recap of lecture 5. In both OpenClaw case studies the control that failed ran in the agent's own runtime, where the agent's code could "
     "rewrite it. That is the question the enforcement point answers today."),
]
LEADER_NOTES_OLD = "Four slides of lecture 4 recap"
LEADER_NOTES = ("Four builds of lecture 5 recap what this lecture builds on: the MCP client–server connection model, the parts of a tool "
                "contract that the server enforces, incident analysis with OWASP and ATLAS, and the OpenClaw finding that the failed controls "
                "sat in the agent's runtime.")


def strip_slide_links(slide):
    """A copied slide carries no slide-jump links and no presenter navigation."""
    for sh in list(slide.shapes):
        if sh.name in ("Back link", "Skip link"):
            sh._element.getparent().remove(sh._element)
    for h in list(slide._element.iter(qn("a:hlinkClick"))):
        if h.get("action", "").startswith("ppaction://hlinksldjump"):
            h.getparent().remove(h)


def recap(prs, src):
    """The four builds after Rahul's leader. Returns {old number in the 416-slide deck: the copy}."""
    leader = next(i for i, s in enumerate(prs.slides) if title_of(s) == "Lecture 5 Recap")
    lead = prs.slides[leader]
    assert lead.notes_slide.notes_text_frame.text.startswith(LEADER_NOTES_OLD), lead.notes_slide.notes_text_frame.text[:80]
    set_notes(lead, LEADER_NOTES)
    new, copies = [], {}
    for title, first, last, notes in RECAP5:
        for n in range(first, last + 1):
            sl = src.slides[n - 1]
            assert title_of(sl).replace("[1]", "").strip() == title, (n, title_of(sl))
            strip_slide_links(sl)
            c = copy_slide(prs, sl)
            for b in banners(c):
                if fill_key(b) == LILAC:
                    retheme(b)
            set_notes(c, notes)
            new.append(c)
            copies[n] = c
    move_to(prs, new, leader + 1)
    log(f"recap: {len(new)} slides after the leader at {leader + 1}; the leader's notes name the four builds")
    for title, first, last, _ in RECAP5:
        clear_box([copies[n] for n in range(first, last + 1)])
    return copies


def clear_box(slides):
    """A build whose closing box sits closer than MIN_GAP under its lone picture (lecture 5's slide 38 sits at 9.6 pt): the picture shrinks
    about its top centre on every click until the gap is MIN_GAP, as lectures/CLAUDE.md orders, never below MIN_SCALE."""
    bs = banners(slides[-1])
    pics = [sh for sh in slides[-1].shapes if sh._element.tag == qn("p:pic")]
    if len(bs) != 1 or len(pics) != 1:
        return
    pic = pics[0]
    short = pic.top + pic.height + MIN_GAP - bs[0].top
    if short <= 0:
        return
    w0, h0, t0, l0 = pic.width, pic.height, pic.top, pic.left
    s_ = max(MIN_SCALE, (h0 - short) / h0)
    w1, h1 = int(round(w0 * s_)), int(round(h0 * s_))
    for s in slides:
        for sh in s.shapes:
            if sh._element.tag == qn("p:pic") and (sh.left, sh.top, sh.width, sh.height) == (l0, t0, w0, h0):
                sh.left, sh.width, sh.height = l0 + (w0 - w1) // 2, w1, h1
    log(f"recap: {title_of(slides[-1])!r}: picture at {s_:.1%} on {len(slides)} clicks, closing box "
        f"{(bs[0].top - t0 - h1) / EMU_PT:.1f} pt under it")


# ----------------------------------------------------------------------------------------------- 2. links that PowerPoint re-pointed
def repair_links(prs, src, slide_for_old):
    """When Rahul cut a slide that a link pointed to, PowerPoint kept the link's part name, so a link whose old target was slide 46 or 38
    of the 416-slide deck now opens slide 46 or 38 of his cut. Each slide-jump link of his slides is compared with the same link on the
    slide's original: it is pointed at the slide that now carries the original target (one of his slides or a recap copy), or, when this
    deck no longer carries the target, it stops being a link. Returns the slide ids that the links now point to."""
    index_416 = {s.part: i + 1 for i, s in enumerate(src.slides)}
    repointed, unlinked, targets = [], [], set()
    for i, old in MAP.items():
        s = SLIDE_OF[int(i)]
        mine = list(s._element.iter(qn("a:hlinkClick")))
        theirs = list(src.slides[old - 1]._element.iter(qn("a:hlinkClick")))
        assert len(mine) == len(theirs), (i, old, len(mine), len(theirs))
        for h, o in zip(mine, theirs):
            if not o.get("action", "").startswith("ppaction://hlinksldjump"):
                continue
            want = slide_for_old.get(index_416[src.slides[old - 1].part.rels[o.get(qn("r:id"))].target_part])
            rid = h.get(qn("r:id"))
            have = s.part.rels[rid].target_part if rid and h.get("action", "").startswith("ppaction://hlinksldjump") else None
            if want is None:
                h.getparent().remove(h)
                drop_if_unused(s, rid)
                unlinked.append(int(i))
            elif have is not want.part:
                h.set("action", "ppaction://hlinksldjump")
                h.set(qn("r:id"), s.part.relate_to(want.part, RT.SLIDE))
                drop_if_unused(s, rid)
                repointed.append(int(i))
            if want is not None:
                targets.add(want.slide_id)
    log(f"links: {len(repointed)} re-pointed at the slide that carries their original target (his slides {sorted(set(repointed))}); "
        f"{len(unlinked)} whose target this deck no longer carries are plain text now (his slides {sorted(set(unlinked))})")
    return targets


def back_link_on_targets(copies, targets, template):
    """A recap copy that a link now points to carries the small '‹ back' link, as every link target does."""
    added = []
    for old, c in copies.items():
        if c.slide_id in targets and not named(c, "Back link"):
            el = copy.deepcopy(template)
            el.find(".//" + qn("p:cNvPr")).set("id", str(next_id(c)))
            c.shapes._spTree.append(el)
            added.append(old)
    log(f"back links: added to the recap copies of lecture 5 slides {added}")


# ----------------------------------------------------------------------------------------------- 3. tables become figures
FIGURES = {"Each place has its own bypass.": ("bypass-places", 4), "OpenShell controls by protected asset": ("openshell-assets", 6),
           "Limits of OpenShell enforcement": ("openshell-assets", 6), "Attacks enter through text or the process.": ("entry-points", 6),
           "OpenShell controls at creation and run time": ("policy-layers", 4)}
# "Limits of OpenShell enforcement" continues the figure that the build before it completed (spec 2.2: one figure for both builds), so it
# shows the last stage. Its five table clicks revealed one row each; with the figure the middle three would change nothing, and
# lectures/CLAUDE.md asks for one new element per click, so the build keeps its first click and its last (the closing box): a build pair.
WHOLE = {"Limits of OpenShell enforcement"}


def collapse_to_pair(prs, title):
    """A build whose clicks between the first and the last show what the first shows keeps those two. Returns {dropped slide's part: the
    last slide} (a dropped slide has no id any more); links to a dropped click are pointed at the last one, which shows what a reference
    to the build names."""
    slides = [prs.slides[i] for i in build(prs, title)]
    if len(slides) <= 2:
        return {}
    first, last, gone = slides[0], slides[-1], slides[1:-1]
    for s in gone:
        assert look(s) == look(first), ("a middle click differs from the first", title, list(prs.slides).index(s) + 1)
        assert s.notes_slide.notes_text_frame.text == last.notes_slide.notes_text_frame.text, (title, "notes differ")
    relinked = retarget_links(prs, {s.part: last.part for s in gone})
    at = list(prs.slides).index(first) + 1
    drop_slides(prs, gone)
    log(f"pair: {title!r}: {len(slides)} clicks -> 2 at {at}-{at + 1} (the figure, then the figure and its box); "
        f"{len(gone)} identical middle clicks dropped, {relinked} links to them now open the last click")
    return {s.part: last for s in gone}


LEAD_INS = {  # build title -> (lead-in as saved, lead-in for the figure); the old text named the table, its rows or a cut slide
    "Each place has its own bypass.": (
        "This table gives, for each place, what a bypass requires and the ATLAS technique that names it. Rows three and four lie outside the agent's process.",
        "This figure gives, for each place, what a bypass requires and the ATLAS technique that names it. Places three and four lie outside the agent's process."),
    "Attacks enter through text or the process.": (
        "This table gives, for each of the six techniques, the place where it enters the tool call and the step of slide 46 it touches.",
        "This figure gives, for each of the six techniques, the place where it enters the tool call."),
    "OpenShell controls by protected asset": (
        "Each row pairs an ATLAS technique with the asset it acts on and the OpenShell layer that restricts it.",
        "Each column pairs an asset with the OpenShell layer that restricts it and the ATLAS technique that acts on it."),
}


def tables_to_figures(prs):
    """Returns {dropped slide's part: the slide that replaces it} for the builds collapse_to_pair shortened."""
    replaced = {}
    for title, (name, n) in FIGURES.items():
        stages = [os.path.join(FIG6, f"{name}-{k}.png") for k in range(1, n + 1)]
        missing = [p for p in stages if not os.path.exists(p)]
        if missing:
            log(f"figures: SKIP {title!r}: {len(missing)} of {n} PNGs of {name} missing; the build keeps its table")
            continue
        sizes = {png_size(p) for p in stages}
        assert len(sizes) == 1, (name, sizes)
        (wpx, hpx), = sizes
        slides = [prs.slides[i] for i in build(prs, title)]
        tables = [named(s, "Ledger table") for s in slides]
        assert all(len(t) == 1 for t in tables), (title, [len(t) for t in tables])
        tops = {t[0].top for t in tables}
        assert len(tops) == 1, (title, tops)
        t0 = tops.pop()
        last = slides[-1]
        body = body_of(last)
        old_new = LEAD_INS.get(title)
        if old_new:
            for s in slides:
                b = body_of(s)
                assert b.text_frame.text == old_new[0], (title, b.text_frame.text)
                set_first_run(b, old_new[1])
        tb = text_bottom(prs, last, body) if body is not None else None
        top = t0 if tb is None else max(t0, tb + MIN_GAP)
        w, h = COL_WIDTH, int(round(COL_WIDTH * hpx / wpx))
        bs = banners(last)
        assert len(bs) <= 1, (title, [b.text_frame.text for b in bs])
        gap, scale = GAP, 1.0
        if bs:
            bh = bs[0].height
            if top + h + GAP + bh > FLOOR:
                scale = max(MIN_SCALE, (FLOOR - bh - GAP - top) / h)
                gap = min(GAP, FLOOR - bh - top - int(round(h * scale)))
                if gap < MIN_GAP:
                    log(f"WARN {title!r}: the closing box sits {gap / EMU_PT:.1f} pt under the figure at {MIN_SCALE:.0%}")
        fw, fh = int(round(w * scale)), int(round(h * scale))
        left = COL_LEFT if scale == 1.0 else COL_AXIS - fw // 2
        box_top = top + fh + gap
        for k, s in enumerate(slides, 1):
            stage = n if title in WHOLE else min(k, n)
            table = tables[k - 1][0]
            pic = s.shapes.add_picture(stages[stage - 1], left, top, fw, fh)
            pic.name = f"Figure {name}"
            s.shapes._spTree.remove(pic._element)
            table._element.addprevious(pic._element)
            drop(table)
            for b in banners(s):
                b.top = box_top
            b_k = body_of(s)
            if b_k is not None and tb is not None and b_k.top + b_k.height > top - TEXT_GAP:
                b_k.height = top - TEXT_GAP - b_k.top
        where = f"top {top}" + (f" ({(top - tb) / EMU_PT:.1f} pt under the lead-in)" if tb is not None else " (the table's)")
        log(f"figures: {title!r}: slides {list(prs.slides).index(slides[0]) + 1}-{list(prs.slides).index(last) + 1} show "
            f"{name} stages {[n if title in WHOLE else min(k, n) for k in range(1, len(slides) + 1)]}, {where}, "
            f"{scale:.0%} ({fw} x {fh}), closing box at {box_top}")
        if title in WHOLE:
            replaced.update(collapse_to_pair(prs, title))
    return replaced


# ----------------------------------------------------------------------------------------------- 4. the closing build and the midterm slide
CLOSING_OLD = "Next week, the plan becomes a boundary."
CLOSING_TITLE = "Next Friday is the midterm."
CLOSING_LEAD = ("Next week:", "Friday, October 23:")
CLOSING_REST = (" the midterm, one hour, individual, closed book, units 1 and 2 as taught. Week 8, October 30, teaches concurrency and "
                "multi-agent patterns. HW1 is due tonight before 11:59 pm. HW2 is released today and due Friday, November 13.")
DEFERRED = "Deferred to week 11: failure semantics, including which component makes a side effect happen once."
CLOSING_BOX_OLD = "Next week a plan fixed before any tool output arrives"
CLOSING_BOX = "A rule belongs where the adversary cannot reach it from inside the agent."


def place_box_under_text(prs, slides, what):
    """With measurements: the closing box of the build's last click goes GAP under the body text, at the height of its line count, and
    the body's declared box ends above it."""
    last = slides[-1]
    body, bs = body_of(last), banners(last)
    tb = text_bottom(prs, last, body)
    if tb is None or not bs:
        return
    m = measured(prs, last, bs[0])
    bh = box_height(int(m["lines"])) if m and m.get("lines") else bs[0].height
    top = min(tb + GAP, FLOOR - bh)
    for s in slides:
        for b in banners(s):
            b.top, b.height = top, bh
        b_k = body_of(s)
        if b_k.top + b_k.height > top - TEXT_GAP:
            b_k.height = top - TEXT_GAP - b_k.top
    log(f"{what}: closing box at {top}, {bh} tall, {(top - tb) / EMU_PT:.1f} pt under the text")


def closing(prs):
    slides = [prs.slides[i] for i in build(prs, CLOSING_OLD)]
    for s in slides:
        set_first_run(title_shape(s), CLOSING_TITLE)
        ps = body_of(s).text_frame.paragraphs
        assert len(ps) == 2 and ps[1].text == DEFERRED and ps[0].runs[0].text == CLOSING_LEAD[0], [p.text for p in ps]
        ps[0].runs[0].text = CLOSING_LEAD[1]
        ps[0].runs[1].text = CLOSING_REST
        for r in ps[0].runs[2:]:
            r._r.getparent().remove(r._r)
    bs = banners(slides[-1])
    assert len(bs) == 1 and bs[0].text_frame.text.startswith(CLOSING_BOX_OLD), [b.text_frame.text for b in bs]
    set_first_run(bs[0], CLOSING_BOX)
    log(f"closing: {len(slides)} slides retitled {CLOSING_TITLE!r}, first bullet rewritten, closing box rewritten, notes kept")
    return slides


MIDTERM_TITLE = "What the midterm covers"
MIDTERM_BULLETS = [  # (bold lead phrase, rest): the sentences are the plan's, the bold split is the house style's lead phrase
    ("Dynamic control", " and who chooses the next operation."),
    ("State records, routing and termination;", " token accounting and admission."),
    ("Tool contracts and the dispatch cycle;", " action representation, structured and code actions."),
    ("MCP hosts, clients, servers", " and transports."),
    ("The tool boundary under attack,", " and where a rule is enforced."),
]
MIDTERM_BOX = "One hour, individual, closed book. The questions ask for reasoning about scenarios rather than recall of APIs."
MIDTERM_NOTES = ("Midterm scope, as taught. Friday, October 23: one hour, individual, closed book, units 1 and 2. Scheduling tradeoffs are "
                 "not on the midterm. Week 8, on October 30, teaches concurrency and multi-agent patterns.")
TEMPLATE = "Model-based security controls"
POLL = "Where should the ~/.ssh rule be enforced?"


def bullet_protos(prs):
    """The house bullet, shown and not yet revealed, as the template build has them: its third bullet ('Both live in the prompt or the
    weights,') on its last click (black, the ● glyph) and on its first (transparent white, alpha 0, no glyph)."""
    tb = build(prs, TEMPLATE)
    shown = copy.deepcopy(body_of(prs.slides[tb[-1]]).text_frame.paragraphs[2]._p)
    hidden = copy.deepcopy(body_of(prs.slides[tb[0]]).text_frame.paragraphs[2]._p)
    for p, glyph in ((shown, "a:buChar"), (hidden, "a:buNone")):
        assert len(p.findall(qn("a:r"))) == 2 and p.find(qn("a:pPr")).find(qn(glyph)) is not None, glyph
    alphas = list(hidden.iter(qn("a:alpha")))
    assert len(alphas) == 3 and all(a.get("val") == "0" for a in alphas) and not list(shown.iter(qn("a:alpha")))
    return shown, hidden


def bullet(proto, lead, rest):
    p = copy.deepcopy(proto)
    r1, r2 = p.findall(qn("a:r"))
    r1.find(qn("a:t")).text, r2.find(qn("a:t")).text = lead, rest
    return p


def midterm_clicks(prs, full):
    """The midterm slide with every bullet and its box is the build's last click. Before it go one click per bullet (lectures/CLAUDE.md:
    a text slide shows one bullet per click, and the closing box is the last click): click k shows bullets 1 to k, carries the later
    ones in the not-yet-revealed format so nothing moves, has no box, and carries the full slide's notes. Returns the six slides in order."""
    shown, hidden = bullet_protos(prs)
    paras = body_of(full).text_frame.paragraphs
    assert [p.text for p in paras] == [lead + rest for lead, rest in MIDTERM_BULLETS], [p.text for p in paras]
    assert len(banners(full)) == 1, [b.text_frame.text for b in banners(full)]
    clicks = []
    for k in range(1, len(MIDTERM_BULLETS) + 1):
        c = copy_slide(prs, full)
        for b in banners(c):
            drop(b)
        txBody = body_of(c).text_frame._txBody
        for j, (p, (lead, rest)) in enumerate(zip(txBody.findall(qn("a:p")), MIDTERM_BULLETS)):
            if j >= k:
                txBody.replace(p, bullet(hidden, lead, rest))
        copy_notes(c, full)
        clicks.append(c)
    return clicks + [full]


def midterm(prs):
    """The midterm-scope build after the poll. Its last click is a copy of the first slide of the 'Model-based security controls' build
    without its references, with five bullets in the house format of that build's last click and its closing box; midterm_clicks puts one
    click per bullet before it. Returns the six slides."""
    tb = build(prs, TEMPLATE)
    first, last = prs.slides[tb[0]], prs.slides[tb[-1]]
    s = copy_slide(prs, first)
    for sh in list(s.shapes):
        if sh.name == "Citations" or sh._element.tag == qn("p:pic"):
            drop(sh)
    set_first_run(title_shape(s), MIDTERM_TITLE)
    txBody = body_of(s).text_frame._txBody
    shown, _ = bullet_protos(prs)
    for p in txBody.findall(qn("a:p")):
        txBody.remove(p)
    for lead, rest in MIDTERM_BULLETS:
        txBody.append(bullet(shown, lead, rest))
    box = copy.deepcopy(banners(last)[0]._element)
    box.find(".//" + qn("p:cNvPr")).set("id", str(next_id(s)))
    s.shapes._spTree.append(box)
    set_first_run(banners(s)[0], MIDTERM_BOX)
    for rid, rel in list(s.part.rels.items()):           # the template's ATLAS links went with its paragraphs
        if rel.is_external:
            drop_if_unused(s, rid)
    set_notes(s, MIDTERM_NOTES)
    slides = midterm_clicks(prs, s)
    poll = build(prs, POLL)
    move_to(prs, slides, poll[-1] + 1)
    log(f"midterm: {MIDTERM_TITLE!r} inserted at {poll[-1] + 2}-{poll[-1] + 1 + len(slides)}, after the poll: one bullet per click, "
        f"the closing box on the last")
    return slides


# ----------------------------------------------------------------------------------------------- 5. slide numbers
# Numbers in Rahul's notes that are wrong in the 416-slide deck as well: they were written against revision 3 (405 slides) and earlier
# cuts. Each is corrected to the slide whose content its sentence describes, checked against lecture5.pptx on 2026-10-15; the generic
# renumbering then maps the corrected number. (build title, text in one run of the notes, replacement)
STALE = [
    ("Model-based security controls", "family of slide 220)", "family of slide 219)"),   # 212-219 lists the 'harden the model' family
    ("Model-based security controls", "Slide 242 quotes", "Slide 241 quotes"),           # 237-241 quotes ATLAS's warning; 242 is OpenClaw
    ("Enforcement points and trust boundaries", "The table on slide 328 gives", "The figure on slide 333 gives"),   # the bypass build, 329-333
    ("Attacks enter through text or the process.", "sequence diagram of slide 48)", "sequence diagram of slide 46)"),
    ("OpenShell governs each sandbox on its own.", "(slide 395;", "(slide 400;"),          # AgentKernel is on 396-400, as the body's link says
    ("Limits of OpenShell enforcement", "Slide 64", "Slide 62"),                             # the contract's enforced parts, 56-62
    ("Limits of OpenShell enforcement", "(Persistence): Slide 49", "(Persistence): Slide 47"),   # the tool result, 47
    ("Limits of OpenShell enforcement", "Slide 108, a ", "Slide 100, a "),                   # 96-100: 'a changed implementation under an unchanged description'
    ("The agent must not reach the runtime.", "five parts (slide 64)", "five parts (slide 62)"),
    ("The agent must not reach the runtime.", "slides 372 and 378", "slides 382 and 387"),   # the two asset builds, 377-382 and 383-387
    ("The agent must not reach the runtime.", "(slides 338 to 382)", "(slides 343 to 387)"),  # the OpenShell slides
    ("The agent must not reach the runtime.", "slide 24", "slide 23"),                       # 'A rule inside the agent can be disabled.', 21-23
    (POLL, "Sentry (slide 367)", "Sentry (slide 372)"),                                      # 369-372
]


# The early ~/.ssh poll. Rahul's notes cite "the poll of slide 25", which "asked the class" and "returns on slide 407", and the poll's own
# notes compare its split "with the one recorded on slide 25". That poll was slide 25 of lecture 5's revision 3 (2026-10-09 07:29); every
# save of his from 09:02 that day on lacks it, so lecture 5 was most likely taught without it, and lecture6.pptx asks the question once.
# The first sentence now names the poll this deck carries; the comparison sentence goes. In a full run the poll is the 416-slide
# deck's 412 (renumber6 maps it); in a MODE=fix1 run the notes carry the first patch's wording and name the poll by its position in the
# input (159 in the first patch, 163 once patch-r6b.py has added its four slides before it).
POLL_CITES = "Tool use weakens a model's refusals."
POLL_ASKED = " asked the class where the rule about ~/.ssh belongs, and returns on slide {}."
POLL_ASKS = " asks the class where the rule about ~/.ssh belongs."
POLL_COMPARE = ". Compare this split with the one recorded on "
EARLY_POLL = {"full": ("slide 25", 407, 412), "fix1": ("lecture 5's revision 3 (its 25th slide)", None, None)}


def poll_refs(prs):
    early, said, poll_at = EARLY_POLL[MODE]
    if said is None:                                   # fix1: the poll where the input deck has it
        said = poll_at = build(prs, POLL)[0] + 1
    n = 0
    for i in build(prs, POLL_CITES):
        runs = list(prs.slides[i].notes_slide.notes_text_frame._txBody.iter(qn("a:t")))
        at = [k for k, t in enumerate(runs) if t.text == early]
        assert len(at) == 1 and runs[at[0] + 1].text == POLL_ASKED.format(said), (i + 1, [t.text for t in runs])
        runs[at[0]].text, runs[at[0] + 1].text = f"slide {poll_at}", POLL_ASKS
        n += 1
    for i in build(prs, POLL):
        runs = list(prs.slides[i].notes_slide.notes_text_frame._txBody.iter(qn("a:t")))
        at = [k for k, t in enumerate(runs) if t.text == early]
        assert len(at) == 1 and runs[at[0] - 1].text == POLL_COMPARE and runs[at[0] + 1].text == ". ", (i + 1, [t.text for t in runs])
        runs[at[0] - 1].text = ". "
        for t in (runs[at[0]], runs[at[0] + 1]):
            r = t.getparent()
            r.getparent().remove(r)
        n += 1
    log(f"poll: {n} notes no longer cite the early ~/.ssh poll; '{POLL_CITES}' names the poll at slide {poll_at} "
        f"(this run's numbering), the poll's own notes drop the comparison")


def fix_stale(prs):
    fixed = 0
    for title, old, new in STALE:
        for i in build(prs, title):
            runs = [t for t in prs.slides[i].notes_slide.notes_text_frame._txBody.iter(qn("a:t"))
                    if t.text and (t.text == old if re.fullmatch(r"(?i)slides? \d+", old) else old in t.text)]
            assert len(runs) == 1, (title, old, i + 1, len(runs))
            runs[0].text = runs[0].text.replace(old, new)
            fixed += 1
    log(f"notes: {len(STALE)} stale slide numbers corrected by content, {fixed} runs")


NUMREF = re.compile(r"(?i)\b(slides?)(\s+)(\d+)((?:\s*(?:,|and|to|–|-|&)\s*\d+)*)")


def remap_text(text, old_to_new, old_titles):
    """'slide 291' -> 'slide 39'; a number this deck no longer carries -> 'the removed slide 219 (“title”)'."""
    def removed(n):
        return f"{n} (“{old_titles.get(n, '?')}”)"

    def one(m):
        word, sp, first, rest = m.groups()
        nums = [int(first)] + [int(x) for x in re.findall(r"\d+", rest)]
        gone = [n not in old_to_new for n in nums]
        if not any(gone):
            return f"{word}{sp}{old_to_new[int(first)]}" + re.sub(r"\d+", lambda k: str(old_to_new[int(k.group(0))]), rest)
        lead = "The removed " if word[0].isupper() else "the removed "
        if all(gone):
            return f"{lead}{word.lower()}{sp}{removed(int(first))}" + re.sub(r"\d+", lambda k: removed(int(k.group(0))), rest)
        log(f"WARN notes: a reference mixes kept and removed slides: {m.group(0)!r}")
        num = lambda n: str(old_to_new[n]) if n in old_to_new else f"removed {removed(n)}"
        return f"{word}{sp}{num(int(first))}" + re.sub(r"\d+", lambda k: num(int(k.group(0))), rest)
    return NUMREF.sub(one, text)


def renumber6(prs, old_to_new, old_titles, skip_ids):
    index_of = {s.part: i + 1 for i, s in enumerate(prs.slides)}
    linked = shifted = 0
    for s in prs.slides:
        for h in s._element.iter(qn("a:hlinkClick")):
            if h.get("action", "").startswith("ppaction://hlinksldjump"):
                target = s.part.rels[h.get(qn("r:id"))].target_part
                t = h.getparent().getparent().find(qn("a:t"))
                if t is not None and t.text and t.text.strip().isdigit():
                    t.text = str(index_of[target]); linked += 1
        if s.slide_id in skip_ids or not s.has_notes_slide:
            continue
        for t in s.notes_slide.notes_text_frame._txBody.iter(qn("a:t")):
            if t.text and NUMREF.search(t.text):
                new = remap_text(t.text, old_to_new, old_titles)
                if new != t.text:
                    t.text = new; shifted += 1
    log(f"renumbered: {linked} link texts, {shifted} note runs")


POSREF = re.compile(r"(?i)(?<!removed )\b(slides?)(\s+)(\d+)((?:\s*(?:,|and|to|–|-|&)\s*\d+)*)")


def renumber_positions(prs, pos_map):
    """MODE=fix1: the notes already name this deck's slides by position (renumber6 wrote them). Every slide-jump link text follows its
    target, and every 'slide N' in the notes moves to N's new position; 'the removed slide N (“…”)' names a lecture 5 slide and stays."""
    index_of = {s.part: i + 1 for i, s in enumerate(prs.slides)}
    linked = shifted = 0

    def one(m):
        word, sp, first, rest = m.groups()
        for n in [int(first)] + [int(x) for x in re.findall(r"\d+", rest)]:
            assert n in pos_map, ("a slide number this deck does not have", m.group(0))
        return f"{word}{sp}{pos_map[int(first)]}" + re.sub(r"\d+", lambda k: str(pos_map[int(k.group(0))]), rest)
    for s in prs.slides:
        for h in s._element.iter(qn("a:hlinkClick")):
            if h.get("action", "").startswith("ppaction://hlinksldjump"):
                target = s.part.rels[h.get(qn("r:id"))].target_part
                t = h.getparent().getparent().find(qn("a:t"))
                if t is not None and t.text and t.text.strip().isdigit():
                    t.text = str(index_of[target]); linked += 1
        if not s.has_notes_slide:
            continue
        for t in s.notes_slide.notes_text_frame._txBody.iter(qn("a:t")):
            if t.text and POSREF.search(t.text):
                new = POSREF.sub(one, t.text)
                if new != t.text:
                    t.text = new; shifted += 1
    log(f"renumbered: {linked} link texts, {shifted} note runs moved to the new positions")


# ----------------------------------------------------------------------------------------------- main
SLIDE_OF = {}   # Rahul's slide number in SRC -> the slide object


def save(prs, n0):
    for title in ("Limits of OpenShell enforcement", POLL, MIDTERM_TITLE, CLOSING_TITLE):
        at = build(prs, title)
        log(f"at: {title!r} on slides {at[0] + 1}-{at[-1] + 1}")
    prs.save(OUT)
    log(f"saved {OUT}: {n0} -> {len(prs.slides)} slides")
    with open(OUT + ".log", "w") as f:
        f.write("\n".join(LOG) + "\n")


def main():
    prs = Presentation(SRC)
    src = Presentation(L5)
    n0 = len(prs.slides)
    SLIDE_OF.update({k: s for k, s in enumerate(prs.slides, 1)})
    back_template = copy.deepcopy(named(SLIDE_OF[int(next(i for i in MAP if named(SLIDE_OF[int(i)], "Back link")))], "Back link")[0]._element)
    old_titles = {n: clean_title(title_of(s)) for n, s in enumerate(src.slides, 1)}
    copies = recap(prs, src)
    mid = midterm(prs)
    slide_for_old = {old: SLIDE_OF[int(i)] for i, old in MAP.items()}
    slide_for_old.update(copies)
    targets = repair_links(prs, src, slide_for_old)
    back_link_on_targets(copies, targets, back_template)
    replaced = tables_to_figures(prs)
    slide_for_old = {old: replaced.get(s.part, s) for old, s in slide_for_old.items()}
    end = closing(prs)
    place_box_under_text(prs, end, "closing")
    place_box_under_text(prs, mid, "midterm")
    fix_stale(prs)
    poll_refs(prs)
    position = {s.slide_id: i + 1 for i, s in enumerate(prs.slides)}
    old_to_new = {old: position[s.slide_id] for old, s in slide_for_old.items()}
    renumber6(prs, old_to_new, old_titles, {c.slide_id for c in copies.values()} | {m.slide_id for m in mid})
    save(prs, n0)


def main_fix1():
    """The two corrections on a deck that already carries the first patch (lecture6.pptx as installed, or Rahul's later save of it)."""
    prs = Presentation(SRC)
    n0 = len(prs.slides)
    before = [s.part for s in prs.slides]
    poll_refs(prs)                                     # before anything moves: its numbers are the input's positions
    at = build(prs, MIDTERM_TITLE)
    assert len(at) == 1, ("the midterm build already has its clicks", len(at))
    slides = midterm_clicks(prs, prs.slides[at[0]])
    move_to(prs, slides, at[0])
    log(f"midterm: {MIDTERM_TITLE!r} at {at[0] + 1}-{at[0] + len(slides)}: one bullet per click, the closing box on the last")
    replaced = collapse_to_pair(prs, "Limits of OpenShell enforcement")
    assert replaced, "the Limits build has no clicks to drop"
    position = {s.part: i + 1 for i, s in enumerate(prs.slides)}
    pos_map = {k: position[replaced[part].part if part in replaced else part] for k, part in enumerate(before, 1)}
    log(f"positions: {sum(1 for k, v in pos_map.items() if k != v)} of {len(pos_map)} slides moved")
    renumber_positions(prs, pos_map)
    save(prs, n0)


if __name__ == "__main__":
    main() if MODE == "full" else main_fix1()
