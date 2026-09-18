"""Build the Section 1 slides onto a clean copy of the deck, one slide at a time.

Always reads SRC (the pristine 12-slide deck) and writes DST, then the caller installs DST.
Never delete-and-re-add slides in one python-pptx session: new parts can reuse a part name a
surviving slide still holds, silently overwriting it.
"""
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

SRC = "/private/tmp/claude-501/-Users-rkrsn-COMSE6998-019/c5b1d7a8-efae-4cba-b3f1-56f01f01a9bc/scratchpad/deck-clean.pptx"
DST = "/private/tmp/claude-501/-Users-rkrsn-COMSE6998-019/c5b1d7a8-efae-4cba-b3f1-56f01f01a9bc/scratchpad/deck-built.pptx"
INSERT_AT = 10                      # after the deck's slide 10, before "Questions"
NAVY = RGBColor(0x2A, 0x2A, 0x63)
BODY_L, BODY_W = Emu(319251), Emu(6014545)
FIGS = "/private/tmp/claude-501/-Users-rkrsn-COMSE6998-019/c5b1d7a8-efae-4cba-b3f1-56f01f01a9bc/scratchpad/slidefigs"

prs = Presentation(SRC)
M = prs.slide_masters[0]
LAY_CONTENT, LAY_DIVIDER = M.slide_layouts[1], M.slide_layouts[3]

def sub(el, tag, **attrs):
    e = el.makeelement(qn(tag), {k: str(v) for k, v in attrs.items()}); el.append(e); return e

def scheme(font, val):
    sf = sub(font._rPr, 'a:solidFill'); sub(sf, 'a:schemeClr', val=val)

def content_slide(title, keep_body=False):
    s = prs.slides.add_slide(LAY_CONTENT)
    for ph in list(s.placeholders):
        idx = ph.placeholder_format.idx
        if idx == 0 or (keep_body and idx == 1):
            continue
        ph._element.getparent().remove(ph._element)
    s.shapes.title.text_frame.text = title
    return s

def bluebox(slide, quote, attribution, top, height, size=14, attr_size=10):
    """The deck's navy statement bar, here holding a quoted definition."""
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, BODY_L, top, BODY_W, height)
    sh.fill.solid(); sh.fill.fore_color.rgb = NAVY
    sh.line.color.rgb = NAVY; sh.shadow.inherit = False
    tf = sh.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = tf.margin_right = Emu(182880)
    p = tf.paragraphs[0]
    sub(p._p.get_or_add_pPr(), 'a:lnSpc').append(p._p.makeelement(qn('a:spcPct'), {'val': '114000'}))
    r = p.add_run(); r.text = quote; r.font.size = Pt(size); scheme(r.font, 'tx2')
    if attribution:
        p2 = tf.add_paragraph(); p2.alignment = PP_ALIGN.RIGHT
        sub(p2._p.get_or_add_pPr(), 'a:spcBef').append(p2._p.makeelement(qn('a:spcPts'), {'val': '600'}))
        r2 = p2.add_run(); r2.text = attribution
        r2.font.size = Pt(attr_size); r2.font.italic = True; scheme(r2.font, 'tx2')
    return sh


def banner(slide, runs, top, height=Emu(560000), size=14, left=BODY_L, width=BODY_W):
    """The deck's navy statement bar; pass (text, emphasis) pairs."""
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    sh.fill.solid(); sh.fill.fore_color.rgb = NAVY
    sh.line.color.rgb = NAVY; sh.shadow.inherit = False
    tf = sh.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Emu(137160); tf.margin_right = Emu(137160)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    for text, emph in runs:
        r = p.add_run(); r.text = text
        r.font.size = Pt(size); r.font.bold = bool(emph); r.font.underline = bool(emph)
        scheme(r.font, 'tx2')
    return sh

def callout(slide, text, top, height=Emu(430000), size=12, left=BODY_L, width=BODY_W):
    """The deck's outlined note: no fill, navy rule, bold navy text."""
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    sh.fill.background(); sh.line.color.rgb = NAVY; sh.shadow.inherit = False
    tf = sh.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Emu(137160); tf.margin_right = Emu(137160)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = True; r.font.color.rgb = NAVY
    return sh

