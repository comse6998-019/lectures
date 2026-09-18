"""Approximate renderer for checking deck slides: real font metrics, per-run colour.

DECK=<path> SLIDES=13,14 python preview.py   ->  writes preview/slide-NN.png and reports overflows.
"""
import os, io, re
from pptx import Presentation
from pptx.oxml.ns import qn
from PIL import Image, ImageDraw, ImageFont

DECK = os.environ.get("DECK", "/Users/rkrsn/COMSE6998-019/lectures/lecture-2--2026-09-18/lecture2-1.pptx")
SLIDES = [int(x) for x in os.environ.get("SLIDES", "11").split(",")]
OUT = os.environ.get("OUT", "/tmp/slide-preview")
os.makedirs(OUT, exist_ok=True)
DPI = 150
EMU_PX = 914400 / DPI
FDIR = "/Users/rkrsn/Library/Fonts"
SCHEME = {"tx2": "#E8E8E8", "tx1": "#000000", "bg1": "#FFFFFF", "dk1": "#000000", "lt1": "#FFFFFF"}


def _deck_scheme(path):
    """The theme's colours, read through the master's colour map. This deck swaps bg2 and tx2,
    so a hard-coded table gets the navy citation and the light panel text the wrong way round."""
    import zipfile
    z = zipfile.ZipFile(path)
    block = re.search(r"<a:clrScheme.*?</a:clrScheme>",
                      z.read("ppt/theme/theme1.xml").decode("utf-8"), re.S).group(0)
    raw = {}
    for m in re.finditer(r'<a:(\w+)>\s*<a:(?:srgbClr val="([0-9A-Fa-f]{6})"'
                         r'|sysClr[^>]*lastClr="([0-9A-Fa-f]{6})")', block):
        raw[m.group(1)] = "#" + (m.group(2) or m.group(3)).upper()
    out = dict(raw)
    mp = re.search(r"<p:clrMap([^/]*)/>",
                   z.read("ppt/slideMasters/slideMaster1.xml").decode("utf-8"))
    if mp:
        for k, v in re.findall(r'(\w+)="(\w+)"', mp.group(1)):
            if v in raw:
                out[k] = raw[v]
    return out


def slide_background(slide):
    """The page colour, taken from the slide's own <p:bg>, then its layout, then the master.
    A slide can carry a dark background on the ordinary content layout, so the layout's name
    says nothing about whether the page is dark."""
    for part in (slide, slide.slide_layout, slide.slide_layout.slide_master):
        xml = part.part.blob.decode("utf-8")
        m = re.search(r"<p:bg>.*?</p:bg>", xml, re.S)
        if m:
            col = shape_colour(m.group(0))
            if col:
                return col
    return "#FFFFFF"


def shape_colour(frag):
    """A shape's fill or line colour, literal or from the scheme. Returns None when neither."""
    m = re.search(r'<a:srgbClr val="([0-9A-Fa-f]{6})"', frag)
    if m:
        return "#" + m.group(1)
    m = re.search(r'<a:schemeClr val="(\w+)"', frag)
    return SCHEME.get(m.group(1)) if m else None


try:
    SCHEME.update(_deck_scheme(DECK))
except Exception as exc:                      # a deck without a theme still renders, in fallback colours
    print("theme colours unavailable, using defaults:", exc)

_fcache = {}
def font(sz, bold=False, ital=False, mono=False):
    key = (round(sz, 1), bold, ital, mono)
    if key not in _fcache:
        if mono:
            path = "/System/Library/Fonts/Menlo.ttc"
        else:
            name = "FiraSans-%s.ttf" % ("BoldItalic" if bold and ital else "Bold" if bold else "Italic" if ital else "Regular")
            path = f"{FDIR}/{name}"
        _fcache[key] = ImageFont.truetype(path, max(1, int(sz * DPI / 72)))
    return _fcache[key]

def px(e):
    return int(e / EMU_PX)

def para_props(p, d):
    pPr = p._p.find(qn('a:pPr'))
    d = dict(d)
    if pPr is not None:
        for attr, key in (('marL', 'marL'), ('indent', 'indent')):
            if pPr.get(attr) is not None:
                d[key] = int(pPr.get(attr))
        if pPr.get('algn'):
            d['algn'] = pPr.get('algn')
        if pPr.find(qn('a:buNone')) is not None:
            d['bullet'] = None
        bc = pPr.find(qn('a:buChar'))
        if bc is not None:
            d['bullet'] = bc.get('char')
        bclr = pPr.find(qn('a:buClr'))
        if bclr is not None and bclr.find(qn('a:srgbClr')) is not None:
            d['buClr'] = "#" + bclr.find(qn('a:srgbClr')).get('val')
        bsz = pPr.find(qn('a:buSzPts'))
        if bsz is not None:
            d['buSz'] = int(bsz.get('val')) / 100
        for tag, key in (('a:spcAft', 'spcAft'), ('a:spcBef', 'spcBef')):
            el = pPr.find(qn(tag))
            if el is not None and el.find(qn('a:spcPts')) is not None:
                d[key] = int(el.find(qn('a:spcPts')).get('val')) / 100
        ls = pPr.find(qn('a:lnSpc'))
        if ls is not None and ls.find(qn('a:spcPct')) is not None:
            d['lnSpc'] = int(ls.find(qn('a:spcPct')).get('val')) / 100000
    return d

