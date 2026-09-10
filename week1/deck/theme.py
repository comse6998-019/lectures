"""Geometry, palette, and text-fit budgets measured from template.pptx."""

from pptx.dml.color import RGBColor

INK = RGBColor(0x00, 0x00, 0x00)
PAPER = RGBColor(0xFF, 0xFF, 0xFF)
MUTED = RGBColor(0x59, 0x59, 0x59)
WASH = RGBColor(0xEE, 0xEE, 0xEE)
PRIMARY = RGBColor(0x42, 0x85, 0xF4)
DARK = RGBColor(0x21, 0x21, 0x21)
GREY = RGBColor(0x78, 0x90, 0x9C)
WARM = RGBColor(0xFF, 0xAB, 0x40)
TEAL = RGBColor(0x00, 0x97, 0xA7)
LIME = RGBColor(0xEE, 0xFF, 0x41)

SLIDE_W = 7.5
SLIDE_H = 5.625

# Free canvas below a TITLE_ONLY heading. Clear of the slide-number
# placeholder, which sits at 7.05, 5.19, 0.45 x 0.43.
CANVAS = (0.26, 0.65, 6.98, 4.45)

BODY_FONT = "Fira Sans"
MONO_FONT = "Fira Code"

# (layout, placeholder idx) -> point size.
# Values with a template source are the template's own; the rest are overrides
# for placeholders that would otherwise inherit 10.5pt from the master.
PLACEHOLDER_PT = {
    ("TITLE", 0): 31.5,
    ("TITLE", 1): 18.0,
    ("SECTION_HEADER", 0): 27.0,
    ("SECTION_HEADER_1", 0): 27.0,
    ("TITLE_ONLY", 0): 20.0,          # override, inherits 10.5
    ("ONE_COLUMN_TEXT", 0): 18.0,
    ("ONE_COLUMN_TEXT", 1): 9.0,
    ("MAIN_POINT", 0): 36.0,
    ("SECTION_TITLE_AND_DESCRIPTION", 0): 31.5,
    ("SECTION_TITLE_AND_DESCRIPTION", 1): 15.75,
    ("SECTION_TITLE_AND_DESCRIPTION", 2): 12.0,   # override
    ("CAPTION_ONLY", 1): 12.0,        # override
    ("BIG_NUMBER", 0): 90.0,
    ("BIG_NUMBER", 1): 14.0,          # override
}

# Placeholder boxes measured from the template, in inches.
PLACEHOLDER_BOX = {
    ("TITLE", 0): (0.26, 0.08, 6.99, 2.24),
    ("TITLE", 1): (0.26, 2.38, 6.99, 0.87),
    ("SECTION_HEADER", 0): (0.26, 2.35, 6.99, 0.92),
    ("SECTION_HEADER_1", 0): (0.26, 2.35, 6.99, 0.92),
    ("TITLE_ONLY", 0): (0.02, 0.02, 6.99, 0.63),
    ("ONE_COLUMN_TEXT", 0): (0.26, 0.61, 2.30, 0.83),
    ("ONE_COLUMN_TEXT", 1): (0.26, 1.52, 2.30, 3.48),
    ("MAIN_POINT", 0): (0.40, 0.49, 5.22, 4.47),
    ("SECTION_TITLE_AND_DESCRIPTION", 0): (0.22, 1.35, 3.32, 1.62),
    ("SECTION_TITLE_AND_DESCRIPTION", 1): (0.22, 3.07, 3.32, 1.35),
    ("SECTION_TITLE_AND_DESCRIPTION", 2): (4.05, 0.79, 3.15, 4.04),
    ("CAPTION_ONLY", 1): (0.26, 4.63, 4.92, 0.66),
    ("BIG_NUMBER", 0): (0.26, 1.21, 6.99, 2.15),
    ("BIG_NUMBER", 1): (0.26, 3.45, 6.99, 1.42),
}

# Placeholder text-frame insets (left, top, right, bottom), in inches, measured
# from each placeholder's own <a:bodyPr> in template.pptx's slide layouts
# (read via python-pptx text_frame.margin_left/top/right/bottom on the
# layout's placeholder shape). Every one of these fourteen placeholders
# declares its own bodyPr insets directly on the layout -- none fall back to
# the master or the OOXML default -- and every declared value is
# lIns=tIns=rIns=bIns="97500" EMU = 0.1066in. (A lone 68569 EMU inset does
# exist in slideLayout7.xml, but it belongs to a non-placeholder background
# rectangle, not to any placeholder in PLACEHOLDER_BOX, so it does not apply
# here.)
PLACEHOLDER_INSET = {
    ("TITLE", 0): (0.1066, 0.1066, 0.1066, 0.1066),
    ("TITLE", 1): (0.1066, 0.1066, 0.1066, 0.1066),
    ("SECTION_HEADER", 0): (0.1066, 0.1066, 0.1066, 0.1066),
    ("SECTION_HEADER_1", 0): (0.1066, 0.1066, 0.1066, 0.1066),
    ("TITLE_ONLY", 0): (0.1066, 0.1066, 0.1066, 0.1066),
    ("ONE_COLUMN_TEXT", 0): (0.1066, 0.1066, 0.1066, 0.1066),
    ("ONE_COLUMN_TEXT", 1): (0.1066, 0.1066, 0.1066, 0.1066),
    ("MAIN_POINT", 0): (0.1066, 0.1066, 0.1066, 0.1066),
    ("SECTION_TITLE_AND_DESCRIPTION", 0): (0.1066, 0.1066, 0.1066, 0.1066),
    ("SECTION_TITLE_AND_DESCRIPTION", 1): (0.1066, 0.1066, 0.1066, 0.1066),
    ("SECTION_TITLE_AND_DESCRIPTION", 2): (0.1066, 0.1066, 0.1066, 0.1066),
    ("CAPTION_ONLY", 1): (0.1066, 0.1066, 0.1066, 0.1066),
    ("BIG_NUMBER", 0): (0.1066, 0.1066, 0.1066, 0.1066),
    ("BIG_NUMBER", 1): (0.1066, 0.1066, 0.1066, 0.1066),
}

# Average glyph advance as a fraction of point size. Fira Sans mixed case
# measures 0.484 em (fontTools, FiraSans-Regular.otf, English letter-frequency
# sample); 0.55 is deliberately pessimistic so the check errs toward flagging.
# Fira Sans caps run narrower than Arial's (W 0.826 against 0.944), so headings
# have more slack than this constant assumes, not less.
# Fira Code is fixed-pitch at 1200/1950 = 0.6154 em (fontTools,
# FiraCode-Regular.ttf); 0.62 rounds up so mono is pessimistic too. It is wider
# than Menlo's 0.6021, so a mono budget written for Menlo would overrun here.
PROPORTIONAL_ADVANCE = 0.55
MONO_ADVANCE = 0.62
LINE_SPACING = 1.2


def budget(width_in, height_in, pt, mono=False):
    """Return (chars_per_line, max_lines, total_chars) for a text box."""
    advance = (MONO_ADVANCE if mono else PROPORTIONAL_ADVANCE) * pt / 72.0
    line_height = LINE_SPACING * pt / 72.0
    chars_per_line = max(1, int(width_in / advance))
    max_lines = max(1, int(height_in / line_height))
    return chars_per_line, max_lines, chars_per_line * max_lines


def wrapped_lines(text, chars_per_line):
    """Line count after hard newlines and greedy wrapping."""
    total = 0
    for hard_line in text.split("\n"):
        if not hard_line:
            total += 1
            continue
        total += -(-len(hard_line) // chars_per_line)
    return total