def bullets(slide, lead, items, top, height, lead_size=15, size=16, gap=800):
    """The deck's own list style: Fira Sans, the layout's round bullet, navy text."""
    body = [ph for ph in slide.placeholders if ph.placeholder_format.idx == 1][0]
    body.left, body.top, body.width, body.height = BODY_L, top, BODY_W, height
    tf = body.text_frame; tf.word_wrap = True
    first = True
    if lead:
        p = tf.paragraphs[0]
        pPr = p._p.get_or_add_pPr(); pPr.set('marL', '0'); pPr.set('indent', '0')
        sub(pPr, 'a:buNone')
        sub(pPr, 'a:spcAft').append(p._p.makeelement(qn('a:spcPts'), {'val': '1000'}))
        r = p.add_run(); r.text = lead
        r.font.size = Pt(lead_size); r.font.bold = True; r.font.color.rgb = NAVY
        first = False
    for it in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        pPr = p._p.get_or_add_pPr()
        pPr.set('marL', '400050'); pPr.set('indent', '-285750')
        sub(pPr, 'a:spcAft').append(p._p.makeelement(qn('a:spcPts'), {'val': str(gap)}))
        bu = sub(pPr, 'a:buClr'); sub(bu, 'a:srgbClr', val='2A2A63')
        sub(pPr, 'a:buSzPts', val=str(int(size * 100 * 0.9)))
        sub(pPr, 'a:buFont', typeface='Fira Sans')
        sub(pPr, 'a:buChar', char='●')
        r = p.add_run(); r.text = it
        r.font.size = Pt(size); r.font.color.rgb = NAVY
    return body


MONO = "Menlo"
GREY = RGBColor(0x8A, 0x8A, 0x9A)
CRIMSON = RGBColor(0xC7, 0x35, 0x61)
TEAL = RGBColor(0x09, 0x91, 0x91)

def label(slide, text, top, size=12):
    tb = slide.shapes.add_textbox(BODY_L, top, BODY_W, Emu(200000))
    r = tb.text_frame.paragraphs[0].add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = True; r.font.color.rgb = NAVY
    return tb

def codepanel(slide, rows, top, height, size=11):
    """A light panel of monospace source, one paragraph per line, changed spans coloured."""
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, BODY_L, top, BODY_W, height)
    sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor(0xF2, 0xF2, 0xF6)
    sh.line.fill.background(); sh.shadow.inherit = False
    try: sh.adjustments[0] = 0.04
    except Exception: pass
    tf = sh.text_frame; tf.word_wrap = False; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Emu(150000); tf.margin_top = Emu(60000); tf.margin_bottom = Emu(60000)
    for i, spans in enumerate(rows):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        sub(p._p.get_or_add_pPr(), 'a:buNone')
        for text, colour in spans:
            r = p.add_run(); r.text = text
            r.font.size = Pt(size); r.font.name = MONO
            r.font.color.rgb = colour or NAVY
            if colour is not None and colour != GREY:
                r.font.bold = True
    return sh

def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text

# ============================================================ slide 1: rational agents
s = content_slide("Rational agents", keep_body=True)
bluebox(s,
    "“For each possible percept sequence, a rational agent should select an action that is "
    "expected to maximize its performance measure, given the evidence provided by the percept "
    "sequence and whatever built-in knowledge the agent has.”",
    "Russell and Norvig, §2.2.2",
    Emu(820000), Emu(1330000), size=14)
bullets(s,
    "What is rational at any given time depends on four things:",
    ["The performance measure that defines the criterion of success",
     "The agent’s prior knowledge of the environment",
     "The actions that the agent can perform",
     "The agent’s percept sequence to date"],
    Emu(2360000), Emu(2300000))
notes(s, "Read the definition once, slowly. Then the four things it depends on. Two of the four are "
         "ours to write down before the agent runs: the performance measure and the action set. One is "
         "the world we put it in. The last one is the only thing that changes during a run, and every "
         "architecture in this lecture is a different answer to what to do with it.")

# ============================================================ slide 2: the demo agent
s = content_slide("A demo agent: mini-swe-agent")
bluebox(s,
    "One alert from OWASP BenchmarkPython, read as an issue report. mini-swe-agent localizes the "
    "flagged code, edits it, and submits a patch. The run ends when the submission is accepted.",
    None, Emu(730000), Emu(760000), size=14)
s.shapes.add_picture(f"{FIGS}/state-graph.png", Emu(751388), Emu(1720000), height=Emu(3290000))
notes(s, "This is the whole agent, as a state machine. Three states and five transitions. The controller "
         "decides the next action; a tool executes it and hands back an observation; the controller can "
         "instead ask to submit, and the run ends only when that submission is accepted. Read the labels "
         "as event, then condition in brackets. Every architecture in the rest of this block is a change "
         "to this machine: a new state, a new edge, or a different component deciding.")