def run_props(r, dsz, dcol, dbold):
    f = r.font
    sz = f.size.pt if f.size else dsz
    bold = bool(f.bold) if f.bold is not None else dbold
    ital = bool(f.italic)
    mono = bool(f.name and ("Menlo" in f.name or "Mono" in f.name or "Courier" in f.name))
    col = dcol
    try:
        if f.color is not None and f.color.type is not None and int(f.color.type) == 1:
            col = "#" + str(f.color.rgb)          # RGBColor is a tuple subclass; str gives the hex
    except Exception:
        pass
    rPr = f._rPr
    if rPr is not None:
        sf = rPr.find(qn('a:solidFill'))
        if sf is not None and sf.find(qn('a:schemeClr')) is not None:
            col = SCHEME.get(sf.find(qn('a:schemeClr')).get('val'), col)
    return sz, bold, ital, col, mono

def layout_paragraph(d, runs, avail, dsz, dcol, dbold):
    """Wrap a paragraph whose runs may differ in font and colour. Returns lines of segments."""
    chars = []
    for r in runs:
        sz, bold, ital, col, mono = run_props(r, dsz, dcol, dbold)
        fo = font(sz, bold, ital, mono)
        for ch in r.text:
            chars.append((ch, fo, col))
    words, cur, started = [], [], False
    for ch, fo, col in chars:
        if ch == " " and started:
            if cur:
                words.append(cur); cur = []
        else:
            # leading spaces belong to the first word: code panels are indented with them
            if ch != " ":
                started = True
            cur.append((ch, fo, col))
    if cur:
        words.append(cur)

    def seg(word):
        out = []
        for ch, fo, col in word:
            if out and out[-1][1] is fo and out[-1][2] == col:
                out[-1][0] += ch
            else:
                out.append([ch, fo, col])
        return [(t, f, c) for t, f, c in out]

    def wordw(word):
        return sum(d.textlength(t, font=f) for t, f, c in seg(word))

    lines, line, w = [], [], 0.0
    for word in words:
        ww = wordw(word)
        sp = d.textlength(" ", font=word[0][1]) if line else 0
        if line and w + sp + ww > avail:
            lines.append(line); line, w, sp = [], 0.0, 0
        line.append((seg(word), sp)); w += sp + ww
    if line:
        lines.append(line)
    return lines