# ============================================================ slide 3: before, the run, after
s = content_slide("One alert, one run, one patch")
label(s, "Before: the query is built by interpolation", Emu(630000))
codepanel(s, [
    [("46  ", GREY), ("sql = f'SELECT username from USERS where password = \\'", None),
     ("{bar}", CRIMSON), ("\\''", None)],
    [("49  ", GREY), ("cur.execute(sql)", None)],
], Emu(890000), Emu(520000))
s.shapes.add_picture(f"{FIGS}/run-compact.png", Emu(229000), Emu(1470000), width=Emu(6400000))
label(s, "After: the query carries a placeholder and the value is bound", Emu(3620000))
codepanel(s, [
    [("46  ", GREY), ("sql = 'SELECT username from USERS where password = ", None),
     ("?", TEAL), ("'", None)],
    [("49  ", GREY), ("cur.execute(sql", None), (", (bar,)", TEAL), (")", None)],
], Emu(3880000), Emu(520000))
notes(s, "The alert points at line 46, where the query is built by interpolating a request value. The agent "
         "reads the region, edits two lines, and submits. The patch puts a placeholder in the query text and "
         "binds the value when the query runs, so the value can no longer change the shape of the statement. "
         "Two lines, one file, and the whole run is six exchanges.")

# ============================================================ slide 4: why it is rational
s = content_slide("Why this is a rational agent", keep_body=True)
bullets(s,
    "It is rational, but only given four things we have to state:",
    ["The performance measure: one point if the patch removes the reported weakness and leaves the endpoint behaving as it did",
     "Prior knowledge: the application's layout, and what each tool returns",
     "The actions available: read_file, search, edit, submit",
     "The percepts: whatever the tools return, and nothing else"],
    Emu(740000), Emu(2700000), lead_size=14, size=14, gap=700)
banner(s, [("Reading the flagged lines before editing them is the action that ", None),
           ("maximizes expected performance", 1), (". No other agent does better in expectation.", None)],
       Emu(3480000), height=Emu(640000), size=14)
callout(s, "Rationality is relative to those four. State them, or the word means nothing.",
        Emu(4220000), height=Emu(430000))
notes(s, "Rationality is not a property of the program alone. It is a property of the program against a measure, "
         "prior knowledge, an action set, and a percept sequence. Say the four out loud, and the claim becomes "
         "checkable. The agent reads before it edits because looking is how it maximizes expected performance.")

# ============================================================ slide 5: when it is not
s = content_slide("When it is not", keep_body=True)
bullets(s,
    "Change one of those four and the same program stops being rational:",
    ["Charge a point per tool call, and an agent that reads whole files fares poorly. A better agent reads the smallest range that answers its question",
     "Let the value arrive from a helper in another file, and editing only the flagged line can leave the weakness in place, or change what the endpoint returns",
     "Keep editing after the submission is accepted, and every further call is waste that risks breaking behavior"],
    Emu(740000), Emu(2600000), lead_size=14, size=14, gap=800)
banner(s, [("Budget", 1), (", ", None), ("depth of investigation", 1), (", ", None), ("termination", 1),
           (". Each later section makes one of them a decision.", None)],
       Emu(3540000), height=Emu(500000), size=15)
callout(s, "And the Submit state checks less than the measure asks: accepted is not correct.",
        Emu(4180000), height=Emu(430000))
notes(s, "Three circumstances, and each becomes a component later. The budget is the runtime refusing a call. "
         "The depth of investigation is what the planner decides. Termination is the stopping rule the runtime "
         "owns. Close on the gap: the Submit state can check that the patch applies and that the rescan is clean, "
         "which is not the same as the endpoint still behaving as it did.")

# ---- place the new slides before the closing "Questions" slide --------------------
ids = list(prs.slides._sldIdLst)
new = ids[len(ids) - (len(ids) - 12):] if len(ids) > 12 else []
new = ids[12:]
for el in new:
    prs.slides._sldIdLst.remove(el)
for k, el in enumerate(new):
    prs.slides._sldIdLst.insert(INSERT_AT + k, el)

prs.save(DST)
print("built ->", DST, "| slides:", len(Presentation(DST).slides))