def draw_text_frame(d, sh, L, T, RW, RH, is_title, is_body):
    tf = sh.text_frame
    dflt = dict(marL=0, indent=0, algn='l', bullet=None, buClr="#434343", buSz=None,
                spcAft=0, spcBef=0, lnSpc=1.0)
    if is_body:
        dflt.update(marL=457200, indent=-331453, bullet="●", lnSpc=1.15)
    # presentation.xml's defaultTextStyle is 14 pt: a plain text box does not fall back to 18
    dsz = 24 if is_title else 14
    # an uncoloured run falls back to defaultTextStyle, which is black, not navy
    dcol = "#2D2A62" if is_title else ("#434343" if is_body else "#000000")
    dbold = bool(is_title)
    li = px(tf.margin_left if tf.margin_left is not None else 91440)
    ri = px(tf.margin_right if tf.margin_right is not None else 91440)

    blocks = []
    for p in tf.paragraphs:
        runs = [r for r in p.runs if r.text]
        if not runs:
            continue
        pp = para_props(p, dflt)
        sz0, b0, i0, c0, m0 = run_props(runs[0], dsz, dcol, dbold)
        avail = RW - li - ri - px(pp['marL'])
        if tf.word_wrap is False:          # wrap="none": PowerPoint lets the text run past the box
            avail = 10 ** 6
        lines = layout_paragraph(d, runs, avail, dsz, dcol, dbold)
        lh = int(sz0 * pp['lnSpc'] * 1.12 * DPI / 72)
        blocks.append((pp, lines, lh, sz0, c0))

    total = sum(int(b[0]['spcBef'] * DPI / 72) + len(b[1]) * b[2] + int(b[0]['spcAft'] * DPI / 72)
                for b in blocks)
    anchor = tf.vertical_anchor
    y = T + ((RH - total) // 2 if anchor is not None and int(anchor) == 3 else px(45720))

    for pp, lines, lh, sz0, c0 in blocks:
        y += int(pp['spcBef'] * DPI / 72)
        for i, line in enumerate(lines):
            linew = sum(sp + sum(d.textlength(t, font=f) for t, f, c in segs) for segs, sp in line)
            tx = L + li + px(pp['marL'])
            if pp['algn'] == 'ctr':
                tx = L + li + (RW - li - ri - linew) // 2
            elif pp['algn'] == 'r':
                tx = L + RW - ri - linew
            if i == 0 and pp['bullet']:
                bs = (pp['buSz'] or sz0 * 0.9) * DPI / 72
                bx, by = tx + px(pp['indent']), y + lh * 0.42
                r = bs * 0.19
                d.ellipse([bx, by - r, bx + 2 * r, by + r], fill=pp['buClr'])
            x = tx
            for segs, sp in line:
                x += sp
                for t, f, c in segs:
                    d.text((x, y), t, font=f, fill=c)
                    x += d.textlength(t, font=f)
            y += lh
        y += int(pp['spcAft'] * DPI / 72)
    return y

prs = Presentation(DECK)
W, H = px(prs.slide_width), px(prs.slide_height)
problems = []
for idx in SLIDES:
    s = prs.slides[idx - 1]
    page = slide_background(s)
    dark = page.lower() not in ("#ffffff", "white")
    img = Image.new("RGB", (W, H), page)
    d = ImageDraw.Draw(img)
    for sh in s.shapes:
        if sh.left is None:
            continue
        L, T, RW, RH = px(sh.left), px(sh.top), px(sh.width), px(sh.height)
        if sh.shape_type == 13:
            img.paste(Image.open(io.BytesIO(sh.image.blob)).convert("RGB").resize((RW, RH)), (L, T))
            continue
        if sh.has_table:
            tbl = sh.table
            y = T
            for ri_, row in enumerate(tbl.rows):
                cells, hs, x = [], [], L
                for ci, cell in enumerate(row.cells):
                    cw = px(tbl.columns[ci].width)
                    runs = [r for p in cell.text_frame.paragraphs for r in p.runs if r.text]
                    if runs:
                        sz = runs[0].font.size.pt if runs[0].font.size else 10
                        lines = layout_paragraph(d, runs, cw - px(190500), 10, "#000000", False)
                    else:
                        sz, lines = 10, []
                    lh = int(sz * 1.22 * DPI / 72)
                    hs.append(len(lines) * lh + px(95250))
                    cells.append((x, lines, lh))
                    x += cw
                rh = max(max(hs), px(tbl.rows[ri_].height))
                for (x, lines, lh) in cells:
                    ty = y + px(47625)
                    for line in lines:
                        cx = x + px(95250)
                        for segs, sp in line:
                            cx += sp
                            for t, f, c in segs:
                                d.text((cx, ty), t, font=f, fill=c)
                                cx += d.textlength(t, font=f)
                        ty += lh
                d.line([(L, y), (L + RW, y)], fill="#000000", width=2 if ri_ == 0 else 1)
                y += rh
            d.line([(L, y), (L + RW, y)], fill="#000000", width=1)
            if y > T + RH + 3:
                problems.append(f"slide {idx}: table grew {y - (T + RH)}px past its box")
            continue
        spPr = sh._element.xml.split('<p:txBody')[0]
        fm = re.search(r'<a:solidFill>.*?</a:solidFill>', spPr.split('<a:ln')[0], re.S)
        fill = shape_colour(fm.group(0)) if fm else None
        lnm = re.search(r'<a:ln[ >].*?</a:ln>', spPr, re.S)
        outline = shape_colour(lnm.group(0)) if lnm else None
        # a connector has no area: draw it corner to corner, honouring its flip flags
        if str(sh.shape_type).startswith("LINE") or sh._element.tag.endswith('}cxnSp'):
            flipH = 'flipH="1"' in spPr
            flipV = 'flipV="1"' in spPr
            x0, x1 = (L + RW, L) if flipH else (L, L + RW)
            y0, y1 = (T + RH, T) if flipV else (T, T + RH)
            d.line([(x0, y0), (x1, y1)], fill=outline or "#000000", width=2)
            continue
        oval = '<a:prstGeom prst="ellipse"' in spPr
        if fill or outline:
            box = [L, T, L + RW, T + RH]
            if oval:
                d.ellipse(box, fill=fill, outline=outline, width=2 if outline else 1)
            else:
                if fill:
                    d.rectangle(box, fill=fill)
                if outline:
                    d.rectangle(box, outline=outline, width=2)
        if not sh.has_text_frame or not sh.text_frame.text.strip():
            continue
        is_title = sh.is_placeholder and sh.placeholder_format.idx == 0
        is_body = sh.is_placeholder and sh.placeholder_format.idx == 1
        yend = draw_text_frame(d, sh, L, T, RW, RH, is_title, is_body)
        if yend > T + RH + 4:
            problems.append(f"slide {idx}: {sh.name!r} text overflows its box by {yend - (T + RH)}px")
    img.save(f"{OUT}/slide-{idx:02d}.png")

print("problems:" if problems else "no fit problems found")
for p in problems:
    print(" -", p)
